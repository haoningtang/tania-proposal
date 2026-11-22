"""T15c analysis: table.csv, analysis.json, analysis.png from conv.json (moire_conv.py)."""
import json, os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

d = sys.argv[1]
res = json.load(open(os.path.join(d, "conv.json")))
rows, summ = [], {}
for key, v in res.items():
    if "error" in v: continue
    tw, kind, N = v["twist"], v["kind"], v["N"]
    recs = v["recs"]; i0 = 4  # centre = lam_target
    def q(r, pol="x"):
        p = r[pol]; return dict(Tmax=max(p["T_moire"]), Rmax=max(p["R_moire"]), T4=sum(p["T_moire"]), R4=sum(p["R_moire"]),
                                T0=p["T0"], T=p["T"], R=p["R"])
    c = q(recs[i0]); cs = q(recs[i0], "sp")
    win = [q(r) for r in recs]; j = int(np.argmax([w["Tmax"] for w in win]))
    rows.append(dict(twist=tw, kind=kind, N=N, lam=v["lam_target"], **{k: c[k] for k in c},
                     Tmax_sp=cs["Tmax"], T4_sp=cs["T4"],
                     win_Tmax=win[j]["Tmax"], win_lam=recs[j]["lam"], win_T4=win[j]["T4"], win_R4=win[j]["R4"], win_T0=win[j]["T0"],
                     sec=v["sec_per_solve"], mem=v["peak_mem_GiB"], energy=c["T"] + c["R"]))
rows.sort(key=lambda r: (r["twist"], r["kind"], r["N"]))
keys = list(rows[0].keys())
with open(os.path.join(d, "table.csv"), "w") as f:
    f.write(",".join(keys) + "\n")
    for r in rows: f.write(",".join(f"{r[k]:.6g}" if isinstance(r[k], float) else str(r[k]) for k in keys) + "\n")
cases = sorted({(r["twist"], r["kind"]) for r in rows})
for tw, kind in cases:
    rr = [r for r in rows if r["twist"] == tw and r["kind"] == kind]
    summ[f"{tw}_{kind}"] = dict(lam=rr[0]["lam"], N=[r["N"] for r in rr], Tmax=[r["Tmax"] for r in rr], Rmax=[r["Rmax"] for r in rr],
                                T4=[r["T4"] for r in rr], R4=[r["R4"] for r in rr], T0=[r["T0"] for r in rr],
                                win_Tmax=[r["win_Tmax"] for r in rr], win_lam=[r["win_lam"] for r in rr])
cost = {N: dict(sec=float(np.mean([r["sec"] for r in rows if r["N"] == N])), mem=float(max(r["mem"] for r in rows if r["N"] == N)))
        for N in sorted({r["N"] for r in rows})}
json.dump(dict(cases=summ, cost=cost, max_energy_err=float(max(abs(r["energy"] - 1) for r in rows))),
          open(os.path.join(d, "analysis.json"), "w"), indent=1)

fig, ax = plt.subplots(1, 3, figsize=(15, 4.3))
for tw, kind in cases:
    s = summ[f"{tw}_{kind}"]; lab = f"{tw}°, {kind} {s['lam']:.1f} nm"
    ls = "-" if kind == "res" else "--"
    l, = ax[0].plot(s["N"], np.array(s["Tmax"]) * 100, "o" + ls, label=lab)
    ax[1].plot(s["N"], np.array(s["win_Tmax"]) * 100, "o" + ls, color=l.get_color())
    ax[2].plot(s["N"], np.array(s["T4"]) * 100, "o" + ls, color=l.get_color())
ax[0].set_title("strongest single moiré order T (x input), at λ target")
ax[1].set_title("same, max over λ target ± 4 nm")
ax[2].set_title("four-order sum T")
for a in ax: a.set_xlabel("N"); a.set_ylabel("%"); a.grid(alpha=.3)
ax[0].legend(fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(d, "analysis.png"), dpi=110)
for r in rows:
    print(f"{r['twist']:>2} {r['kind']:4} N{r['N']} lam {r['lam']:.2f}: Tmax {100*r['Tmax']:.2f} Rmax {100*r['Rmax']:.2f} T4 {100*r['T4']:.2f} "
          f"R4 {100*r['R4']:.2f} T0 {r['T0']:.3f} | win max {100*r['win_Tmax']:.2f} @ {r['win_lam']:.0f} | {r['sec']:.1f}s {r['mem']:.2f}GiB")
print(cost)
