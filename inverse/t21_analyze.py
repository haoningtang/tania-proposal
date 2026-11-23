"""T21 analysis: E1 meets the second bright doublet near t 300 (hex_r3, gap 380). PHYSICAL polarization names.
Lines and curvatures exactly as hex_r3_analyze.py (T16c): bright = 20 < Q < 1e6 (T16c: 1e4) and weight > 0.05 at 0.5 deg azimuth 0;
doublet = TE and TM pole within half a linewidth; c from the Q-matched 3 deg pole (azimuth 0 and 30), M = -1/(2c).
Tracking (see below): lower and upper branch of the E1 / second-doublet anticrossing and the third line L3, over t 290-310 in 5 nm steps,
cost |lam - pred|/3 nm + |ln(Q/Q_prev)|/2 + |c_TE - c_TE_prev|/0.1; each line taken once per point. T16c (t 280, 320) used only for the seeds' identity.
Through an anticrossing this follows the branch continuous in (lambda, Q), i.e. the adiabatic branch, not the diabatic state.
Dark singlets: poles at 0.5 deg (either pol) with weight <= 0.05 or Q >= 1e6, or bright poles with no partner, within +-10 nm of a tracked line.
Usage: python t21_analyze.py RUN_T21 RUN_T16c"""
import csv, glob, json, os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

R, R16 = sys.argv[1], sys.argv[2]
SWAP = {"TE": "TM", "TM": "TE"}; IDENT = {"TE": "TE", "TM": "TM"}
S2 = np.sin(np.radians(3.0)) ** 2 - np.sin(np.radians(0.5)) ** 2
LO, HI = 1440, 1600


QMAX = 1e6   # T21: up to 1e6 so the high-Q (Friedrich-Wintgen-like) branch near the crossing is kept; Q > 1e4 flagged in the table


def bright(pl):
    return [p for p in pl if 20 < p["Q"] < QMAX and p["w"] > 0.05]


def qmatch(p, pl3):
    tol = max(4 * p["lam"] / p["Q"], 3.0)
    qlo, qhi = (0.5, 2) if p["Q"] < 2000 else (0.2, 5)    # high-Q lines change Q fast with angle
    c = [q for q in pl3 if abs(q["lam"] - p["lam"]) < tol and qlo < q["Q"] / p["Q"] < qhi]
    if not c: return None
    q = min(c, key=lambda q: abs(q["lam"] - p["lam"]))
    return (q["lam"] - p["lam"]) / p["lam"] / S2


def lines_of(d):
    sc = d["scans"]; PH = IDENT if d.get("pol_keys") == "physical" else SWAP
    L = {pol: bright(sc["0.5_0"][PH[pol]]["poles"]) for pol in ("TE", "TM")}
    out = []; used = set()
    for pe in L["TE"]:
        c = [(i, pm) for i, pm in enumerate(L["TM"]) if i not in used and abs(pm["lam"] - pe["lam"]) < 0.5 * pe["lam"] / min(pe["Q"], pm["Q"]) + 0.3]
        if not c: continue
        i, pm = min(c, key=lambda x: abs(x[1]["lam"] - pe["lam"])); used.add(i)
        r = dict(lam=pe["lam"], Q=pe["Q"], lam_TM=pm["lam"], Q_TM=pm["Q"], highQ=bool(pe["Q"] > 1e4))
        for pol, p in (("TE", pe), ("TM", pm)):
            for az in ("0", "30"):
                r[f"c_{pol}_{az}"] = qmatch(p, sc[f"3_{az}"][PH[pol]]["poles"])
        cs = [r[f"c_{p}_{a}"] for p in ("TE", "TM") for a in ("0", "30")]
        r["max_abs_c"] = max(abs(c) for c in cs) if all(c is not None for c in cs) else None
        r["worst_absM"] = 1 / (2 * r["max_abs_c"]) if r["max_abs_c"] else None
        out.append(r)
    dark = []
    for pol in ("TE", "TM"):
        for p in sc["0.5_0"][PH[pol]]["poles"]:
            if p["w"] <= 0.05 or p["Q"] >= QMAX or (20 < p["Q"] and not any(abs(p["lam"] - r["lam" if pol == "TE" else "lam_TM"]) < 1e-6 for r in out)):
                if p["Q"] > 20: dark.append(dict(pol=pol, lam=p["lam"], Q=p["Q"], w=p["w"]))
    return out, dark


