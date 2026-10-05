#!/usr/bin/env python3
"""
Magic rows 深挖 — 5 個 opcode 行嘅完整結構
============================================
目標: 搵出 d ∈ {7,14,20,22,33} 嘅生成規則
方法: 列出每個 magic row 全部成員, 分析 (n,m,s,deg) 結構
"""
import csv

# 讀 master_atlas
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
print("1. Magic rows 全成員結構")
print("="*72)
for d in magic:
    members = [r for r in rows if r['d'] == d and r['n'] < r['m']]
    # 排序 by n
    members.sort(key=lambda r: r['n'])
    print(f"\n--- d={d} ({len(members)} 個成員) ---")
    for r in members:
        lbl = f" [{r['label']}]" if r['label'] else ""
        print(f"  ({r['n']:2d},{r['m']:2d}) s={r['s']:3d} deg_d={r['deg_diff']:2d} deg_s={r['deg_sum']:2d}{lbl}")

print("\n" + "="*72)
print("2. Magic rows 嘅 s 值分析")
print("="*72)
for d in magic:
    members = [r for r in rows if r['d'] == d and r['n'] < r['m']]
    s_vals = sorted(set(r['s'] for r in members))
    n_vals = sorted(set(r['n'] for r in members))
    print(f"  d={d:2d}: s 值 {s_vals}")
    print(f"          n 值 {n_vals}")

print("\n" + "="*72)
print("3. ★ 每個 magic row 嘅『首成員』(n=1)")
print("="*72)
for d in magic:
    first = [r for r in rows if r['d'] == d and r['n'] == 1]
    if first:
        r = first[0]
        lbl = f" [{r['label']}]" if r['label'] else ""
        print(f"  d={d:2d}: (1,{r['m']}) s={r['s']} deg={r['deg_diff']}{lbl}")
    else:
        print(f"  d={d:2d}: 冇 n=1 成員!")

print("\n" + "="*72)
print("4. ★ Magic rows 嘅『生成假說』測試")
print("="*72)
print("""
  假說 1: magic d 值 = 某啲 n 嘅 SYNC (2×n)?
    d=14 = 2×7  (7 = L₄)
    d=22 = 2×11 (11 = L₅)
    → 檢查: d=7,20,33 係咪都有 n 令 2n = d?
    → d=7 唔係偶數! d=20 = 2×10, d=33 奇數!
    
  假說 2: magic d 值 = L_k 組合?
    7 = L₄
    14 = 2×L₄
    20 = L₆+L₀ = 18+2
    22 = 2×L₅
    33 = 3×L₅
    → 唔規律
    
  假說 3: magic d 值嘅『位置』= 某啲特殊 s 值?
""")

# 檢查每個 magic row 嘅 s 值有冇規律
print("\n" + "="*72)
print("5. ★ s 值 = 成員數同 s 嘅關係")
print("="*72)
for d in magic:
    members = [r for r in rows if r['d'] == d and r['n'] < r['m']]
    s_vals = sorted(r['s'] for r in members)
    print(f"  d={d:2d}: {len(members)} 個成員, s={s_vals[0]}..{s_vals[-1]} (step {s_vals[1]-s_vals[0] if len(s_vals)>1 else '-'})")

# s 值步長
print("\ns 值步長分析:")
for d in magic:
    members = [r for r in rows if r['d'] == d and r['n'] < r['m']]
    s_vals = sorted(r['s'] for r in members)
    steps = [s_vals[k+1]-s_vals[k] for k in range(len(s_vals)-1)]
    print(f"  d={d:2d}: s 步長 = {set(steps)}")
