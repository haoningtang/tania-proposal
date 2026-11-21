# T11a: hexagonal-lattice survey + isotropy check (configs/stage11a_hex_survey.json; inverse/hex_survey.py, inverse/hex_isotropy.py)

- Survey: 24 designs (a 700/750/800/850 × r/a 0.25/0.30/0.35 × t 220/280 nm; t2 = t, r2 = r, c4 = c8 = 0), gap 380, 80/96, 0.5°,
  1450–1650 nm on a 0.5 nm grid plus a fine refit. TE/TM pairs (≤ 0.2 nm apart) with Q ≥ 300: **3**, all a 850, t 280:
  r/a 0.30: 1536.53 nm, Q 8.1e4; r/a 0.25: 1571.87 nm, Q 7.2e4; r/a 0.35: 1500.21 nm, Q 5.5e4 (quasi-BICs). 18 designs: no pole Q ≥ 300.
  Caveats: analyze.poles drops Q > 1e5 and Q < 10, and the survey refits only poles with Q ≥ 150. So pairs with Q > 1e5 and broad bright
  modes are not listed. The best candidate's gap-500 line has Q 1.07e5 and was found only by hand.
- Isotropy (hex_isotropy.py: band()'s M fit, start window ±3 linewidths; θ 0.5/3/6°; azimuth 0/15/30°; 80/96). Each pair splits into
  two bands: A shifts up (+0.4–0.6 nm by 3°), B shifts down (−2.1 to −2.9 nm by 3°; lost after 3° at most azimuths).
  **Per band the dispersion is isotropic:** band-A M at az 0/15/30: cand 0 gap 380 −4.75/−4.89/−5.05; gap 260 −3.39/−3.46/−3.53;
  gap 500 −/−5.61/−5.77 (az 0: tracker jumped at 6°); cand 1 −4.30/−4.29/−4.66. Band-B wavelength at 3° agrees within 0.006 nm across az.
  **Per polarization it is not.** At az 0 TE couples to A and TM to B; at az 30 they swap; at az 15 (no mirror) both inputs excite A
  most. Cand 2 (r/a 0.35) is not isotropic at all (TE M 13.8 / −21.7 / −6.3).
- Best candidate across gaps (a 850, r/a 0.30, t 280): 1541.9 / 1536.5 / 1534.5 nm at gaps 260 / 380 / 500 (Q 6.4e4 / 8.1e4 / 1.07e5)
  → **tuning 0.48 %**. |M| ≤ 5.8 for every line.
- Verdict for the targets: not a design (survey). |M| < 10, tuning 0.48 % < 2 %. What it shows: the C6v O(k²) isotropy holds per band.
  But these Γ quasi-BICs behave like an E2-type doublet: TE/TM map to different bands on the two kinds of mirror line. So "flat for TE at
  every azimuth" needs **both** bands of the doublet flat (or a non-degenerate, singlet-type line).
