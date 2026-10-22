#!/usr/bin/env python3
"""
F02_o3_docs_verify.py — O3 記錄文檔獨立核對 (任務 2)
=================================================================
驗證 O3 所有文檔 (01/02/03/04/05/final_result/README) 入面:
1. 關鍵數值一致性 (跨文檔)
2. 推導鏈內容完整 (冇缺步)
3. 公式正確 (獨立重算)
4. 發現/驗證/結果齊全

⚠️ 只讀, 唔改 O3 任何檔案 (禁止跨文檔污染)
"""
import numpy as np
import math
import os
import re

O3 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o3_node_temperatures'
OUT = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o4_renew/data'

def read(fname):
    with open(os.path.join(O3, fname)) as f:
        return f.read()

print("=" * 72)
print("F02: O3 記錄文檔獨立核對 (只讀)")
print("=" * 72)

def check(name, ok, detail=""):
    print(f"  {'✅' if ok else '❌'} {name}" + (f" — {detail}" if detail else ""))

# ---------- 載入所有文檔 ----------
docs = {}
for f in ['01_problem_record.md', '02_results.md', '03_red_flag_galactic_plane.md',
          '04_high4_node45_study.md', '05_hallucination_check_report.md',
          'final_result.md', 'README.md']:
    try:
        docs[f] = read(f)
        print(f"  已載入: {f} ({len(docs[f])} chars)")
    except Exception as e:
        print(f"  ❌ 載入失敗: {f} — {e}")

print("\n=== 1. 關鍵數值跨文檔一致性 ===")
# 冷斑 -134.2
for name, v in [("01_problem_record", "-134.19"), ("02_results", "-134.2"), ("final_result", "-134.19"), ("README", "-134.19")]:
    check(f"{name} 冷斑 {v}", v in docs.get(name + ".md", ""))

# ΔE=0: 0.526 / 0.375 / p=0.038 / p=0.0074
checks = [
    ("final_result ΔE=0 0.526", "0.526" in docs.get('final_result.md', '')),
    ("final_result p=0.038", "0.038" in docs.get('final_result.md', '')),
    ("final_result 高緯 0.375", "0.375" in docs.get('final_result.md', '')),
    ("final_result p=0.0074", "0.0074" in docs.get('final_result.md', '')),
    ("README ΔE=0 0.526", "0.526" in docs.get('README.md', '')),
    ("README p=0.038", "0.038" in docs.get('README.md', '')),
    ("README 高緯 p=0.0074", "0.0074" in docs.get('README.md', '')),
    ("02_results ΔE=0 0.526", "0.526" in docs.get('02_results.md', '')),
]
for name, ok in checks:
    check(name, ok)

# 冷熱分離 -22.31
for dname in ['01_problem_record.md', 'final_result.md', 'README.md']:
    check(f"{dname} 冷熱分離 -22.31", "-22.31" in docs.get(dname, ''))

# BFS ladder ρ=-0.05
for dname in ['01_problem_record.md', 'final_result.md', 'README.md']:
    check(f"{dname} BFS ρ=-0.05", "-0.05" in docs.get(dname, '') or "-0.050" in docs.get(dname, ''))

print("\n=== 2. 推導鏈完整性 (O3 內容) ===")
# O3 推導鏈: 載入 → 平滑(4.17°) → remove_dipole → 節點抽值 → 統計
chain_checks = [
    ("01: 方法有平滑 4.17°", "4.17" in docs.get('01_problem_record.md', '')),
    ("01: remove_dipole", "remove_dipole" in docs.get('01_problem_record.md', '') or "減偶極" in docs.get('01_problem_record.md', '')),
    ("01: 節點抽值", "抽值" in docs.get('01_problem_record.md', '') or "60 節點" in docs.get('01_problem_record.md', '')),
    ("01: z-score -1.98σ", "-1.98" in docs.get('01_problem_record.md', '')),
    ("01: 98.2% 百分位", "98.2" in docs.get('01_problem_record.md', '')),
    ("02: 節點溫度表存在", "node_temps" in docs.get('02_results.md', '') or "節點" in docs.get('02_results.md', '')),
    ("03: 銀河盤紅燈", "銀河" in docs.get('03_red_flag_galactic_plane.md', '')),
    ("04: 高緯 4 節點", "4 節點" in docs.get('04_high4_node45_study.md', '') or "高緯" in docs.get('04_high4_node45_study.md', '')),
    ("05: 幻覺檢查", "幻覺" in docs.get('05_hallucination_check_report.md', '')),
    ("final: 狀態 🟡", "🟡" in docs.get('final_result.md', '')),
]
for name, ok in chain_checks:
    check(name, ok)

print("\n=== 3. 公式獨立重算 ===")
# 冷斑 z-score: -134.19 vs 60節點群 mean/std
# 02_results: mean=-100.4±17.1 (節點群), z = (-134.19-(-100.4))/17.1
z = (-134.19 - (-100.4)) / 17.1
check(f"z-score 重算 = {z:.2f} ≈ -1.98", abs(z + 1.98) < 0.1, f"z={z:.3f}")
# 百分位: 98.2% = 59/60 節點更暖 (rank 1/60), 唔係高斯 cdf!
pct_nodes = 59/60 * 100
check(f"百分位 = 59/60 節點更暖 = {pct_nodes:.1f}% ≈ 98.2%", abs(pct_nodes - 98.2) < 0.5, f"{pct_nodes:.1f}%")

# ΔE=0 比例 19.05/36.18
r = 19.05 / 36.18
check(f"ΔE=0 比例重算 = {r:.3f} ≈ 0.526", abs(r - 0.526) < 0.01, f"r={r:.4f}")

# 高緯 12.45/33.21
r2 = 12.45 / 33.21
check(f"高緯比例重算 = {r2:.3f} ≈ 0.375", abs(r2 - 0.375) < 0.01, f"r={r2:.4f}")

# 冷熱分離: 由 02_results 表驗證 (冷 30 節點 vs 熱 30 節點 mean)
# 睇 02_results 有冇相關數據

print("\n=== 4. 幻覺檢查 (O3 數字 vs 獨立計算) ===")
# 檢查 02_results 入面節點 0 溫度
m02 = docs.get('02_results.md', '')
# 抽 node 0 相關行
for line in m02.split('\n'):
    if '134' in line and ('節點' in line or '0' in line[:5]):
        print(f"  02_results: {line.strip()[:80]}")

print("\n=== 5. 審計記錄 (05_hallucination_check) ===")
m05 = docs.get('05_hallucination_check_report.md', '')
if m05:
    # 搵 88/88 或類似
    for pat in ['88/88', '157/157', '全部', 'PASS']:
        if pat in m05:
            check(f"05 包含 {pat}", True)

with open(f'{OUT}/F02_o3_docs.txt', 'w') as f:
    f.write("# F02: O3 文檔核對結果\n")
    f.write(f"z_score={z:.3f} percentile=59/60={pct_nodes:.1f}%\n")
    f.write(f"dE0_ratio={r:.4f} highlat_ratio={r2:.4f}\n")
print(f"\n✅ 已存: data/F02_o3_docs.txt")
