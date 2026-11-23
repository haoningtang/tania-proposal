#!/usr/bin/env bash
# 2026-11-23 restart: remaining T19a parts (N 7 at +1 deg; N 6 at +-0.25 deg). Cores 0-3.
source ~/venvs/r4d/bin/activate
cd "$(dirname "$0")/../../inverse"
OUT=../runs/20261122-1710_T19a_twist_maps
taskset -c 0-3 python twist_maps.py --out $OUT/amps --twists 0.25 -0.25 --N 6
taskset -c 0-3 python twist_maps.py --out $OUT/amps --twists 1 --N 7
echo ALLDONE
