"""T19b: LPA reference. Aligned square prelim bilayer (fmmax, model.py; a 620, t 220, r 120, gap 200 nm) with a uniform
lateral shift delta = (i, j) a / n of slab 2, normal incidence, the T19a wavelength grid. Saves the complex zero-order
2x2 Jones transmission J[out, in] (part*.npz: model.py blocks (block 0, block 1) = (-E_y, E_x), i.e. keys (TE, TM) since T20, (TM, TE) before; lpa_jones.npz: physical
x, y after conversion), for the C4v-distinct shifts only; the others
follow from J(g delta) = M_g J(delta) M_g^T (g in C4v acting on the shift, M_g its 2x2 matrix; the holes are C4v about
their centres, so applying g to the whole structure only maps the shift).
fmmax convention is exp(-i w t) (rcwa4d-mf: exp(+i w t)); compare powers, not phases, with T19a.
Usage: python lpa_shift_map.py --out DIR --n 16 --part k --nparts m ; merge with --merge."""
import argparse, glob, os, sys, time
import numpy as np



def lam_grid():  # same as twist_maps.lam_grid (T19a); duplicated so that this script needs no torch
    return np.unique(np.round(np.concatenate([np.arange(1480, 1580.1, 2.0), np.arange(1500.5, 1512.51, 0.5)]), 3))


def reps_c4v(n):
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
    return reps


def expand(J, n):
    """J: dict (i,j) -> [L,2,2] for reps -> full [n,n,L,2,2] via C4v."""
    full = {}
    for (i, j), Jr in J.items():
        for swap in (False, True):
            for sp in (1, -1):
                for sq in (1, -1):
                    # g: delta -> (sp*p, sq*q) after optional swap. Matrix on (x, y) vectors:
                    M = np.array([[0, 1], [1, 0]]) if swap else np.eye(2)
                    M = np.diag([sp, sq]) @ M
                    p, q = (j, i) if swap else (i, j)
                    key = ((sp * p) % n, (sq * q) % n)
                    if key not in full:
                        full[key] = np.einsum("ab,lbc,dc->lad", M, Jr, M)
    out = np.zeros((n, n) + next(iter(J.values())).shape, complex)
    for (i, j), v in full.items(): out[i, j] = v
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True); ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--part", type=int, default=0); ap.add_argument("--nparts", type=int, default=1)
    ap.add_argument("--n_terms", type=int, default=80); ap.add_argument("--ngrid", type=int, default=96)
    ap.add_argument("--merge", action="store_true")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    n = a.n; lams = lam_grid()
    if a.merge:
        J = {}
        for f in sorted(glob.glob(os.path.join(a.out, "part*.npz"))):
            d = np.load(f)
            for k in d.files:
                if k.startswith("J_"):
                    i, j = map(int, k[2:].split("_"))
                    # model.py amplitude blocks are (block0, block1) = (-E_y, E_x) (fmmax field order (-ey, ex, ...);
                    # see check_pol_labels.py). Convert to the physical (x, y) basis BEFORE the C4v expansion:
                    # e_xy = P e_block, P = [[0, 1], [-1, 0]]; J_xy = P J_block P^T.
                    P = np.array([[0, 1], [-1, 0]])
                    J[(i, j)] = np.einsum("ab,lbc,dc->lad", P, d[k], P)
        assert len(J) == len(reps_c4v(n)), (len(J), len(reps_c4v(n)))
        full = expand(J, n)
        np.savez_compressed(os.path.join(a.out, "lpa_jones.npz"), lam=lams, J=full, n=n, a_nm=620.0, gap_nm=200.0,
                            n_terms=a.n_terms, ngrid=a.ngrid,
                            note="J[i,j,l,out,in], shift (i,j)*a/n of slab 2 (along x, y), physical x/y basis (converted from the model.py blocks), fmmax exp(-iwt)")
        print("merged", full.shape); sys.exit()
    from model import bilayer_t
    mine = reps_c4v(n)[a.part::a.nparts]
    fn = os.path.join(a.out, f"part{a.part}.npz")
    res = dict(np.load(fn)) if os.path.exists(fn) else {}
    ll = lams * 1e-3
    for (i, j), mult in mine:
        if f"J_{i}_{j}" in res: continue
        t0 = time.time(); o = {}
        for c in range(0, len(ll), 16):
            r = bilayer_t(ll[c:c + 16], 0.0, 0.62, 0.22, 0.12, 0.2, shift=i / n, shift_y=j / n, n_terms=a.n_terms, ngrid=a.ngrid)
            for k in ("t_TM", "t_TE", "t_TM_TE", "t_TE_TM"):
                o.setdefault(k, []).append(np.asarray(r[k]))
        o = {k: np.concatenate(v) for k, v in o.items()}
        # J in model.py amplitude blocks (block 0, block 1) = (-E_y, E_x). Since T20 (2026-11-23) key TE = block 0 and
        # key TM = block 1 at azimuth 0 (before: key TM = block 0); t_TE_TM = block 1 out for block 0 in. Same J as before.
        J = np.empty((len(ll), 2, 2), complex)
        J[:, 0, 0] = o["t_TE"]; J[:, 1, 0] = o["t_TE_TM"]; J[:, 1, 1] = o["t_TM"]; J[:, 0, 1] = o["t_TM_TE"]
        res[f"J_{i}_{j}"] = J
        np.savez_compressed(fn, **res)
        Tp = 0.5 * np.sum(np.abs(J @ np.array([1, 1j])) ** 2, -1); Tm = 0.5 * np.sum(np.abs(J @ np.array([1, -1j])) ** 2, -1)
        Tx = np.sum(np.abs(J[:, :, 0]) ** 2, -1)
        print(f"shift ({i},{j})/{n} mult {mult}: {time.time()-t0:.0f}s, min Tx {Tx.min():.3f} at {lams[Tx.argmin()]:.1f}, "
              f"max|CD| {np.abs(Tp - Tm).max():.1e}", flush=True)