pts = {}
for src in (R16, R):
    for f in glob.glob(os.path.join(src, "pts", "*_g380.json")):
        d = json.load(open(f)); pts[(round(d["D"], 3), d["t"])] = (d, src == R)
Ds = sorted({D for (D, t), (_, new) in pts.items() if new})
T21_t = sorted({t for (D, t), (_, new) in pts.items() if new})
SEED = dict(E1=1498.9, D2=1467.0, L3=1474.3); SEEDQ = dict(E1=135, D2=79, L3=265)   # T16c, Delta 0, t 280

rows, tracks, darks = [], {}, {}
for (D, t), (d, new) in sorted(pts.items()):
    L, dk = lines_of(d); darks[(D, t)] = dk
    if new:
        for r in L: rows.append(dict(D=D, t=t, **r))
    pts[(D, t)] = (d, new, L)

# Tracking over the T21 t grid (5 nm steps). Seeds at t 290, Delta 0: lower and upper branch of the E1/D2 anticrossing and L3
# (checked by hand against T16c t 280/320: lower = D2 at t 280 -> E1 at t 320, upper = E1 at t 280 -> D2 at t 320).
# Delta != 0: seed = line at t 290 closest to the Delta 0 seed. Lines with Q > 3e4 are not tracked.
SEED = dict(lower=1494.5, upper=1510.2, L3=1501.8)


def cost(r, ref, pred):
    c = abs(r["lam"] - pred) / 3 + abs(np.log(r["Q"] / ref["Q"])) / 2
    c += abs(r["c_TE_0"] - ref["c_TE_0"]) / 0.1 if (r["c_TE_0"] is not None and ref["c_TE_0"] is not None) else 1.0
    return c


t0 = T21_t[0]
L00 = [r for r in pts[(0.0, t0)][2] if r["Q"] < 3e4]
seed0 = {n: min(L00, key=lambda r: abs(r["lam"] - l)) for n, l in SEED.items()}
for D in Ds:
    hist = {}
    L = [r for r in pts[(D, t0)][2] if r["Q"] < 3e4]
    taken = set()
    for cst, n, i in sorted((cost(r, seed0[n], seed0[n]["lam"]), n, i) for n in SEED for i, r in enumerate(L)):
        if n in hist or i in taken: continue
        hist[n] = [(t0, L[i])]; taken.add(i)
    for t in T21_t[1:]:
        if (D, t) not in pts: continue
        L = [r for r in pts[(D, t)][2] if r["Q"] < 3e4]; cand = []
        for n, h in hist.items():
            pred = h[-1][1]["lam"] + ((h[-1][1]["lam"] - h[-2][1]["lam"]) / (h[-1][0] - h[-2][0]) * (t - h[-1][0]) if len(h) > 1 else 2.0 * (t - h[-1][0]))
            for i, r in enumerate(L): cand.append((cost(r, h[-1][1], pred), n, i))
        done, taken = set(), set()
        for cst, n, i in sorted(cand):
            if n in done or i in taken: continue
            hist[n].append((t, L[i])); done.add(n); taken.add(i)
    tracks[D] = {n: [dict(t=t, src="T21", D_pt=D, **r) for t, r in h] for n, h in hist.items()}

