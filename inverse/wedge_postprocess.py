"""T18b (controller): tilt = local average over a wedge gap. Post-processing of runs/<..>_T18a_wedge_table/table.json, no field solves.

Model (PI, 2026-11-22): aperture D, tilt alpha; local gap g(x) = g0 + alpha*x, x uniform in [-D/2, D/2]; incidence angle theta - alpha/2;
P(lam, theta; alpha) = < T(lam, theta - alpha/2; g(x)) >_x.
T(lam; g, theta) between table points: shift-aligned interpolation. Each table spectrum is moved so that its pole lam0 sits at the
interpolated lam0, then the two neighbours are mixed linearly (in g, and in s = sin^2 theta). This keeps a narrow line narrow when it
moves by a sizeable fraction of its width between table points (plain linear mixing would broaden it). T is even in theta (aligned
structure, mirror x -> -x), so |theta| is used; below 0.5 deg lam0 is extrapolated linearly in s from the 0.5 and 2 deg records.
Usage: python wedge_postprocess.py --table ../runs/<..>_T18a_wedge_table/table.json --out ../runs/<..>_T18b_wedge_average
"""
import argparse, json, os
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--table", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--nx", type=int, default=121, help="samples across the aperture")
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)

d = json.load(open(args.table))
DATA = {}
for r in d["records"]:
    lam = np.asarray(r["lam_nm"], float); t = np.asarray(r["t_re"]) + 1j * np.asarray(r["t_im"]); o = np.argsort(lam)
    f = r["fit"]
    DATA.setdefault((r["structure"], r["g0"], r["pol"]), {})[(float(r["g"]), float(r["theta"]))] = dict(
        lam=lam[o], T=np.abs(t[o]) ** 2, lam0=f["lam0_nm"], Q=f["Q"], G=f["Gamma_nm"], dldg=f.get("dlam_dg_nm_per_nm"),
        flag=bool(f.get("flag_jump_post")) or bool(f.get("flag_jump_chain")))

def s_of(th): return np.sin(np.radians(th)) ** 2

def spec_theta(key, g, theta):
    """(lam0, f(lam)) at table gap g and any |theta|, by shift-aligned interpolation in s = sin^2 theta"""
    recs = DATA[key]; ths = sorted(t for (gg, t) in recs if gg == g)
    th = abs(theta); s = s_of(th)
    if th <= ths[0]:
        r0, r1 = recs[(g, ths[0])], recs[(g, ths[1])]
        lam0 = r0["lam0"] + (r1["lam0"] - r0["lam0"]) * (s - s_of(ths[0])) / (s_of(ths[1]) - s_of(ths[0]))
        return lam0, (lambda L, r=r0, dl=lam0 - r0["lam0"]: np.interp(L - dl, r["lam"], r["T"]))
    if th >= ths[-1]:
        r = recs[(g, ths[-1])]; return r["lam0"], (lambda L, r=r: np.interp(L, r["lam"], r["T"]))
    k = np.searchsorted(ths, th) - 1; ta, tb = ths[k], ths[k + 1]
    ra, rb = recs[(g, ta)], recs[(g, tb)]; w = (s - s_of(ta)) / (s_of(tb) - s_of(ta))
    lam0 = (1 - w) * ra["lam0"] + w * rb["lam0"]
    return lam0, (lambda L: (1 - w) * np.interp(L - (lam0 - ra["lam0"]), ra["lam"], ra["T"])
                  + w * np.interp(L - (lam0 - rb["lam0"]), rb["lam"], rb["T"]))

def T_of(key, lam, theta, g):
    """T(lam; g, theta), shift-aligned interpolation in g between the two neighbouring table gaps"""
    gs = sorted({gg for (gg, t) in DATA[key]})
    g = min(max(g, gs[0]), gs[-1])
    k = min(np.searchsorted(gs, g, side="right") - 1, len(gs) - 2); ga, gb = gs[k], gs[k + 1]
    la, fa = spec_theta(key, ga, theta); lb, fb = spec_theta(key, gb, theta)
    w = (g - ga) / (gb - ga); lam0 = (1 - w) * la + w * lb
    return (1 - w) * fa(lam - (lam0 - la)) + w * fb(lam - (lam0 - lb))

def P_of(key, lam, theta, alpha_urad, D_um, g0):
    """aperture average; alpha in urad, D in um -> gap spread alpha*D in nm (1 urad * 1 um = 1e-12 m = 1e-3 nm)"""
    xs = np.linspace(-0.5, 0.5, args.nx) * D_um
    th = theta - np.degrees(alpha_urad * 1e-6) / 2
    return np.mean([T_of(key, lam, th, g0 + alpha_urad * x * 1e-3) for x in xs], axis=0)

