"""Proposal figure: square lattice (C4v) is flat along x only; hex lattice (C6v) is equally flat at every azimuth.
Square: T9b best, 200/192, azimuth 0 vs 45 deg. Hex: T12a E1 lines, 80/96, azimuth 0 vs 30 deg."""
import json, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"; SQ, HX = "#eb6834", "#2a78d6"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False})
def rows(f): return json.load(open(f))["rows"]
sq0 = rows("runs/20261121-0556_T9b_gaps260/hires/analysis.json")
sq45 = rows("runs/20261121-0556_T9b_gaps260/az45/hires/analysis.json")
hx = rows("runs/20261121-1501_T12a_hex_bright/iso/iso_A.json") + rows("runs/20261121-1501_T12a_hex_bright/iso/iso_B.json")
fig, ax = plt.subplots(1, 2, figsize=(8.4, 3.4), gridspec_kw=dict(width_ratios=[1, 1.15]))
a = ax[0]; lim = (0.6, 2000)
a.plot(lim, lim, color=INK2, lw=0.8, ls="--"); a.text(700, 300, "equal flatness\nat both azimuths", fontsize=7, color=INK2, ha="right")
xs, ys, est = [], [], []
for r0, r1 in zip(sq0, sq45):
    for pol in ("TE", "TM"):
        m0 = abs(r0[pol]["M"]); m1 = r1[pol]["M"]
        if m1 != m1:   # pole lost after 3 deg: estimate M from the 3-deg shift
            p = r1[pol]["pts"]; dl = (p[1][1] - p[0][1]) / p[0][1]; m1 = np.sin(np.radians(p[1][0]))**2 / (2 * abs(dl)); est.append(len(xs))
        xs.append(m0); ys.append(abs(m1))
for i, (x, y) in enumerate(zip(xs, ys)):
    a.plot(x, y, "s", color=SQ, ms=6.5, mec="white" if i not in est else SQ, mew=0.8 if i not in est else 1.4,
           mfc=SQ if i not in est else "white", label="square, 0° vs 45°" if i == 0 else None)
hx0 = {(r["cand"], r["gap"], r["p"]["t"]): r for r in hx if r["azimuth"] == 0.0}
first = True
for r in hx:
    if r["azimuth"] != 30.0: continue
    r0 = hx0[(r["cand"], r["gap"], r["p"]["t"])]
    for pol in ("TE", "TM"):
        a.plot(abs(r0[pol]["M"]), abs(r[pol]["M"]), "o", color=HX, ms=6.5, mec="white", mew=0.8, label="hexagonal, 0° vs 30°" if first else None); first = False
a.set_xscale("log"); a.set_yscale("log"); a.set_xlim(*lim); a.set_ylim(*lim)
a.set_xlabel("|M| along a lattice axis (azimuth 0°)"); a.set_ylabel("|M| along the other mirror line")
a.set_title("(a) Flatness at two azimuths", loc="left", fontsize=9.5, color=INK); a.legend(frameon=False, fontsize=7.5, loc="upper left")
b = ax[1]
def shift(r): q = np.array([p[:2] for p in r["pts"]]); return q[:, 0], (q[:, 1] - q[0, 1]) * 1e3
t, y = shift(sq0[1]["TM"]); b.plot(t, y, "-s", color=SQ, lw=2, ms=5, mec="white", mew=0.8, label="square TM, azimuth 0°")
t, y = shift(sq45[1]["TM"]); b.plot(t, y, "--s", color=SQ, lw=2, ms=5, mfc="white", mew=1.2, label="square TM, azimuth 45°")
h0 = [r for r in hx if r["gap"] == 0.38 and r["p"]["t"] == 0.28]
t, y = shift(h0[0]["TE"]); b.plot(t, y, "-", color=HX, lw=7, alpha=0.3, solid_capstyle="round", label="hex TE, azimuth 0°")
t, y = shift(h0[1]["TE"]); b.plot(t, y, "--o", color=HX, lw=2, ms=5, mfc="white", mew=1.2, label="hex TE, azimuth 30°")
b.text(6.25, -3.35, "square: flat along x,\nnot along the diagonal", fontsize=7, color=SQ, va="center")
b.text(6.25, -1.45, "hex: the same curve at 0° and 30°\n(not yet flattened)", fontsize=7, color=HX, va="center")
b.set_xlabel("angle of incidence θ (deg)"); b.set_ylabel("resonance shift Δλ (nm)")
b.set_title("(b) One line, two azimuths (gap 380 nm)", loc="left", fontsize=9.5, color=INK); b.legend(frameon=False, fontsize=7.3, loc="lower left", handlelength=3.2)
b.set_xlim(0, 10.6)
for x_ in ax: x_.grid(True, color=GRID, lw=0.6); x_.set_axisbelow(True)
fig.text(0.01, -0.04, "Square: inverse-designed Si bilayer T9b (gaps 260/380/500 nm), fmmax 200/192; open square = pole lost after 3°, M from the 3° shift. "
         "Hexagonal: two bright E1 lines (a 850 nm), gaps 260/380/500 nm, fmmax 80/96 (|M| ≈ 1–6, not yet optimized).", fontsize=6.6, color=INK2)
plt.tight_layout()
for ext in ("png", "pdf"): plt.savefig(f"docs/figs/isotropy_square_vs_hex.{ext}", dpi=200, bbox_inches="tight")
print("square pairs", [(round(x,1), round(y,1)) for x, y in zip(xs, ys)])
