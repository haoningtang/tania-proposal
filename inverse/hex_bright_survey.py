"""T12a bright-doublet survey on the hexagonal lattice.

For each (a, r/a, t) in cfg["survey"] (t2 = t, r2 = r, c4 = c8 = 0) and each gap in cfg["survey"]["gaps"]: scan lam_range at
theta (deg, azimuth 0), find TE and TM poles (AAA in overlapping windows, no Q cap), refine the narrow ones (Q >= 150) with a
fine scan, keep Q >= qmin, and list TE/TM-degenerate pairs (|lam_TE - lam_TM| <= pair_tol) per gap. Then match each gap-380
pair to the nearest pair at the other gaps (|dlam| <= match_tol, Q within a factor 10) and report the tuning
(lam(gap_min) - lam(gap_max)) / mean of the same line. Ambiguous matches (> 1 pair inside match_tol) are flagged;
the best candidates must be confirmed with --follow (track the line through intermediate gaps).

Usage:
  python hex_bright_survey.py --config configs/stage12a_hex_bright_survey.json --out ../runs/<name> [--qmin 30 --pair_tol 0.0005]
  python hex_bright_survey.py --config ... --out ../runs/<name> --follow a r_over_a t lam380 [--gap_step 0.02]
Writes survey.json (resumable) and candidates.json (lines sorted by tuning, then Q); --follow writes follow_<...>.json.
"""
import argparse, json, os, itertools, time
import numpy as np
from scipy.interpolate import AAA
from analyze import scan

