# T19a (amplitudes) + T19c (analysis): twisted square bilayer at the aligned (AA) point, rcwa4d-mf, normal incidence
- Run (T19a): a 620, t 220, r 120, gap 200 nm; 70 λ in 1480–1580 nm (0.5 nm steps in 1500–1512.5). N 6 at θ ±0.25, ±0.5, ±1, +2°; N 7 at +0.25, +0.5, +1°;
  N 8 at +1° (3804 s). amps/*.npz: complex t, r (x, y, z) of every kept moiré order with labels and k. AA = twist axis = r = 0 (parity exact: CD(+θ) = −CD(−θ) to 1e-11).
  |R + T − 1| ≤ 7e-12 except N 7 at 0.5° (1.3e-7) and 0.25° (2.3e-4, not checked further). Helicity: solver is exp(+iωt), σ+ = (x + iy)/√2 = positive helicity.
- Definition: E(r) = Σ_m c_m e^{i q_m·r} over all kept orders, T_σ = |E_x|² + |E_y|² (normal-incidence power), CD = T_σ+ − T_σ−. Disc average over diameter D
  at AA via Σ c_m c_m'* 2J1(|Δq|R)/(|Δq|R) (`inverse/twist_aperture_cd.py`; D = 0 reproduces the point value). Main line = 1500–1512.5 nm.
- **Point CD_AA does not converge in N.** At 1°, main-line max |CD_AA| 0.093 / 0.009 / 0.010 at N 6 / 7 / 8, but N 7 − N 8 is up to 0.013 (as large as the value,
  with sign changes); off the line N 8 has ±0.09 at 1530–1540 nm where N 7 had < 0.01. N 7 at 0.5° and 0.25° gives spikes of 0.41 (1558 nm) and 0.16 (1538 nm)
  off the line. **No κ is quoted; |CD_AA| ≲ 0.01–0.015 on the main line for θ ≤ 1° is the bound at N ≤ 8.** The 1509–1512 nm features at N 6 were truncation artifacts.
- **Disc-averaged CD converges on the main line:** 1°, D 10 µm max 0.0060 (N 8) / 0.0062 (N 7); D 20 µm **+0.0178 at 1505.5 nm (N 8) vs +0.0175 (N 7)**.
  0.5° (N 7, N 6 − N 7 ≤ 0.005): D 10 / 20 / 50 µm 0.0015 / 0.004 / 0.014. 0.25° (N 7): 0.011 / 0.007 / 0.003, but N 6 − N 7 up to 0.04 at D 10 (not converged).
  D 20 µm at 1° is 56 % of the 35.5 µm moiré cell, so it averages over non-aligned stacking; it is not the "aligned-region-only" response.
- LPA (T19b n 48, band-limited to the kept harmonics, `inverse/twist_local_filtered.py`): CD_LPA(AA) = 0 exactly. rms ΔT over the cell and band 0.13–0.16 at the
  same λ for all (θ, N); with the 2 nm solver offset (07:58, N 6 only) 0.033 at 0.25° and 0.081 at 1° on the line, so the LPA holds at 0.25° (cell 142 µm) and
  fails on the line at 1° (cell 35 µm): mode propagation length is of order 10 µm. AA dip stays at 1505.5–1506.5 nm for 0.25–2° (N 6–8); the 1.3 nm offset to the
  80/96 fmmax line is fmmax resolution (1505.22 nm at 160/128).
- Meaning: first-order twist chirality at AA is below what rcwa4d resolves at N ≤ 8 for a point; for a device-sized aperture (D 10–20 µm) at θ ≤ 1° the
  main-line |CD| is ≤ 0.02 (converged at 1°). Not checked: N 8 at 0.25/0.5°, N 7 at 2°, the 0.25° energy error. Figures: analysis.png (1° map vs LPA, 07:39),
  analysis_T19c_conv.png (CD_AA and disc CD vs N at 1°; main-line |CD| vs θ).
