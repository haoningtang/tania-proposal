"""T13a: Jacobian of the resonance observables with respect to the mechanical controls (gap, shift x, shift y).

Observables (see observe()): the two 0.5-deg modes lam_lo, lam_hi and their Q (sorted by wavelength; aligned: lo = TM, hi = TE;
with a diagonal shift both are diagonal modes seen in both polarizations), and the TE and TM band curvature
c = (dlam/lam) / sin^2(theta) from the 3- and 6-deg poles (c = -1/(2M); M diverges for a flat band).
v1 (TE/TM pole nearest a fixed guess, c from 0.5/3/6 deg) was wrong at the biased point: the two split modes swapped between
finite-difference states.
Central differences of +-h nm in each control, at each working point (shift x, shift y in nm; gap fixed).

Two tables per working point:
  raw:  d lam/d u (nm/nm), d Q/d u (1/nm), d c/d u (1/nm)
  norm: d(lam)/lam, d(Q)/Q, d c, each per nm  -> singular values and numerical rank (sigma > rtol * sigma_max)
Usage: python jacobian.py --out ../runs/<name> [--a 0.62 --t 0.22 --r 0.12 --gap 0.2 --points 0,0 20,20 --h 5 --n_terms 80 --ngrid 96]
"""
import argparse, json, os, time
import numpy as np
from scipy.interpolate import AAA
from analyze import scan

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--a", type=float, default=0.62); ap.add_argument("--t", type=float, default=0.22)
ap.add_argument("--r", type=float, default=0.12); ap.add_argument("--gap", type=float, default=0.20)
ap.add_argument("--points", nargs="+", default=["0,0", "20,20"], help="working points 'dx,dy' in nm")
ap.add_argument("--h", type=float, default=5.0, help="finite-difference step, nm")
ap.add_argument("--lam0", type=float, default=1.507)
ap.add_argument("--thetas", type=float, nargs="+", default=[0.5, 3.0, 6.0])
ap.add_argument("--n_terms", type=int, default=80); ap.add_argument("--ngrid", type=int, default=96)
ap.add_argument("--rtol", type=float, default=1e-2)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
kw = dict(n_terms=a.n_terms, ngrid=a.ngrid)
p = dict(a=a.a, t=a.t, r=a.r, r2=a.r, t2=a.t)
OBS = ["lam_lo", "lam_hi", "Q_lo", "Q_hi", "c_TE", "c_TM"]
CTRL = ["gap", "shift_x", "shift_y"]


def poles_w(ll, t, lo, hi):
    """AAA poles with their weight |residue|/|Im pole| (as analyze.poles, but weight returned and no Q cap)"""
    A = AAA(1 / np.asarray(ll), np.asarray(t), rtol=1e-8, max_terms=14)
    out = []
    for z, rz in zip(A.poles(), A.residues()):
        if z.real <= 0 or z.imag == 0:
            continue
        l0 = 1 / z.real; Q = z.real / (2 * abs(z.imag)); w = abs(rz) / abs(z.imag)
        if lo < l0 < hi and 20 < Q < 1e8 and w > 0.05:
            out.append((float(l0), float(Q), float(w)))
    return out


