"""Proposal figure for A3 (tilt): wedge-gap local average, T18b post-processing of the T18a fmmax tables.
Run from the repo root: python3 docs/figs/make_T18b_wedge_figure.py [runs/<..>_T18b_wedge_average]"""
import json, sys, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
RUN = sys.argv[1] if len(sys.argv) > 1 else "runs/20261122-0608_T18b_wedge_average"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"; C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False})
d = json.load(open(f"{RUN}/wedge_average.json"))
fig, ax = plt.subplots(2, 2, figsize=(9.0, 6.6))

# (a), (b): structure (i), T9b best, TE (TM is the same within 0.5 %); x = gap spread across the aperture, alpha * D
lines = (("T9b|500|TE", C2, "Q 6900 (gap 500 nm)"), ("T9b|380|TE", C1, "Q 630 (gap 380 nm)"))
def curve(res, key):
    r = sorted((x["alpha_urad"] * x["D_um"] * 1e-3, x[key], x[key + "_analytic" if key == "peak" else "fwhm_analytic_nm"]) for x in res["rows"])
    u = {}
    for dg, v, va in r: u.setdefault(round(dg, 6), (v, va))
    dg = np.array(sorted(u)); return dg, np.array([u[k][0] for k in dg]), np.array([u[k][1] for k in dg])
a, b = ax[0, 0], ax[0, 1]
txt = []
for key, col, lab in lines:
    res = d["a"][key]; G0 = res["Gamma0_nm"]
    dg, w, wa = curve(res, "fwhm_nm"); m = dg > 0
    a.plot(dg[m], w[m] / G0, color=col, lw=2.2, label=lab); a.plot(dg[m], wa[m] / G0, color=col, lw=1.1, ls=(0, (4, 2.5)))
    for f in (1.1, 2.0):
        j = np.where(w / G0 >= f)[0]
        if len(j):
            x0 = np.interp(f, w[j[0] - 1:j[0] + 1] / G0, dg[j[0] - 1:j[0] + 1]); a.plot([x0], [f], "o", color=col, ms=6, mec="white", mew=0.9)
            a.text(x0 * 0.92, f * (1.10 if f > 1.5 else 1.04), f"{x0 * 10:.0f} µrad", fontsize=7, color=col, ha="right", va="bottom")
    dg, p, pa = curve(res, "peak"); m = dg > 0
    b.plot(dg[m], p[m], color=col, lw=2.2, label=lab); b.plot(dg[m], pa[m], color=col, lw=1.1, ls=(0, (4, 2.5)))
    th = res["thresholds"]
    s10 = " / ".join(f"{th[D]['10pct_numeric_urad']:.0f}" if th[D]["10pct_numeric_urad"] >= 20 else f"{th[D]['10pct_numeric_urad']:.1f}" for D in ("50", "100", "200"))
    s100 = " / ".join(("—" if th[D]["100pct_numeric_urad"] is None else f"{th[D]['100pct_numeric_urad']:.0f}") for D in ("50", "100", "200"))
    txt.append((col, f"{lab.split(' (')[0]}:  10 %: {s10} µrad;  2×: {s100} µrad"))
for f, lab in ((1.1, "10 % wider"), (2.0, "2× wider")):
    a.axhline(f, color=INK2, lw=0.8, ls=":"); a.text(0.105, f * 1.04, lab, fontsize=7, color=INK2)
a.set_xscale("log"); a.set_yscale("log"); a.set_xlim(0.1, 40); a.set_ylim(0.95, 10)
a.yaxis.set_major_locator(FixedLocator([1, 2, 5, 10])); a.yaxis.set_major_formatter(FixedFormatter(["1", "2", "5", "10"])); a.yaxis.set_minor_locator(NullLocator())
a.xaxis.set_major_locator(FixedLocator([0.1, 0.3, 1, 3, 10, 30])); a.xaxis.set_major_formatter(FixedFormatter(["0.1", "0.3", "1", "3", "10", "30"])); a.xaxis.set_minor_locator(NullLocator())
a.set_xlabel("gap difference across the aperture, α·D (nm)"); a.set_ylabel("passband width / width at α = 0")
a.set_title("(a) Tilt widens the passband", loc="left", fontsize=9.5, color=INK)
a.plot([], [], color=INK2, lw=2.2, label="local average (table)"); a.plot([], [], color=INK2, lw=1.1, ls=(0, (4, 2.5)), label="√(Γ² + W²)")
a.legend(frameon=False, fontsize=7, loc="upper left", bbox_to_anchor=(0.0, 0.93))
a.text(0.02, 0.50, "dots: tilt α for D = 100 µm\n(α scales as 1/D)", transform=a.transAxes, fontsize=7, color=INK2)
b.set_xscale("log"); b.set_xlim(0.1, 40); b.set_ylim(0, 1.05)
b.xaxis.set_major_locator(FixedLocator([0.1, 0.3, 1, 3, 10, 30])); b.xaxis.set_major_formatter(FixedFormatter(["0.1", "0.3", "1", "3", "10", "30"])); b.xaxis.set_minor_locator(NullLocator())
b.set_xlabel("gap difference across the aperture, α·D (nm)"); b.set_ylabel("peak / peak at α = 0")
b.set_title("(b) ...and lowers its peak", loc="left", fontsize=9.5, color=INK)
b.plot([], [], color=INK2, lw=1.1, ls=(0, (4, 2.5)), label="(Γ/W)·atan(W/Γ)"); b.legend(frameon=False, fontsize=7, loc="lower left")
b.text(0.12, 0.30, "α·D = 1 nm is 10 µrad over 100 µm.\nW = (dλ/dg)·α·D: dλ/dg = 0.093 (Q 6900),\n0.146 nm/nm (Q 630)", fontsize=6.6, color=INK2)

