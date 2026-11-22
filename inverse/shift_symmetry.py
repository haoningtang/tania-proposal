"""T13b: is the resonance wavelength even in the lateral shift of slab 2? Prelim square structure (a 620, t 220, r 120 nm),
gap 200 nm. Shift along x (shift) and y (shift_y) by +-5/10/20 nm; theta 0.5 and 6 deg in the x-z plane (azimuth 0).
Coarse scan + AAA poles (analyze.poles), then a fine rescan of +-4 linewidths around each pole. Writes shift_symmetry.json."""
import json, os, sys, time, numpy as np
from analyze import poles
from model import bilayer_t
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
A, T, R, GAP = 0.62, 0.22, 0.12, 0.20
kw = dict(n_terms=int(os.environ.get("NT", 80)), ngrid=int(os.environ.get("NG", 96)))
def scan(lams, th, sx, sy):
    tE, tM = [], []
    for i in range(0, len(lams), 16):
        l = lams[i:i + 16]
        o = bilayer_t(l, np.full(len(l), th), A, T, R, GAP, shift=sx / A, shift_y=sy / A, **kw)
        tE.append(np.asarray(o["t_TE"])); tM.append(np.asarray(o["t_TM"]))
    return {"TE": np.concatenate(tE), "TM": np.concatenate(tM)}
def find(th, sx, sy, lo=1.47, hi=1.55):
    lams = np.arange(lo, hi + 1e-9, 0.001); s = scan(lams, th, sx, sy); res = {}
    for pol in ("TE", "TM"):
        P = [p for p in poles(lams, s[pol], lo, hi) if p[1] >= 20]
        fine = []
        for l0, Q in P:
            w = max(4 * l0 / (2 * Q), 0.0005); ll = np.linspace(l0 - w, l0 + w, 41)
            Pf = poles(ll, scan(ll, th, sx, sy)[pol], ll[0], ll[-1])
            if Pf: fine.append(min(Pf, key=lambda x: abs(x[0] - l0)))
        res[pol] = sorted(fine)
    return res
t0 = time.time(); rows = []
for th in (0.5, 6.0):
    base = find(th, 0.0, 0.0); rows.append(dict(theta=th, axis="none", delta_nm=0, poles=base))
    print(json.dumps({"theta": th, "shift": 0, "poles": base}), round(time.time() - t0), "s", flush=True)
    for axis in ("x", "y"):
        for d in (5, 10, 20):
            for sgn in (+1, -1):
                sx, sy = (sgn * d * 1e-3, 0.0) if axis == "x" else (0.0, sgn * d * 1e-3)
                P = find(th, sx, sy); rows.append(dict(theta=th, axis=axis, delta_nm=sgn * d, poles=P))
                print(json.dumps({"theta": th, "axis": axis, "delta": sgn * d, "poles": P}), round(time.time() - t0), "s", flush=True)
json.dump(dict(structure=dict(a=A, t=T, r=R, gap=GAP), settings=kw, rows=rows), open(os.path.join(out, "shift_symmetry.json"), "w"), indent=1)
print("done", round(time.time() - t0), "s")
