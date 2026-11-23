#!/usr/bin/env bash
# E1 identification by gap tuning (task: "identify E1 ... as the gap-tunable bright doublet"): r/a 0.22, Delta 0, gap 420 (and 340 if needed)
cd "$(dirname "$0")/../../../inverse"
export XLA_PYTHON_CLIENT_PREALLOCATE=false
taskset -c 0-3 ../.venv/bin/python hex_r3_scan.py --out ../runs/20261123-1705_T22_hole_scan/gap_id --lo 1480 --hi 1700 --points "0.22,0,280,420"
echo ALLDONE
