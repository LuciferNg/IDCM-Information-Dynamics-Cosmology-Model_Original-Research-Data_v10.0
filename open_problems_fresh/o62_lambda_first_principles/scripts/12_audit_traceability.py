#!/usr/bin/env python3
"""
O62 AUDIT 02: docs traceability 檢查
=====================================
檢查 docs/01 + SESSION_START + 01_problem_record 有冇覆蓋所有 script 發現:
  - 每個 script 嘅關鍵數字有冇喺 docs 出現
  - 每個 script 名有冇 traceable
"""
import os, re, sys

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o62_lambda_first_principles"

# 要檢查嘅關鍵發現 (script → 數字)
KEY_FINDINGS = {
    "01": ["F(γ)", "264.08", "Y(γ) kernel", "M_rank", "32"],
    "02": ["264.082129", "283.082", "0.00245", "44−F₈−B", "19"],
    "03": ["random t", "0.0000", "stat", "283.0821"],
    "04": ["264.0821", "283.0821", "0.00245", "8/8", "第一性原理"],
    "05": ["P̂", "row-norm", "corr", "-0.9947", "support"],
    "06": ["-0.9947", "a = -0.478", "熵", "30.79", "18.03"],
    "07": ["kernel(A)", "W ≡ 0", "flat", "GVW", "通量"],
    "08": ["F_diag", "728.48", "block", "3×12"],
    "09": ["264", "3×88", "Σγ_even", "88", "對偶鏈"],
    "10": ["283.082129", "0.00245", "0/10000", "0/500", "唯一命中"],
}

passed = 0
failed = 0

for script, keys in KEY_FINDINGS.items():
    print(f"\n=== scripts/{script} ===")
    for key in keys:
        # 喺 docs/01 搵
        found_docs = False
        found_session = False
        for fname in ["docs/01_lambda_first_principles_closure.md", "SESSION_START.md", "01_problem_record.md"]:
            fpath = os.path.join(BASE, fname)
            if not os.path.exists(fpath):
                continue
            content = open(fpath, encoding="utf-8").read()
            if key in content:
                if "docs" in fname:
                    found_docs = True
                else:
                    found_session = True
        if found_docs or found_session:
            locs = []
            if found_docs: locs.append("docs/01")
            if found_session: locs.append("SESSION_START")
            print(f"  ✅ '{key}' → {', '.join(locs)}")
            passed += 1
        else:
            print(f"  ❌ '{key}' 冇 traceable!")
            failed += 1

print(f"\n{'='*60}")
print(f"AUDIT 02: Passed {passed}, Failed {failed}")
print(f"{'='*60}")
if failed > 0:
    sys.exit(1)
print("🎉 全部發現 traceable!")