# CSV of all lines
cols = ["D", "t", "lam", "Q", "highQ", "lam_TM", "Q_TM", "c_TE_0", "c_TM_0", "c_TE_30", "c_TM_30", "max_abs_c", "worst_absM"]
with open(os.path.join(R, "table.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore"); w.writeheader()
    for r in sorted(rows, key=lambda r: (r["t"], r["D"], r["lam"])):
        w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
inwin = [r for r in rows if r["max_abs_c"] is not None and 1440 <= r["lam"] <= 1600]
best = sorted(inwin, key=lambda r: r["max_abs_c"])[:10]
near = {}
for D in Ds:
    for n, tr in tracks[D].items():
        for p in tr:
            if p["src"] != "T21": continue
            near[f"{n}_D{D:+.2f}_t{p['t']:.0f}"] = [k for k in darks[(D, p["t"])] if abs(k["lam"] - p["lam"]) <= 10]
summ = dict(n_points=len([1 for v in pts.values() if v[1]]), points=[f"D{D:+.3f}_t{t:.0f}" for (D, t), v in sorted(pts.items()) if v[1]],
            target="|c| <= 0.05 for TE and TM at azimuth 0 and 30 (|M| >= 10)",
            meets_target=[r for r in inwin if r["max_abs_c"] <= 0.05], within_0p15=[r for r in inwin if r["max_abs_c"] <= 0.15],
            best10=best, tracks={f"{D:+.2f}": v for D, v in tracks.items()}, dark_near_tracked=near,
            naming="physical TE/TM", settings=dict(n_terms=240, ngrid=160, angles="0.5/3 deg, az 0/30", gap=380))
json.dump(summ, open(os.path.join(R, "analysis.json"), "w"), indent=1, default=float)

# figure: row 1 lambda(t) of tracked lines per Delta; row 2 maps of c_TE_0 and c_TM_0 of the tracked lines over (t, Delta)
fig, ax = plt.subplots(2, 3, figsize=(16, 8.5))
col = dict(lower="C0", upper="C3", L3="C2")
for D in Ds:
    for n, tr in tracks[D].items():
        ax[0, 0].plot([p["t"] for p in tr], [p["lam"] for p in tr], "o-", ms=3, color=col[n], alpha=0.3 + 0.7 * (abs(D) < 1e-9))
ax[0, 0].set_xlabel("t (nm)"); ax[0, 0].set_ylabel("λ (nm), 0.5°"); ax[0, 0].set_title("tracked lines (dark = Δ 0); lower blue, upper red, L3 green")
for n, a_ in (("lower", ax[0, 1]), ("upper", ax[0, 2])):
    for D in Ds:
        tr = [p for p in tracks[D][n]]
        a_.plot([p["t"] for p in tr], [p["c_TE_0"] if p["c_TE_0"] is not None else np.nan for p in tr], "o-", ms=3, label=f"TE Δ {D:+.2f}")
        a_.plot([p["t"] for p in tr], [p["c_TM_0"] if p["c_TM_0"] is not None else np.nan for p in tr], "s--", ms=3, label=f"TM Δ {D:+.2f}")
    a_.axhspan(-0.05, 0.05, color="0.9"); a_.axhline(0, color="k", lw=0.5); a_.set_xlabel("t (nm)"); a_.set_ylabel("c (az 0)")
    a_.set_title(f"{n} branch of the E1 / second-doublet pair"); a_.legend(fontsize=6, ncol=2)
for j, (key, ttl) in enumerate((("c_TE_0", "c_TE az 0"), ("c_TM_0", "c_TM az 0"), ("max_abs_c", "max |c| (TE, TM, az 0, 30)"))):
    a_ = ax[1, j]; X, Y, Z = [], [], []
    for r in rows:
        if 1490 <= r["lam"] <= 1560 and 40 <= r["Q"] <= 2000 and r.get(key) is not None:
            X.append(r["t"] + 0.8 * (r["lam"] - 1525) / 35); Y.append(r["D"]); Z.append(r[key])
    sc = a_.scatter(X, Y, c=Z, cmap="RdBu_r", vmin=(-0.6 if j < 2 else 0), vmax=0.6, s=40, edgecolor="k", lw=0.3)
    plt.colorbar(sc, ax=a_); a_.set_xlabel("t (nm) (+ small offset ∝ λ − 1525 nm)"); a_.set_ylabel("Δ"); a_.set_title(ttl + ", lines 1490–1560 nm, Q 40–2000")
fig.tight_layout(); fig.savefig(os.path.join(R, "analysis.png"), dpi=110)
print(f"{summ['n_points']} T21 points, {len(rows)} doublets; target met: {len(summ['meets_target'])}; within 0.15: {len(summ['within_0p15'])}")
for r in best[:6]:
    print(f"  D {r['D']:+.2f} t {r['t']:.0f} lam {r['lam']:.1f} Q {r['Q']:.0f}: c_TE {r['c_TE_0']:+.3f}/{r['c_TE_30']:+.3f} c_TM {r['c_TM_0']:+.3f}/{r['c_TM_30']:+.3f}  worst|M| {r['worst_absM']:.2f}")
for D in Ds:
    for n, tr in tracks[D].items():
        print(f"D {D:+.2f} {n}: " + "  ".join(f"t{p['t']:.0f} {p['lam']:.1f}/Q{p['Q']:.0f} ({p['c_TE_0'] if p['c_TE_0'] is not None else np.nan:+.2f},{p['c_TM_0'] if p['c_TM_0'] is not None else np.nan:+.2f})" for p in tr))
