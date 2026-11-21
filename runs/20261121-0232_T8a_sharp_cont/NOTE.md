# T8a: continuation from the T7a2 best, η 1/8000, S_t 1500 (configs/stage8a_sharp_continuation_from_T7a2.json)

- 120/128; gaps 200/320/500 nm; θ 0.5/3.5/6.5°; fd 3e-5; trust region ±3 % around the T7a2 best, lam_k ±0.3 %. L-BFGS-B
  converged after 65 it / 220 evals / 95 min. Smoothed loss 1.227 → 0.983 (flat after eval ~45). No variable on a bound.
- Best: a 729.7, t 279.4, r 242.4, c4 2.2, c8 −0.5, r2 239.4 nm; lam_k 1520.5 / 1548.8 / 1572.5 nm; tune 3.3 %.
- S at real λ (0.5/3.5/6.5°), start (= T7a2 best) → best: gap 200 TE 411/215/24 → 700/111/24, TM 401/650/494 → 671/732/558;
  gap 320 TE 517/599/556 → 588/705/697, TM 518/602/753 → 591/1295/348; gap 500 TE 955/938/903 → 3092/2961/2618,
  TM 981/1314/588 → 3153/2777/895.
- analyze.py M (Q at 0.5°), 120/128 | 200/192: gap 200 TE pole only to 3° (Q 390 | 439), TM −5.1 | −6.3 (Q 380 | 427);
  gap 320 TE −7.0 | −6.7 (Q 304 | 336), TM −3.4 | −3.7 (Q 304 | 337; was −57 | +16 in T7a2); gap 500 TE −902 | −346
  (Q 2.0e3 | 1.9e3, flat to 10°), TM −9.4 | −12.2 (Q 2.0e3 | 1.9e3). λ shift between resolutions ≤ 1.1 nm, Q +5–15 %.
- Verdict: **not met**. Gap 500 is much sharper and nearly flat for both pols. Gap 320 TM got worse and gap-200 TE is unchanged
  (the line leaves lam_k after 3°). The trade between gaps suggests the 6-variable design cannot hold TE flat at gap 200.
