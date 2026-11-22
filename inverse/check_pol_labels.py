"""Check of the TE/TM labels of model.py (2026-11-22, worker). Three independent tests:
1. Brewster: uniform slab n 3.48 at theta_B = atan(3.48) = 73.97 deg must give T = 1 for TM (p, E in the plane of incidence).
2. Stripes (eps varies along the first grid axis = u = x), lambda >> period: E parallel to the stripes (y) sees the larger index.
3. fmmax source: fields_from_wave_amplitudes splits the field vector as (-ey, ex, hx, hy): amplitude block 0 is -E_y, block 1 is E_x.
Usage: JAX_PLATFORMS=cpu python check_pol_labels.py"""
import cmath, numpy as np, jax.numpy as jnp
import model

thB = float(np.degrees(np.arctan(3.48)))
for az in (0.0, 90.0):
    o = model.bilayer_t([1.5], thB, 0.62, 0.3, -0.1, None, n_terms=9, ngrid=16, azimuth_deg=az)
    print(f"Brewster {thB:.2f} deg, azimuth {az:g}: key T_TM = {float(o['T_TM'][0]):.6f}, key T_TE = {float(o['T_TE'][0]):.6f}"
          "   (physical TM must be 1)")
orig = model.hole_eps
def stripes(r, a, n_slab, ngrid, **k):
    x = (np.arange(ngrid) + 0.5) / ngrid
    F1, _ = np.meshgrid(x, x, indexing="ij")
    return jnp.asarray(np.where(F1 < 0.5, n_slab ** 2, 1.0))
model.hole_eps = stripes
o = model.bilayer_t([3.0], 0.0, 0.3, 0.1, 0.1, None, n_terms=25, ngrid=64)
model.hole_eps = orig
print(f"stripes along y (eps varies along x), normal incidence: phase of key t_TM (block 0) {cmath.phase(complex(o['t_TM'][0])):.3f}, "
      f"key t_TE (block 1) {cmath.phase(complex(o['t_TE'][0])):.3f}   (E_y, parallel to the stripes, must have the larger phase)")
