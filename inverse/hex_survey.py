"""T11a hexagonal-lattice survey: for each (a, r/a, t) in cfg["survey"] (t2 = t, r2 = r, c4 = c8 = 0, one gap), scan
lam_range at theta (deg), find poles (AAA fit, analyze.poles) with Q >= qmin for TE and TM, refine each with a fine scan of
+-3 linewidths, and list TE/TM-degenerate pairs (|lam_TE - lam_TM| <= pair_tol). Uses cfg["lattice"] (should be "hex").

Usage: python hex_survey.py --config configs/stage11a_hex_survey.json --out ../runs/<name> [--qmin 300 --pair_tol 0.0002]
Writes survey.json (every design: all poles + pairs) and candidates.json (pairs sorted by |lam - 1550 nm|); resumes from an
existing survey.json (skips designs already done)."""
import argparse, json, os, itertools, time
import numpy as np
from analyze import poles, scan

ap = argparse.ArgumentParser()
ap.add_argument("--config", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--qmin", type=float, default=300); ap.add_argument("--pair_tol", type=float, default=0.0002)
a = ap.parse_args()
cfg = json.load(open(a.config)); sv = cfg["survey"]
kw = dict(n_terms=cfg.get("n_terms", 80), ngrid=cfg.get("ngrid", 96), lattice=cfg.get("lattice", "hex"))
st = dict(gap=sv["gap"], shift=0.0)
lo, hi = sv["lam_range"]; lams = np.arange(lo, hi + 1e-12, sv["lam_step"]); th = sv["theta"]
os.makedirs(a.out, exist_ok=True)
fn = os.path.join(a.out, "survey.json")
done = json.load(open(fn)) if os.path.exists(fn) else dict(settings=dict(kw, gap=sv["gap"], lam_range=sv["lam_range"],
                                                                          lam_step=sv["lam_step"], theta=th, qmin=a.qmin,
                                                                          pair_tol=a.pair_tol), designs=[])
have = {(d["p"]["a"], d["p"]["r_over_a"], d["p"]["t"]) for d in done["designs"]}

def refine(p, l0, Q, pol):
    w = max(3 * l0 / Q, 0.0005)
    ll = np.linspace(l0 - w, l0 + w, 41)
    tf = scan(p, st, ll, th, kw)[pol]
    Pf = [x for x in poles(ll, tf, ll[0], ll[-1])]
    if not Pf:
        return None
    best = min(Pf, key=lambda x: abs(x[0] - l0))
    return [float(best[0]), float(best[1])]

for A, ra, T in itertools.product(sv["a"], sv["r_over_a"], sv["t"]):
    if (A, ra, T) in have:
        continue
    t0 = time.time()
    p = dict(a=A, t=T, r=ra * A, r2=ra * A, t2=T, c4=0.0, c8=0.0)
    t = scan(p, st, lams, th, kw)
    rec = dict(p=dict(a=A, r_over_a=ra, t=T, r=ra * A), poles={}, pairs=[])
    for pol in ("TE", "TM"):
        P = [x for x in poles(lams, t[pol], lo, hi) if x[1] >= 0.5 * a.qmin]   # refine slightly below qmin too
        R = [refine(p, l0, Q, pol) for l0, Q in P]
        rec["poles"][pol] = [r for r in R if r is not None and r[1] >= a.qmin]
    for lte, qte in rec["poles"]["TE"]:
        for ltm, qtm in rec["poles"]["TM"]:
            if abs(lte - ltm) <= a.pair_tol:
                rec["pairs"].append(dict(lam=0.5 * (lte + ltm), dlam=lte - ltm, Q_TE=qte, Q_TM=qtm))
    rec["wall_s"] = round(time.time() - t0, 1)
    done["designs"].append(rec)
    json.dump(done, open(fn, "w"), indent=1)
    print(json.dumps(dict(a=A, r_over_a=ra, t=T, nTE=len(rec["poles"]["TE"]), nTM=len(rec["poles"]["TM"]),
                          pairs=[(round(x["lam"] * 1e3, 2), round(min(x["Q_TE"], x["Q_TM"]))) for x in rec["pairs"]],
                          s=rec["wall_s"])), flush=True)

cands = [dict(d["p"], **x) for d in done["designs"] for x in d["pairs"]]
cands.sort(key=lambda c: abs(c["lam"] - 1.55))
json.dump(cands, open(os.path.join(a.out, "candidates.json"), "w"), indent=1)
print("candidates (closest to 1550 nm):")
for c in cands[:15]:
    print(f"  a {c['a']*1e3:.0f} r/a {c['r_over_a']:.2f} t {c['t']*1e3:.0f}: lam {c['lam']*1e3:.2f} nm  dlam {c['dlam']*1e3:+.3f}"
          f"  Q {c['Q_TE']:.0f}/{c['Q_TM']:.0f}")
