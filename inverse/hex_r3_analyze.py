"""T16c analysis: bright lines and Q-matched TE/TM curvature over the hex_r3 scan (pts/*.json from hex_r3_scan.py).

PHYSICAL polarization names. pts written before T20 (no "pol_keys" field) have swapped keys: physical TE = key "TM";
pts with pol_keys == "physical" (model.py since 2026-11-23) use the physical keys directly.
Line at 0.5 deg (pol P): pole with 20 < Q < 1e4 and weight > 0.05. Doublet: a physical-TE and a physical-TM pole within
half a linewidth (both pols bright). Curvature (T16b Q-matched slope): 3 deg pole of the same pol and azimuth within
max(4 lam/Q, 3 nm) and Q within x2, nearest in lambda; c = ((lam3 - lam05)/lam05) / (sin^2 3 - sin^2 0.5), M = -1/(2c).
Target: |M| >= 10 for TE and TM at azimuth 0 and 30, i.e. |c| <= 0.05.
Usage: python hex_r3_analyze.py RUN"""
import csv, glob, json, os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

R = sys.argv[1]
SWAP = {"TE": "TM", "TM": "TE"}        # physical -> stored key, old (swapped) pts
IDENT = {"TE": "TE", "TM": "TM"}
S2 = np.sin(np.radians(3.0)) ** 2 - np.sin(np.radians(0.5)) ** 2


def bright(pl):
    return [p for p in pl if 20 < p["Q"] < 1e4 and p["w"] > 0.05]


def qmatch(p, pl3):
    tol = max(4 * p["lam"] / p["Q"], 3.0)
    c = [q for q in pl3 if abs(q["lam"] - p["lam"]) < tol and 0.5 < q["Q"] / p["Q"] < 2]
    if not c: return None
    q = min(c, key=lambda q: abs(q["lam"] - p["lam"]))
    cc = (q["lam"] - p["lam"]) / p["lam"] / S2
    return dict(lam3=q["lam"], Q3=q["Q"], c=cc, M=(-1 / (2 * cc) if cc != 0 else np.inf))


rows = []; pts = {}
for f in sorted(glob.glob(os.path.join(R, "pts", "*.json"))):
    d = json.load(open(f)); k = os.path.basename(f)[:-5]; pts[k] = d
    sc = d["scans"]; PHYS = IDENT if d.get("pol_keys") == "physical" else SWAP
    lines = {pol: bright(sc["0.5_0"][PHYS[pol]]["poles"]) for pol in ("TE", "TM")}
    # doublets
    used = set()
    for pe in lines["TE"]:
        cands = [(i, pm) for i, pm in enumerate(lines["TM"]) if abs(pm["lam"] - pe["lam"]) < 0.5 * pe["lam"] / min(pe["Q"], pm["Q"]) + 0.3]
        pm = min(cands, key=lambda x: abs(x[1]["lam"] - pe["lam"]))[1] if cands else None
        row = dict(key=k, D=d["D"], t=d["t"], gap=d["gap"], lam=pe["lam"], Q_TE=pe["Q"], Q_TM=(pm["Q"] if pm else None),
                   lam_TM=(pm["lam"] if pm else None), doublet=pm is not None)
        for pol, p in (("TE", pe), ("TM", pm)):
            for az in ("0", "30"):
                m = qmatch(p, sc[f"3_{az}"][PHYS[pol]]["poles"]) if p else None
                row[f"c_{pol}_{az}"] = m["c"] if m else None; row[f"M_{pol}_{az}"] = m["M"] if m else None
        cs = [row[f"c_{p}_{a}"] for p in ("TE", "TM") for a in ("0", "30")]
        row["worst_absM"] = (min(abs(-1 / (2 * c)) if c else np.inf for c in cs) if all(c is not None for c in cs) else None)
        rows.append(row)
    # TM lines with no TE partner (singlets) also listed
    for pm in lines["TM"]:
        if not any(r["key"] == k and r["lam_TM"] == pm["lam"] for r in rows):
            row = dict(key=k, D=d["D"], t=d["t"], gap=d["gap"], lam=pm["lam"], Q_TE=None, Q_TM=pm["Q"], lam_TM=pm["lam"], doublet=False)
            for az in ("0", "30"):
                m = qmatch(pm, sc[f"3_{az}"][PHYS["TM"]]["poles"])
                row[f"c_TM_{az}"] = m["c"] if m else None; row[f"M_TM_{az}"] = m["M"] if m else None
                row[f"c_TE_{az}"] = None; row[f"M_TE_{az}"] = None
            row["worst_absM"] = None; rows.append(row)

