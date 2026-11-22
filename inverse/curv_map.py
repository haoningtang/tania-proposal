"""T16a: TE/TM band curvature of one hex line over (t2 - t, r2 - r).

Base design (T12a E1 line): a 0.85, r/a 0.25 (r 0.2125), t 0.28 um, gap 0.38, lam 1.49856 um, Q 133 at 0.5 deg.
For each grid point (dt2, dr2) the line is followed from a neighbouring point: start at (0, 0), walk along dr2 = 0 to
the row's dt2, then along the row outwards from dr2 = 0. At each point and for TE and TM separately: pole nearest the
neighbour's 0.5-deg wavelength (window +-3 linewidths), then tracked to 3 and 6 deg (as hex_isotropy.track).
c = slope of (lam(theta) - lam(0.5))/lam(0.5) vs sin^2(theta) over the three angles; M = -1/(2c).

Usage: python curv_map.py --rows -40 -26.67 ... (nm) --out ../runs/<name>/map_<tag>.json [--n_terms 80 --ngrid 96]
Resumable: points already in the output file are reused as starts and not recomputed.
"""
import argparse, json, os, time
import numpy as np
from scipy.interpolate import AAA
from analyze import scan

ap = argparse.ArgumentParser()
ap.add_argument("--rows", type=float, nargs="+", required=True, help="dt2 values (nm) handled by this process")
ap.add_argument("--grid", type=float, nargs="+", default=list(np.linspace(-40, 40, 7)), help="grid values (nm)")
ap.add_argument("--thetas", type=float, nargs="+", default=[0.5, 3, 6])
ap.add_argument("--azimuth", type=float, default=0.0)
ap.add_argument("--gap", type=float, default=0.38)
ap.add_argument("--lam0", type=float, default=1.4985595)
ap.add_argument("--q0", type=float, default=133.0)
ap.add_argument("--n_terms", type=int, default=80); ap.add_argument("--ngrid", type=int, default=96)
ap.add_argument("--out", required=True)
a = ap.parse_args()
A, T, R = 0.85, 0.28, 0.2125
kw = dict(n_terms=a.n_terms, ngrid=a.ngrid, lattice="hex", azimuth_deg=a.azimuth)
st = dict(gap=a.gap, shift=0.0)
G = [round(float(x), 2) for x in a.grid]


def poles(lams, t, lo, hi):
    A_ = AAA(1 / np.asarray(lams), np.asarray(t), rtol=1e-6, max_terms=12)
    out = []
    for p, rz in zip(A_.poles(), A_.residues()):
        if p.real <= 0 or p.imag == 0:
            continue
        l0 = 1 / p.real; Q = p.real / (2 * abs(p.imag))
        if lo < l0 < hi and 10 < Q < 1e8 and abs(rz) / abs(p.imag) > 0.05:
            out.append((float(l0), float(Q)))
    return out


def track(p, l0, Q, pol):
    w = max(3 * l0 / Q, 2e-4)
    s = None; allp = []
    for _ in range(3):
        ll = np.linspace(l0 - w, l0 + w, 41)
        allp = poles(ll, scan(p, st, ll, a.thetas[0], kw)[pol], ll[0], ll[-1])
        if allp:
            s = min(allp, key=lambda x: abs(x[0] - l0)); break
        w *= 2
    if s is None:
        return None
    pts = [(a.thetas[0], s[0], s[1])]
    for th in a.thetas[1:]:
        w = max(6 * pts[-1][1] / pts[-1][2], 0.004) + 0.02 * np.sin(np.radians(th)) ** 2 * pts[-1][1]
        ll = np.linspace(pts[-1][1] - w, pts[-1][1] + w, 41)
        P = poles(ll, scan(p, st, ll, th, kw)[pol], ll[0], ll[-1])
        if not P:
            break
        q = min(P, key=lambda x: abs(x[0] - pts[-1][1]))
        pts.append((th, q[0], q[1]))
    s2 = np.sin(np.radians([q[0] for q in pts])) ** 2
    y = np.array([q[1] for q in pts]); y = (y - y[0]) / y[0]
    c = float(np.polyfit(s2, y, 1)[0]) if len(pts) >= 3 else float("nan")
    return dict(lam=pts[0][1], Q=pts[0][2], c=c, M=float(-1 / (2 * c)) if c else float("inf"), pts=pts,
                others_05=[x for x in allp if x != s])


res = json.load(open(a.out)) if os.path.exists(a.out) else dict(
    settings=dict(kw, gap=a.gap, thetas=a.thetas, base=dict(a=A, t=T, r=R), lam0=a.lam0, q0=a.q0, grid_nm=G), points=[])
done = {(q["dt2"], q["dr2"]): q for q in res["points"]}


def point(dt2, dr2, prev):
    key = (dt2, dr2)
    if key in done:
        return done[key]
    p = dict(a=A, t=T, r=R, t2=T + dt2 * 1e-3, r2=R + dr2 * 1e-3, c4=0.0, c8=0.0)
    t0 = time.time()
    q = dict(dt2=dt2, dr2=dr2, p=p, start=prev)
    for pol in ("TE", "TM"):
        l0, Q0 = prev[pol] if prev else (a.lam0, a.q0)
        q[pol] = track(p, l0, Q0, pol)
    q["sec"] = round(time.time() - t0, 1)
    res["points"].append(q); done[key] = q
    json.dump(res, open(a.out, "w"), indent=1)
    f = lambda b: "lost" if b is None else f"{b['lam']*1e3:8.2f} nm Q {b['Q']:6.0f} c {b['c']:+.4f} M {b['M']:+8.2f}"
    print(f"dt2 {dt2:+6.2f} dr2 {dr2:+6.2f} | TE {f(q['TE'])} | TM {f(q['TM'])} | {q['sec']} s", flush=True)
    return q


def nxt(q):
    return {pol: ((q[pol]["lam"], q[pol]["Q"]) if q[pol] else None) for pol in ("TE", "TM")}


def fill(prev_q, start_from):
    s = nxt(prev_q)
    for pol in ("TE", "TM"):
        if s[pol] is None:
            s[pol] = start_from[pol]
    return s


i0 = G.index(0.0)
base = point(0.0, 0.0, None)
for row in sorted(a.rows, key=abs):
    row = round(row, 2); j = G.index(row)
    # walk along dr2 = 0 from 0 to the row
    q = base
    step = 1 if j > i0 else -1
    for k in range(i0 + step, j + step, step) if j != i0 else []:
        q = point(G[k], 0.0, fill(q, nxt(base)))
    rowc = q
    for direction in (1, -1):
        q = rowc
        for k in range(i0 + direction, len(G) if direction > 0 else -1, direction):
            q = point(row, G[k], fill(q, nxt(rowc)))
print("done", flush=True)
