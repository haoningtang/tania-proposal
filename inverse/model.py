"""Differentiable forward model for an ALIGNED Si photonic-crystal bilayer (fmmax / JAX).

Stack (top to bottom): vacuum | slab 1 | air gap | slab 2 (laterally shifted) | vacuum.
Lengths in micrometres. Returns the complex zero-order transmission coefficient for TE (E perpendicular to the
plane of incidence) and TM (E in the plane of incidence), for a plane wave at polar angle theta and azimuth phi
(phi = 0: plane of incidence x-z, TE = E along y; phi = 45 deg: lattice diagonal).

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


def bilayer_t(lam, theta_deg, a, t, r, gap, shift=0.0, n_slab=3.48, n_terms=120, ngrid=128, r2=None, c4=0.0, c8=0.0,
              azimuth_deg=0.0):
    """Complex zero-order transmission (t_TE, t_TM) and powers (T_TE, T_TM).

    lam, theta_deg may be arrays of the same shape (batched). azimuth_deg is a scalar.
    Also returns the cross-polarized amplitudes t_TE_TM (TM out for TE in) and t_TM_TE, to check that TE and TM
    decouple (they must along a mirror line of the lattice: phi = 0 or 45 deg for C4v holes, shift 0)."""
    lam = jnp.atleast_1d(jnp.asarray(lam))
    # complex wavelength lam*(1 + i*eta) is allowed: it smooths every resonance by an extra linewidth ~ eta*lam
    # (frequency averaging, Liang & Johnson 2013); used by optimize.py objective "sharp" with smooth_eta > 0.
    lam = lam.astype(jnp.complex128 if jnp.iscomplexobj(lam) else jnp.float64)
    th = jnp.radians(jnp.atleast_1d(jnp.asarray(theta_deg, dtype=jnp.float64)))
    lv = fmmax.LatticeVectors(u=a * fmmax.X, v=a * fmmax.Y)
    # The basis (integer reciprocal-lattice indices) depends only on the lattice shape, not on a, and
    # generate_expansion uses numpy; build it on the unit square lattice so that a can be a traced design variable.
    exp = fmmax.generate_expansion(fmmax.LatticeVectors(u=fmmax.X, v=fmmax.Y), approximate_num_terms=n_terms,
                                   truncation=fmmax.Truncation.CIRCULAR)
    k = 2 * jnp.pi / lam * jnp.sin(th)
    ph = np.radians(float(azimuth_deg)); cph, sph = float(np.cos(ph)), float(np.sin(ph))
    kvec = jnp.stack([k * cph, k * sph], axis=-1)
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
    # amplitude index: block 0 = x-polarised, block 1 = y-polarised (tangential E of the vacuum plane waves).
    # TE: tangential E along (-sin phi, cos phi); TM: along (cos phi, sin phi). At phi = 0: TE = y block, TM = x block.
    pol = {"TM": (cph, sph), "TE": (-sph, cph)}
    def vec(c):
        return jnp.zeros((2 * nb, 1), dtype=jnp.complex128).at[i0, 0].set(c[0]).at[nb + i0, 0].set(c[1])
    for name in ("TM", "TE"):
        a_out = S.s11 @ vec(pol[name])  # forward amplitude leaving the bottom
        other = "TE" if name == "TM" else "TM"
        tt = pol[name][0] * a_out[..., i0, 0] + pol[name][1] * a_out[..., nb + i0, 0]
        out["t_" + name] = tt
        out["T_" + name] = jnp.abs(tt) ** 2
        out[f"t_{name}_{other}"] = pol[other][0] * a_out[..., i0, 0] + pol[other][1] * a_out[..., nb + i0, 0]
    return out
