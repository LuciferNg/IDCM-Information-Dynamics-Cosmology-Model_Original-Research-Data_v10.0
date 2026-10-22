#!/usr/bin/env python3
"""
O9 — 記錄完整性最終核對 (Record Completeness Final Check)
==========================================================
確認本 session 所有推導、發現、計算、驗證結果已正確寫入記錄文檔。
核對: 01_problem_record.md / 02_results.md / 03_open_items_results.md /
      04_cascade_mother_function.md / 07_act_dr4_correct.md
"""

import os, sys, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
passes, fails = [], []

def check_doc(fname, keywords):
    path = os.path.join(BASE, fname)
    if not os.path.exists(path):
        fails.append(f"{fname} MISSING")
        return
    with open(path) as f:
        content = f.read()
    for kw in keywords:
        if kw in content:
            passes.append(f"{fname}: {kw}")
        else:
            fails.append(f"{fname}: 缺 '{kw}'")

print("="*70)
print("O9: 記錄完整性最終核對")
print("="*70)

# 01_problem_record.md
check_doc("01_problem_record.md", [
    "✅ 已閉合",
    "m=5", "1121", "F₆=8", "F₈=21",
    "RMS = 0.83%",
    "309/309 PASS",
    "58_master_verify_final.py",
    "58_master_verify_session.py",
])

# 02_results.md
check_doc("02_results.md", [
    "🟢🟢",
    "m=5 結構閉合",
    "1121", "326", "守恆",
    "112/112 PASS",
    "RMS 0.83%",
    "CAMB 1129 = 殘餘假峰",
])

# 03_open_items_results.md
check_doc("03_open_items_results.md", [
    "7 峰截斷",
    "674", "1374",
    "偶峰", "奇峰",
    "3/14", "1/7",
])

# 04_cascade_mother_function.md
check_doc("04_cascade_mother_function.md", [
    "((k+1)/(4k−1))²",
    "零自由參數",
    "3/14", "1/7",
    "27/56", "2/3",
    "0.4%", "1.7%",
])

# 07_act_dr4_correct.md
check_doc("07_act_dr4_correct.md", [
    "800.5", "1100.5", "1400.5",
    "−1.17%", "−1.83%", "−0.81%",
    "27/56", "2/3",
    "0.4%", "1.7%",
    "作廢",
])

# 05/06 作廢標記
check_doc("05_cascade_act_verdict.md", ["作廢", "解析錯誤"])
check_doc("06_act_dr4_deep_verify.md", ["作廢", "解析錯誤"])

print(f"\nPASS: {len(passes)}  FAIL: {len(fails)}")
for f in fails:
    print(f"  ❌ {f}")
if fails:
    print("❌ 有缺漏")
    sys.exit(1)
print("✅ 記錄完整 — 所有推導/發現/計算/驗證已正確寫入文檔")
