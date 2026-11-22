"""Proposal figure for thrust C: shift symmetry (T13b) and Jacobian rank at the aligned and biased states (T13a)."""
import json, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"; BLUE, ORANGE = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False})
s = json.load(open("runs/20261121-2005_T13b_shift_symmetry/shift_symmetry.json"))["rows"]
def lam(th, ax, dl, pol):
    for r in s:
        if r["theta"] == th and r["axis"] == ax and r["delta_nm"] == dl: return r["poles"][pol][0][0]
J = json.load(open("runs/20261121-2122_T13a_jacobian/jacobian.json"))["points"]
fig, ax = plt.subplots(1, 2, figsize=(8.2, 3.2), gridspec_kw=dict(width_ratios=[1.15, 1]))
a = ax[0]
for pol, c, mk, axis, lab, fill in (("TM", ORANGE, "s", "x", "TE, shift along x", True), ("TE", BLUE, "o", "y", "TM, shift along y", False),
                                     ("TE", INK2, "^", "x", "TM, shift along x (cross term)", True)):
    b0 = lam(0.5, "none", 0, pol)
    ds = np.array([-20, -10, -5, 0, 5, 10, 20]); ys = np.array([0 if d == 0 else (lam(0.5, axis, int(d), pol) - b0) * 1e3 for d in ds])
    k = np.polyfit(ds.astype(float) ** 2, ys, 1)[0]; xx = np.linspace(-22, 22, 120)
    a.plot(xx, k * xx**2, color=c, lw=2 if fill else 0, ls="-" if c != INK2 else "--")
    a.plot(ds, ys, mk, color=c, ms=6 if fill else 9, mfc=c if fill else "none", mec="white" if fill else c, mew=0.8 if fill else 1.4, label=lab)
a.legend(frameon=False, fontsize=7.3, loc="upper center")
a.annotate("aligned: ∂λ/∂δ = 0\n(insensitive to shift noise)", xy=(0, 0), xytext=(-9, 0.16), fontsize=7.5, color=INK2,
           arrowprops=dict(arrowstyle="->", color=INK2, lw=0.8))
a.annotate("biased: ∂λ/∂δ ≠ 0\n(a control knob)", xy=(20, 0.352), xytext=(9.5, 0.18), fontsize=7.5, color=INK2,
           arrowprops=dict(arrowstyle="->", color=INK2, lw=0.8))
a.set_ylim(-0.03, 0.52); a.set_xlabel("lateral shift δ of slab 2 (nm)"); a.set_ylabel("resonance shift Δλ (nm)")
a.set_title("(a) λ is even in the shift", loc="left", fontsize=9.5, color=INK)
b = ax[1]; idx = np.arange(1, 4)
for key, c, lab in (("0,0", BLUE, "aligned (0, 0) nm: rank 1"), ("20,20", ORANGE, "biased (20, 20) nm: rank 3")):
    sv = np.array(J[key]["sv"]); b.semilogy(idx, sv, "-o", color=c, lw=2, ms=6, mec="white", mew=0.8, label=lab)
b.axhline(J["0,0"]["sv"][0] * 1e-2, color=INK2, lw=0.8, ls="--"); b.text(3.05, J["0,0"]["sv"][0] * 1.3e-2, "rank cut", fontsize=7, color=INK2, ha="right")
b.set_xticks(idx, ["σ₁", "σ₂", "σ₃"]); b.set_ylabel("singular value of J (normalized, per nm)")
b.set_title("(b) Jacobian (gap, δx, δy) → optics", loc="left", fontsize=9.5, color=INK); b.legend(frameon=False, fontsize=7.5, loc="lower left")
for x_ in ax: x_.grid(True, color=GRID, lw=0.6); x_.set_axisbelow(True)
fig.text(0.01, -0.03, "Prelim square Si bilayer (a 620, t 220, r 120 nm, gap 200 nm), fmmax RCWA 80/96, θ = 0.5°. J rows: λ, Q of the two modes and TE/TM band curvature (physical names; model.py keys are swapped, corrected 2026-11-22); "
         "±5 nm central differences.", fontsize=6.8, color=INK2)
plt.tight_layout()
for ext in ("png", "pdf"): plt.savefig(f"docs/figs/C_prelim_symmetry_rank.{ext}", dpi=200, bbox_inches="tight")
