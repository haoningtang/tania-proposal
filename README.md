# tania-proposal

Computations for the ARO white paper "MEMS-Reconfigurable Moiré Photonics: Tunable Flat Bands for Selective
Electro-Optic Sensing Before Detection".

| folder | what |
|---|---|
| `docs/HANDOFF.md` | the science, targets, preliminary results and task list |
| `prelim/` | preliminary results (grcwa): code, data, figures A–C |
| `inverse/` | differentiable model (fmmax/JAX), optimizer, band analysis, configs |
| `runs/` | one folder per run |
| `TASKS.md` | the task queue (controller: cloud session; worker: GPU session) |
| `BOARD.md`, `STATUS.md` | messages and run log between the two sessions |
| `CLAUDE.md` | working rules for any Claude session here |

## Setup on the GPU machine

JAX runs on NVIDIA GPUs under **Linux**. On a Windows machine, use **WSL2** (Ubuntu) and do everything inside it.

```bash
git clone -b compute https://github.com/haoningtang/tania-proposal.git
cd tania-proposal
python -m venv .venv && source .venv/bin/activate
pip install -U "jax[cuda12]" fmmax scipy matplotlib
python -c "import jax; print(jax.devices())"     # must list a CUDA device
python inverse/check_vs_grcwa.py                  # cross-check against prelim/
```

`git push` needs credentials on that machine (`gh auth login`, or a personal access token).
