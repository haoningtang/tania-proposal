# T7c: T8a best at azimuth 45° (lattice diagonal)

- Design = runs/20261121-0232_T8a_sharp_cont/best.json (chosen over T7a2, reasons in BOARD 04:55). `analyze.py --azimuth 45` at
  120/128 and 200/192 (θ 0.5/3/6/10°), `spectra.py --azimuth 45` (θ 0.5/3.5/6.5°) at 120/128. 0° spectra: T8a folder.
- 45°, M (Q at 0.5°), 120/128 | 200/192: gap 200 TE −1.7 | −1.7 (Q 381 | 428), TM −1.4 | pole only to 3° (Q 389 | 438);
  gap 320 TE −1.6 | +1.3 (Q 304 | 336), TM +3.5 | +3.6; gap 500 TE pole only to 3° (Q 2.0e3 | 1.9e3), TM +1.8 | +1.8.
  The poles move 3–8 nm by 6° (gap 500 TM 1571.1 → 1566.5 nm, 200/192). TE/TM stay degenerate at 0.5° (≤ 0.1 nm).
- Verdict: **not met**. No |M| ≥ 10 at 45° for either polarization at any gap. Even the gap-500 TE line, flat to 10° along x
  (M −346), moves 1.4 nm by 3° along the diagonal. The flatness of this design family is along x only, as with T3/T4.
