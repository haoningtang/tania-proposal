"""T19a: complex amplitudes of every propagating (moire) order of the twisted square prelim bilayer, rcwa4d-mf (GPU).

Structure as T15 (twist.py): square a 620, eps 12.11, circular hole r 120, d 220, gap 200 nm, normal incidence.
Rotation centre: rcwa4d-mf positions are relative to the twist axis; the hole of each layer is at (0, 0), so the
aligned (AA, zero-shift) stacking sits at r = 0 of the moire cell. Layer 2 is layer 1 rotated by +twist.
Per lambda and input (x, y; sigma+- built as (x +- i y)/sqrt(2) in the analysis) we save the complex E (x, y, z) of every
transmitted and reflected order with kz > 0, its labels (layer-1 order (p1, q1), layer-2 order (p2, q2)) and its lateral
k-vector in units of k0. Solver convention: exp(+i w t), propagation exp(-i k.r) (see twist.py); the analysis records it.
Output: one npz per twist, tw<+g>_N<N>.npz.
"""
import argparse, math, os, time
import numpy as np, torch, rcwa4d_mf
from rcwa4d_mf import structured as st
from twist import PAT, A_NM, DEV


def solve(N, twist, lams, gap_nm=200.0, batch=1):
    model = rcwa4d_mf.bilayer(PAT, d=220 / A_NM, gap=gap_nm / A_NM, twist_deg=twist, N=N)
    nm = model.nm; orders = model.orders
    keep = None; rows = []
    for lam in lams:
        f = torch.tensor([A_NM / lam], dtype=torch.float64, device=DEV); z = torch.zeros_like(f)
        with torch.no_grad():
            x, y = rcwa4d_mf.solve_lab_basis(model, f, ux=z, uy=z)
            k0 = 2 * torch.pi * f / model.a
            ex, ey, _, _ = st._k_expanded_vectors(model, z, z, k0, model.twist)
        ex = ex[0].real.cpu().numpy(); ey = ey[0].real.cpu().numpy()
        kzt = x.kz_transmission[0].real.cpu().numpy(); kzr = x.kz_reflection[0].real.cpu().numpy()
        prop = np.where(kzt > 0)[0]
        if keep is None:
            keep = prop
        elif not np.array_equal(prop, keep):
            keep = np.union1d(keep, prop)  # rare: a new order opens; stored set is the union (recomputed below)
        rows.append(dict(lam=lam, kx=ex, ky=ey, kzt=kzt, kzr=kzr,
                         tx=x.transmitted_e[0].cpu().numpy(), ty=y.transmitted_e[0].cpu().numpy(),
                         rx=x.reflected_e[0].cpu().numpy(), ry=y.reflected_e[0].cpu().numpy(),
                         Tx=float(x.transmission[0]), Ty=float(y.transmission[0]),
                         Rx=float(x.reflection[0]), Ry=float(y.reflection[0])))
    keep = np.asarray(keep)
    lab = np.array([(*orders[i // nm], *orders[i % nm]) for i in keep], dtype=np.int16)
    S = lambda k: np.stack([r[k][keep] for r in rows])
    return dict(lam=np.array(lams), labels=lab, index=keep, kx=S("kx"), ky=S("ky"), kzt=S("kzt"), kzr=S("kzr"),
                tx=S("tx").astype(np.complex128), ty=S("ty").astype(np.complex128),
                rx=S("rx").astype(np.complex128), ry=S("ry").astype(np.complex128),
                Tx=np.array([r["Tx"] for r in rows]), Ty=np.array([r["Ty"] for r in rows]),
                Rx=np.array([r["Rx"] for r in rows]), Ry=np.array([r["Ry"] for r in rows]),
                twist=twist, N=N, gap_nm=gap_nm, a_nm=A_NM, n_orders_total=nm * nm)


def lam_grid():
    coarse = np.arange(1480, 1580.1, 2.0)
    fine = np.arange(1500.5, 1512.51, 0.5)
    return np.unique(np.round(np.concatenate([coarse, fine]), 3))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True)
    ap.add_argument("--twists", type=float, nargs="+", default=[1, -1, 0.5, -0.5, 2])
    ap.add_argument("--N", type=int, default=6)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    lams = lam_grid()
    for tw in a.twists:
        fn = os.path.join(a.out, f"tw{tw:+g}_N{a.N}.npz")
        if os.path.exists(fn): continue
        t0 = time.time(); r = solve(a.N, tw, lams)
        np.savez_compressed(fn, **r)
        err = np.max(np.abs(r["Tx"] + r["Rx"] - 1))
        print(f"tw {tw:+g} N {a.N}: {len(lams)} lam, {len(r['index'])} prop orders, {time.time()-t0:.0f}s, "
              f"min Tx {r['Tx'].min():.3f} at {r['lam'][np.argmin(r['Tx'])]:.1f}, |R+T-1| {err:.1e}, "
              f"{os.path.getsize(fn)/1e6:.2f} MB", flush=True)
