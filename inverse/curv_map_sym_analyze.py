"""T16b: merge map_*.json of curv_map_sym.py, write analysis.json, table.csv and analysis.png.

Per point: lam, Q, c, M for TE and TM (bright line followed from the T12a base), and the nearest OTHER pole within
+-25 nm (wide scan) per polarization at 0.5 deg and at the wide angle (3 deg), with its Q.
Usage: python curv_map_sym_analyze.py ../runs/<name>
"""
import csv, glob, json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = sys.argv[1]
pts = {}
for f in sorted(glob.glob(os.path.join(d, "map_*.json"))):
    S = json.load(open(f)); settings = S["settings"]
    for q in S["points"]:
        pts[(q["dt2"], q["dr2"])] = q
GT, GR = settings["tgrid_nm"], settings["ragrid"]; nT, nR = len(GT), len(GR)
keys = ("lam_TE", "lam_TM", "Q_TE", "Q_TM", "c_TE", "c_TM", "M_TE", "M_TM", "dl_TM", "Qn_TM", "dl_TE", "Qn_TE")
F = {k: np.full((nT, nR), np.nan) for k in keys}
QDARK = 1e4
QHOP = 2.0
SAME = 0.3e-3   # poles closer than this (um) to the followed line are the line itself


def hops(q):
    if not q.get("start") or q["TE"] is None:
        return []
    seq = [(0.0, *q["start"]["TE"])] + [(r[0], r[1], r[2]) for r in q["path"]] + [(1.0, q["TE"]["lam"], q["TE"]["Q"])]
    return [[round(b[0], 2), round((b[1] - a[1]) * 1e3, 2), round(a[1] / a[2] * 1e3, 2)]
            for a, b in zip(seq, seq[1:]) if abs(b[1] - a[1]) > 0.5 * a[1] / a[2]]


def nearest(q, pol, th, lref=None):
    """nearest other pole to the followed line, in the wide scan at angle th; the reference is the line's lam at th
    (at the wide angle: the Q-matched pole if there is one, since the tracker can switch poles)"""
    b = q[pol]
    if b is None or "wide" not in q:
        return None
    if lref is None:
        ref = [x for x in b["pts"] if abs(x[0] - float(th)) < 1e-6]
        if not ref:
            return None
        lref = ref[0][1]
    P = [x for x in q["wide"][str(th)][pol] if abs(x[0] - lref) > SAME]
    if not P:
        return None
    l, Q = min(P, key=lambda x: abs(x[0] - lref))
    return dict(dlam_nm=(l - lref) * 1e3, lam_nm=l * 1e3, Q=Q)


wth = str(settings["wide_theta"]); th0 = str(settings["thetas"][0])
rows = []
for (tn, ra), q in sorted(pts.items()):
    i, j = GT.index(tn), GR.index(ra)
    row = dict(t_nm=tn, r_over_a=ra, from_=q.get("from_"), hops=hops(q))
    row["dark"] = bool(q["TE"] and q["TE"]["Q"] > QDARK)
    # E1 doublet: TE and TM on the same line at 0.5 deg (|dlam| < half the larger linewidth); otherwise not the E1 line -> masked
    row["split"] = bool(q["TE"] is None or q["TM"] is None or
                        abs(q["TE"]["lam"] - q["TM"]["lam"]) > 0.5 * max(q["TE"]["lam"] / q["TE"]["Q"], q["TM"]["lam"] / q["TM"]["Q"]))
    for pol in ("TE", "TM"):
        b = q[pol]
        if b is None:
            continue
        # angle hop: Q changes > 2x between consecutive angles -> the 3-angle fit mixes poles; use the 0.5->3 deg slope
        P = b["pts"]
        hop = any(max(p1[2], p2[2]) / min(p1[2], p2[2]) > QHOP for p1, p2 in zip(P, P[1:]))
        c3 = ((P[1][1] - P[0][1]) / P[0][1]) / (np.sin(np.radians(P[1][0])) ** 2 - np.sin(np.radians(P[0][0])) ** 2) if len(P) > 1 else np.nan
        row[f"c_fit3_{pol}"] = b["c"]; row[f"c_05_3_{pol}"] = float(c3); row[f"angle_hop_{pol}"] = bool(hop or len(P) < 3)
        # Q-matched slope from the wide scans: at the wide angle take the pole minimizing |ln(Q/Q05)| + |dlam|/(2 linewidth)
        cq = np.nan
        if "wide" in q and q["wide"][wth][pol]:
            l5, Q5 = P[0][1], P[0][2]
            l3, Q3 = min(q["wide"][wth][pol], key=lambda x: abs(np.log(x[1] / Q5)) + abs(x[0] - l5) / (2 * l5 / Q5))
            if abs(l3 - l5) < max(4 * l5 / Q5, 3e-3) and abs(np.log(Q3 / Q5)) < np.log(2):
                cq = ((l3 - l5) / l5) / (np.sin(np.radians(float(wth))) ** 2 - np.sin(np.radians(P[0][0])) ** 2)
                row[f"qmatch_{pol}"] = dict(lam3_nm=l3 * 1e3, Q3=Q3, c=float(cq))
        row[f"c_qmatch_{pol}"] = float(cq)
        b = dict(b, c=float(cq) if np.isfinite(cq) else (float(c3) if row[f"angle_hop_{pol}"] else b["c"]))
        b["M"] = -1 / (2 * b["c"]) if b["c"] else np.inf
        for k in ("lam", "Q", "c", "M"):
            row[f"{k}_{pol}"] = b[k] * 1e3 if k == "lam" else b[k]
        qm = row.get(f"qmatch_{pol}")
        row[f"nearest_{pol}_{th0}deg"] = nearest(q, pol, th0)
        row[f"nearest_{pol}_{wth}deg"] = nearest(q, pol, wth, qm["lam3_nm"] * 1e-3 if qm else None)
        if row["dark"] or row["split"]:
            continue
        for k in ("lam", "Q", "c", "M"):
            F[f"{k}_{pol}"][i, j] = b[k]
        nb = row[f"nearest_{pol}_{wth}deg"]
        if nb:
            F[f"dl_{pol}"][i, j] = nb["dlam_nm"]; F[f"Qn_{pol}"][i, j] = nb["Q"]
    row["all_poles_wide"] = {th: {pol: [[round(l * 1e3, 3), round(Q, 1)] for l, Q in v] for pol, v in w.items()}
                             for th, w in q.get("wide", {}).items()}
    rows.append(row)


