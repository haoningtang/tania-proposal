"""Proposal figure for A3/C (signed twist readout), T19a/T19c/T19d: CD at the aligned (AA) point of a twisted bilayer (rcwa4d-mf).
(a) 1 deg twist, 20 um spot: CD spectrum at N 6/7/8 and at -1 deg (N 6); (b) main-line peak CD vs twist with the spot scaled to the moire
period (D = 0.4 and 0.56 x period), error bar = difference between the two highest N, dashed: CD = kappa * theta (fit through 0).
Disc average as in inverse/twist_aperture_cd.py. Wavelengths with |R + T - 1| > 1e-3 are dropped (only the 0.5 deg N 8 run has some, at 1512-1526 nm).
Run from the repo root: python3 docs/figs/make_T19d_twist_scaling_figure.py"""
import os, numpy as np, matplotlib
from scipy.special import j1
matplotlib.use("Agg"); import matplotlib.pyplot as plt
A19, A19D = "runs/20261122-1710_T19a_twist_maps/amps", "runs/20261123-1327_T19d_twist_scaling/amps"
INK, INK2 = "#0b0b0b", "#52514e"; C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False})
LO, HI = 1500, 1512.5


def path(tag):
    for d in (A19D, A19):
        if os.path.exists(f"{d}/tw{tag}.npz"): return f"{d}/tw{tag}.npz"


def disc_cd(tag, D_um=None, frac=None):
    d = np.load(path(tag)); lam = d["lam"]; o = np.argsort(lam)
    cell = float(d["a_nm"]) / np.deg2rad(abs(float(d["twist"]))) / 1e3
    D = frac * cell if frac is not None else D_um
    ok = np.ones(len(lam), bool)
    if "Rx" in d.files:
        ok = np.maximum(np.abs(d["Rx"] + d["Tx"] - 1), np.abs(d["Ry"] + d["Ty"] - 1)) <= 1e-3
    out = []
    for li in o:
        q = np.stack([d["kx"][li], d["ky"][li]], -1) * 2 * np.pi / d["lam"][li]
        x = np.linalg.norm(q[:, None] - q[None], axis=-1) * D * 1e3 / 2
        A = np.where(x > 1e-12, 2 * j1(x) / np.where(x > 1e-12, x, 1), 1.0)
        T = [np.real(np.einsum("mk,nk,mn->", c, np.conj(c), A)) for c in
             ((d["tx"][li][:, :2] + s * 1j * d["ty"][li][:, :2]) / np.sqrt(2) for s in (1, -1))]
        out.append(T[0] - T[1])
    lam, cd, ok = lam[o], 100 * np.array(out), ok[o]
    return lam[ok], cd[ok]


def peak(tag, frac):
    lam, cd = disc_cd(tag, frac=frac); m = (lam >= LO) & (lam <= HI); i = np.argmax(np.abs(cd[m])); return cd[m][i]


fig, (a, b) = plt.subplots(1, 2, figsize=(9.0, 3.5))

# (a) 1 deg, 20 um spot
pk = {}
for tag, lw, al, lab in (("+1_N6", 1.0, 0.45, "N 6"), ("+1_N7", 1.4, 0.7, "N 7"), ("+1_N8", 2.3, 1.0, "N 8")):
    lam, cd = disc_cd(tag, D_um=20); m = (lam >= LO) & (lam <= HI); pk[lab] = cd[m].max()
    a.plot(lam[m], cd[m], color=C1, lw=lw, alpha=al, label=f"+1°, {lab}")
lam, cd = disc_cd("-1_N6", D_um=20); m = (lam >= LO) & (lam <= HI)
a.plot(lam[m], cd[m], color=C2, lw=1.6, label="−1°, N 6")
a.axhline(0, color=INK2, lw=0.7); a.set_xlim(LO, HI); a.set_ylim(-2.3, 2.6)
a.set_xlabel("wavelength (nm)"); a.set_ylabel("CD in a 20 µm spot (%)")
a.set_title("(a) 1° twist: CD at the aligned point", loc="left", fontsize=9.5, color=INK)
a.legend(frameon=False, fontsize=7, loc="upper left")
a.text(HI - 0.1, 2.58, f"peak +{pk['N 8']:.1f} % at 1505.5–1506 nm\nN 6 / 7 / 8: {pk['N 6']:.2f} / {pk['N 7']:.2f} / {pk['N 8']:.2f} %",
       fontsize=7, color=C1, ha="right", va="top")
a.text(1510.3, -2.15, "−1°: opposite sign", fontsize=7, color=C2, ha="center", va="bottom")

# (b) peak CD vs twist, spot scaled with the moire period
runs = {0.25: ("+0.25_N7", "+0.25_N6"), 0.5: ("+0.5_N8", "+0.5_N7"), 1.0: ("+1_N8", "+1_N7"), 2.0: ("+2_N7", "+2_N6")}
res = {}
for frac, col, lab in ((0.4, C1, "D = 0.4 × moiré period"), (0.56, C3, "D = 0.56 × moiré period")):
    th, v, v0 = [], [], []
    for t, (hi_, lo_) in runs.items():
        th.append(t); v.append(peak(hi_, frac)); v0.append(peak(lo_, frac))
    th, v, v0 = map(np.array, (th, v, v0)); e = np.abs(v - v0)
    conv = (np.sign(v) == np.sign(v0)) & (e <= 0.25 * np.abs(v))     # same sign at the two highest N, difference <= 25 %
    k = np.sum(th[conv] * v[conv]) / np.sum(th[conv] ** 2)
    res[frac] = (th, v, e, conv, k)
    b.plot([0, 2.15], [0, 2.15 * k], color=col, lw=1.0, ls=(0, (4, 2.5)))
    b.errorbar(th[conv], v[conv], yerr=e[conv], fmt="o", color=col, ms=6, mec="white", mew=0.9, capsize=2.5, lw=1.2, label=f"{lab}: {k:.1f} %/deg")
    if (~conv).any():
        b.plot(th[~conv], v[~conv], "o", ms=6, mfc="white", mec=col, mew=1.2)
b.set_xlim(0, 2.2); b.set_ylim(0, 4.6)
b.set_xlabel("twist angle θ (deg)"); b.set_ylabel("peak CD at the aligned point (%)")
b.set_title("(b) CD grows linearly with twist", loc="left", fontsize=9.5, color=INK)
b.plot([], [], "o", ms=6, mfc="white", mec=INK2, mew=1.2, label="open: not converged in N")
b.legend(frameon=False, fontsize=7, loc="upper left")
b.set_xticks([0, 0.5, 1, 1.5, 2])
b.text(2.15, 0.25, "spot scaled with the moiré period\n(142 µm at 0.25°, 17.8 µm at 2°);\nerror bar: two highest N", fontsize=7, color=INK2, ha="right")

fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(f"docs/figs/T19d_twist_cd_vs_twist.{ext}", dpi=220)
for frac, (th, v, e, conv, k) in res.items():
    print(f"D/cell {frac}: " + ", ".join(f"{t}°: {x:+.2f}±{y:.2f}{'' if c else ' (not conv.)'}" for t, x, y, c in zip(th, v, e, conv)) + f"  kappa {k:.2f} %/deg")
print("1 deg 20 um peaks:", {k: round(float(x), 2) for k, x in pk.items()})
