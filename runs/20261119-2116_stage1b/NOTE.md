# T2b stage 1b (partial) — stopped

- Ran `configs/stage1b_flat_first.json` (n_terms 80, ngrid 96, thetas 0.5/3/6°, gaps 200/260/320 nm). The process
  died after 18 evaluations (≈ 13 min, last write 2026-11-19 21:28); no done.json, no analysis.
- Best so far (eval 17): loss 0.320 (start 0.461), dip 0.097, side 0.742, tune 2.00 %; a 768.9, t 266.8, r = r2 241.3,
  c4 3.4, c8 0.2 nm; lam 1498.1 / 1521.0 / 1528.5 nm.
- The loss fell mainly by meeting tune 2 % (start 1.58 %); the dip got shallower (mean T 0.026 → 0.097) and side
  barely moved (0.754 → 0.742: the dips are still broad, as expected for flatness-first).
- Resumed from this best in `runs/20261120-*_stage1b_resume` with the same trust region (centred on the original init).
