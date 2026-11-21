# T7b2: objective "sharp" + smoothing η = 1/3000 from the original start (configs/stage7b2_sharp_smooth_from_init.json)

- 120/128; gaps 200/260/320 nm; θ 0.5/3.5/6.5°; S_t 500; trust region ±5 %, lam_k ±0.5 %. L-BFGS-B converged (projected
  gradient ≤ pgtol) after 36 it / 46 evals / 21 min. Smoothed loss 2.258 → 1.736; tune 1.58 → 2.59 %.
- Best: a 769.7, t 273.0, r 233.7, c4 −5.0, c8 0.9, r2 228.1 nm; lam_k 1494.5 / 1512.4 / 1533.6 nm. **Box corner:** a, t (upper),
  r, c4 (lower), all three lam_k on their bounds. Nearly the same design as T7b (unsmoothed).
- S at real λ (0.5/3.5/6.5°), start 45–113 everywhere → best: gap 200 TE 158/247/523, TM 158/156/151; gap 260 TE 1404/225/106,
  TM 24/24/23; gap 320 TE 347/423/197, TM 24/24/24.
- analyze.py M (Q at 0.5°), 120/128 | 200/192 (λ within 0.3 nm, Q within 1 %): TE gap 200 −6.1 | −6.5 (Q 101); gap 260 pole only
  at 0.5° (Q 1.45e4); gap 320 +1.4 | +1.4 (Q 1.0e4, moves 6 nm by 6°). TM: one broad flat mode, M +22.4/+18.2/+16.2, Q 100–115,
  at 1491/1495/1498 nm (tunes 0.47 %; 17–35 nm below lam_k at gaps 260/320).
- Verdict: **not met**, same failure as T7b. From the broad start, smoothing does not stop the run going to the box corner.
  Not checked at 45°.
