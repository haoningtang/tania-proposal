"""T22 analysis: hex sqrt3 x sqrt3 supercell, hole-size scan (mean r/a 0.20/0.22/0.28/0.30, T16c r/a 0.25 as reference),
t 280, gap 380, Delta 0 / +-0.05 / +-0.03. PHYSICAL polarization names (T16c points have swapped keys; converted on load).
Lines and curvatures as t21_analyze.py (bright = 20 < Q < 1e6, weight > 0.05 at 0.5 deg az 0; doublet = TE and TM pole within half a
linewidth; c from the Q-matched 3 deg pole with the T21 qmatch rule, M = -1/(2c)).
E1: at r/a 0.25, Delta 0 the T16c line at 1498.9 nm (Q 135); followed to the other r/a by continuity in (lambda, Q, c_TE); at Delta != 0 the
line closest (same cost) to E1 at Delta 0 and the same r/a. The candidate list per r/a is printed for a check by eye.
Partners: every 3 deg pole (TE or TM, az 0 or 30, Q > 20) within +-15 nm of E1 that is NOT the 3 deg continuation of a bright doublet of the
same point, plus 0.5 deg dark poles (weight <= 0.05 or Q >= 1e6 or unpaired). For each, the branch it couples to = the polarization(s)
in which it appears at 3 deg; "TE-acting" if it appears in TE and not in TM within a linewidth.
Usage: python t22_analyze.py RUN_T22 RUN_T16c"""
import csv, glob, json, os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

R, R16 = sys.argv[1], sys.argv[2]
SWAP = {"TE": "TM", "TM": "TE"}; IDENT = {"TE": "TE", "TM": "TM"}
S2 = np.sin(np.radians(3.0)) ** 2 - np.sin(np.radians(0.5)) ** 2
QMAX = 1e6
WIN = 15.0


def bright(pl):
    return [p for p in pl if 20 < p["Q"] < QMAX and p["w"] > 0.05]


def qmatch_pole(p, pl3):
    tol = max(4 * p["lam"] / p["Q"], 3.0)
    qlo, qhi = (0.5, 2) if p["Q"] < 2000 else (0.2, 5)
    c = [q for q in pl3 if abs(q["lam"] - p["lam"]) < tol and qlo < q["Q"] / p["Q"] < qhi]
    if not c: return None
    return min(c, key=lambda q: abs(np.log(q["Q"] / p["Q"])) + abs(q["lam"] - p["lam"]) * p["Q"] / p["lam"])


def cval(p, q):
    return None if q is None else (q["lam"] - p["lam"]) / p["lam"] / S2


