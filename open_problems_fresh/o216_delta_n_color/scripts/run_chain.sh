#!/usr/bin/env bash
# O216 scripts/run_chain.sh — driver of record（§4.9 ⑥）
# 預設 dry-run；--execute 先真跑。確定性 scripts ⟹ 重跑輸出應與 logs/ 正典一致。
# 用法: ./run_chain.sh [--execute]
set -u
cd "$(dirname "$0")/.."
EXEC=0
if [ "${1:-}" = "--execute" ]; then EXEC=1; fi

declare -a SCRIPTS=(01_density_baseline.py 02_color_routes.py 03_nogo_barriers.py 04_AUDIT_independent_recheck.py)

for s in "${SCRIPTS[@]}"; do
    nm="${s%.py}"
    echo "RUN $nm"
    if [ $EXEC -eq 1 ]; then
        PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 "scripts/$s" > "logs/${nm}.out" 2>&1
        rc=$?
        # 正典 log 帶 RESULT: 行（由尾行總結抽）
        res=$(grep -oE "[0-9]+ / FAIL [0-9]+|[0-9]+ / [0-9]+" "logs/${nm}.out" | tail -1)
        echo "RESULT: $nm rc=$rc ($res)" >> "logs/${nm}.out"
        echo "  -> rc=$rc RESULT=$res"
    else
        echo "  (dry-run; --execute 先真跑)"
    fi
done
[ $EXEC -eq 1 ] && echo "CHAIN DONE" || echo "(dry-run only)"