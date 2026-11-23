"""Proposal figure for A3/C (twist sign): CD at the aligned (AA) point of a twisted bilayer, from the T19a moire amplitudes (rcwa4d-mf).
Spot-averaged CD over a disc of diameter D centred at AA, same definition as inverse/twist_aperture_cd.py:
E_sigma(r) = sum_m c_m exp(i q_m . r), disc average of |E|^2 = sum_mm' c_m c_m'^* 2 J1(|dq| R)/(|dq| R), CD = T_sigma+ - T_sigma-.
Run from the repo root: python3 docs/figs/make_T19c_twist_cd_figure.py [runs/<..>_T19a_twist_maps]"""
import sys, numpy as np, matplotlib
from scipy.special import j1
matplotlib.use("Agg"); import matplotlib.pyplot as plt
RUN = sys.argv[1] if len(sys.argv) > 1 else "runs/20261122-1710_T19a_twist_maps"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"; C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False})


def disc_cd(tag, D_um):
    d = np.load(f"{RUN}/amps/tw{tag}.npz"); lam = d["lam"]; o = np.argsort(lam); out = []
    for li in o:
        q = np.stack([d["kx"][li], d["ky"][li]], -1) * 2 * np.pi / d["lam"][li]
        x = np.linalg.norm(q[:, None] - q[None], axis=-1) * D_um * 1e3 / 2
        A = np.where(x > 1e-12, 2 * j1(x) / np.where(x > 1e-12, x, 1), 1.0)
        T = [np.real(np.einsum("mk,nk,mn->", c, np.conj(c), A)) for c in
             ((d["tx"][li][:, :2] + s * 1j * d["ty"][li][:, :2]) / np.sqrt(2) for s in (1, -1))]
        out.append(T[0] - T[1])
    return lam[o], 100 * np.array(out)            # CD in %


fig, (a, b) = plt.subplots(1, 2, figsize=(9.0, 3.5))
lo, hi = 1500, 1512.5

# (a) 20 um spot at +1 deg, N 6/7/8, and -1 deg (N 6)
peaks = {}
for tag, lw, alpha, lab in (("+1_N6", 1.0, 0.45, "N 6"), ("+1_N7", 1.4, 0.7, "N 7"), ("+1_N8", 2.3, 1.0, "N 8")):
    lam, cd = disc_cd(tag, 20); m = (lam >= lo) & (lam <= hi); peaks[lab] = cd[m].max()
    a.plot(lam[m], cd[m], color=C1, lw=lw, alpha=alpha, label=f"+1°, {lab}")
lam, cd = disc_cd("-1_N6", 20); m = (lam >= lo) & (lam <= hi)
a.plot(lam[m], cd[m], color=C2, lw=1.6, label="−1°, N 6")
a.axhline(0, color=INK2, lw=0.7)
a.set_xlim(lo, hi); a.set_ylim(-2.3, 2.6)
a.set_xlabel("wavelength (nm)"); a.set_ylabel("CD in a 20 µm spot (%)")
a.set_title("(a) 1° twist: CD at the aligned point", loc="left", fontsize=9.5, color=INK)
a.legend(frameon=False, fontsize=7, loc="upper left")
a.text(1512.4, 2.58, f"peak +{peaks['N 8']:.1f} % at 1505.5–1506 nm\nN 6 / 7 / 8: {peaks['N 6']:.2f} / {peaks['N 7']:.2f} / {peaks['N 8']:.2f} %",
       fontsize=7, color=C1, ha="right", va="top")
a.text(1510.3, -2.15, "−1°: opposite sign", fontsize=7, color=C2, ha="center", va="bottom")

# (b) spot size at +1 deg, N 8 (and N 7 for the single point)
for D, col, lw, lab in ((20, C1, 2.3, "D = 20 µm"), (10, C3, 2.0, "D = 10 µm")):
    lam, cd = disc_cd("+1_N8", D); m = (lam >= lo) & (lam <= hi)
    b.plot(lam[m], cd[m], color=col, lw=lw, label=lab)
for tag, ls, lab in (("+1_N8", "-", "single point, N 8"), ("+1_N7", (0, (3, 2)), "single point, N 7")):
    lam, cd = disc_cd(tag, 0); m = (lam >= lo) & (lam <= hi)
    b.plot(lam[m], cd[m], color=INK2, lw=1.0, ls=ls, label=lab)
b.axhline(0, color=INK2, lw=0.7)
b.set_xlim(lo, hi); b.set_ylim(-2.3, 2.6)
b.set_xlabel("wavelength (nm)"); b.set_ylabel("CD at +1° (%)")
b.set_title("(b) The spot average converges, one point does not", loc="left", fontsize=9.5, color=INK)
b.legend(frameon=False, fontsize=7, loc="lower left", ncol=2)
b.text(1512.4, 2.58, "moiré period 35.5 µm", fontsize=7, color=INK2, ha="right", va="top")

fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(f"docs/figs/T19c_twist_cd.{ext}", dpi=220)
print({k: round(float(v), 3) for k, v in peaks.items()})
