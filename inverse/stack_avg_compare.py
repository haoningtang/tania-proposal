"""Average the stack_avg parts over the cell and compare with rcwa4d-mf dense spectra (explore/*.npz)."""
import json, glob, sys, os
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
d = sys.argv[1]
sh = {}
for f in glob.glob(os.path.join(d, "stack_avg/stack_part*.json")):
    J = json.load(open(f)); lam = np.array(J["lam_nm"]); n = J["n"]; sh.update(J["shifts"])
W = sum(v["mult"] for v in sh.values()); assert W == n * n, W
# each representative stands for its C4v orbit: 90-deg rotations swap x and y, mirrors swap + and -, so the orbit
# average of T_x (and of T_+-) is the representative's (T_x + T_y)/2 (and (T_+ + T_-)/2); the averaged CD is 0 by symmetry.
for v in sh.values():
    v["Tsym"] = 0.5 * (np.array(v["Tx"]) + np.array(v["Ty"])); v["Tcsym"] = 0.5 * (np.array(v["Tp"]) + np.array(v["Tm"]))
avg = {k: sum(v["mult"] * np.array(v[k]) for v in sh.values()) / W for k in ("Tsym", "Tcsym")}
avg["Tx"] = avg["Tsym"]
out = dict(lam_nm=lam.tolist(), n=n, avg={k: v.tolist() for k, v in avg.items()}, max_abs_Tlin_minus_Tcirc=float(np.abs(avg["Tsym"] - avg["Tcsym"]).max()), max_abs_CD_single_shift=float(max(np.abs(np.array(v["Tp"]) - np.array(v["Tm"])).max() for v in sh.values())),
           min_Tavg=float(avg["Tx"].min()), lam_at_min=float(lam[avg["Tx"].argmin()]))
fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
ax[0].plot(lam, sh["0,0"]["Tx"], "k:", label="aligned (fmmax 80/96)")
ax[0].plot(lam, avg["Tx"], "k-", lw=2.5, label=f"aligned, averaged over {n}×{n} shifts")
cmp = {}
for f in sorted(glob.glob(os.path.join(d, "explore/dense_N*_th*.npz"))):
    z = np.load(f); tag = os.path.basename(f)[6:-4]
    if "+0.1_" in tag or "+1_" in tag:
        ax[0].plot(z["lam"], z["Tx"], label="rcwa4d " + tag.replace("_g200", ""), lw=1, ls="-" if "+0.1_" in tag else "--")
        Ti = np.interp(lam, z["lam"], z["Tx"]); cmp[tag] = dict(rms_vs_avg=float(np.sqrt(np.mean((Ti - avg["Tx"]) ** 2))),
                                                               rms_vs_aligned=float(np.sqrt(np.mean((Ti - np.array(sh["0,0"]["Tx"])) ** 2))))
ax[0].set_xlabel("λ (nm)"); ax[0].set_ylabel("T_x (normal incidence)"); ax[0].legend(fontsize=7); ax[0].set_title("small twist vs stacking average")
# lambda_res vs shift
lr = {k: lam[np.argmin(v["Tx"])] for k, v in sh.items()}
M = np.full((n + 1, n + 1), np.nan)
for i in range(n + 1):
    for j in range(n + 1):
        p, q = sorted([min(i % n, (-i) % n), min(j % n, (-j) % n)])
        M[j, i] = lr.get(f"{p},{q}", np.nan)
im = ax[1].imshow(M, origin="lower", extent=[-0.5 / n * 620, (n + 0.5) / n * 620, -0.5 / n * 620, (n + 0.5) / n * 620], cmap="viridis")
plt.colorbar(im, ax=ax[1], label="λ at min T_x (nm)"); ax[1].set_xlabel("shift δx (nm)"); ax[1].set_ylabel("shift δy (nm)")
ax[1].set_title("aligned bilayer: resonance vs lateral shift")
fig.tight_layout(); fig.savefig(os.path.join(d, "stack_avg.png"), dpi=120)
out["rcwa4d_vs"] = cmp; json.dump(out, open(os.path.join(d, "stack_avg.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ("lam_nm", "avg")}, indent=1))
