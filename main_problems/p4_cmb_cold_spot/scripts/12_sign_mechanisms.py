#!/usr/bin/env python3
"""
Gemini 機制一驗證: 背景向量投影 ΔT ∝ r̂·V_bg
===============================================
如果冷熱符號 = 節點向量同背景場 V_bg 嘅內積:
ΔT_i ∝ r̂_i · V_bg

測試: V_bg = 冷斑方向?
- 冷斑本身 ΔT < 0 → V_bg 應該同冷斑方向相反
- 60 節點分成 30 熱 + 30 冷 (大致)
- 節點 |ΔT| 分佈應該係 |cos θ|

對比機制三 (幾何阻挫): 兩個機制有冇分辨力?
"""
import numpy as np
import math
from collections import defaultdict, deque

# 載入節點
nodes = []
with open("data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))

vecs = []
for ra, dec in nodes:
    r, d = math.radians(ra), math.radians(dec)
    vecs.append(np.array([math.cos(d)*math.cos(r),
                          math.cos(d)*math.sin(r),
                          math.sin(d)]))
vecs = np.array(vecs)

# 冷斑方向 (RA=48.30°, Dec=-20.44°)
ra_cs, dec_cs = math.radians(48.30), math.radians(-20.44)
v_cs = np.array([math.cos(dec_cs)*math.cos(ra_cs),
                 math.cos(dec_cs)*math.sin(ra_cs),
                 math.sin(dec_cs)])

print("=" * 66)
print("機制一: 背景向量投影 ΔT ∝ r̂·V_bg")
print("=" * 66)

# 測試 1: V_bg = 冷斑方向 (冷斑應該係負極大)
dots = vecs @ v_cs
print(f"\n[1] V_bg = 冷斑方向")
print(f"冷斑自身 cos = {np.dot(v_cs, v_cs):.3f} (應該 +1)")
print(f"節點 cos 分佈: min={dots.min():.3f}, max={dots.max():.3f}")
print(f"正 (熱): {(dots > 0).sum()}, 負 (冷): {(dots < 0).sum()}")

# 測試 2: V_bg = 銀南極方向? (冷斑 b=-57° 偏南)
# 銀南極: (l,b) = (0,-90) → ICRS RA=?, Dec=?
# 用 astropy
from astropy.coordinates import SkyCoord, Galactic
import astropy.units as u
south = SkyCoord(l=0*u.deg, b=-90*u.deg, frame=Galactic).icrs
v_south = np.array([math.cos(math.radians(south.dec.deg))*math.cos(math.radians(south.ra.deg)),
                    math.cos(math.radians(south.dec.deg))*math.sin(math.radians(south.ra.deg)),
                    math.sin(math.radians(south.dec.deg))])
dots2 = vecs @ v_south
print(f"\n[2] V_bg = 銀南極")
print(f"正: {(dots2 > 0).sum()}, 負: {(dots2 < 0).sum()}")
print(f"冷斑同銀南極夾角: {math.degrees(math.acos(np.clip(np.dot(v_cs, v_south),-1,1))):.1f}°")

# 測試 3: V_bg = CMB dipole 方向 (l=264, b=48.3)
dip = SkyCoord(l=264*u.deg, b=48.3*u.deg, frame=Galactic).icrs
v_dip = np.array([math.cos(math.radians(dip.dec.deg))*math.cos(math.radians(dip.ra.deg)),
                  math.cos(math.radians(dip.dec.deg))*math.sin(math.radians(dip.ra.deg)),
                  math.sin(math.radians(dip.dec.deg))])
dots3 = vecs @ v_dip
print(f"\n[3] V_bg = CMB dipole (264°, 48.3°)")
print(f"正: {(dots3 > 0).sum()}, 負: {(dots3 < 0).sum()}")

# 測試 4: V_bg = 對跖冷斑方向 (-v_cs)
dots4 = vecs @ (-v_cs)
print(f"\n[4] V_bg = -冷斑方向 (反方向)")
print(f"正: {(dots4 > 0).sum()}, 負: {(dots4 < 0).sum()}")

# ============ 對比機制三 ============
print("\n" + "=" * 66)
print("機制三: 幾何阻挫 (圖著色)")
print("=" * 66)

# 重建圖 (degree 4)
d_min = 26.091
edge_thresh = d_min * 1.05
adj = defaultdict(set)
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < edge_thresh:
            adj[i].add(j)
            adj[j].add(i)

# 二分著色 (BFS 2-color, 遇衝突就強制)
color = {}
q = deque()
for start in range(60):
    if start in color:
        continue
    color[start] = 0
    q.append(start)
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in color:
                color[v] = 1 - color[u]
                q.append(v)

# 衝突邊 (同色邊) = 阻挫缺陷
frustration_edges = []
for u in range(60):
    for v in adj[u]:
        if u < v and color[u] == color[v]:
            frustration_edges.append((u, v))
print(f"最大 2-著色下嘅衝突邊 (阻挫): {len(frustration_edges)}")
print(f"總邊數: {sum(len(a) for a in adj.values())//2}")

# 冷熱分配 (機制三): color 0 = 熱, color 1 = 冷 (盡量)
n_hot = sum(1 for c in color.values() if c == 0)
n_cold = sum(1 for c in color.values() if c == 1)
print(f"熱: {n_hot}, 冷: {n_cold}")
print(f"衝突邊 = 「冷-冷/熱-熱」相鄰 = 異常帶")

# 冷斑節點 0 (應該係冷 = color 1)
print(f"\n冷斑 (節點 0) 著色: {'冷' if color[0]==1 else '熱'}")

# 阻挫邊對應嘅天球位置 (RA/Dec)
print(f"\n阻挫缺陷邊 (冷-冷/熱-熱):")
for u, v in frustration_edges[:15]:
    ra1, dec1 = nodes[u]
    ra2, dec2 = nodes[v]
    print(f"  ({ra1:.1f},{dec1:.1f}) ↔ ({ra2:.1f},{dec2:.1f})")

# 儲存
with open("data/frustration_edges.txt", "w") as f:
    for u, v in frustration_edges:
        ra1, dec1 = nodes[u]
        ra2, dec2 = nodes[v]
        f.write(f"{ra1:.4f} {dec1:.4f} {ra2:.4f} {dec2:.4f}\n")
print(f"\n阻挫邊已存: data/frustration_edges.txt")
print(f"可證偽預測: 呢啲位置應該有「同極性」異常 (兩個都冷或兩個都熱)")
