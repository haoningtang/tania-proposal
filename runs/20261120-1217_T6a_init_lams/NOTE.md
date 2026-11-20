# T6a init_lams: resonances of the T3 step-1 best with r2 = r − 10 nm at 0.5° (n_terms 120, ngrid 128)

- `find_resonances.py` (0.5 nm scan + AAA, fine rescan around each pole, Q ≥ 300 unless stated).
- Gap 200: TE/TM-degenerate pole 1522.74 nm, Q 1202 (TE) / 1148 (TM); Fano lineshape (T 0.35 at the pole, T → 0 at 1526.4).
  Also a TE-only pole 1505.96 nm, Q 1.4e4.
- Gap 320: degenerate pole 1547.46 nm, Q 474 (T → 0 at 1547.1).
- Gap 500: no degenerate pole with Q ≥ 300 in 1400–1700 nm (only TE 1427/1440/1476/1493, Q 1–2e4, and TM 1568.6, Q 1.8e4).
  Narrow search 1555–1620 nm (qmin 100): degenerate pole 1569.1 nm, Q 192. Used as the nearest (TASKS T6a).
- init_lams = 1522.74 / 1547.46 / 1569.11 nm (tuning 3.0 %). Same family across gaps (+25, +22 nm).
