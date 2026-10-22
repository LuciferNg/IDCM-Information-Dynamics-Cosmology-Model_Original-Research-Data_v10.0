#!/usr/bin/env bash
# O229 全鏈 driver of record（§4.9⑥；預設 dry-run，--execute 才真跑）
# 放 verify/（唔以 scripts/NN_ 命名）⟹ E1/E2 名單不受影響。
# ⚠️ 2026-10-03 教訓：chain rerun 會覆寫正典 log —— 執行前必須先備份 logs/（cp -a logs/ logs_prechain_<date>/）
# 用法: bash verify/run_full_chain.sh [--execute]
set -u
D="$(cd "$(dirname "$0")/.." && pwd)"
SCRATCH="$D/verify/.chain_tmp"
mkdir -p "$SCRATCH"
trap 'rm -rf "$SCRATCH"' EXIT   # in-O scratch，結束即清 ⟹ 唔入 MANIFEST、唔入 path_hygiene WRITE
EXECUTE=0; [ "${1:-}" = "--execute" ] && EXECUTE=1
cd "$D" || exit 2
mapfile -t SCRIPTS < <(ls scripts/[0-9][0-9]_*.py | sort)
echo "O229 全鏈重跑 $(date '+%Y-%m-%d %H:%M:%S') ｜ dry-run=${EXECUTE/1/0}" > "$SCRATCH/chain05.txt"
gates=""
for s in "${SCRIPTS[@]}"; do
    base="$(basename "$s" .py)"
    num="${base:0:2}"
    log="$(/usr/bin/python3 - "$num" <<'PY'
import json,sys,os
m=json.load(open("MANIFEST.json"))["files"]
n=sys.argv[1]
cands=[k for k in m if k.startswith("logs/"+n+"_") and k.endswith(".out")]
print(cands[0] if cands else "")
PY
)"
    if [ -z "$log" ]; then echo "  $base: 無對應 log（跳過）" >> "$SCRATCH/chain05.txt"; continue; fi
    if [ "$EXECUTE" = "1" ]; then
        # 完成後先寫正典 log（temp 重定向 ⟹ 核對器執行期間讀到舊版全 log，唔會被截斷）
        tmp="$SCRATCH/chain_one_$$.txt"
        timeout 900 /usr/bin/python3 "$s" > "$tmp" 2>&1; rc=$?
        cp "$tmp" "$log"
        res=$(grep -E "^RESULT:" "$log" | tail -1)
    else
        rc="--"; res=$(grep -E "^RESULT:" "$log" | tail -1)
    fi
    printf "  %-34s rc=%-3s %s\n" "$base" "$rc" "$res" >> "$SCRATCH/chain05.txt"
    gates="$gates $num"
done
if [ "$EXECUTE" = "1" ]; then
    echo "--- 仲裁器 ---" >> "$SCRATCH/chain05.txt"
    timeout 1800 /usr/bin/python3 verify/third_route_arbiter.py > "$SCRATCH/arb_chain.txt" 2>&1
    echo "  third_route_arbiter rc=$?  $(grep -E '^RESULT:|差異原子數' verify/third_route_arbiter.out | tr '\n' ' ')" >> "$SCRATCH/chain05.txt"
fi
echo "覆蓋: $(echo $gates | tr ' ' '\n' | grep -c .) 支腳本" >> "$SCRATCH/chain05.txt"
[ "$EXECUTE" = "1" ] && cp "$SCRATCH/chain05.txt" logs/chain_05_full_rerun.out
cat "$SCRATCH/chain05.txt"
