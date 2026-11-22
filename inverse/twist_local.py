"""T19c: local transmitted field of the twisted bilayer (T19a amplitudes) against the LPA map (T19b Jones).

Local field just below the bilayer, propagating orders only (all of them are moire orders k = (1 - R) G(m)):
  E(r) = sum_j E_j exp(i k_j.r) (rcwa4d-mf: exp(+i w t), so the lateral phase is exp(-i k.r); T_sigma(r) is the same for
  r -> -r because the twisted bilayer is C2z-symmetric about the twist axis, so the sign does not matter for powers),
  H_j = k_j x E_j (vacuum, k in units of k0, k_j = (kx, ky, -kz): wave to -z), local power T(r) = -Re[(E x H*)_z](r); its cell average is sum_j kz_j |E_j|^2.
Inputs: x, y, sigma+- = (x +- i y)/sqrt(2) in the rcwa4d convention. CD(r) = T_sigma+(r) - T_sigma-(r).
LPA: J_LPA(delta) from fmmax (exp(-i w t)) is conjugated to the rcwa4d convention before forming sigma+-, so sigma+ is the
same physical state in both. Local shift delta(r) = (R(theta) - 1) r (layer 2 = layer 1 rotated about r = 0).
Shift interpolation: periodic bilinear on the n x n LPA grid (T19b n = 16 and n48/).
"""
import numpy as np

A_NM = 620.0
EP = np.array([1, 1j]) / np.sqrt(2); EM = np.array([1, -1j]) / np.sqrt(2)


def load_amps(fn):
    d = np.load(fn)
    return {k: d[k] for k in d.files}


def moire_basis(d):
    lab = d["labels"]
    assert np.all(lab[:, 0] + lab[:, 2] == 0) and np.all(lab[:, 1] + lab[:, 3] == 0), "non-moire propagating order"
    m = lab[:, :2].astype(int)                         # k_j = m1 b1 + m2 b2
    i1 = np.where((m[:, 0] == 1) & (m[:, 1] == 0))[0][0]; i2 = np.where((m[:, 0] == 0) & (m[:, 1] == 1))[0][0]
    return m, i1, i2


def local_maps(d, li, ngrid=101, inputs=("x", "y", "sp", "sm"), s_range=0.5, center=(0.0, 0.0)):
    """maps of local T over the moire cell r = s1 L1 + s2 L2, s in [-s_range, s_range) + center, at lambda index li.
    Returns dict(T_<inp>=[ngrid, ngrid]), s grid, L1, L2 (nm), and r (nm, [ngrid, ngrid, 2])."""
    m, i1, i2 = moire_basis(d)
    lam = d["lam"][li]; k0 = 2 * np.pi / lam
    kx, ky, kz = d["kx"][li], d["ky"][li], d["kzt"][li]
    b = np.array([[kx[i1], ky[i1]], [kx[i2], ky[i2]]]) * k0          # rows b1, b2 (1/nm)
    # check that every order is the integer combination
    kk = m @ b
    assert np.allclose(kk, np.c_[kx, ky] * k0, atol=1e-9 * k0), "orders not on the moire lattice"
    Lm = 2 * np.pi * np.linalg.inv(b).T                                # rows L1, L2: L_i . b_j = 2 pi delta_ij
    s = (np.arange(ngrid) / ngrid - 0.5) * (2 * s_range)
    S1, S2 = np.meshgrid(s + center[0], s + center[1], indexing="ij")
    ph = np.exp(-2j * np.pi * (np.einsum("j,ab->abj", m[:, 0], S1) + np.einsum("j,ab->abj", m[:, 1], S2)))
    # rcwa4d stores transmitted E for a wave exp(-i k.r) with k = (kx, ky, -kz) (k.E = 0 holds only with -kz: checked
    # 2e-18); the transmitted wave travels to -z. Power to -z: -Re[(E x H*)_z], H = k x E.
    kv = np.stack([kx, ky, -kz], -1)
    E = dict(x=d["tx"][li], y=d["ty"][li])
    E["sp"] = (E["x"] + 1j * E["y"]) / np.sqrt(2); E["sm"] = (E["x"] - 1j * E["y"]) / np.sqrt(2)
    out = {}
    for inp in inputs:
        Ej = E[inp]; Hj = np.cross(kv, Ej)
        Er = ph @ Ej; Hr = ph @ Hj
        out["T_" + inp] = -np.real(Er[..., 0] * np.conj(Hr[..., 1]) - Er[..., 1] * np.conj(Hr[..., 0]))
        out["Tavg_" + inp] = float(np.sum(kz * np.sum(np.abs(Ej) ** 2, -1)))
    r = S1[..., None] * Lm[0] + S2[..., None] * Lm[1]
    return dict(out, s=s, L=Lm, r=r, lam=lam)


def lpa_interp(Jfull, n, delta_frac):
    """Jfull [n, n, ..., 2, 2] on shifts (i, j)/n; delta_frac [..., 2] in units of a (Cartesian = lattice for square).
    Periodic bilinear interpolation of J (complex) ... returns J at the shifts."""
    u = (delta_frac[..., 0] % 1.0) * n; v = (delta_frac[..., 1] % 1.0) * n
    i0 = np.floor(u).astype(int); j0 = np.floor(v).astype(int); fu = u - i0; fv = v - j0
    i1 = (i0 + 1) % n; j1 = (j0 + 1) % n; i0 %= n; j0 %= n
    w = lambda f: f[(...,) + (None,) * (Jfull.ndim - 2)]
    return (w((1 - fu) * (1 - fv)) * Jfull[i0, j0] + w(fu * (1 - fv)) * Jfull[i1, j0]
            + w((1 - fu) * fv) * Jfull[i0, j1] + w(fu * fv) * Jfull[i1, j1])


def lpa_T(J):
    """J [..., 2, 2] in rcwa convention -> powers for x, y, sigma+-"""
    return dict(T_x=np.sum(np.abs(J[..., :, 0]) ** 2, -1), T_y=np.sum(np.abs(J[..., :, 1]) ** 2, -1),
                T_sp=np.sum(np.abs(J @ EP) ** 2, -1), T_sm=np.sum(np.abs(J @ EM) ** 2, -1))


def local_shift(r_nm, twist_deg):
    th = np.radians(twist_deg); R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    return (r_nm @ (R - np.eye(2)).T) / A_NM
