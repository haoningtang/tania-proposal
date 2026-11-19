T1 validation (GPU: RTX 4090, JAX 0.12.1 CUDA, fmmax 1.7.1; other jobs share the GPU/CPU: atopt.py, mode_opt4.py).
- Prelim structure a=620, t=220, r=120 nm, gap 200 nm, thetas 0.5/3/6 deg:
  n_terms 120, ngrid 128: TE lam 1505.4 nm, Q 161, M 31.5; TM Q 161, M 0.594 (nt120/).
  n_terms 200, ngrid 192: TE lam 1504.9 nm, Q 161, M 31.7; TM M 0.597 (nt200/). Converged to < 1 %; matches grcwa (M 31 / 0.59).
- check_vs_grcwa.py (n_terms 80, ngrid 96): gap 200 nm dips at 1.508 um (TE, TM) at 0.5 deg; at 6 deg TE 1.507, TM 1.493 um, as in grcwa.
- Eigensolver is on the GPU (HLO calls cusolver_geev; batch of 8 complex 242x242: 1.7 s GPU vs 25.7 s CPU device).
- Stage-1 timing (n_terms 80, ngrid 96, 3 gaps x 3 angles x 3 wavelengths, value+grad): ~40 s per evaluation, 81 s for the first (compile). stage1_timing/.
- Fixed two bugs found here: model.py crashed when `a` is a design variable (fmmax basis built with numpy; now built on the unit lattice);
  optimize.py history key `t` (time) collided with thickness `t` (renamed to `wall_s`).
