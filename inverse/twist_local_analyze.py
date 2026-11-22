"""T19c: analysis of T19a (rcwa4d-mf moire-order amplitudes) against T19b (LPA Jones map). See twist_local.py.
Usage: python twist_local_analyze.py RUN_T19a RUN_T19b"""
import glob, json, os, sys
import numpy as np
from scipy.interpolate import AAA
from scipy.special import j1
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from twist_local import load_amps, local_maps, lpa_interp, lpa_T, local_shift, moire_basis

RA, RB = sys.argv[1], sys.argv[2]
amps = {}
for f in sorted(glob.glob(os.path.join(RA, "amps", "tw*_N*.npz"))):
    b = os.path.basename(f)[2:-4]; tw, N = b.split("_N"); amps[(float(tw), int(N))] = load_amps(f)
lp = os.path.join(RB, "n48", "lpa_jones.npz")
lp = lp if os.path.exists(lp) else os.path.join(RB, "lpa_jones.npz")
L = np.load(lp); Jl = np.conj(L["J"]); nL = int(L["n"])      # conj: fmmax exp(-iwt) -> rcwa4d exp(+iwt)
lam = next(iter(amps.values()))["lam"]; o = np.argsort(lam); lam_s = lam[o]
assert np.allclose(L["lam"], lam)
out = dict(lpa_grid=nL, lpa_file=os.path.relpath(lp, RA), twists={})


def pole(l, T, lo=1495, hi=1525):
    A_ = AAA(1 / l, T, rtol=1e-6, max_terms=20); best = None
    for p, rz in zip(A_.poles(), A_.residues()):
        if p.real <= 0 or p.imag == 0: continue
        l0 = 1 / p.real; Q = p.real / (2 * abs(p.imag))
        if lo < l0 < hi and 20 < Q < 1e6 and abs(rz) / abs(p.imag) > 0.05:
            if best is None or abs(rz) / abs(p.imag) > best[2]: best = (float(l0), float(Q), float(abs(rz) / abs(p.imag)))
    return best


def aa_spectrum(d):
    T = {k: np.zeros(len(lam)) for k in ("x", "y", "sp", "sm")}
    for li in range(len(lam)):
        M = local_maps(d, li, ngrid=1, s_range=0.0)
        for k in T: T[k][li] = M["T_" + k][0, 0]
    return T


def disc_avg(d, li, D_nm):
    """power-weighted disc average (diameter D, centred at AA) of T for sp, sm: sum_ij w_ij P_ij, w = 2 J1(qR)/(qR)."""
    lamv = d["lam"][li]; k0 = 2 * np.pi / lamv
    kx, ky, kz = d["kx"][li], d["ky"][li], d["kzt"][li]
    kv = np.stack([kx, ky, -kz], -1)
    dq = np.hypot(kx[:, None] - kx[None], ky[:, None] - ky[None]) * k0 * D_nm / 2
    w = np.where(dq > 1e-12, 2 * j1(np.maximum(dq, 1e-12)) / np.maximum(dq, 1e-12), 1.0)
    res = {}
    for inp, E in (("sp", (d["tx"][li] + 1j * d["ty"][li]) / np.sqrt(2)), ("sm", (d["tx"][li] - 1j * d["ty"][li]) / np.sqrt(2))):
        H = np.cross(kv, E)
        P = E[:, None, 0] * np.conj(H[None, :, 1]) - E[:, None, 1] * np.conj(H[None, :, 0])
        res[inp] = float(-np.real(np.sum(w * P)))
    return res


AA = {}
for (tw, N), d in sorted(amps.items()):
    T = aa_spectrum(d); AA[(tw, N)] = T
    rec = dict(N=N, mean_Tx_min=float(d["Tx"].min()), energy_err=float(np.max(np.abs(d["Tx"] + d["Rx"] - 1))),
               moire_period_um=float(620 / (2 * np.sin(np.radians(abs(tw)) / 2)) / 1e3), n_orders=int(len(d["index"])))
    rec["AA_pole"] = pole(lam_s, T["x"][o]); rec["CD_AA"] = (T["sp"] - T["sm"])[o].tolist()
    rec["AA_Tx"] = T["x"][o].tolist(); rec["AA_Tsp"] = T["sp"][o].tolist(); rec["AA_Tsm"] = T["sm"][o].tolist()
    # aperture CD
    rec["aperture"] = {}
    for D in (10e3, 20e3, 50e3):
        if D >= rec["moire_period_um"] * 1e3: continue
        cd = []
        for li in o:
            r = disc_avg(d, li, D); cd.append(r["sp"] - r["sm"])
        rec["aperture"][f"{D/1e3:g}"] = cd
    out["twists"][f"{tw:+g}_N{N}"] = rec
