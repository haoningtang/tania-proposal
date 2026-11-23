#!/usr/bin/env bash
# 2026-11-23: finish the n 48 LPA map (232/325 C4v shifts done before the 18:16 stop); cores 1-3, then merge.
cd "$(dirname "$0")/../../../inverse"
OUT=../runs/20261122-1720_T19b_lpa_shift_map/n48
export JAX_PLATFORMS=cpu OMP_NUM_THREADS=1 XLA_FLAGS="--xla_cpu_multi_thread_eigen=false intra_op_parallelism_threads=1"
for k in 0 1 2; do
  taskset -c $((k+1)) ../.venv/bin/python lpa_shift_map.py --out $OUT --n 48 --part $k --nparts 3 >> $OUT/log_part$k.txt 2>&1 &
done
wait
../.venv/bin/python lpa_shift_map.py --out $OUT --n 48 --merge >> $OUT/log_merge.txt 2>&1
echo ALLDONE >> $OUT/log_merge.txt
