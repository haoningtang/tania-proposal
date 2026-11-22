import numpy as np
from scipy.interpolate import AAA


def poles(lams, t, lo, hi, max_terms=12):
    A_ = AAA(1 / np.asarray(lams), np.asarray(t), rtol=1e-6, max_terms=max_terms)
    out = []
    for p, rz in zip(A_.poles(), A_.residues()):
        if p.real <= 0 or p.imag == 0:
            continue
        l0 = 1 / p.real; Q = p.real / (2 * abs(p.imag))
        if lo < l0 < hi and 10 < Q < 1e8 and abs(rz) / abs(p.imag) > 0.05:
            out.append((float(l0), float(Q)))
    return out


