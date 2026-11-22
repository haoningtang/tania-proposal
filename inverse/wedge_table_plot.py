"""T18a figure: lam0(g) and Q(g) per theta for each (structure, g0, pol), and the +-theta symmetry check."""
import json, os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
D = sys.argv[1]
T = json.load(open(os.path.join(D, "table.json"))); S = json.load(open(os.path.join(D, "symmetry.json")))
cases = [("T9b", 380, "TE"), ("T9b", 380, "TM"), ("T9b", 500, "TE"), ("T9b", 500, "TM"), ("prelim", 200, "TM")]
fig, ax = plt.subplots(3, 4, figsize=(17, 11)); ax = ax.flat
cols = dict(zip([0.5, 2.0, 4.0, 6.0, 8.0], plt.cm.viridis(np.linspace(0, 0.9, 5))))
summ = {}
for k, (s, g0, pol) in enumerate(cases):
    for th, c in cols.items():
        rr = sorted([r for r in T["records"] if r["structure"] == s and r["g0"] == g0 and r["pol"] == pol and r["theta"] == th], key=lambda r: r["g"])
        g = [r["g"] for r in rr]
        ax[2 * k].plot(g, [r["fit"]["lam0_nm"] for r in rr], "o-", color=c, ms=3, label=f"{th:g}°")
        ax[2 * k + 1].semilogy(g, [r["fit"]["Q"] for r in rr], "o-", color=c, ms=3)
        h = [r for r in T["hires"] if r["structure"] == s and r["g0"] == g0 and r["pol"] == pol and r["theta"] == th]
        if h:
            ax[2 * k].plot([g0], [h[0]["fit"]["lam0_nm"]], "*", color=c, ms=10, mec="k")
            ax[2 * k + 1].semilogy([g0], [h[0]["fit"]["Q"]], "*", color=c, ms=10, mec="k")
    ax[2 * k].set_title(f"{s} g0 {g0} {pol}: λ0 (★ 200/192 at g0)", fontsize=9); ax[2 * k].set_xlabel("gap (nm)"); ax[2 * k].legend(fontsize=6)
    ax[2 * k + 1].set_title(f"{s} g0 {g0} {pol}: Q", fontsize=9); ax[2 * k + 1].set_xlabel("gap (nm)")
for c_ in S["cases"]:
    l = np.array(c_["lam_nm"])
    for key, ls in (("TE_total", "-"), ("TM_total", "--"), ("sum", ":")):
        ax[10].plot(l, np.array(c_["plus"][key]) - np.array(c_["minus"][key]), ls=ls, label=f"{c_['theta']:g}° {key}")
ax[10].set_title("shift (20,20) nm, gap 200: T(+θ) − T(−θ)", fontsize=9); ax[10].legend(fontsize=6); ax[10].set_xlabel("λ (nm)")
ax[11].axis("off")
fig.tight_layout(); fig.savefig(os.path.join(D, "analysis.png"), dpi=100)
