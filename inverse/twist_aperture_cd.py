"""T19c (4): CD averaged over a disc of diameter D centred at AA (r = 0, the twist axis).
E_sigma(r) = sum_m c_m exp(i q_m . r), q_m = 2 pi (kx, ky)/lam; disc average of |E|^2 is
sum_{m,m'} c_m c_m'^* A(|q_m - q_m'| R), A(x) = 2 J1(x)/x. Normal-incidence power |E_x|^2 + |E_y|^2 (same as CD_AA).
sigma+- = (x +- i y)/sqrt(2). Usage: python twist_aperture_cd.py RUN_T19a -> RUN/analysis_T19c_aperture.json"""
import glob, json, os, sys
import numpy as np
from scipy.special import j1
R = sys.argv[1]; out = {}
for f in sorted(glob.glob(os.path.join(R, "amps", "tw*_N*.npz"))):
    d = np.load(f); tag = os.path.basename(f)[2:-4]; tw = float(d["twist"])
    if tw < 0: continue
    lam = d["lam"]; o = np.argsort(lam); lam = lam[o]; cell = float(d["a_nm"]) / np.deg2rad(abs(tw)) / 1e3   # moire period, um
    res = dict(twist=tw, N=int(d["N"]), cell_um=cell, lam=lam.tolist())
    for D in (0, 10, 20, 50):
        if D >= cell: continue
        cd = []
        for li in o:
            q = np.stack([d["kx"][li], d["ky"][li]], -1) * 2 * np.pi / d["lam"][li]
            dq = np.linalg.norm(q[:, None] - q[None], axis=-1) * D * 1e3 / 2
            A = np.where(dq > 1e-12, 2 * j1(dq) / np.where(dq > 1e-12, dq, 1), 1.0)
            T = []
            for s in (1, -1):
                c = (d["tx"][li][:, :2] + s * 1j * d["ty"][li][:, :2]) / np.sqrt(2)          # [m, 2]
                T.append(np.real(np.einsum("mk,nk,mn->", c, np.conj(c), A)))
            cd.append(T[0] - T[1])
        cd = np.array(cd); main = (lam >= 1500) & (lam <= 1512.5)
        res[f"D{D}"] = dict(CD=cd.tolist(), max_main=float(np.abs(cd[main]).max()), max_full=float(np.abs(cd).max()),
                            lam_max_full=float(lam[np.argmax(np.abs(cd))]))
        print(f"{tag:8s} cell {cell:6.1f} um  D {D:2d} um: max|CD| main {res[f'D{D}']['max_main']:.4f}  full {res[f'D{D}']['max_full']:.4f} @ {res[f'D{D}']['lam_max_full']:.0f}")
    out[tag] = res
json.dump(out, open(os.path.join(R, "analysis_T19c_aperture.json"), "w"))
