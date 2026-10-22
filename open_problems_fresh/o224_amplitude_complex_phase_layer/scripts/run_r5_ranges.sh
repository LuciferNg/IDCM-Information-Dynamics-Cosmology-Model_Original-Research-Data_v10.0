#!/bin/bash
# O224 round-5 launcher: exact global extremes of all five Bell windows of n=4 Mermin over the whole
# 62^8 space, by the verified Numba-JIT engine (scripts/18_windows_global_jit.py, J1 all-OK against the
# numpy reduced path AND the numpy FULL 62^4 enumeration on 136 declared groups, J6 range-aggregation
# all-OK against the numpy per-pair path).
#
# Eight disjoint pair ranges (each a multiple of 12, so the strided shard assignment p % 12 == k stays
# exact); every range writes a checkpoint npz; the last steps merge the checkpoints into the 12 shard
# artefacts and run the round-4 aggregate (which re-verifies every winner by the FULL 62^4 CPU
# enumeration and by the direct 8-term evaluation).
cd /home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o224_amplitude_complex_phase_layer || exit 1
LOG=logs/18_run_r5.log
: > "$LOG"
for R in "0 480" "480 960" "960 1440" "1440 1920" "1920 2400" "2400 2880" "2880 3360" "3360 3844"; do
  set -- $R
  echo "=== range [$1,$2) start $(date -Is)" >> "$LOG"
  /usr/bin/python3 scripts/18_windows_global_jit.py --run-range "$1" "$2" >> "$LOG" 2>&1
  echo "=== range [$1,$2) exit=$? end $(date -Is)" >> "$LOG"
done
echo "=== merge $(date -Is)" >> "$LOG"
/usr/bin/python3 scripts/18_windows_global_jit.py --merge >> "$LOG" 2>&1
echo "=== merge exit=$? $(date -Is)" >> "$LOG"
echo "=== aggregate $(date -Is)" >> "$LOG"
/usr/bin/python3 scripts/16_windows_global.py --aggregate >> "$LOG" 2>&1
echo "=== aggregate exit=$? $(date -Is)" >> "$LOG"
echo "=== DONE $(date -Is)" >> "$LOG"
tail -40 "$LOG"
