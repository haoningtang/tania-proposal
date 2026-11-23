"""Differentiable forward model for an ALIGNED Si photonic-crystal bilayer (fmmax / JAX).

2026-11-23 (T20): TE/TM KEYS FIXED. The keys "TE"/"TM" (t_TE, t_TM, t_TE_TM, t_TM_TE, T_TE, T_TM) are now the PHYSICAL ones
(TE = s = E perpendicular to the plane of incidence). Before this date the two were swapped (check_pol_labels.py, Brewster):
fmmax amplitude blocks are (-E_y, E_x), not (E_x, E_y). The fix is a pure rename: new key "TE" = old key "TM" exactly (same
amplitude, same sign), new "TM" = old "TE", new t_TE_TM = old t_TM_TE. Run folders made before 2026-11-23 keep the old keys
(rule in docs/POLARIZATION_NOTE.md). POL_KEYS below marks the convention; scripts that write results store it.

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

POL_KEYS = "physical"   # since 2026-11-23 (T20); results written before used swapped keys


def hole_eps(r, a, n_slab, ngrid, sx=0.0, sy=0.0, smooth=1.0, c4=0.0, c8=0.0, lattice="square", rb=None):
    """Permittivity grid of a slab with one hole per cell (smoothed edge, differentiable).

    lattice "square": u = a x, v = a y. Hole boundary r(phi) = r + c4 cos(4 phi) + c8 cos(8 phi) (C4v).
    lattice "hex":    u = a x, v = a (x/2 + sqrt3/2 y). The two shape harmonics are then 6 and 12:
                      r(phi) = r + c4 cos(6 phi) + c8 cos(12 phi) (C6v), i.e. c4/c8 are "first/second allowed harmonic".
    In both cases the holes keep the full point group, so TE and TM stay degenerate at normal incidence.
    The grid is sampled in fractional coordinates of (u, v), as fmmax expects; distances are Cartesian, to the
    nearest image. r, c4, c8 in micrometres; sx, sy shift in fractional units of u and v."""
    x = (jnp.arange(ngrid) + 0.5) / ngrid
    F1, F2 = jnp.meshgrid(x, x, indexing="ij")
    if lattice == "hex_r3":
        # T16c: sqrt3 x sqrt3 R30 supercell of the hex lattice a1 = a x, a2 = a (x/2 + sqrt3/2 y) (orientation kept, so
        # azimuth 0 / 30 deg mean the same as for "hex"). u = a1 + a2 = a (3/2, sqrt3/2), v = 2 a2 - a1 = a (0, sqrt3).
        # Three holes: radius r at fractional (0, 0) of (u, v), radius rb at (1/3, 1/3) and (2/3, 2/3) (= -a1, +a1).
        # C6v about the r site. c4/c8 not supported here. a is the hex period; the supercell period is sqrt3 a.
        rb = r if rb is None else rb
        h = np.sqrt(3.0)
        fill = 1.0
        for (c1, c2), rr in (((0.0, 0.0), r), ((1 / 3, 1 / 3), rb), ((2 / 3, 2 / 3), rb)):
            d1 = (F1 - c1 - sx + 0.5) % 1.0 - 0.5
            d2 = (F2 - c2 - sy + 0.5) % 1.0 - 0.5
            cands = []
            for m1, m2 in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)):
                e1, e2 = d1 + m1, d2 + m2
                cands.append((1.5 * e1, (h / 2) * e1 + h * e2))   # Cartesian / a
            rho = jnp.sqrt(jnp.min(jnp.stack([cx**2 + cy**2 for cx, cy in cands]), axis=0) + 1e-12) * a
            fill = fill * jax.nn.sigmoid((rho - rr) / (smooth * h * a / ngrid))
        return 1.0 + (n_slab**2 - 1.0) * fill
    d1 = (F1 - 0.5 - sx + 0.5) % 1.0 - 0.5
    d2 = (F2 - 0.5 - sy + 0.5) % 1.0 - 0.5
    if lattice == "hex":
        h = np.sqrt(3.0) / 2
        cands = []
        for m1, m2 in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)):
            e1, e2 = d1 + m1, d2 + m2
            cands.append((e1 + 0.5 * e2, h * e2))
        dist2 = jnp.stack([cx**2 + cy**2 for cx, cy in cands])
        idx = jnp.argmin(dist2, axis=0)
        dx = jnp.choose(idx, [c[0] for c in cands], mode="clip")
        dy = jnp.choose(idx, [c[1] for c in cands], mode="clip")
        n1, n2 = 6, 12
    else:
        dx, dy = d1, d2
        n1, n2 = 4, 8
    rho = jnp.sqrt(dx**2 + dy**2 + 1e-12) * a
    phi = jnp.arctan2(dy, dx)
    rb = r + c4 * jnp.cos(n1 * phi) + c8 * jnp.cos(n2 * phi)
    w = smooth * a / ngrid  # edge width ~ one pixel
    fill = jax.nn.sigmoid((rho - rb) / w)  # 0 in hole, 1 in slab
    return 1.0 + (n_slab**2 - 1.0) * fill


def bilayer_t(lam, theta_deg, a, t, r, gap, shift=0.0, n_slab=3.48, n_terms=120, ngrid=128, r2=None, c4=0.0, c8=0.0, t2=None,
              azimuth_deg=0.0, lattice="square", shift_y=0.0, rb=None):
    """Complex zero-order transmission (t_TE, t_TM) and powers (T_TE, T_TM).

    lam, theta_deg may be arrays of the same shape (batched). azimuth_deg is a scalar.
    Also returns the cross-polarized amplitudes t_TE_TM (TM out for TE in) and t_TM_TE, to check that TE and TM
    decouple (they must along a mirror line of the lattice: phi = 0 or 45 deg for C4v holes, shift 0).
    shift, shift_y: lateral offset of slab 2 along u and v, in fractions of the period (shift_y added 2026-11-21 for T13a)."""
    lam = jnp.atleast_1d(jnp.asarray(lam))
    # complex wavelength lam*(1 + i*eta) is allowed: it smooths every resonance by an extra linewidth ~ eta*lam
    # (frequency averaging, Liang & Johnson 2013); used by optimize.py objective "sharp" with smooth_eta > 0.
    lam = lam.astype(jnp.complex128 if jnp.iscomplexobj(lam) else jnp.float64)
    th = jnp.radians(jnp.atleast_1d(jnp.asarray(theta_deg, dtype=jnp.float64)))
    # lattice "hex" (C6v): quadratic band dispersion at Gamma is isotropic by symmetry, so a band that is flat along
    # one azimuth is flat along all of them to O(k^2). Square (C4v) allows separate (kx^2 - ky^2) and kx*ky terms
    # (T4/T7c: flat along x only). Mirror lines for hex: azimuth 0 and 30 deg.
    vhat = fmmax.Y if lattice != "hex" else (0.5 * fmmax.X + (np.sqrt(3.0) / 2) * fmmax.Y)
    uhat = fmmax.X
    if lattice == "hex_r3":  # T16c supercell (see hole_eps); rb = radius of the two b holes (both slabs), default r
        uhat = 1.5 * fmmax.X + (np.sqrt(3.0) / 2) * fmmax.Y
        vhat = np.sqrt(3.0) * fmmax.Y
    lv = fmmax.LatticeVectors(u=a * uhat, v=a * vhat)
    # The basis (integer reciprocal-lattice indices) depends only on the lattice shape, not on a, and
    # generate_expansion uses numpy; build it on the unit lattice so that a can be a traced design variable.
    exp = fmmax.generate_expansion(fmmax.LatticeVectors(u=uhat, v=vhat), approximate_num_terms=n_terms,
                                   truncation=fmmax.Truncation.CIRCULAR)
    k = 2 * jnp.pi / lam * jnp.sin(th)
    ph = np.radians(float(azimuth_deg)); cph, sph = float(np.cos(ph)), float(np.sin(ph))
    kvec = jnp.stack([k * cph, k * sph], axis=-1)
    def solve(eps):
        return fmmax.eigensolve_isotropic_media(wavelength=lam, in_plane_wavevector=kvec,
                                                primitive_lattice_vectors=lv, permittivity=eps,
                                                expansion=exp, formulation=fmmax.Formulation.FFT)
    vac = solve(jnp.ones((1, 1), dtype=jnp.complex128))
    e1 = hole_eps(r, a, n_slab, ngrid, c4=c4, c8=c8, lattice=lattice, rb=rb).astype(jnp.complex128)
    e2 = hole_eps(r if r2 is None else r2, a, n_slab, ngrid, sx=shift, sy=shift_y, c4=c4, c8=c8, lattice=lattice,
                  rb=rb).astype(jnp.complex128)
    s1, s2 = solve(e1), solve(e2)
    if gap is None:
        S = fmmax.stack_s_matrix([vac, s1, vac], [jnp.zeros(()), jnp.asarray(t), jnp.zeros(())])
    else:
        S = fmmax.stack_s_matrix([vac, s1, vac, s2, vac],
                                 [jnp.zeros(()), jnp.asarray(t), jnp.asarray(gap), jnp.asarray(t if t2 is None else t2),
                                  jnp.zeros(())])  # t2: second-slab thickness (default = t)
    nb = exp.num_terms
    i0 = int(np.argmin(np.sum(np.abs(np.asarray(exp.basis_coefficients)), axis=1)))  # zero order
    out = {}
    # amplitude blocks: (block 0, block 1) = (-E_y, E_x) (fmmax field order (-ey, ex, hx, hy); check_pol_labels.py).
    # TE: E along (-sin phi, cos phi) -> blocks -(cos phi, sin phi); TM: E along (cos phi, sin phi) -> blocks (-sin phi, cos phi).
    # The overall sign of the TE vector is dropped (t is unchanged by it; this keeps new t_TE identical to the old key t_TM).
    # At phi = 0: TE = E_y = block 0, TM = E_x = block 1. (Before 2026-11-23 the two names below were swapped.)
    pol = {"TE": (cph, sph), "TM": (-sph, cph)}
    def vec(c):
        return jnp.zeros((2 * nb, 1), dtype=jnp.complex128).at[i0, 0].set(c[0]).at[nb + i0, 0].set(c[1])
    for name in ("TE", "TM"):
        a_out = S.s11 @ vec(pol[name])  # forward amplitude leaving the bottom
        other = "TE" if name == "TM" else "TM"
        tt = pol[name][0] * a_out[..., i0, 0] + pol[name][1] * a_out[..., nb + i0, 0]
        out["t_" + name] = tt
        out["T_" + name] = jnp.abs(tt) ** 2
        out[f"t_{name}_{other}"] = pol[other][0] * a_out[..., i0, 0] + pol[other][1] * a_out[..., nb + i0, 0]
    return out
