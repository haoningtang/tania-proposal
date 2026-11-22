# T15: twist response of the square prelim bilayer, rcwa4d-mf (GPU), normal incidence, gap 200 nm

- Spectra 1480–1580 nm (1 nm; 0.5 nm in `explore/`) of T_x, T_y, T_σ± (all transmitted orders incl. moiré) and the zero order alone, N = 5 at θ = ±0.1, ±0.25, ±0.5, ±1, ±2, ±4°
  (+0.9, 1.1°, gap 195/205 at 1°); N = 3, 4, 5, 6 at θ = 0.1° and 1°. Energy |R+T−1| ≤ 4e-11, |T_x − T_y| ≤ 4e-12 (C4). `table.csv`, `analysis.json/png`.
- **Parity holds exactly:** max|T_x(θ) − T_x(−θ)| ≤ 3e-12, max|CD(θ) + CD(−θ)| ≤ 5e-12 at every |θ| (λ, Q, T even; CD odd), as the mirror requires.
- **λ(θ → 0) does not approach the aligned 1506.5 nm.** No single line survives; the spectrum is a broad band 1505–1580 nm (mean T 0.71) at every θ from 0.1° to 4°,
  nothing like the aligned dip (T → 0 at 1506.6 nm). It matches the aligned spectrum averaged over all lateral shifts (`stack_avg.png`: fmmax 80/96, 16×16 shifts; the aligned
  resonance moves 1508 → 1563 nm from (0,0) to (a/2,a/2)). The RMS distance to that average falls with N: 0.061 / 0.040 / 0.030 / 0.034 (N 3/4/5/6 at 1°), against ~0.2 to the aligned spectrum.
  Reading: the moiré period a/θ (36 µm at 1°, 355 µm at 0.1°) is far longer than the mode's propagation length, so a plane wave sees every stacking at once. The θ → 0 limit is the stacking
  average, discontinuous at θ = 0. Hence d²λ/dθ², d²Q/dθ² "at the aligned state" are not defined for a plane wave on an infinite twisted bilayer (AAA-tracked poles switch lines; fits in analysis.json are not meaningful).
- **CD:** band-mean CD at N 5 is 1.4e-4 (0.1°), 1.4e-4 (0.25°), 2.5e-4 (0.5°), −0.7e-4 (1°), 1e-5 (2°), −1e-4 (4°); the peak CD of sharp lines is 5.8e-3 … 6.9e-2 (4°) and grid-sensitive.
  **Not converged in N:** at 1°, band CD 5.1e-4 / −0.7e-4 / −0.7e-4 / −1.3e-4 and peak CD −0.026 / −0.010 / −0.025 / −0.010 (N 3/4/5/6); at 0.1°, band CD 1.4e-4 / 0.6e-4 / 1.4e-4 / −0.05e-4.
  So dCD/dθ at 0 cannot be extracted: the N = 5 value stays finite as θ → 0⁺, but N = 6 drops it 30×, consistent with CD → 0 (each shifted stacking is inversion-symmetric, and the
  stacking-average CD is 0 exactly). The zero order alone has larger CD (up to 0.10 at 4°); helicity-dependent power goes into the moiré orders.
- (gap, twist) Jacobian at 1° (N 5, ±5 nm, ±0.1°) on band observables (extinction centroid λ_c ≈ 1546 nm, width ≈ 22.4 nm, band CD, integrated extinction): σ = 2.0e-2, 3.7e-3 (normalized), cond 5.5.
  dλ_c/dgap = 0.058 nm/nm (aligned line: 0.247). The twist column (e.g. dCD_band/dθ = 3.5e-5 /deg) is far below the N-truncation spread (5e-4), so **the twist control is not resolved at N ≤ 6**.
- Implication for the proposal (my reading): a first-order CD from twist at the aligned working point would need a device or beam much smaller than a/θ (D ≪ 36 µm/θ[deg]). That regime is a
  finite, locally rotated aligned bilayer, which plane-wave rcwa4d does not model. Not checked: N ≥ 7; other gaps; a finite-aperture model.
