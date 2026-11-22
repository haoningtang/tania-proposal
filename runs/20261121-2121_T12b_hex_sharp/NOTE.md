# T12b: first hex optimization, "sharp" (η 1/3000, S_t 500, trust ±5 %, azimuth 0), `configs/stage12b_hex_sharp_from_T12a.json`

- Start: T12a best E1 line (a 850, r/a 0.25, t 280, r2 = r, t2 = t; λ_k 1477.93 / 1498.56 / 1509.02 nm). 120/128, θ 0.5/3.5/6.5°. L-BFGS-B converged
  ("relative reduction of F") after 20 it / 106 evals / 35 min; loss 1.039 → 0.607. **The design barely moved**: a 850.9, t 279.9 (= t2), r 211.7 (= r2),
  c4 0.08, c8 0.01 nm. Most of the gain came from λ_k at gap 260 moving 1477.9 → 1473.6 nm onto a **different, narrower feature** (Q 432; the survey's
  1470 nm line). So the run's "tune 2.36 %" mixes two lines; the followed E1 line itself still tunes 2.08 %.
- M at 200/192 (120/128), azimuth 0° | 30°; Q at 0.5°: gap 260 TE −6.1 (−5.9) | −6.7, TM +4.7 (+4.3) | +4.9, Q 450 (432);
  gap 380 TE +5.9 (+5.5) | +5.9, TM +1.18 (+1.16) | +1.18, Q 117 (130); gap 500 TE +5.1 (+5.0) | +5.2, TM +1.09 (+1.07) | +1.09, Q 96 (102).
  S at real λ (best): gap 260 TE 800–1100, TM 900 → 350 by 6.5°; gaps 380/500 S 150–300 (target 500).
- Verdict: **not met** (0/12 |M| ≥ 10; Q ≥ 300 only at gap 260, on the other line). Isotropy holds (M at 0° vs 30° within 10 %), so the hex
  approach works on that side. But from this start the 7 variables find no direction that flattens TM (M ≈ 1, FP-like) at gaps 380/500: a local minimum next to the start.
  The λ_k at 380/500 sit on the steep edge of a broad Fano feature (spectra.png), not on a narrow line.