aligned = lpa_T(Jl[0, 0])
out["aligned_pole"] = pole(lam_s, aligned["T_x"][o])
out["lam_nm"] = lam_s.tolist()

# parity and kappa fit (N 6 only)
tws = sorted(t for (t, N) in amps if N == 6)
pos = [t for t in tws if t > 0 and -t in tws]
out["parity_max_abs_CD_sum"] = {f"{t:g}": float(np.max(np.abs(np.array(out["twists"][f"{t:+g}_N6"]["CD_AA"]) + np.array(out["twists"][f"{-t:+g}_N6"]["CD_AA"])))) for t in pos}
out["parity_max_abs_Tx_diff"] = {f"{t:g}": float(np.max(np.abs(np.array(out["twists"][f"{t:+g}_N6"]["AA_Tx"]) - np.array(out["twists"][f"{-t:+g}_N6"]["AA_Tx"])))) for t in pos}
th = np.array(tws); CD = np.array([out["twists"][f"{t:+g}_N6"]["CD_AA"] for t in tws])       # [ntw, nlam]
small = np.abs(th) <= 1.0
k1 = np.linalg.lstsq(th[small, None], CD[small], rcond=None)[0][0]                            # linear, |theta| <= 1
X = np.c_[th, th ** 3]; k13 = np.linalg.lstsq(X, CD, rcond=None)[0]                            # linear + cubic, all
ib = int(np.argmax(np.abs(k1)))
out["kappa"] = dict(fit_linear_abs_theta_le_1=dict(kappa_per_deg=k1.tolist()), fit_lin_cubic_all=dict(kappa=k13[0].tolist(), kappa3=k13[1].tolist()),
                    best_lam_nm=float(lam_s[ib]), kappa_best_per_deg=float(k1[ib]), kappa_best_lincubic=float(k13[0][ib]),
                    kappa_at_AA_line=None)
if out["aligned_pole"]:
    il = int(np.argmin(np.abs(lam_s - out["aligned_pole"][0])))
    out["kappa"]["kappa_at_AA_line"] = dict(lam_nm=float(lam_s[il]), kappa_per_deg=float(k1[il]))
# residual of the linear fit: how odd/linear
pred = th[:, None] * k1[None]
out["kappa"]["rms_resid_linear_le1"] = float(np.sqrt(np.mean((CD[small] - pred[small]) ** 2)))
out["AA_line_vs_twist"] = {f"{t:+g}": out["twists"][f"{t:+g}_N6"]["AA_pole"] for t in tws}

# maps at 1 deg (and others) vs LPA; AA location check; rms
maps = {}
for (tw, N), d in sorted(amps.items()):
    if N != 6: continue
    rms_x, cd_rms, cdl_rms, cdg_rms, li_list = [], [], [], [], []
    for li in o:
        M = local_maps(d, li, ngrid=61)
        dl = local_shift(M["r"], tw)
        Jr = lpa_interp(Jl[:, :, li], nL, dl); TL = lpa_T(Jr)
        rms_x.append(float(np.sqrt(np.mean((M["T_x"] - TL["T_x"]) ** 2))))
        cdr = M["T_sp"] - M["T_sm"]; cdl = TL["T_sp"] - TL["T_sm"]
        cd_rms.append(float(np.sqrt(np.mean(cdr ** 2)))); cdl_rms.append(float(np.sqrt(np.mean(cdl ** 2))))
        cdg_rms.append(float(np.sqrt(np.mean((cdr - cdl) ** 2))))
    maps[tw] = dict(rms_Tx_vs_LPA=rms_x, rms_CD=cd_rms, rms_CD_LPA=cdl_rms, rms_CD_minus_LPA=cdg_rms)
    out["twists"][f"{tw:+g}_N6"]["map_vs_LPA"] = dict(rms_Tx_band=float(np.sqrt(np.mean(np.square(rms_x)))),
                                                      rms_Tx_max=float(np.max(rms_x)), rms_CD_band=float(np.sqrt(np.mean(np.square(cd_rms)))),
                                                      rms_CD_LPA_band=float(np.sqrt(np.mean(np.square(cdl_rms)))),
                                                      rms_CD_minus_LPA_band=float(np.sqrt(np.mean(np.square(cdg_rms)))), per_lam=maps[tw])

