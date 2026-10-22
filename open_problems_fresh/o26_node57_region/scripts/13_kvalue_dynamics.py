#!/usr/bin/env python3
"""
13_kvalue_dynamics.py — O26: k 值 (8/40/12) 動力學分解
=========================================================
假說: 60 節點圖 = Rhombicosidodecahedron (20△ + 30□ + 12⬠)
- 奇數面 (△, ⬠) 必有阻挫邊 (odd cycle 唔可以完美 2-coloring)
- 正方形 (□) 完美交替, 零阻挫
- 32 條阻挫邊 = 20 (△) + 12 (⬠)
- k(i) = [△邊同色] + [⬠邊同色] ∈ {0,1,2}
- 預測: 12 個 k=2 = △∩⬠ 雙阻挫節點
         28 個 k=1 = △-only, 12 個 k=1 = ⬠-only
         8 個 k=0 = 冇阻挫

驗證:
1. 搵全部 20△ + 12⬠ 面
2. BFS 著色 (anchor 0)
3. 每面阻挫邊
4. k 值 = △阻挫 + ⬠阻挫 分解
5. 阻挫邊連接結構
6. random anchor 對照 → 8/40/12 係咪冷斑簽名?
"""
import numpy as np
import math
import os
from collections import defaultdict, deque, Counter

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
OUT = os.path.join(BASE, "o26_node57_region", "data")

