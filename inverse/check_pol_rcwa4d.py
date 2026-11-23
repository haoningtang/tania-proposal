"""T20: x/y convention of rcwa4d-mf (solve_lab_basis), stripes test. Both layers: stripes (eps 12.11 for |x| < a/4, air elsewhere,
uniform along y), layer 2 rotated by a small twist (rcwa4d-mf refuses 0), lambda = 5 a (sub-wavelength, effective-medium regime).
E along the stripes (y) must see the larger index: n_par = sqrt(f eps + 1 - f) = 2.57, n_perp = 1.36 (f = 0.5).
Phase of the zero-order transmitted field relative to an all-air reference (same solver), so arg(t/t_air) = -/+ (n - 1) k d.
Usage: python check_pol_rcwa4d.py"""
import numpy as np, torch, rcwa4d_mf
from rcwa4d_mf import structured as st
dev = "cuda" if torch.cuda.is_available() else "cpu"
stripe = rcwa4d_mf.Polygon([(-0.25, -0.5), (0.25, -0.5), (0.25, 0.5), (-0.25, 0.5)])
pats = {"stripes": rcwa4d_mf.Pattern(1.0, [(stripe, 12.11)], device=dev),
        "air": rcwa4d_mf.Pattern(1.0, [(rcwa4d_mf.Circle((0.0, 0.0), 0.1), 1.0)], device=dev)}
d, gap, tw, N, f = 220 / 620, 200 / 620, 0.5, 3, 0.2
res = {}
for name, P in pats.items():
    m = rcwa4d_mf.bilayer(P, d=d, gap=gap, twist_deg=tw, N=N)
    fr = torch.tensor([f], dtype=torch.float64, device=dev); z = torch.zeros_like(fr)
    with torch.no_grad():
        x, y = rcwa4d_mf.solve_lab_basis(m, fr, ux=z, uy=z)
    i0 = [i for i, o in enumerate(m.orders) if tuple(int(v) for v in o) == (0, 0)][0]; j = i0 * m.nm + i0
    ex = x.transmitted_e[0, j].cpu().numpy(); ey = y.transmitted_e[0, j].cpu().numpy()
    res[name] = (ex, ey)
    print(f"{name:8s} x in: E_out {np.round(ex, 4)}   y in: E_out {np.round(ey, 4)}   Tx {float(x.transmission[0]):.4f} Ty {float(y.transmission[0]):.4f}")
px = np.angle(res["stripes"][0][0] / res["air"][0][0]); py = np.angle(res["stripes"][1][1] / res["air"][1][1])
k0d = 2 * np.pi * f * 2 * d
print(f"phase vs air: x input {px:+.3f}, y input {py:+.3f} rad; effective-medium estimate -(n-1) k0 (2d) [exp(+iwt)]: "
      f"x (perp) {-(1.36 - 1) * k0d:+.3f}, y (par) {-(2.57 - 1) * k0d:+.3f}")
print("PASS: x/y are lab x/y (E_y along stripes has the larger |phase|)" if abs(py) > abs(px) else "FAIL: x/y swapped")
