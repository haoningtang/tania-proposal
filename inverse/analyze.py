"""Band analysis of a design: resonance wavelength, Q and M (etendue x resolving power, FP = 1) for
TE and TM, at each mechanical state, from complex-transmission pole fitting (AAA).

Usage:
  python analyze.py --run ../runs/<name>                 # uses best.json + config.json of that run
  python analyze.py --params '{"a":0.62,"t":0.22,"r":0.12}' --states '[{"gap":0.2}]' --lams '[1.506]' --out ../runs/check
Writes analysis.json and analysis.png into the run folder.

M is defined from the band curvature:  dlam/lam = -sin^2(theta) / (2 M)   (air-gap FP: M = 1).
Flat band: |M| large. Negative M = band bends the other way.
"""
import argparse, json, os
import numpy as np
from scipy.interpolate import AAA
from model import bilayer_t

def poles(lams, t, lo, hi):
    A = AAA(1 / np.asarray(lams), np.asarray(t), rtol=1e-6, max_terms=12)
    out = []
    for p, rz in zip(A.poles(), A.residues()):
        if p.real <= 0 or p.imag == 0:
            continue
        l0 = 1 / p.real; Q = p.real / (2 * abs(p.imag))
        if lo < l0 < hi and 10 < Q < 1e5 and abs(rz) / abs(p.imag) > 0.05:
            out.append((float(l0), float(Q)))
    return out

def scan(p, st, lams, th, kw, chunk=16):
    tTE, tTM = [], []
    for i in range(0, len(lams), chunk):
        o = bilayer_t(lams[i:i + chunk], th, p["a"], p["t"], p["r"], st.get("gap"), shift=st.get("shift", 0.0),
                      shift_y=st.get("shift_y", 0.0), c4=p.get("c4", 0.0), c8=p.get("c8", 0.0), r2=p.get("r2"), t2=p.get("t2"), **kw)
        tTE.append(np.asarray(o["t_TE"])); tTM.append(np.asarray(o["t_TM"]))
    return {"TE": np.concatenate(tTE), "TM": np.concatenate(tTM)}

def band(p, st, lam_guess, thetas, kw, span=0.04, n=41):
    res = {}
    lams = np.linspace(lam_guess - span, lam_guess + span, n)
    t0 = scan(p, st, lams, thetas[0], kw)
    for pol in ("TE", "TM"):
        P = poles(lams, t0[pol], lams[0], lams[-1])
        if not P:
            res[pol] = None; continue
        l0, Q0 = min(P, key=lambda x: abs(x[0] - lam_guess) / x[0] + 1e-4 * x[1] / 1000)
        pts = [(thetas[0], l0, Q0)]
        for th in thetas[1:]:
            w = max(6 * pts[-1][1] / pts[-1][2], 0.004) + 0.02 * np.sin(np.radians(th)) ** 2 * pts[-1][1]
            ll = np.linspace(pts[-1][1] - w, pts[-1][1] + w * 0.4, 31)
            P = poles(ll, scan(p, st, ll, th, kw)[pol], ll[0], ll[-1])
            if not P:
                break
            pts.append((th, *min(P, key=lambda x: abs(x[0] - pts[-1][1]))))
        s2 = np.sin(np.radians([q[0] for q in pts])) ** 2
        y = np.array([q[1] for q in pts]); y = (y - y[0]) / y[0]
        c = np.polyfit(s2[:3], y[:3], 1)[0] if len(pts) >= 3 else np.nan
        res[pol] = dict(lam=l0, Q=Q0, M=float(-1 / (2 * c)) if c else float("inf"), pts=pts)
    return res

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run"); ap.add_argument("--params"); ap.add_argument("--states"); ap.add_argument("--lams")
    ap.add_argument("--out"); ap.add_argument("--thetas", default="[0.5,3,6,10]")
    ap.add_argument("--n_terms", type=int, default=None); ap.add_argument("--ngrid", type=int, default=None)
    ap.add_argument("--azimuth", type=float, default=0.0, help="azimuth of the plane of incidence, deg (45 = lattice diagonal)")
    a = ap.parse_args()
    if a.run:
        cfg = json.load(open(os.path.join(a.run, "config.json"))); best = json.load(open(os.path.join(a.run, "best.json")))
        p = dict(cfg.get("fixed", {})); p.update({n: best[n] for n in cfg["design_vars"]})
        states = cfg["states"]; lams = [best[f"lam{k}"] for k in range(len(states))]
        kw = dict(n_terms=a.n_terms or cfg.get("n_terms", 120), ngrid=a.ngrid or cfg.get("ngrid", 128),
                  lattice=cfg.get("lattice", "square"))
        out = a.run
    else:
        p = json.loads(a.params); states = json.loads(a.states); lams = json.loads(a.lams)
        kw = dict(n_terms=a.n_terms or 120, ngrid=a.ngrid or 128); out = a.out
    if a.azimuth: kw["azimuth_deg"] = a.azimuth
    os.makedirs(out, exist_ok=True)
    thetas = json.loads(a.thetas)
    rows = []
    for st, lg in zip(states, lams):
        b = band(p, st, lg, thetas, kw)
        rows.append(dict(state=st, **{pol: b[pol] for pol in ("TE", "TM")}))
        print(json.dumps({"state": st, **{pol: (None if b[pol] is None else {k: round(v, 4) for k, v in b[pol].items() if k != "pts"}) for pol in ("TE", "TM")}}), flush=True)
    json.dump(dict(params=p, azimuth_deg=a.azimuth, settings=kw, rows=rows), open(os.path.join(out, "analysis.json"), "w"), indent=1)
    try:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(10, 4))
        for r in rows:
            for pol, ls in (("TE", "-"), ("TM", "--")):
                if r[pol] is None: continue
                q = np.array([x[:2] for x in r[pol]["pts"]])
                ax[0].plot(q[:, 0], (q[:, 1] - q[0, 1]) * 1000, ls, marker="o", label=f"{pol} gap={r['state'].get('gap')}")
        ax[0].set_xlabel("angle (deg)"); ax[0].set_ylabel("resonance shift (nm)"); ax[0].legend(fontsize=7)
        for pol, m in (("TE", "o"), ("TM", "s")):
            z = [(r[pol]["lam"] * 1000, abs(r[pol]["M"])) for r in rows if r[pol]]
            if z: z = np.array(z); ax[1].semilogy(z[:, 0], z[:, 1], m + "-", label=pol)
        ax[1].axhline(10, ls=":", c="k"); ax[1].set_xlabel("resonance wavelength (nm)"); ax[1].set_ylabel("|M|"); ax[1].legend()
        plt.tight_layout(); plt.savefig(os.path.join(out, "analysis.png"), dpi=130)
    except Exception as e:
        print("plot skipped:", e)