def dip_metrics(lam, P):
    i = int(np.argmin(P)); lo = P[i]; hi = P.max(); half = lo + 0.5 * (hi - lo)
    left = np.where(P[:i] > half)[0]; right = np.where(P[i:] > half)[0]
    if not len(left) or not len(right): return dict(lam_min=lam[i], depth=hi - lo, fwhm=np.nan)
    a = left[-1]; b = i + right[0]
    la = np.interp(half, [P[a + 1], P[a]], [lam[a + 1], lam[a]]); lb = np.interp(half, [P[b - 1], P[b]], [lam[b - 1], lam[b]])
    return dict(lam_min=lam[i], depth=hi - lo, fwhm=lb - la, P_min=lo, P_max=hi)

out = dict(model=__doc__.split("Usage")[0], settings=dict(nx=args.nx), a={}, b={}, c={})
# (a) structure (i): T9b, g0 380 / 500, TE / TM, normal incidence (0.5 deg records), D 50/100/200 um, alpha 0..200 urad.
# The passband is taken as the Lorentzian of the resonant pole, L(lam) = (G/2)^2 / ((lam - lam0)^2 + (G/2)^2), with lam0(g) and G(g) read
# from the table fits (so the real, slightly nonlinear dlam/dg and the change of G across the wedge are included). The analytic estimate
# uses a fixed G and a linear dlam/dg. The full |t|^2 average (Fano line, background included) is stored as curves for the figure.
alphas = np.linspace(0, 200, 41)
def lor_params(key, g):
    recs = DATA[key]; gs = sorted({gg for (gg, t) in recs if t == 0.5})
    l0 = np.interp(g, gs, [recs[(gg, 0.5)]["lam0"] for gg in gs]); G = np.interp(g, gs, [recs[(gg, 0.5)]["G"] for gg in gs])
    return l0, G
def lor_avg(key, lam, alpha_urad, D_um, g0):
    xs = np.linspace(-0.5, 0.5, args.nx) * D_um; acc = 0
    for x in xs:
        l0, G = lor_params(key, g0 + alpha_urad * x * 1e-3); acc = acc + (G / 2) ** 2 / ((lam - l0) ** 2 + (G / 2) ** 2)
    return acc / len(xs)
def peak_metrics(lam, P):
    i = int(np.argmax(P)); pk = P[i]; half = pk / 2
    a = np.where(P[:i] < half)[0]; b = np.where(P[i:] < half)[0]
    if not len(a) or not len(b): return dict(peak=pk, fwhm=np.nan, lam_peak=lam[i])
    a = a[-1]; b = i + b[0]
    la = np.interp(half, [P[a], P[a + 1]], [lam[a], lam[a + 1]]); lb = np.interp(half, [P[b], P[b - 1]], [lam[b], lam[b - 1]])
    return dict(peak=pk, fwhm=lb - la, lam_peak=lam[i])
for key in sorted(k for k in DATA if k[0] == "T9b"):
    g0 = key[1]; r0 = DATA[key][(float(g0), 0.5)]; G0 = r0["G"]; dldg = r0["dldg"]
    lam = np.linspace(r0["lam0"] - 8 * G0 - 8, r0["lam0"] + 8 * G0 + 8, 4001)
    rows = []
    for D in (50, 100, 200):
        for al in alphas:
            m = peak_metrics(lam, lor_avg(key, lam, al, D, g0)); W = abs(dldg) * al * D * 1e-3
            rows.append(dict(D_um=D, alpha_urad=float(al), W_nm=float(W), fwhm_nm=float(m["fwhm"]), peak=float(m["peak"]),
                             fwhm_analytic_nm=float(np.sqrt(G0 ** 2 + W ** 2)),
                             peak_analytic=float(1.0 if W == 0 else (G0 / W) * np.arctan(W / G0))))
    res = dict(Gamma0_nm=G0, Q0=r0["Q"], lam0_nm=r0["lam0"], dlam_dg=dldg, rows=rows, thresholds={}, curves={})
    for D in (50, 100, 200):
        rr = [r for r in rows if r["D_um"] == D]; al = np.array([r["alpha_urad"] for r in rr]); wd = np.array([r["fwhm_nm"] for r in rr]) / G0
        th = {}
        for lab, f in (("10pct", 1.1), ("100pct", 2.0)):
            j = np.where(wd >= f)[0]
            th[lab + "_numeric_urad"] = float(np.interp(f, wd[j[0] - 1:j[0] + 1], al[j[0] - 1:j[0] + 1])) if len(j) and j[0] > 0 else None
            th[lab + "_analytic_urad"] = float(G0 * np.sqrt(f ** 2 - 1) / (abs(dldg) * D * 1e-3))
        res["thresholds"][str(D)] = th
    lam_c = np.linspace(r0["lam0"] - 6 * G0 - 4, r0["lam0"] + 6 * G0 + 4, 801)
    for al in (0, 50, 100, 200):
        res["curves"][f"D100_a{al}"] = dict(lam_nm=lam_c.tolist(), P=P_of(key, lam_c, 0.0, al, 100, g0).tolist())
    out["a"]["|".join(map(str, key))] = res
    print("(a)", key, "G0", round(G0, 3), "Q0", round(r0["Q"]), "dl/dg", round(dldg, 4), res["thresholds"], flush=True)
