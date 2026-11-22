"""T18a: table of the complex zero-order transmission t(lam; g, theta) around the tracked resonance (fmmax, model.py via analyze.scan),
aligned structures, azimuth 0, for the controller's wedge-gap average (T18b).

Chain mode: one structure, g0, direction (up: g0, g0+5, ... g0+30; down: g0-5 ... g0-30). At each gap the resonance is tracked
in theta (0.5, 2, 4, 6, 8 deg) from the previous theta; the theta = 0.5 point is tracked from the previous gap (linear extrapolation
in g). Locate: AAA poles of the complex t on a 61-point window; accepted pole minimizes |dlam|/Gamma_prev + |ln(Q/Q_prev)|;
a jump (|dlam - predicted| > 1.5 Gamma or Q ratio outside 1/2..2) is flagged ("flag" field). Stored grid: lam0 +- 4 Gamma at
Gamma/20 (union over the requested polarizations) plus lam0 +- 10 nm at 0.25 nm (outside the fine part).
Symmetry mode (item 5): prelim structure, gap 200, shift (20, 20) nm, theta = +-2, +-4, +-6 deg, lam_res(theta) +- 10 nm at 0.1 nm;
co-pol, cross-pol and total transmitted power for TE and TM input, and their sum.
"""
import argparse, json, os, time
import numpy as np
from scipy.interpolate import AAA
from model import bilayer_t

STRUCT = {
    "T9b": dict(a=0.7275399070410195, t=0.27914173408136206, r=0.241215594779024, c4=0.005179381802178516,
                c8=0.00020238233822538788, r2=0.23963235240275943),
    "prelim": dict(a=0.62, t=0.22, r=0.12),
}
GUESS = {("T9b", 380): 1.5569, ("T9b", 500): 1.5706, ("prelim", 200): 1.5065}   # lam at 0.5 deg (um)
THETAS = [0.5, 2.0, 4.0, 6.0, 8.0]


def tvals(p, gap, ll, th, kw, shift=(0.0, 0.0)):
    out = {k: [] for k in ("TE", "TM", "TE_TM", "TM_TE")}
    for i in range(0, len(ll), 16):
        o = bilayer_t(ll[i:i + 16], th, p["a"], p["t"], p["r"], gap, shift=shift[0] / p["a"], shift_y=shift[1] / p["a"],
                      c4=p.get("c4", 0.0), c8=p.get("c8", 0.0), r2=p.get("r2"), **kw)
        for k in out:
            out[k].append(np.asarray(o["t_" + k]))
    return {k: np.concatenate(v) for k, v in out.items()}


a_wmin = 0.03   # AAA weight cut; lowered to 0.005 on resume of T9b g0 500 up (TE weight 0.024 at g 530, 6 deg)


def poles(ll, t):
    A = AAA(1 / ll, t, rtol=1e-9, max_terms=14)
    out = []
    for z, rz in zip(A.poles(), A.residues()):
        if z.real <= 0 or z.imag == 0: continue
        l0 = 1 / z.real; Q = z.real / (2 * abs(z.imag)); w = abs(rz) / abs(z.imag)
        if ll[0] < l0 < ll[-1] and 20 < Q < 1e6 and w > a_wmin: out.append((float(l0), float(Q), float(w)))
    return out


def locate(p, gap, th, kw, pols, prev, pred):
    """prev: {pol: (lam, Q)} reference for selection; pred: {pol: predicted lam}"""
    res = {}
    for tries in range(4):
        G = max(prev[pol][0] / prev[pol][1] for pol in pols)
        c = np.mean([pred[pol] for pol in pols]); spread = np.ptp([pred[pol] for pol in pols]) if len(pols) > 1 else 0
        hw = (max(4 * G, 0.0006) + spread / 2) * 2 ** tries
        ll = np.linspace(c - hw, c + hw, 61)
        T = tvals(p, gap, ll, th, kw)
        ok = True
        for pol in pols:
            P = poles(ll, T[pol])
            if not P: ok = False; break
            Gp = prev[pol][0] / prev[pol][1]
            b = min(P, key=lambda x: abs(x[0] - pred[pol]) / Gp + abs(np.log(x[1] / prev[pol][1])))
            flag = abs(b[0] - pred[pol]) > 1.5 * Gp or not (0.5 < b[1] / prev[pol][1] < 2)
            res[pol] = dict(lam0=b[0], Q=b[1], w=b[2], flag=bool(flag), n_poles=len(P))
        if ok: return res
    raise RuntimeError(f"no pole at gap {gap} theta {th}")


