#!/usr/bin/env python3
"""
★ 終極分層: 操作 (magic) vs 數據 (data) vs 填充 (filler)
==========================================================
發現: data rows 全 gcd=1 (deg40) 除 d=11
      d=14 雙重身份 (GEN 操作 + quark 數據)
問題: 完整分層有咩規律? 18 個物理參數全部坐喺邊?
"""
import csv
from math import gcd

rows = []
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/beat_periodic_table/data/master_atlas.csv') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append({'n': int(r['n']), 'm': int(r['m']), 'd': int(r['d']),
                     's': int(r['s']), 'deg_diff': int(r['deg_diff']),
                     'label': r['label'].strip()})

pairs = [r for r in rows if r['n'] < r['m']]

print("="*72)
print("1. 全部物理參數格 (18 個?) 嘅位置")
print("="*72)
phys = [(r['n'], r['m'], r['d'], r['s'], r['deg_diff'], r['label']) for r in pairs if r['label'] and not r['label'].startswith('Row')]
print(f"物理參數格總數: {len(phys)}")
for n, m, d, s, deg, lbl in phys:
    print(f"  ({n:2d},{m:2d}) d={d:2d} s={s:3d} deg={deg:2d} [{lbl}]")

print("\n" + "="*72)
print("2. ★ 物理參數嘅 deg 分佈")
print("="*72)
from collections import Counter
degc = Counter(p[4] for p in phys)
print(f"deg 分佈: {dict(degc)}")
print(f"deg=40 (高次數): {sum(1 for p in phys if p[4]==40)}")
print(f"deg<40 (低次數): {sum(1 for p in phys if p[4]<40)}")

print("\n" + "="*72)
print("3. ★ 物理參數嘅 gcd 分佈")
print("="*72)
gcdc = Counter(gcd(abs(44-p[2]),176) for p in phys)
print(f"gcd(|44−d|,176) 分佈: {dict(sorted(gcdc.items()))}")
print(f"gcd=1 (高次數行): {sum(1 for p in phys if gcd(abs(44-p[2]),176)==1)}")

print("\n" + "="*72)
print("4. ★ 物理參數 vs magic rows")
print("="*72)
for d in sorted(set(p[2] for p in phys)):
    magic = d in [7,14,20,22,33]
    labels = [p[5] for p in phys if p[2]==d]
    print(f"  d={d:2d}: {'MAGIC' if magic else 'data '} → {labels}")

print("\n" + "="*72)
print("5. ★ d=14 雙重身份分析")
print("="*72)
d14_members = [r for r in pairs if r['d']==14]
row_label = set(r['label'] for r in d14_members if r['label'].startswith('Row'))
cell_labels = [(r['n'],r['m'],r['label']) for r in d14_members if r['label'] and not r['label'].startswith('Row')]
print(f"d=14 行 label: {row_label}")
print(f"d=14 格 label: {cell_labels}")
print()
print("→ d=14 同時係: GEN 操作行 + 3 quark 數據格!")
print("→ 世代操作 (GEN) 直接產出三代 quark 質量比!")
print("→ 呢個係『操作 = 數據』嘅結合點!")

print("\n" + "="*72)
print("6. ★ 完整分層規則")
print("="*72)
print("""
  176 = 2⁴ × 11
  
  ├── 低次數端點 (24) = gcd≥2 = 偶數 ∪ {11,33}
  │     ├── magic rows (操作): gcd 類別 {1,2,8,11,22} 代表
  │     │     = ANCHOR(7), GEN(14), TRANSFER(20), HALF(22), KTREE(33)
  │     ├── data rows (物理): gcd=1 為主
  │     │     = m_W/m_Z(11), n/p(13), m_μ/m_τ(17), m_H/m_W(19), m_s/m_d(21), m_c/m_b(25)
  │     └── filler (填充): 其餘
  │
  └── 高次數端點 (20) = gcd=1 = 奇數非 11 倍數
  
  ★ 操作 (magic) 覆蓋 gcd 類別代表
  ★ 數據 (data) 坐高次數行 (deg40) — 物理參數要「最大複雜度」?
  ★ d=14: 操作+數據雙重 (GEN → quark)
""")

print("\n" + "="*72)
print("7. 驗證: data rows 嘅 s 值有冇規律")
print("="*72)
for n, m, d, s, deg, lbl in phys:
    print(f"  ({n:2d},{m:2d}) d={d:2d} s={s:3d} s mod 4 = {s%4} deg={deg:2d}")