ap = argparse.ArgumentParser()
ap.add_argument("--config", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--qmin", type=float, default=30); ap.add_argument("--pair_tol", type=float, default=0.0005)
ap.add_argument("--match_tol", type=float, default=0.08)
ap.add_argument("--win", type=float, default=0.07, help="AAA window width (um); windows overlap by half")
ap.add_argument("--follow", type=float, nargs=4, default=None, metavar=("A", "R_OVER_A", "T", "LAM380"))
ap.add_argument("--gap_step", type=float, default=0.02)
a = ap.parse_args()
cfg = json.load(open(a.config)); sv = cfg["survey"]
kw = dict(n_terms=cfg.get("n_terms", 80), ngrid=cfg.get("ngrid", 96), lattice=cfg.get("lattice", "hex"))
lo, hi = sv["lam_range"]; lams = np.arange(lo, hi + 1e-12, sv["lam_step"]); th = sv["theta"]; gaps = sv["gaps"]
os.makedirs(os.path.join(a.out, "spectra"), exist_ok=True)


def poles_nocap(ll, t, lo, hi, max_terms=12):
    A = AAA(1 / np.asarray(ll), np.asarray(t), rtol=1e-6, max_terms=max_terms)
    out = []
    for p, rz in zip(A.poles(), A.residues()):
        if p.real <= 0 or p.imag == 0:
            continue
        l0 = 1 / p.real; Q = p.real / (2 * abs(p.imag))
        if lo < l0 < hi and 10 < Q < 1e8 and abs(rz) / abs(p.imag) > 0.05:
            out.append((float(l0), float(Q)))
    return out


def poles_windowed(ll, t):
    """AAA in windows of width win, step win/2; keep each pole only from the window whose central half contains it"""
    out = []
    w = a.win; s = w / 2
    starts = np.arange(ll[0], ll[-1] - w + s + 1e-9, s)
    for k, x0 in enumerate(starts):
        x1 = min(x0 + w, ll[-1]); m = (ll >= x0 - 1e-9) & (ll <= x1 + 1e-9)
        c0 = ll[0] if k == 0 else x0 + w / 4
        c1 = ll[-1] if k == len(starts) - 1 else x0 + 3 * w / 4
        for l0, Q in poles_nocap(ll[m], t[m], x0, x1):
            if c0 <= l0 < c1:
                out.append((l0, Q))
    out.sort()
    ded = []
    for l0, Q in out:   # drop near-duplicates (same pole seen twice at a window edge)
        if ded and abs(l0 - ded[-1][0]) < 0.1 * l0 / max(Q, ded[-1][1]):
            continue
        ded.append((l0, Q))
    return ded


def refine_joint(p, st, cands):
    """cands: list of (l0, Q, pol). Merge their fine windows (+-3 linewidths, 0.5 nm .. 20 nm) and scan each merged
    window once (one scan gives TE and TM); return refined [lam, Q] per pol."""
    W = sorted((l0 - min(max(3 * l0 / Q, 0.0005), 0.02), l0 + min(max(3 * l0 / Q, 0.0005), 0.02), l0, pol)
               for l0, Q, pol in cands)
    groups = []
    for w in W:
        if groups and w[0] <= groups[-1]["hi"]:
            groups[-1]["hi"] = max(groups[-1]["hi"], w[1]); groups[-1]["m"].append(w)
        else:
            groups.append(dict(lo=w[0], hi=w[1], m=[w]))
    out = {"TE": [], "TM": []}
    for G in groups:
        n = int(min(81, max(25, 25 * (G["hi"] - G["lo"]) / (2 * min(w[1] - w[2] for w in G["m"])))))
        ll = np.linspace(G["lo"], G["hi"], n)
        t = scan(p, st, ll, th, kw)
        for pol in ("TE", "TM"):
            P = poles_nocap(ll, t[pol], ll[0], ll[-1])
            for _, _, l0, q in G["m"]:
                if q == pol and P:
                    b = min(P, key=lambda x: abs(x[0] - l0))
                    if abs(b[0] - l0) < 0.01:
                        out[pol].append([float(b[0]), float(b[1])])
    return out


def survey_gap(p, g, spec):
    st = dict(gap=g, shift=0.0)
    t = scan(p, st, lams, th, kw)
    spec[str(g)] = np.stack([np.abs(t["TE"]) ** 2, np.abs(t["TM"]) ** 2]).astype(np.float32)
    rec = dict(poles={}, pairs=[])
    coarse, fine = {}, []
    for pol in ("TE", "TM"):
        P = [x for x in poles_windowed(lams, t[pol]) if x[1] >= 0.5 * a.qmin]
        coarse[pol] = [list(x) for x in P if x[1] < 150]
        fine += [(l0, Q, pol) for l0, Q in P if Q >= 150]
    R = refine_joint(p, st, fine) if fine else {"TE": [], "TM": []}
    for pol in ("TE", "TM"):
        rec["poles"][pol] = sorted(r for r in coarse[pol] + R[pol] if r[1] >= a.qmin)
    print(f"   gap {g}: TE {len(rec['poles']['TE'])}, TM {len(rec['poles']['TM'])} poles ({len(fine)} refined)", flush=True)
    for lte, qte in rec["poles"]["TE"]:
        for ltm, qtm in rec["poles"]["TM"]:
            if abs(lte - ltm) <= a.pair_tol:
                rec["pairs"].append(dict(lam=0.5 * (lte + ltm), dlam=lte - ltm, Q_TE=qte, Q_TM=qtm))
    return rec


def params(A, ra, T):
    return dict(a=A, t=T, r=ra * A, r2=ra * A, t2=T, c4=0.0, c8=0.0)


if a.follow:
    # follow one TE/TM line from gap 0.38 down to min(gaps) and up to max(gaps) in steps of gap_step
    A, ra, T, l380 = a.follow
    p = params(A, ra, T)
    res = dict(p=dict(a=A, r_over_a=ra, t=T), settings=dict(kw, theta=th, gap_step=a.gap_step), TE=[], TM=[])
    for pol in ("TE", "TM"):
        pts = {}
        for direction in (-1, 1):
            l, Q = l380, None
            g_end = min(gaps) if direction < 0 else max(gaps)
            gg = np.round(np.arange(0.38, g_end + direction * 1e-9, direction * a.gap_step), 4)
            for g in gg:
                if direction > 0 and g == 0.38:
                    continue
                w = 0.012 if Q is None else min(max(4 * l / Q, 0.002), 0.03)
                ll = np.linspace(l - w, l + w, 41)
                P = poles_nocap(ll, scan(p, dict(gap=float(g), shift=0.0), ll, th, kw)[pol], ll[0], ll[-1])
                P = [x for x in P if x[1] >= 0.5 * a.qmin]
                if not P:
                    print(f"{pol}: lost at gap {g}", flush=True); break
                l, Q = min(P, key=lambda x: abs(x[0] - l))
                pts[float(g)] = (l, Q)
                print(f"{pol} gap {g:.3f}: {l*1e3:.2f} nm Q {Q:.0f}", flush=True)
        res[pol] = sorted([g, *v] for g, v in pts.items())
    for pol in ("TE", "TM"):
        d = {g: l for g, l, _ in res[pol]}
        if min(gaps) in d and max(gaps) in d:
            l1, l2 = d[min(gaps)], d[max(gaps)]
            res[pol + "_tuning"] = (l1 - l2) / (0.5 * (l1 + l2))
    fn = os.path.join(a.out, f"follow_a{A*1e3:.0f}_ra{ra:.2f}_t{T*1e3:.0f}_l{l380*1e3:.0f}.json")
    json.dump(res, open(fn, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k.endswith("tuning")}))
    raise SystemExit

