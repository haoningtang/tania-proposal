"""Proposal figure for B (both polarizations flat): T16c hex sqrt3 x sqrt3 supercell, base row t 280 nm, gap 380 nm, a 850 nm.
Band curvature c (T16b Q-matched slope; |c| <= 0.05 <=> |M| >= 10) of TE and TM versus the supercell knob Delta = (r1 - r2)/a,
(a) for the gap-tunable E1 line, (b) for the second bright doublet (1463-1471 nm), followed by continuity in lambda and Q: there Delta moves both curvatures together.
Physical polarization names (T16c table, written with the old swapped model.py keys and converted by hex_r3_analyze.py).
Run from the repo root: python3 docs/figs/make_T16c_supercell_figure.py [runs/<..>_T16c_hex_r3]"""
import csv, json, sys, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
RUN = sys.argv[1] if len(sys.argv) > 1 else "runs/20261122-1735_T16c_hex_r3"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"; C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False})

E1 = sorted((v for v in json.load(open(f"{RUN}/analysis.json"))["E1"].values()
             if int(v["t"]) == 280 and int(v["gap"]) == 380), key=lambda v: v["D"])
rows = [r for r in csv.DictReader(open(f"{RUN}/table.csv"))
        if int(float(r["t"])) == 280 and int(float(r["gap"])) == 380 and r["doublet"] == "True" and r["c_TE_0"] not in ("", "nan")]
# second bright doublet: start at Delta 0 (1467.0 nm, Q 79) and follow the nearest line with Q 60-170 in 1460-1475 nm
doub, lam_prev = {}, None
for sgn in (1, -1):
    lam_prev = 1467.0
    for D in sorted({float(r["D"]) for r in rows if sgn * float(r["D"]) >= 0 and abs(float(r["D"])) <= 0.05}, key=abs):
        cand = [r for r in rows if float(r["D"]) == D and 1460 <= float(r["lam"]) <= 1475 and 60 <= float(r["Q_TE"]) <= 170]
        r = min(cand, key=lambda r: abs(float(r["lam"]) - lam_prev)); lam_prev = float(r["lam"]); doub[D] = r

fig, (a, b) = plt.subplots(1, 2, figsize=(9.0, 3.5), sharey=True)
for ax in (a, b):
    ax.axhspan(-0.05, 0.05, color=C3, alpha=0.18, lw=0)
    ax.axhline(0, color=INK2, lw=0.7)
    ax.set_xlim(-0.09, 0.09); ax.set_ylim(-0.75, 0.85)
    ax.set_xlabel("supercell knob Δ = (r₁ − r₂)/a")

x = np.array([v["D"] for v in E1])
a.plot(x, [v["c_TE_0"] for v in E1], "o-", color=C2, lw=2, ms=4, label="TE")
a.plot(x, [v["c_TM_0"] for v in E1], "o-", color=C1, lw=2, ms=4, label="TM")
a.set_ylabel("band curvature c")
a.set_title("(a) E1 line (tunes with the gap): Δ flattens TM only", loc="left", fontsize=9.5, color=INK)
a.text(0.0, -0.58, "TE stays curved (c ≈ −0.46)", fontsize=7, color=C2, ha="center")
a.text(0.0, 0.17, "TM flat at |Δ| ≈ 0.045", fontsize=7, color=C1, ha="center")
from matplotlib.patches import Patch
h, l = a.get_legend_handles_labels(); h.append(Patch(color=C3, alpha=0.35, lw=0)); l.append("target |c| ≤ 0.05 (M ≥ 10)")
a.legend(h, l, frameon=False, fontsize=7, loc="upper left")

xd = np.array(sorted(doub)); rr = [doub[k] for k in xd]
b.plot(xd, [float(r["c_TE_0"]) for r in rr], "o-", color=C2, lw=2, ms=4, label="TE")
b.plot(xd, [float(r["c_TM_0"]) for r in rr], "o-", color=C1, lw=2, ms=4, label="TM")
b.set_title("(b) Second doublet (1463–1471 nm): TE and TM move together", loc="left", fontsize=9.5, color=INK)
b.text(-0.05, -0.40, "TE flat at Δ ≈ −0.03,\nwhere TM is +0.3", fontsize=7, color=C2, ha="left")
b.text(0.033, 0.12, "TM flat at Δ ≈ +0.03,\nwhere TE is −0.36", fontsize=7, color=C1, ha="left")
b.text(-0.087, -0.70, "c_TE − c_TM stays −0.33 to −0.41", fontsize=7, color=INK2, ha="left")
b.text(0.088, 0.62, f"Q {min(float(r['Q_TE']) for r in rr):.0f}–{max(float(r['Q_TE']) for r in rr):.0f}", fontsize=7, color=INK2, ha="right")
fig.text(0.5, 0.005, "Hex √3×√3 supercell, a 850 nm, t 280 nm, gap 380 nm; azimuth 0° (30° differs by ≤ 0.03 in (a), ≤ 0.15 in (b)). "
         "Best line in the full scan: worst |M| 3.1, about 3× short of M ≥ 10.", ha="center", fontsize=7, color=INK2)
fig.tight_layout(rect=(0, 0.04, 1, 1))
for ext in ("png", "pdf"):
    fig.savefig(f"docs/figs/T16c_supercell_knobs.{ext}", dpi=220)
print("doublet:", [(k, round(float(doub[k]["lam"]), 2), round(float(doub[k]["Q_TE"])), doub[k]["c_TE_0"], doub[k]["c_TM_0"]) for k in sorted(doub)])
