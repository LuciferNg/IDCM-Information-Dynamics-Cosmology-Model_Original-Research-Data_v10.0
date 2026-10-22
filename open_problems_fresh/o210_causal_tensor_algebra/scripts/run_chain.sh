#!/usr/bin/env bash
# O210 driver of record（skill idcm-closeout §4.9 ⑥）
# 契約：**預設 dry-run**，只印將要跑嘅劇本；`--execute` 才真跑並寫正典 log。
# 一律 pin /usr/bin/python3（背景 shell 嘅 python3 可能係 miniforge，缺 numpy/mpmath 版本不同）。
# 產物：logs/<劇本名>.out（帶 RESULT: 行，供 §4.9/C2 機械讀）。
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE="$(dirname "$HERE")"
PY=/usr/bin/python3
EXEC=0
[ "${1:-}" = "--execute" ] && EXEC=1
mkdir -p "$BASE/logs"
run () {
  local s="$1"
  if [ "$EXEC" -eq 1 ]; then
    ( cd "$BASE" && "$PY" "$HERE/$s.py" > "$BASE/logs/$s.out" 2>&1 )
    local rc=$?
    echo "[RUN ] $s.py -> logs/$s.out  (exit=$rc)"
  else
    echo "[DRY ] $s.py -> logs/$s.out"
  fi
}
echo "== O210 chain driver of record（EXEC=$EXEC，0=DRY-RUN）=="
for s in 01_closure_verify 02_type_registry 03_inbound_recompute 04_escape_period_derivation \
         05_operator_layer_selection 06_branch_charge_definition 07_ktree_two_counts \
         08_z4_bridge_definition 09_common_measure 10_audit_independent \
         11_session_chain_provenance 12_register_coverage 13_manifest; do
  run "$s"
done
echo "== 完 =="
