#!/usr/bin/env python3
"""
★ Magic rows = gcd 類別代表? — 一致梳理 + 行/格 label 分別
============================================================
修正: 用 gcd(|44−d|, 176) 一致地分類 (唔係 gcd(d,176))
問題: 每個 gcd 類別, 邊個 d 係 magic? 邊啲類別缺 magic?
      magic rows (行 label) vs 物理格 (格 label) 嘅分別?
"""
import csv
from math import gcd
from collections import defaultdict

def phi(n):
    r=n; p=2
    while p*p<=n:
        if n%p==0:
            while n%p==0: n//=p
            r-=r//p
        p+=1
    if n>1: r-=r//n
    return r

def omega_deg(n):
    if n == 44: return 1
    dd = abs(44-n)
    g = gcd(dd, 176)
    return phi(176//g)//2

# 讀 atlas
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

# 每個 d 行嘅 label 分析
print("="*72)
print("1. 每行 d 嘅 label 分類 (行 label vs 格 label)")
print("="*72)
d_info = {}
for d in range(1, 44):
    members = [r for r in pairs if r['d'] == d]
    row_labels = set(r['label'] for r in members if r['label'].startswith('Row'))
    cell_labels = set(r['label'] for r in members if r['label'] and not r['label'].startswith('Row'))
    d_info[d] = (row_labels, cell_labels)

# 分類: magic (有行 label), data (有格 label), filler (冇)
magic_ds = []
data_ds = []
filler_ds = []
for d in range(1, 44):
    rl, cl = d_info[d]
    if rl:
        magic_ds.append(d)
    elif cl:
        data_ds.append(d)
    else:
        filler_ds.append(d)

print(f"magic rows (行 label): {magic_ds}")
print(f"data rows (格 label): {data_ds}")
print(f"filler rows (冇 label): {filler_ds} ({len(filler_ds)} 個)")

print("\n" + "="*72)
print("2. ★ magic/data/filler × gcd 類別")
print("="*72)
gcd_classes = defaultdict(list)
for d in range(1, 44):
    dd = abs(44-d)
    g = gcd(dd, 176)
    gcd_classes[g].append(d)

print(f"{'gcd':>5} {'deg ω_d':>7} | {'magic':<30} {'data':<20} {'filler'}")
for g in sorted(gcd_classes, reverse=True):
    ds = gcd_classes[g]
    m = [d for d in ds if d in magic_ds]
    dt = [d for d in ds if d in data_ds]
    f = [d for d in ds if d in filler_ds]
    d0 = ds[0]
    print(f"{g:>5} {omega_deg(d0):>7} | {str(m):<30} {str(dt):<20} {f}")

print("\n" + "="*72)
print("3. ★ 觀察: magic 覆蓋 gcd 類別 {1,2,8,11,22}, 缺 {4,16}")
print("="*72)
missing_gcd = [g for g in gcd_classes if not any(d in magic_ds for d in gcd_classes[g])]
present_gcd = [g for g in gcd_classes if any(d in magic_ds for d in gcd_classes[g])]
print(f"有 magic 嘅 gcd 類別: {sorted(present_gcd)}")
print(f"冇 magic 嘅 gcd 類別: {sorted(missing_gcd)}")
print()
print("176 = 2⁴ × 11")
print(f"有 magic: {sorted(present_gcd)} = 2⁰, 2¹, 2³, 11, 2·11")
print(f"冇 magic: {sorted(missing_gcd)} = 2², 2⁴ (純 2 次方, 偶數 v₂!)")
print()
print("★ 缺嘅係 v₂(176/g) ∈ {2,4} — 偶數 2-adic 階!")
print("  有嘅: v₂ = 4,3,1,0 (g=1,2,8) + 11 因子 (g=11,22)")

print("\n" + "="*72)
print("4. ★ magic rows 內部選擇規則")
print("="*72)
# 每個有 magic 嘅 gcd 類別, magic 係邊個 + 類別全體
for g in sorted(present_gcd):
    ds = gcd_classes[g]
    m = [d for d in ds if d in magic_ds]
    print(f"gcd={g:3d} (deg {omega_deg(ds[0]):2d}): 類別 {ds}, magic = {m}")
    # 檢查規則
    if len(m) == 1:
        md = m[0]
        # Lucas?
        L = [2,1,3,4,7,11,18,29,47]
        print(f"    magic {md}: Lucas? {md in L}, 質數? {md in [2,3,5,7,11,13,17,19,23,29,31,37,41,43]}, 11 倍數? {md%11==0}")
        # 位置
        print(f"    44−{md} = {44-md}, d/2 = {md/2}")

print("\n" + "="*72)
print("5. ★ 選擇規則測試")
print("="*72)
print("""
  規則 A (Lucas 代表): gcd=1 類別 Lucas 有 {1,3,7,29} → 揀 7?
    7 = L₄ — 最大嘅 Lucas ≤ 22 (half)! 29 > 22 排除
    1, 3 太細 (種子位)
    → 7 = 「≤22 最大 Lucas」✅ 講得通
    
  規則 B (SYNC 鏈): 14 = 2×7!
    gcd=2 類別 (deg20) 揀 14 = 2×(gcd=1 代表)
    → 7 → 14 係「×2 SYNC 鏈」!
    
  規則 C (中心): gcd=8 類別 {4,20,36} 揀 20 = 中心 (4+36)/2
    → 20 = 類別算術中心 ✅
    
  規則 D (11 族): gcd=11 類別 {11,33} 揀 33, gcd=22 類別 {22} 揀 22
    → 33 = 3×11, 22 = 2×11 — 揀「非最小」11 倍數?
    → 11 本身唔係 magic (1×11 排除)
""")

print("\n" + "="*72)
print("6. ★ data rows (格 label) 嘅 gcd 分佈")
print("="*72)
for g in sorted(gcd_classes, reverse=True):
    ds = gcd_classes[g]
    dt = [d for d in ds if d in data_ds]
    if dt:
        print(f"gcd={g:3d}: data rows {dt}")
print()
print("★ data rows 喺邊? gcd=4 類別有 8 (c/s, m_c/m_b 格)!")
print("  → 8 行係『數據行』唔係『操作行』!")
