"""Proposal figure for the T9b design (square-lattice Si bilayer, best along x). Data: runs/20261121-0556_T9b_gaps260/hires/analysis.json (200/192)."""
import json, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
d = json.load(open("runs/20261121-0556_T9b_gaps260/hires/analysis.json"))
C = {0.26: "#2a78d6", 0.38: "#eb6834", 0.5: "#1baf7a"}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(1, 3, figsize=(10.5, 3.3), gridspec_kw=dict(width_ratios=[1.35, 1, 0.9]))
# (a) shift vs angle, with the |M| >= 10 window
th = np.linspace(0, 10, 200); lam0 = 1555.0
win = lam0 * np.sin(np.radians(th))**2 / 20
a = ax[0]
a.fill_between(th, -win, win, color=GRID, lw=0, label="|M| ≥ 10 window")
a.axvline(6.5, color=INK2, lw=0.8, ls=":"); a.text(6.6, 2.6, "±6.5° acceptance", color=INK2, fontsize=7.5)
for r in d["rows"]:
    g = r["state"]["gap"]
    for pol, ls, mk in (("TE", "-", "o"), ("TM", "--", "s")):
        x = r[pol]
        if not x: continue
        q = np.array([p[:2] for p in x["pts"]]); y = (q[:, 1] - q[0, 1]) * 1e3
        a.plot(q[:, 0], y, ls, marker=mk, ms=4.5, lw=2, color=C[g], mec="white", mew=0.8)
        dy = {("TM", 0.26): 0.12, ("TE", 0.5): -0.1}.get((pol, g), 0.0)
        a.text(q[-1, 0] + 0.15, y[-1] + dy, f"{pol} {int(g*1000)}", color=INK2, fontsize=7, va="center")
a.set_xlim(0, 11.8); a.set_ylim(-2.2, 3.6)
a.set_xlabel("angle of incidence θ (deg)"); a.set_ylabel("resonance shift Δλ (nm)")
a.set_title("(a) Shift with angle, azimuth 0°", loc="left", fontsize=9.5, color=INK)
a.legend(frameon=False, fontsize=7.5, loc="upper left")
# (b) |M| per gap and polarization
b = ax[1]; xs = np.arange(3); w = 0.36
gaps = [r["state"]["gap"] for r in d["rows"]]
for k, pol in enumerate(("TE", "TM")):
    M = [abs(r[pol]["M"]) for r in d["rows"]]
    bars = b.bar(xs + (k - 0.5) * w, M, w * 0.92, color=[C[g] for g in gaps], hatch=None if pol == "TE" else "///",
                 edgecolor="white", lw=0.8)
    for xi, m in zip(xs + (k - 0.5) * w, M):
        ok = m >= 10
        b.text(xi, m * 1.15, f"{m:.0f}" + (" ✓" if ok else " ✗"), ha="center", fontsize=7, color=INK if ok else "#c0392b")
b.set_yscale("log"); b.set_ylim(1, 3000); b.axhline(10, color=INK, lw=1, ls="--")
b.text(-0.62, 11.5, "target 10", fontsize=7, color=INK2, ha="left", va="bottom")
b.set_xticks(xs, [f"gap {int(g*1000)}" for g in gaps]); b.set_ylabel("|M|  (TE solid, TM hatched)")
b.set_title("(b) Flatness |M|: 5 of 6 ≥ 10", loc="left", fontsize=9.5, color=INK)
# (c) tuning
c = ax[2]
L = [r["TE"]["lam"] * 1e3 for r in d["rows"]]; Q = [r["TE"]["Q"] for r in d["rows"]]
c.plot([g * 1000 for g in gaps], L, "-", color=INK2, lw=1.5, zorder=1)
for g, l, qq in zip(gaps, L, Q):
    c.scatter(g * 1000, l, s=60, color=C[g], edgecolor="white", lw=1, zorder=2)
    c.text(g * 1000 + 12, l - 0.5, f"Q {qq:.0f}", ha="left", va="top", fontsize=7, color=INK2)
tune = (L[-1] - L[0]) / np.mean(L) * 100
c.set_xlabel("air gap (nm)"); c.set_ylabel("resonance λ at 0.5° (nm)"); c.set_ylim(1527, 1578); c.set_xlim(240, 540)
c.set_title(f"(c) MEMS tuning {tune:.1f} %", loc="left", fontsize=9.5, color=INK)
for x_ in ax:
    x_.grid(True, color=GRID, lw=0.6); x_.set_axisbelow(True)
fig.text(0.01, -0.02, "Square-lattice Si bilayer (a 728, t 279, r 241/240 nm), fmmax RCWA n_terms 200 / ngrid 192. "
         "Azimuth 0° only; along the lattice diagonal the lines move 2–8 nm by 6° (see hex lattice).", fontsize=7, color=INK2)
plt.tight_layout()
for ext in ("png", "pdf"):
    plt.savefig(f"docs/figs/T9b_square_best.{ext}", dpi=200, bbox_inches="tight")
print("tuning", round(tune, 2))
