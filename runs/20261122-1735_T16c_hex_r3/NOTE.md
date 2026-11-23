# T16c — hex √3×√3 supercell (r1 at origin, r2 at the other two sites), PHYSICAL polarization names
- Run: 35 points (base row t 280 / gap 380 at Δ = (r1 − r2)/a ∈ {0, ±0.015, ±0.03, ±0.04, ±0.05, ±0.08}; Δ ∈ {0, ±0.05} at the 8 other (t, gap) pairs of
  t {240, 280, 320} × gap {340, 380, 420}), fmmax 240 terms / ngrid 160, θ 0.5/3/6°, azimuth 0 and 30°, Q-matched slope method (T16b). 172 bright lines in
  1450–1580 nm. The rest of the 81-point grid was skipped by decision (BOARD 18:02). r1 = r2 reproduces T12a (E1 1498.88 nm, Q 135).
- **Target (|M| ≥ 10 for TE and TM at both azimuths, i.e. |c| ≤ 0.05) is met at 0 of 35 points.** Closest line in 1450–1560 nm: the folded doublet at
  1467.8 nm (Δ 0, t 280, gap 420, Q 88): c_TE −0.16, c_TM +0.16, worst |M| 3.07, i.e. curvature ~3× too large in both polarizations. Outside the window,
  1572.0 nm (Δ 0, t 320, gap 420, Q 87) has worst |M| 3.66.
- E1 line: the supercell makes TM flat (|c_TM| ≤ 0.04 at |Δ| 0.04–0.05, t 280, gap 380–420; at t 240 and 320 c_TM stays −0.07…−0.21), but TE stays curved at every point (|c_TE| 0.31–0.81; best 0.31 at Δ +0.08,
  t 280, gap 380), so worst |M| ≤ 1.6 on E1. The TE-flat lines (e.g. 1466.3 nm at Δ −0.03, c_TE −0.02/+0.03) have c_TM 0.26–0.31.
  E1 and the folded ~1467 nm line stay 25–30 nm apart over the scan, so they never mix (answer to BOARD 18:33).
- Meaning: in this C6v supercell the Δ knob tunes only the TM curvature of E1, so no point has both polarizations flat; reaching the target needs a
  second knob acting on TE. Not checked: the 3× resolution spot check (no point near the target), Δ values other than above off the base row.
- Files: table.csv (all lines), analysis.json (best10, E1 per point), analysis.png (c_TM map), pts/ (per-point poles and slopes), config.json.
