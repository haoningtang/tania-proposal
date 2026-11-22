"""Proposal figure for A3 (twist): power per moiré order of the twisted square prelim bilayer (T15b, rcwa4d-mf).
Run from the repo root: python3 docs/figs/make_T15b_moire_figure.py"""
import csv, json, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
RUN = "runs/20261122-0700_T15b_moire_orders"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"; C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False})
rows = list(csv.DictReader(open(f"{RUN}/table.csv")))
fig, ax = plt.subplots(1, 3, figsize=(11.0, 3.4))

# (a) angle of the first moire order vs twist
a = ax[0]; tw = np.linspace(0, 8.5, 200); lam, per = 1509.0, 620.0
a.plot(tw, np.degrees(np.arcsin(2 * lam / per * np.sin(np.radians(tw) / 2))), color=INK2, lw=1.4, label="sin θ = 2(λ/a)·sin(Δα/2)")
pts = sorted({(float(r["twist"]), float(r["theta_out"])) for r in rows if r["pol"] == "x" and r["where"] == "res" and r["N"] == "5" and float(r["twist"]) > 0})
a.plot([p[0] for p in pts], [p[1] for p in pts], "o", color=C2, ms=6.5, mec="white", mew=0.9, label="full-wave (rcwa4d-mf)")
a.set_xlim(0, 8.5); a.set_ylim(0, 21); a.set_xlabel("twist Δα (deg)"); a.set_ylabel("direction of the moiré order θ (deg)")
a.set_title("(a) Twist sets the receive direction", loc="left", fontsize=9.5, color=INK)
a.text(4.6, 6.0, "2.4° per 1° of twist\n(a = 620 nm, λ ≈ 1509 nm)", fontsize=7.5, color=INK2)
a.legend(frameon=False, fontsize=7, loc="upper left")

# (b) spectra at 2 deg, N 5, x input
b = ax[1]; d = json.load(open(f"{RUN}/orders_spec_N5_tw+2.json"))
L = np.array([e["lam"] for e in d]); T0 = np.array([e["x"]["T0"] for e in d])
Tm = np.array([max(e["x"]["T_moire"]) for e in d]); Rm = np.array([max(e["x"]["R_moire"]) for e in d])
b.plot(L, T0, color=INK2, lw=1.6, label="straight through (zero order)")
b.plot(L, Rm, color=C1, lw=2, label="reflected into one moiré order")
b.plot(L, Tm, color=C2, lw=2.2, label="transmitted into one moiré order")
b.set_xlim(1480, 1580); b.set_ylim(0, 1.02); b.set_xlabel("wavelength λ (nm)"); b.set_ylabel("fraction of x-polarized input")
b.set_title("(b) Twist 2°: where the light goes", loc="left", fontsize=9.5, color=INK)
b.legend(frameon=False, fontsize=7, loc="upper right")

# (c) strongest single order vs twist, converged values from T15c (N 6-8): at the resonance and at the best other wavelength
c = ax[2]; conv = list(csv.DictReader(open("runs/20261122-0710_T15c_moire_conv/table.csv")))
def series(kinds):
    out = []
    for tw in ("1", "2", "4", "8"):
        best = None
        for k in kinds:
            v = {int(r["N"]): 100 * float(r["Tmax"]) for r in conv if r["twist"] == tw and r["kind"] == k}
            if not v: continue
            hi = [v[N] for N in sorted(v) if N >= 6]; top = v[max(v)]
            if best is None or top > best[1]: best = (float(tw), top, min(hi), max(hi), max(v))
        out.append(best)
    return out
for kinds, col, mk, lab in ((("res",), C2, "o", "at the resonance (1507–1512 nm)"), (("pk", "pk2"), C1, "s", "best band edge (1518–1554 nm)")):
    p = series(kinds); x = np.array([q[0] for q in p]) * (0.94 if mk == "o" else 1.06)
    c.vlines(x, [q[2] for q in p], [q[3] for q in p], color=col, lw=3, alpha=0.35)
    c.plot(x, [q[1] for q in p], mk + "-", color=col, lw=1.6, ms=6.5, mec="white", mew=0.9, label=lab)
c.set_xscale("log", base=2); c.set_xticks([1, 2, 4, 8]); c.set_xticklabels(["1", "2", "4", "8"]); c.minorticks_off()
c.set_ylim(0, 12); c.set_xlim(0.8, 10); c.set_xlabel("twist Δα (deg)"); c.set_ylabel("transmitted into one moiré order (%)")
c.set_title("(c) Unoptimized: 3–5 % per order", loc="left", fontsize=9.5, color=INK)
c.text(0.85, 7.6, "points: highest N (7 or 8)\nbars: spread over N = 6–8", fontsize=7, color=INK2)
c.legend(frameon=False, fontsize=6.8, loc="upper left")
for x_ in ax: x_.grid(True, color=GRID, lw=0.6); x_.set_axisbelow(True)
fig.text(0.01, -0.06, "Twisted square Si bilayer (a 620, t 220, r 120 nm, gap 200 nm), normal incidence, rcwa4d-mf (T15b). By reciprocity, the fraction sent into a moiré order equals "
         "the fraction received from that direction into normal incidence.\nThe mirror order carries the same; the perpendicular pair < 0.2 %. (a, b): N = 5. (c): T15c, "
         "the last two N agree within 7 %; the 8° resonance value still rises (5.9 → 6.2 % for N 6 → 7). The resonance is the stacking-averaged band (T15), not the aligned line.",
         fontsize=6.6, color=INK2)
plt.tight_layout()
for ext in ("png", "pdf"): plt.savefig(f"docs/figs/T15b_twist_moire_orders.{ext}", dpi=200, bbox_inches="tight")
print("saved docs/figs/T15b_twist_moire_orders.png")
