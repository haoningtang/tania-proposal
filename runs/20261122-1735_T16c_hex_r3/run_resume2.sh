#!/usr/bin/env bash
# 2026-11-23 10:40 restart after WSL reboot (~08:20): remaining 21 points of Delta {0, +-0.05} x 8 (t, gap) pairs. 7 procs x 4 threads.
cd "$(dirname "$0")/../../inverse"
OUT=../runs/20261122-1735_T16c_hex_r3
export JAX_PLATFORMS=cpu OMP_NUM_THREADS=4 XLA_FLAGS="--xla_cpu_multi_thread_eigen=true intra_op_parallelism_threads=4"
for i in 0 1 2 3 4 5 6; do
  c0=$((4+4*i)); c1=$((c0+3))
  ( taskset -c $c0-$c1 ../.venv/bin/python hex_r3_scan.py --out $OUT --D 0 0.05 -0.05 ) > $OUT/log_s$i.txt 2>&1 &
  sleep 3
done
wait
echo ALLDONE >> $OUT/log_s0.txt
