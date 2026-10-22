#!/usr/bin/env python3
"""
18_planarity_check.py — O26: 圖平面性 + 真正面結構
=====================================================
發現: 「角距離 <28°」圖有 60 節點 120 邊, 但 5-ring 好多有 chord
→ 可能唔係平面嵌入!

正 Rhombicosidodecahedron: V=60, E=120, F=62, 面 = 20△+30□+12⬠
平面圖要求: 每條邊屬於 exactly 2 個面, Euler V-E+F=2

檢查:
1. 圖平面性 (Kuratowski: 有冇 K5/K3,3 minor?)
2. 真正面 (冇 chord 嘅最短環)
3. 三角形面 20 確認
4. 正方形面 (冇 chord 4-ring)
5. 五邊形面 (冇 chord 5-ring)
6. 面數 = 62?
"""
import numpy as np
import math
from collections import defaultdict, deque, Counter

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
OUT = f"{BASE}/o26_node57_region/data"

nodes = []
with open(f"{BASE}/cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])

adj = [set() for _ in range(60)]
edges = []
for i in range(60):
    for j in range(i+1, 60):
        a = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if a < 28:
            adj[i].add(j); adj[j].add(i)
            edges.append((i, j))

results = []
def log(*args):
    line = " ".join(str(a) for a in args)
    print(line)
    results.append(line)

log("=" * 72)
log("O26: 圖平面性 + 真正面結構")
log("=" * 72)
log(f"圖: V=60, E={len(edges)}")

# ============ 1. 面結構 (冇 chord 最短環) ============
log("\n=== 1. 面結構 (冇 chord) ===")
# 三角形 (3-ring 一定冇 chord)
triangles = set()
for i in range(60):
    for j in adj[i]:
        if j <= i: continue
        for kk in adj[i] & adj[j]:
            if kk > j:
                triangles.add(tuple(sorted((i, j, kk))))
log(f"  三角形面: {len(triangles)} (期望 20)")

# 4-ring 冇 chord
def rings4():
    out = set()
    for s in range(60):
        path = [s]; vp = {s}
        def dfs(u, d):
            if d == 4:
                if s in adj[u]: out.add(tuple(sorted(path)))
                return
            for v in adj[u]:
                if v not in vp:
                    vp.add(v); path.append(v); dfs(v, d+1); path.pop(); vp.discard(v)
        dfs(s, 1)
    return out
r4 = rings4()
sq_faces = []
for r in r4:
    # 冇 chord: 對角唔相連
    no_chord = True
    for i in range(4):
        for j in range(i+1, 4):
            if (j-i) % 4 in (2,):  # 對角
                if r[j] in adj[r[i]]:
                    no_chord = False
    if no_chord:
        sq_faces.append(r)
log(f"  4-ring 總數: {len(r4)}, 冇 chord (正方形面): {len(sq_faces)} (期望 30)")

# 5-ring 冇 chord
def rings5():
    out = set()
    for s in range(60):
        path = [s]; vp = {s}
        def dfs(u, d):
            if d == 5:
                if s in adj[u]: out.add(tuple(sorted(path)))
                return
            for v in adj[u]:
                if v not in vp:
                    vp.add(v); path.append(v); dfs(v, d+1); path.pop(); vp.discard(v)
        dfs(s, 1)
    return out
r5 = rings5()
pent_faces = []
for r in r5:
    no_chord = True
    for i in range(5):
        for j in range(i+1, 5):
            if (j-i) % 5 in (2, 3):  # 對角
                if r[j] in adj[r[i]]:
                    no_chord = False
    if no_chord:
        pent_faces.append(r)
log(f"  5-ring 總數: {len(r5)}, 冇 chord (五邊形面): {len(pent_faces)} (期望 12)")

# ============ 2. 面總數 + Euler ============
log("\n=== 2. Euler 檢查 ===")
F = len(triangles) + len(sq_faces) + len(pent_faces)
log(f"  F = {len(triangles)}△ + {len(sq_faces)}□ + {len(pent_faces)}⬠ = {F}")
log(f"  V - E + F = 60 - {len(edges)} + {F} = {60 - len(edges) + F} (期望 2)")
# 邊-面計數: 每邊屬於幾多面?
edge_face = Counter()
for t in triangles:
    for a, b in [(t[0],t[1]),(t[1],t[2]),(t[0],t[2])]:
        edge_face[(min(a,b),max(a,b))] += 1
for r in sq_faces:
    for i in range(4):
        edge_face[(min(r[i],r[(i+1)%4]),max(r[i],r[(i+1)%4]))] += 1
for r in pent_faces:
    for i in range(5):
        edge_face[(min(r[i],r[(i+1)%5]),max(r[i],r[(i+1)%5]))] += 1
ef_dist = Counter(edge_face.values())
log(f"  邊屬於面數分佈: {dict(sorted(ef_dist.items()))} (平面圖要求全部 2)")

# ============ 3. 對照: 完美多面體面 ============
log("\n=== 3. 完美面結構 (每邊 2 面) ===")
# 揀啲面令每邊 exactly 2
# 三角形面固定 20
# 正方形 30 + 五邊形 12 = 62 總面
# 但如果 4-ring 唔齊, 可能圖唔係平面

# ============ 4. 檢查非平面性 ============
log("\n=== 4. 非平面性檢查 ===")
# 如果 E > 3V-6 = 174? 120 < 174 所以唔會自動非平面
# 但 4-regular 120 邊: max planar = 3V-6 = 174, 120 OK
# 真正檢查: 5-ring chord 數量
n_chord_rings = sum(1 for r in r5 if any(r[j] in adj[r[i]] for i in range(5) for j in range(i+1,5) if (j-i)%5 in (2,3)))
log(f"  有 chord 嘅 5-ring: {n_chord_rings}/{len(r5)}")
# 檢查 chord 係咪「平面 chord」(將環分為面)
# 平面嵌入: 如果 5-ring 有 chord, 唔可以係面

# ============ 5. 最短環 ============
log("\n=== 5. 最短環 (girth) ===")
# 三角形存在 → girth=3
log(f"  Girth = 3 (有三角形)")

with open(f"{OUT}/node57_planarity.txt", "w") as f:
    f.write("\n".join(results) + "\n")
print(f"\n✅ 結果寫入 {OUT}/node57_planarity.txt")
