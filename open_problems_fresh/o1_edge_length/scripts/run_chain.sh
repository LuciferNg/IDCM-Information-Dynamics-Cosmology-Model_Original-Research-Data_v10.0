#!/usr/bin/env bash
# ==============================================================================
# O1/edge-length — driver of record (closeout §4.9 ⑥)
# ==============================================================================
# 用法:
#   ./run_chain.sh              # dry-run: 只列出將執行嘅命令 (預設)
#   ./run_chain.sh --execute    # 真跑全部腳本 + 寫 log
#
# 次序 = 推導時序 (01→10 原始, 11 修正 data, 12 獨立驗證)
# ⚠️ 11 必須排喺 07 之後: 07 有已知 L121 loop 變量覆蓋 bug, 會把
#    data/edge_formula.txt 嘅 theta_formula 寫成群元素角 (113.54°);
#    11 負責修正該欄並備份原檔。12 係獨立 verifier, 零 import 01-11。
#
# log 位置: logs/NN_<script>.out   (scripts 相對路徑 → O 目錄內執行)
# ==============================================================================
set -uo pipefail

PY=/usr/bin/python3          # 一律絕對解譯器 (background shell 嘅 python3 係 miniforge, 缺 numpy/mpmath)
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGS="$DIR/logs"
EXECUTE=0
[ "${1:-}" = "--execute" ] && EXECUTE=1

run () {
  local name="$1"; shift
  local script="$1"; shift
  local log="$LOGS/${name}.out"
  local cmd="$PY $DIR/scripts/$script $*"
  if [ "$EXECUTE" -eq 1 ]; then
    mkdir -p "$LOGS"
    echo "── RUN  $script → logs/${name}.out"
    ( cd "$DIR" && timeout 600 $PY "scripts/$script" "$@" ) > "$log" 2>&1
    local rc=$?
    local res
    res=$(grep -E '^RESULT:|全部驗證通過|全部數字驗證通過|✅ 已存|✅ 已修正' "$log" | tail -1)
    echo "   rc=$rc  ${res:-（無 RESULT 行 — 診斷類腳本）}"
    return $rc
  else
    echo "   $cmd"
  fi
}

echo "=============================================================================="
echo "O1/edge-length derivation chain — $( [ "$EXECUTE" -eq 1 ] && echo 'EXECUTE' || echo 'DRY-RUN (加 --execute 真跑)' )"
echo "=============================================================================="

# ── 原始推導鏈 (2026-08-16 14:50 → 15:02) ──
run 01_edge_measure       01_edge_measure.py
run 02_formula_search     02_formula_search.py
run 03_seed_dependence    03_seed_dependence.py
run 04_rotation_test      04_rotation_test.py
run 05_exact_formula      05_exact_formula.py
run 06_group_theory       06_group_theory.py
run 07_edge_formula_verify 07_edge_formula_verify.py
run 08_verify_closure     08_verify_closure.py
run 09_delta_formula      09_delta_formula.py
run 10_delta_group_word   10_delta_group_word.py

# ── 審計層 (2026-10-22) ──
run 11_audit_fix_theta_field 11_audit_fix_theta_field.py   # ⚠️ 必須在 07 之後
run 12_audit_independent     12_audit_independent.py

echo "=============================================================================="
if [ "$EXECUTE" -eq 1 ]; then
  echo "全部腳本執行完畢。核對要點:"
  echo "  · 08_verify_closure   → 全部驗證通過 (8/8)"
  echo "  · 11_audit_fix        → theta_formula=26.09135714 (修正 07 bug)"
  echo "  · 12_audit_independent → RESULT: 21/21 PASS"
else
  echo "DRY-RUN 完畢 — 以上 12 支腳本。加 --execute 真跑。"
fi
echo "=============================================================================="
