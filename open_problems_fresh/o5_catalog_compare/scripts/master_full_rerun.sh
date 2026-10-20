#!/usr/bin/env bash
# ============================================================
# O5 MASTER FULL RERUN — no timeout, full re-smoothing from raw
# ============================================================
# 調律者指令 (2026-08-17): 所有曾因超時而優化過嘅測試重新跑一次
# 完整版 — 唔用 cache (已改名 .prefull), 唔設 timeout, 只監控
# 有冇因 bug 導致停止運作。
#
# 順序: 02 (SMICA 目錄) → 03 (匹配) → 04 (1000 旋轉顯著性)
#       → 05 (尺度) → 06 (交叉尺度) → 07 (驗證) → 08 (node9 多尺度)
#       → 09 (node9 null) → 10 (node9 hop) → 11 (node9 三地圖)
# ============================================================

set -u  # 未定義變數即 error (但唔 set -e, 我哋要逐個 script 捕獲 exit code)

BASE="/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare"
LOG="$BASE/data/full_rerun_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$BASE/data"

# ⚠️ 坑 (2026-08-17): background process 嘅 PATH 優先搵 /home/wsl/miniconda/bin/python3
#    (冇 numpy/healpy)。Foreground 先係 /usr/bin/python3。必須用絕對路徑。
PY="/usr/bin/python3"
"$PY" -c "import numpy, healpy, scipy, astropy" 2>/dev/null || {
  echo "ERROR: $PY 缺少 numpy/healpy/scipy/astropy — 搵另一個 interpreter" | tee "$LOG"
  for cand in /usr/bin/python3.13 /usr/local/bin/python3; do
    if "$cand" -c "import numpy, healpy" 2>/dev/null; then PY="$cand"; break; fi
  done
  echo "Using interpreter: $PY" | tee -a "$LOG"
}

SCRIPTS=(
  "02_smica_catalog.py"
  "03_match_nodes.py"
  "04_significance.py"
  "05_scale_check.py"
  "06_cross_scale_match.py"
  "07_verify.py"
  "08_node9_deepdive.py"
  "09_node9_null.py"
  "10_node9_hop.py"
  "11_node9_crossmap.py"
)

echo "==============================================================" | tee -a "$LOG"
echo "O5 FULL RERUN START: $(date)" | tee -a "$LOG"
echo "Cache 狀態: 所有 /tmp/smica2_smooth*.fits 已改名 .prefull" | tee -a "$LOG"
echo "==============================================================" | tee -a "$LOG"

FAILED=0
for s in "${SCRIPTS[@]}"; do
  echo "" | tee -a "$LOG"
  echo ">>> [$s] START: $(date +%H:%M:%S)" | tee -a "$LOG"
  start_ts=$(date +%s)

  cd "$BASE"
  "$PY" "scripts/$s" >> "$LOG" 2>&1
  rc=$?

  end_ts=$(date +%s)
  dur=$((end_ts - start_ts))

  if [ $rc -eq 0 ]; then
    echo ">>> [$s] DONE (exit=0, ${dur}s): $(date +%H:%M:%S)" | tee -a "$LOG"
  else
    echo ">>> [$s] FAILED (exit=$rc, ${dur}s): $(date +%H:%M:%S)" | tee -a "$LOG"
    echo "    ⚠️  script 停止 — 檢查 log 尾部搵 bug" | tee -a "$LOG"
    FAILED=1
    break
  fi
done

echo "" | tee -a "$LOG"
echo "==============================================================" | tee -a "$LOG"
if [ $FAILED -eq 0 ]; then
  echo "ALL SCRIPTS COMPLETED SUCCESSFULLY: $(date)" | tee -a "$LOG"
else
  echo "RUN ABORTED — SCRIPT FAILURE: $(date)" | tee -a "$LOG"
fi
echo "Log: $LOG" | tee -a "$LOG"
echo "==============================================================" | tee -a "$LOG"
