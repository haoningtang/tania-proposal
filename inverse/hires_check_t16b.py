"""T16b spot check: 0.5 and 3 deg scans (+-4 nm, 61 pts) at given (t nm, r/a), a 0.85, gap 0.38, symmetric; poles per pol.
Usage: python hires_check_t16b.py --t 340 --ra 0.21 --lam 1.66851 --n_terms 200 --ngrid 192 --out file.json"""
import argparse, json
import numpy as np
from analyze import scan
from curv_map_sym_poles import poles
ap = argparse.ArgumentParser()
ap.add_argument("--t", type=float); ap.add_argument("--ra", type=float); ap.add_argument("--lam", type=float)
ap.add_argument("--n_terms", type=int, default=200); ap.add_argument("--ngrid", type=int, default=192); ap.add_argument("--out")
a = ap.parse_args()
p = dict(a=0.85, t=a.t * 1e-3, r=a.ra * 0.85, t2=a.t * 1e-3, r2=a.ra * 0.85, c4=0.0, c8=0.0)
kw = dict(n_terms=a.n_terms, ngrid=a.ngrid, lattice="hex", azimuth_deg=0.0)
ll = np.linspace(a.lam - 0.004, a.lam + 0.004, 61)
out = dict(t=a.t, ra=a.ra, n_terms=a.n_terms, ngrid=a.ngrid)
for th in (0.5, 3.0):
    t = scan(p, dict(gap=0.38, shift=0.0), ll, th, kw)
    out[str(th)] = {pol: sorted(poles(ll, t[pol], ll[0], ll[-1], 20)) for pol in ("TE", "TM")}
    print(th, {k: [(round(l * 1e3, 3), round(Q)) for l, Q in v] for k, v in out[str(th)].items()}, flush=True)
json.dump(out, open(a.out, "w"), indent=1)
