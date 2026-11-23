#!/usr/bin/env bash
# 15:35: GPU idle after T19d. Check point D 0 t 300 on GPU (compare with the CPU pts), then the 4 unclaimed t 310 points on GPU.
cd "$(dirname "$0")/../../inverse"
OUT=../runs/20261123-1326_T21_E1_doublet_cross
export XLA_PYTHON_CLIENT_PREALLOCATE=false
taskset -c 0-3 ../.venv/bin/python hex_r3_scan.py --out $OUT/gpu_check --lo 1440 --hi 1600 --points "0,300,380"
echo CHECKDONE
taskset -c 0-3 ../.venv/bin/python hex_r3_scan.py --out $OUT --lo 1440 --hi 1600 --points "0.02,310,380;-0.02,310,380;0.04,310,380;-0.04,310,380"
echo ALLDONE
