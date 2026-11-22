# T15b: power per diffraction order of the twisted square prelim bilayer (rcwa4d-mf), normal incidence, gap 200 nm

- N 5 order spectra 1480–1580 nm (2 nm) at Δα = ±0.5, ±1, ±2, ±4, ±8°; at λ_res (largest-weight pole of T_x in 1495–1525 nm: 1506.7–1511.7 nm) and λ_res ± 10 nm for N = 3, 4, 5.
  Inputs x, y, σ± (σ+ = (x + iy)/√2). Orders: zero; the four first-order moiré orders ±(g1x − g2x), ±(g1y − g2y), found as |k∥|/k0 = 2(λ/a) sin(Δα/2); the rest. `table.csv`, `analysis.json/png`.
- **Angles:** the moiré orders leave at exactly the formula angle (1.217 / 2.436 / 4.870 / 9.766 / 19.887° at 0.5 / 1 / 2 / 4 / 8°, i.e. 2.43° per 1° of twist), azimuth rotated by Δα/2 from the lattice axes.
  This is geometry (the k-vectors), not a fitted result.
- **Efficiency at the resonance (N 5, x input):** the strongest single moiré order carries T = 3.3–5.0 % (0.5°: 4.0, 1°: 3.3, 2°: 4.0, 4°: 3.5, 8°: 5.0 %). Its mirror order (opposite azimuth) carries the same.
  The two perpendicular orders carry 0.01–0.2 %. All four together: T 7–10 %, R 12.5–15.7 %. Zero order T0 = 0.48–0.64; other propagating orders T 6–12 %, R 6–11 %.
  Circular input splits equally over the four orders (C4): 1.7–2.7 % each, σ+ vs σ− differing by up to 20 % relative at 8°. Exact parity: σ± swap under Δα → −Δα; x/y numbers are even.
- **Off resonance:** at λ_res − 10 nm the strongest order drops to 0.3–1.2 % (T0 0.89–0.97); at +10 nm it is 0.9–4.1 % (the band of moiré-coupled lines extends to ~1560 nm).
- **Not converged in N:** at 1°, strongest order 5.6 / 4.3 / 3.3 % and the four-order sum 11.3 / 8.6 / 7.0 % (N 3/4/5); at 8°, 2.4 / 2.5 / 5.0 %. Treat ±30 % as the uncertainty at N 5.
- Conclusion: the unoptimized structure sends ~3–5 % of the x-polarized light into one first-order moiré order (so, by reciprocity, it receives from that direction into normal incidence with ~3–5 %),
  the same into its mirror order, and leaves ~50–65 % in the zero order, with ~13–16 % reflected into the moiré orders. Not checked: N ≥ 6; λ grid finer than 2 nm; other gaps.
