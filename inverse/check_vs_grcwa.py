"""Cross-check the fmmax model against the grcwa preliminary results in prelim/.

grcwa (nG = 81) gave: single slab (r = 120 nm) resonance near 1.535 um, flat in TE and curved in TM;
bilayer, gap 200 nm, near 1.506 um; at 6 deg TE stays (flat) and TM shifts to shorter wavelength."""
import numpy as np, time
from model import bilayer_t

def scan(lams, th, gap, chunk=16, **kw):
    TE, TM = [], []
    for i in range(0, len(lams), chunk):
        o = bilayer_t(lams[i:i+chunk], th, 0.62, 0.22, 0.12, gap, **kw)
        TE.append(np.asarray(o["T_TE"])); TM.append(np.asarray(o["T_TM"]))
    return np.concatenate(TE), np.concatenate(TM)

if __name__ == "__main__":
    lams = np.linspace(1.47, 1.55, 81)
    for gap in (0.20, 0.085):
        for th in (0.5, 6.0):
            t0 = time.time()
            TE, TM = scan(lams, th, gap, n_terms=80, ngrid=96)
            print(f"gap={gap} th={th}: min T_TE at {lams[TE.argmin()]:.4f} ({TE.min():.3f}), "
                  f"min T_TM at {lams[TM.argmin()]:.4f} ({TM.min():.3f})  [{time.time()-t0:.1f}s]", flush=True)
