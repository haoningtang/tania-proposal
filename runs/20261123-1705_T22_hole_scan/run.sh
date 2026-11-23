#!/usr/bin/env bash
cd "$(dirname "$0")/../../inverse"
OUT=../runs/20261123-1705_T22_hole_scan
PTS="0.22,0,280,380;0.28,0,280,380;0.20,0,280,380;0.30,0,280,380;0.22,0.05,280,380;0.28,0.05,280,380;0.20,0.05,280,380;0.30,0.05,280,380;0.22,-0.05,280,380;0.28,-0.05,280,380;0.20,-0.05,280,380;0.30,-0.05,280,380;0.22,0.03,280,380;0.28,0.03,280,380;0.20,0.03,280,380;0.30,0.03,280,380;0.22,-0.03,280,380;0.28,-0.03,280,380;0.20,-0.03,280,380;0.30,-0.03,280,380"
( export XLA_PYTHON_CLIENT_PREALLOCATE=false; taskset -c 0-3 ../.venv/bin/python hex_r3_scan.py --out $OUT --lo 1350 --hi 1700 --points "$PTS" ) > $OUT/log_gpu.txt 2>&1 &
sleep 5
export JAX_PLATFORMS=cpu OMP_NUM_THREADS=4 XLA_FLAGS="--xla_cpu_multi_thread_eigen=true intra_op_parallelism_threads=4"
for i in 0 1 2 3 4 5 6; do
  c0=$((4+4*i)); c1=$((c0+3))
  ( taskset -c $c0-$c1 ../.venv/bin/python hex_r3_scan.py --out $OUT --lo 1350 --hi 1700 --points "$PTS" ) > $OUT/log_s$i.txt 2>&1 &
  sleep 3
done
wait
echo ALLDONE >> $OUT/log_s0.txt
