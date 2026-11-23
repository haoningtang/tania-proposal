"""T19c supplement: is the rcwa4d local map (and CD at AA) just the LPA field band-limited to the kept moire harmonics?

The rcwa4d-mf field below the twisted bilayer contains only the moire harmonics m = (m1, m2) of the kept orders (|m| <= N).
The LPA field E_LPA(r) = J(delta(r)) e_in (T19b n 48 Jones map, bilinear in delta) has sharp features where the local line
sweeps through lambda. Here E_LPA is Fourier-filtered on the moire cell to exactly the same harmonic set, and the local
power |E_x|^2 + |E_y|^2 (normal-incidence approximation, used for both maps here) and CD = T_sp - T_sm are compared:
  rcwa4d vs LPA (unfiltered), rcwa4d vs LPA (filtered), and CD at AA (r = 0) for all three.
If filtered LPA ~ rcwa4d, the beyond-LPA (gradient) part is only the difference rcwa4d - filtered LPA.
Usage: python twist_local_filtered.py RUN_T19a RUN_T19b   (writes analysis_T19c_filtered.json)"""
import glob, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from twist_local import load_amps, moire_basis, lpa_interp, local_shift

RA, RB = sys.argv[1], sys.argv[2]
NG = 96
L = np.load(os.path.join(RB, "n48", "lpa_jones.npz")); Jl = np.conj(L["J"]); nL = int(L["n"])
EIN = dict(x=np.array([1, 0]), y=np.array([0, 1]), sp=np.array([1, 1j]) / np.sqrt(2), sm=np.array([1, -1j]) / np.sqrt(2))
out = {}
for f in sorted(glob.glob(os.path.join(RA, "amps", "tw*_N*.npz"))):
    tag = os.path.basename(f)[2:-4]; d = load_amps(f); tw = float(d["twist"])
    m, i1, i2 = moire_basis(d); lam = d["lam"]; o = np.argsort(lam)
    s = np.arange(NG) / NG; S1, S2 = np.meshgrid(s, s, indexing="ij")
    ph = np.exp(-2j * np.pi * (m[:, 0, None, None] * S1 + m[:, 1, None, None] * S2))      # [nm, NG, NG]
    res = dict(rms_T_unf=[], rms_T_filt=[], rms_CD_unf=[], rms_CD_filt=[], CD_AA_rcwa=[], CD_AA_filt=[], CD_AA_unf=[],
               Tx_AA_rcwa=[], Tx_AA_filt=[], rms_CD_rcwa=[])
    for li in o:
        kx, ky = d["kx"][li], d["ky"][li]
        b = np.array([[kx[i1], ky[i1]], [kx[i2], ky[i2]]]) * 2 * np.pi / lam[li]
        Lm = 2 * np.pi * np.linalg.inv(b).T
        r = S1[..., None] * Lm[0] + S2[..., None] * Lm[1]
        J = lpa_interp(Jl[:, :, li], nL, local_shift(r, tw))                                  # [NG, NG, 2, 2]
        Tm = {}
        for inp, e in EIN.items():
            E_u = J @ e                                                                          # [NG, NG, 2]
            c = np.einsum("jab,abk->jk", np.conj(ph), E_u) / NG ** 2                            # coefficients on kept m
            E_f = np.einsum("jab,jk->abk", ph, c)
            E_r = {"x": d["tx"][li][:, :2], "y": d["ty"][li][:, :2]}
            E_r["sp"] = (E_r["x"] + 1j * E_r["y"]) / np.sqrt(2); E_r["sm"] = (E_r["x"] - 1j * E_r["y"]) / np.sqrt(2)
            E_rc = np.einsum("jab,jk->abk", ph, E_r[inp])
            Tm[inp] = [np.sum(np.abs(E) ** 2, -1) for E in (E_rc, E_f, E_u)]
        rc, fi, un = (Tm["x"][k] for k in range(3))
        res["rms_T_unf"].append(float(np.sqrt(np.mean((rc - un) ** 2)))); res["rms_T_filt"].append(float(np.sqrt(np.mean((rc - fi) ** 2))))
        cd = [Tm["sp"][k] - Tm["sm"][k] for k in range(3)]
        res["rms_CD_rcwa"].append(float(np.sqrt(np.mean(cd[0] ** 2))))
        res["rms_CD_unf"].append(float(np.sqrt(np.mean((cd[0] - cd[2]) ** 2)))); res["rms_CD_filt"].append(float(np.sqrt(np.mean((cd[0] - cd[1]) ** 2))))
        res["CD_AA_rcwa"].append(float(cd[0][0, 0])); res["CD_AA_filt"].append(float(cd[1][0, 0])); res["CD_AA_unf"].append(float(cd[2][0, 0]))
        res["Tx_AA_rcwa"].append(float(rc[0, 0])); res["Tx_AA_filt"].append(float(fi[0, 0]))
    res["lam_nm"] = lam[o].tolist(); res["twist"] = tw; res["N"] = int(d["N"])
    res["summary"] = {k: float(np.sqrt(np.mean(np.square(res[k])))) for k in ("rms_T_unf", "rms_T_filt", "rms_CD_rcwa", "rms_CD_unf", "rms_CD_filt")}
    res["summary"].update(max_abs_CD_AA_rcwa=float(np.max(np.abs(res["CD_AA_rcwa"]))), max_abs_CD_AA_filt=float(np.max(np.abs(res["CD_AA_filt"]))),
                          max_abs_CD_AA_rcwa_minus_filt=float(np.max(np.abs(np.subtract(res["CD_AA_rcwa"], res["CD_AA_filt"])))),
                          max_abs_TxAA_rcwa_minus_filt=float(np.max(np.abs(np.subtract(res["Tx_AA_rcwa"], res["Tx_AA_filt"])))))
    out[tag] = res
    print(tag, {k: round(v, 4) for k, v in res["summary"].items()}, flush=True)
json.dump(out, open(os.path.join(RA, "analysis_T19c_filtered.json"), "w"))