def zero_crossings(Z):
    out = []
    for i in range(nT):
        for j in range(nR):
            for di, dj in ((1, 0), (0, 1)):
                if i + di < nT and j + dj < nR:
                    z0, z1 = Z[i, j], Z[i + di, j + dj]
                    if np.isfinite(z0) and np.isfinite(z1) and z0 * z1 < 0:
                        s = z0 / (z0 - z1)
                        out.append(dict(t_nm=GT[i] + s * (GT[i + di] - GT[i]) if di else GT[i],
                                        r_over_a=GR[j] + s * (GR[j + dj] - GR[j]) if dj else GR[j],
                                        between=[[GT[i], GR[j]], [GT[i + di], GR[j + dj]]]))
    return out


zTE, zTM = zero_crossings(F["c_TE"]), zero_crossings(F["c_TM"])
W = np.maximum(np.abs(F["c_TE"]), np.abs(F["c_TM"]))
ib = np.unravel_index(np.nanargmin(W), W.shape)
best = dict(t_nm=GT[ib[0]], r_over_a=GR[ib[1]], **{k: float(F[k][ib]) for k in ("c_TE", "c_TM", "M_TE", "M_TM", "Q_TE", "Q_TM")},
            lam_TE_nm=float(F["lam_TE"][ib] * 1e3))
ibm = np.unravel_index(np.nanargmin(np.abs(F["c_TM"])), W.shape)
best_TM = dict(t_nm=GT[ibm[0]], r_over_a=GR[ibm[1]], **{k: float(F[k][ibm]) for k in ("c_TE", "c_TM", "M_TE", "M_TM", "Q_TM")},
               lam_TM_nm=float(F["lam_TM"][ibm] * 1e3))
bright = [r for r in rows if not r["dark"] and not r["split"] and np.isfinite(r.get("c_TM", np.nan))]
ranges = {k: [min(r[k] for r in bright), max(r[k] for r in bright)] for k in ("c_TE", "c_TM", "M_TM", "lam_TE", "Q_TE")}
# trend: c_TM vs |distance| to the nearest TM pole at the wide angle
m = np.isfinite(F["c_TM"]) & np.isfinite(F["dl_TM"])
x, y = np.abs(F["dl_TM"][m]), F["c_TM"][m]
corr = float(np.corrcoef(np.log(x), y)[0, 1]) if m.sum() > 2 else float("nan")
out = dict(settings=settings, n_points=len(pts), n_bright=len(bright),
           dark_points=[(r["t_nm"], r["r_over_a"]) for r in rows if r["dark"]],
           split_points=[(r["t_nm"], r["r_over_a"]) for r in rows if r["split"]], n_with_hops=sum(1 for r in rows if r["hops"]), n_angle_hop=sum(1 for r in rows if r.get("angle_hop_TE") or r.get("angle_hop_TM")),
           ranges_bright=ranges, zero_TE=zTE, zero_TM=zTM, closest_both=best, smallest_abs_c_TM=best_TM,
           corr_cTM_vs_log_abs_dl_TM=corr, points_both_absM_ge_10=[(GT[i], GR[j]) for i in range(nT) for j in range(nR) if W[i, j] <= 0.05],
           rows=rows)
json.dump(out, open(os.path.join(d, "analysis.json"), "w"), indent=1, default=float)
with open(os.path.join(d, "table.csv"), "w", newline="") as fh:
    cols = ["t_nm", "r_over_a", "dark", "lam_TE", "Q_TE", "c_TE", "M_TE", "lam_TM", "Q_TM", "c_TM", "M_TM",
            "near_TM_dl_nm", "near_TM_Q", "near_TE_dl_nm", "near_TE_Q", "n_hops"]
    w = csv.writer(fh); w.writerow(cols)
    for r in rows:
        nm, ne = r.get(f"nearest_TM_{wth}deg"), r.get(f"nearest_TE_{wth}deg")
        w.writerow([r["t_nm"], r["r_over_a"], r["dark"]] + [r.get(k, "") for k in cols[3:11]] +
                   [nm and round(nm["dlam_nm"], 2), nm and round(nm["Q"]), ne and round(ne["dlam_nm"], 2), ne and round(ne["Q"]), len(r["hops"])])

