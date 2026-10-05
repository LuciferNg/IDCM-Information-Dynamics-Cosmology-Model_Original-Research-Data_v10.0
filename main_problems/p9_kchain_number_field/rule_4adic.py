#!/usr/bin/env python3
"""
★ 4-adic 規則閉合 — d≡s (mod 4) 係低次數充分必要條件?
========================================================
發現: d≡s (mod 4) 時先有 deg<40
      d≡s≡0: 110/110 全低次數!
      d≡s≡2: 121/121 全低次數!
      d≡s≡1: 11/121 (部分)
      d≡s≡3: 10/110 (部分)
問題: 呢個規則嘅完整形式係咩?
"""
import csv
from math import gcd, lcm

rows = []
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/beat_periodic_table/data/master_atlas.csv') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append({
            'n': int(r['n']), 'm': int(r['m']), 'd': int(r['d']), 's': int(r['s']),
            'deg_diff': int(r['deg_diff']), 'deg_sum': int(r['deg_sum']),
            'label': r['label'].strip()
        })

pairs = [r for r in rows if r['n'] < r['m']]

print("="*72)
print("1. 規則 I (奇偶): d≡s (mod 2)")
print("="*72)
viol1 = [r for r in pairs if (r['d']-r['s']) % 2 == 1 and r['deg_diff'] < 40]
print(f"d≠s (mod 2) 但 deg<40: {len(viol1)} 個 {'✅ 無違反' if not viol1 else viol1[:3]}")

print("\n" + "="*72)
print("2. 規則 II (4-adic): d≡s (mod 4) 先有 deg<40")
print("="*72)
viol2 = [r for r in pairs if (r['d']-r['s']) % 4 != 0 and r['deg_diff'] < 40]
print(f"d≠s (mod 4) 但 deg<40: {len(viol2)} 個")
if viol2:
    for r in viol2[:10]:
        print(f"  ({r['n']},{r['m']}) d={r['d']} s={r['s']} deg={r['deg_diff']}")

print("\n" + "="*72)
print("3. ★ d≡s≡0 (mod 4): 全低次數?")
print("="*72)
sub = [r for r in pairs if r['d']%4==0 and r['s']%4==0]
low = [r for r in sub if r['deg_diff'] < 40]
hi = [r for r in sub if r['deg_diff'] >= 40]
print(f"d≡s≡0: {len(sub)} 個, deg<40 = {len(low)}, deg=40 = {len(hi)}")
if hi:
    print("違反成員:")
    for r in hi:
        print(f"  ({r['n']},{r['m']}) d={r['d']} s={r['s']} deg={r['deg_diff']}")

print("\n" + "="*72)
print("4. ★ d≡s≡2 (mod 4): 全低次數?")
print("="*72)
sub = [r for r in pairs if r['d']%4==2 and r['s']%4==2]
low = [r for r in sub if r['deg_diff'] < 40]
hi = [r for r in sub if r['deg_diff'] >= 40]
print(f"d≡s≡2: {len(sub)} 個, deg<40 = {len(low)}, deg=40 = {len(hi)}")
if hi:
    print("違反成員:")
    for r in hi:
        print(f"  ({r['n']},{r['m']}) d={r['d']} s={r['s']} deg={r['deg_diff']}")

print("\n" + "="*72)
print("5. d≡s≡1 同 3 (mod 4): 部分低次數")
print("="*72)
for m4 in [1, 3]:
    sub = [r for r in pairs if r['d']%4==m4 and r['s']%4==m4]
    low = [r for r in sub if r['deg_diff'] < 40]
    print(f"d≡s≡{m4}: {len(sub)} 個, deg<40 = {len(low)}")
    for r in low:
        print(f"  ({r['n']:2d},{r['m']:2d}) d={r['d']:2d} s={r['s']:3d} deg={r['deg_diff']:2d} {r['label']}")

print("\n" + "="*72)
print("6. ★ 完整規則總結")
print("="*72)
print("""
  deg<40 嘅充分必要條件:
  
  d ≡ s (mod 4)   [4-adic 守恆, 奇偶嘅推廣]
  AND
  (d≡s≡0 or d≡s≡2) → 全部 deg<40  (110+121 = 231 個)
  (d≡s≡1 or d≡s≡3) → 部分 deg<40  (11+10 = 21 個, 特殊端點)
  
  即係: deg<40 只可能喺 d≡s (mod 4)
        而且 d≡s≡偶數時必然 deg<40!
        
  ★ 規則 III (4-adic 守恆): d ≡ s (mod 4) ⇔ deg < 40 可能
  ★ 規則 IV (偶數填充): d≡s≡0/2 (mod 4) → 必定 deg<40 (231/231)
""")
