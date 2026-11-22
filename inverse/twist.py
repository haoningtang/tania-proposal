"""T15: twist response of the square prelim bilayer with rcwa4d-mf (PyTorch, GPU).

Structure (units of a = 620 nm): square lattice, slab eps 12.11 (n 3.48, as model.py), exact circular hole r = 120/620
(rcwa4d_mf.Pattern, no grid), slab d = 220/620, vacuum gap g/620, slab 2 rotated by the twist about the hole centre.
Normal incidence. Transmission summed over all transmitted orders (zero order and the moire orders G1 + R(theta) G2).

Inputs x, y (solve_lab_basis) and the two circular states built from their complex amplitudes:
  e_pm = (e_x +- i e_y)/sqrt(2) for every order and component, T_pm = sum Re(kz) |e_pm|^2 / kz_inc.
Naming: the solver propagates as exp(-i kz z) (gap phase exp(-i kz k0 gap)), i.e. exp(+i w t) time convention; then
(x + i y)/sqrt(2) rotates x -> -y in time. We call sigma+ = (x + i y)/sqrt(2) and report CD = T_sigma+ - T_sigma-;
which of the two is "RCP" depends on the handedness convention, and the parity in theta does not.
T0_pm: the zero order alone (by C4 + reciprocity + no loss, T0_+ = T0_- is expected; CD must then come from moire orders).
"""
import argparse, json, math, os, time
import numpy as np
import torch, rcwa4d_mf
from scipy.interpolate import AAA

A_NM = 620.0


def get_dev():
    if torch.cuda.is_available():
        torch.backends.cuda.preferred_linalg_library("cusolver")
        return "cuda"
    torch.set_num_threads(1)
    return "cpu"


DEV = get_dev()
PAT = rcwa4d_mf.Pattern(12.11, [(rcwa4d_mf.Circle((0.0, 0.0), 120 / A_NM), 1.0)], device=DEV)


def spectrum(N, theta_deg, gap_nm, lams_nm, batch=None):
    """dict of arrays over lams_nm: Tx, Ty, Tp, Tm (sigma+-), T0p, T0m (zero order), Rx, Rp, Rm, err (max |R+T-1|)."""
    batch = batch or (8 if N <= 3 else 2)
    model = rcwa4d_mf.bilayer(PAT, d=220 / A_NM, gap=gap_nm / A_NM, twist_deg=theta_deg, N=N)
    keys = ["Tx", "Ty", "Tp", "Tm", "T0p", "T0m", "Rx", "Rp", "Rm", "err"]
    out = {k: [] for k in keys}
    lams_nm = np.asarray(lams_nm, float)
    for i in range(0, len(lams_nm), batch):
        f = torch.tensor(A_NM / lams_nm[i:i + batch], dtype=torch.float64, device=DEV)
        z = torch.zeros_like(f)
        with torch.no_grad():
            x, y = rcwa4d_mf.solve_lab_basis(model, f, ux=z, uy=z)
        big = x.transmitted_e.shape[1]; c0 = big // 2
        kzt = x.kz_transmission.real; kzr = x.kz_reflection.real
        def pw(ex, ey, kz, only0=False):
            for s, e in ((1, None), (-1, None)):
                pass
            res = []
            for s in (1, -1):
                e = (ex + s * 1j * ey) / math.sqrt(2)
                p = kz[..., None] * e.abs().square()          # [B, big, 3]
                res.append((p[:, c0].sum(-1) if only0 else p.sum((-1, -2))))
            return res
        Tp, Tm = pw(x.transmitted_e, y.transmitted_e, kzt)
        T0p, T0m = pw(x.transmitted_e, y.transmitted_e, kzt, only0=True)
        Rp, Rm = pw(x.reflected_e, y.reflected_e, kzr)
        vals = dict(Tx=x.transmission, Ty=y.transmission, Tp=Tp, Tm=Tm, T0p=T0p, T0m=T0m, Rx=x.reflection, Rp=Rp, Rm=Rm,
                    err=torch.maximum((x.transmission + x.reflection - 1).abs(), (Tp + Rp - 1).abs()))
        for k in keys:
            out[k] += vals[k].detach().cpu().numpy().tolist()
    return {k: np.array(v) for k, v in out.items()}


