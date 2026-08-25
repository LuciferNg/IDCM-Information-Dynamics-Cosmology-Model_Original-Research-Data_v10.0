#!/usr/bin/env python3
"""
★ s mod 4 規則推廣 — 低次數拍頻嘅完整生成規則
================================================
發現: d=14 低次數 s ≡ 2 (mod 4), 高次數 s ≡ 0 (mod 4)
問題: 呢個規則對全部 946 拍頻成立嗎?
      deg<40 ⇔ 某個 s mod 4 條件?
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
print(f"總拍頻: {len(pairs)}")

print("="*72)
print("1. 全表: deg<40 vs s mod 4")
print("="*72)
from collections import Counter
# 對每個 s mod 4, 統計 deg 分布
for smod in range(4):
    subset = [r for r in pairs if r['s'] % 4 == smod]
    degs = Counter(r['deg_diff'] for r in subset)
    low = sum(v for k,v in degs.items() if k < 40)
    hi = sum(v for k,v in degs.items() if k >= 40)
    print(f"  s ≡ {smod} (mod 4): {len(subset)} 個, deg<40 = {low} ({low/max(len(subset),1)*100:.1f}%), deg40 = {hi}")

print("\n" + "="*72)
print("2. 進一步: s mod 8?")
print("="*72)
for smod in range(8):
    subset = [r for r in pairs if r['s'] % 8 == smod]
    if not subset: continue
    degs = Counter(r['deg_diff'] for r in subset)
    low = sum(v for k,v in degs.items() if k < 40)
    print(f"  s ≡ {smod} (mod 8): {len(subset):3d} 個, deg<40 = {low:3d} ({low/max(len(subset),1)*100:.0f}%)")

print("\n" + "="*72)
print("3. ★ 關鍵問題: deg<40 嘅充分條件?")
print("="*72)
# 全部 deg<40 成員嘅 s mod 8
low_all = [r for r in pairs if r['deg_diff'] < 40]
print(f"deg<40 總數: {len(low_all)}")
print(f"  s mod 4 分布: {Counter(r['s']%4 for r in low_all)}")
print(f"  s mod 8 分布: {Counter(r['s']%8 for r in low_all)}")
print(f"  d mod 4 分布: {Counter(r['d']%4 for r in low_all)}")
print(f"  d mod 8 分布: {Counter(r['d']%8 for r in low_all)}")

print("\n" + "="*72)
print("4. ★ d mod 4 × s mod 4 全格")
print("="*72)
for dmod in range(4):
    row_outs = []
    for smod in range(4):
        subset = [r for r in pairs if r['d']%4 == dmod and r['s']%4 == smod]
        low = sum(1 for r in subset if r['deg_diff'] < 40)
        row_outs.append(f"d≡{dmod},s≡{smod}: {low}/{len(subset)}")
    print(f"  {' | '.join(row_outs)}")
