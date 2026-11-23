#!/usr/bin/env bash
# T21: 25 points, 7 procs x 4 threads on cores 4-31 (cores 0-3 left for the T19d GPU job).
cd "$(dirname "$0")/../../inverse"
OUT=../runs/20261123-1326_T21_E1_doublet_cross
export JAX_PLATFORMS=cpu OMP_NUM_THREADS=4 XLA_FLAGS="--xla_cpu_multi_thread_eigen=true intra_op_parallelism_threads=4"
for i in 0 1 2 3 4 5 6; do
  c0=$((4+4*i)); c1=$((c0+3))
  ( taskset -c $c0-$c1 ../.venv/bin/python hex_r3_scan.py --out $OUT --lo 1440 --hi 1600 --points "0,300,380;0.02,300,380;-0.02,300,380;0.04,300,380;-0.04,300,380;0,295,380;0.02,295,380;-0.02,295,380;0.04,295,380;-0.04,295,380;0,305,380;0.02,305,380;-0.02,305,380;0.04,305,380;-0.04,305,380;0,290,380;0.02,290,380;-0.02,290,380;0.04,290,380;-0.04,290,380;0,310,380;0.02,310,380;-0.02,310,380;0.04,310,380;-0.04,310,380" ) > $OUT/log_s$i.txt 2>&1 &
  sleep 3
done
wait
echo ALLDONE >> $OUT/log_s0.txt
