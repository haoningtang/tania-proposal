#!/bin/sh
# runs after the six 80/96 chains: 200/192 at g = g0 (all theta) and the +-theta symmetry check (item 5)
cd /home/haoning/tania-proposal/inverse
while pgrep -f "wedge_table.py --out ../runs/20261122-0600_T18a_wedge_table/chains --struct" >/dev/null; do sleep 30; done
run() { lo=$1; hi=$2; shift 2; JAX_PLATFORMS=cpu OMP_NUM_THREADS=8 XLA_FLAGS="--xla_cpu_multi_thread_eigen=true intra_op_parallelism_threads=8" taskset -c $lo-$hi ../.venv/bin/python wedge_table.py "$@"; }
run 0 7 --out ../runs/20261122-0600_T18a_wedge_table/chains --struct T9b --g0 380 --pols TE TM --n_terms 200 --ngrid 192 --only_g0 > ../runs/20261122-0600_T18a_wedge_table/chains/log_hires_T9b_380.txt 2>&1 &
run 8 15 --out ../runs/20261122-0600_T18a_wedge_table/chains --struct T9b --g0 500 --pols TE TM --n_terms 200 --ngrid 192 --only_g0 --q0 3000 > ../runs/20261122-0600_T18a_wedge_table/chains/log_hires_T9b_500.txt 2>&1 &
run 16 23 --out ../runs/20261122-0600_T18a_wedge_table/chains --struct prelim --g0 200 --pols TM --n_terms 200 --ngrid 192 --only_g0 > ../runs/20261122-0600_T18a_wedge_table/chains/log_hires_prelim_200.txt 2>&1 &
run 24 29 --out ../runs/20261122-0600_T18a_wedge_table --mode symmetry > ../runs/20261122-0600_T18a_wedge_table/log_symmetry.txt 2>&1 &
wait
