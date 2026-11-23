"""T16c: hex sqrt3 x sqrt3 R30 supercell (model.py lattice "hex_r3"), three holes: r1 at the origin, rb at the two other
sites (C6v about r1). Base = T12a E1 line: a 850, mean r/a 0.25, t 280, gap 380 nm. Mean radius fixed:
r1 = rbar + (2/3) D a, rb = rbar - (1/3) D a with D = (r1 - rb)/a, so (r1 + 2 rb)/3 = rbar.

Per point (D, t, gap): three full scans 1450-1560 nm, 0.5 nm step (221 lambda), TE and TM:
  theta 0.5 deg azimuth 0; theta 3 deg azimuth 0; theta 3 deg azimuth 30.
Poles by AAA in overlapping 30 nm windows (stride 20 nm), deduplicated. Curvature: T16b Q-matched slope, done in the
analysis (hex_r3_analyze.py) from the stored pole lists. 6 deg windows are added later for the candidate lines only.
Points are claimed by lock files (claims/), so any number of processes can run; results in pts/<key>.json.
Usage: python hex_r3_scan.py --out RUN [--n_terms 240 --ngrid 160]"""
import argparse, json, os, time
import numpy as np
from scipy.interpolate import AAA
from analyze import scan
import model

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--n_terms", type=int, default=240); ap.add_argument("--ngrid", type=int, default=160)
ap.add_argument("--D", type=float, nargs="+", default=[0, 0.015, -0.015, 0.03, -0.03, 0.05, -0.05, 0.08, -0.08])
ap.add_argument("--t", type=float, nargs="+", default=[280, 240, 320])
ap.add_argument("--gap", type=float, nargs="+", default=[380, 340, 420])
ap.add_argument("--lo", type=float, default=1450); ap.add_argument("--hi", type=float, default=1560)
ap.add_argument("--step", type=float, default=0.5)
ap.add_argument("--points", type=str, default=None, help="explicit list 'D,t,gap;D,t,gap' (refinements)")
a = ap.parse_args()
A = 0.85; RBAR = 0.25 * A
os.makedirs(os.path.join(a.out, "pts"), exist_ok=True); os.makedirs(os.path.join(a.out, "claims"), exist_ok=True)


def poles(lams, t, lo, hi, max_terms=30):
    A_ = AAA(1 / np.asarray(lams), np.asarray(t), rtol=1e-7, max_terms=max_terms)
    out = []
    for p, rz in zip(A_.poles(), A_.residues()):
        if p.real <= 0 or p.imag == 0:
            continue
        l0 = 1 / p.real; Q = p.real / (2 * abs(p.imag))
        if lo < l0 < hi and 5 < Q < 1e8:
            out.append(dict(lam=float(l0) * 1e3, Q=float(Q), w=float(abs(rz) / abs(p.imag))))
    return out


def all_poles(ll, t):
    out = []
    w0 = ll[0]
    while w0 < ll[-1] - 1e-9:
        m = (ll >= w0 - 1e-12) & (ll <= w0 + 0.030 + 1e-12)
        lo, hi = (w0 + 0.005 if w0 > ll[0] else w0), (w0 + 0.025 if w0 + 0.030 < ll[-1] - 1e-9 else w0 + 0.030)
        out += poles(ll[m], t[m], lo, hi)   # keep the window's central part only
        w0 += 0.020
    out.sort(key=lambda p: p["lam"])
    ded = []
    for p in out:
        if ded and abs(p["lam"] - ded[-1]["lam"]) < 0.02 and abs(np.log(p["Q"] / ded[-1]["Q"])) < 0.3:
            continue
        ded.append(p)
    return ded


def key(D, t, g):
    return f"D{D:+.3f}_t{t:.0f}_g{g:.0f}"


def run_point(D, t, g):
    k = key(D, t, g); fn = os.path.join(a.out, "pts", k + ".json")
    if os.path.exists(fn):
        return
    try:
        os.close(os.open(os.path.join(a.out, "claims", k), os.O_CREAT | os.O_EXCL))
    except FileExistsError:
        return
    r1 = RBAR + (2 / 3) * D * A; rb = RBAR - (1 / 3) * D * A
    p = dict(a=A, t=t * 1e-3, r=r1)
    st = dict(gap=g * 1e-3, shift=0.0)
    ll = np.round(np.arange(a.lo, a.hi + 1e-9, a.step), 4) * 1e-3
    t0 = time.time(); rec = dict(pol_keys=getattr(model, "POL_KEYS", "swapped"), D=D, t=t, gap=g, r1_nm=r1 * 1e3, rb_nm=rb * 1e3, n_terms=a.n_terms, ngrid=a.ngrid, scans={})
    for th, az in ((0.5, 0.0), (3.0, 0.0), (3.0, 30.0)):
        kw = dict(n_terms=a.n_terms, ngrid=a.ngrid, lattice="hex_r3", azimuth_deg=az, rb=rb)
        tt = scan(p, st, ll, th, kw)
        rec["scans"][f"{th:g}_{az:g}"] = {pol: dict(poles=all_poles(ll, tt[pol]),
                                                     Tmin=float(np.min(np.abs(tt[pol]) ** 2)),
                                                     T=np.round(np.abs(tt[pol]) ** 2, 5).tolist()) for pol in ("TE", "TM")}
    rec["lam_nm"] = [float(a.lo), float(a.hi), float(a.step)]
    rec["sec"] = round(time.time() - t0, 1)
    json.dump(rec, open(fn, "w"))
    br = [q for q in rec["scans"]["0.5_0"]["TE"]["poles"] if 20 < q["Q"] < 1e4 and q["w"] > 0.05]
    print(f"{k}: {rec['sec']} s; bright TE poles at 0.5 deg: " + ", ".join(f"{q['lam']:.1f}/Q{q['Q']:.0f}" for q in br), flush=True)


if a.points:
    pts = [tuple(float(x) for x in s.split(",")) for s in a.points.split(";")]
else:
    # base row (t 280, gap 380) first, then the rest ordered by distance from the base
    pts = [(D, t, g) for t in a.t for g in a.gap for D in a.D]
    pts.sort(key=lambda q: (q[1] != 280 or q[2] != 380, abs(q[1] - 280) / 40 + abs(q[2] - 380) / 40, abs(q[0])))
for q in pts:
    run_point(*q)
print("done", flush=True)
