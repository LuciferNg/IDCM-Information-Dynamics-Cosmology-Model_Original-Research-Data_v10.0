#!/usr/bin/env bash
# O121 — driver of record (skill `idcm-closeout` §4.9⑥)
# =====================================================
# 用途: 一次過以正典順序重跑整條推導鏈, 每支寫入 logs/<name>.out。
# 用法:
#   bash scripts/run_chain.sh              # dry-run (預設) — 只列出將跑嘅指令
#   bash scripts/run_chain.sh --execute    # 真跑
#   bash scripts/run_chain.sh --execute --from 11   # 由 scripts/11 起跑
#
# 硬性約束 (§9.2):
#   · 一律 foreground; 解譯器 pin 絕對路徑 /usr/bin/python3 (WSL background shell
#     之 `python3` 會解到 miniforge, 缺 numpy/healpy)。
#   · stderr 一定入 log: `> log 2>&1`。
#   · 每支腳本之正典 log 必須帶 `^RESULT:` 行 (診斷腳本 _probe_* 按設計豁免)。
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE="$(dirname "$HERE")"
PY=/usr/bin/python3
EXEC=0; FROM=1
for a in "$@"; do
  case "$a" in
    --execute) EXEC=1 ;;
    --from) shift ;;
    [0-9]*) FROM="$a" ;;
  esac
done

# 正典鏈序 (由 §4.9① 之 docs/SCRIPT_CHAIN.md 決定)
CHAIN=(
  01_tpipe_dag_spectrum 02_bh_formation 03_microstate_count 04_hawking_radiation
  05_information_paradox 06_cosmic_horizon 07_transceiver_mechanism 08_gravity_metric
  09_schwarzschild 10_singularity_resolution audit_independent
  11_g8_handover_verify 12_tau_rec_derivation 13_g8_three_items 14_g8_deepening
  15_prediction_register 16_tau_ref_volume_audit 17_reeval_corrected 18_three_final
  19_closeout_audit
)

rc=0; n=0
for s in "${CHAIN[@]}"; do
  if [ "$s" = "audit_independent" ]; then num=10; else num="${s%%_*}"; fi
  if [ "$num" -lt "$FROM" ]; then continue; fi
  n=$((n+1))
  printf '[%2d] %-32s -> logs/%s.out\n' "$n" "scripts/$s.py" "$s"
  if [ "$EXEC" = "1" ]; then
    ( cd "$BASE" && "$PY" "scripts/$s.py" > "logs/$s.out" 2>&1 )
    e=$?
    res="$(grep -m1 '^RESULT:' "$BASE/logs/$s.out" 2>/dev/null || echo '(no RESULT line)')"
    printf '     exit=%s  %s\n' "$e" "$res"
    [ "$e" -ne 0 ] && rc=1
  fi
done
if [ "$EXEC" = "0" ]; then
  echo "--- DRY RUN: $n 支; 加 --execute 真跑 ---"
else
  echo "--- 完成 $n 支; 總 exit=$rc ---"
fi
exit $rc