def lines_of(d):
    sc = d["scans"]; PH = IDENT if d.get("pol_keys") == "physical" else SWAP
    L = {pol: bright(sc["0.5_0"][PH[pol]]["poles"]) for pol in ("TE", "TM")}
    out = []; used = set(); used3 = set()
    for pe in L["TE"]:
        c = [(i, pm) for i, pm in enumerate(L["TM"]) if i not in used and abs(pm["lam"] - pe["lam"]) < 0.5 * pe["lam"] / min(pe["Q"], pm["Q"]) + 0.3
             and 1 / 3 < pm["Q"] / pe["Q"] < 3]   # T22: Q-ratio guard (T16c rule paired a Q 1e5 TE pole with the Q 96 TM pole of E1)
        if not c: continue
        i, pm = min(c, key=lambda x: abs(x[1]["lam"] - pe["lam"])); used.add(i)
        r = dict(lam=pe["lam"], Q=pe["Q"], lam_TM=pm["lam"], Q_TM=pm["Q"], highQ=bool(pe["Q"] > 1e4))
        for pol, p in (("TE", pe), ("TM", pm)):
            for az in ("0", "30"):
                q = qmatch_pole(p, sc[f"3_{az}"][PH[pol]]["poles"])
                r[f"c_{pol}_{az}"] = cval(p, q)
                if q is not None: used3.add((pol, az, round(q["lam"], 4)))
        cs = [r[f"c_{p}_{a}"] for p in ("TE", "TM") for a in ("0", "30")]
        r["max_abs_c"] = max(abs(c) for c in cs) if all(c is not None for c in cs) else None
        r["worst_absM"] = 1 / (2 * r["max_abs_c"]) if r["max_abs_c"] else None
        out.append(r)
    # the 3 deg continuations of unpaired bright 0.5 deg poles are not partners either (they are bright lines)
    for pol in ("TE", "TM"):
        for p in L[pol]:
            for az in ("0", "30"):
                q = qmatch_pole(p, sc[f"3_{az}"][PH[pol]]["poles"])
                if q is not None and p["Q"] < 2000: used3.add((pol, az, round(q["lam"], 4)))
    extra3 = []
    for pol in ("TE", "TM"):
        for az in ("0", "30"):
            for q in sc[f"3_{az}"][PH[pol]]["poles"]:
                if q["Q"] > 20 and (pol, az, round(q["lam"], 4)) not in used3:
                    extra3.append(dict(pol=pol, az=az, lam=q["lam"], Q=q["Q"], w=q["w"]))
    dark05 = []
    for pol in ("TE", "TM"):
        for p in sc["0.5_0"][PH[pol]]["poles"]:
            if p["Q"] > 20 and (p["w"] <= 0.05 or p["Q"] >= QMAX or not any(abs(p["lam"] - r["lam" if pol == "TE" else "lam_TM"]) < 1e-6 for r in out)):
                dark05.append(dict(pol=pol, lam=p["lam"], Q=p["Q"], w=p["w"]))
    return out, extra3, dark05


def partners(E, extra3):
    """group the 3 deg extra poles within +-WIN nm of E1 into lines; branch = polarizations where they appear"""
    ps = sorted([q for q in extra3 if abs(q["lam"] - E["lam"]) <= WIN and q["w"] > 1e-3], key=lambda q: q["lam"])
    groups = []
    for q in ps:
        for g in groups:
            ref = g[0]
            if abs(q["lam"] - ref["lam"]) < max(0.5 * ref["lam"] / min(ref["Q"], q["Q"]), 0.3) and abs(np.log(q["Q"] / ref["Q"])) < 1.0:
                g.append(q); break
        else:
            groups.append([q])
    out = []
    for g in groups:
        pols = sorted({q["pol"] for q in g}); azs = sorted({q["az"] for q in g})
        out.append(dict(lam3=float(np.mean([q["lam"] for q in g])), dlam=float(np.mean([q["lam"] for q in g]) - E["lam"]),
                        Q3=float(np.exp(np.mean([np.log(q["Q"]) for q in g]))), wmax=max(q["w"] for q in g),
                        pols=pols, azs=azs, acts_on=("TE" if pols == ["TE"] else "TM" if pols == ["TM"] else "both"),
                        detail=[{k: (round(v, 3) if isinstance(v, float) else v) for k, v in q.items()} for q in g]))
    return out


pts = {}
for f in glob.glob(os.path.join(R16, "pts", "D*_t280_g380.json")):
    d = json.load(open(f)); D = round(d["D"], 3)
    if D in (0.0, 0.05, -0.05, 0.03, -0.03): pts[(0.25, D)] = (d, False)
for f in glob.glob(os.path.join(R, "pts", "r*_t280_g380.json")):
    d = json.load(open(f)); pts[(round(d["rbar_over_a"], 3), round(d["D"], 3))] = (d, True)
P = {k: lines_of(d) + (new,) for k, (d, new) in pts.items()}
rs = sorted({r for r, D in P}); Ds = sorted({D for r, D in P})


def cost(r, ref, pred):
    c = abs(r["lam"] - pred) / 10 + abs(np.log(r["Q"] / ref["Q"]))
    c += abs(r["c_TE_0"] - ref["c_TE_0"]) / 0.2 if (r["c_TE_0"] is not None and ref["c_TE_0"] is not None) else 1.0
    return c


