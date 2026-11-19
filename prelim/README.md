# Preliminary results (grcwa, cloud CPU, 2026-11-19)

Figures A–C in `figures/`; numbers in `docs/HANDOFF.md` section 2.

**Polarization names in these scripts are swapped.** `pol='p'` in `code/*.py` and `data/*.json` reads the
y-polarised output for an x–z incidence plane, i.e. **TE** (E perpendicular to the plane of incidence);
`pol='s'` is **TM**. This was confirmed with the independent fmmax model (`inverse/check_vs_grcwa.py`,
`inverse/analyze.py`). The figures use TE/TM correctly.

Code: `lib.py` (grcwa wrapper), `rc.py`/`track.py` (pole tracking with AAA), `job*.py` (scans), `figs2.py` (figures).
Settings: nG = 81, 96×96 grid, Si n = 3.48, lossless, suspended. Increasing nG to 141 moved resonances by
≈ 1.7 nm and changed angular dispersion and Q by < 2 %.
