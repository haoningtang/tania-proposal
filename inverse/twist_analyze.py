"""T15 analysis of twist.py spectra (rcwa4d-mf, square prelim bilayer, normal incidence).
Per spectrum (1480-1580 nm): mean T_x; band-mean CD = <T+ - T->; CD extremum and its lambda; rms distance to the stacking
average (stack_avg.json); C4 check max|T_x - T_y|; energy max|R+T-1|; AAA poles of T_x and the tracked line = largest-weight
pole in 1495-1525 nm (the aligned line is at 1506.6 nm with fmmax 80/96), with CD interpolated at its wavelength.
Parity from +-theta pairs; odd fit CD(theta) = c1 theta + c3 theta^3; even fit lam(theta) = l0 + l2 theta^2 (theta in deg);
Jacobian of (lam, Q, CD_at_lam, CD_band) w.r.t. (gap, twist) at theta = 1 deg by central differences.
Usage: python twist_analyze.py RUN_DIR"""
import glob, json, os, sys
import numpy as np
from scipy.interpolate import AAA
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

D = sys.argv[1]
SA = json.load(open(os.path.join(D, "stack_avg.json")))
lam_sa = np.array(SA["lam_nm"]); T_sa = np.array(SA["avg"]["Tx"])


def poles_w(l, t, lo, hi):
    A = AAA(1 / l, t, rtol=1e-8, max_terms=20)
    out = []
    for z, rz in zip(A.poles(), A.residues()):
        if z.real <= 0 or z.imag == 0: continue
        l0 = 1 / z.real; Q = z.real / (2 * abs(z.imag)); w = abs(rz) / abs(z.imag)
        if lo < l0 < hi and 20 < Q < 1e6 and w > 0.03: out.append((float(l0), float(Q), float(w)))
    return sorted(set(out))


def load(f):
    z = dict(np.load(f)); tag = os.path.basename(f)
    if "N" not in z:   # explore/dense_N{N}_th{th}_g{g}.npz
        p = tag[6:-4].split("_"); z["N"] = int(p[0][1:]); z["theta"] = float(p[1][2:]); z["gap"] = float(p[2][1:])
    return {k: (np.asarray(v).item() if np.ndim(v) == 0 else v) for k, v in z.items()}


def observe(z):
    l = z["lam"]; cd = z["Tp"] - z["Tm"]; cd0 = z["T0p"] - z["T0m"]
    P = poles_w(l, z["Tx"], l[0], l[-1])
    near = [p for p in P if 1495 < p[0] < 1525]
    tr = max(near, key=lambda p: p[2]) if near else (np.nan, np.nan, np.nan)
    i = np.argmax(np.abs(cd)); Ti = np.interp(lam_sa, l, z["Tx"])
    dl = np.gradient(l); ext = 1 - z["Tx"]
    lc = float(np.sum(l * ext * dl) / np.sum(ext * dl)); sw = float(np.sqrt(np.sum((l - lc) ** 2 * ext * dl) / np.sum(ext * dl)))
    return dict(lam_c=lc, width=sw, ext_int=float(np.sum(ext * dl)),N=int(z["N"]), theta=float(z["theta"]), gap=float(z["gap"]), T_mean=float(np.sum(z["Tx"] * dl) / np.sum(dl)),
                CD_band=float(np.sum(cd * dl) / np.sum(dl)), CD_ext=float(cd[i]), lam_CD_ext=float(l[i]),
                CD0_ext=float(cd0[np.argmax(np.abs(cd0))]), rms_vs_stack_avg=float(np.sqrt(np.mean((Ti - T_sa) ** 2))),
                c4_err=float(np.abs(z["Tx"] - z["Ty"]).max()), energy_err=float(z["err"].max()),
                lam=tr[0], Q=tr[1], w=tr[2], CD_at_lam=float(np.interp(tr[0], l, cd)) if np.isfinite(tr[0]) else np.nan,
                poles=P)