fn = os.path.join(a.out, "survey.json")
done = json.load(open(fn)) if os.path.exists(fn) else dict(
    settings=dict(kw, gaps=gaps, lam_range=sv["lam_range"], lam_step=sv["lam_step"], theta=th, qmin=a.qmin,
                  pair_tol=a.pair_tol, win=a.win), designs=[])
have = {(d["p"]["a"], d["p"]["r_over_a"], d["p"]["t"]) for d in done["designs"]}

for A, ra, T in itertools.product(sorted(sv["a"], reverse=True), sv["r_over_a"], sv["t"]):
    if (A, ra, T) in have:
        continue
    t0 = time.time(); p = params(A, ra, T)
    rec = dict(p=dict(a=A, r_over_a=ra, t=T, r=ra * A), gaps={}); spec = {}
    for g in gaps:
        rec["gaps"][str(g)] = survey_gap(p, g, spec)
    np.savez_compressed(os.path.join(a.out, "spectra", f"a{A*1e3:.0f}_ra{ra:.2f}_t{T*1e3:.0f}.npz"), lams=lams,
                        **{"gap" + k: v for k, v in spec.items()})
    rec["wall_s"] = round(time.time() - t0, 1)
    done["designs"].append(rec)
    json.dump(done, open(fn, "w"), indent=1)
    print(json.dumps(dict(a=A, r_over_a=ra, t=T, s=rec["wall_s"],
                          pairs={g: [(round(x["lam"] * 1e3, 1), round(min(x["Q_TE"], x["Q_TM"])))
                                     for x in r["pairs"]] for g, r in rec["gaps"].items()})), flush=True)

# match lines across gaps (reference gap: the middle one)
gref = str(sorted(gaps)[len(gaps) // 2]); g1, g2 = str(min(gaps)), str(max(gaps))
lines = []
for d in done["designs"]:
    G = d["gaps"]
    for x in G[gref]["pairs"]:
        q = min(x["Q_TE"], x["Q_TM"]); row = dict(d["p"], lam=x["lam"], Q=q, Q_TE=x["Q_TE"], Q_TM=x["Q_TM"], dlam=x["dlam"], chain={gref: [x["lam"], q]}, ambiguous=False)
        for g in (g1, g2):
            near = [y for y in G[g]["pairs"] if abs(y["lam"] - x["lam"]) <= a.match_tol
                    and 0.1 <= min(y["Q_TE"], y["Q_TM"]) / q <= 10]
            if len(near) > 1:
                row["ambiguous"] = True
            if near:
                # cost: wavelength distance (in units of 3 %) + Q mismatch (in units of a factor 3)
                y = min(near, key=lambda y: abs(y["lam"] - x["lam"]) / (0.03 * x["lam"])
                        + abs(np.log(min(y["Q_TE"], y["Q_TM"]) / q)) / np.log(3))
                row["chain"][g] = [y["lam"], min(y["Q_TE"], y["Q_TM"])]
        if g1 in row["chain"] and g2 in row["chain"]:
            l1, l2 = row["chain"][g1][0], row["chain"][g2][0]
            row["tuning"] = (l1 - l2) / (0.5 * (l1 + l2))
        lines.append(row)
lines.sort(key=lambda r: (-(abs(r.get("tuning", 0)) >= 0.02), -r["Q"]))
json.dump(lines, open(os.path.join(a.out, "candidates.json"), "w"), indent=1)
print(f"{len(lines)} degenerate lines at gap {gref}; {sum('tuning' in r for r in lines)} matched at all gaps; "
      f"{sum(abs(r.get('tuning', 0)) >= 0.02 for r in lines)} with |tuning| >= 2 %")
for r in lines[:20]:
    ch = " / ".join(f"{r['chain'][g][0]*1e3:.1f}" if g in r["chain"] else "-" for g in (g1, gref, g2))
    print(f"  a {r['a']*1e3:.0f} r/a {r['r_over_a']:.2f} t {r['t']*1e3:.0f}: lam {ch} nm  Q {r['Q']:.0f}  "
          f"tune {100*r.get('tuning', float('nan')):+.2f} %{'  (ambiguous)' if r['ambiguous'] else ''}")
