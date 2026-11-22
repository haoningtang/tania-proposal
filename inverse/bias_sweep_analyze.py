"""T17a analysis: merge jacobian.json parts (T17a) with T13a's points, table + figure.
lam_bar = (lam_lo + lam_hi)/2; g = (d lam_bar/d dx, d lam_bar/d dy) (nm/nm): shift-noise sensitivity |g|.
Quadratic check: lam_bar(d) - lam_bar(0) = k |d|^2  ->  |g| = 2 k |d|."""
import json, sys, glob, os
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
out = sys.argv[1]; t13 = sys.argv[2]
pts = {}
for f in sorted(glob.glob(os.path.join(out, "part*/jacobian.json"))) + [os.path.join(t13, "jacobian.json")]:
    for k, v in json.load(open(f))["points"].items():
        pts.setdefault(k, dict(v, src=os.path.relpath(f, out)))
rows = []
for k, v in pts.items():
    dx, dy = map(float, k.split(",")); J = np.array(v["J_raw"]); b = v["base"]
    lb = 0.5 * (b["lam_lo"] + b["lam_hi"])
    gx, gy = 0.5 * (J[0, 1] + J[1, 1]), 0.5 * (J[0, 2] + J[1, 2])
    sv = v["sv"]
    rows.append(dict(point=k, dx=dx, dy=dy, lam_lo=b["lam_lo"], lam_hi=b["lam_hi"], split_nm=b["lam_hi"] - b["lam_lo"], Q_lo=b["Q_lo"], Q_hi=b["Q_hi"],
                     lam_bar=lb, dlam_dgap=0.5 * (J[0, 0] + J[1, 0]), g_x=gx, g_y=gy, g_abs=float(np.hypot(gx, gy)),
                     sv1=sv[0], sv2=sv[1], sv3=sv[2], cond_13=sv[0] / sv[2], cond_12=sv[0] / sv[1], rank=v["rank"],
                     sv_lam=v["sv_lam_only"], src=v["src"]))
rows.sort(key=lambda r: (r["dx"] != r["dy"], r["dx"] + r["dy"], r["dx"]))
l0 = [r for r in rows if r["point"] == "0,0"][0]["lam_bar"]
diag = [r for r in rows if r["dx"] == r["dy"] and r["dx"] > 0]
d2 = np.array([2 * r["dx"] ** 2 for r in diag]); dl = np.array([r["lam_bar"] - l0 for r in diag])
k_fit = float(np.sum(d2 * dl) / np.sum(d2 * d2))
for r in rows:
    r["dlam_bar_from_0"] = r["lam_bar"] - l0; r["g_quadratic"] = 2 * k_fit * float(np.hypot(r["dx"], r["dy"]))
json.dump(dict(rows=rows, k_fit_nm_per_nm2=k_fit, note=__doc__), open(os.path.join(out, "analysis.json"), "w"), indent=1)
keys = ["point", "lam_lo", "lam_hi", "split_nm", "Q_lo", "Q_hi", "dlam_dgap", "g_x", "g_y", "g_abs", "g_quadratic", "sv1", "sv2", "sv3", "cond_13", "rank"]
with open(os.path.join(out, "table.csv"), "w") as f:
    f.write(",".join(keys) + "\n")
    for r in rows: f.write(",".join(f'"{r[k]}"' if k == "point" else f"{r[k]:.6g}" for k in keys) + "\n")
for r in rows: print("  ".join(f"{k} {r[k]:.4g}" if k != "point" else f"({r[k]})" for k in keys))
print("k_fit", k_fit)
fig, ax = plt.subplots(1, 3, figsize=(14, 4.2))
D = [r["dx"] for r in diag]; Dall = [0.0] + D
dg = [[r for r in rows if r["point"] == "0,0"][0]] + diag
for i, c in enumerate(["C0", "C1", "C2"]):
    ax[0].semilogy(Dall, [r[f"sv{i+1}"] for r in dg], "o-", color=c, label=f"σ{i+1} (diagonal bias)")
for r in rows:
    if r["dx"] != r["dy"]:
        for i, c in enumerate(["C0", "C1", "C2"]):
            ax[0].semilogy([20], [r[f"sv{i+1}"]], "s" if r["dx"] else "^", mfc="none", color=c, ms=9)
ax[0].plot([], [], "ks", mfc="none", label="(20,0)"); ax[0].plot([], [], "k^", mfc="none", label="(0,20)")
ax[0].set_xlabel("bias δx = δy (nm)"); ax[0].set_ylabel("singular value (normalized)"); ax[0].legend(fontsize=7); ax[0].set_title("Jacobian (gap, δx, δy) → 6 observables")
ax[1].semilogy(Dall, [r["cond_13"] for r in dg], "o-k", label="σ1/σ3")
ax[1].semilogy(Dall, [r["cond_12"] for r in dg], "o--", color="gray", label="σ1/σ2")
for r in rows:
    if r["dx"] != r["dy"]: ax[1].semilogy([20], [min(r["cond_13"], 1e9)], "s" if r["dx"] else "^", mfc="none", color="k", ms=9)
ax[1].axhline(100, color="r", lw=0.8, ls=":", label="rank cut (rtol 1e-2)"); ax[1].set_xlabel("bias δx = δy (nm)"); ax[1].legend(fontsize=7); ax[1].set_title("condition number")
ax[2].plot([np.hypot(r["dx"], r["dy"]) for r in dg], [r["g_abs"] for r in dg], "o", color="C3", label="|∇λ̄| from Jacobian")
xx = np.linspace(0, 60, 50); ax[2].plot(xx, 2 * k_fit * xx, "-", color="C3", lw=0.8, label=f"2k|δ|, k = {k_fit:.2e} nm/nm²")
for r in rows:
    if r["dx"] != r["dy"]: ax[2].plot([20], [r["g_abs"]], "s" if r["dx"] else "^", mfc="none", color="C3", ms=9)
ax[2].set_xlabel("|δ| (nm)"); ax[2].set_ylabel("∂λ̄/∂δ (nm/nm)"); ax[2].legend(fontsize=7); ax[2].set_title("shift-noise sensitivity")
fig.suptitle("T17a: prelim square bilayer, gap 200 nm, 80/96, ±5 nm central differences", fontsize=10); fig.tight_layout()
fig.savefig(os.path.join(out, "analysis.png"), dpi=120)
