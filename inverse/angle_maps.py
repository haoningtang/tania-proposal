"""T13c: flat vs curved angle response of the prelim square bilayer.

1. Find the gap where the TE band curvature c = (dlam/lam)/sin^2(theta) (theta 0.5/3/6 deg, as in jacobian.py) crosses zero:
   coarse scan over --gaps, then secant steps on the bracketing pair until |c| < ctol.
2. At that gap and at --gap_ref: transmission maps T(theta_x, theta_y), theta_x, theta_y = 0..10 deg (1 deg), at the 0.5-deg
   resonance wavelength of that state, for TE and TM (defined w.r.t. the local plane of incidence) and the unpolarized mean.
   Direction: (kx, ky)/k0 = (sin theta_x, sin theta_y), i.e. sin(theta) = sqrt(sin^2 theta_x + sin^2 theta_y),
   azimuth = atan2(sin theta_y, sin theta_x).
Usage: python angle_maps.py --out ../runs/<name> [--gaps 120 ... --gap_ref 200 --n_terms 80 --ngrid 96]
Writes maps.json, angle_maps.png.
"""
import argparse, json, os, time
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from analyze import band
from model import bilayer_t

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--a", type=float, default=0.62); ap.add_argument("--t", type=float, default=0.22)
ap.add_argument("--r", type=float, default=0.12)
ap.add_argument("--gaps", type=float, nargs="+", default=[120, 160, 200, 240, 280, 320, 400, 500])
ap.add_argument("--gap_ref", type=float, default=200)
ap.add_argument("--ctol", type=float, default=2e-4)
ap.add_argument("--lam0", type=float, default=1.507)
ap.add_argument("--thetas", type=float, nargs="+", default=[0.5, 3.0, 6.0])
ap.add_argument("--n_terms", type=int, default=80); ap.add_argument("--ngrid", type=int, default=96)
ap.add_argument("--amax", type=float, default=10); ap.add_argument("--astep", type=float, default=1)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
kw = dict(n_terms=a.n_terms, ngrid=a.ngrid)
p = dict(a=a.a, t=a.t, r=a.r, r2=a.r, t2=a.t)
fn = os.path.join(a.out, "maps.json")
res = json.load(open(fn)) if os.path.exists(fn) else dict(settings=vars(a), scan=[], maps={})
lam_guess = {}


def curv(g):
    """TE and TM: lam, Q, c at gap g (nm); follows the line from the nearest gap already done"""
    near = min(res["scan"], key=lambda s: abs(s["gap"] - g)) if res["scan"] else None
    guess = near["lam_TE"] * 1e-3 if near else a.lam0
    b = band(p, dict(gap=g * 1e-3, shift=0.0), guess, a.thetas, kw)
    row = dict(gap=g)
    for pol in ("TE", "TM"):
        if b[pol] is None:                     # no pole found near the guess for this polarization
            row.update({f"lam_{pol}": float("nan"), f"Q_{pol}": float("nan"), f"c_{pol}": float("nan"), f"pts_{pol}": []})
            continue
        pts = b[pol]["pts"]
        s2 = np.sin(np.radians([q[0] for q in pts])) ** 2
        y = np.array([q[1] for q in pts]); y = (y - y[0]) / y[0]
        row.update({f"lam_{pol}": b[pol]["lam"] * 1e3, f"Q_{pol}": b[pol]["Q"],
                    f"c_{pol}": float(np.polyfit(s2[:3], y[:3], 1)[0]) if len(pts) >= 3 else float("nan"),
                    f"pts_{pol}": [[q[0], q[1] * 1e3, q[2]] for q in pts]})
    res["scan"].append(row); res["scan"].sort(key=lambda s: s["gap"])
    json.dump(res, open(fn, "w"), indent=1)
    print(f"gap {g:.2f}: TE {row['lam_TE']:.3f} nm Q {row['Q_TE']:.0f} c {row['c_TE']:+.5f} | "
          f"TM {row['lam_TM']:.3f} nm Q {row['Q_TM']:.0f} c {row['c_TM']:+.5f}", flush=True)
    return row


# 1. zero crossing of c_TE
done = {s["gap"] for s in res["scan"]}
for g in a.gaps:
    if g not in done:
        curv(g)
