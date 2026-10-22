#!/bin/bash
# 重跑全部 O158 scripts 驗證
cd /home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o158_nd_pm_ngen_cluster || exit 1
for s in 01 02 03 04 07 08 09 10 11 12 14 17 18; do
  r=$(python3 scripts/${s}_*.py 2>&1 | grep -E "RESULT:" | head -1)
  echo "scripts/$s: $r"
done
echo "--- 特殊 scripts ---"
echo "scripts/05: $(python3 scripts/05_tension_exhaustion.py 2>&1 | grep 'RESULT:')"
echo "scripts/13: $(python3 scripts/13_audit_all_docs.py 2>&1 | grep 'AUDIT RESULT:')"
echo "scripts/16: $(python3 scripts/16_audit_docs_11_12.py 2>&1 | grep 'AUDIT RESULT:')"
echo "scripts/19: $(python3 scripts/19_mu_e_two_step_iteration.py 2>&1 | grep 'RESULT:')"
