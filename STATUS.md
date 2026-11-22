# Status

One line per run, newest at the bottom: `date | runs/ folder | state (running/done/failed) | headline number`.

| date | run | state | headline |
|---|---|---|---|
| 2026-11-19 | prelim/ (grcwa, cloud CPU) | done | TE flat-band path 2.6 %; R ≈ 1300 with M ≈ 12; TE+TM flat single slab at Q ≈ 37 |
| 2026-11-19 | runs/smoke_cpu (cloud CPU, tiny) | done | optimizer runs, gradients flow; not a design |
| 2026-11-19 | runs/20261119-1748_validate | done | prelim gap 200: TE M 31.5 / TM M 0.594 (nt120); 31.7 / 0.597 (nt200); ~40 s per stage-1 evaluation |
| 2026-11-19 | runs/20261119-1807_stage1 | done | stage 1 NOT met: loss 0.724, no dip at lam_k (T ~ 0.85); poles Q 11-17 only |
| 2026-11-19 | runs/20261119-2020_stage1_r2 | stopped | fallback r2: stopped at 106 evals (loss 0.783, dip 0.157); r2 stayed = r |
| 2026-11-19 | runs/20261119-2116_stage1b | stopped | T2b: process died at 18 evals; best loss 0.320 (dip 0.097, side 0.742, tune 2.00 %) |
| 2026-11-20 | runs/20261120-0910_stage1b_resume | done | T2b NOT met: loss 0.272, T < 0.2 at all lam_k (broad stop band, Q < 10); TE \|M\| ≤ 1.8, TM only gap 260 (M −3.4 / −5.9 hires) |
| 2026-11-20 | runs/20261120-1026_stage2_step1 | done | T3 step 1 NOT met: lam_k on broad band; TM-flat Fano Q 2.3/4.3e3 at gap 260/320 (hires, shift ≤ 0.1 nm to 6°), TE \|M\| ≤ 4; steps 2–3 skipped |
| 2026-11-20 | runs/20261120-1148_azimuth45 | done | T4 NOT met: at 45° TM \|M\| 11.8 (gap 260) / 4.7 (gap 320) / 0.8 (gap 200), TE lost after 3° (200/192) |
| 2026-11-20 | runs/20261120-1216_T5_convergence | stopped | T5 deferred by controller (12:10); stopped before any result |
| 2026-11-20 | runs/20261120-1217_T6a_init_lams | done | T6a init_lams 1522.7 (Q 1.2e3) / 1547.5 (Q 474) / 1569.1 nm (Q 192, nearest at gap 500) |
| 2026-11-20 | runs/20261120-1234_T6a_contrast | done | T6a NOT met: converged at 16 it, loss 0.662, no pole at any gap (resonances removed; t, r, c4, lam0 on bounds) |
| 2026-11-20 | runs/20261120-1313_T6b_contrast | done | T6b NOT met: converged at 48 it, loss 0.692, no pole at any gap; all design vars on trust-region bounds |
| 2026-11-20 | runs/20261120-2118_T7a_sharp | done | T7a NOT met: could not move (7 it, loss 1.159 → 1.132); 120/128 TM M −13.8/+12.3/−10.2, TE fails; hires stopped (closed by controller) |
| 2026-11-20 | runs/20261120-2156_T7b_sharp | done | T7b NOT met: 10 it, loss 2.361, box corner; TE poles Q 1e4–1.7e4 at 0.5° only (M ≤ 3.6); TM flat (M 16–23) but Q ~ 100, tuning 0.47 % |
| 2026-11-21 | runs/20261121-0014_T7a2_sharp_smooth | done | T7a2 NOT met (but moved, no bound hit): Q 300–800 at 0.5°, TE/TM degenerate, tune 3.3 %; \|M\| ≥ 10 only TE gap 500 (flat to 10°) and TM gap 320; gap 200 fails |
| 2026-11-21 | runs/20261121-0132_T7b2_sharp_smooth | done | T7b2 NOT met: box corner ≈ T7b; TE Q 1e4 at 0.5° only (M ≤ 6.5), TM flat M 16–22 but Q ~ 100, 0.47 % tuning |
| 2026-11-21 | runs/20261121-0232_T8a_sharp_cont | done | T8a NOT met: gap 500 Q 1.9e3, TE flat, TM M −9.4/−12.2 (120/128 / 200/192); gap 320 TE/TM M −6.7/−3.7; gap 200 TE lost after 3°, TM −6.3 |
| 2026-11-21 | runs/20261121-0445_T7c_azimuth45 | done | T7c NOT met: T8a best at 45°, \|M\| ≤ 3.6 at every gap, both pols (120/128 and 200/192); flat along x only |
| 2026-11-21 | runs/20261121-0523_T9a_t2 | done | T9a NOT met: no move from the T8a best (3 it, loss 0.983); t2-only check: t2 = t is a local minimum |
| 2026-11-21 | runs/20261121-0546_T9b_init_lams | done | T9b init_lams 1535.08 (Q 207) / 1558.36 (Q 653) / 1572.26 nm (Q 2.0e3); tuning 2.39 % |
| 2026-11-21 | runs/20261121-0556_T9b_gaps260 | done | T9b NOT met (closest): 5/6 \|M\| ≥ 10 at 0° (200/192): gap 260 TM −26, gap 380 TE −16 / TM −893 (Q 815), gap 500 TE −407 / TM +25 (Q 5.8e3); gap-260 TE −2.6, Q 220; tune 2.3 % |
| 2026-11-21 | runs/20261121-0740_T10a_iso | done | T10a NOT met: 200/192 \|M\| ≥ 10 at 0° 3/6, at 45° 1/6 (T9b start: 5/6, 1/6); 45° lines at gaps 380/500 still move 2–5 nm by 6° |
| 2026-11-21 | runs/20261121-1129_T11a_hex_survey | done | T11a hex: 3 degenerate pairs (a 850, t 280, Q 5–8e4); per-band isotropic (M within 2–8 %), TE/TM swap bands between az 0° and 30°; \|M\| ≤ 5.8; tuning 0.48 % (gaps 260–500) |
| 2026-11-21 | runs/20261121-1501_T12a_hex_bright | done | T12a met (barely): best E1 line a 850 r/a 0.25 t 280, 1478/1499/1509 nm, Q 102–133, followed tuning −2.08 %; M az 0/30: TE 4.7–5.4, TM 1.0–1.1 (within 3 %); 29/60 designs |
| 2026-11-21 | runs/20261121-2122_T13a_jacobian | done | T13a Jacobian (prelim, 80/96, ±5 nm): aligned rank 1 (gap only, dλ/dgap 0.247 nm/nm); biased (20,20) rank 3, σ 1.5e-3 / 5.7e-4 / 1.1e-4 (normalized); λ-only rank 2 |
| 2026-11-21 | runs/20261121-2124_T13c_angle_maps | done | T13c: TE zero curvature at gap 81.85 nm (M ≈ 7700); T(θx,θy) TE = cross (T 0 along axes to 10°, diagonal 0.70 at 4°); TM central spot; gap 200 same, lower contrast |
| 2026-11-21 | runs/20261121-2121_T12b_hex_sharp | done | T12b NOT met: converged near start (20 it); 200/192 M TE 5.1–6.7, TM 1.1–4.9 (az 0 and 30 within 10 %); Q 96/117/450; gap-260 λ_k moved to another line (1473.6 nm) |
| 2026-11-22 | runs/20261121-2330_T16a_curv_map | done | T16a NOT met: 7×7 (t2−t, r2−r) ±40 nm, 80/96; c_TM never 0 (M_TM 0.99–4.2 on 45 bright points); c_TE changes sign (mostly a line switch 1510↔1471 nm); closest (−40, 0): M_TE −6.0, M_TM 4.2, Q 97 |
| 2026-11-22 | runs/20261122-0036_T16b_sym_map | done | T16b NOT met: symmetric r/a × t 7×7, 80/96; c_TM < 0 on all 31 E1-doublet points (−0.55…−0.036, M_TM ≤ 3.2 except Q-17 point); partner within few nm halves \|c_TM\| but no sign change; closest (t 260, r/a 0.31) M_TE −5.4 / M_TM 3.2 |
| 2026-11-22 | runs/20261122-0400_T17a_bias_sweep | running | T17a: 6 bias points on CPU (3 × 10 cores, 2 points each); T15 setup (rcwa4d-mf clone + checks) on GPU |
