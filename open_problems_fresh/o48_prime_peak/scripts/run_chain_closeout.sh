#!/usr/bin/env bash
# O48 closeout — 補正典 logs（scripts 11-65 缺 log）
# 逐支重跑 scripts/11..65，輸出存 logs/<NN>_q1_*.out
# 日期: 2026-10-10（closeout 盤點）
set -u
cd "$(dirname "$0")/.."

mkdir -p logs
FAILED=0
for s in $(ls scripts/*.py | sort -V); do
    bn=$(basename "$s" .py)
    log="logs/${bn}.out"
    [ ${bn:0:2} -lt 11 ] && continue   # 01-10 已有 log
    # 已有 log 且非空則跳過（補缺，唔覆寫）
    if [ -s "$log" ]; then
        echo "SKIP $bn (log exists)"
        continue
    fi
    echo "RUN  $bn"
    if /usr/bin/python3 "$s" > "$log" 2>&1; then
        echo "  OK  $bn (exit 0)"
    else
        echo "  ERR $bn (exit $?)"
        FAILED=$((FAILED+1))
    fi
done
echo "=== DONE: FAILED=$FAILED ==="
exit $FAILED