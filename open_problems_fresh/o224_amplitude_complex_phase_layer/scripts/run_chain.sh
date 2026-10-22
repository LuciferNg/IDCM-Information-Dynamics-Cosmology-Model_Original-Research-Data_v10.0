#!/bin/bash
# ============================================================================================
# O224 scripts/run_chain.sh -- DRIVER OF RECORD for the whole O224 derivation chain (rounds 1-5).
#
# WHY THIS FILE EXISTS: the round-1..5 invocations were issued interactively, so the *command
# lines* (unlike the scripts, the artefacts and the logs) were not preserved anywhere executable.
# This driver reconstructs the chain from the scripts' own docstring usage blocks
# (`python3 scripts/<name>.py [flags]`) and from logs/ file names that were produced at the time.
#
# SAFETY: this script is DRY-RUN BY DEFAULT.  Running it bare only PRINTS the chain (verifiable,
# side-effect free).  Pass --execute to actually re-run the chain -- which OVERWRITES data/*.json
# and logs/*.out (all re-runs are deterministic in their decision projections; see docs/06).
#
# ARG ORDER = the order the chain was built.  Fresh reproduction from a clean checkout needs
# only data/frozen/* (the external O222 inputs) and the scripts themselves.
# ============================================================================================
set -uo pipefail
cd "$(dirname "$(readlink -f "$0")")/.." || exit 1
ROOT="$(pwd)"
PY=/usr/bin/python3
EXEC=0
[ "${1:-}" = "--execute" ] && EXEC=1

run() {                       # run <log> <script> [args...]
  local log="$1"; shift
  if [ "$EXEC" = "1" ]; then
    echo "[run ] $PY $* > $log"
    "$PY" "$@" > "$log" 2>&1 || { echo "[FAIL] $* (see $log)"; exit 1; }
  else
    printf '[dry ] %s %s > %s\n' "$PY" "$*" "$log"
  fi
}

echo "=== O224 chain (rounds 1-5) from $ROOT  [mode: $([ $EXEC = 1 ] && echo EXECUTE || echo dry-run)]"
echo
echo "--- round 1: contract, re-lock of the frozen machine, the five judgment items, audit"
run logs/00_contract.out          scripts/00_contract.py
run logs/01_relock.out            scripts/01_relock.py
run logs/02_phase.out             scripts/02_phase.py
run logs/03_tensor.out            scripts/03_tensor.py
run logs/04_multiparty.out        scripts/04_multiparty.py
run logs/04b_window.out           scripts/04b_window.py
run logs/05_valueset.out          scripts/05_valueset.py
run logs/06_escape.out            scripts/06_escape.py
run logs/07_audit.out             scripts/07_audit.py
echo
echo "--- round 2: the four round-1 residuals, then re-audit"
run logs/08_residuals.out         scripts/08_residuals.py
run logs/07_audit.out             scripts/07_audit.py
echo
echo "--- round 3: E4 layer, E5 layer, determinism, re-audit"
run logs/09_global_n.out          scripts/09_global_n.py
run logs/10_e5.out                scripts/10_e5.py
run logs/11_determinism.out       scripts/11_determinism.py
run logs/07_audit.out             scripts/07_audit.py
echo
echo "--- round 4: 12 shards over the party-1 ordered-pair index, then aggregate + addenda"
for k in 0 1 2 3 4 5 6 7 8 9 10 11; do
  printf -v kk '%02d' "$k"
  run "logs/12_shard_${kk}.out"   scripts/12_n4_global.py --shard "$k" 12
done
run logs/12_n4_global.out         scripts/12_n4_global.py
run logs/13_party_window.out      scripts/13_party_window.py
run logs/14_census_exact.out      scripts/14_census_exact.py
run logs/15_anti_convention.out   scripts/15_anti_convention.py
run logs/11_determinism.out       scripts/11_determinism.py
run logs/07_audit.out             scripts/07_audit.py
echo
echo "--- round 5: cross-engine checks FIRST, then 8 mutually exclusive ranges, merge, aggregate"
run logs/18_check_j1.out          scripts/18_windows_global_jit.py --check
run logs/18_j6_bmax2_pairs0_24.out scripts/18_windows_global_jit.py --check-range 0 24 2
run logs/17_check_g1.out          scripts/17_windows_global_gpu.py --check
for r in "0 480" "480 960" "960 1440" "1440 1920" "1920 2400" "2400 2880" "2880 3360" "3360 3844"; do
  run logs/18_run_r5.log          scripts/18_windows_global_jit.py --run-range $r
done
run logs/18_merge_revB.out        scripts/18_windows_global_jit.py --merge
run logs/16_aggregate.out         scripts/16_windows_global.py --aggregate
run logs/16_smoke_shard0of3844.out scripts/16_windows_global.py --shard 0 3844
echo
echo "--- round 5 close-out: engine measurements, chain audit"
run logs/18_engine_measure.out    scripts/measure_engines.py
run logs/19_chain_audit.out       scripts/chain_audit.py
echo
if [ "$EXEC" = "1" ]; then
  echo "=== chain re-run complete; re-verify with: bash scripts/run_chain.sh (dry-run) and"
  echo "    $PY scripts/07_audit.py   (A15/A16 re-check the artefacts and this chain)"
else
  echo "=== DRY RUN ONLY (no file written).  Re-run with --execute to rebuild everything."
fi
