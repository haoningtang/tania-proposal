"""Transmission spectra of a run's init and best designs, and the dip check at each lam_k.

Usage:  python spectra.py --run ../runs/<name> [--lo 1.46 --hi 1.60 --step 0.001] [--n_terms N --ngrid N]
Writes spectra.json (dip table + minima per curve) and spectra.png into the run folder.
Dip check: T_TE and T_TM at lam_k for every theta in the config (TE = E perpendicular to the plane of incidence).
"""
import argparse, json, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from model import bilayer_t

ap = argparse.ArgumentParser()
ap.add_argument("--run", required=True)
ap.add_argument("--lo", type=float, default=1.46); ap.add_argument("--hi", type=float, default=1.60)
ap.add_argument("--step", type=float, default=0.001)
ap.add_argument("--thetas", default="[0.5,6.0]")
ap.add_argument("--n_terms", type=int, default=None); ap.add_argument("--ngrid", type=int, default=None)
args = ap.parse_args()
cfg = json.load(open(os.path.join(args.run, "config.json")))
best = json.load(open(os.path.join(args.run, "best.json")))
kw = dict(n_terms=args.n_terms or cfg.get("n_terms", 80), ngrid=args.ngrid or cfg.get("ngrid", 96))
names = cfg["design_vars"]; K = len(cfg["states"])
start = dict(cfg["init"]); start_lams = list(cfg["init_lams"])
if cfg.get("init_from"):
    prev = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), cfg["init_from"])))
    start.update({n: prev[n] for n in names if n in prev}); start_lams = [prev[f"lam{k}"] for k in range(K)]
designs = {"start": (start, start_lams), "best": ({n: best[n] for n in names}, [best[f"lam{k}"] for k in range(K)])}

def T(p, st, lam, th):
    lam = np.atleast_1d(lam); out = {"TE": [], "TM": []}
    for i in range(0, len(lam), 16):
        l = lam[i:i + 16]
        o = bilayer_t(l, np.full(l.shape, th), p["a"], p["t"], p["r"], st["gap"], shift=st.get("shift", 0.0),
                      c4=p.get("c4", 0.0), c8=p.get("c8", 0.0), r2=p.get("r2"), **kw)
        out["TE"].append(np.asarray(o["T_TE"])); out["TM"].append(np.asarray(o["T_TM"]))
    return {k: np.concatenate(v) for k, v in out.items()}

res = {"settings": dict(kw, lo=args.lo, hi=args.hi, step=args.step), "dip_check": {}, "curves": {}}
lams = np.arange(args.lo, args.hi + 1e-9, args.step)
ths = json.loads(args.thetas)
fig, axs = plt.subplots(2, K, figsize=(4.2 * K, 6), sharex=True, sharey=True, squeeze=False)
for di, (dn, (p, lk)) in enumerate(designs.items()):
    for k, st in enumerate(cfg["states"]):
        rows = []
        for th in cfg["thetas_deg"]:
            o = T(p, st, lk[k], th)
            rows.append(dict(theta=th, TE=float(o["TE"][0]), TM=float(o["TM"][0])))
        res["dip_check"][f"{dn} g{st['gap']}"] = dict(lam_nm=lk[k] * 1e3, rows=rows,
                                                     max_T=max(max(r["TE"], r["TM"]) for r in rows))
        ax = axs[di, k]
        for th, ls in zip(ths, ["-", "--", ":"]):
            o = T(p, st, lams, th)
            key = f"{dn} g{st['gap']} th{th}"
            res["curves"][key] = {pol: [float(lams[np.argmin(o[pol])] * 1e3), float(o[pol].min())] for pol in o}
            ax.plot(lams * 1e3, o["TE"], "C0" + ls, lw=1, label=f"TE {th}°")
            ax.plot(lams * 1e3, o["TM"], "C3" + ls, lw=1, label=f"TM {th}°")
        ax.axvline(lk[k] * 1e3, color="k", lw=0.6)
        ax.set_title(f"{dn}, gap {st['gap'] * 1e3:.0f} nm", fontsize=9)
        if k == 0: ax.set_ylabel("T")
        if di == 1: ax.set_xlabel("wavelength (nm)")
axs[0, 0].legend(fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(args.run, "spectra.png"), dpi=110)
json.dump(res, open(os.path.join(args.run, "spectra.json"), "w"), indent=1)
for k, v in res["dip_check"].items():
    print(k, f"lam {v['lam_nm']:.1f} nm  max T at lam_k {v['max_T']:.3f}")
