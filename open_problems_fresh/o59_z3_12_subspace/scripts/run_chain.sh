#!/bin/bash
# O59 closeout rerun driver — 全鏈重跑scripts 01-31, logs入 logs/, 產物JSON落 data/
# 用法: bash run_chain.sh [--execute]   (預設 dry-run)
set -u
cd "$(dirname "$0")/.." || exit 1
O="$(basename "$(pwd)")"
LOGDIR="logs"
mkdir -p "$LOGDIR"

MODE="${1:-}"
if [ "$MODE" != "--execute" ]; then
    echo "DRY-RUN mode — use --execute to actually run"
    for f in scripts/[0-9]*.py; do
        echo "  run logs/$(basename "$f" .py).out  /usr/bin/python3 \"$f\""
    done
    exit 0
fi

echo "=== O59 full chain rerun: $(date '+%Y-%m-%d %H:%M:%S') ==="
fail=0
for f in scripts/[0-9]*.py; do
    name="$(basename "$f")"
    log="$LOGDIR/${name%.py}.out"
    echo "--- run $name → $log ---"
    if /usr/bin/python3 "$f" > "$log" 2>&1; then
        rc=0
    else
        rc=$?
    fi
    # append RESULT line: rc + tail PASS summary (last line with [0-9]+ PASS)
    tail_line="$(grep -oE '[0-9]+ PASS, [0-9]+ FAIL|[0-9]+/[0-9]+ PASS|[0-9]+ PASS' "$log" | tail -1)"
    echo "RESULT: rc=$rc | $tail_line" >> "$log"
    echo "  → rc=$rc | $tail_line"
    if [ "$rc" -ne 0 ]; then fail=$((fail+1)); fi
done
echo "=== chain done $(date '+%Y-%m-%d %H:%M:%S') — failed scripts: $fail ==="
exit 0