specs = {}
for f in sorted(glob.glob(os.path.join(D, "spectra/spec_*.npz"))) + sorted(glob.glob(os.path.join(D, "explore/dense_*.npz"))):
    z = load(f); key = (z["N"], round(z["theta"], 4), z["gap"])
    if key not in specs: specs[key] = z
obs = {k: observe(z) for k, z in specs.items()}
res = dict(note=__doc__, spectra=[dict(o, poles=[list(p) for p in o["poles"]]) for o in obs.values()])

# parity at N = 5, gap 200
N0, G0 = 5, 200.0
par = []
for (N, th, g), z in specs.items():
    if N == N0 and g == G0 and th > 0 and (N, -th, g) in specs:
        m = specs[(N, -th, g)]; cdp, cdm = z["Tp"] - z["Tm"], m["Tp"] - m["Tm"]
        par.append(dict(theta=th, max_Tx_diff=float(np.abs(z["Tx"] - m["Tx"]).max()), max_CD_sum=float(np.abs(cdp + cdm).max()),
                        max_CD=float(np.abs(cdp).max()), lam_diff=obs[(N, th, g)]["lam"] - obs[(N, -th, g)]["lam"],
                        Q_diff=obs[(N, th, g)]["Q"] - obs[(N, -th, g)]["Q"]))
res["parity_N5"] = sorted(par, key=lambda p: p["theta"])

# fits on theta > 0 (N = 5, gap 200), small angles <= 1 deg
pos = sorted([o for o in obs.values() if o["N"] == N0 and o["gap"] == G0 and o["theta"] > 0 and o["theta"] in (0.1, 0.25, 0.5, 1.0, 2.0, 4.0)],
             key=lambda o: o["theta"])
th = np.array([o["theta"] for o in pos])
fits = {}
for key in ("CD_band", "CD_ext", "CD_at_lam"):
    y = np.array([o[key] for o in pos]); s = th <= 1.0
    c = np.linalg.lstsq(np.c_[th[s], th[s] ** 3], y[s], rcond=None)[0]
    fits[key] = dict(c1_per_deg=float(c[0]), c3_per_deg3=float(c[1]), slope_0p1=float(y[0] / th[0]) if th[0] == 0.1 else None)
for key in ("lam", "Q", "T_mean", "lam_c", "width"):
    y = np.array([o[key] for o in pos]); s = (th <= 1.0) & np.isfinite(y)
    c = np.linalg.lstsq(np.c_[np.ones(s.sum()), th[s] ** 2], y[s], rcond=None)[0]
    fits[key] = dict(limit_theta0=float(c[0]), c2_per_deg2=float(c[1]), second_derivative_per_deg2=float(2 * c[1]))
res["fits_N5_theta_le_1"] = fits

# Jacobian at theta 1, N 5: gap (+-5 nm) and twist (+-0.1 deg)
J = None
need = [(5, 1.0, 195.0), (5, 1.0, 205.0), (5, 0.9, 200.0), (5, 1.1, 200.0), (5, 1.0, 200.0)]
if all(k in obs for k in need):
    O = ["lam_c", "width", "CD_band", "ext_int"]
    b = obs[(5, 1.0, 200.0)]
    J = np.array([[(obs[(5, 1.0, 205.0)][o] - obs[(5, 1.0, 195.0)][o]) / 10.0, (obs[(5, 1.1, 200.0)][o] - obs[(5, 0.9, 200.0)][o]) / 0.2] for o in O])
    sc = np.array([b["lam_c"], b["width"], 1.0, b["ext_int"]])
    Jn = J / sc[:, None]; sv = np.linalg.svd(Jn, compute_uv=False)
    res["jacobian_theta1_N5"] = dict(observables=O, controls=["gap (per nm)", "twist (per deg)"], J_raw=J.tolist(), J_norm=Jn.tolist(),
                                     sv=sv.tolist(), cond=float(sv[0] / sv[1]), base={o: b[o] for o in O},
                                     note="observables: extinction centroid lam_c and rms width of (1 - T_x) over 1480-1580 nm, band-mean CD, integrated extinction; normalized rows: dlam_c/lam_c, dwidth/width, dCD_band, dext/ext; columns per nm (gap) and per deg (twist); unit choice sets cond. Pole-tracked lam, Q are not used: the tracked pole switches lines between neighbouring states")
