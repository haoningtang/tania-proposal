"""T11a isotropy check for hexagonal-lattice candidates: M (and Q) of one TE/TM line at several azimuths.

Like analyze.band, but the 0.5-deg start is a fine window of +-3 linewidths around a known pole (the survey poles have
Q ~ 1e4-1e5, too narrow for band()'s 80 nm / 41-point start). Following angles use band()'s window rule; M from the
same fit (first three angles, shift vs sin^2 theta).

Usage: python hex_isotropy.py --config <survey config> --cands <candidates.json> --idx 0 1 2 --gaps 0.38
         --azimuths 0 15 30 --thetas 0.5 3 6 --out ../runs/<name>/iso.json
"""
import argparse, json, os
import numpy as np
from scipy.interpolate import AAA
from analyze import scan

def poles(lams, t, lo, hi):
    """as analyze.poles, but without its Q < 1e5 cap (hex quasi-BICs reach Q ~ 1e5 at 0.5 deg)"""
    A = AAA(1 / np.asarray(lams), np.asarray(t), rtol=1e-6, max_terms=12)
    out = []
    for p, rz in zip(A.poles(), A.residues()):
        if p.real <= 0 or p.imag == 0:
            continue
        l0 = 1 / p.real; Q = p.real / (2 * abs(p.imag))
        if lo < l0 < hi and 10 < Q < 1e8 and abs(rz) / abs(p.imag) > 0.05:
            out.append((float(l0), float(Q)))
    return out

ap = argparse.ArgumentParser()
ap.add_argument("--config", required=True); ap.add_argument("--cands", required=True)
ap.add_argument("--idx", type=int, nargs="+", default=[0, 1, 2])
ap.add_argument("--gaps", type=float, nargs="+", default=[0.38])
ap.add_argument("--lam0", type=float, nargs="*", default=None, help="start wavelength per gap (default: candidate lam)")
ap.add_argument("--q0", type=float, default=None, help="start Q guess when lam0 is given")
ap.add_argument("--azimuths", type=float, nargs="+", default=[0, 15, 30])
ap.add_argument("--thetas", type=float, nargs="+", default=[0.5, 3, 6])
ap.add_argument("--n_terms", type=int, default=None); ap.add_argument("--ngrid", type=int, default=None)
ap.add_argument("--out", required=True)
a = ap.parse_args()
cfg = json.load(open(a.config)); cands = json.load(open(a.cands))
base = dict(n_terms=a.n_terms or cfg.get("n_terms", 80), ngrid=a.ngrid or cfg.get("ngrid", 96), lattice=cfg.get("lattice", "hex"))

def start(p, st, l0, Q, th, kw, pol):
    """find the pole near l0 at angle th: fine window of +-3 linewidths, widened up to 3 times if nothing is found"""
    w = max(3 * l0 / Q, 2e-5)
    for _ in range(4):
        ll = np.linspace(l0 - w, l0 + w, 41)
        P = poles(ll, scan(p, st, ll, th, kw)[pol], ll[0], ll[-1])
        if P:
            return min(P, key=lambda x: abs(x[0] - l0))
        w *= 4
    return None

def track(p, st, l0, Q0, kw, pol):
    s = start(p, st, l0, Q0, a.thetas[0], kw, pol)
    if s is None:
        return None
    pts = [(a.thetas[0], float(s[0]), float(s[1]))]
    for th in a.thetas[1:]:
        w = max(6 * pts[-1][1] / pts[-1][2], 0.004) + 0.02 * np.sin(np.radians(th)) ** 2 * pts[-1][1]
        ll = np.linspace(pts[-1][1] - w, pts[-1][1] + w, 41)   # symmetric: the line may move either way
        P = poles(ll, scan(p, st, ll, th, kw)[pol], ll[0], ll[-1])
        if not P:
            break
        q = min(P, key=lambda x: abs(x[0] - pts[-1][1]))
        pts.append((th, float(q[0]), float(q[1])))
    s2 = np.sin(np.radians([q[0] for q in pts])) ** 2
    y = np.array([q[1] for q in pts]); y = (y - y[0]) / y[0]
    c = np.polyfit(s2[:3], y[:3], 1)[0] if len(pts) >= 3 else np.nan
    return dict(lam=pts[0][1], Q=pts[0][2], M=float(-1 / (2 * c)) if c else float("inf"), pts=pts)

res = dict(settings=dict(base, thetas=a.thetas, azimuths=a.azimuths), rows=[])
if os.path.exists(a.out):
    res = json.load(open(a.out))
for i in a.idx:
    c = cands[i]
    p = dict(a=c["a"], t=c["t"], r=c["r_over_a"] * c["a"], r2=c["r_over_a"] * c["a"], t2=c["t"], c4=0.0, c8=0.0)
    for j, g in enumerate(a.gaps):
        l0 = a.lam0[j] if a.lam0 else c["lam"]; Q0 = a.q0 or min(c["Q_TE"], c["Q_TM"])
        st = dict(gap=g, shift=0.0)
        for az in a.azimuths:
            kw = dict(base, azimuth_deg=az)
            row = dict(cand=i, p=p, gap=g, azimuth=az)
            for pol in ("TE", "TM"):
                row[pol] = track(p, st, l0, Q0, kw, pol)
            res["rows"].append(row)
            json.dump(res, open(a.out, "w"), indent=1)
            f = lambda b: None if b is None else (round(b["lam"] * 1e3, 3), round(b["Q"]), round(b["M"], 2),
                                                  [(q[0], round(q[1] * 1e3, 3), round(q[2])) for q in b["pts"]])
            print(json.dumps(dict(cand=i, gap=g, az=az, TE=f(row["TE"]), TM=f(row["TM"]))), flush=True)
