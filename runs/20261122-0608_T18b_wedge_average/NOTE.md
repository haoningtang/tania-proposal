# T18b — tilt as a local average over a wedge gap (controller, no field solves)

**Run.** `inverse/wedge_postprocess.py --table runs/20261122-0600_T18a_wedge_table/table.json --out runs/20261122-0608_T18b_wedge_average --nx 121`
(cubic splines in sin²θ, the default), then `inverse/wedge_tables.py`. Input: the final T18a table (325 records at fmmax n_terms 80, ngrid 96; the 25 records
at 200/192 are not used). θ 0.5, 2, 4, 6, 8°; azimuth 0; gap g0 ± 30 nm in 5 nm steps (T9b g0 380 and 500 nm, TE and TM; prelim g0 200 nm, TM); 121 points
across the aperture. (A first pass on the controller's merge of the T18a chain files gave the same numbers to < 0.5 %.)
Figure: `docs/figs/T18b_tilt_wedge.png/.pdf` (`docs/figs/make_T18b_wedge_figure.py`). Numbers: `table_a.csv`, `table_bc.csv`, `wedge_average.json`.

**(a) Passband width and peak vs tilt (T9b best, normal incidence).** Tilt α (µrad) that widens the line by 10 % / 2×:

| line | Γ0, Q, dλ/dg (nm/nm) | D (µm) | α for 10 % wider: table / analytic | α for 2× wider: table / analytic |
|---|---|---|---|---|
| gap 380, TE | 2.46 nm, 634, 0.147 | 50 | 153 / 154 | > 200 / 581 |
| | | 100 | 76 / 77 | > 200 / 291 |
| | | 200 | 38 / 38 | 144 / 145 |
| gap 500, TE | 0.228 nm, 6900, 0.093 | 50 | 22.1 / 22.4 | 84 / 85 |
| | | 100 | 10.9 / 11.2 | 42 / 42 |
| | | 200 | 5.4 / 5.6 | 21 / 21 |

TM is within 0.5 % of TE. The width depends only on α·D (the gap difference across the aperture): 10 % at α·D = 7.6 nm (Q 630) and 1.1 nm (Q 6900),
2× at 28.9 nm and 4.2 nm. The analytic width agrees with the local average to 0.7 % at every α and D (the 10 % thresholds to 1–4 %, because the curve is flat
there). The analytic peak agrees to 0.3 % for Q 630, and to within 21 % for Q 6900 at the largest spread (α·D = 40 nm, W/Γ ≈ 16), where Γ
(0.22–0.42 nm) and dλ/dg (0.10–0.085 nm/nm) change across the wedge. The simple formula works because the average Γ over a symmetric wedge
stays close to Γ0, even though Γ changes by 2.8× across the gap-380 table (Q 400–1120 at gap 350–410). At α = 200 µrad and D = 100 µm the Q 6900 line is 8.3×
wider and its peak 0.18 of the untilted one.

**(b) Centre of the receive pattern (prelim, gap 200 nm, TM, λ = 1503.66 nm = blue half depth).** The pattern P(θ) is 0.50 at θ = 0, has a dark ring at
|θ| = 3.0° and rises to 0.85 at 8°. Its mirror centre is at α/2 for α = 0, ±20, ±50 µrad and D = 50, 100, 200 µm (10.00 and 25.01 µrad). This holds
exactly in this model (T is even in θ, so P(α/2 + u) = P(α/2 − u)); the check only confirms the code, not the physics.

**(c) Dither signal S(θ) = [P(θ; +αd) − P(θ; −αd)]/2 (same structure, λ).** S is odd in θ and zero at θ = 0. Slope at 0: 3.81×10⁻⁵ per degree for
αd = 10 µrad and 7.63×10⁻⁵ for 20 µrad (linear in αd; D = 50–200 µm within 0.3 %). |S|max = 1.05×10⁻⁴ (10 µrad) and 2.1×10⁻⁴ (20 µrad) at |θ| = 4.0°.
S also changes sign at the dark ring (±3.0°), so sign(S) = sign(θ) only for |θ| < 3.0°. S equals −(αd/2)·dP/dθ to 3×10⁻⁶: the dither measures the
slope of the receive pattern. Rough estimate (not solved; shot noise only, ideal detector): with 1 µW incident, αd = 10 µrad, θ resolution ≈ 0.01°/√Hz,
scaling as 1/(αd·√P).

**Model assumptions.** P(λ, θ; α) = ⟨T(λ, θ − α/2; g0 + αx)⟩ over x uniform in ±D/2 (PI). Each strip of the wedge is treated as a uniform bilayer with
the local gap; a real tilted slab also sees θ − α on top and θ below, and has gap gradients inside one period; neither is included. The 0.5° record is
used as normal incidence. (a) uses the Lorentzian of the resonance pole (λ0 and Γ from the fits at each gap), not the full |t|²: the T9b lines are Fano
lines (|t|² dip ≈ 3 nm from the pole at gap 380), so the background is not included. (b), (c) use the full |t|² of the table.

**Interpolation.** Between table angles: pole-aligned spectra and λ0 as natural cubic splines in s = sin²θ (leave-one-out on the prelim TM line: λ0
error 0.03–0.08 nm and |ΔT| ≤ 0.015, against 0.08–0.54 nm and ≤ 0.10 for the first, piecewise-linear version, which also put kinks into S at the table
angles). Between table gaps: shift-aligned linear mixing. The spline undershoots to −3×10⁻⁵ near the T ≈ 0 ring.

**Not checked.** Full-wave solve of a tilted (non-parallel) bilayer. Resolution: at 200/192 (T18a, at g0) every line moves by −1.7 to −2.1 nm and Q changes
634 → 816 (gap 380) and 6900 → 5800 (gap 500); the (a) thresholds scale as Γ/(dλ/dg), so they would move by about −22 % and +19 % (not recomputed). Azimuth ≠ 0; other wavelengths
on the pattern; the T15 twist route to moving the receive direction (that is T15b).
