"""T16a: merge map_*.json, write analysis.json (table + zero contours + best point) and analysis.png.

Usage: python curv_map_analyze.py ../runs/<name>
"""
import glob, json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = sys.argv[1]
pts = {}
for f in sorted(glob.glob(os.path.join(d, "map_*.json"))):
    S = json.load(open(f))
    settings = S["settings"]
    for q in S["points"]:
        pts[(q["dt2"], q["dr2"])] = q
G = settings["grid_nm"]; n = len(G)
F = {k: np.full((n, n), np.nan) for k in ("lam_TE", "lam_TM", "Q_TE", "Q_TM", "c_TE", "c_TM", "M_TE", "M_TM")}
rows = []
for (t2, r2), q in sorted(pts.items()):
    i, j = G.index(t2), G.index(r2)
    row = dict(dt2_nm=t2, dr2_nm=r2)
    for pol in ("TE", "TM"):
        b = q[pol]
        if b is None:
            continue
        for k in ("lam", "Q", "c", "M"):
            F[f"{k}_{pol}"][i, j] = b[k]
            row[f"{k}_{pol}"] = b[k] * 1e3 if k == "lam" else b[k]
    rows.append(row)


def zero_crossings(Z):
    """linear-interpolated zero crossings along grid edges: list of (dt2, dr2) in nm"""
    out = []
    for i in range(n):
        for j in range(n):
            for di, dj in ((1, 0), (0, 1)):
                if i + di < n and j + dj < n:
                    z0, z1 = Z[i, j], Z[i + di, j + dj]
                    if np.isfinite(z0) and np.isfinite(z1) and z0 * z1 < 0:
                        s = z0 / (z0 - z1)
                        out.append((G[i] + s * (G[i + di] - G[i]) if di else G[i],
                                    G[j] + s * (G[j + dj] - G[j]) if dj else G[j]))
    return out


zTE, zTM = zero_crossings(F["c_TE"]), zero_crossings(F["c_TM"])
# closest approach on the grid: minimize max(|c_TE|, |c_TM|)
W = np.fmax(np.abs(F["c_TE"]), np.abs(F["c_TM"]))
ib = np.unravel_index(np.nanargmin(W), W.shape)
best = dict(dt2_nm=G[ib[0]], dr2_nm=G[ib[1]], c_TE=F["c_TE"][ib], c_TM=F["c_TM"][ib], M_TE=F["M_TE"][ib], M_TM=F["M_TM"][ib],
            lam_TE_nm=F["lam_TE"][ib] * 1e3, Q_TE=F["Q_TE"][ib], Q_TM=F["Q_TM"][ib])
# M >= 10 means |c| <= 0.05
both10 = [(G[i], G[j]) for i in range(n) for j in range(n) if W[i, j] <= 0.05]
out = dict(settings=settings, n_points=len(pts), rows=rows, zero_TE=zTE, zero_TM=zTM, closest=best,
           points_both_absM_ge_10=both10)
json.dump(out, open(os.path.join(d, "analysis.json"), "w"), indent=1, default=float)

fig, ax = plt.subplots(2, 3, figsize=(13, 8), constrained_layout=True)
ext = [G[0] - 6.67, G[-1] + 6.67, G[0] - 6.67, G[-1] + 6.67]   # x = dr2, y = dt2
cm = max(np.nanmax(np.abs(F["c_TE"])), np.nanmax(np.abs(F["c_TM"])))
for k, (key, title) in enumerate((("c_TE", "c_TE"), ("c_TM", "c_TM"))):
    a_ = ax[0, k]
    im = a_.imshow(F[key], origin="lower", extent=ext, cmap="RdBu_r", vmin=-cm, vmax=cm)
    fig.colorbar(im, ax=a_, shrink=0.8)
    a_.set_title(f"{title} = (Δλ/λ)/sin²θ")
for k in (0, 1):
    for key, col, ls in (("c_TE", "k", "-"), ("c_TM", "k", "--")):
        if np.nanmin(F[key]) < 0 < np.nanmax(F[key]):
            ax[0, k].contour(G, G, F[key], [0], colors=col, linestyles=ls)
a_ = ax[0, 2]
im = a_.imshow(np.log10(1 / np.maximum(W, 1e-6) / 2), origin="lower", extent=ext, cmap="viridis")
fig.colorbar(im, ax=a_, shrink=0.8, label="log10 min(|M_TE|, |M_TM|)")
a_.plot(best["dr2_nm"], best["dt2_nm"], "r*", ms=12)
a_.set_title("min |M| (red star: closest approach)")
for k, (key, title, cmap) in enumerate((("lam_TE", "λ TE at 0.5° (nm)", "cividis"), ("Q_TE", "Q TE at 0.5°", "magma"),
                                        ("lam_TM", "λ TM − λ TE at 0.5° (nm)", "RdBu_r"))):
    a_ = ax[1, k]
    Z = F[key] * 1e3 if key.startswith("lam") else F[key]
    if key == "lam_TM":
        Z = (F["lam_TM"] - F["lam_TE"]) * 1e3; v = np.nanmax(np.abs(Z)) or 1
        im = a_.imshow(Z, origin="lower", extent=ext, cmap=cmap, vmin=-v, vmax=v)
    else:
        im = a_.imshow(Z, origin="lower", extent=ext, cmap=cmap)
    fig.colorbar(im, ax=a_, shrink=0.8); a_.set_title(title)
for a_ in ax.flat:
    a_.set_xlabel("r2 − r (nm)"); a_.set_ylabel("t2 − t (nm)")
fig.suptitle(f"T16a hex E1 line (a 850, r 212.5, t 280 nm), gap {settings['gap']*1e3:.0f} nm, "
             f"{settings['n_terms']}/{settings['ngrid']}, θ {settings['thetas']}°, az {settings.get('azimuth_deg', 0)}°; "
             "contours: c_TE = 0 solid, c_TM = 0 dashed")
fig.savefig(os.path.join(d, "analysis.png"), dpi=110)
print(json.dumps(dict(n=len(pts), zero_TE=len(zTE), zero_TM=len(zTM), closest=best, both10=both10), default=float, indent=1))