def observe(gap_nm, dx_nm, dy_nm, lam_c):
    """Mode-based observables at one mechanical state.
    lam_lo/lam_hi, Q_lo/Q_hi: the two 0.5-deg modes near lam_c, merged from the TE and TM fits and sorted by wavelength
      (aligned: lo = TM, hi = TE; with a diagonal shift both modes are diagonal and appear in both polarizations).
    c_TE/c_TM: curvature (dlam/lam)/sin^2 from the 3- and 6-deg poles of each polarization (largest-weight pole in that
      polarization's fit), where the angle splitting (>= 1.8 nm) is much larger than the shift splitting (~0.2 nm)."""
    st = dict(gap=gap_nm * 1e-3, shift=dx_nm * 1e-3 / a.a, shift_y=dy_nm * 1e-3 / a.a)
    ll = np.linspace(lam_c - 0.015, lam_c + 0.015, 91)
    t = scan(p, st, ll, 0.5, kw)
    P = sorted(poles_w(ll, t["TE"], ll[0], ll[-1]) + poles_w(ll, t["TM"], ll[0], ll[-1]))
    modes = []
    for x in P:                                   # merge the same pole seen in TE and TM
        if modes and abs(x[0] - modes[-1][0][0]) < 5e-6:   # 0.005 nm
            modes[-1].append(x)
        else:
            modes.append([x])
    modes = [(np.mean([m[0] for m in g]), np.mean([m[1] for m in g])) for g in modes]
    modes = sorted(sorted(modes, key=lambda m: abs(m[0] - lam_c))[:2])
    out = dict(modes_all=[[m[0] * 1e3, m[1]] for m in modes])
    if len(modes) < 2:
        raise RuntimeError(f"only {len(modes)} mode(s) found at {(gap_nm, dx_nm, dy_nm)}: {P}")
    out.update(lam_lo=modes[0][0] * 1e3, lam_hi=modes[1][0] * 1e3, Q_lo=modes[0][1], Q_hi=modes[1][1])
    lam_ref = 0.5 * (modes[0][0] + modes[1][0])
    for pol in ("TE", "TM"):
        pts = []
        for th in (3.0, 6.0):
            w = 0.06 + 0.02 * np.sin(np.radians(th)) ** 2 * lam_ref
            l2 = np.linspace(lam_ref - w, lam_ref + 0.4 * w, 61)
            Pp = poles_w(l2, scan(p, st, l2, th, kw)[pol], l2[0], l2[-1])
            Pp = [x for x in Pp if x[1] > 50]
            b = max(Pp, key=lambda x: x[2])
            pts.append((th, b[0], b[1]))
        s2 = np.sin(np.radians([3.0, 6.0])) ** 2
        out["c_" + pol] = float((pts[1][1] - pts[0][1]) / lam_ref / (s2[1] - s2[0]))
        out["pts_" + pol] = [[q[0], q[1] * 1e3, q[2]] for q in pts]
    return out


res = dict(settings=dict(vars(a), structure=p), points={})
fn = os.path.join(a.out, "jacobian.json")
for P in a.points:
    dx0, dy0 = map(float, P.split(","))
    t0 = time.time()
    base = observe(a.gap * 1e3, dx0, dy0, a.lam0)
    lc = 0.5 * (base["lam_lo"] + base["lam_hi"]) * 1e-3
    print(f"point ({dx0},{dy0}) base: " + ", ".join(f"{k} {base[k]:.6g}" for k in OBS), flush=True)
    J = np.zeros((6, 3)); states = {}
    for j, cname in enumerate(CTRL):
        d = np.zeros(3); d[j] = a.h
        up = observe(a.gap * 1e3 + d[0], dx0 + d[1], dy0 + d[2], lc)
        dn = observe(a.gap * 1e3 - d[0], dx0 - d[1], dy0 - d[2], lc)
        states[cname] = dict(plus=up, minus=dn)
        for i, o in enumerate(OBS):
            J[i, j] = (up[o] - dn[o]) / (2 * a.h)
        print(f"  {cname}: " + ", ".join(f"d{o} {J[i, j]:+.4e}" for i, o in enumerate(OBS)), flush=True)
    scale = np.array([base["lam_lo"], base["lam_hi"], base["Q_lo"], base["Q_hi"], 1.0, 1.0])
    Jn = J / scale[:, None]
    sv = np.linalg.svd(Jn, compute_uv=False)
    rank = int(np.sum(sv > a.rtol * sv[0]))
    # rank of the wavelength-only block (lam_TE, lam_TM): what a two-line read-out can resolve
    sv_lam = np.linalg.svd(Jn[:2], compute_uv=False)
    res["points"][P] = dict(base=base, J_raw=J.tolist(), J_norm=Jn.tolist(), sv=sv.tolist(), rank=rank,
                            sv_lam_only=sv_lam.tolist(), states=states, wall_s=round(time.time() - t0, 1))
    json.dump(res, open(fn, "w"), indent=1)
    print(f"  singular values (normalized): {', '.join(f'{s:.3e}' for s in sv)}; rank {rank} (rtol {a.rtol}); "
          f"lam-only sv {', '.join(f'{s:.3e}' for s in sv_lam)}; {time.time() - t0:.0f} s", flush=True)