# (c) receive pattern at fixed lambda, structure (ii) prelim TM, gap 200, D 100 um
c = ax[1, 0]; cv = d["b"]["curves"]
th = np.array(cv["D100_a0"]["theta_deg"]); P = np.array(cv["D100_a0"]["P"])
c.plot(th, P, color=C3, lw=2.2)
c.set_xlim(-8, 8); c.set_ylim(0, 1); c.set_xlabel("incidence angle θ (deg)"); c.set_ylabel("transmission P at fixed λ")
c.set_title(f"(c) Receive pattern at λ = {d['b']['lam_half_nm']:.1f} nm (curved TM band)", loc="left", fontsize=9.5, color=INK)
c.text(0, 0.10, "symmetric\nin ±θ", ha="center", fontsize=7, color=INK2)
ins = c.inset_axes([0.335, 0.63, 0.33, 0.33])
al = np.array([-50, -20, 0, 20, 50]); ce = np.array([cv[f"D100_a{x}"]["centre_urad"] for x in al])
ins.plot([-60, 60], [-30, 30], color=INK2, lw=1, ls=(0, (4, 2.5))); ins.plot(al, ce, "o", color=C3, ms=5, mec="white", mew=0.8)
ins.set_xlim(-60, 60); ins.set_ylim(-32, 32); ins.tick_params(labelsize=6); ins.set_xlabel("tilt α (µrad)", fontsize=6.5, labelpad=1)
ins.set_ylabel("centre (µrad)", fontsize=6.5, labelpad=1); ins.text(-55, 18, "centre = α/2", fontsize=6.5, color=INK2)
ins.grid(True, color=GRID, lw=0.5)

# (d) dither signal
e = ax[1, 1]
for k, col, lab in (("D100_ad20", C1, "dither ±20 µrad"), ("D100_ad10", C2, "dither ±10 µrad")):
    r = d["c"][k]; t = np.array(r["theta_deg"])
    e.plot(t, np.array(r["S"]) * 1e4, color=col, lw=2.2, label=lab); e.plot(t, np.array(r["S_first_order"]) * 1e4, color=INK, lw=0.8, ls=(0, (3, 2)))
e.plot([], [], color=INK, lw=0.8, ls=(0, (3, 2)), label="−(α_d/2)·dP/dθ"); e.axhline(0, color=INK2, lw=0.8)
r = d["c"]["D100_ad10"]
t_, S_ = np.array(r["theta_deg"]), np.array(r["S"]); k_ = np.where((np.sign(S_[:-1]) != np.sign(S_[1:])) & (t_[:-1] > 1))[0][0]
ring = float(np.interp(0, [S_[k_ + 1], S_[k_]], [t_[k_ + 1], t_[k_]]))
e.text(-7.8, -1.0, f"S is odd in θ: zero at 0,\nslope {r['slope_per_deg'] * 1e5:.1f}×10⁻⁵ per deg\n(dither ±10 µrad).\nSign of S = sign of θ\nfor |θ| < {ring:.1f}° (dark ring)", fontsize=7, color=INK2, ha="left", va="top")
e.set_xlim(-8, 8); e.set_xlabel("incidence angle θ (deg)"); e.set_ylabel("dither signal S (10⁻⁴ of input)")
e.set_title("(d) Dithering the tilt tells +θ from −θ", loc="left", fontsize=9.5, color=INK)
e.legend(frameon=False, fontsize=7, loc="upper right")
for x_ in ax.flat: x_.grid(True, color=GRID, lw=0.6); x_.set_axisbelow(True)
fig.text(0.01, -0.035, "Local-average model (PI): P(λ, θ; α) = ⟨T(λ, θ − α/2; g₀ + αx)⟩ over x in ±D/2. T from fmmax 80/96 tables (T18a; gap g₀ ± 25–30 nm in 5 nm steps, "
         "θ 0.5–8°, azimuth 0; cubic splines in sin²θ between table angles).\n(a, b): T9b best structure, TE (TM within 0.5 %), Lorentzian of the resonance pole at normal incidence (0.5° record); the Fano "
         "background is not included. (c, d): prelim square bilayer, gap 200 nm, TM, D = 100 µm\n(D = 50 and 200 µm give the same within 0.5 %). In this model the "
         "centre shift α/2 holds exactly by symmetry; a full-wave solve of a tilted slab was not done.", fontsize=6.4, color=INK2)
plt.tight_layout()
for ext in ("png", "pdf"): plt.savefig(f"docs/figs/T18b_tilt_wedge.{ext}", dpi=200, bbox_inches="tight")
print("saved docs/figs/T18b_tilt_wedge.png")
