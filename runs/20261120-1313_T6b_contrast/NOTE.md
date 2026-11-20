# T6b: contrast objective from the original start (configs/stage6b_contrast_from_init.json, unchanged)

- n_terms 120, ngrid 128; gaps 200/260/320 nm; thetas 0.5/5/10°; δ 0.2 %; trust region ±10 % (lam ±1 %); r2 = r − 10 nm;
  init_lams 1502/1520/1526 nm. L-BFGS-B **converged** after 48 iterations / 101 evals / 46 min.
  Loss 1.001 → 0.692: mostly the tuning term (tune 1.58 → 3.19 %); dip 0.193 → 0.197; contrast deficit 0.600 → 0.495.
- Best: a 659.7, t 234.0, r 270.6, c4 −10.0, c8 −10.0, r2 259.6 nm; lam_k 1492.6 / 1535.2 / 1541.3 nm. **Every design
  variable is on a trust-region bound** (a, t, c4, c8 lower; r, r2 upper), and lam1, lam2 on their upper lam bound.
- spectra.png: featureless background at all gaps (T 0.19–0.25 at lam_k, TE = TM at 0.5–10°); only TM at 6° shows a
  Fano line ~1475–1485 nm. analyze.py: no pole at any gap at 120/128 or 200/192.
- Verdict: **not met**. Same plateau as T6a: with no resonance, side ≈ dip, deficit ≈ c0 = 0.5 and flat, and the
  remaining terms (dip, tune) drive the design to the box corner.