def record(p, gap, th, kw, pols, fit):
    lo = min(fit[q]["lam0"] - 4 * fit[q]["lam0"] / fit[q]["Q"] for q in pols)
    hi = max(fit[q]["lam0"] + 4 * fit[q]["lam0"] / fit[q]["Q"] for q in pols)
    step = min(fit[q]["lam0"] / fit[q]["Q"] for q in pols) / 20
    fine = np.arange(lo, hi + step / 2, step)
    c = 0.5 * (lo + hi)
    coarse = np.arange(c - 0.010 - (hi - lo) / 2, c + 0.010 + (hi - lo) / 2 + 1e-9, 0.00025)
    coarse = coarse[(coarse < lo) | (coarse > hi)]
    ll = np.sort(np.r_[fine, coarse])
    T = tvals(p, gap, ll, th, kw)
    for q in pols:   # refit on the fine part
        sel = (ll >= lo) & (ll <= hi)
        P = poles(ll[sel], T[q][sel])
        if P:
            b = min(P, key=lambda x: abs(x[0] - fit[q]["lam0"]))
            fit[q].update(lam0=b[0], Q=b[1], w=b[2])
        Tp = np.abs(T[q][sel]) ** 2
        fit[q].update(T_min=float(Tp.min()), T_max=float(Tp.max()), lam_T_min=float(ll[sel][Tp.argmin()] * 1e3))
    return ll, T


def chain(a):
    p = STRUCT[a.struct]; kw = dict(n_terms=a.n_terms, ngrid=a.ngrid); pols = a.pols
    g0 = a.g0; step = 5 if a.dir == "up" else -5
    gaps = [g0 + k * step for k in range(0 if a.dir == "up" else 0, 7)]
    fn = os.path.join(a.out, f"chain_{a.struct}_g{g0}_{a.dir}_{a.n_terms}.json")
    recs = json.load(open(fn)) if os.path.exists(fn) else []
    done = {(r["g"], r["theta"], r["pol"]) for r in recs}
    hist = []   # (g, {pol: (lam, Q)}) at theta 0.5
    lam_g = GUESS[(a.struct, g0)]
    prev = {q: (lam_g, a.q0 or (150.0 if a.struct == "prelim" else 700.0)) for q in pols}
    for gi, g in enumerate(gaps):
        if len(hist) >= 2:
            pred = {q: hist[-1][1][q][0] + (hist[-1][1][q][0] - hist[-2][1][q][0]) for q in pols}
        else:
            pred = {q: (hist[-1][1][q][0] if hist else lam_g) for q in pols}
        prev_th = dict(hist[-1][1]) if hist else dict(prev)
        th_hist = []
        for th in THETAS:
            t0 = time.time()
            if th_hist:
                last = th_hist[-1]
                if len(th_hist) >= 2:   # extrapolate in sin^2
                    s = np.sin(np.radians([th_hist[-2][0], last[0], th])) ** 2
                    pred = {q: last[1][q][0] + (last[1][q][0] - th_hist[-2][1][q][0]) * (s[2] - s[1]) / (s[1] - s[0]) for q in pols}
                else:
                    pred = {q: last[1][q][0] for q in pols}
                prev_th = last[1]
            old = {r["pol"]: r for r in recs if r["g"] == g and r["theta"] == th}
            if all(q in old for q in pols):   # resume: reuse the stored point
                cur = {q: (old[q]["fit"]["lam0_nm"] * 1e-3, old[q]["fit"]["Q"]) for q in pols}
                th_hist.append((th, cur))
                if th == THETAS[0]: hist.append((g, cur))
                continue
            fit = locate(p, g * 1e-3, th, kw, pols, prev_th, pred)
            ll, T = record(p, g * 1e-3, th, kw, pols, fit)
            cur = {q: (fit[q]["lam0"], fit[q]["Q"]) for q in pols}
            th_hist.append((th, cur))
            if th == THETAS[0]: hist.append((g, cur))
            for q in pols:
                if (g, th, q) in done: continue
                recs.append(dict(structure=a.struct, g0=g0, g=g, theta=th, pol=q, n_terms=a.n_terms, ngrid=a.ngrid,
                                 lam_nm=np.round(ll * 1e3, 6).tolist(), t_re=np.round(T[q].real, 7).tolist(), t_im=np.round(T[q].imag, 7).tolist(),
                                 fit=dict(lam0_nm=fit[q]["lam0"] * 1e3, Q=fit[q]["Q"], Gamma_nm=fit[q]["lam0"] * 1e3 / fit[q]["Q"],
                                          T_min=fit[q]["T_min"], T_max=fit[q]["T_max"], lam_T_min_nm=fit[q]["lam_T_min"],
                                          flag_jump=fit[q]["flag"], n_poles_in_window=fit[q]["n_poles"])))
            json.dump(recs, open(fn, "w"))
            print(f"{a.struct} g0 {g0} g {g} th {th}: " + "; ".join(f"{q} {fit[q]['lam0']*1e3:.3f} Q {fit[q]['Q']:.0f}{' JUMP' if fit[q]['flag'] else ''}" for q in pols)
                  + f"  ({len(ll)} pts, {time.time()-t0:.0f}s)", flush=True)
        if a.only_g0: break


