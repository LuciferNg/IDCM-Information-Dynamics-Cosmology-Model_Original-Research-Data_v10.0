#!/usr/bin/env python3
"""O81 裁決最終驗證"""
import os, sys

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o38_kappa_prediction"
os.chdir(BASE)

print("=== O81 裁決最終驗證 ===")
checks = []

# 1. scripts 13/14 存在
ok1 = os.path.exists("scripts/13_o81_adjudication.py") and os.path.exists("scripts/14_verdict_consistency.py")
checks.append(ok1)
print(f"  scripts/13,14 存在: {'✅' if ok1 else '❌'}")

# 2. SESSION_START 有裁決回覆
sess = open("SESSION_START.md").read()
ok2 = "裁決回覆" in sess and "1/B⁴" in sess and "0.8583" in sess
checks.append(ok2)
print(f"  SESSION_START 裁決回覆: {'✅' if ok2 else '❌'}")

# 3. 01_problem_record 有 O81 行
rec = open("01_problem_record.md").read()
ok3 = "O81 要求" in rec and "13_o81_adjudication" in rec
checks.append(ok3)
print(f"  01_problem_record O81: {'✅' if ok3 else '❌'}")

# 4. docs/01 附錄
d1 = open("docs/01_derivation_record.md").read()
ok4 = "外部回報處理附錄" in d1 and "9.2 O81" in d1
checks.append(ok4)
print(f"  docs/01 附錄: {'✅' if ok4 else '❌'}")

# 5. final_result O81 裁決
fr = open("final_result.md").read()
ok5 = "O81 裁決" in fr and "1/256" in fr
checks.append(ok5)
print(f"  final_result O81: {'✅' if ok5 else '❌'}")

print(f"\n  最終: {sum(checks)}/{len(checks)}")
sys.exit(0 if all(checks) else 1)
