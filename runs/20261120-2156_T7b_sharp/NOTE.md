# T7b: objective "sharp" (no smoothing) from the original start (configs/stage7b_sharp_from_init.json)

- 120/128; gaps 200/260/320 nm; θ 0.5/3.5/6.5°; S_t 1000; trust region ±5 %, lam_k ±0.5 %. L-BFGS-B **converged** after
  10 it / 92 evals / 100 min (slow: a concurrent non-queue job shared the machine). Loss 2.897 → 2.361, tune 1.58 → 2.59 %.
- Best: a 768.9, t 272.8, r 233.7, c4 −1.7, c8 0.0, r2 224.3 nm; lam_k 1494.5 / 1513.2 / 1533.6 nm. On or at the trust-region
  bounds: r, r2 (lower), a, t (upper, within 0.1 %), lam0 (lower), lam2 (upper). Box corner again.
- S table (sharp_table.json, real λ, 120/128), start → best, TE/TM at 0.5/3.5/6.5°: start S 45–113 everywhere (broad dips).
  Best: gap 200 TE 139/211/577, TM 140/138/134; gap 260 TE 1000/204/106, TM 23/23/23; gap 320 TE 32/320/216, TM 24/24/24.
- analyze.py 120/128 (200/192 within 0.3 nm and 2 % in Q): **TE** grew sharp poles that are not flat. Gap 260: Q 1.7e4 at
  1513.5 nm, found only at 0.5°. Gap 320: Q 1.0e4 at 0.5°, then 282/104/124 and 1537 → 1531 nm by 6°, M 1.4. Gap 200:
  Q 97 → 1594, 1490.9 → 1493.4 nm, M −3.6. **TM**: one broad flat mode Q 96–106, M +22.6/+18.3/+16.3, at 1490.8/1494.4/1497.8 nm
  (tunes only 0.47 %, and 20–36 nm from lam_k at gaps 260/320). TE and TM are not degenerate at gaps 260/320.
- Verdict: **not met** (TE |M| ≤ 3.6; TM flat but Q ~ 100 < 300 with 0.5 % tuning). Unsmoothed log S drove it to a box corner
  where TE has narrow lines at 0.5° only. Not checked at 45°.