# AA location: spectral distance of every local spectrum (1 deg) to the aligned spectrum
d1 = amps.get((1.0, 6))
if d1 is not None:
    ng = 41; S = np.zeros((ng, ng)); Tall = []
    for li in o:
        Tall.append(local_maps(d1, li, ngrid=ng, inputs=("x",))["T_x"])
    Tall = np.array(Tall)                                    # [lam, ng, ng]
    dist = np.sqrt(np.mean((Tall - aligned["T_x"][o][:, None, None]) ** 2, 0))
    ij = np.unravel_index(np.argmin(dist), dist.shape); sgrid = np.arange(ng) / ng - 0.5
    out["AA_location_1deg"] = dict(grid=ng, argmin_s=[float(sgrid[ij[0]]), float(sgrid[ij[1]])], dist_min=float(dist.min()),
                                   dist_at_0=float(dist[ng // 2, ng // 2]), dist_at_corner=float(dist[0, 0]), dist_median=float(np.median(dist)))
json.dump(out, open(os.path.join(RA, "analysis_T19c.json"), "w"), indent=1)

# ---- figure
fig, ax = plt.subplots(2, 3, figsize=(15, 9))
if d1 is not None:
    lsel = out["aligned_pole"][0] if out["aligned_pole"] else 1508.0
    li = int(np.argmin(np.abs(lam - lsel)))
    M = local_maps(d1, li, ngrid=101); dl = local_shift(M["r"], 1.0); TL = lpa_T(lpa_interp(Jl[:, :, li], nL, dl))
    ext = [-0.5, 0.5, -0.5, 0.5]
    im = ax[0, 0].imshow(M["T_x"].T, origin="lower", extent=ext, vmin=0, vmax=1); plt.colorbar(im, ax=ax[0, 0])
    ax[0, 0].set_title(f"rcwa4d N6, 1°: local T_x at {lam[li]:.1f} nm"); ax[0, 0].set_xlabel("s1"); ax[0, 0].set_ylabel("s2")
    im = ax[0, 1].imshow(TL["T_x"].T, origin="lower", extent=ext, vmin=0, vmax=1); plt.colorbar(im, ax=ax[0, 1]); ax[0, 1].set_title("LPA (fmmax) T_x at δ(r)")
    cd = M["T_sp"] - M["T_sm"]; m = np.abs(cd).max()
    im = ax[0, 2].imshow(cd.T, origin="lower", extent=ext, cmap="RdBu_r", vmin=-m, vmax=m); plt.colorbar(im, ax=ax[0, 2])
    cdl = TL["T_sp"] - TL["T_sm"]; ax[0, 2].set_title(f"rcwa4d CD(r) (max {m:.2g}); LPA max {np.abs(cdl).max():.2g}")
for t in tws:
    ax[1, 0].plot(lam_s, out["twists"][f"{t:+g}_N6"]["CD_AA"], label=f"{t:+g}°")
ax[1, 0].set_xlabel("λ (nm)"); ax[1, 0].set_ylabel("CD at AA"); ax[1, 0].legend(fontsize=7); ax[1, 0].set_title("CD_AA(λ), N 6")
ax2 = ax[1, 1]; ax2.plot(lam_s, k1, label="κ (lin fit |θ|≤1°) per deg"); ax2.plot(lam_s, k13[0], "--", label="κ (lin+cubic)")
ax2.set_xlabel("λ (nm)"); ax2.legend(fontsize=7); ax2.set_title("κ(λ) = dCD_AA/dθ")
for t in tws:
    for Ds, cd in out["twists"][f"{t:+g}_N6"]["aperture"].items():
        if t > 0: ax[1, 2].plot(lam_s, cd, label=f"{t:g}°, D {Ds} µm")
ax[1, 2].set_xlabel("λ (nm)"); ax[1, 2].set_ylabel("aperture CD"); ax[1, 2].legend(fontsize=6); ax[1, 2].set_title("disc-averaged CD centred at AA")
fig.tight_layout(); fig.savefig(os.path.join(RA, "analysis.png"), dpi=100)
print(json.dumps({k: v for k, v in out.items() if k not in ("twists", "lam_nm", "kappa")}, indent=1))
print("kappa best", out["kappa"]["best_lam_nm"], out["kappa"]["kappa_best_per_deg"], out["kappa"]["kappa_at_AA_line"])
for k, v in out["twists"].items():
    print(k, "AA pole", v["AA_pole"], "maxCD_AA", max(np.abs(v["CD_AA"])), "map", {a: round(b, 4) for a, b in v.get("map_vs_LPA", {}).items() if a != "per_lam"},
          "aperture max", {a: round(float(np.max(np.abs(b))), 5) for a, b in v["aperture"].items()})
