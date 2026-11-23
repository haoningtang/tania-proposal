"""T19d: does the disc CD at AA scale like theta at a fixed fraction of the moire cell?
Same definition as twist_aperture_cd.py (T19c): E_sigma(r) = sum_m c_m exp(i q_m . r), disc of diameter D centred at AA (r = 0),
<|E|^2> = sum_{m,m'} c_m c_m'^* 2 J1(|dq| R)/(|dq| R), normal-incidence power |E_x|^2 + |E_y|^2, sigma+- = (x +- i y)/sqrt(2),
CD = T_sigma+ - T_sigma-. Positive twists only (CD(-theta) = -CD(theta) exactly, T19a).
Apertures: fixed D = 10, 20, 50 um (only if D < cell) and fixed D/cell = 0.25, 0.4, 0.56.
Main line 1500-1512.5 nm, full band 1480-1580 nm. Per (theta, N, aperture): max |CD| and the signed value at the peak.
Last-two-N difference: max over the main line (or band) of |CD_N - CD_(N-1)| on the common lambda grid.
Wavelengths with |R+T-1| > 1e-3 are dropped (listed in per_run[..].dropped_lam).
Usage: python twist_scaling.py OUT AMPS_DIR [AMPS_DIR ...]  -> OUT/analysis.json, OUT/table.csv"""
import glob, json, os, sys
import numpy as np
from scipy.special import j1

OUT = sys.argv[1]; DIRS = sys.argv[2:]
D_FIX = (10, 20, 50); FRAC = (0.25, 0.4, 0.56)
MAIN = (1500.0, 1512.5)


EMAX = 1e-3   # drop wavelengths with max(|Rx+Tx-1|, |Ry+Ty-1|) > EMAX (0.5 deg N 8: 10 lambda in 1511.5-1528 nm up to 5e-2)


def good(d):
    return np.maximum(np.abs(d["Tx"] + d["Rx"] - 1), np.abs(d["Ty"] + d["Ry"] - 1)) <= EMAX


def disc_cd(d, D_um):
    lam = d["lam"]; g = good(d); o = [i for i in np.argsort(lam) if g[i]]; cd = []
    for li in o:
        q = np.stack([d["kx"][li], d["ky"][li]], -1) * 2 * np.pi / d["lam"][li]
        x = np.linalg.norm(q[:, None] - q[None], axis=-1) * D_um * 1e3 / 2
        A = np.where(x > 1e-12, 2 * j1(x) / np.where(x > 1e-12, x, 1), 1.0)
        T = []
        for s in (1, -1):
            c = (d["tx"][li][:, :2] + s * 1j * d["ty"][li][:, :2]) / np.sqrt(2)
            T.append(np.real(np.einsum("mk,nk,mn->", c, np.conj(c), A)))
        cd.append(T[0] - T[1])
    return lam[o], np.array(cd)


files = {}
for D in DIRS:
    for f in sorted(glob.glob(os.path.join(D, "tw*_N*.npz"))):
        tag = os.path.basename(f)[2:-4]
        if tag.startswith("-"):
            continue
        files[tag] = f            # later dirs win (none overlap)

res = {}
for tag, f in sorted(files.items(), key=lambda kv: (float(kv[0].split("_")[0]), int(kv[0].split("N")[1]))):
    d = np.load(f); tw = float(d["twist"]); N = int(d["N"])
    cell = float(d["a_nm"]) / np.deg2rad(abs(tw)) / 1e3
    g = good(d); r = dict(twist=tw, N=N, cell_um=cell, file=f, ap={}, dropped_lam=sorted(float(x) for x in d["lam"][~g]))
    if (~g).any(): print(f"{tag}: dropped {(~g).sum()} lambda with |R+T-1| > {EMAX}: {r['dropped_lam']}")
    aps = [(f"D{D}", float(D)) for D in D_FIX if D < cell] + [(f"f{fr}", fr * cell) for fr in FRAC]
    for name, Dum in aps:
        lam, cd = disc_cd(d, Dum)
        m = (lam >= MAIN[0]) & (lam <= MAIN[1]); im = np.argmax(np.abs(np.where(m, cd, 0)))
        r["ap"][name] = dict(D_um=Dum, lam=lam.tolist(), CD=cd.tolist(), max_main=float(abs(cd[im])), signed_main=float(cd[im]),
                             lam_main=float(lam[im]), max_full=float(np.abs(cd).max()), lam_full=float(lam[np.argmax(np.abs(cd))]))
        print(f"{tag:9s} cell {cell:6.1f}  {name:6s} D {Dum:6.1f} um: main {cd[im]:+.4f} @ {lam[im]:.1f}  full {np.abs(cd).max():.4f} @ {lam[np.argmax(np.abs(cd))]:.0f}", flush=True)
    res[tag] = r

# last-two-N differences
summ = []
for tw in sorted({r["twist"] for r in res.values()}):
    Ns = sorted(r["N"] for r in res.values() if r["twist"] == tw)
    top = res[f"{tw:+g}_N{Ns[-1]}"]
    for name, a in top["ap"].items():
        row = dict(twist=tw, cell_um=top["cell_um"], ap=name, D_um=a["D_um"], N=Ns[-1], max_main=a["max_main"], signed_main=a["signed_main"],
                   lam_main=a["lam_main"], max_full=a["max_full"], lam_full=a["lam_full"],
                   per_N={str(n): res[f"{tw:+g}_N{n}"]["ap"][name]["signed_main"] for n in Ns if name in res[f"{tw:+g}_N{n}"]["ap"]})
        if len(Ns) > 1 and name in res[f"{tw:+g}_N{Ns[-2]}"]["ap"]:
            b = res[f"{tw:+g}_N{Ns[-2]}"]["ap"][name]
            la, lb = np.array(a["lam"]), np.array(b["lam"])
            cb = np.interp(la, lb, b["CD"]); diff = np.abs(np.array(a["CD"]) - cb)
            m = (la >= MAIN[0]) & (la <= MAIN[1])
            row.update(N_prev=Ns[-2], dN_main=float(diff[m].max()), dN_full=float(diff.max()),
                       dpeak_main=float(abs(a["max_main"] - b["max_main"])))
        summ.append(row)
os.makedirs(OUT, exist_ok=True)
json.dump(dict(definition=__doc__, main_line_nm=MAIN, per_run=res, summary=summ), open(os.path.join(OUT, "analysis.json"), "w"))
with open(os.path.join(OUT, "table.csv"), "w") as fh:
    fh.write("twist_deg,cell_um,aperture,D_um,N,signed_CD_main,lam_main_nm,max_CD_full,lam_full_nm,N_prev,dN_main,dpeak_main,dN_full,CD_main_per_N\n")
    for s in summ:
        fh.write(f"{s['twist']:g},{s['cell_um']:.1f},{s['ap']},{s['D_um']:.1f},{s['N']},{s['signed_main']:+.4f},{s['lam_main']:.1f},{s['max_full']:.4f},"
                 f"{s['lam_full']:.0f},{s.get('N_prev','')},{s.get('dN_main', float('nan')):.4f},{s.get('dpeak_main', float('nan')):.4f},"
                 f"{s.get('dN_full', float('nan')):.4f},\"{json.dumps(s['per_N'])}\"\n")
print("wrote", OUT)
