#!/usr/bin/env python3
"""
★ Magic 選擇規則統一 — 每個 gcd 類別點解揀呢個代表?
======================================================
magic: gcd1→7, gcd2→14, gcd8→20, gcd11→33, gcd22→22
問題: 有冇統一嘅選擇函數 f(類別) → 代表?
"""
from math import gcd

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

# gcd 類別 (用 |44−d|)
gcd_classes = {}
for d in range(1, 44):
    dd = abs(44-d)
    g = gcd(dd, 176)
    gcd_classes.setdefault(g, []).append(d)

magic = {1: 7, 2: 14, 8: 20, 11: 33, 22: 22}

print("="*72)
print("1. 候選規則測試")
print("="*72)
for g in sorted(magic):
    cls = gcd_classes[g]
    rep = magic[g]
    idx = cls.index(rep)
    print(f"gcd={g:3d}: 類別 {cls}, 代表 {rep} (位置 {idx}/{len(cls)})")

print("\n" + "="*72)
print("2. ★ 候選: 代表 = 類別中『最接近 22』? (half 中心)")
print("="*72)
for g in sorted(magic):
    cls = gcd_classes[g]
    rep = magic[g]
    # 離 22 最近
    nearest = min(cls, key=lambda d: abs(d-22))
    print(f"gcd={g:3d}: 離 22 最近 = {nearest}, 代表 = {rep}, {'✅' if nearest==rep else '❌'}")

print("\n" + "="*72)
print("3. ★ 候選: 代表 = 44−代表 ∈ 同類別? (對偶閉合)")
print("="*72)
for g in sorted(magic):
    cls = gcd_classes[g]
    rep = magic[g]
    comp = 44 - rep
    in_cls = comp in cls
    print(f"gcd={g:3d}: 代表 {rep}, 44−{rep}={comp}, 喺類別? {in_cls}")

print("\n" + "="*72)
print("4. ★ 候選: 代表 = 類別嘅『幾何中心』(平均)")
print("="*72)
for g in sorted(magic):
    cls = gcd_classes[g]
    rep = magic[g]
    center = sum(cls)/len(cls)
    print(f"gcd={g:3d}: 類別 {cls}, 平均 = {center:.2f}, 代表 = {rep}, 差 = {abs(center-rep):.2f}")

print("\n" + "="*72)
print("5. ★ 候選: 代表嘅『Lucas/Fib 身份』")
print("="*72)
L = [2,1,3,4,7,11,18,29,47]
F = [1,1,2,3,5,8,13,21,34]
for g in sorted(magic):
    cls = gcd_classes[g]
    rep = magic[g]
    lh = [v for v in L if v in cls]
    fh = [v for v in F if v in cls]
    print(f"gcd={g:3d}: 類別 {cls}")
    print(f"        Lucas 喺類別: {lh}")
    print(f"        Fib 喺類別: {fh}")
    print(f"        代表 {rep} 係 Lucas? {rep in L}  Fib? {rep in F}")

print("\n" + "="*72)
print("6. ★ 統一規則: 代表 = 類別中『唯一符合物理角色』?")
print("="*72)
print("""
  逐個分析:
  
  gcd=1 (deg40, 高次數): 20 個 → 揀 7
    7 = L₄, 唯一 Lucas ≤ 22 且 > 4
    1,3 太細; 29 太大 (L₇)
    7 = m7 anchor (O35 DM 13.8 MeV)
    
  gcd=2 (deg20): 10 個 → 揀 14
    14 = 2×7 = SYNC(7)
    14 ∈ {2,6,10,14,18,26,30,34,38,42}
    步長 4 = B! 揀 14 = 類別中第 4 個 (2+3×4)
    
  gcd=8 (deg5): 3 個 {4,20,36} → 揀 20
    20 = 4+16 = 中心 = 44/2.2? 唔係
    20 = 4×5 = B×5, 20 = 2n_u (T 轉移矩陣!)
    
  gcd=11 (deg4): 2 個 {11,33} → 揀 33
    33 = 3×11 = M (K_tree pipeline)
    11 = L₅ 但 11 行係 data row (m_μ/m_τ)
    
  gcd=22 (deg2): 1 個 {22} → 揀 22
    22 = half-node, 唯一!
    
  ★ 冇單一規則! 每個代表有自己嘅物理身份:
    7  = L₄ m7 anchor
    14 = SYNC(7) GEN
    20 = 2n_u 轉移矩陣
    22 = half-node
    33 = M K_tree
""")

print("\n" + "="*72)
print("7. ★ 但係: magic rows 嘅『共同性質』?")
print("="*72)
# 所有 magic rows 嘅共同: 行 label = 'Row X'
# 檢查: 每行 label 嘅格式
import csv
rows = []
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/beat_periodic_table/data/master_atlas.csv') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append({'n': int(r['n']), 'm': int(r['m']), 'd': int(r['d']), 'label': r['label'].strip()})
for d in [7,14,20,22,33]:
    labels = set(r['label'] for r in rows if r['d']==d and r['label'])
    print(f"d={d:2d}: labels = {labels}")

print("\n" + "="*72)
print("8. ★ 轉換: magic rows 嘅『工作流角色』")
print("="*72)
print("""
  從 label 睇:
  d=7:  'Row m7 anchor'  — 質量 anchor 行
  d=14: 'Row GEN d=14'   — 世代生成行
  d=20: 'Row T(s->d)'    — 轉移矩陣行
  d=22: 'Row half-node'  — 半節點行
  d=33: 'Row K_tree'     — K_tree 行
  
  ★ 5 個操作族: ANCHOR, GEN, TRANSFER, HALF, KTREE
  ★ 每個都係『宏指令』(macro) — 唔係基本操作
  ★ 基本操作 = 43 條邊 (STEP) + 44 self loop (SYNC)
  ★ magic rows = 5 個高階操作族 (macro opcodes)
""")
