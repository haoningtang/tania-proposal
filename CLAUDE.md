# Instructions for Claude sessions in this repository

This repository is shared by two Claude sessions and the PI (Haoning Tang):

- **Cloud session** (no GPU): writes the proposal text, sets tasks, analyses results, makes figures.
- **GPU session** (runs on the lab machine with an NVIDIA GPU): runs the inverse design and full-wave checks.

The two sessions cannot talk to each other directly. **The repository is the only channel.**
Read `docs/HANDOFF.md` first for the science; this file is only about how to work here.

## Every time you start

1. Make sure you are on the `compute` branch (`git checkout compute`), then `git pull --rebase --autostash`
2. Read `BOARD.md` from the bottom up. Act on the newest entries addressed to you.
3. Read `STATUS.md` to see what is running and what is done.

## Every time you finish a step (or at least every hour of compute)

1. Put outputs in `runs/<YYYYMMDD-HHMM>_<short-tag>/`: `config.json`, `history.csv`, `best.json`,
   `done.json`, `analysis.json`, `analysis.png`, and a 3–6 line `NOTE.md` (what was run, the result in numbers,
   what you think it means). No single file over 5 MB; no raw field dumps.
2. Update `STATUS.md` (one line per run: date, tag, state, headline number).
3. Add a dated entry to `BOARD.md` under the right heading (see the format there).
4. `bash scripts/sync.sh "<one-line message>"`. It pulls, commits and pushes.

Never force-push. Never rewrite history. If a pull conflicts, keep both versions of `BOARD.md`/`STATUS.md` lines.

## Rules for results

- Report numbers you computed, with the settings (`n_terms`, `ngrid`, angles). Say what was not checked.
- Before calling a design good, re-run `inverse/analyze.py` at higher resolution (`--n_terms 200 --ngrid 192`)
  and report both sets of numbers.
- Polarization names: **TE** = E perpendicular to the plane of incidence, **TM** = E in the plane of incidence.
  (The grcwa scripts in `prelim/code` use `pol='p'` for TE and `pol='s'` for TM. Do not copy those names.)
- The proposal targets are fixed by the PI and are not to be lowered: both polarizations, 1 nm window
  (R ≈ 1550), acceptance ±6.5° (M ≥ 10), tunable ≥ 2%. Report how far a design is from them; do not redefine them.
- Do not edit `docs/HANDOFF.md` or `prelim/`. The GPU session writes to `runs/`, `STATUS.md`, `BOARD.md`,
  `docs/RESULTS.md` and may add new configs or scripts under `inverse/`.

## Solvers

- Aligned bilayers (no twist): `inverse/model.py` (fmmax, JAX, differentiable). rcwa4d-mf refuses twist = 0.
- Twisted bilayers (A3, moiré colour ruler): `github.com/haoningtang/rcwa4d-mf` (PyTorch, GPU).