cols = ["key", "D", "t", "gap", "lam", "Q_TE", "lam_TM", "Q_TM", "doublet", "c_TE_0", "c_TM_0", "c_TE_30", "c_TM_30",
        "M_TE_0", "M_TM_0", "M_TE_30", "M_TM_30", "worst_absM"]
with open(os.path.join(R, "table.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore"); w.writeheader()
    for r in sorted(rows, key=lambda r: (r["t"], r["gap"], r["D"], r["lam"])):
        w.writerow({c: (round(v, 5) if isinstance(v, float) else v) for c, v in r.items()})
dbl = [r for r in rows if r["doublet"] and r["worst_absM"] is not None]
best = sorted(dbl, key=lambda r: -r["worst_absM"])[:10]
# E1 line per point: the doublet nearest the D = 0 E1 line at the same (t, gap); D = 0 E1 = doublet nearest 1498.6 nm (base)
e1 = {}
for (t, g) in sorted({(r["t"], r["gap"]) for r in rows}):
    z = [r for r in dbl if r["t"] == t and r["gap"] == g and abs(r["D"]) < 1e-9]
    ref = min(z, key=lambda r: abs(r["lam"] - 1498.6))["lam"] if z else None   # D = 0: doublet nearest the T12a E1 line
    if not ref: continue
    Dall = sorted({r["D"] for r in rows if r["t"] == t and r["gap"] == g})
    # follow the E1 line outwards from D = 0 in both directions: nearest in lambda (10 nm) and Q (log ratio) to the neighbour
    for side in (1, -1):
        prev = None
        for D in sorted([D for D in Dall if D * side >= 0], key=abs):
            c = [r for r in dbl if r["t"] == t and r["gap"] == g and r["D"] == D]
            if not c: continue
            if prev is None:
                e1[(t, g, D)] = prev = min(c, key=lambda r: abs(r["lam"] - ref)); continue
            e1[(t, g, D)] = prev = min(c, key=lambda r: abs(r["lam"] - prev["lam"]) / 10 + abs(np.log(r["Q_TE"] / prev["Q_TE"])))
summ = dict(n_points=len(pts), n_lines=len(rows), n_doublets_with_all_slopes=len(dbl),
            meets_target=[r for r in dbl if r["worst_absM"] >= 10],
            best10=best, E1={f"t{t:.0f}_g{g:.0f}_D{D:+.3f}": v for (t, g, D), v in e1.items()},
            naming="physical TE/TM (model.py keys swapped)")
json.dump(summ, open(os.path.join(R, "analysis.json"), "w"), indent=1, default=float)

# figure: c_TM (physical) at azimuth 0 and 30 of the E1 line vs D, one panel per (t, gap)
tg = sorted({(t, g) for (t, g, D) in e1})
fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
for t, g in tg:
    Ds = sorted(D for (tt, gg, D) in e1 if (tt, gg) == (t, g))
    for j, (pol, az, a_) in enumerate((("TM", "0", ax[0]), ("TM", "30", ax[1]), ("TE", "0", ax[2]))):
        y = [e1[(t, g, D)][f"c_{pol}_{az}"] for D in Ds]
        a_.plot(Ds, [np.nan if v is None else v for v in y], "o-", ms=3, label=f"t {t:.0f}, gap {g:.0f}")
for a_, ttl in zip(ax, ("c_TM azimuth 0", "c_TM azimuth 30", "c_TE azimuth 0")):
    a_.axhspan(-0.05, 0.05, color="0.9"); a_.axhline(0, color="k", lw=0.5); a_.set_xlabel("Δ = (r1 − rb)/a"); a_.set_title(ttl + " (physical), E1 line")
ax[0].legend(fontsize=6); fig.tight_layout(); fig.savefig(os.path.join(R, "analysis.png"), dpi=110)
print(f"{len(pts)} points, {len(rows)} lines, {len(dbl)} doublets with all slopes; target met: {len(summ['meets_target'])}")
for r in best[:6]:
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
