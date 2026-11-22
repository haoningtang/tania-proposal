"""T16b: TE/TM band curvature of the hex E1 line over the SYMMETRIC shape (r2 = r, t2 = t; C6v kept), grid r/a x t at a 0.85.
Derived from curv_map.py (T16a). Grid keys: (t_nm, ra). Rows = t, columns = r/a. Path: from the base (t 280, r/a 0.25)
along the r/a = 0.25 column to the row's t, then along the row outwards. Extra per point: a wide neighbour scan
(+-25 nm around the line, --nwide points) at 0.5 deg and at --wide_theta (3 deg, where dark modes radiate ~36x more
and are resolvable on a coarse grid); all poles found there (both pols) are stored.
Original T16a doc follows.

T16a: TE/TM band curvature of one hex line over (t2 - t, r2 - r).

Base design (T12a E1 line): a 0.85, r/a 0.25 (r 0.2125), t 0.28 um, gap 0.38, lam 1.49856 um, Q 133 at 0.5 deg.
For each grid point (dt2, dr2) the line is followed from a neighbouring point: start at (0, 0), walk along dr2 = 0 to
the row's dt2, then along the row outwards from dr2 = 0. At each point and for TE and TM separately: pole nearest the
neighbour's 0.5-deg wavelength, followed in --nsub substeps at 0.5 deg (window +-3 linewidths, one scan for both pols), then tracked to 3 and 6 deg (as hex_isotropy.track).
c = slope of (lam(theta) - lam(0.5))/lam(0.5) vs sin^2(theta) over the three angles; M = -1/(2c).

Usage: python curv_map.py --rows -40 -26.67 ... (nm) --out ../runs/<name>/map_<tag>.json [--n_terms 80 --ngrid 96]
Resumable: points already in the output file are reused as starts and not recomputed.
"""
import argparse, json, os, time
import numpy as np
from scipy.interpolate import AAA
from analyze import scan

ap = argparse.ArgumentParser()
ap.add_argument("--rows", type=float, nargs="+", required=True, help="t values (nm) handled by this process")
ap.add_argument("--tgrid", type=float, nargs="+", default=[220, 240, 260, 280, 300, 320, 340])
ap.add_argument("--ragrid", type=float, nargs="+", default=[0.19, 0.21, 0.23, 0.25, 0.27, 0.29, 0.31])
ap.add_argument("--wide", type=float, default=0.025, help="half width of the neighbour scan (um)")
ap.add_argument("--nwide", type=int, default=201)
ap.add_argument("--wide_theta", type=float, default=3.0)
ap.add_argument("--thetas", type=float, nargs="+", default=[0.5, 3, 6])
ap.add_argument("--azimuth", type=float, default=0.0)
ap.add_argument("--gap", type=float, default=0.38)
ap.add_argument("--lam0", type=float, default=1.4985595)
ap.add_argument("--q0", type=float, default=133.0)
ap.add_argument("--n_terms", type=int, default=80); ap.add_argument("--ngrid", type=int, default=96)
ap.add_argument("--nsub", type=int, default=5, help="substeps (0.5 deg only) between neighbouring grid points")
ap.add_argument("--out", required=True)
a = ap.parse_args()
A, T, R = 0.85, 0.28, 0.2125
kw = dict(n_terms=a.n_terms, ngrid=a.ngrid, lattice="hex", azimuth_deg=a.azimuth)
st = dict(gap=a.gap, shift=0.0)
GT = [round(float(x), 2) for x in a.tgrid]; GR = [round(float(x), 4) for x in a.ragrid]


def poles(lams, t, lo, hi, max_terms=12):
    A_ = AAA(1 / np.asarray(lams), np.asarray(t), rtol=1e-6, max_terms=max_terms)
    out = []
    for p, rz in zip(A_.poles(), A_.residues()):
        if p.real <= 0 or p.imag == 0:
            continue
        l0 = 1 / p.real; Q = p.real / (2 * abs(p.imag))
        if lo < l0 < hi and 10 < Q < 1e8 and abs(rz) / abs(p.imag) > 0.05:
            out.append((float(l0), float(Q)))
    return out


def at05(p, starts):
    """one 0.5-deg scan shared by TE and TM: window +-3 linewidths (>= 3 nm) around the mean start; widened x2 up to
    twice if a polarization has no pole. Returns {pol: (lam, Q) nearest its start, or None} and all poles."""
    l0 = np.mean([s[0] for s in starts.values()]); Q = min(s[1] for s in starts.values())
    w = max(3 * l0 / Q, 0.003)
    for _ in range(3):
        ll = np.linspace(l0 - w, l0 + w, 41)
        t = scan(p, st, ll, a.thetas[0], kw)
        allp = {pol: poles(ll, t[pol], ll[0], ll[-1]) for pol in ("TE", "TM")}
        if all(allp.values()):
            break
        w *= 2
    best = {pol: (min(allp[pol], key=lambda x: abs(x[0] - starts[pol][0])) if allp[pol] else None) for pol in ("TE", "TM")}
    return best, allp