json.dump(res, open(os.path.join(D, "analysis.json"), "w"), indent=1, default=float)

keys = ["N", "theta", "gap", "lam_c", "width", "ext_int", "lam", "Q", "CD_at_lam", "CD_band", "CD_ext", "lam_CD_ext", "CD0_ext", "T_mean", "rms_vs_stack_avg", "c4_err", "energy_err"]
with open(os.path.join(D, "table.csv"), "w") as f:
    f.write(",".join(keys) + "\n")
    for k in sorted(obs):
        f.write(",".join(f"{obs[k][c]:.6g}" for c in keys) + "\n")
for k in sorted(obs): print(" ".join(f"{c} {obs[k][c]:.4g}" for c in keys))
print(json.dumps({k: res[k] for k in res if k not in ("note", "spectra")}, indent=1, default=float))

# figure
fig, ax = plt.subplots(2, 2, figsize=(13, 9))
cols = plt.cm.viridis(np.linspace(0, 0.9, 6))
for c, t in zip(cols, [0.1, 0.25, 0.5, 1.0, 2.0, 4.0]):
    if (5, t, 200.0) in specs:
        z = specs[(5, t, 200.0)]; ax[0, 0].plot(z["lam"], z["Tx"], color=c, label=f"θ = {t:g}°")
        ax[0, 1].plot(z["lam"], z["Tp"] - z["Tm"], color=c, label=f"+{t:g}°")
        if (5, -t, 200.0) in specs:
            m = specs[(5, -t, 200.0)]; ax[0, 1].plot(m["lam"], m["Tp"] - m["Tm"], color=c, ls=":", lw=2)
ax[0, 0].plot(lam_sa, T_sa, "k-", lw=2.5, alpha=0.6, label="aligned, stacking average")
ax[0, 0].set_ylabel("T_x"); ax[0, 0].set_title("rcwa4d-mf N = 5, gap 200 nm, normal incidence"); ax[0, 0].legend(fontsize=7)
ax[0, 1].set_ylabel("CD = T+ − T−"); ax[0, 1].set_title("CD spectra (solid +θ, dotted −θ)"); ax[0, 1].legend(fontsize=7)
for o in ("CD_band", "CD_ext"):
    pts = sorted([(v["theta"], v[o]) for v in obs.values() if v["N"] == 5 and v["gap"] == 200.0 and abs(v["theta"]) in (0.1, 0.25, 0.5, 1, 2, 4)])
    ax[1, 0].plot(*zip(*pts), "o-", label=o)
ax[1, 0].axhline(0, color="k", lw=0.5); ax[1, 0].axvline(0, color="k", lw=0.5)
ax[1, 0].set_xlabel("twist θ (deg)"); ax[1, 0].set_ylabel("CD"); ax[1, 0].legend(); ax[1, 0].set_title("CD vs twist (N = 5)")
for c, N in zip(["C0", "C1", "C2", "C3"], [3, 4, 5, 6]):
    if (N, 1.0, 200.0) in specs:
        z = specs[(N, 1.0, 200.0)]; ax[1, 1].plot(z["lam"], z["Tx"], color=c, label=f"T_x N={N}")
        ax[1, 1].plot(z["lam"], 5 * (z["Tp"] - z["Tm"]) + 0.2, color=c, ls="--", lw=0.8)
ax[1, 1].plot(lam_sa, T_sa, "k-", lw=2.5, alpha=0.6, label="stacking average")
ax[1, 1].set_title("θ = 1°: convergence in N (dashed: 0.2 + 5·CD)"); ax[1, 1].legend(fontsize=7)
for a_ in ax.flat[[0, 1, 3]]: a_.set_xlabel("λ (nm)")
fig.tight_layout(); fig.savefig(os.path.join(D, "analysis.png"), dpi=110)
