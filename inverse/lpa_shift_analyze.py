"""T19b analysis: checks and summary of the LPA Jones map (lpa_jones.npz)."""
import json, sys, os, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = sys.argv[1]; d = np.load(os.path.join(R, "lpa_jones.npz")); J = d["J"]; lam = d["lam"]; n = int(d["n"])
ep, em = np.array([1, 1j]) / np.sqrt(2), np.array([1, -1j]) / np.sqrt(2)
Tp = np.sum(np.abs(J @ ep) ** 2, -1); Tm = np.sum(np.abs(J @ em) ** 2, -1); CD = Tp - Tm
Tx = np.sum(np.abs(J[..., :, 0]) ** 2, -1)
sym = np.abs(J[..., 0, 1] - J[..., 1, 0]).max()
cdform = 2 * np.imag((J[..., 0, 0] - J[..., 1, 1]) * np.conj(J[..., 0, 1]))
# mirror x -> -x on the shift: CD(-dx, dy) = -CD(dx, dy)
idx = (-np.arange(n)) % n
odd = np.abs(CD + CD[idx, :, :]).max()
il = np.argmin(Tx[0, 0])
out = dict(n=n, n_lam=int(len(lam)), solver="fmmax 80/96 (model.py), normal incidence, a 620, t 220, r 120, gap 200 nm",
           max_abs_Jxy_minus_Jyx=float(sym), max_abs_CD_minus_formula=float(np.abs(CD - cdform).max()),
           CD_mirror_odd_residual=float(odd), aligned_line_nm=float(lam[il]), aligned_Tx_min=float(Tx[0, 0, il]),
           max_abs_CD=float(np.abs(CD).max()), CD_at_000=float(np.abs(CD[0, 0]).max()),
           max_abs_CD_on_mirror_lines=float(max(np.abs(CD[0]).max(), np.abs(CD[:, 0]).max(),
                                                 max(np.abs(CD[i, i]).max() for i in range(n)), max(np.abs(CD[i, -i % n]).max() for i in range(n)))),
           shift_avg_CD_max=float(np.abs(CD.mean((0, 1))).max()),
           where_max=[int(v) for v in np.unravel_index(np.abs(CD).argmax(), CD.shape)])
out["where_max_lam_nm"] = float(lam[out["where_max"][2]])
json.dump(out, open(os.path.join(R, "analysis.json"), "w"), indent=1); print(json.dumps(out, indent=1))
fig, ax = plt.subplots(1, 3, figsize=(13, 3.8))
li = int(np.argmin(np.abs(lam - 1510)))
im = ax[0].imshow(Tx[:, :, li].T, origin="lower", extent=[0, 1, 0, 1]); ax[0].set_title(f"T_x at {lam[li]:.1f} nm"); plt.colorbar(im, ax=ax[0])
m = np.abs(CD[:, :, li]).max()
im = ax[1].imshow(CD[:, :, li].T, origin="lower", extent=[0, 1, 0, 1], cmap="RdBu_r", vmin=-m, vmax=m); ax[1].set_title(f"CD_LPA(δ) at {lam[li]:.1f} nm"); plt.colorbar(im, ax=ax[1])
for a_ in ax[:2]: a_.set_xlabel("δx / a"); a_.set_ylabel("δy / a")
ax[2].plot(lam, Tx[0, 0], label="T_x (0,0)"); ax[2].plot(lam, Tx[2, 4], label="T_x (2,4)/16")
ax[2].plot(lam, CD[2, 4], label="CD (2,4)/16"); ax[2].plot(lam, CD.mean((0, 1)), label="CD shift avg"); ax[2].set_xlabel("λ (nm)"); ax[2].legend(fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(R, "analysis.png"), dpi=110)
