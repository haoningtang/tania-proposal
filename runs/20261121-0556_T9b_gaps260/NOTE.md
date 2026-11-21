# T9b: T8a best with gaps 260/380/500 nm, η 1/8000, S_t 1500 (configs/stage9b_gaps260_from_T8a.json)

- init_lams from runs/20261121-0546_T9b_init_lams: 1535.08 / 1558.36 / 1572.26 nm (TE/TM-degenerate, Q 207/653/2.0e3 at 0.5°).
  120/128; θ 0.5/3.5/6.5°, azimuth 0; trust ±3 %, lam_k ±0.3 %. **Hit the 80-iteration limit** (150 evals / 64 min). Smoothed loss
  0.907 → 0.596; tune 2.39 → 2.19 %. No variable on a bound. Best: a 727.5, t 279.1, r 241.2, c4 5.2, c8 0.2, r2 239.6 nm;
  lam_k 1536.5 / 1557.1 / 1570.6 nm.
- S at real λ (sharp_table.json), best: gap 260 TE 278/396/883, TM 277/294/1455; gap 380 TE 1308/1521/1608, TM 1304/1318/1285;
  gap 500 TE 9628/8594/4780, TM 9644/9868/4238 (start: 100–3874).
- analyze.py M (Q at 0.5°), 120/128 | 200/192: gap 260 TE −2.6 | −2.6 (Q 201 | 220), TM −15.6 | −25.9 (Q 199 | 219);
  gap 380 TE −17.2 | −16.1 (Q 721 | 816), TM −40 | −893 (Q 719 | 814); gap 500 TE −1589 | −407 (Q 6.5e3 | 5.8e3), TM +51 | +25.
  λ shift between resolutions ≤ 1.1 nm, Q +10–13 % (gap 500 −11 %). Pole tuning (200/192, 0.5°) 1533.1 → 1569.5 nm = 2.34 %.
- Verdict: **not met, but closest so far**: 5 of 6 |M| ≥ 10 at 0° at both resolutions. Misses: gap-260 TE (M −2.6, moves 3 nm by 6°)
  and Q ≥ 300 at gap 260 (Q 220). Gaps 380/500 meet |M| ≥ 10 and Q ≥ 300 for both pols. Not checked at 45° (T10a does this).
