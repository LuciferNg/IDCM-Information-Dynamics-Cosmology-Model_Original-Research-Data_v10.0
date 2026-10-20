#!/usr/bin/env bash
# ============================================================
# O5 FULL RERUN — RESUME from 06 (02-05 done)
# ============================================================
# 02-05 已完成 (log: full_rerun_20260817_113326.log)
# 06 喺舊 int64 版本 OOM — 已改 int32 (峰值 2.5GB)
# 繼續: 06 → 07 → 08 → 09 → 10 → 11
# ============================================================

set -u

BASE="/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare"
LOG="$BASE/data/full_rerun_resume_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$BASE/data"

# ⚠️ 坑: background PATH 搵 /home/wsl/miniconda/bin/python3 (冇 numpy)
PY="/usr/bin/python3"
"$PY" -c "import numpy, healpy, scipy, astropy" 2>/dev/null || {
  echo "ERROR: interpreter missing deps" | tee "$LOG"; exit 1
}

SCRIPTS=(
  "06_cross_scale_match.py"
  "07_verify.py"
  "08_node9_deepdive.py"
  "09_node9_null.py"
  "10_node9_hop.py"
  "11_node9_crossmap.py"
)

echo "==============================================================" | tee -a "$LOG"
echo "O5 FULL RERUN RESUME START: $(date)" | tee -a "$LOG"
echo "Interpreter: $PY" | tee -a "$LOG"
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
    echo "    ⚠️  script 停止 — 檢查 log 尾部" | tee -a "$LOG"
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