def poles_w(lams_nm, t, lo, hi, qmin=20):
    """AAA poles (in 1/lambda) with weight |residue|/|Im pole|: list of (lam_nm, Q, weight)"""
    A = AAA(1 / np.asarray(lams_nm), np.asarray(t), rtol=1e-8, max_terms=14)
    out = []
    for z, rz in zip(A.poles(), A.residues()):
        if z.real <= 0 or z.imag == 0:
            continue
        l0 = 1 / z.real; Q = z.real / (2 * abs(z.imag)); w = abs(rz) / abs(z.imag)
        if lo < l0 < hi and qmin < Q < 1e8 and w > 0.05:
            out.append((float(l0), float(Q), float(w)))
    return sorted(out)


def dense(N_list, thetas, gap, lo, hi, n, outdir):
    """dense spectra saved as npz + one figure (explore mode)"""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    os.makedirs(outdir, exist_ok=True)
    ll = np.linspace(lo, hi, n)
    fig, ax = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
    for N in N_list:
        for th in thetas:
            t0 = time.time(); s = spectrum(N, th, gap, ll)
            np.savez(os.path.join(outdir, f"dense_N{N}_th{th:+g}_g{gap:g}.npz"), lam=ll, **s)
            P = poles_w(ll, s["Tx"], lo, hi)
            print(f"N {N} th {th} gap {gap}: {time.time()-t0:.0f}s err {s['err'].max():.1e}; poles " +
                  ", ".join(f"{p[0]:.2f}/Q{p[1]:.0f}/w{p[2]:.2f}" for p in dict.fromkeys(P)), flush=True)
            ax[0].plot(ll, s["Tx"], label=f"N{N} θ{th:g}"); ax[1].plot(ll, s["Tp"] - s["Tm"], label=f"N{N} θ{th:g}")
    ax[0].set_ylabel("T_x"); ax[1].set_ylabel("CD = T+ − T−"); ax[1].set_xlabel("λ (nm)"); ax[0].legend(fontsize=7)
    fig.savefig(os.path.join(outdir, f"dense_{'_'.join(map(str, N_list))}_{'_'.join(f'{t:g}' for t in thetas)}.png"), dpi=110)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--explore", action="store_true", help="coarse scan only, print poles")
    ap.add_argument("--N", type=int, nargs="+", default=[3])
    ap.add_argument("--theta", type=float, nargs="+", default=[1.0])
    ap.add_argument("--gap", type=float, default=200.0)
    ap.add_argument("--lo", type=float, default=1400); ap.add_argument("--hi", type=float, default=1650)
    ap.add_argument("--n", type=int, default=126)
    ap.add_argument("--dense", default=None, help="outdir: dense scan + plot")
    ap.add_argument("--sweep", default=None, help="outdir: one npz per (N, theta, gap) job, skipped if present (resumable)")
    ap.add_argument("--gaps", type=float, nargs="+", default=None)
    a = ap.parse_args()
    if a.sweep:
        os.makedirs(a.sweep, exist_ok=True); ll = np.linspace(a.lo, a.hi, a.n)
        for N in a.N:
            for g in (a.gaps or [a.gap]):
                for th in a.theta:
                    fn = os.path.join(a.sweep, f"spec_N{N}_th{th:+g}_g{g:g}.npz")
                    if os.path.exists(fn):
                        continue
                    t0 = time.time(); s_ = spectrum(N, th, g, ll)
                    np.savez(fn, lam=ll, N=N, theta=th, gap=g, **s_)
                    print(f"N {N} th {th:+g} gap {g:g}: {time.time()-t0:.0f}s err {s_['err'].max():.1e} max|CD| {np.abs(s_['Tp']-s_['Tm']).max():.3e}", flush=True)
    elif a.dense:
        dense(a.N, a.theta, a.gap, a.lo, a.hi, a.n, a.dense)
    elif a.explore:
        ll = np.linspace(a.lo, a.hi, a.n)
        for N in a.N:
            for th in a.theta:
                t0 = time.time(); s = spectrum(N, th, a.gap, ll)
                print(f"N {N} theta {th}: {time.time()-t0:.0f}s, max err {s['err'].max():.1e}, max|CD| {np.abs(s['Tp']-s['Tm']).max():.2e}, "
                      f"max|CD0| {np.abs(s['T0p']-s['T0m']).max():.2e}, Tx min {s['Tx'].min():.3f} at {ll[s['Tx'].argmin()]:.1f}", flush=True)
                for P in poles_w(ll, s["Tx"], a.lo, a.hi):
                    print(f"   pole Tx: lam {P[0]:.2f} Q {P[1]:.1f} w {P[2]:.2g}", flush=True)

