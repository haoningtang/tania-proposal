# T13b: resonance wavelength vs lateral shift (controller, cloud CPU, `inverse/shift_symmetry.py`)

- Prelim square bilayer a 620 / t 220 / r 120 nm, gap 200 nm, fmmax 80/96, azimuth 0. Shift of slab 2 along x or y by ±5/10/20 nm; θ 0.5° and 6°.
- **λ is even in δ**: λ(+δ) − λ(−δ) ≤ 6e-6 nm for every case (fit precision), so ∂λ/∂δ = 0 at the aligned state (also Q).
- The even part is quadratic, Δλ = k δ²: shift along x moves **TM** (k = 0.88e-3 nm/nm², +0.35 nm at 20 nm) and TE only weakly (0.06e-3);
  shift along y does the reverse (TE 0.88e-3, TM 0.06e-3). Same at 6° (TM x: +0.25 nm at 20 nm; TE y: +0.35 nm).
- At 6° a shift of ≥ 10 nm along x also brings in a second TM line at ~1546 nm (a symmetry-protected mode made bright by the broken mirror).
- Meaning for the Jacobian (T13a): at the aligned state the shift columns are zero, so the rank there is set by the gap alone.
  Biased at (δx, δy) = (20, 20) nm, ∂λ_TM/∂δx ≈ 2k·20 = 0.035 nm/nm and ∂λ_TE/∂δy ≈ 0.035 nm/nm act on different polarizations,
  so gap + δx + δy can give independent columns there.
