#!/usr/bin/env python3
"""
G02_o4_docs_verify.py — O4 記錄文檔獨立核對 (任務 2)
=================================================================
只讀核對 o4_fib_motivation 所有文檔 (禁止跨文檔污染):
1. 關鍵數值跨文檔一致性
2. 推導鏈內容完整
3. 公式獨立重算
4. 發現/驗證/結果齊全
"""
import numpy as np
import math
import os
import re

O4 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o4_fib_motivation'
OUT = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o4_renew/data'
phi = (1 + 5**0.5) / 2

def read(fname):
    with open(os.path.join(O4, fname)) as f:
        return f.read()

print("=" * 72)
print("G02: O4 記錄文檔獨立核對 (只讀)")
print("=" * 72)

def check(name, ok, detail=""):
    print(f"  {'✅' if ok else '❌'} {name}" + (f" — {detail}" if detail else ""))

# ---------- 載入 ----------
docs = {}
for f in ['01_problem_record.md', '03_complete_record.md', '04_open_issues.md',
          '05_full_test_record.md', '06_fatal_finding.md', '07_tasks12_findings.md',
          'README.md']:
    try:
        docs[f] = read(f)
        print(f"  已載入: {f} ({len(docs[f])} chars)")
    except Exception as e:
        print(f"  ❌ 載入失敗: {f} — {e}")

print("\n=== 1. 關鍵數值跨文檔一致性 ===")
# λ₂ = φ⁻²
lambda_target = f"{phi**-2:.10f}"
lambda_checks = [
    ("01 λ₂", "0.381966011250" in docs.get('01_problem_record.md', '') or lambda_target[:10] in docs.get('01_problem_record.md', '')),
    ("03 λ₂", "0.381966011250" in docs.get('03_complete_record.md', '') or lambda_target[:10] in docs.get('03_complete_record.md', '')),
    ("README λ₂", "0.381966011250" in docs.get('README.md', '') or lambda_target[:10] in docs.get('README.md', '')),
]
for name, ok in lambda_checks:
    check(name, ok)

# ω₂ = φ⁻¹
omega_checks = [
    ("01 ω₂", "0.618033988750" in docs.get('01_problem_record.md', '') or "0.6180339887" in docs.get('01_problem_record.md', '')),
    ("03 ω₂", "0.618033988750" in docs.get('03_complete_record.md', '') or "0.6180339887" in docs.get('03_complete_record.md', '')),
    ("README ω₂", "0.618033988750" in docs.get('README.md', '') or "0.6180339887" in docs.get('README.md', '')),
]
for name, ok in omega_checks:
    check(name, ok)

# 冷斑 -134.2
for dname in ['01_problem_record.md', '03_complete_record.md', '06_fatal_finding.md', 'README.md']:
    check(f"{dname} 冷斑 -134.2", "-134.2" in docs.get(dname, '') or "134.2" in docs.get(dname, ''))

# BIC: constant 33.5 贏 φ^-d 34.8
bic_checks = [
    ("06 BIC constant 33.5", "33.5" in docs.get('06_fatal_finding.md', '')),
    ("06 BIC φ^-d 34.8", "34.8" in docs.get('06_fatal_finding.md', '')),
    ("07 BIC constant 33.5", "33.5" in docs.get('07_tasks12_findings.md', '')),
    ("README BIC constant 33.5", "33.5" in docs.get('README.md', '')),
]
for name, ok in bic_checks:
    check(name, ok)

# ΔE=0 0.526 / p=0.017
for dname in ['06_fatal_finding.md', '07_tasks12_findings.md', 'README.md']:
    check(f"{dname} ΔE=0 0.526", "0.526" in docs.get(dname, ''))
    check(f"{dname} ΔE=0 p=0.017", "0.017" in docs.get(dname, ''))

# 排除 node 0 單點驅動
for dname in ['06_fatal_finding.md', '07_tasks12_findings.md', 'README.md']:
    check(f"{dname} 單點驅動", "node 0" in docs.get(dname, '') or "node0" in docs.get(dname, '') or "單點" in docs.get(dname, ''))

# 跨地圖 SMICA 特定
for dname in ['06_fatal_finding.md', '07_tasks12_findings.md', 'README.md']:
    check(f"{dname} SMICA 特定", "SMICA" in docs.get(dname, '') and ("NILC" in docs.get(dname, '') or "Commander" in docs.get(dname, '')))

print("\n=== 2. 推導鏈完整性 ===")
chain_checks = [
    ("01: 問題陳述 (Fibonacci ladder)", "Fibonacci" in docs.get('01_problem_record.md', '') or "ladder" in docs.get('01_problem_record.md', '').lower()),
    ("01: 狀態 🔴", "🔴" in docs.get('01_problem_record.md', '')),
    ("03: 完整記錄 §11 完整測試", "完整測試" in docs.get('03_complete_record.md', '') or "11." in docs.get('03_complete_record.md', '')),
    ("04: 開放問題", "開放" in docs.get('04_open_issues.md', '')),
    ("05: 14/14 PASS", "14/14" in docs.get('05_full_test_record.md', '')),
    ("06: 致命發現", "致命" in docs.get('06_fatal_finding.md', '')),
    ("07: 任務 1+2+3", "任務" in docs.get('07_tasks12_findings.md', '') or "Task" in docs.get('07_tasks12_findings.md', '')),
    ("README: 三重否定", "三重否定" in docs.get('README.md', '') or "否定" in docs.get('README.md', '')),
]
for name, ok in chain_checks:
    check(name, ok)

print("\n=== 3. 公式獨立重算 ===")
# 冷斑 150 μK = 5ε⁵/8 × T_cmb
eps = phi**-1 / 4
A5 = 5 * eps**5 / 8 * 2.72548 * 1e6
check(f"A = 5ε⁵/8×T_cmb = {A5:.2f} μK = 150", abs(A5 - 150) < 0.1)
# 冷斑觀測 vs 預測偏差
obs = 134.2
dev = abs(A5 - obs) / obs * 100
check(f"觀測偏差 = {dev:.1f}%", 10 < dev < 13, f"{dev:.1f}%")

print("\n=== 4. 發現/修正記錄 ===")
# 06 有無幻覺發現
m06 = docs.get('06_fatal_finding.md', '')
check("06: 三重否定完整", all(k in m06 for k in ['BIC', '排除', '跨地圖']))
# 07 有高緯釐清
m07 = docs.get('07_tasks12_findings.md', '')
check("07: 高緯 ΔE=0 子集", "高緯" in m07 or "21_" in m07)

with open(f'{OUT}/G02_o4_docs.txt', 'w') as f:
    f.write("# G02: O4 文檔核對結果\n")
    f.write(f"A5={A5:.2f}uK obs={obs}uK dev={dev:.1f}%\n")
print(f"\n✅ 已存: data/G02_o4_docs.txt")
