#!/usr/bin/env bash
# T19d new solves (rcwa4d-mf, GPU): N 7 at +2 deg, then N 8 at +0.5 deg. Same setup as T19a (twist_maps.py defaults).
source ~/venvs/r4d/bin/activate
cd "$(dirname "$0")/../../inverse"
OUT=../runs/20261123-1327_T19d_twist_scaling
taskset -c 0-3 python twist_maps.py --out $OUT/amps --twists 2 --N 7
taskset -c 0-3 python twist_maps.py --out $OUT/amps --twists 0.5 --N 8
echo ALLDONE
