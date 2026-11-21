"""S = lam*|dt/dlam| (as in optimize.loss_sharp) per state, angle and polarization, at the start (config init) and
at best.json of a run.  Usage: python sharp_table.py --run ../runs/<folder> [--n_terms N --ngrid G]
Writes <run>/sharp_table.json."""
import argparse, json, os
import numpy as np, jax.numpy as jnp
from model import bilayer_t
ap = argparse.ArgumentParser(); ap.add_argument("--run", required=True)
ap.add_argument("--n_terms", type=int, default=None); ap.add_argument("--ngrid", type=int, default=None)
a = ap.parse_args()
cfg = json.load(open(os.path.join(a.run, "config.json"))); best = json.load(open(os.path.join(a.run, "best.json")))
kw = dict(n_terms=a.n_terms or cfg["n_terms"], ngrid=a.ngrid or cfg["ngrid"])
th = np.asarray(cfg["thetas_deg"]); e = cfg.get("fd_frac", 3e-5); names = cfg["design_vars"]
azs = cfg.get("azimuths_deg", [0.0])
def table(p, lams):
    out = []
    for k, st in enumerate(cfg["states"]):
      for az in azs:
        lam = lams[k]; n = len(th)
        o = bilayer_t(jnp.concatenate([jnp.full(n, lam * (1 - e)), jnp.full(n, lam * (1 + e)), jnp.full(n, lam)]),
                      jnp.asarray(np.concatenate([th, th, th])), p["a"], p["t"], p["r"], st["gap"],
                      shift=st.get("shift", 0.0), c4=p.get("c4", 0.0), c8=p.get("c8", 0.0), r2=p.get("r2"), t2=p.get("t2"),
                      azimuth_deg=az, **kw)
        for pol in ("TE", "TM"):
            t = np.asarray(o["t_" + pol]); T = np.asarray(o["T_" + pol])
            S = np.abs(t[n:2 * n] - t[:n]) / (2 * e)
            out.append(dict(gap=st["gap"], azimuth=az, lam=float(lam), pol=pol, thetas=th.tolist(),
                            S=[round(float(s), 1) for s in S], T=[round(float(x), 3) for x in T[2 * n:]]))
    return out
init = dict(cfg["init"]); init_lams = list(cfg["init_lams"])
if cfg.get("init_from"):  # same rule as optimize.py: the start is the earlier run's best
    prev = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), cfg["init_from"])))
    init.update({n: prev[n] for n in names if n in prev})
    init_lams = [prev.get(f"lam{k}", init_lams[k]) for k in range(len(init_lams))]
res = dict(n_terms=kw["n_terms"], ngrid=kw["ngrid"],
           start=table(init, init_lams),
           best=table({n: best[n] for n in names}, [best[f"lam{k}"] for k in range(len(cfg["states"]))]))
json.dump(res, open(os.path.join(a.run, "sharp_table.json"), "w"), indent=1)
for w in ("start", "best"):
    print(w)
    for r in res[w]: print(f"  gap {r['gap']*1e3:.0f} az {r['azimuth']:g} lam {r['lam']*1e3:.2f} {r['pol']}  S {r['S']}  T {r['T']}")
