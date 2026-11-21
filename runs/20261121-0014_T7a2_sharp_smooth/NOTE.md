# T7a2: objective "sharp" + frequency smoothing η = 1/3000 from the T6a start (configs/stage7a2_sharp_smooth_from_T3.json)

- 120/128; gaps 200/320/500 nm; θ 0.5/3.5/6.5°; S_t 500, fd 1e-4; trust region ±3 %, lam_k ±0.5 %. L-BFGS-B **converged** after
  35 it / 96 evals / 40 min. Smoothed loss 0.923 → 0.403 (most of it by eval 18); tune 3.0 → 3.3 %. **No variable on a bound.**
- Best: a 729.5, t 279.1, r 242.4, c4 0.5, c8 −0.8, r2 237.7 nm; lam_k 1521.3 / 1548.2 / 1572.7 nm.
- S at real λ (sharp_table.json, 0.5/3.5/6.5°), start → best: gap 200 TE 1335/16/35 → 411/216/24, TM 1293/1344/1032 → 401/648/493;
  gap 320 TE 301/350/216 → 516/597/555, TM 300/319/357 → 516/600/749; gap 500 TE 353/343/310 → 953/936/901, TM 598/319/279 → 978/1295/587.
  S ≥ 400 at 16 of 18 points (start 9 of 18). The failure left is gap-200 TE at 6.5° (S 24).
- analyze.py, M (Q at 0.5°), 120/128 | 200/192: gap 200 TE pole only to 3° (Q 381 | 428), TM −3.0 | −3.5 (Q 371 | 416);
  gap 320 TE −7.1 | −6.7 (Q 282 | 310), TM −57 | +16 (Q 282 | 309; sign flips, shift ≤ 0.6 nm to 6°, so flat within fit noise);
  gap 500 TE −2250 | −791 (Q 823 | 790; flat to 10°), TM −4.4 | −5.1 (Q 817 | 786; +2 nm by 6°). λ shift between resolutions ≤ 1.1 nm, Q +8–13 %.
- Verdict: **not met**, but the first run that improves at every gap without leaving the resonance: TE/TM degenerate at 0.5°,
  Q ≈ 300–800 (meets Q ≥ 300 at 200/192), tuning 3.3 %. |M| ≥ 10: TE gap 500 and TM gap 320 only. Not checked at 45°.
