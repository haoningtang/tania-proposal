# T17a: Jacobian (gap, δx, δy) → (λ_lo, λ_hi, Q_lo, Q_hi, c_TE, c_TM) along a bias sweep, prelim square bilayer, gap 200 nm

- Same as T13a (`inverse/jacobian.py`, 80/96, ±5 nm central differences, mode-sorted observables, θ 0.5/3/6°, azimuth 0), CPU 3 × 10 cores.
  New points (5,5) (10,10) (30,30) (40,40) (20,0) (0,20); (0,0), (20,20) taken from T13a. Table `table.csv`, `analysis.json`, `analysis.png`.
- **Diagonal bias: rank 3 from 5 nm on.** σ3/σ1 = 1.1e-2 (5 nm, cond 90, just inside rtol 1e-2), 1.7e-2 (10), 7.5e-2 (20, cond 13.3, best),
  6.3e-2 (30), 5.7e-2 (40). σ2 keeps rising (1.3e-4 → 1.0e-3), σ3 peaks at 20 nm (1.1e-4) and then drops slightly.
- **Single-axis bias: rank 2** ((20,0): σ3 1.6e-9; (0,20): 5.1e-10). That is symmetry, not noise: a bias along x keeps the y → −y mirror, so all
  observables are even in δy and ∂/∂δy = 0. A diagonal (two-axis) bias is needed for three controls. (20,0) and (0,20) differ (σ2 5.0e-4 vs 8.9e-5)
  because c_TE, c_TM are taken with the incidence plane along x.
- **Shift-noise cost:** λ̄ = λ0 + k|δ|² with k = 4.66e-4 nm/nm² (fit on the diagonal bases), and the Jacobian's |∇λ̄| agrees with 2k|δ| to ≤ 1.3 %:
  0.0066 nm/nm at (5,5), 0.026 at (20,20), 0.052 at (40,40) (linewidth 9.3 nm, Q 162). dλ/dgap 0.247 → 0.237 nm/nm from 0 to 40 nm.
  So (20,20) gives the best conditioning, and 1 nm of shift noise there moves λ by 0.026 nm (0.3 % of a linewidth, ~1/10 of dλ/dgap per nm).
- Not checked: 200/192 resolution; other gaps; step-size dependence of the small σ3 at 5 nm (h = 5 nm equals the bias there).
