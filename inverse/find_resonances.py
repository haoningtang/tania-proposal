"""Find the resonances (pole wavelength, Q) of a design at one angle, for each gap, TE and TM.

Coarse scan + AAA pole fit (analyze.poles), then a fine rescan of +-3 linewidths around each pole for a second fit.
Usage: python find_resonances.py --config configs/X.json --out ../runs/<name> [--lo 1.50 --hi 1.555 --step 0.0005]
Uses cfg["init"] and cfg["states"]. Writes resonances.json.
"""
import argparse, json, os
import numpy as np
from analyze import poles, scan

ap = argparse.ArgumentParser()
ap.add_argument("--config", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--lo", type=float, default=1.50); ap.add_argument("--hi", type=float, default=1.555)
ap.add_argument("--step", type=float, default=0.0005); ap.add_argument("--theta", type=float, default=0.5)
ap.add_argument("--qmin", type=float, default=300)
ap.add_argument("--n_terms", type=int, default=None); ap.add_argument("--ngrid", type=int, default=None)
a = ap.parse_args()
cfg = json.load(open(a.config)); p = dict(cfg.get("fixed", {})); p.update(cfg["init"])
kw = dict(n_terms=a.n_terms or cfg.get("n_terms", 120), ngrid=a.ngrid or cfg.get("ngrid", 128))
os.makedirs(a.out, exist_ok=True)
lams = np.arange(a.lo, a.hi + 1e-12, a.step)
res = dict(params=p, settings=dict(kw, theta=a.theta, lo=a.lo, hi=a.hi, step=a.step), states=[])
for st in cfg["states"]:
    t = scan(p, st, lams, a.theta, kw)
    row = dict(state=st, coarse={}, fine={}, Tmin={})
    for pol in ("TE", "TM"):
        T = np.abs(t[pol]) ** 2
        row["Tmin"][pol] = [float(lams[np.argmin(T)]), float(T.min())]
        P = [x for x in poles(lams, t[pol], a.lo, a.hi) if x[1] >= a.qmin]
        row["coarse"][pol] = P
        fine = []
        for l0, Q in P:
            w = max(3 * l0 / Q, 0.0005)
            ll = np.linspace(l0 - w, l0 + w, 61)
            tf = scan(p, st, ll, a.theta, kw)[pol]
            Tf = np.abs(tf) ** 2
            Pf = poles(ll, tf, ll[0], ll[-1])
            fine.append(dict(coarse=[l0, Q], fit=Pf, Tmin=[float(ll[np.argmin(Tf)]), float(Tf.min())],
                             Tmax=[float(ll[np.argmax(Tf)]), float(Tf.max())]))
        row["fine"][pol] = fine
    res["states"].append(row)
    print(json.dumps({"gap": st["gap"], **{pol: [(round(f["coarse"][0] * 1e3, 2), round(f["coarse"][1]),
          "Tmin", round(f["Tmin"][0] * 1e3, 2), round(f["Tmin"][1], 3)) for f in row["fine"][pol]] for pol in ("TE", "TM")}}),
          flush=True)
json.dump(res, open(os.path.join(a.out, "resonances.json"), "w"), indent=1)
