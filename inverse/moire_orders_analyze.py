"""T15b analysis: orders_spec_N5_tw*.json (spectra, N 5) and points.json (lam_res, lam_res +- 10 nm; N 3/4/5) -> table.csv, analysis.json, analysis.png"""
import glob, json, os, sys, math
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
D = sys.argv[1]; A = 620.0
spec = {}
for f in glob.glob(os.path.join(D, "orders_spec_N5_tw*.json")):
    r = json.load(open(f)); spec[r[0]["twist"]] = r
pts = json.load(open(os.path.join(D, "points.json")))
rows = []
for key, v in sorted(pts.items(), key=lambda kv: (float(kv[0].split("_")[0]), kv[0])):
    tw = float(key.split("_")[0]); N = int(key.split("_N")[1])
    for rec, tag in zip(v["recs"], ("-10nm", "res", "+10nm")):
        for pol in ("x", "y", "sp", "sm"):
            d = rec[pol]; m = rec["moire"]
            rows.append(dict(twist=tw, N=N, where=tag, lam=rec["lam"], pol=pol, T=d["T"], R=d["R"], T0=d["T0"], R0=d["R0"],
                             T_moire_sum=sum(d["T_moire"]), T_moire_max=max(d["T_moire"]) if m else float("nan"),
                             T_moire_min=min(d["T_moire"]) if m else float("nan"), R_moire_sum=sum(d["R_moire"]), T_rest=d["T_rest"], R_rest=d["R_rest"],
                             theta_out=m[0]["theta_deg"] if m else float("nan"),
                             theta_formula=math.degrees(math.asin(rec["sin_formula"])), n_moire=len(m),
                             az_of_max=m[int(np.argmax(d["T_moire"]))]["azimuth_deg"] if m else float("nan")))
keys = list(rows[0].keys())
with open(os.path.join(D, "table.csv"), "w") as f:
    f.write(",".join(keys) + "\n")
    for r in rows: f.write(",".join(f"{r[k]:.6g}" if isinstance(r[k], float) else str(r[k]) for k in keys) + "\n")
res = dict(rows=rows, lam_res={k: v["lam_res"] for k, v in pts.items()})
# headline: N 5, x input, at resonance, per twist
head = [r for r in rows if r["N"] == 5 and r["where"] == "res" and r["pol"] in ("x", "sp", "sm")]
res["headline_N5_res"] = head
json.dump(res, open(os.path.join(D, "analysis.json"), "w"), indent=1)
for r in head: print(f"tw {r['twist']:+5g} {r['pol']:2s} lam {r['lam']:.1f}: T0 {r['T0']:.3f} moire sum {r['T_moire_sum']:.4f} max {r['T_moire_max']:.4f} min {r['T_moire_min']:.4f} "
                      f"R_moire {r['R_moire_sum']:.4f} rest T {r['T_rest']:.4f} R {r['R_rest']:.4f}; angle {r['theta_out']:.3f} vs {r['theta_formula']:.3f}")
conv = [r for r in rows if r["where"] == "res" and r["pol"] == "x" and abs(r["twist"]) == 1]
for r in conv: print(f"conv tw {r['twist']:+g} N {r['N']}: T0 {r['T0']:.4f} moire max {r['T_moire_max']:.4f} sum {r['T_moire_sum']:.4f}")
fig, ax = plt.subplots(2, 2, figsize=(13, 9))
tws = sorted(t for t in spec if t > 0); cols = plt.cm.viridis(np.linspace(0, 0.9, len(tws)))
for c, t in zip(cols, tws):
    l = [r["lam"] for r in spec[t]]
    ax[0, 0].plot(l, [r["x"]["T0"] for r in spec[t]], color=c, label=f"zero order, Δα={t:g}°")
    ax[0, 0].plot(l, [max(r["x"]["T_moire"]) for r in spec[t]], color=c, ls="--")
    ax[0, 1].plot(l, [sum(r["x"]["T_moire"]) + sum(r["x"]["R_moire"]) for r in spec[t]], color=c, label=f"{t:g}°")
ax[0, 0].set_title("x input, N = 5: zero order (solid), strongest moiré order (dashed)"); ax[0, 0].legend(fontsize=7); ax[0, 0].set_xlabel("λ (nm)")
ax[0, 1].set_title("x input: all four first-order moiré orders, T + R"); ax[0, 1].legend(fontsize=7); ax[0, 1].set_xlabel("λ (nm)")
for pol, mk in (("x", "o"), ("sp", "s"), ("sm", "^")):
    for N, ls in ((3, ":"), (4, "--"), (5, "-")):
        rr = sorted([r for r in rows if r["N"] == N and r["where"] == "res" and r["pol"] == pol], key=lambda r: r["twist"])
        if rr: ax[1, 0].plot([r["twist"] for r in rr], [r["T_moire_max"] for r in rr], marker=mk, ls=ls, label=f"{pol} N{N}", ms=4)
ax[1, 0].set_xlabel("twist Δα (deg)"); ax[1, 0].set_ylabel("T into strongest single moiré order"); ax[1, 0].set_title("at the resonance"); ax[1, 0].legend(fontsize=6, ncol=3)
tt = np.linspace(0.3, 8.5, 50)
ax[1, 1].plot(tt, np.degrees(np.arcsin(2 * (1508 / A) * np.sin(np.radians(tt) / 2))), "k-", label="sin θ = 2(λ/a) sin(Δα/2), λ 1508")
rr = [r for r in rows if r["N"] == 5 and r["pol"] == "x" and r["twist"] > 0]
ax[1, 1].plot([r["twist"] for r in rr], [r["theta_out"] for r in rr], "o", mfc="none", label="moiré order angle (solver k-vectors)")
ax[1, 1].set_xlabel("twist Δα (deg)"); ax[1, 1].set_ylabel("polar angle of first moiré order (deg)"); ax[1, 1].legend(fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(D, "analysis.png"), dpi=110)
