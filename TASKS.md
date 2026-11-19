# Task queue

Owned by the **cloud session (controller)**. Only the controller adds tasks, changes their order, or closes them.
The GPU session (worker) takes the first `todo` task, sets it to `doing`, and when finished sets it to `review`
with a link to its `runs/` folder. The controller then marks it `done` or sends it back with a note.

States: `todo` → `doing` → `review` → `done` (or `blocked`, with the reason on BOARD.md).

| id | state | task | done when | notes |
|---|---|---|---|---|
| T1 | doing | Validate: GPU visible to JAX; `inverse/check_vs_grcwa.py`; `analyze.py` on the prelim structure (gap 200 nm) at n_terms 120 and 200 | TE M ≈ 30 and TM M ≈ 0.6 at gap 200 nm (within 10 %); time per stage-1 iteration measured | HANDOFF §4.1 |
| T2 | todo | Stage 1: `configs/stage1_bothpol_flat.json`, then `analyze.py --run` | TE and TM \|M\| ≥ 10 at all three gaps (200, 260, 320 nm) and tuning ≥ 2 % | stop at 80 iterations; post best numbers either way |
| T3 | todo | Stage 2: narrow the linewidth by continuation (half_window_frac 0.003 → 0.001 → 0.0004), each from the previous best | R ≥ 1500 with TE and TM \|M\| ≥ 10 at all three gaps | one run per step; push after each |
| T4 | todo | Check the best design along the lattice diagonal (azimuth 45°): add an `azimuth` argument to `model.py` | TE and TM \|M\| ≥ 10 at 45° as well | needed for "all azimuths" |
| T5 | todo | High-resolution check of the best design: `analyze.py --n_terms 200 --ngrid 192` | numbers change < 10 % from the optimization resolution | required before the controller uses a design in the proposal |

Fallbacks if T2 or T3 stalls (try in order, one run each, post results; do not invent other directions without
asking on BOARD.md): different radii in the two slabs (`r2`); lateral shift as a per-state design variable;
more angles (0.5, 3, 6, 9°); hexagonal lattice.