fig, ax = plt.subplots(2, 3, figsize=(14, 8.5), constrained_layout=True)
dR, dT = (GR[1] - GR[0]) / 2, (GT[1] - GT[0]) / 2
ext = [GR[0] - dR, GR[-1] + dR, GT[0] - dT, GT[-1] + dT]
cm = np.nanmax(np.abs(np.r_[F["c_TE"].ravel(), F["c_TM"].ravel()]))
for k, key in enumerate(("c_TE", "c_TM")):
    a_ = ax[0, k]
    im = a_.imshow(F[key], origin="lower", extent=ext, aspect="auto", cmap="RdBu_r", vmin=-cm, vmax=cm)
    fig.colorbar(im, ax=a_, shrink=0.8); a_.set_title(f"{key} = (Δλ/λ)/sin²θ")
    for kk, ls in (("c_TE", "-"), ("c_TM", "--")):
        Z = F[kk]
        if np.nanmin(Z) < 0 < np.nanmax(Z):
            a_.contour(GR, GT, Z, [0], colors="k", linestyles=ls)
a_ = ax[0, 2]
im = a_.imshow(np.log10(1 / np.maximum(W, 1e-6) / 2), origin="lower", extent=ext, aspect="auto", cmap="viridis")
fig.colorbar(im, ax=a_, shrink=0.8, label="log10 min(|M_TE|, |M_TM|)")
a_.plot(best["r_over_a"], best["t_nm"], "r*", ms=12); a_.set_title("min |M| (star: closest approach)")
a_ = ax[1, 0]
im = a_.imshow(F["lam_TE"] * 1e3, origin="lower", extent=ext, aspect="auto", cmap="cividis")
fig.colorbar(im, ax=a_, shrink=0.8); a_.set_title("λ (TE) at 0.5° (nm)")
a_ = ax[1, 1]
v = np.nanmax(np.abs(F["dl_TM"])) if np.isfinite(F["dl_TM"]).any() else 25
im = a_.imshow(F["dl_TM"], origin="lower", extent=ext, aspect="auto", cmap="PuOr", vmin=-v, vmax=v)
fig.colorbar(im, ax=a_, shrink=0.8); a_.set_title(f"nearest other TM pole − line at {wth}° (nm)")
for a_ in list(ax[0]) + [ax[1, 0], ax[1, 1]]:
    for r in rows:
        if r["dark"]:
            a_.plot(r["r_over_a"], r["t_nm"], "x", color="0.4", ms=8)
        elif r["split"]:
            a_.plot(r["r_over_a"], r["t_nm"], "+", color="0.4", ms=9)
        elif r["hops"]:
            a_.plot(r["r_over_a"], r["t_nm"], ".", color="0.3", ms=4)
        if r.get("angle_hop_TM") or r.get("angle_hop_TE"):
            a_.plot(r["r_over_a"], r["t_nm"], "o", mfc="none", mec="m", ms=9)
    a_.set_xlabel("r/a"); a_.set_ylabel("t (nm)")
a_ = ax[1, 2]
if m.any():
    sc = a_.scatter(F["dl_TM"][m], F["c_TM"][m], c=np.log10(F["Qn_TM"][m]), cmap="plasma", s=25)
    fig.colorbar(sc, ax=a_, shrink=0.8, label=f"log10 Q of that pole at {wth}°")
a_.axhline(0, color="k", lw=0.5); a_.axvline(0, color="k", lw=0.5)
a_.set_xlabel(f"nearest TM pole − line at {wth}° (nm)"); a_.set_ylabel("c_TM"); a_.set_title("c_TM vs nearest TM pole")
fig.suptitle(f"T16b hex E1 line, symmetric r/a × t (a 850, gap {settings['gap']*1e3:.0f} nm), {settings['n_terms']}/{settings['ngrid']}, "
             f"θ {settings['thetas']}°, az {settings.get('azimuth_deg', 0)}°\ncontours c_TE = 0 solid, c_TM = 0 dashed. "
             "x: Q > 1e4 line, +: TE and TM on different lines (both masked)\ndot: λ hop > ½ linewidth along the follow path; magenta ring: tracker pole switch in angle (Q ×2). c = Q-matched 0.5→3° slope from the wide scans")
fig.savefig(os.path.join(d, "analysis.png"), dpi=110)
print(json.dumps(dict(n=len(pts), n_bright=len(bright), ranges=ranges, dark=out["dark_points"], split=out["split_points"], n_hops=out["n_with_hops"], n_angle_hop=out["n_angle_hop"],
                      zero_TE=len(zTE), zero_TM=zTM, closest=best, smallest_cTM=best_TM, corr=corr), default=float, indent=1))
