#!/usr/bin/env python3
"""
物理島假說檢驗: 9 個已閉合物理參數嘅 (d,s) 座標有冇結構?
=========================================================
如果物理參數喺 (d,s) 平面聚類 → 可以用嚟預言未發現參數位置 (有預言性, 值得挖)
如果散落 → 純撞彩, 唔值得挖
"""
from math import pi, sin
from collections import Counter

Nd = 44
w = lambda n: 2*sin(pi*n/88)
pairs = [(i,j) for i in range(1,Nd) for j in range(i+1,Nd+1)]

# 9 個已閉合物理參數 (from master_atlas)
phys = {
    (10,24): "u/d", (8,22): "c/s", (19,33): "t/b",
    (8,33): "m_c/m_b", (1,22): "m_s/m_d", (30,41): "m_W/m_Z",
    (19,38): "m_H/m_W", (1,18): "m_mu/m_tau", (7,20): "n/p",
}

print("="*70)
print("1. 9 個物理參數嘅 (d,s) 座標")
print("="*70)
coords = []
for (i,j), name in phys.items():
    d = j-i; s = j+i
    coords.append((d,s,name))
    print(f"  {name:12s} ({i:2d},{j:2d})  d={d:2d}  s={s:3d}  d/s={d/s:.4f}")

print("\n" + "="*70)
print("2. d 值分析")
print("="*70)
ds = sorted(d for d,s,n in coords)
print(f"  d 值: {ds}")
print(f"  d 全奇數? {all(d%2==1 for d in ds)}  (u/d c/s t/b 用 d=14)")
print(f"  d 範圍: {min(ds)}..{max(ds)}")
print(f"  d 平均: {sum(ds)/len(ds):.2f}")
print(f"  d 之間差距: {[ds[k+1]-ds[k] for k in range(len(ds)-1)]}")

print("\n" + "="*70)
print("3. s 值分析")
print("="*70)
ss = sorted(s for d,s,n in coords)
print(f"  s 值: {ss}")
print(f"  s 奇偶: {['偶' if s%2==0 else '奇' for s in ss]}")
print(f"  s 全奇數? {all(s%2==1 for s in ss)}")

print("\n" + "="*70)
print("4. 物理島假說: 隨機 9 點嘅期望分布 vs 實際")
print("="*70)
# 全 946 點嘅 d,s 分布
all_ds = [(j-i, j+i) for (i,j) in pairs]
d_mean = sum(d for d,s in all_ds)/len(all_ds)
s_mean = sum(s for d,s in all_ds)/len(all_ds)
print(f"  全 946 點: d_mean={d_mean:.1f}, s_mean={s_mean:.1f}")
print(f"  物理 9 點: d_mean={sum(d for d,s,n in coords)/9:.1f}, s_mean={sum(s for d,s,n in coords)/9:.1f}")
print(f"  → d 偏移: {sum(d for d,s,n in coords)/9 - d_mean:+.1f} (負=偏低端)")
print(f"  → s 偏移: {sum(s for d,s,n in coords)/9 - s_mean:+.1f}")

# 密度分析: 物理參數附近 (±2) 有幾多其他物理參數?
print(f"\n  物理參數聚類檢查 (d±2, s±2 內有第二個物理參數?):")
for k,(d1,s1,n1) in enumerate(coords):
    near = [(d2,s2,n2) for d2,s2,n2 in coords if k != coords.index((d1,s1,n1)) and abs(d2-d1)<=2 and abs(s2-s1)<=2]
    if near:
        print(f"    {n1} ({d1},{s1}) 附近有: {[(n2,d2,s2) for d2,s2,n2 in near]}")

# 5. d=14 行物理成員比例 vs 全表
print("\n" + "="*70)
print("5. d=14 (GEN) 行 vs 其他行嘅物理命中率")
print("="*70)
for d in [7,14,20,22,33]:
    members = [(i,j) for (i,j) in pairs if j-i==d]
    hit = sum(1 for (i,j) in members if (i,j) in phys)
    print(f"  d={d:2d}: {len(members):2d} 成員, {hit} 物理 ({hit/len(members)*100:.0f}%)")
# 隨機 30 成員行
import random
random.seed(1)
sample_ds = random.sample([d for d in range(1,44) if d not in [7,14,20,22,33]], 5)
for d in sample_ds:
    members = [(i,j) for (i,j) in pairs if j-i==d]
    hit = sum(1 for (i,j) in members if (i,j) in phys)
    print(f"  d={d:2d} (隨機): {len(members):2d} 成員, {hit} 物理 ({hit/len(members)*100:.0f}%)")

print("\n" + "="*70)
print("6. 全部 946 點 (d,s) 分布熱區 — 物理參數集中喺邊?")
print("="*70)
# 分區: d<15, 15<=d<25, d>=25 × s<33, 33<=s<55, s>=55
zones = Counter()
for d,s in all_ds:
    dz = "d<15" if d<15 else ("15≤d<25" if d<25 else "d≥25")
    sz = "s<33" if s<33 else ("33≤s<55" if s<55 else "s≥55")
    zones[(dz,sz)] += 1
for (dz,sz),c in sorted(zones.items()):
    print(f"  {dz:7s} × {sz:7s}: {c:3d} 點 ({c/9.46:.0f}%)")
print(f"\n  物理參數分區:")
pzones = Counter()
for d,s,n in coords:
    dz = "d<15" if d<15 else ("15≤d<25" if d<25 else "d≥25")
    sz = "s<33" if s<33 else ("33≤s<55" if s<55 else "s≥55")
    pzones[(dz,sz)] += 1
for (dz,sz),c in sorted(pzones.items()):
    print(f"  {dz:7s} × {sz:7s}: {c} 個物理參數")
