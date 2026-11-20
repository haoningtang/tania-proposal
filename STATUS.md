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
| 2026-11-20 | runs/20261120-1026_stage2_step1 | analysing | T3 step 1 (0.3 %): 80 it / 120 evals; loss 0.986 → 0.766, dip 0.043, side 0.944 → 0.724, tune 2.28 % |
