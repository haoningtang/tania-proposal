# Polarization names: which code uses which (2026-11-22)

**Physical names used from now on:** TE (s) = E perpendicular to the plane of incidence; TM (p) = E in the plane of incidence.

## Evidence (Brewster angle, uniform Si slabs n = 3.48, θ_B = atan(3.48) = 73.97°, λ 1550 nm; physical TM must give T = 1)

| code | input | T at θ_B | so this input is |
|---|---|---|---|
| `inverse/model.py` (fmmax) | key `TE` | 0.999996 | physical **TM** |
| `inverse/model.py` (fmmax) | key `TM` | 0.153 | physical **TE** |
| prelim grcwa (`prelim/code/lib.py`) | `pol='p'` | 1.000000 | physical **TM** (standard name) |
| prelim grcwa (`prelim/code/lib.py`) | `pol='s'` | 0.166 | physical **TE** (standard name) |

The worker found the model.py swap first (`inverse/check_pol_labels.py`: Brewster, sub-wavelength stripes, and the fmmax source, whose amplitude
blocks are (−E_y, E_x), not (E_x, E_y)). The controller repeated the Brewster test for model.py and ran it on the prelim grcwa code.
So the earlier instruction "grcwa `pol='p'` is TE" was wrong: grcwa uses the standard names, and model.py was written to match the wrong rule.

## Rule for every run made with model.py before task T20

**key `TE` = physical TM (p); key `TM` = physical TE (s).** Shift directions, lattice orientation and azimuths are not affected (the permittivity grid
axis 0 is x). Powers and λ, Q, M values are unaffected apart from the names. rcwa4d-mf runs (T15, T15b, T15c, T19a) do not use model.py; its x/y
convention is checked in T20.

## Statements that change (physical names)

- **Prelim square bilayer: the flat branch is TM (p), the curved branch is TE (s).** (It was called "flat TE, curved TM".)
- T9b best: 5 of 6 |M| ≥ 10 at azimuth 0; the one that fails is **TM at gap 260 nm** (|M| ≈ 3).
- T13c: the band whose curvature crosses zero (gap 81.85 nm, M ≈ 7700) is **TM**; the "cross" angle map is TM, the central spot is TE.
- T12a/T12b/T16a/T16b (hex): on the E1 lines it is **TE** whose curvature never flips (|M_TE| ≤ 4.2); TM reaches |M| ≈ 5–7.
- T18b: panels (a, b) use the TM line of T9b (TE within 0.5 %); panels (c, d) use the curved **TE** band of the prelim structure.
- T18a item 5 and T13a/T13b/T17a: the statements are symmetric in TE/TM or are about λ and rank; only the labels swap.

The proposal figures in `docs/figs` (and the PI's "提案用图" folder) were relabelled on 2026-11-22: T9b_square_best, isotropy_square_vs_hex,
C_prelim_symmetry_rank, T18b_tilt_wedge, T13c_angle_maps (replotted from maps.json).

## T20 fix (2026-11-23, worker): model.py keys are physical from now on

- `inverse/model.py` now returns **physical** keys: `TE` = s, `TM` = p (`POL_KEYS = "physical"` in the module). The change is a pure rename: new `t_TE` =
  old `t_TM` exactly (same amplitude and sign), new `t_TM` = old `t_TE`, new `t_TE_TM` = old `t_TM_TE` (checked: difference 0.0 at three (θ, azimuth, shift)
  points). Brewster test now gives key T_TM = 1.000000. The prelim analysis (T1 setting, 120/128) reproduces T1 with names swapped: key TM M 31.478, key TE M 0.594.
- **Rule for old run folders:** every result written with model.py **before 2026-11-23 13:00** (all `runs/` folders dated up to 20261122-*, and
  20261122-1735_T16c_hex_r3) uses the OLD, swapped keys: stored key `TE` = physical TM. Folders from `20261123-1310_T20_pol_keys` on use physical keys.
  Files that carry `"pol_keys": "physical"` (hex_r3_scan.py from now on) say so explicitly; files without that field are old. `hex_r3_analyze.py` reads both.
  `lpa_shift_map.py` stores the same J as before (model blocks (−E_y, E_x) → physical x, y at merge), so T19b data are unaffected.
- **rcwa4d-mf x/y convention** (`inverse/check_pol_rcwa4d.py`, stripes, λ = 5a): `solve_lab_basis` x and y are the lab x and y (no block swap);
  E along the stripes (y) gets the larger phase (−2.09 vs −0.63 rad relative to air; negative = exp(+iωt)). So σ± = (x ± iy)/√2 as used in T19a/T19c
  is in the lab basis, and with exp(+iωt) and transmission towards −z, σ+ is positive helicity (BOARD 2026-11-23 07:58).