# ============ 載入 ============
nodes = []
with open(f"{BASE}/cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])

# 圖 (閾值 28°)
adj = [set() for _ in range(60)]
edges = []
for i in range(60):
    for j in range(i+1, 60):
        a = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if a < 28:
            adj[i].add(j); adj[j].add(i)
            edges.append((i, j))
print(f"圖: 60 節點, {len(edges)} 邊 (期望 120 = 60×4/2)")
deg = Counter(len(adj[i]) for i in range(60))
print(f"度數分佈: {dict(deg)} (期望 全部 4)")

results = []
def log(*args):
    line = " ".join(str(a) for a in args)
    print(line)
    results.append(line)

log("=" * 72)
log("O26: k 值動力學分解 (Rhombicosidodecahedron 面結構)")
log("=" * 72)

# ============ 1. 搵全部三角形 ============
log("\n=== 1. 三角形面 (20 個) ===")
triangles = set()
for i in range(60):
    for j in adj[i]:
        if j <= i: continue
        common = adj[i] & adj[j]
        for k in common:
            if k > j:
                triangles.add(tuple(sorted((i, j, k))))
print(f"  三角形數: {len(triangles)} (期望 20)")
# 驗證: 每個三角形都係「面」(唔係 K4 內部)
# rhombicosidodecahedron 冇共享邊嘅三角形? 檢查: 每條邊屬於幾多三角形
edge_tri_count = defaultdict(int)
for tri in triangles:
    for a, b in [(tri[0],tri[1]), (tri[1],tri[2]), (tri[0],tri[2])]:
        edge_tri_count[(min(a,b),max(a,b))] += 1
bad = {e: c for e, c in edge_tri_count.items() if c > 1}
print(f"  邊屬於 >1 三角形: {len(bad)} (期望 0)")

# ============ 2. 搵全部五邊形面 ============
log("\n=== 2. 五邊形面 (12 個) ===")
# 用 11_c60_graph.py 嘅 DFS 方法 (5-ring)
pentagons = set()
def find_rings(n_ring):
    rings = []
    for start in range(60):
        path = [start]
        visited_path = {start}
        def dfs(u, depth):
            if depth == n_ring:
                if start in adj[u]:
                    rings.append(tuple(sorted(path)))
                return
            for v in adj[u]:
                if v not in visited_path:
                    visited_path.add(v)
                    path.append(v)
                    dfs(v, depth+1)
                    path.pop()
                    visited_path.discard(v)
        dfs(start, 1)
    return set(rings)
pentagons = find_rings(5)
# 過濾: 5-ring 可以係「非面」(5 節點 5 邊環繞但唔係面) — 檢查所有邊都喺環上
print(f"  5-ring 總數: {len(pentagons)} (之前 11 腳本: 72)")
# 真正嘅五邊形面: 冇 chord (內部邊)? 面 = 最短環 (girth=3 但有三角同五角共存)
# 用 face 判斷: 五邊形面嘅 5 條邊各自屬於幾多三角形 = 0
pent_faces = []
for ring in pentagons:
    is_face = True
    for a, b in [(ring[0],ring[1]),(ring[1],ring[2]),(ring[2],ring[3]),(ring[3],ring[4]),(ring[4],ring[0])]:
        if edge_tri_count.get((min(a,b),max(a,b)), 0) > 0:
            is_face = False
            break
    if is_face:
        pent_faces.append(ring)
print(f"  五邊形面: {len(pent_faces)} (期望 12)")

# ============ 3. 正方形面 (30 個) ============
log("\n=== 3. 正方形面 (30 個) ===")
squares = set()
for ring in find_rings(4):
    is_face = True
    for a, b in [(ring[0],ring[1]),(ring[1],ring[2]),(ring[2],ring[3]),(ring[3],ring[0])]:
        if edge_tri_count.get((min(a,b),max(a,b)), 0) > 0:
            is_face = False
            break
    if is_face:
        squares.add(ring)
# 正方形面: 4-ring 唔含三角形邊 → 但要排除「5 環內嘅 4 環」? 正方形面 = 每條邊都唔係三角形邊
print(f"  正方形面: {len(squares)} (期望 30)")
# Euler: V - E + F = 60 - 120 + (20+30+12) = 2 ✓

# ============ 4. BFS 著色 + 阻挫邊 ============
log("\n=== 4. BFS 著色 (anchor 0 = 冷) + 阻挫邊 ===")
color = {0: 1}
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in color:
            color[v] = 1 - color[u]
            q.append(v)
frust = []
for u, v in edges:
    if color[u] == color[v]:
        frust.append((u, v))
print(f"  阻挫邊: {len(frust)} (期望 32)")

# ============ 5. k 值 = △阻挫 + ⬠阻挫 ============
log("\n=== 5. k 值分解 ===")
# 每節點: 三角形阻挫邊數 + 五邊形阻挫邊數
tri_frust = []   # 三角形面內嘅阻挫邊
pent_frust = []  # 五邊形面內嘅阻挫邊
frust_set = set(frust)
for tri in triangles:
    for a, b in [(tri[0],tri[1]), (tri[1],tri[2]), (tri[0],tri[2])]:
        e = (min(a,b), max(a,b))
        if e in frust_set:
            tri_frust.append(e)
for pent in pent_faces:
    for a, b in [(pent[0],pent[1]),(pent[1],pent[2]),(pent[2],pent[3]),(pent[3],pent[4]),(pent[4],pent[0])]:
        e = (min(a,b), max(a,b))
        if e in frust_set:
            pent_frust.append(e)
tri_frust = list(set(tri_frust))
pent_frust = list(set(pent_frust))
print(f"  三角形阻挫邊: {len(tri_frust)} (期望 20)")
print(f"  五邊形阻挫邊: {len(pent_frust)} (期望 12)")
print(f"  合計: {len(tri_frust) + len(pent_frust)} (期望 32)")

# 每節點 k = △端 + ⬠端
k_tri = Counter()
k_pent = Counter()
for a, b in tri_frust:
    k_tri[a] += 1; k_tri[b] += 1
for a, b in pent_frust:
    k_pent[a] += 1; k_pent[b] += 1
k_total = defaultdict(int)
for i in range(60):
    k_total[i] = k_tri[i] + k_pent[i]
# 同 anchored_coloring.txt 對照
k_ref = {}
with open(f"{BASE}/cmb_cold_spot/data/anchored_coloring.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        p = line.split()
        k_ref[int(p[0])] = int(p[4])
match = sum(1 for i in range(60) if k_total[i] == k_ref[i])
print(f"  k 值同參考對照: {match}/60 {'✅' if match==60 else '❌'}")

# 分佈
k_dist = Counter(k_total.values())
print(f"  k 分佈: {dict(sorted(k_dist.items()))} (期望 {{0:8, 1:40, 2:12}})")
# 分解 k=1: 三角形-only vs 五邊形-only
tri_only = [i for i in range(60) if k_tri[i] == 1 and k_pent[i] == 0]
pent_only = [i for i in range(60) if k_pent[i] == 1 and k_tri[i] == 0]
k2_nodes = [i for i in range(60) if k_total[i] == 2]
k0_nodes = [i for i in range(60) if k_total[i] == 0]
print(f"  k=2 (△+⬠ 雙阻挫): {len(k2_nodes)} -> {sorted(k2_nodes)}")
print(f"  k=1 △-only: {len(tri_only)}")
print(f"  k=1 ⬠-only: {len(pent_only)}")
print(f"  k=0: {len(k0_nodes)} -> {sorted(k0_nodes)}")

# ============ 6. 阻挫邊連接結構 ============
log("\n=== 6. 阻挫邊連接 (k 值之間) ===")
conn = Counter()
for e in tri_frust:
    a, b = e
    ka, kb = k_total[a], k_total[b]
    conn[("△", ka, kb)] += 1
for e in pent_frust:
    a, b = e
    ka, kb = k_total[a], k_total[b]
    conn[("⬠", ka, kb)] += 1
print("  三角形阻挫邊:")
for key in sorted(conn):
    if key[0] == "△":
        print(f"    {key[1]}↔{key[2]}: {conn[key]}")
print("  五邊形阻挫邊:")
for key in sorted(conn):
    if key[0] == "⬠":
        print(f"    {key[1]}↔{key[2]}: {conn[key]}")

# ============ 7. k=2 節點嘅面結構 ============
log("\n=== 7. k=2 節點係咪 1△ + 1⬠? ===")
# 每個 k=2 節點: 1 三角形阻挫邊 + 1 五邊形阻挫邊?
all_ok = all(k_tri[i] == 1 and k_pent[i] == 1 for i in k2_nodes)
print(f"  全部 k=2 節點 = 1△ + 1⬠: {all_ok}")
# k=2 節點參與嘅面
for i in k2_nodes[:6]:
    tris = [t for t in triangles if i in t]
    pents = [p for p in pent_faces if i in p]
    sqs = [s for s in squares if i in s]
    print(f"  #{i}: {len(tris)}△ {len(sqs)}□ {len(pents)}⬠ (期望 1/2/1)")

# ============ 8. random anchor 對照 ============
log("\n=== 8. random anchor 對照 (k 分佈係咪冷斑簽名?) ===")
rng = np.random.default_rng(13)
N = 2000
kdist_hist = Counter()
for trial in range(N):
    anchor = rng.integers(0, 60)
    col = {anchor: 1}
    qq = deque([anchor])
    while qq:
        u = qq.popleft()
        for v in adj[u]:
            if v not in col:
                col[v] = 1 - col[u]
                qq.append(v)
    # 阻挫邊
    fr = [e for e in edges if col[e[0]] == col[e[1]]]
    # 每節點 k
    kk = Counter()
    for a, b in fr:
        kk[a] += 1; kk[b] += 1
    dist = tuple(sorted(Counter(kk.values()).items()))
    kdist_hist[dist] += 1
print(f"  random anchor k 分佈變異: {len(kdist_hist)} 種")
# 最常見分佈
for dist, cnt in kdist_hist.most_common(8):
    print(f"    {dist}: {cnt/N*100:.1f}%")
# 冷斑 (anchor 0) 嘅分佈
obs = tuple(sorted(Counter(k_total.values()).items()))
print(f"  冷斑 anchor 0 分佈: {obs}")
pct = kdist_hist[obs] / N * 100
print(f"  出現率: {pct:.1f}%")
# 冷斑分佈喺全部中嘅排名 (按 k=2 數)
k2_hist = Counter()
for dist in kdist_hist:
    d = dict(dist)
    k2_hist[d.get(2, 0)] += kdist_hist[dist]
print(f"  k=2 數分佈: {dict(sorted(k2_hist.items()))}")
print(f"  冷斑 k=2 = 12: {(k2_hist.get(12,0)/N*100):.1f}%")

# ============ 9. 對徑對嘅 k 分佈 ============
log("\n=== 9. 對徑對 k 分佈 (30 對) ===")
# 對徑對
pairs = []
for i in range(60):
    for j in range(i+1, 60):
        a = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if a > 170:
            pairs.append((i, j))
print(f"  對徑對: {len(pairs)}")
pair_k = Counter()
for i, j in pairs:
    pair_k[(k_total[i], k_total[j])] += 1
for key in sorted(pair_k):
    print(f"    k={key[0]}↔{key[1]}: {pair_k[key]} 對")

import json
with open(os.path.join(OUT, "node57_kvalue_dynamics.txt"), "w") as f:
    f.write("\n".join(results) + "\n")
print(f"\n✅ 結果寫入 {OUT}/node57_kvalue_dynamics.txt")
