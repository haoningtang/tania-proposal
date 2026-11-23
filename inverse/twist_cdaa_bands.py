"""T19c (cloud 08:33 check): max |CD_AA| per (twist, N), on the main line and over the full band.
Definition: field at r = 0 (AA = twist axis) = sum over all kept moire orders of the complex transmitted amplitude (x, y components),
T_sigma = |E_x|^2 + |E_y|^2 with sigma+- input = (x +- i y)/sqrt(2) (linear combination of the x and y runs), CD_AA = T_s+ - T_s-.
Usage: python twist_cdaa_bands.py RUN_T19a  -> prints table, writes RUN/analysis_T19c_cdaa_bands.json"""
import glob, json, os, sys
import numpy as np
R = sys.argv[1]; out = {}
for f in sorted(glob.glob(os.path.join(R, "amps", "tw*_N*.npz"))):
    d = np.load(f); lam = d["lam"]; o = np.argsort(lam); lam = lam[o]
    Ex = d["tx"][o][:, :, :2].sum(1); Ey = d["ty"][o][:, :, :2].sum(1)
    Tp = (np.abs(Ex + 1j * Ey) ** 2).sum(-1) / 2; Tm = (np.abs(Ex - 1j * Ey) ** 2).sum(-1) / 2; cd = Tp - Tm
    main = (lam >= 1500) & (lam <= 1512.5)
    tag = os.path.basename(f)[2:-4]
    i, j = np.argmax(np.abs(cd[main])), np.argmax(np.abs(cd))
    out[tag] = dict(twist=float(d["twist"]), N=int(d["N"]), lam=lam.tolist(), CD_AA=cd.tolist(),
                    max_main=float(cd[main][i]), lam_max_main=float(lam[main][i]), rms_main=float(np.sqrt((cd[main] ** 2).mean())),
                    max_full=float(cd[j]), lam_max_full=float(lam[j]), rms_full=float(np.sqrt((cd ** 2).mean())))
    r = out[tag]
    print(f"{tag:10s} main 1500-1512.5: max {r['max_main']:+.4f} @ {r['lam_max_main']:.1f}  rms {r['rms_main']:.4f} | "
          f"full {lam[0]:.0f}-{lam[-1]:.0f}: max {r['max_full']:+.4f} @ {r['lam_max_full']:.1f}  rms {r['rms_full']:.4f}")
json.dump(out, open(os.path.join(R, "analysis_T19c_cdaa_bands.json"), "w"))
