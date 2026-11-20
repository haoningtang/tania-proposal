# T4: T3 step-1 best at azimuth 45° (lattice diagonal)

- Design = runs/20261120-1026_stage2_step1/best.json. `analyze.py --azimuth 45` at 120/128 and 200/192
  (thetas 0.5/3/6/10°), `spectra.py --azimuth 45` at 120/128. Model checks: runs/20261120-azimuth_check.
- 200/192: TM gap 260 λ 1523.8 nm Q 2375 M −11.8 (+0.7 nm from 0.5° to 6°); TM gap 320 λ 1534.9 Q 4359 M +4.7
  (−1.7 nm by 6°, −4.9 nm by 10°); TM gap 200 λ 1495.6 Q 2.2e4 M 0.76. TE: poles at 1523.8 / 1535.0 / (gap 200: none)
  found only to 3°, M NaN. 120/128 gives the same picture (TM M −12.9 / +4.5 / 0.76).
- Compare azimuth 0 (T3 NOTE): TM gap 320 was flat (≤ 0.1 nm to 6°) at 0°, but moves 1.7 nm by 6° at 45°. So it is not
  flat for all azimuths. At gap 200 the TE/TM labels of the two modes swap between 0° and 45°.
- Dip check at lam_k, 45°: max T 0.089 / 0.059 / 0.074 (broad band, as at 0°).
- Verdict: **not met** (TE and TM |M| ≥ 10 at 45°: only TM at gap 260). One 4 GB CUDA OOM message at 120/128 (shared
  GPU); the run finished all states.
