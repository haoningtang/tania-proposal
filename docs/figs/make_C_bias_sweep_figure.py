"""Proposal figure for thrust C: Jacobian (gap, dx, dy) -> optics along a diagonal bias sweep (T13a + T17a)."""
import csv, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"; C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False})
rows = {r["point"]: r for r in csv.DictReader(open("runs/20261122-0400_T17a_bias_sweep/table.csv"))}
diag = ["0,0", "5,5", "10,10", "20,20", "30,30", "40,40"]
d = np.array([float(p.split(",")[0]) for p in diag])
sv = np.array([[float(rows[p][f"sv{i}"]) for i in (1, 2, 3)] for p in diag])
cond = np.array([float(rows[p]["cond_13"]) for p in diag]); g = np.array([float(rows[p]["g_abs"]) for p in diag])
fig, ax = plt.subplots(1, 3, figsize=(10.2, 3.2))
a = ax[0]
for i, (c, lab) in enumerate(((C1, "σ₁"), (C2, "σ₂"), (C3, "σ₃"))):
    a.semilogy(d[1:], sv[1:, i], "-o", color=c, lw=2, ms=5.5, mec="white", mew=0.8, label=lab)
    a.semilogy([0], [max(sv[0, i], 1e-12)], "o", color=c, ms=5.5, mec="white", mew=0.8)
a.axhline(sv[:, 0].max() * 1e-2, color=INK2, lw=0.8, ls="--"); a.text(40, sv[:, 0].max() * 1.3e-2, "rank cut", fontsize=7, color=INK2, ha="right")
for p, mk, lab in (("20,0", "s", "bias along x only"), ("0,20", "^", "bias along y only")):
    a.semilogy([20], [float(rows[p]["sv3"])], mk, color=INK2, ms=6.5, mfc="white", mew=1.3, label=f"σ₃, {lab}")
a.text(1.2, 3e-11, "aligned:\nrank 1", fontsize=7.5, color=INK2)
a.set_ylim(1e-12, 1e-2); a.set_xlabel("bias (δ, δ) of slab 2 (nm)"); a.set_ylabel("singular value of J (normalized, per nm)")
a.set_title("(a) Rank 3 needs a two-axis bias", loc="left", fontsize=9.5, color=INK); a.legend(frameon=False, fontsize=6.8, loc="center right")
b = ax[1]
b.semilogy(d[1:], cond[1:], "-o", color=C1, lw=2, ms=5.5, mec="white", mew=0.8)
b.plot([20], [cond[3]], "o", ms=12, mfc="none", mec=C2, mew=1.8)
b.annotate(f"best: {cond[3]:.0f} at (20, 20) nm", xy=(20, cond[3]), xytext=(24, 40), fontsize=7.5, color=INK2,
           arrowprops=dict(arrowstyle="->", color=INK2, lw=0.8))
from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
b.yaxis.set_major_locator(FixedLocator([10, 20, 50, 100])); b.yaxis.set_major_formatter(FixedFormatter(["10", "20", "50", "100"])); b.yaxis.set_minor_locator(NullLocator()); b.set_ylim(9, 120)
b.set_xlabel("bias (δ, δ) of slab 2 (nm)"); b.set_ylabel("condition number σ₁/σ₃")
b.set_title("(b) How independent the 3 controls are", loc="left", fontsize=9.5, color=INK)
c = ax[2]
dd = np.linspace(0, 42, 100); k = 4.66e-4
c.plot(dd, 2 * k * dd * np.sqrt(2), color=C2, lw=2, label="2k|δ| (k from T13b/T17a fits)")
c.plot(d, g, "o", color=C2, ms=6, mec="white", mew=0.8, label="from the Jacobian")
c.axhline(float(rows["20,20"]["dlam_dgap"]), color=C1, lw=1.5, ls="--"); c.text(1, 0.236, "∂λ/∂gap = 0.24 nm/nm", fontsize=7, color=C1, va="top")
c.set_ylim(0, 0.26); c.set_xlabel("bias (δ, δ) of slab 2 (nm)"); c.set_ylabel("|∂λ/∂δ| (nm per nm of shift)")
c.set_title("(c) Cost: sensitivity to shift noise", loc="left", fontsize=9.5, color=INK); c.legend(frameon=False, fontsize=7, loc="center left")
for x_ in ax: x_.grid(True, color=GRID, lw=0.6); x_.set_axisbelow(True)
fig.text(0.01, -0.04, "Prelim square Si bilayer (a 620, t 220, r 120 nm, gap 200 nm), fmmax 80/96, ±5 nm central differences. J: (gap, δx, δy) → λ and Q of the two "
         "0.5° modes and the TE/TM band curvature.", fontsize=6.8, color=INK2)
plt.tight_layout()
for ext in ("png", "pdf"): plt.savefig(f"docs/figs/C_bias_sweep.{ext}", dpi=200, bbox_inches="tight")
