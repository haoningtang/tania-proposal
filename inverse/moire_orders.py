"""T15b: power per diffraction order of the twisted square prelim bilayer (rcwa4d-mf), normal incidence.
Orders: zero; the four first-order moire orders (|k_par|/k0 = 2 (lam/a) sin(twist/2), i.e. +-(g1x - g2x), +-(g1y - g2y)); the rest.
Inputs x, y and sigma+- = (x +- i y)/sqrt(2) (see twist.py for the naming; sigma+ is LCP in the exp(+iwt), IEEE convention).
Per order: transmitted and reflected power fraction, polar angle and azimuth of the order.
Mode spec: order spectra on 1480-1580 nm (2 nm) at N = 5, all twists; resonance = largest-weight AAA pole of T_x in 1495-1525 nm.
Mode points: lam_res and lam_res +- 10 nm for N = 3, 4, 5."""
import argparse, json, math, os, time
import numpy as np, torch, rcwa4d_mf
from rcwa4d_mf import structured as st
from twist import PAT, A_NM, DEV, poles_w

def solve(N, twist, lams, gap_nm=200.0):
    model = rcwa4d_mf.bilayer(PAT, d=220 / A_NM, gap=gap_nm / A_NM, twist_deg=twist, N=N)
    nm = model.nm; orders = model.orders
    out = []
    for lam in lams:
        f = torch.tensor([A_NM / lam], dtype=torch.float64, device=DEV); z = torch.zeros_like(f)
        with torch.no_grad():
            x, y = rcwa4d_mf.solve_lab_basis(model, f, ux=z, uy=z)
            k0 = 2 * torch.pi * f / model.a
            ex, ey, _, _ = st._k_expanded_vectors(model, z, z, k0, model.twist)
        ex = ex[0].real.cpu().numpy(); ey = ey[0].real.cpu().numpy(); kp = np.hypot(ex, ey)
        kzt = x.kz_transmission[0].real.cpu().numpy(); kzr = x.kz_reflection[0].real.cpu().numpy()
        c0 = len(kp) // 2
        target = 2 * (lam / A_NM) * math.sin(math.radians(abs(twist)) / 2)
        moire = [int(i) for i in np.where((np.abs(kp - target) < 1e-6 * max(target, 1e-9)) & (kzt > 0))[0]]
        lab = lambda i: (orders[i // nm], orders[i % nm])
        E = dict(x=(x.transmitted_e[0].cpu().numpy(), x.reflected_e[0].cpu().numpy()),
                 y=(y.transmitted_e[0].cpu().numpy(), y.reflected_e[0].cpu().numpy()))
        E["sp"] = tuple((E["x"][k] + 1j * E["y"][k]) / math.sqrt(2) for k in (0, 1))
        E["sm"] = tuple((E["x"][k] - 1j * E["y"][k]) / math.sqrt(2) for k in (0, 1))
        rec = dict(lam=lam, twist=twist, N=N, sin_formula=target, moire=[dict(index=i, label=lab(i), sin_theta=float(kp[i]),
                   theta_deg=float(np.degrees(np.arcsin(min(kp[i], 1)))), azimuth_deg=float(np.degrees(np.arctan2(ey[i], ex[i])))) for i in moire],
                   n_propagating=int((kzt > 0).sum()))
        for pol, (te, re) in E.items():
            Pt = kzt * (np.abs(te) ** 2).sum(-1); Pr = kzr * (np.abs(re) ** 2).sum(-1)
            Pt[kzt <= 0] = 0; Pr[kzr <= 0] = 0
            rec[pol] = dict(T=float(Pt.sum()), R=float(Pr.sum()), T0=float(Pt[c0]), R0=float(Pr[c0]),
                            T_moire=[float(Pt[i]) for i in moire], R_moire=[float(Pr[i]) for i in moire],
                            T_rest=float(Pt.sum() - Pt[c0] - Pt[moire].sum()), R_rest=float(Pr.sum() - Pr[c0] - Pr[moire].sum()))
        out.append(rec)
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True)
    ap.add_argument("--mode", choices=["spec", "points"], default="spec")
    ap.add_argument("--twists", type=float, nargs="+", default=[0.5, -0.5, 1, -1, 2, -2, 4, -4, 8, -8])
    ap.add_argument("--N", type=int, nargs="+", default=[5])
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    if a.mode == "spec":
        lams = np.arange(1480, 1580.1, 2.0)
        for tw in a.twists:
            fn = os.path.join(a.out, f"orders_spec_N5_tw{tw:+g}.json")
            if os.path.exists(fn): continue
            t0 = time.time(); r = solve(5, tw, lams); json.dump(r, open(fn, "w"))
            print(f"spec tw {tw:+g}: {time.time()-t0:.0f}s; moire orders {len(r[0]['moire'])}", flush=True)
    else:
        res = json.load(open(os.path.join(a.out, "points.json"))) if os.path.exists(os.path.join(a.out, "points.json")) else {}
        for tw in a.twists:
            sp = json.load(open(os.path.join(a.out, f"orders_spec_N5_tw{tw:+g}.json")))
            l = np.array([r["lam"] for r in sp]); Tx = np.array([r["x"]["T"] for r in sp])
            P = [p for p in poles_w(l, Tx, 1495, 1525)]
            lr = max(P, key=lambda p: p[2])[0] if P else float(l[np.argmin(Tx)])
            for N in a.N:
                key = f"{tw:+g}_N{N}"
                if key in res: continue
                t0 = time.time(); res[key] = dict(lam_res=lr, poles_N5=P, recs=solve(N, tw, [lr - 10, lr, lr + 10]))
                json.dump(res, open(os.path.join(a.out, "points.json"), "w"))
                print(f"points tw {tw:+g} N {N}: lam_res {lr:.2f}, {time.time()-t0:.0f}s", flush=True)
