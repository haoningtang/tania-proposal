"""T12a summary: collect followed lines (follow/*.json) and isotropy results (iso/iso_*.json) of a hex bright survey run into
analysis.json and analysis.png.  Usage: python t12a_summary.py ../runs/<T12a run>"""
import sys, json, glob, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = sys.argv[1]
S = json.load(open(os.path.join(R, "survey.json")))
lines = []
for fn in sorted(glob.glob(os.path.join(R, "follow", "*.json"))):
    f = json.load(open(fn)); p = f["p"]
    row = dict(a=p["a"], r_over_a=p["r_over_a"], t=p["t"], lam380=f["lam380"],
               TE=[[g, l, q] for g, l, q in f["TE"]], TM=[[g, l, q] for g, l, q in f["TM"]],
               tuning_TE=f.get("TE_tuning"), tuning_TM=f.get("TM_tuning"),
               lost=not ("TE_tuning" in f and "TM_tuning" in f))
    lines.append(row)
lines.sort(key=lambda r: -abs(r["tuning_TE"] or 0))
iso = {}
for fn in sorted(glob.glob(os.path.join(R, "iso", "iso_*.json"))):
    iso[os.path.basename(fn)[4:-5]] = [dict(gap=r["gap"], azimuth=r["azimuth"],
                                           **{pol: None if r[pol] is None else dict(lam=r[pol]["lam"], Q=r[pol]["Q"], M=r[pol]["M"])
                                              for pol in ("TE", "TM")}) for r in json.load(open(fn))["rows"]]
out = dict(n_designs=len(S["designs"]), survey_settings=S["settings"], n_followed=len(lines), lines=lines, isotropy=iso)
json.dump(out, open(os.path.join(R, "analysis.json"), "w"), indent=1)

# figure
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]; INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#e4e3dd"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw=dict(width_ratios=[1.2, 1]))
ok = [r for r in lines if not r["lost"]]
lab = lambda r: f"a {r['a']*1e3:.0f}, r/a {r['r_over_a']:.2f}, t {r['t']*1e3:.0f} ({r['lam380']*1e3:.0f} nm)"
for k, r in enumerate(ok):
    g = np.array([x[0] for x in r["TE"]]) * 1e3; l = np.array([x[1] for x in r["TE"]])
    l0 = l[np.argmin(abs(g - 380))]; y = 100 * (l - l0) / l0
    if k < 4:
        ax[0].plot(g, y, "-o", color=C[k], lw=2, ms=4, label=lab(r), zorder=3)
        ax[0].annotate(f"{100*r['tuning_TE']:+.2f} %", (g[0], y[0]), xytext=(-6, 0), textcoords="offset points",
                       ha="right", va="center", color=INK, fontsize=8)
    else:
        ax[0].plot(g, y, "-", color="#b5b4ad", lw=1, zorder=2)
ax[0].set_xlabel("gap (nm)"); ax[0].set_ylabel("line shift from gap 380 (%)")
ax[0].set_xlim(215, 510); ax[0].grid(color=GRID, lw=0.6); ax[0].legend(frameon=False, fontsize=7.5, loc="lower right")
ax[0].set_title("Followed TE line vs gap (TM within 0.001 %); gray: other lines", fontsize=9, color=INK, loc="left")
y = np.arange(len(ok))
ax[1].axvspan(-10, -2, color="#f3f2ee"); ax[1].axvspan(2, 10, color="#f3f2ee")
for x in (-2, 2):
    ax[1].axvline(x, color=MUTED, lw=1, ls="--")
ax[1].scatter([100 * r["tuning_TE"] for r in ok], y, s=36, color=[C[k] if k < 4 else "#8d8c85" for k in range(len(ok))], zorder=3)
ax[1].set_yticks(y); ax[1].set_yticklabels([lab(r) for r in ok], fontsize=7); ax[1].invert_yaxis()
ax[1].set_xlim(-3, 3); ax[1].set_xlabel("tuning (λ(260) − λ(500)) / λ  (%)"); ax[1].grid(axis="x", color=GRID, lw=0.6)
ax[1].set_title(f"Followed tuning, {len(ok)} lines ({len(lines) - len(ok)} lost); target |tuning| ≥ 2 %", fontsize=9, color=INK, loc="left")
fig.suptitle(f"T12a hex bright-doublet survey: {len(S['designs'])}/60 designs, 80/96, θ 0.5°, azimuth 0°", fontsize=10, color=INK)
fig.tight_layout(); fig.savefig(os.path.join(R, "analysis.png"), dpi=130)
print(json.dumps(dict(n_designs=out["n_designs"], n_followed=len(lines),
                      top=[(lab(r), round(100 * r["tuning_TE"], 3)) for r in ok[:5]])))
