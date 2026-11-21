# T9a: T8a best + second-slab thickness t2 (7 variables), η 1/8000, S_t 1500 (configs/stage9a_t2_from_T8a.json)

- 120/128; gaps 200/320/500 nm; trust region ±3 %, lam_k ±0.3 %. L-BFGS-B "converged" after **3 it / 16 evals / 7 min without
  moving**. The first trial steps went to loss 3.47 / 3.63 (eval 1–2), then 1.02 and back to the start. Best loss 0.9827 vs start 0.9828;
  every variable within 1e-6 of the T8a best (t2 = t = 279.4 nm).
- Diagnostic (`t2only/`, config `inverse/configs/stage9a_diag_t2only.json`): only t2 and lam_k free, the other 5 fixed at the T8a best.
  4 it / 35 evals: t2 = 271.0 nm (−3 %) → loss 3.20; t2 = 279.01 nm (−0.37 nm) → 1.10; back to t2 = 279.38 → 0.9827. So the point is a local
  minimum along t2 too. The smoothed loss changes by 0.12 for a 0.4 nm change of t2, because the Q ~ 300–2000 lines move with t2 off lam_k.
- Not analyzed again: the best design is the T8a best (analysis in runs/20261121-0232_T8a_sharp_cont, 45° in runs/20261121-0445_T7c_azimuth45).
- Verdict: **not met**. Adding t2 at the T8a optimum gives no descent direction at η 1/8000. A t2 study would need a start with t2 ≠ t
  (or a larger η first). Not tried: out of the task scope.
