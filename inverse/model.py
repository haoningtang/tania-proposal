"""Differentiable forward model for an ALIGNED Si photonic-crystal bilayer (fmmax / JAX).

Stack (top to bottom): vacuum | slab 1 | air gap | slab 2 (laterally shifted) | vacuum.
Lengths in micrometres. Returns the complex zero-order transmission coefficient for TE (E along y)
and TM (E in the plane of incidence), for a plane wave incident in the x-z plane at angle theta.

rcwa4d-mf cannot be used here: it requires a nonzero twist (README, section 7).
Use rcwa4d-mf only for twisted structures (A3).
"""
import jax, jax.numpy as jnp, numpy as np
import fmmax

jax.config.update("jax_enable_x64", True)


def hole_eps(r, a, n_slab, ngrid, sx=0.0, sy=0.0, smooth=1.0, c4=0.0, c8=0.0):
    """Permittivity grid of a square-lattice slab with one hole (smoothed edge, differentiable).

    Hole boundary: r(phi) = r + c4 cos(4 phi) + c8 cos(8 phi)  (C4v symmetric, so TE and TM stay
    degenerate at normal incidence). r, c4, c8 in micrometres; sx, sy shift in units of the period."""
    x = (jnp.arange(ngrid) + 0.5) / ngrid
    X, Y = jnp.meshgrid(x, x, indexing="ij")
    dx = (X - 0.5 - sx + 0.5) % 1.0 - 0.5
    dy = (Y - 0.5 - sy + 0.5) % 1.0 - 0.5
    rho = jnp.sqrt(dx**2 + dy**2 + 1e-12) * a
    phi = jnp.arctan2(dy, dx)
    rb = r + c4 * jnp.cos(4 * phi) + c8 * jnp.cos(8 * phi)
    w = smooth * a / ngrid  # edge width ~ one pixel
    fill = jax.nn.sigmoid((rho - rb) / w)  # 0 in hole, 1 in slab
    return 1.0 + (n_slab**2 - 1.0) * fill


def bilayer_t(lam, theta_deg, a, t, r, gap, shift=0.0, n_slab=3.48, n_terms=120, ngrid=128, r2=None, c4=0.0, c8=0.0):
    """Complex zero-order transmission (t_TE, t_TM) and powers (T_TE, T_TM).

    lam, theta_deg may be arrays of the same shape (batched)."""
    lam = jnp.atleast_1d(jnp.asarray(lam, dtype=jnp.float64))
    th = jnp.radians(jnp.atleast_1d(jnp.asarray(theta_deg, dtype=jnp.float64)))
    lv = fmmax.LatticeVectors(u=a * fmmax.X, v=a * fmmax.Y)
    exp = fmmax.generate_expansion(lv, approximate_num_terms=n_terms, truncation=fmmax.Truncation.CIRCULAR)
    k = 2 * jnp.pi / lam * jnp.sin(th)
    kvec = jnp.stack([k, jnp.zeros_like(k)], axis=-1)
    def solve(eps):
        return fmmax.eigensolve_isotropic_media(wavelength=lam, in_plane_wavevector=kvec,
                                                primitive_lattice_vectors=lv, permittivity=eps,
                                                expansion=exp, formulation=fmmax.Formulation.FFT)
    vac = solve(jnp.ones((1, 1), dtype=jnp.complex128))
    e1 = hole_eps(r, a, n_slab, ngrid, c4=c4, c8=c8).astype(jnp.complex128)
    e2 = hole_eps(r if r2 is None else r2, a, n_slab, ngrid, sx=shift, c4=c4, c8=c8).astype(jnp.complex128)
    s1, s2 = solve(e1), solve(e2)
    if gap is None:
        S = fmmax.stack_s_matrix([vac, s1, vac], [jnp.zeros(()), jnp.asarray(t), jnp.zeros(())])
    else:
        S = fmmax.stack_s_matrix([vac, s1, vac, s2, vac],
                                 [jnp.zeros(()), jnp.asarray(t), jnp.asarray(gap), jnp.asarray(t), jnp.zeros(())])
    nb = exp.num_terms
    i0 = int(np.argmin(np.sum(np.abs(np.asarray(exp.basis_coefficients)), axis=1)))  # zero order
    out = {}
    # amplitude index: block 0 = x-polarised (TM for kx incidence), block 1 = y-polarised (TE)
    for name, idx in (("TM", i0), ("TE", nb + i0)):
        a_in = jnp.zeros((2 * nb, 1), dtype=jnp.complex128).at[idx, 0].set(1.0)
        a_out = S.s11 @ a_in  # forward amplitude leaving the bottom
        tt = a_out[..., idx, 0]
        out["t_" + name] = tt
        out["T_" + name] = jnp.abs(tt) ** 2
    return out