E1 = {}
L0 = [x for x in P[(0.25, 0.0)][0] if x["Q"] < 3e4]
E1[(0.25, 0.0)] = min(L0, key=lambda x: abs(x["lam"] - 1498.9))
cand_log = {}
for seq in ([0.28, 0.30], [0.22, 0.20]):
    prev_r, prev2 = 0.25, None
    for r in seq:
        if (r, 0.0) not in P: break
        ref = E1[(prev_r, 0.0)]
        pred = ref["lam"] + ((ref["lam"] - E1[(prev2, 0.0)]["lam"]) / (prev_r - prev2) * (r - prev_r) if prev2 else 0.0)
        L = [x for x in P[(r, 0.0)][0] if x["Q"] < 3e4 and abs(x["lam"] - pred) < 120]
        L.sort(key=lambda x: cost(x, ref, pred))
        cand_log[r] = [(round(cost(x, ref, pred), 2), round(x["lam"], 1), round(x["Q"]), x["c_TE_0"], x["c_TM_0"]) for x in L[:5]]
        if L: E1[(r, 0.0)] = L[0]
        prev2, prev_r = prev_r, r
for (r, D) in P:
    if D == 0.0 or (r, 0.0) not in E1: continue
    ref = E1[(r, 0.0)]
    L = [x for x in P[(r, D)][0] if x["Q"] < 3e4]
    if L: E1[(r, D)] = min(L, key=lambda x: cost(x, ref, ref["lam"]))

rows = []
for (r, D), (L, ex, dk, new) in sorted(P.items()):
    for x in L: rows.append(dict(rbar=r, D=D, src="T22" if new else "T16c", **x))
cols = ["rbar", "D", "src", "lam", "Q", "highQ", "lam_TM", "Q_TM", "c_TE_0", "c_TM_0", "c_TE_30", "c_TM_30", "max_abs_c", "worst_absM"]
with open(os.path.join(R, "table.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore"); w.writeheader()
    for x in sorted(rows, key=lambda x: (x["rbar"], x["D"], x["lam"])):
        w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in x.items()})

e1tab = {}
for (r, D), E in sorted(E1.items()):
    pr = partners(E, P[(r, D)][1])
    dk = [k for k in P[(r, D)][2] if abs(k["lam"] - E["lam"]) <= WIN]
    e1tab[f"r{r:.2f}_D{D:+.2f}"] = dict(rbar=r, D=D, E1=E, partners_3deg=pr, dark_0p5deg=dk)

# stop rule: c_TE of E1 between Delta 0 and +-0.05
stop = {}
for r in rs:
    if (r, 0.0) in E1:
        c0 = E1[(r, 0.0)]["c_TE_0"]
        stop[f"{r:.2f}"] = {f"{D:+.2f}": (None if E1.get((r, D), {}).get("c_TE_0") is None or c0 is None else E1[(r, D)]["c_TE_0"] - c0) for D in (0.05, -0.05)}
inwin = [x for x in rows if x["max_abs_c"] is not None and x["src"] == "T22"]
summ = dict(points=[f"r{r:.2f}_D{D:+.2f}" for (r, D), v in sorted(P.items()) if v[3]],
            target="|c| <= 0.05 for TE and TM at azimuth 0 and 30 (|M| >= 10)",
            meets_target=[x for x in inwin if x["max_abs_c"] <= 0.05], within_0p15=[x for x in inwin if x["max_abs_c"] <= 0.15],
            best10=sorted(inwin, key=lambda x: x["max_abs_c"])[:10], E1=e1tab, E1_candidates_by_rbar=cand_log,
            stop_rule_dcTE_vs_D0=stop, naming="physical TE/TM (T16c swapped keys converted)",
            settings=dict(n_terms=240, ngrid=160, angles="0.5/3 deg, az 0/30", t=280, gap=380))
json.dump(summ, open(os.path.join(R, "analysis.json"), "w"), indent=1, default=float)

fig, ax = plt.subplots(2, 2, figsize=(13, 9))
for D in Ds:
    xs = [r for r in rs if (r, D) in E1]
    ax[0, 0].plot(xs, [E1[(r, D)]["lam"] for r in xs], "o-", label=f"Δ {D:+.2f}")
