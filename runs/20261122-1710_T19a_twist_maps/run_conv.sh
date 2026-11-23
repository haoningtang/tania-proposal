#!/usr/bin/env bash
# 2026-11-23 08:05: N convergence of CD_AA (N 6 -> 7 changed CD_AA at +1 deg by ~10x near 1511 nm). Positive twists only (parity exact).
source ~/venvs/r4d/bin/activate
cd "$(dirname "$0")/../../inverse"
OUT=../runs/20261122-1710_T19a_twist_maps
taskset -c 0 python twist_maps.py --out $OUT/amps --twists 1 --N 8
taskset -c 0 python twist_maps.py --out $OUT/amps --twists 0.5 0.25 --N 7
echo ALLDONE_CONV
