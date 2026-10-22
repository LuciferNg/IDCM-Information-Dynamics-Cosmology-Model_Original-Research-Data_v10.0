#!/usr/bin/env python3
"""O215 回報處理後最終驗證"""
import os, sys

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o38_kappa_prediction"
os.chdir(BASE)

print("=== O215 回報處理最終驗證 ===")
checks = []

# 1. docs/02 存在 + 內容
d2 = open("docs/02_o215_report.md").read()
ok1 = "O215" in d2 and "66.83" in d2 and "κ̃² = 88" in d2 and "19/450" in d2 and "3/60" in d2
checks.append(ok1)
print(f"  docs/02_o215_report.md 完整: {'✅' if ok1 else '❌'}")

# 2. scripts 10/11 存在
ok2 = os.path.exists("scripts/10_o215_adjudication.py") and os.path.exists("scripts/11_o215_impact.py")
checks.append(ok2)
print(f"  scripts/10,11 存在: {'✅' if ok2 else '❌'}")

# 3. final_result 有 O215 標記
fr = open("final_result.md").read()
ok3 = "O215" in fr and "剩餘開放" in fr
checks.append(ok3)
print(f"  final_result O215 標記: {'✅' if ok3 else '❌'}")

# 4. 01_problem_record 有 O215 回報行 + docs/02 索引
rec = open("01_problem_record.md").read()
ok4 = "O215 回報" in rec and "02_o215_report" in rec and "10_o215_adjudication" in rec
checks.append(ok4)
print(f"  01_problem_record O215 更新: {'✅' if ok4 else '❌'}")

# 5. docs/01 冇被污染 (冇 O215 內容混入舊記錄)
d1 = open("docs/01_derivation_record.md").read()
ok5 = "O215" not in d1
checks.append(ok5)
print(f"  docs/01 冇污染 (禁回溯改寫): {'✅' if ok5 else '❌'}")

# 6. 原有 scripts 01-09 仍 PASS
import subprocess
ok6 = True
for i in ["01_kappa2_numerical", "02_kappa_structure", "03_kappa_meaning", "04_independent_prediction",
          "05_verification_audit", "06_doc_audit", "07_legacy_closure", "08_final_cross_verify", "09_session_final"]:
    r = subprocess.run([sys.executable, f"scripts/{i}.py"], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        ok6 = False
        print(f"  ❌ {i} exit={r.returncode}")
checks.append(ok6)
print(f"  scripts/01-09 全部 PASS: {'✅' if ok6 else '❌'}")

print(f"\n  最終: {sum(checks)}/{len(checks)}")
sys.exit(0 if all(checks) else 1)
