"""T15 check: aligned bilayer (fmmax, model.py) at normal incidence for lateral shifts (dx, dy) on an n x n grid over the unit cell.
A small-twist bilayer is locally an aligned bilayer whose shift sweeps the whole cell over one moire period L = a / (2 sin(theta/2))
(57 a at 1 deg); if the mode propagation length << L, the plane-wave transmission is the area average over shifts.
Computes the C4v-distinct shifts only (multiplicity recorded); per shift: T_x, T_y (co + cross, zero order is the only open
channel at f = 0.41), and circular T_+- from the zero-order Jones matrix.
Usage: python stack_avg.py --out DIR --n 16 --part k --nparts m"""
import argparse, json, os, time
import numpy as np
from model import bilayer_t

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True); ap.add_argument("--n", type=int, default=16)
ap.add_argument("--part", type=int, default=0); ap.add_argument("--nparts", type=int, default=1)
ap.add_argument("--lo", type=float, default=1480); ap.add_argument("--hi", type=float, default=1580); ap.add_argument("--nl", type=int, default=101)
ap.add_argument("--gap", type=float, default=200.0)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
n = a.n
def orbit(i, j):
    s = set()
    for (p, q) in [(i, j), (j, i)]:
        for sp in (1, -1):
            for sq in (1, -1):
                s.add(((sp * p) % n, (sq * q) % n))
    return s
seen, reps = set(), []
for i in range(n):
    for j in range(n):
        if (i, j) in seen: continue
        o = orbit(i, j); seen |= o; reps.append(((i, j), len(o)))
assert sum(m for _, m in reps) == n * n
mine = reps[a.part::a.nparts]
ll = np.linspace(a.lo, a.hi, a.nl) * 1e-3
res = {}
for (i, j), mult in mine:
    t0 = time.time(); o = {}
    for c in range(0, len(ll), 16):
        r = bilayer_t(ll[c:c + 16], 0.0, 0.62, 0.22, 0.12, a.gap * 1e-3, shift=i / n, shift_y=j / n, n_terms=80, ngrid=96)
        for k in ("t_TM", "t_TE", "t_TM_TE", "t_TE_TM"):
            o.setdefault(k, []).append(np.asarray(r[k]))
    o = {k: np.concatenate(v) for k, v in o.items()}
    txx, tyx, tyy, txy = o["t_TM"], o["t_TM_TE"], o["t_TE"], o["t_TE_TM"]   # t_ab: out a, in b
    Tx = abs(txx) ** 2 + abs(tyx) ** 2; Ty = abs(tyy) ** 2 + abs(txy) ** 2
    def circ(s):
        ex, ey = (txx + s * 1j * txy) / np.sqrt(2), (tyx + s * 1j * tyy) / np.sqrt(2)
        return abs(ex) ** 2 + abs(ey) ** 2
    res[f"{i},{j}"] = dict(mult=mult, Tx=Tx.tolist(), Ty=Ty.tolist(), Tp=circ(1).tolist(), Tm=circ(-1).tolist(),
                           cross_max=float(max(abs(tyx).max(), abs(txy).max())))
    json.dump(dict(lam_nm=(ll * 1e3).tolist(), n=n, gap=a.gap, shifts=res), open(os.path.join(a.out, f"stack_part{a.part}.json"), "w"))
    print(f"shift ({i},{j})/{n} mult {mult}: {time.time()-t0:.0f}s, min Tx {Tx.min():.3f} at {ll[Tx.argmin()]*1e3:.1f}, max|CD| {abs(circ(1)-circ(-1)).max():.1e}", flush=True)
