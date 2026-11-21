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
| 2026-11-21 | runs/20261121-0132_T7b2_sharp_smooth | running | T7b2 converged after 36 it, smoothed loss 2.258 → 1.736, box corner; analysis running |
