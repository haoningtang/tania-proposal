"""T13a: Jacobian of the resonance observables with respect to the mechanical controls (gap, shift x, shift y).

Observables for TE and TM: resonance wavelength lam (0.5 deg), Q (0.5 deg), and band curvature c = (dlam/lam) / sin^2(theta),
fitted on theta 0.5/3/6 deg (c = -1/(2M); used instead of M because M diverges for a flat band).
Central differences of +-h nm in each control, at each working point (shift x, shift y in nm; gap fixed).

Two tables per working point:
  raw:  d lam/d u (nm/nm), d Q/d u (1/nm), d c/d u (1/nm)
  norm: d(lam)/lam, d(Q)/Q, d c, each per nm  -> singular values and numerical rank (sigma > rtol * sigma_max)
Usage: python jacobian.py --out ../runs/<name> [--a 0.62 --t 0.22 --r 0.12 --gap 0.2 --points 0,0 20,20 --h 5 --n_terms 80 --ngrid 96]
"""
import argparse, json, os, time
import numpy as np
from analyze import band

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
OBS = ["lam_TE", "lam_TM", "Q_TE", "Q_TM", "c_TE", "c_TM"]
CTRL = ["gap", "shift_x", "shift_y"]


def observe(gap_nm, dx_nm, dy_nm):
    """lam, Q, c for TE and TM at one mechanical state (wraps analyze.band; shift_y passed through st)"""
    st = dict(gap=gap_nm * 1e-3, shift=dx_nm * 1e-3 / a.a, shift_y=dy_nm * 1e-3 / a.a)
    b = band(p, st, a.lam0, a.thetas, kw)
    out = {}
    for pol in ("TE", "TM"):
        r = b[pol]
        pts = r["pts"]
        s2 = np.sin(np.radians([q[0] for q in pts])) ** 2
        y = np.array([q[1] for q in pts]); y = (y - y[0]) / y[0]
        out["lam_" + pol] = r["lam"] * 1e3                     # nm
        out["Q_" + pol] = r["Q"]
        out["c_" + pol] = float(np.polyfit(s2[:3], y[:3], 1)[0]) if len(pts) >= 3 else np.nan
        out["pts_" + pol] = [[q[0], q[1] * 1e3, q[2]] for q in pts]
    return out


res = dict(settings=dict(vars(a), structure=p), points={})
fn = os.path.join(a.out, "jacobian.json")
for P in a.points:
    dx0, dy0 = map(float, P.split(","))
    t0 = time.time()
    base = observe(a.gap * 1e3, dx0, dy0)
    print(f"point ({dx0},{dy0}) base: " + ", ".join(f"{k} {base[k]:.6g}" for k in OBS), flush=True)
    J = np.zeros((6, 3)); states = {}
    for j, cname in enumerate(CTRL):
        d = np.zeros(3); d[j] = a.h
        up = observe(a.gap * 1e3 + d[0], dx0 + d[1], dy0 + d[2])
        dn = observe(a.gap * 1e3 - d[0], dx0 - d[1], dy0 - d[2])
        states[cname] = dict(plus=up, minus=dn)
        for i, o in enumerate(OBS):
            J[i, j] = (up[o] - dn[o]) / (2 * a.h)
        print(f"  {cname}: " + ", ".join(f"d{o} {J[i, j]:+.4e}" for i, o in enumerate(OBS)), flush=True)
    scale = np.array([base["lam_TE"], base["lam_TM"], base["Q_TE"], base["Q_TM"], 1.0, 1.0])
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
