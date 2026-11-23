# T19d — disc CD at AA vs twist at fixed D/cell and at fixed D (rcwa4d-mf, same structure and definition as T19a/T19c)
- Run: new solves N 7 at +2° (1400 s, |R+T−1| 1e-11) and N 8 at +0.5° (4795 s; **|R+T−1| up to 5e-2 at 7 λ in 1512–1526 nm, dropped**; 1500–1511.5 nm < 1e-3).
  Plus the T19a amps. Disc CD at AA as in T19c (`inverse/twist_scaling.py`); main line 1500–1512.5 nm; error = last-two-N difference over the line.
- **At fixed D/cell 0.4 the main-line CD is ∝ θ:** +0.0031 / +0.0058 / +0.0102 / +0.0217 at 0.25 / 0.5 / 1 / 2° (N 7 / 8 / 8 / 7), CD/θ = 0.0123 / 0.0116 /
  0.0102 / 0.0109 per degree, fit **κ = 0.011 per degree** (log-log slope 0.93). Peak N-differences ≤ 0.0005; whole-line differences 0.0005–0.009 (largest at 2°).
  D/cell 0.56: +0.0070 / +0.0094 / +0.0176 / +0.0411 (κ 0.020 /deg, slope 0.86; 0.25° is high, CD/θ 0.028). D/cell 0.25: +0.0030 / +0.0052 at 0.5 / 1°;
  at 0.25° it changes sign between N 6 and N 7 (not converged), and at 2° the line-edge value (−0.022 at 1512.5 nm) is not converged while the dip peak is +0.018/+0.019 (N 7/N 6) at 1502 nm.
- **At fixed D there is no simple law:** D 10 µm +0.0105 (not conv.) / +0.0013 / +0.0060 / +0.0415; D 20 µm −0.007 (not conv.) / +0.0036 / +0.0178 (2°: D > cell).
  The fixed-D growth with θ mixes the θ scaling with the growing D/cell. 0.5° N 8 confirms N 7 on the line: f0.4 0.0058 vs 0.0060, D 20 µm 0.0036 vs 0.0039.
- Meaning: the signed twist readout follows CD ≈ κ(D/cell)·θ with κ ≈ 0.011 /deg at D/cell 0.4 (0.02 /deg at 0.56), so the aperture should scale with the moiré
  cell (D ∝ 1/θ). Not checked: N 8 at 2° and 0.25°, the cause of the 0.5° N 8 energy error, 0.25° N 7 (|R+T−1| 2.3e-4, kept). Figure analysis.png; table.csv; analysis.json.
