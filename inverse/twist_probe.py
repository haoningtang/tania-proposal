"""Quick timing / sanity probe for T15 (rcwa4d-mf, square prelim structure)."""
import math, sys, time, torch, rcwa4d_mf
dev = "cuda"; torch.backends.cuda.preferred_linalg_library("cusolver")
a = 620.0
pat = rcwa4d_mf.Pattern(12.11, [(rcwa4d_mf.Circle((0.0, 0.0), 120 / a), 1.0)], device=dev)
for N in map(int, sys.argv[1:]):
    m = rcwa4d_mf.bilayer(pat, d=220 / a, gap=200 / a, twist_deg=1.0, N=N)
    f = torch.tensor([a / 1506.5, a / 1520.0], dtype=torch.float64, device=dev)
    z = torch.zeros_like(f)
    t0 = time.time(); x, y = rcwa4d_mf.solve_lab_basis(m, f, ux=z, uy=z); torch.cuda.synchronize()
    print(N, f"{time.time()-t0:.2f}s", "Tx", x.transmission.tolist(), "Ty", y.transmission.tolist(),
          "R+T-1", (x.transmission + x.reflection - 1).abs().max().item(), "shape", tuple(x.transmitted_e.shape), tuple(x.kz_transmission.shape), flush=True)