def symmetry(a):
    p = STRUCT["prelim"]; kw = dict(n_terms=a.n_terms, ngrid=a.ngrid); out = dict(settings=dict(shift_nm=[20, 20], gap_nm=200, azimuth=0, **kw), cases=[])
    for th in (2.0, 4.0, 6.0):
        # resonance at +theta from a wide scan (TM line, curvature c ~ -0.84 moves it by -0.84 sin^2 theta lam)
        g = 1.5065 * (1 - 0.84 * np.sin(np.radians(th)) ** 2)
        lw = np.linspace(g - 0.03, g + 0.03, 121); T = tvals(p, 0.2, lw, th, kw, shift=(0.02, 0.02))
        P = poles(lw, T["TM"]); lr = min(P, key=lambda x: -x[2])[0] if P else g
        ll = np.round(np.arange(lr - 0.010, lr + 0.010 + 5e-8, 0.0001), 7)
        R = {s: tvals(p, 0.2, ll, s * th, kw, shift=(0.02, 0.02)) for s in (1, -1)}
        case = dict(theta=th, lam_res_nm=lr * 1e3, poles_TM=[list(x) for x in P], lam_nm=(ll * 1e3).tolist())
        for s in (1, -1):
            r = R[s]
            d = dict(TE_co=np.abs(r["TE"]) ** 2, TE_cross=np.abs(r["TE_TM"]) ** 2, TM_co=np.abs(r["TM"]) ** 2, TM_cross=np.abs(r["TM_TE"]) ** 2)
            d["TE_total"] = d["TE_co"] + d["TE_cross"]; d["TM_total"] = d["TM_co"] + d["TM_cross"]; d["sum"] = d["TE_total"] + d["TM_total"]
            case["plus" if s == 1 else "minus"] = {k: v.tolist() for k, v in d.items()}
        ir = int(np.argmin(np.abs(ll - lr)))
        case["max_abs_diff"] = {k: float(np.max(np.abs(np.array(case["plus"][k]) - np.array(case["minus"][k])))) for k in case["plus"]}
        case["diff_at_res"] = {k: float(case["plus"][k][ir] - case["minus"][k][ir]) for k in case["plus"]}
        out["cases"].append(case)
        print(f"theta {th}: lam_res {lr*1e3:.2f}; max|T(+)-T(-)| " + ", ".join(f"{k} {v:.2e}" for k, v in case["max_abs_diff"].items()), flush=True)
        json.dump(out, open(os.path.join(a.out, "symmetry.json"), "w"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True); ap.add_argument("--mode", choices=["chain", "symmetry"], default="chain")
    ap.add_argument("--struct", default="prelim"); ap.add_argument("--g0", type=int, default=200); ap.add_argument("--dir", default="up")
    ap.add_argument("--pols", nargs="+", default=["TM"]); ap.add_argument("--n_terms", type=int, default=80); ap.add_argument("--ngrid", type=int, default=96)
    ap.add_argument("--only_g0", action="store_true")
    ap.add_argument("--wmin", type=float, default=0.03)
    ap.add_argument("--q0", type=float, default=None, help="Q used for the first locate window (lower = wider)")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); a_wmin = a.wmin
    chain(a) if a.mode == "chain" else symmetry(a)