# (b), (c) structure (ii): prelim TM, g0 200
key = ("prelim", 200, "TM")
if key in DATA:
    r0 = DATA[key][(200.0, 0.5)]; G = r0["G"]
    lam = np.linspace(r0["lam0"] - 4 * G, r0["lam0"] + 4 * G, 1601); P0 = P_of(key, lam, 0.0, 0.0, 100, 200)
    m = dip_metrics(lam, P0); half = m["P_min"] + 0.5 * m["depth"]; i = int(np.argmin(P0))
    j = np.where(P0[:i] > half)[0][-1]; lam_h = float(np.interp(half, [P0[j + 1], P0[j]], [lam[j + 1], lam[j]]))   # blue-side half depth
    out["b"]["lam_half_nm"] = lam_h; out["b"]["side"] = "blue (the TM line moves to shorter lam with angle)"
    th = np.concatenate([np.linspace(-8, -1, 141), np.linspace(-1, 1, 801)[1:-1], np.linspace(1, 8, 141)])
    curves = {}
    for D in (50, 100, 200):
        for al in (0, 20, -20, 50, -50):
            Pt = np.array([P_of(key, np.array([lam_h]), t_, al, D, 200)[0] for t_ in th])
            # centre: the c that best mirrors P about itself (|u| <= 6 deg), on a fine grid
            u = np.linspace(0.05, 6, 120)
            f = lambda c: np.sum((np.interp(c + u, th, Pt) - np.interp(c - u, th, Pt)) ** 2)
            cs = np.linspace(-0.01, 0.01, 401); c = cs[int(np.argmin([f(c_) for c_ in cs]))]
            cs = np.linspace(c - 1e-4, c + 1e-4, 401); c = cs[int(np.argmin([f(c_) for c_ in cs]))]
            curves[f"D{D}_a{al}"] = dict(theta_deg=th.tolist(), P=Pt.tolist(), centre_deg=float(c),
                                         centre_urad=float(np.radians(c) * 1e6), expected_urad=al / 2)
            print("(b)", D, al, "centre", round(np.radians(c) * 1e6, 2), "urad; expected", al / 2, flush=True)
    out["b"]["curves"] = curves
    # (c) dither signal S(theta) = [P(theta; +ad) - P(theta; -ad)] / 2; first-order expectation S = -(ad/2) dP/dtheta
    thf = np.concatenate([np.linspace(-8, -0.5, 151), np.linspace(-0.5, 0.5, 201)[1:-1], np.linspace(0.5, 8, 151)])
    for D in (50, 100, 200):
        P_0 = np.array([P_of(key, np.array([lam_h]), t_, 0, D, 200)[0] for t_ in thf])
        dP = np.gradient(P_0, thf)                                    # per degree
        for ad in (10, 20):
            Pp = np.array([P_of(key, np.array([lam_h]), t_, ad, D, 200)[0] for t_ in thf])
            Pm = np.array([P_of(key, np.array([lam_h]), t_, -ad, D, 200)[0] for t_ in thf])
            S = 0.5 * (Pp - Pm); near = np.abs(thf) < 0.5; tn, Sn = thf[near], S[near]
            k = np.where(np.sign(Sn[:-1]) != np.sign(Sn[1:]))[0]
            z = float(np.interp(0, [Sn[k[0]], Sn[k[0] + 1]], [tn[k[0]], tn[k[0] + 1]])) if len(k) else None
            slope = float(np.polyfit(tn[np.abs(tn) < 0.2], Sn[np.abs(tn) < 0.2], 1)[0])           # per degree of theta
            expS = -(np.degrees(ad * 1e-6) / 2) * dP
            out["c"][f"D{D}_ad{ad}"] = dict(zero_deg=z, slope_per_deg=slope,
                                            slope_first_order_per_deg=float(np.polyfit(tn[np.abs(tn) < 0.2], expS[near][np.abs(tn) < 0.2], 1)[0]),
                                            S_max=float(np.max(np.abs(S))), theta_at_S_max=float(thf[int(np.argmax(np.abs(S)))]),
                                            max_dev_from_first_order=float(np.max(np.abs(S - expS))),
                                            theta_deg=thf.tolist(), S=S.tolist(), S_first_order=expS.tolist(), P0=P_0.tolist())
            print("(c)", D, ad, "zero", z, "slope/deg", slope, "|S|max", np.max(np.abs(S)), "at", thf[int(np.argmax(np.abs(S)))], flush=True)
json.dump(out, open(os.path.join(args.out, "wedge_average.json"), "w"))
print("done")
