"""T19d figure from twist_scaling.py output. Usage: python twist_scaling_plot.py OUT (reads OUT/analysis.json, writes OUT/analysis.png)
Panel a: main-line peak CD (signed) vs theta at fixed D/cell; panel b: at fixed D; error bar = last-two-N difference over the main line
(max |CD_N - CD_N-1| on 1500-1512.5 nm, the conservative choice); open marker = only one N available. Dotted: CD proportional to theta
through the 1 deg point. Panel c: CD spectra at D/cell 0.56, highest N per theta."""
import json, os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

OUT = sys.argv[1]; A = json.load(open(os.path.join(OUT, "analysis.json"))); S = A["summary"]
fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))
for a_, names, ttl in ((ax[0], ("f0.25", "f0.4", "f0.56"), "fixed D/cell"), (ax[1], ("D10", "D20", "D50"), "fixed D")):
    for name in names:
        r = sorted([s for s in S if s["ap"] == name], key=lambda s: s["twist"])
        if not r: continue
        th = np.array([s["twist"] for s in r]); y = np.array([s["signed_main"] for s in r])
        e = np.array([s.get("dN_main", np.nan) for s in r]); one = np.isnan(e)
        lab = (f"D/cell {name[1:]}" if name[0] == "f" else f"D {name[1:]} µm")
        h = a_.errorbar(th[~one], y[~one], yerr=e[~one], fmt="o-", capsize=3, label=lab)
        a_.plot(th[one], y[one], "o", mfc="none", color=h[0].get_color())
        i1 = np.where(np.isclose(th, 1))[0]
        if len(i1):
            tt = np.linspace(0.2, 2.1, 50); a_.plot(tt, y[i1[0]] * tt, ":", color=h[0].get_color(), lw=1)
    a_.axhline(0, color="k", lw=0.5); a_.set_xlabel("twist θ (deg)"); a_.set_ylabel("main-line peak CD (signed)")
    a_.set_title(f"disc CD at AA, {ttl}"); a_.legend(fontsize=8)
for tag, r in sorted(A["per_run"].items(), key=lambda kv: (kv[1]["twist"], kv[1]["N"])):
    Ns = [x["N"] for x in A["per_run"].values() if x["twist"] == r["twist"]]
    if r["N"] != max(Ns) or "f0.56" not in r["ap"]: continue
    a = r["ap"]["f0.56"]; ax[2].plot(a["lam"], a["CD"], "-", lw=1, label=f"θ {r['twist']:g}° N {r['N']} (D {a['D_um']:.0f} µm)")
ax[2].axvspan(1500, 1512.5, color="0.9"); ax[2].axhline(0, color="k", lw=0.5); ax[2].set_xlabel("λ (nm)"); ax[2].set_ylabel("CD")
ax[2].set_title("disc CD at D/cell 0.56"); ax[2].legend(fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "analysis.png"), dpi=110); print("wrote", os.path.join(OUT, "analysis.png"))