if "g_zero" not in res:
    S = [s for s in res["scan"] if np.isfinite(s["c_TE"])]
    br = [(S[i], S[i + 1]) for i in range(len(S) - 1) if np.sign(S[i]["c_TE"]) != np.sign(S[i + 1]["c_TE"])]
    if not br:
        print("no sign change of c_TE in the scanned gaps; using the gap of smallest |c_TE|", flush=True)
        best = min(S, key=lambda s: abs(s["c_TE"]))
    else:
        lo, hi = br[0]
        for _ in range(8):
            g = lo["gap"] - lo["c_TE"] * (hi["gap"] - lo["gap"]) / (hi["c_TE"] - lo["c_TE"])
            g = float(np.clip(g, lo["gap"] + 0.05 * (hi["gap"] - lo["gap"]), hi["gap"] - 0.05 * (hi["gap"] - lo["gap"])))
            m = curv(round(g, 2))
            if abs(m["c_TE"]) < a.ctol:
                break
            if np.sign(m["c_TE"]) == np.sign(lo["c_TE"]):
                lo = m
            else:
                hi = m
        best = min([s for s in res["scan"] if np.isfinite(s["c_TE"])], key=lambda s: abs(s["c_TE"]))
    res["g_zero"] = best["gap"]; json.dump(res, open(fn, "w"), indent=1)
print(f"TE zero-curvature gap: {res['g_zero']} nm", flush=True)

# 2. maps
ax_ = np.arange(0, a.amax + 1e-9, a.astep)
TX, TY = np.meshgrid(ax_, ax_, indexing="ij")
SX, SY = np.sin(np.radians(TX)), np.sin(np.radians(TY))
TH = np.degrees(np.arcsin(np.sqrt(SX ** 2 + SY ** 2))); PH = np.degrees(np.arctan2(SY, SX))
for g in (res["g_zero"], a.gap_ref):
    key = f"{g}"
    if key in res["maps"]:
        continue
    row = next((s for s in res["scan"] if s["gap"] == g), None) or curv(g)
    t0 = time.time()
    lam = 0.5 * (row["lam_TE"] + row["lam_TM"]) * 1e-3   # one probe wavelength per state (TE/TM degenerate to ~0.1 nm)
    M = {"TE": np.zeros_like(TH), "TM": np.zeros_like(TH)}
    for ph in np.unique(np.round(PH, 6)):
        idx = np.where(np.isclose(PH, ph, atol=1e-6))
        th = np.maximum(TH[idx], 1e-3)      # normal incidence: 1e-3 deg (TE/TM degenerate there)
        o = bilayer_t(np.full(len(th), lam), th, p["a"], p["t"], p["r"], g * 1e-3, r2=p["r2"], t2=p["t2"],
                      azimuth_deg=float(ph), **kw)
        for pol in ("TE", "TM"):
            M[pol][idx] = np.abs(np.asarray(o[f"t_{pol}"])) ** 2
    M = {k: v.tolist() for k, v in M.items()}
    M["unpol"] = (0.5 * (np.array(M["TE"]) + np.array(M["TM"]))).tolist()
    res["maps"][key] = dict(gap=g, lam_probe=lam * 1e3, lam_TE=row["lam_TE"], lam_TM=row["lam_TM"], c_TE=row["c_TE"], c_TM=row["c_TM"],
                            Q_TE=row["Q_TE"], Q_TM=row["Q_TM"], **M, wall_s=round(time.time() - t0, 1))
    res["maps_axes_deg"] = ax_.tolist()
    json.dump(res, open(fn, "w"), indent=1)
    print(f"map gap {g}: done in {time.time() - t0:.0f} s", flush=True)

# figure: rows = states (zero-curvature gap, gap_ref); columns = TE, TM, unpolarized
keys = [f"{res['g_zero']}", f"{a.gap_ref}"]
fig, axs = plt.subplots(2, 3, figsize=(10, 6.4), constrained_layout=True)
for i, k in enumerate(keys):
    m = res["maps"][k]
    for j, pol in enumerate(("TE", "TM", "unpol")):
        im = axs[i, j].imshow(np.array(m[pol]).T, origin="lower", extent=[-0.5, a.amax + 0.5, -0.5, a.amax + 0.5],
                              cmap="Blues_r", vmin=0, vmax=1)
        axs[i, j].set_title(f"gap {float(k):.1f} nm, {pol}, λ {m['lam_probe']:.2f} nm, c_TE {m['c_TE']:+.4f}", fontsize=8)
        axs[i, j].set_xlabel("θx (deg)"); axs[i, j].set_ylabel("θy (deg)")
fig.colorbar(im, ax=axs, shrink=0.8, label="transmission |t|²")
fig.suptitle("T13c: prelim square bilayer (a 620, t 220, r 120 nm), T(θx, θy) at the 0.5° resonance λ; "
             f"top: TE zero-curvature gap, bottom: gap {a.gap_ref:.0f} nm", fontsize=9)
fig.savefig(os.path.join(a.out, "angle_maps.png"), dpi=130)
print("figure written", flush=True)
