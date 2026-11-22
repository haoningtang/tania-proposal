# T13a: Jacobian of the prelim square bilayer (a 620, t 220, r 120 nm, gap 200 nm), `inverse/jacobian.py`, CPU, 80/96

- Controls gap, shift x, shift y (slab 2, in nm; `shift_y` passthrough added to `analyze.scan`), central differences ±5 nm, at (δx, δy) = (0, 0) and (20, 20) nm.
  Observables: the two 0.5° modes λ_lo, λ_hi and their Q (merged from TE and TM fits, sorted; aligned: lo = TM, hi = TE), and TE/TM curvature
  c = (Δλ/λ)/sin²θ from the 3° and 6° poles. Normalized table: Δλ/λ, ΔQ/Q, Δc, each per nm (analysis.png/json).
- **Aligned: rank 1.** Only the gap acts: dλ/dgap = 0.247 nm/nm (both modes), dQ/dgap = 0.163 /nm, dc_TM/dgap = −4.2e-4 /nm, dc_TE/dgap = −3.3e-5 /nm.
  The shift columns are ≤ 3e-10 (noise floor), as T13b predicts. σ = 1.5e-3, 2.5e-10, 3.9e-12.
- **Biased (20, 20): rank 3** (σ = 1.47e-3, 5.7e-4, 1.1e-4; rtol 1e-2). dλ_lo/dδx + dλ_hi/dδx = 0.037 nm/nm and the same for δy, matching T13b (2kδ = 0.035).
  The two 0.5° modes are split by 0.20 nm (diagonal eigenmodes, seen in both polarizations). With the wavelengths alone σ = 2.3e-4, 1.1e-5
  (2 controls, the second 20× weaker); the third direction comes from Q and c_TM (dc_TM/dδx = −5.2e-4 /nm vs dc_TM/dδy = +1.7e-5).
- Caveats: rank depends on the row scaling (relative λ and Q, absolute c); the 0.20 nm mode splitting is 2 % of the linewidth (9.3 nm, Q 162),
  so λ_lo/λ_hi are separable in a fit, not by eye. v1 (`jacobian_v1_nearest_pole.json`) took the pole nearest a fixed guess and swapped modes
  between states at the biased point; superseded.
