#!/usr/bin/env bash
# ============================================================
# run_all_full.sh — O4 完整測試 runner (無 timeout 限制) v2
# ============================================================
# 修正:
#   1. 用 /usr/bin/python3 絕對路徑 (確保 numpy/healpy/astropy)
#   2. 修正 exit code 捕獲 (唔好用 $? after echo)
#   3. 冇 timeout — 只監控有冇 bug 停止
#
# 輸出: data/full_test_results.txt
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$SCRIPT_DIR/../data"
OUT_FILE="$DATA_DIR/full_test_results.txt"
PYTHON="/usr/bin/python3"
mkdir -p "$DATA_DIR"

# 驗證 python
"$PYTHON" -c "import numpy, healpy, astropy" 2>/dev/null || { echo "ERROR: $PYTHON 缺少 numpy/healpy/astropy"; exit 1; }

echo "==========================================" | tee "$OUT_FILE"
echo "O4 完整測試 (無 timeout) — $(date)" | tee -a "$OUT_FILE"
echo "Python: $PYTHON" | tee -a "$OUT_FILE"
echo "==========================================" | tee -a "$OUT_FILE"

SCRIPTS=(
  01_bfs_fit.py
  02_group_word.py
  03_kchain.py
  04_frustration.py
  05_synthesis.py
  06_mechanism5.py
  07_verify.py
  08_wave_decay.py
  09_spectrum.py
  10_spectrum_closure.py
  11_vertex_transitive.py
  12_final_verify.py
  13_open_issues.py
  14_d1_layer.py
)

PASS=0
FAIL=0
for script in "${SCRIPTS[@]}"; do
    echo "" | tee -a "$OUT_FILE"
    echo "--- Running $script ---" | tee -a "$OUT_FILE"
    START=$(date +%s)

    # 執行 + 捕獲 exit code (唔用 $? after echo)
    "$PYTHON" "$SCRIPT_DIR/$script" >> "$OUT_FILE" 2>&1
    RC=$?

    END=$(date +%s)
    DUR=$((END - START))
    if [ "$RC" -eq 0 ]; then
        echo "[PASS] $script (${DUR}s)" | tee -a "$OUT_FILE"
        PASS=$((PASS + 1))
    else
        echo "[FAIL] $script (${DUR}s) — exit code $RC" | tee -a "$OUT_FILE"
        FAIL=$((FAIL + 1))
    fi
done

echo "" | tee -a "$OUT_FILE"
echo "==========================================" | tee -a "$OUT_FILE"
echo "完成: $PASS PASS, $FAIL FAIL — $(date)" | tee -a "$OUT_FILE"
echo "==========================================" | tee -a "$OUT_FILE"

echo ""
echo "結果已存: $OUT_FILE"
