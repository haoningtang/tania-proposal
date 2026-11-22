#!/usr/bin/env bash
source ~/venvs/r4d/bin/activate
cd "$(dirname "$0")/../../inverse"
OUT=../runs/20261122-1710_T19a_twist_maps
python twist_maps.py --out $OUT/amps --twists 1 -1 0.5 -0.5 2 --N 6
python twist_maps.py --out $OUT/amps --twists 1 --N 7
python twist_maps.py --out $OUT/amps --twists 0.25 -0.25 --N 6
echo ALLDONE
