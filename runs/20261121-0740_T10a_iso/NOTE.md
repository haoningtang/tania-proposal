# T10a: "sharp" at azimuth 0° and 45°, t2 free, η 1/3000, S_t 500, ±5 %, base = T9b best (configs/stage10a_iso_from_T9b.json)

- 120/128; gaps 260/380/500; θ 0.5/3.5/6.5° at φ 0 and 45°. Start = T9b best exactly (init t2 = T9b t). L-BFGS-B converged after
  59 it / 162 evals / 139 min. Smoothed loss 0.704 → 0.420; tune 2.19 → 2.34 %. Best: a 731.1, t 273.2, t2 282.7 (t2 − t = +9.5 nm),
  r 244.1, c4 7.8, c8 0.8, r2 241.2 nm; lam_k 1534.5 / 1557.2 / 1570.9 nm. No variable on a bound.
- M at 200/192 (120/128 in brackets), Q at 0.5°:
  | gap | φ 0° TE | φ 0° TM | φ 45° TE | φ 45° TM | Q |
  | 260 | −2.1 (−2.1) | **+12.4** (+11.1) | +5.8 (−5.1) | **−13.1** (−14.8) | 194 |
  | 380 | **−12.7** (−13.6) | −12.7* (+8.9) | −3.2 (−3.0) | +2.6 (+2.5) | 562 |
  | 500 | **−88** (−114) | +6.0 (+6.5) | −2.9 (−2.7) | +1.9 (+1.9) | 862 |
  *gap-380 TM at 200/192: the fit jumps to a Q ~ 11 feature at 6° and 10°, so this M is unreliable; to 3° the line moves −0.26 nm.
- T9b start at 45° (`runs/20261121-0556_T9b_gaps260/az45`), 200/192 (120/128): gap 260 TE −3.9 (−2.5), TM **+124** (+66); gap 380 TE −2.3 (−2.6),
  TM +2.5 (+2.4); gap 500 TE pole lost after 3° (+1.1 nm by 3°), TM +1.8 (TM lost after 3° at 120/128). T9b at 0° was 5/6.
- Verdict: **not met**. The 45° terms cost a lot at 0° (5/6 → 3/6 at 200/192) and gained nothing at 45° (1/6 before and after).
  At 45° the gap 380/500 lines still move 2–5 nm by 6°, both pols. Q went down at gap 500 (5.8e3 → 862). t2 moved +9.5 nm.
