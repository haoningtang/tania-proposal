# Status

One line per run, newest at the bottom: `date | runs/ folder | state (running/done/failed) | headline number`.

| date | run | state | headline |
|---|---|---|---|
| 2026-11-19 | prelim/ (grcwa, cloud CPU) | done | TE flat-band path 2.6 %; R ≈ 1300 with M ≈ 12; TE+TM flat single slab at Q ≈ 37 |
| 2026-11-19 | runs/smoke_cpu (cloud CPU, tiny) | done | optimizer runs, gradients flow; not a design |
| 2026-11-19 | runs/20261119-1748_validate | done | prelim gap 200: TE M 31.5 / TM M 0.594 (nt120); 31.7 / 0.597 (nt200); ~40 s per stage-1 evaluation |
| 2026-11-19 | runs/20261119-1807_stage1 | done | stage 1 NOT met: loss 0.724, no dip at lam_k (T ~ 0.85); poles Q 11-17 only |
| 2026-11-19 | runs/20261119-2020_stage1_r2 | stopped | fallback r2: stopped at 106 evals (loss 0.783, dip 0.157); r2 stayed = r |
| 2026-11-19 | runs/20261119-2116_stage1b | running | T2b stage 1b (trust region, start on dips) |
