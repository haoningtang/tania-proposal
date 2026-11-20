# T6a: contrast objective from the T3 best (configs/stage6a_contrast_from_T3.json)

- n_terms 120, ngrid 128; gaps 200/320/500 nm; thetas 0.5/5/10°; δ 0.2 %; trust region ±10 % (lam ±1 %); r2 = r − 10 nm.
  init_lams 1522.74 / 1547.46 / 1569.11 nm (runs/20261120-1217_T6a_init_lams). L-BFGS-B **converged** after 16 iterations /
  50 evals / 22 min (relative reduction ≤ factr). Loss 1.011 → 0.662: dip 0.308 → 0.159, contrast deficit 0.703 → 0.503.
- Best: a 797.3, t 311.0, r 221.0, c4 −8.5, c8 −0.4, r2 213.8 nm; lam_k 1507.5 / 1539.1 / 1554.8 nm (tune 3.1 %).
  **On trust-region bounds:** t (upper), r (lower), c4 (lower), lam0 (lower); a near its upper bound (801.4).
- spectra.png: the best design has **no resonance** near lam_k for 0.5° (smooth background, T 0.10–0.29 at lam_k, TE = TM);
  only TM at 6° shows Fano lines. analyze.py finds no pole at any gap, at 120/128 and at 200/192.
- Why: the optimizer found the plateau "featureless background": side ≈ dip, so deficit ≈ 0.5 with ~zero gradient, and
  lowering the background lowers the dip term. The start made this easy. At gaps 200 and 500 lam_k sat on the pole, which
  is a Fano **peak** (T 0.61 / 0.84 at lam_k), so contrast started negative and removing the resonance was a descent
  direction. Gap 320 started with a real dip (T 0.002) but it was lost when the first step moved a to +10 %.
- Verdict: **not met**. Not checked at 45° (no resonance to check).
