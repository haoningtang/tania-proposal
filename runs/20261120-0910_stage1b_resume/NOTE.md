# T2b stage 1b, resumed (configs/stage1b_resume.json)

- Resume of `runs/20261119-2116_stage1b` (stopped at 18 evals) from its best; same trust region (centred on the original
  init). n_terms 80, ngrid 96, gaps 200/260/320 nm, thetas 0.5/3/6°, probe ±1 %, w_side 0.3. 70 iterations (limit),
  114 evals, 44 min. Loss 0.320 → 0.272 (still falling at the end): dip 0.097 → 0.042, side 0.742 → 0.766, tune 2.03 %.
- Best: a 746.1, t 280.2, r = r2 246.1, c4 4.4, c8 0.3 nm (none on a trust-region bound; t closest, limit 286.0);
  lam_k 1497.8 / 1521.0 / 1528.6 nm.
- Dip check (`spectra.py`, 80/96): max T at lam_k over TE/TM and 0.5/3/6° = 0.084 / 0.159 / 0.027 → "T < 0.2 at every
  lam_k" is met. But `spectra.png` shows why: lam_k sit in a broad low-T band (T < 0.2 from ~1460 to ~1530 nm at 0.5°,
  TE = TM), not on a resonance. TE at 6° is a different spectrum (strong features moving by tens of nm), and lam_k sit
  on its slope (e.g. gap 260: T_TE 0.002 at 0.5°, 0.159 at 6°).
- analyze.py (pole fit): TE only finds sharp modes, Q 1.1–1.6e4, |M| 0.7–1.8; TM only at gap 260 (Q 84, M −3.4);
  none at 200/320. At 200/192 (`hires/`): TE Q 1.4–2.3e4, |M| 1.1–1.8 (gap 200 M NaN, mode hop); TM gap 260 Q 98,
  M −5.9. The broad band has Q < 10 and is excluded by the fit, so it has no M here.
- Verdict: **not met** (|M| ≥ 10 not shown for either polarization). Flatness of the broad band near normal incidence
  is real for TM, not for TE at 6°. Not checked: azimuth 45°, angles > 6° in the dip table.
