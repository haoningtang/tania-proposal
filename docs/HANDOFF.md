# Handoff: inverse design for the ARO proposal (MEMS-reconfigurable moiré photonics)

Written by the cloud session, 2026-11-19. Read this once before the first run.

## 1. What the proposal claims

Two Si photonic-crystal membranes stacked with a MEMS-controlled gap, lateral shift and twist. Tunable filters
normally obey "narrower passband ⇒ smaller acceptance cone": an air-gap Fabry–Perot (FP) with a 1 nm window at
1550 nm accepts only ±2°. A **flat band** removes this: the resonance wavelength does not change with angle.

Figure of merit: **M = Ω·R / 2π** (etendue × resolving power; air-gap FP = 1). From the band curvature,
Δλ/λ = −sin²θ / (2M). A planar cavity with 30 % travel can reach M = 10 only with 0.6 % tuning, and cannot reach
M ≥ 12 at all.

**Targets in the proposal (fixed; do not lower them):**

| step | target |
|---|---|
| A1 | sweep the gap through a flat point (band curvature changes sign) on one device |
| A2 | both TE and TM flat, all azimuths; 1 nm window (R ≈ 1550); ±6.5° (M ≥ 10); tunable ≥ 2 %; ≥ 70 % peak transmission without polarizers |
| A3 | moiré colour ruler (twisted), later |

## 2. What is already computed (prelim/, grcwa, nG = 81, incidence plane along a lattice axis)

| result | structure | numbers | figure |
|---|---|---|---|
| gap sweeps curvature through zero | aligned bilayer, a = 620, t = 220, r = 120 nm | TE flat point between gap 80 and 85 nm; at 85 nm the resonance moves < 0.05 nm up to 10° | Fig A (a,b) |
| gap + shift keep the band flat while tuning | same | TE: 1457 → 1495 nm (2.6 %), \|M\| ≳ 100 along the path, Q 155–184 | Fig A (c) |
| narrow linewidth | same, r = 62 nm | TE: R ≈ 1260–1380, M ≈ 12, 82 nm (5.2 %) tuning, gap 60 → 200 nm | Fig B |
| both polarizations flat | single slab, r/a = 0.336 | TE and TM both shift < 1 nm up to 10°, but Q ≈ 37 at 1.31 µm | Fig C |
| bilayer, both pol. | r/a = 0.336, gap 200 nm | Q ≈ 123, TE M ≈ 16, TM \|M\| ≈ 11 (one point only) | — |

The fmmax model in `inverse/` reproduces the grcwa numbers: gap 200 nm, r = 120 nm gives TE λ = 1506.6 nm,
Q = 162, M = 30 and TM M = 0.58 (grcwa: 1505.6 nm, Q = 162, M = 31 and 0.59).

**What is missing (your job):** no single structure yet has all of: TE and TM flat, R ≈ 1550, gap ≥ 200 nm, ≥ 2 %
tuning. The flat point at 80–85 nm gap is too small for the PI's MEMS; designs must work at gaps ≥ 200 nm.

## 3. Method (Steven Johnson's advice; keep to it)

- Optimize a **response**, not eigenvalues: `inverse/optimize.py` asks for a transmission dip at the same λ_k for
  every angle and both polarizations, and high transmission at λ_k ± δλ. No pole tracking inside the loop.
- Use **L-BFGS-B** (deterministic problem), not Adam.
- High Q makes a knife-edge landscape (curvature ∝ Q²). **Continuation:** reach flatness at moderate linewidth first
  (stage 1, δλ/λ = 0.6 %), then narrow step by step (stage 2: 0.3 % → 0.1 % → 0.04 %), each run starting from the
  previous best.
- Keep symmetry: the C4v hole keeps TE and TM degenerate at normal incidence. Break it only on purpose.
- After optimizing, measure the bands with `inverse/analyze.py` (pole fitting, outside the loop).

## 4. Task list (in order)

1. **Set up and validate** (≈ 30 min). Install, confirm `jax.devices()` shows the GPU, run
   `python inverse/check_vs_grcwa.py`, and `python inverse/analyze.py --params '{"a":0.62,"t":0.22,"r":0.12}' --states '[{"gap":0.2}]' --lams '[1.508]' --out runs/<stamp>_validate --thetas '[0.5,3,6]'`.
   Expect TE M ≈ 30, TM M ≈ 0.6. Check convergence at `--n_terms 200`.
2. **Stage 1**: `python inverse/optimize.py --config inverse/configs/stage1_bothpol_flat.json --out runs/<stamp>_stage1`,
   then `analyze.py --run runs/<stamp>_stage1`. Goal: TE and TM |M| ≥ 10 at all three gaps (200–320 nm), tuning ≥ 2 %.
3. **Stage 2**: copy `stage2_narrow.json`, set `init_from`, run with half_window_frac 0.003, then 0.001, then 0.0004.
   Goal: R ≈ 1500 while keeping stage-1 flatness.
4. **If stuck** (loss plateaus, TM will not flatten at R > 300), try in this order and report each:
   different radii in the two slabs (`r2`), thickness as a free variable (already on), lateral shift as a design
   variable per state, a hexagonal lattice (needs a model change), more angles (0.5, 3, 6, 9°).
5. **Write `docs/RESULTS.md`**: a table of the best design per stage (parameters, λ, Q, M for TE and TM at each gap,
   tuning), its analysis figure, and what is still short of the targets.

## 5. Known limitations of the model

- Only the incidence plane along a lattice axis is computed. "All azimuths" needs a check along the diagonal
  (add `azimuth` to `model.py`; the in-plane wavevector is (k cos φ, k sin φ)).
- Infinite, lossless, suspended slabs; no substrate, no fabrication disorder.
- The optimized quantity is a transmission **dip** (notch). The proposal also needs a **passband**; that is a later task.
