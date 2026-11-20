Stage 1 (configs/stage1_bothpol_flat.json; n_terms 80, ngrid 96; gaps 200/260/320 nm; thetas 0.5/3/6 deg; half_window_frac 0.006).
80 L-BFGS-B iterations, 137 evaluations, 94 min. Loss 0.994 -> 0.724 (dip 0.316 -> 0.458, side 0.679 -> 0.266, tune 5.6 %).
Best: a 795.6, t 285.9, r 200.5, c4 -2.8, c8 7.2 nm (none on a bound); lam_k 1512.4 / 1548.3 / 1598.9 nm.
NOT met: spectra.png shows no dip at any lam_k (T ~ 0.8-0.9 there at 0.5 deg). The optimizer raised the side term by moving off
resonance; the dip got worse. analyze.py finds no pole at gap 200 and only Q 11-17 broad features (with mode hopping) at 260/320,
so the M values in analysis.json (|M| < 6, and NaN) are not meaningful; same at n_terms 200, ngrid 192 (hires/).
The init design had broad TE=TM dips at 1502/1520/1526 nm (gap 200/260/320) that sit at the same lam at 0.5 and 6 deg, but the
config's init_lams (1530/1550/1570) were not on them, and the first L-BFGS step went to the box corner and never came back.
