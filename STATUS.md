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
| 2026-11-22 | runs/20261122-0400_T17a_bias_sweep | done | T17a: diagonal bias rank 3 from 5 nm (cond σ1/σ3 90 → 13.3 at 20,20 → 17.6 at 40,40); single-axis (20,0)/(0,20) rank 2 by mirror symmetry; |∇λ̄| = 2k|δ|, k 4.66e-4 nm/nm² (0.026 nm/nm at 20,20) |
| 2026-11-22 | runs/20261122-0420_T15_twist | done | T15: parity exact (≤ 5e-12); small-twist spectrum = stacking average of aligned shifts (rms 0.03 at N 5–6), not the aligned line → λ(θ→0) ≠ 1506.5; CD band-mean ~1e-4, not converged in N (N 6 at 0.1°: −5e-6); twist Jacobian column below truncation noise |
| 2026-11-22 | runs/20261122-0600_T18a_wedge_table | done | T18a: table.json 325 records (+25 at 200/192); T9b 380 Q 634 dλ/dg 0.147, T9b 500 Q 6.9e3 dλ/dg 0.093, prelim Q 162 dλ/dg 0.249; ±θ at shift (20,20): per pol ≤ 7e-5, TE+TM sum ≤ 3e-9 (inversion + reciprocity) |
| 2026-11-22 | runs/20261122-0700_T15b_moire_orders | done | T15b: moiré orders at sin θ = 2(λ/a) sin(Δα/2) exactly (2.43°/°); at resonance strongest order 3.3–5.0 % (x input, N 5), mirror order same, zero order 48–64 %; not converged in N (1°: 5.6/4.3/3.3 % for N 3/4/5) |
| 2026-11-22 | runs/20261122-0608_T18b_wedge_average | done | T18b (controller): wedge-gap local average; 10 % broadening at α·D = 7.6 nm (Q 630) / 1.1 nm (Q 6900), i.e. 76 / 11 µrad at D = 100 µm, analytic √(Γ²+W²) within 0.7 %; centre = α/2 (by construction); dither ±10 µrad: S odd, slope 3.8e-5/deg, sign(S) = sign(θ) for |θ| < 3.0°; figure docs/figs/T18b_tilt_wedge.png |
| 2026-11-22 | runs/20261122-0710_T15c_moire_conv | done | T15c: strongest moiré order (x, at λ_res / red band) 3.0–4.4 % at 1–4° for N 6–8 (converged ±5 %); 8°: 10.1 % at 1536 nm (converged), 6.3 % at λ_res (not converged); N 8: 47 s, 8.5 GiB per λ |
| 2026-11-22 | runs/20261122-1720_T19b_lpa_shift_map | done | T19b: LPA Jones map 16×16 shifts, 80/96; J symmetric (6e-9); CD_LPA = 0 at δ = 0 and on mirror lines but up to 0.24 at generic shifts (= 2 Im[(Jxx−Jyy)Jxy*], linear anisotropy on rotated axes); cell average 0 |
| 2026-11-22 | runs/20261122-1710_T19a_twist_maps | running | T19a: N 6 twists ±0.5, ±1, 2 (then N 7 at +1°, ±0.25°), GPU |
| 2026-11-22 | runs/20261122-1735_T16c_hex_r3 | running | T16c 18:02: 7/81 points (base row t 280 gap 380, 240/160). r1 = rb reproduces T12a (1498.88 nm Q 135 vs 1498.56/133). E1 line, PHYSICAL names: c_TM −0.095 (Δ 0) → +0.025 (Δ ±0.05), crosses 0 near |Δ| 0.045; c_TE stays −0.44…−0.48 (M ≈ 1.1). Refining Δ ±0.04 |
| 2026-11-22 | runs/20261122-1710_T19a_twist_maps | running | T19a 18:02: N 6 done at +1, −1, +0.5, −0.5; +2 running |
| 2026-11-23 | runs/20261122-1735_T16c_hex_r3 | running | T16c 07:12: jobs had died at 18:01 (session killed); 7/81 points done. Restarted (7 × 4 threads): base Δ ±0.04, ±0.08, then Δ {0, ±0.05} at the 8 other (t, gap) pairs (28 points, ETA ~10:00) |
| 2026-11-23 | runs/20261122-1710_T19a_twist_maps | running | T19a 07:12: N 6 done at ±0.5, ±1, +2 (2° finished 18:01). Restarted: N 6 at ±0.25°, then N 7 at +1° (GPU) |
| 2026-11-23 | runs/20261122-1710_T19a_twist_maps | running | T19a 07:55: N 6 done at ±0.25, ±0.5, ±1, +2°; N 7 at +1° running (GPU). T19b n 48 LPA map finished (325/325, merged; merged file 8.6 MB kept local, parts in git) |
| 2026-11-23 | runs/20261122-1735_T16c_hex_r3 | running | T16c 07:55: 14 points done (restart 07:12, 7 procs); ETA ~10:00 |
| 2026-11-23 | runs/20261122-1735_T16c_hex_r3 | running | T16c 10:42: WSL rebooted ~08:20 and killed all jobs (setsid cannot survive a reboot); 14 points done. Restarted the remaining 21 (Δ {0, ±0.05} × 8 (t, gap) pairs), 7 procs, ETA ~12:40 |
| 2026-11-23 | runs/20261122-1710_T19a_twist_maps | running | T19a 10:42: N 8 at +1° lost in the reboot; restarted (N 8 +1°, then N 7 at +0.5°, +0.25°), ETA ~12:30 |
| 2026-11-23 | runs/20261122-1735_T16c_hex_r3 | running | T16c 11:32: 21/35 points (7 of the 21 restarted ones done, ~30 min each). Target met at 0 points; best worst-|M| 3.06 (folded 1467.8 nm doublet, Δ 0, t 280, gap 420, Q 88). Remaining 14, ETA ~12:40 |
| 2026-11-23 | runs/20261122-1710_T19a_twist_maps | running | T19a 11:32: N 8 at +1° still running (52 min so far, GPU 100 %, 9 GiB) |
| 2026-11-23 | runs/20261122-1710_T19a_twist_maps | running | T19a 11:55: N 8 at +1° done (3804 s). Point CD_AA not converged (N 7 vs 8 differ ≤ 0.013 on line, 0.09 off line); disc CD at 1° converged on line: D 20 µm +0.018 at 1505.5 nm. N 7 at 0.5°, 0.25° running |
| 2026-11-23 | (T16c, T19a) | running | 12:12: T16c 30/35 points; T19a N 7 at +0.5° running (started ~11:43), then +0.25°; ETA both ~12:45 |
| 2026-11-23 | runs/20261122-1735_T16c_hex_r3 | review | T16c: 35 points, target met at 0. Closest in window: folded 1467.8 nm doublet (Δ 0, t 280, gap 420, Q 88), c_TE −0.16, c_TM +0.16, worst \|M\| 3.07 (~3× short). E1: TM flat at \|Δ\| 0.04–0.05 but \|c_TE\| ≥ 0.31 everywhere (\|M\| ≤ 1.6) |
| 2026-11-23 | runs/20261122-1710_T19a_twist_maps | review | T19a/T19c: point CD_AA not converged at N ≤ 8 (bound ≲ 0.01–0.015 on line, θ ≤ 1°; no κ). Disc CD at AA converged at 1°: D 10 µm 0.006, D 20 µm +0.018 at 1505.5 nm (N 7 = N 8 within 0.0003 at peak) |
| 2026-11-23 | runs/20261123-1310_T20_pol_keys | running | T20 13:25: model.py keys swapped to physical (pure rename, new−old = 0.0 exactly); Brewster key T_TM = 1.000000; prelim analyze reproduces T1 with names swapped (TM M 31.478). Next: rcwa4d-mf stripes test |
| 2026-11-23 | runs/20261123-1310_T20_pol_keys | review | T20: model.py keys physical (pure rename, diff 0.0); Brewster key T_TM 1.000000; prelim M (key TM) 31.478 = T1; rcwa4d-mf lab x/y confirmed by stripes test (no swap) |
| 2026-11-23 | runs/20261123-1326_T21_E1_doublet_cross | running | T21 13:26: 25 points (t 290–310 × Δ 0/±0.02/±0.04, gap 380), 1440–1600 nm, 7 CPU procs; ~1 h per point, ETA ~17:30 (first 15 points ~16:30) |
| 2026-11-23 | runs/20261123-1327_T19d_twist_scaling | running | T19d 13:30: post-processing of T19a amps done (post_T19a_only/); GPU: N 7 at +2° then N 8 at +0.5° (ETA ~15:00) |