ax[0, 0].set_xlabel("mean r/a"); ax[0, 0].set_ylabel("E1 λ (nm), 0.5°"); ax[0, 0].legend(fontsize=7); ax[0, 0].set_title("E1 (t 280, gap 380)")
for j, pol in enumerate(("TE", "TM")):
    a_ = ax[0, 1]
    for k, r in enumerate(rs):
        xs = [D for D in Ds if (r, D) in E1 and E1[(r, D)][f"c_{pol}_0"] is not None]
        a_.plot(xs, [E1[(r, D)][f"c_{pol}_0"] for D in xs], ("o-" if pol == "TE" else "s--"), color=f"C{k}", label=f"{pol} r/a {r:.2f}")
a_.axhspan(-0.05, 0.05, color="0.9"); a_.axhline(0, color="k", lw=0.5); a_.set_xlabel("Δ"); a_.set_ylabel("c (az 0)")
a_.set_title("E1 curvature vs Δ (TE solid, TM dashed)"); a_.legend(fontsize=6, ncol=2)
a_ = ax[1, 0]
for k_, v in e1tab.items():
    for p in v["partners_3deg"]:
        colr = dict(TE="C3", TM="C0", both="0.4")[p["acts_on"]]
        a_.scatter(v["rbar"] + 0.003 * v["D"] / 0.05, p["dlam"], s=12 + 10 * np.log10(p["Q3"]), color=colr, edgecolor="k", lw=0.3)
a_.axhline(0, color="k", lw=0.5); a_.set_xlabel("mean r/a (+ offset ∝ Δ)"); a_.set_ylabel("λ(3°) − λ_E1 (nm)")
a_.set_title("3° partners near E1: red TE only, blue TM only, grey both; size ∝ log Q")
a_ = ax[1, 1]
X = [x for x in rows if x["max_abs_c"] is not None]
sc = a_.scatter([x["rbar"] + 0.003 * x["D"] / 0.05 for x in X], [x["lam"] for x in X], c=[x["max_abs_c"] for x in X], cmap="viridis_r", vmin=0, vmax=0.6, s=20)
plt.colorbar(sc, ax=a_, label="max |c|"); a_.set_xlabel("mean r/a (+ offset ∝ Δ)"); a_.set_ylabel("λ (nm)"); a_.set_title("all bright doublets: max |c| (TE, TM, az 0, 30)")
fig.tight_layout(); fig.savefig(os.path.join(R, "analysis.png"), dpi=110)

print("E1 candidates at Delta 0 (cost, lam, Q, c_TE_0, c_TM_0):")
for r, c in cand_log.items(): print(f"  r/a {r:.2f}: {c}")
for (r, D), E in sorted(E1.items()):
    v = e1tab[f"r{r:.2f}_D{D:+.2f}"]
    f = lambda z: "nan" if z is None else f"{z:+.2f}"
    print(f"r/a {r:.2f} D {D:+.2f}: E1 {E['lam']:.1f} Q {E['Q']:.0f} c_TE {f(E['c_TE_0'])}/{f(E['c_TE_30'])} c_TM {f(E['c_TM_0'])}/{f(E['c_TM_30'])}; partners: "
          + "; ".join(f"{p['dlam']:+.1f}nm Q{p['Q3']:.0f} {p['acts_on']}" for p in v["partners_3deg"]))
print("stop rule dc_TE:", stop)
print(f"target met: {len(summ['meets_target'])}; within 0.15: {len(summ['within_0p15'])}")
for x in summ["best10"][:5]:
    print(f"  r {x['rbar']:.2f} D {x['D']:+.2f} lam {x['lam']:.1f} Q {x['Q']:.0f} c_TE {x['c_TE_0']:+.3f}/{x['c_TE_30']:+.3f} c_TM {x['c_TM_0']:+.3f}/{x['c_TM_30']:+.3f} worst|M| {x['worst_absM']:.2f}")
