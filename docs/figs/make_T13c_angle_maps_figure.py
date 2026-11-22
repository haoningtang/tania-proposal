"""Replot of the T13c angle maps with physical polarization names (model.py keys are swapped: key TE = physical TM).
Run from the repo root: python3 docs/figs/make_T13c_angle_maps_figure.py"""
import json, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
INK, INK2 = "#0b0b0b", "#52514e"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "xtick.color": INK2, "ytick.color": INK2})
d = json.load(open("runs/20261121-2124_T13c_angle_maps/maps.json"))
amax = max(d["maps_axes_deg"])
PHYS = {"TE": "TM (p, E in the plane of incidence)", "TM": "TE (s, E ⊥ plane of incidence)", "unpol": "unpolarized"}
fig, axs = plt.subplots(2, 3, figsize=(10, 6.4), constrained_layout=True)
for i, k in enumerate((str(d["g_zero"]), "200")):
    m = d["maps"][k]
    for j, key in enumerate(("TE", "TM", "unpol")):
        im = axs[i, j].imshow(np.array(m[key]).T, origin="lower", extent=[-0.5, amax + 0.5, -0.5, amax + 0.5], cmap="Blues_r", vmin=0, vmax=1)
        c = m["c_TE"] if key == "TE" else (m["c_TM"] if key == "TM" else None)
        extra = f", curvature c {c:+.4f}" if c is not None else ""
        axs[i, j].set_title(f"gap {float(k):.1f} nm, {PHYS[key]}\nλ {m['lam_probe']:.2f} nm{extra}", fontsize=8, color=INK)
        axs[i, j].set_xlabel("θx (deg)"); axs[i, j].set_ylabel("θy (deg)")
fig.colorbar(im, ax=axs, shrink=0.8, label="transmission |t|²")
fig.suptitle("Prelim square Si bilayer (a 620, t 220, r 120 nm), T(θx, θy) at the 0.5° resonance λ, fmmax 80/96 (T13c). "
             "Top: gap where the TM band is flat (81.85 nm); bottom: gap 200 nm.\nPhysical polarization names; model.py keys are swapped "
             "(corrected 2026-11-22).", fontsize=8.5, color=INK2)
for ext in ("png", "pdf"): fig.savefig(f"docs/figs/T13c_angle_maps.{ext}", dpi=170)
print("saved docs/figs/T13c_angle_maps.png")
