# Instructions for Claude sessions in this repository

This repository is shared by two Claude sessions and the PI (Haoning Tang):

- **Controller** (no GPU). From 2026-11-20 21:00 this is the PI's own chat session (it took over from the earlier cloud
  session, which is no longer active); it still signs BOARD entries as `cloud`: owns `TASKS.md`, decides what is computed next, checks results,
  writes the proposal text and figures.
- **GPU session = worker** (the PI's Windows machine with an NVIDIA GPU, conversation "Tania总统奖Proposal（win）"):
  runs the tasks in `TASKS.md`, in order, and reports. It does not start new directions on its own; it proposes
  them on `BOARD.md` and waits for the controller.

The two sessions cannot talk to each other directly. **The repository is the only channel.**
Read `docs/HANDOFF.md` first for the science; this file is only about how to work here.

## Every time you start

1. Make sure you are on the `compute` branch (`git checkout compute`), then `git pull --rebase --autostash`
2. Read `BOARD.md` from the bottom up. Act on the newest entries addressed to you.
3. Read `TASKS.md`. Worker: take the first `todo` task (set it to `doing`, push at once so the controller sees it).
4. Read `STATUS.md` to see what is running and what is done.

## Worker loop (GPU session)

Take task → run → write `runs/<folder>/NOTE.md` → set the task to `review` in `TASKS.md` → `STATUS.md` line →
`BOARD.md` entry → `scripts/sync.sh` → pull again and take the next `todo` task. Keep going until no `todo` task is
left, then post "queue empty" on `BOARD.md` and stop. Push at least once an hour during a long run (a `STATUS.md`
line with the current iteration and loss is enough).

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
- Polarization names: **TE** = E perpendicular to the plane of incidence (s), **TM** = E in the plane of incidence (p). Checked at the Brewster
  angle on 2026-11-22 (`docs/POLARIZATION_NOTE.md`): the prelim grcwa code uses the standard names (`pol='p'` is TM), and the keys `TE`/`TM` of
  `inverse/model.py` are **swapped** (key `TE` is physical TM) until task T20 fixes them. Report physical names; when quoting a run made with
  model.py, say which key it came from.
- The proposal targets are fixed by the PI and are not to be lowered: both polarizations, 1 nm window
  (R ≈ 1550), acceptance ±6.5° (M ≥ 10), tunable ≥ 2%. Report how far a design is from them; do not redefine them.
- Do not edit `docs/HANDOFF.md` or `prelim/`. The GPU session writes to `runs/`, `STATUS.md`, `BOARD.md`,
  `docs/RESULTS.md`, the state column of `TASKS.md`, and may add new configs or scripts under `inverse/`.

## Solvers

- Aligned bilayers (no twist): `inverse/model.py` (fmmax, JAX, differentiable). rcwa4d-mf refuses twist = 0.
- Twisted bilayers (A3, moiré colour ruler): `github.com/haoningtang/rcwa4d-mf` (PyTorch, GPU).
