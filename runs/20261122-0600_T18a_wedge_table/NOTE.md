# T18a: wedge-gap table, complex zero-order t(λ; g, θ), fmmax aligned bilayers, azimuth 0

- `table.json` (3.4 MB): 325 records at 80/96 + 25 at 200/192 (g = g0). One record per (structure, g0, g, θ, pol): `lam_nm[]`, `t_re[]`, `t_im[]`
  (co-polarized zero-order t), `fit{lam0_nm, Q, Gamma_nm, T_min, T_max, dlam_dg_nm_per_nm, flag_jump_post}`. Grid: λ0 ± 4Γ at Γ/20 (TE/TM union) + ±10 nm at 0.25 nm.
  Summary in `table.csv`; figure `analysis.png`. Tracking: from g0 outward in g, then in θ; no jumps after the fact (λ0 within 0.5Γ of a quadratic in g, Q smooth).
- **T9b g0 380** (θ 0.5°): λ0 1557.68 nm, Q 634 (Γ 2.46 nm), TE/TM within 0.004 nm; dλ/dg 0.147 nm/nm; Q 400 → 1120 over 350–410 nm. TE Q grows with θ (1470 at 8°), TM stays ~600.
  **T9b g0 500**: λ0 1571.63 nm, Q 6.9e3 (Γ 0.23 nm); dλ/dg 0.093 nm/nm; Q peaks at g ≈ 495 (7.1e3) and falls to 3.7e3 at 470/530. TE contrast collapses at 8° (T_max 0.26).
  **prelim g0 200 TM**: λ0 1506.49 nm, Q 162 (Γ 9.3 nm); dλ/dg 0.249 nm/nm; λ0 moves −23 nm from 0.5° to 8°.
- **200/192 at g0** moves the lines: T9b 380 −1.7 nm (Q 634 → 816), T9b 500 −2.1 nm (Q 6.9e3 → 5.8e3), prelim −1.7 nm (Q unchanged). The θ- and g-dependence is the same shape.
  For the wedge average use the 80/96 table and shift λ by the hires offset if absolute λ matters.
- **Item 5 (symmetry), prelim, gap 200, shift (20,20), θ ±2/4/6°:** per polarization max|T(+θ) − T(−θ)| = 0.7–7.3e-5 (co, cross and total, TE and TM input);
  for the TE + TM sum it is 3.7e-10 / 8.8e-10 / 2.8e-9 (numerically zero). TE_total and TM_total differences are equal and opposite. Reason: a laterally shifted pair of identical
  C2-symmetric slabs is inversion-symmetric about the midpoint between the hole centres; inversion + reciprocity give T_sum(+θ) = T_sum(−θ) for any shift.
  So the unpolarized ±θ signal is zero without tilt; per polarization it is ~1e-5 of the resonance contrast.
- Not checked: azimuths other than 0; 200/192 away from g0; the T9b 500 chain needed a lower AAA weight cut (0.005) at g 530, θ 6–8° (TE line weakening).