def track(p, s, pol, allp):
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
                others_05=[x for x in allp if tuple(x) != tuple(s)])


res = json.load(open(a.out)) if os.path.exists(a.out) else dict(
    settings=dict(kw, gap=a.gap, thetas=a.thetas, base=dict(a=A, t=T, r=R), lam0=a.lam0, q0=a.q0, tgrid_nm=GT, ragrid=GR, wide=a.wide, nwide=a.nwide, wide_theta=a.wide_theta, nsub=a.nsub), points=[])
done = {(q["dt2"], q["dr2"]): q for q in res["points"]}   # here dt2 = t (nm), dr2 = r/a


def params(tn, ra):
    t = tn * 1e-3; r = ra * A
    return dict(a=A, t=t, r=r, t2=t, r2=r, c4=0.0, c8=0.0)


def wide(p, lam_c):
    """neighbour scan +-a.wide around lam_c at 0.5 deg and at a.wide_theta; all poles per pol, AAA with more terms"""
    ll = np.linspace(lam_c - a.wide, lam_c + a.wide, a.nwide)
    out = {}
    for th in (a.thetas[0], a.wide_theta):
        t = scan(p, st, ll, th, kw)
        out[str(th)] = {pol: sorted(poles(ll, t[pol], ll[0], ll[-1], max_terms=40)) for pol in ("TE", "TM")}
    return out


def point(dt2, dr2, prev, prev_key=None):
    """prev: {pol: (lam, Q)} at the neighbouring grid point prev_key (None for the base). The line is followed from
    there in a.nsub substeps at 0.5 deg only, then tracked in angle at the target."""
    key = (dt2, dr2)
    if key in done:
        return done[key]
    p = params(dt2, dr2)
    t0 = time.time()
    q = dict(dt2=dt2, dr2=dr2, p=p, start=prev, from_=prev_key, path=[])
    cur = {pol: (prev[pol] if prev else (a.lam0, a.q0)) for pol in ("TE", "TM")}
    if prev_key is not None:
        for f in np.arange(1, a.nsub) / a.nsub:
            pf = params(prev_key[0] + f * (dt2 - prev_key[0]), prev_key[1] + f * (dr2 - prev_key[1]))
            b, _ = at05(pf, cur)
            cur = {pol: (b[pol] or cur[pol]) for pol in ("TE", "TM")}
            q["path"].append([float(f), *[x for pol in ("TE", "TM") for x in cur[pol]]])
    b, allp = at05(p, cur)
    for pol in ("TE", "TM"):
        q[pol] = track(p, b[pol], pol, allp[pol])
    lc = q["TE"]["lam"] if q["TE"] else (q["TM"]["lam"] if q["TM"] else None)
    if lc is not None and a.nwide > 0:
        q["wide"] = wide(p, lc)
    q["sec"] = round(time.time() - t0, 1)
    res["points"].append(q); done[key] = q
    json.dump(res, open(a.out, "w"), indent=1)
    f = lambda b: "lost" if b is None else f"{b['lam']*1e3:8.2f} nm Q {b['Q']:6.0f} c {b['c']:+.4f} M {b['M']:+8.2f}"
    print(f"t {dt2:6.1f} r/a {dr2:.3f} | TE {f(q['TE'])} | TM {f(q['TM'])} | {q['sec']} s", flush=True)
    return q


def nxt(q):
    return {pol: ((q[pol]["lam"], q[pol]["Q"]) if q[pol] else None) for pol in ("TE", "TM")}


def fill(prev_q, start_from):
    s = nxt(prev_q)
    for pol in ("TE", "TM"):
        if s[pol] is None:
            s[pol] = start_from[pol]
    return s


i0 = GT.index(round(T * 1e3, 2)); j0 = GR.index(round(R / A, 4))
base = point(GT[i0], GR[j0], None)
for row in sorted(a.rows, key=lambda x: abs(x - T * 1e3)):
    row = round(row, 2); j = GT.index(row)
    q = base
    step = 1 if j > i0 else -1
    for k in range(i0 + step, j + step, step) if j != i0 else []:
        q = point(GT[k], GR[j0], fill(q, nxt(base)), (q["dt2"], q["dr2"]))
    rowc = q
    for direction in (1, -1):
        q = rowc
        for k in range(j0 + direction, len(GR) if direction > 0 else -1, direction):
            q = point(row, GR[k], fill(q, nxt(rowc)), (q["dt2"], q["dr2"]))
print("done", flush=True)
