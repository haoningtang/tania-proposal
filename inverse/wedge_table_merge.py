"""T18a merge: chains/*.json -> table.json (records), table.csv (fits), with flags recomputed after the fact:
flag_jump_post = at fixed (structure, g0, theta, pol), lam0(g) deviates from the quadratic fit in g by > 0.5 Gamma,
or Q(g) / neighbour mean outside 0.7 .. 1.4. Duplicate g0 records (computed in both chains) are kept once (up chain).
Hires records (chains/*_200.json, 200/192) are kept in a separate list 'hires'."""
import glob, json, os, sys
import numpy as np
D = sys.argv[1]
recs, hires = {}, []
for f in sorted(glob.glob(os.path.join(D, "chains/chain_*.json")), key=lambda s: ("down" in s, s)):
    for r in json.load(open(f)):
        if r["n_terms"] != 80: hires.append(r); continue
        k = (r["structure"], r["g0"], r["g"], r["theta"], r["pol"])
        recs.setdefault(k, r)
groups = {}
for k, r in recs.items(): groups.setdefault((k[0], k[1], k[3], k[4]), []).append(r)
for key, rs in groups.items():
    rs.sort(key=lambda r: r["g"]); g = np.array([r["g"] for r in rs], float)
    l = np.array([r["fit"]["lam0_nm"] for r in rs]); Q = np.array([r["fit"]["Q"] for r in rs]); G = l / Q
    c = np.polyfit(g, l, 2); dev = np.abs(l - np.polyval(c, g)) / G
    for i, r in enumerate(rs):
        nb = [Q[j] for j in (i - 1, i + 1) if 0 <= j < len(rs)]
        qr = Q[i] / np.mean(nb)
        r["fit"]["flag_jump_post"] = bool(dev[i] > 0.5 or not (0.7 < qr < 1.4))
        r["fit"]["dlam_dg_nm_per_nm"] = float(2 * c[0] * g[i] + c[1])
        r["fit"]["flag_jump_chain"] = r["fit"].pop("flag_jump", False)
out = sorted(recs.values(), key=lambda r: (r["structure"], r["g0"], r["pol"], r["theta"], r["g"]))
meta = dict(note="T18a: complex zero-order t (out = in polarization) of aligned bilayers, azimuth 0, fmmax 80/96 via model.py. "
            "TE = E perpendicular to the plane of incidence. lam grid: lam0 +- 4 Gamma at Gamma/20 (union over TE/TM at that (g, theta)) "
            "plus +-10 nm margin at 0.25 nm. fit: AAA pole of t on the fine part. structures: T9b = runs/20261121-0556_T9b_gaps260/best.json; "
            "prelim = a 620, t 220, r 120 nm. hires: same records at 200/192 for g = g0.", n_records=len(out))
fn = os.path.join(D, "table.json")
json.dump(dict(meta=meta, records=out, hires=hires), open(fn, "w"), separators=(",", ":"))
print("table.json", os.path.getsize(fn) / 1e6, "MB;", len(out), "records;", len(hires), "hires")
keys = ["structure", "g0", "g", "theta", "pol", "lam0_nm", "Q", "Gamma_nm", "T_min", "T_max", "dlam_dg_nm_per_nm", "flag_jump_post", "n_lam"]
with open(os.path.join(D, "table.csv"), "w") as f:
    f.write(",".join(keys) + ",n_terms\n")
    for r in out + hires:
        row = [r["structure"], r["g0"], r["g"], r["theta"], r["pol"]] + [r["fit"].get(k, "") for k in keys[5:12]] + [len(r["lam_nm"]), r["n_terms"]]
        f.write(",".join(f"{v:.7g}" if isinstance(v, float) else str(v) for v in row) + "\n")
print("flagged:", [(r["structure"], r["g0"], r["g"], r["theta"], r["pol"]) for r in out if r["fit"]["flag_jump_post"]])
