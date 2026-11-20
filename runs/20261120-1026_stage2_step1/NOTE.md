# T3 step 1 (half_window_frac 0.003), configs/stage2_step1.json

- From the T2b best; n_terms 120, ngrid 128; T2b trust region (±10 % of start, lam_k ±0.5 %); w_side 1.0; r2 = r at start.
  80 iterations (limit) / 120 evals / 51 min. Loss 0.986 → 0.766: dip 0.042 → 0.043, side 0.944 → 0.724, tune 2.28 %.
  Best a 728.6, t 282.7, r 245.6 (r2 = r), c4 1.5, c8 −0.8 nm; lam_k 1496.6 / 1519.9 / 1531.2 nm. Not on a bound.
- spectra.png: lam_k still in the broad low-T band (max T at lam_k 0.096 / 0.060 / 0.100). The side term rose
  because sharp Fano **peaks** (T → 0.6–1) appeared about +4 nm from lam_k, i.e. at the +0.3 % probe.
- analyze.py 120/128 → 200/192. TM: gap 260 λ 1524.5 → 1523.8 nm, Q 1716 → 2314, M −75 → +190; gap 320 λ 1535.8 → 1535.0,
  Q 2998 → 4268, M −199 → +77 (sign flips = shift below fit noise; 0.5→6° shift ≤ 0.1 nm, 10°: −0.5 / −0.8 nm at hires,
  i.e. |M| ≈ 46 / 29 from the 10° point). Gap 200: TM Q 2.7e4, M −229 at 1511.8 nm at 120/128, **no pole** at 200/192.
  TE: gap 200 M 0.8 (moves 10 nm by 6°); gap 260 pole lost after 3° (both res.); gap 320 M NaN → −4.1 (2 nm by 6°).
- Verdict: **not met** (TE |M| < 10; lam_k not on the resonances; tuning between the two TM-flat features 0.73 %).
  Finding: a TM-flat, Q ≈ 2–4e3 Fano resonance exists in this family (gaps 260/320), TE-degenerate at normal
  incidence but not flat for TE. Steps 2–3 skipped (PI note 11:15). One 4 GB CUDA OOM during the hires run (GPU shared);
  that run still finished all three states. Not checked: azimuth 45° (T4), angles between 6 and 10°.
