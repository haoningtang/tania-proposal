# T12a: hex bright-doublet survey (`inverse/hex_bright_survey.py`, `configs/stage12a_hex_bright_survey.json`, `--qmin 30 --pair_tol 0.0005`)

- 80/96, θ 0.5°, azimuth 0, 1420–1680 nm at 1 nm, gaps 260/380/500, AAA in 70 nm windows, no Q cap. **29/60 designs** (a 850, a 800, 5/12 of a 750);
  stopped because the GPU was shared (one gap > 1 h) and the criterion was met (see BOARD 21:25). Coarse cross-gap matching proved unreliable (a 1603 nm line
  turns into a Q 2.8e5 near-BIC), so the tuning is from **following** each line in 60 nm gap steps (`follow/`); 12/34 bright pairs followed (most promising first).
- Best: **a 850, r/a 0.25, t 280** (r2 = r, t2 = t): one smooth TE/TM line (Δλ ≤ 0.05 nm) at 1477.9 / 1498.6 / 1509.0 nm (gaps 260/380/500), Q 111 / 133 / 102,
  **tuning −2.08 %**. Next: −1.38 % (a 850 r/a 0.20 t 220, 1557 nm, Q 54–88), −1.34 %, −1.14 %, −1.13 %; all others < 1 %. Tuning falls with a.
- Isotropy (`iso/`, hex_isotropy at θ 0.5/3/6°): best line, M at azimuth 0° / 30°: TE 4.72/4.86, 5.34/5.36, 4.89/4.95 and TM 1.07/1.06, 1.13/1.12, 1.04/1.04
  (gaps 260/380/500). Second line (gap 380): TE 4.12/4.15, TM 0.98/0.98. Both **E1-type**: TE stays on its own branch at both azimuths, |M| within 3 %.
- Meaning: criterion met (one E1 candidate with tuning ≥ 2 %, barely). But TM disperses like a plain FP (M ≈ 1) and TE has M ≈ 5, so T12b must flatten TM ~10×
  while keeping the tuning. Not checked: 200/192 resolution; designs a ≤ 750 (partly); 22 lower-ranked lines not followed.
