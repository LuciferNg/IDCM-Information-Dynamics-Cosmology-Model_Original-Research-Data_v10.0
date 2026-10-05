#!/usr/bin/env python3
"""
★ Data rows vs Magic rows — 操作/數據分層
============================================
data rows: d = 11, 13, 17, 19, 21, 25 (格 label)
magic rows: d = 7, 14, 20, 22, 33 (行 label)
問題: 兩層有咩關係? data rows 嘅物理身份?
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
print("1. Data rows 全成員 + 物理身份")
print("="*72)
data_ds = [11, 13, 17, 19, 21, 25]
for d in data_ds:
    members = [r for r in pairs if r['d'] == d]
    labeled = [r for r in members if r['label']]
    print(f"\n--- d={d} ({len(members)} 成員) ---")
    for r in labeled:
        print(f"  ({r['n']:2d},{r['m']:2d}) s={r['s']:3d} deg={r['deg_diff']:2d} [{r['label']}]")

print("\n" + "="*72)
print("2. ★ Data rows 嘅物理參數")
print("="*72)
phys = {}
for r in pairs:
    if r['label'] and not r['label'].startswith('Row'):
        phys.setdefault(r['d'], []).append((r['n'], r['m'], r['label']))
for d in sorted(phys):
    print(f"  d={d:2d}: {phys[d]}")

print("\n" + "="*72)
print("3. ★ Magic vs Data 嘅 gcd 對照")
print("="*72)
print(f"magic rows: {[7,14,20,22,33]}")
print(f"  gcd(|44−d|,176): {[gcd(abs(44-d),176) for d in [7,14,20,22,33]]}")
print(f"data rows: {data_ds}")
print(f"  gcd(|44−d|,176): {[gcd(abs(44-d),176) for d in data_ds]}")

print("\n" + "="*72)
print("4. ★ 結構分層: 操作族 (magic) vs 數據 (data)")
print("="*72)
print("""
  magic rows (操作族/macro):
    d=7   gcd=1  deg40  → ANCHOR (m7)
    d=14  gcd=2  deg20  → GEN (世代)
    d=20  gcd=8  deg5   → TRANSFER (s→d)
    d=22  gcd=22 deg2   → HALF (半節點)
    d=33  gcd=11 deg4   → KTREE (pipeline)
    
  data rows (物理數據):
    d=11  gcd=11 deg4  → m_μ/m_τ (格 (1,18)?)
    d=13  gcd=1  deg40 → u/d? no 睇 label
    d=17  gcd=1  deg40 → ?
    d=19  gcd=1  deg40 → ?
    d=21  gcd=1  deg40 → m_s/m_d
    d=25  gcd=1  deg40 → m_c/m_b? no
    
  ★ data rows 幾乎全部 gcd=1 (deg40)!
  ★ magic rows 覆蓋 gcd {1,2,8,11,22}
  ★ 唯一例外: d=11 (gcd=11) 係 data 而唔係 magic!
""")

print("\n" + "="*72)
print("5. ★ 11 嘅雙重身份")
print("="*72)
# d=11 行嘅 label
d11 = [r for r in pairs if r['d'] == 11 and r['label']]
print("d=11 行全部 label:")
for r in d11:
    print(f"  ({r['n']},{r['m']}) [{r['label']}]")
print()
print("→ d=11 行有 data label, 但係冇 Row label")
print("→ 11 = L₅ (Lucas 5), gcd=11 (176 因子)")
print("→ 11 係『質因子本身』— 唔係操作, 係數據!")
print("→ 33 = 3×11 = M — 先係操作 (K_tree)")

print("\n" + "="*72)
print("6. ★ 完整分層總結")
print("="*72)
print("""
  176 = 2⁴ × 11
  
  低次數端點集 (24) = 偶數 (22) ∪ {11, 33} (2)
  = 同 176 共享因子嘅 n (gcd ≥ 2)
  
  magic rows (5) = gcd 類別 {1,2,8,11,22} 嘅代表
    = 每個「有操作身份」嘅 gcd 類別揀一個代表
  
  data rows (6) = 物理參數所在行
    = gcd=1 (5 個) + gcd=11 (1 個, d=11)
    
  ★ 操作 (magic) vs 數據 (data) 係兩個唔同層!
  ★ magic 由 gcd 類別定義, data 由物理公式定義
  ★ 交集: gcd=11 類別有 2 個成員 (11=data, 33=magic)
""")
