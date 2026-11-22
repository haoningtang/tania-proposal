# T13c: flat vs curved angle response, prelim square bilayer (a 620, t 220, r 120 nm), `inverse/angle_maps.py`, CPU, 80/96

- Gap scan of the TE band curvature c = (Δλ/λ)/sin²θ (θ 0.5/3/6°, same line followed from gap 500 down to 60 nm, Q 154–316): c_TE = −0.022 (500), −0.0167 (200),
  −0.0087 (100), **0 at gap 81.85 nm** (c −6.5e-5, M ≈ 7700; bracket +0.0015 at 80, −0.00097 at 83), +0.054 at 60. TM stays curved: c −0.82 (M 0.61).
  Below 60 nm the line changes character (gap 40: c ±0.73; gap 20: Q 1.9e4); not used. TM c at gaps 320–500 is unreliable (tracker jumps lines).
- Maps T(θx, θy), 0–10°, 1° steps, (kx, ky)/k0 = (sin θx, sin θy), TE/TM w.r.t. the local plane of incidence, probe λ = 0.5° pole (1455.98 nm at 81.85;
  1506.55 nm at 200). **Neither a disk nor a ring: TE is a cross.** At 81.85 nm TE T = 0.00 along the θx and θy axes out to 10°, but along the diagonal
  T = 0.13 / 0.70 / 0.94 at 2 / 4 / 6°. That is the same as TM, which is a central spot (T 0.15 / 0.73 / 0.95 along x). At gap 200 the pattern is the same
  with lower contrast (on-axis TE T between 0.01 and 0.06 out to 10°; diagonal 0.45 at 4°).
- Meaning: zero TE curvature along x makes the square lattice flat only along its axes (C4v: the x and diagonal curvatures are independent; cf. T7c, T10a).
  The diagonal response is TM-like. A uniform disk needs the hex E1 case (T12). Unpolarized: on-axis T ≈ 0.5 (TE dark, TM bright) beyond ~4°.
- Settings/caveats: Q ≈ 155 (linewidth 9.4 nm), so a curved band leaves the probe λ only after ~2–3°. Fixed probe λ, |t|² only. Two of my restarts overlapped
  on maps.json (the log is incomplete), but the scan rows are continuous and both maps were computed once each (`wall_s` 91 s / 87 s).
