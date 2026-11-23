# T20 — model.py TE/TM keys made physical; rcwa4d-mf x/y convention
- Diff summary: `model.py` `pol = {"TM": (cos, sin), "TE": (−sin, cos)}` → `{"TE": (cos, sin), "TM": (−sin, cos)}` (pure rename), `POL_KEYS = "physical"`,
  dated header; `lpa_shift_map.py` J assembly re-keyed (same J); `hex_r3_scan.py` stores `pol_keys`; `hex_r3_analyze.py` reads old and new pts;
  `check_pol_labels.py` expectations updated; `check_vs_grcwa.py` docstring; other scripts pass keys through, so their labels are now physical.
- Checks: new vs old model.py, every key vs its swapped old key: max difference 0.0 (n_terms 60, θ 3/6/4°, azimuth 0/30/17°, one shifted case).
  Brewster (check_pol_labels.txt): key T_TM = 1.000000, key T_TE 0.035; stripes: key t_TE (E_y) larger phase. Prelim analyze.py (120/128, θ 0.5/3/6):
  key TM λ 1505.4 nm, Q 161.0, M 31.478; key TE Q 161.2, M 0.594, identical to T1 nt120 with the names swapped (prelim_nt120/).
- rcwa4d-mf stripes (check_pol_rcwa4d.txt): lab x/y, no swap; E_y along stripes phase −2.09 vs −0.63 rad (exp(+iωt)). CD sign in T19a/T19c stands.
- Rule for old folders in docs/POLARIZATION_NOTE.md. Not changed: stored results in old runs/ folders, the scripts' handling of old stored files other than hex_r3.
