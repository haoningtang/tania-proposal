#!/usr/bin/env bash
# 2026-11-23 restart after the 2026-11-22 18:01 session died: 7 processes x 4 threads on cores 4-31 (CPU, fmmax).
cd "$(dirname "$0")/../../inverse"
OUT=../runs/20261122-1735_T16c_hex_r3
REF="0.04,280,380;-0.04,280,380;0.08,280,380;-0.08,280,380"
export JAX_PLATFORMS=cpu OMP_NUM_THREADS=4 XLA_FLAGS="--xla_cpu_multi_thread_eigen=true intra_op_parallelism_threads=4"
for i in 0 1 2 3 4 5 6; do
  c0=$((4+4*i)); c1=$((c0+3))
  ( taskset -c $c0-$c1 ../.venv/bin/python hex_r3_scan.py --out $OUT --points "$REF"
    taskset -c $c0-$c1 ../.venv/bin/python hex_r3_scan.py --out $OUT --D 0 0.05 -0.05 ) > $OUT/log_r$i.txt 2>&1 &
  sleep 3
done
wait
echo ALLDONE >> $OUT/log_r0.txt
