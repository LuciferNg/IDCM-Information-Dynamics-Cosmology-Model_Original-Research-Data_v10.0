#!/usr/bin/env python3
"""
Magic rows 低次數成員分析 — 生成規則核心
==========================================
發現: d=14/20/22/33 都有低次數 (deg<40) 成員
      d=7 全 deg 40/20
問題: 低次數成員嘅位置有咩規律? 係咪生成規則?
"""
import csv

rows = []
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/beat_periodic_table/data/master_atlas.csv') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append({
            'n': int(r['n']), 'm': int(r['m']), 'd': int(r['d']), 's': int(r['s']),
            'deg_diff': int(r['deg_diff']), 'deg_sum': int(r['deg_sum']),
            'label': r['label'].strip()
        })

magic = [7, 14, 20, 22, 33]
print("="*72)
print("1. Magic rows 低次數成員 (deg<40)")
print("="*72)
for d in magic:
    members = [r for r in rows if r['d'] == d and r['n'] < r['m']]
    low = [r for r in members if r['deg_diff'] < 40]
    print(f"\n--- d={d:2d}: {len(low)}/{len(members)} 低次數 ---")
    for r in low:
        lbl = f" [{r['label']}]" if r['label'] else ""
        print(f"  ({r['n']:2d},{r['m']:2d}) s={r['s']:3d} deg={r['deg_diff']:2d}{lbl}")

print("\n" + "="*72)
print("2. ★ 低次數成員嘅 (n,m) 位置規律")
print("="*72)
for d in magic:
    members = [r for r in rows if r['d'] == d and r['n'] < r['m']]
    low = [r for r in members if r['deg_diff'] < 40]
    n_vals = sorted(set(r['n'] for r in low))
    m_vals = sorted(set(r['m'] for r in low))
    print(f"  d={d:2d}: 低次數 n = {n_vals}")
    print(f"         低次數 m = {m_vals}")

print("\n" + "="*72)
print("3. ★ 低次數位置 vs 特殊端點 (11,22,33,44)")
print("="*72)
special = {11, 22, 33, 44}
for d in magic:
    members = [r for r in rows if r['d'] == d and r['n'] < r['m']]
    low = [r for r in members if r['deg_diff'] < 40]
    # 檢查低次數成員係咪「端點近 special」
    hits = []
    for r in low:
        sp = [x for x in (r['n'], r['m']) if x in special]
        hits.append((r['n'], r['m'], sp))
    print(f"  d={d:2d}: 低次數成員 + 特殊端點: {hits}")

print("\n" + "="*72)
print("4. ★ deg 10 成員特別分析 (d=14, d=20)")
print("="*72)
for d in [14, 20]:
    members = [r for r in rows if r['d'] == d and r['n'] < r['m']]
    deg10 = [r for r in members if r['deg_diff'] == 10]
    print(f"\n  d={d:2d}: deg10 成員 ({len(deg10)} 個)")
    for r in deg10:
        lbl = f" [{r['label']}]" if r['label'] else ""
        print(f"    ({r['n']:2d},{r['m']:2d}) s={r['s']:3d}{lbl}")

print("\n" + "="*72)
print("5. ★ 所有 deg<40 嘅 (d,n) 全圖")
print("="*72)
all_low = []
for d in range(1, 44):
    members = [r for r in rows if r['d'] == d and r['n'] < r['m']]
    low = [r for r in members if r['deg_diff'] < 40]
    if low:
        n_set = sorted(set(r['n'] for r in low))
        m_set = sorted(set(r['m'] for r in low))
        all_low.append((d, n_set, m_set))
# 打印 d vs n
print("d → 低次數 n 值:")
for d, n_set, m_set in all_low:
    print(f"  d={d:2d}: n={n_set}")
