"""T15c: N convergence of the T15b moire-order efficiencies (rcwa4d-mf, GPU). Same structure and solve() as moire_orders.py.
For each twist (1, 2, 4, 8 deg) and two target wavelengths from the T15b N 5 data
  lam_res  = largest-weight AAA pole of T_x (points.json, N 5),
  lam_pk   = lam of the largest single-order T_x in the N 5 order spectrum (4 deg: also the near-tied 1552 nm),
solve N = 3..7 on lam_target + [-4..4] nm (1 nm), so that a line that moves with N is seen.
Records time and peak GPU memory per solve. Output: conv.json (all records, compact)."""
import argparse, json, os, time
import numpy as np, torch
from moire_orders import solve

T15B = os.path.join(os.path.dirname(__file__), "..", "runs", "20261122-0700_T15b_moire_orders")


def targets():
    P = json.load(open(os.path.join(T15B, "points.json")))
    out = []
    for tw in [1, 2, 4, 8]:
        sp = json.load(open(os.path.join(T15B, f"orders_spec_N5_tw+{tw}.json")))
        l = np.array([r["lam"] for r in sp]); m = np.array([max(r["x"]["T_moire"]) for r in sp])
        out.append((tw, "res", float(P[f"+{tw}_N5"]["lam_res"])))
        out.append((tw, "pk", float(l[np.argmax(m)])))
        if tw == 4: out.append((tw, "pk2", 1552.0))
    return out


def compact(r):
    c = dict(lam=r["lam"], n_prop=r["n_propagating"], moire_theta=[m["theta_deg"] for m in r["moire"]])
    for pol in ("x", "sp", "sm"):
        p = r[pol]; c[pol] = {k: p[k] for k in ("T", "R", "T0", "R0", "T_moire", "R_moire", "T_rest", "R_rest")}
    return c


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True)
    ap.add_argument("--N", type=int, nargs="+", default=[3, 4, 5, 6, 7])
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    fn = os.path.join(a.out, "conv.json")
    res = json.load(open(fn)) if os.path.exists(fn) else {}
    for N in a.N:
        for tw, kind, lt in targets():
            key = f"{tw}_{kind}_N{N}"
            if key in res: continue
            lams = list(lt + np.arange(-4, 4.1, 1.0))
            torch.cuda.reset_peak_memory_stats(); t0 = time.time()
            try:
                recs = solve(N, float(tw), lams)
            except torch.cuda.OutOfMemoryError as e:
                res[key] = dict(error="OOM", N=N); json.dump(res, open(fn, "w")); print(key, "OOM", flush=True)
                torch.cuda.empty_cache(); continue
            torch.cuda.synchronize(); dt = time.time() - t0
            res[key] = dict(twist=tw, kind=kind, lam_target=lt, N=N, sec_per_solve=dt / len(lams),
                            peak_mem_GiB=torch.cuda.max_memory_allocated() / 2 ** 30, recs=[compact(r) for r in recs])
            json.dump(res, open(fn, "w"))
            i0 = 4; x = res[key]["recs"][i0]["x"]
            print(f"{key}: lam {lt:.2f} Tmax {max(x['T_moire']):.4f} T0 {x['T0']:.3f} | {dt/len(lams):.1f}s/solve "
                  f"{res[key]['peak_mem_GiB']:.2f}GiB", flush=True)
