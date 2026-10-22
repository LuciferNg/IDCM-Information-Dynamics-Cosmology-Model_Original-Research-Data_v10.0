#!/usr/bin/env python3
"""
14_kvalue_fix.py — O26: k 值分解修正
================================================
13 腳本問題:
1. 正方形面 15 唔係 30 — 過濾錯
2. 五邊形阻挫邊 5 唔係 12 — 五邊形面搵錯
3. random anchor k 分佈 {1:40,2:12} vs 冷斑 {0:15,1:40,2:5} 矛盾

真相: 阻挫邊總數 32 固定, 但 k 值分佈由 anchor 決定?
- random anchor 2000 次全部得到 {1:40, 2:12} → k 分佈同 anchor 無關?
- 但冷斑 anchor 0 得到 {0:15, 1:40, 2:5}?

等等 — 冷斑嘅 k 值係由 anchored_coloring.txt 嚟 (k_ref), 可能同我計嘅唔同!
其實 k 值定義: 節點嘅阻挫邊數 = 同色鄰居數 (唔限面結構)
- k_ref (anchored_coloring): 每節點同色鄰居數
- 我計嘅 k_total = △阻挫 + ⬠阻挫 (只計面內阻挫)

正確方法: k(i) = 同色鄰居數 (直接由 BFS 著色 + 邊)
"""
import numpy as np
import math
import os
from collections import defaultdict, deque, Counter

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
OUT = os.path.join(BASE, "o26_node57_region", "data")

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
log("O26: k 值修正 — 直接同色鄰居數")
log("=" * 72)

# ============ 1. BFS 著色 (anchor 0) + 直接 k ============
log("\n=== 1. BFS 著色 + 同色鄰居數 (直接) ===")
color = {0: 1}
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in color:
            color[v] = 1 - color[u]
            q.append(v)
k_direct = [0]*60
for i in range(60):
    k_direct[i] = sum(1 for v in adj[i] if color[v] == color[i])
# 同參考對照
k_ref = {}
with open(f"{BASE}/cmb_cold_spot/data/anchored_coloring.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        p = line.split()
        k_ref[int(p[0])] = int(p[4])
match = sum(1 for i in range(60) if k_direct[i] == k_ref[i])
log(f"  直接 k vs 參考: {match}/60 {'✅' if match==60 else '❌'}")
dist = Counter(k_direct)
log(f"  k 分佈: {dict(sorted(dist.items()))} (參考: {{0:8, 1:40, 2:12}})")
k0 = [i for i in range(60) if k_direct[i] == 0]
k2 = [i for i in range(60) if k_direct[i] == 2]
log(f"  k=0: {sorted(k0)}")
log(f"  k=2: {sorted(k2)}")

# ============ 2. 修正: 用正確面結構 ============
def find_rings4():
    rings = set()
    for start in range(60):
        path = [start]
        vp = {start}
        def dfs(u, depth):
            if depth == 4:
                if start in adj[u]:
                    rings.add(tuple(sorted(path)))
                return
            for v in adj[u]:
                if v not in vp:
                    vp.add(v); path.append(v)
                    dfs(v, depth+1)
                    path.pop(); vp.discard(v)
        dfs(start, 1)
    return rings

def find_rings5():
    rings = set()
    for start in range(60):
        path = [start]
        vp = {start}
        def dfs(u, depth):
            if depth == 5:
                if start in adj[u]:
                    rings.add(tuple(sorted(path)))
                return
            for v in adj[u]:
                if v not in vp:
                    vp.add(v); path.append(v)
                    dfs(v, depth+1)
                    path.pop(); vp.discard(v)
        dfs(start, 1)
    return rings

log("\n=== 2. 面結構 (修正版) ===")
# 三角形: 20 (已確認)
triangles = set()
for i in range(60):
    for j in adj[i]:
        if j <= i: continue
        common = adj[i] & adj[j]
        for k in common:
            if k > j:
                triangles.add(tuple(sorted((i, j, k))))
print(f"  三角形: {len(triangles)}")

# 五邊形面: 用「面」嘅正確定義 — 最小環
# 12 個五邊形面 = 每個五邊形面嘅 5 條邊都唔屬於三角形
# 但 13 腳本得 12 個? 再驗證: 72 個 5-ring, 邊屬三角形過濾後 12
# 問題: 五邊形面嘅邊可能同三角形共享節點但唔共享邊?
# Rhombicosidodecahedron: 每條邊屬於 1 個三角形 OR 1 個正方形 OR 1 個五邊形?
# 實際: 每條邊屬於 2 個面 (多面體)
# 三角形面 20 × 3 邊 = 60 邊-面
# 五邊形面 12 × 5 = 60
# 正方形面 30 × 4 = 120
# 總邊-面 = 240 = 120 邊 × 2 ✓
# 所以: 每條邊屬於 2 個面

# 正確搵五邊形面: 5-ring 中, 所有邊都唔屬於三角形 = 五邊形面?
# 13 腳本: pent_faces = 12, 但唔齊?
# 其實應該有 12 個五邊形面 — 用「非三角形邊」嘅環
# 修正: 搵全部 5-ring, 邊唔喺三角形邊集
tri_edges = set()
for t in triangles:
    for a, b in [(t[0],t[1]), (t[1],t[2]), (t[0],t[2])]:
        tri_edges.add((min(a,b), max(a,b)))
print(f"  三角形邊: {len(tri_edges)} (期望 60)")

# 5-ring 過濾: 5 條邊全部唔係三角形邊
pent_faces = []
for ring in find_rings5():
    ok = True
    for a, b in [(ring[0],ring[1]),(ring[1],ring[2]),(ring[2],ring[3]),(ring[3],ring[4]),(ring[4],ring[0])]:
        if (min(a,b), max(a,b)) in tri_edges:
            ok = False
            break
    if ok:
        pent_faces.append(ring)
print(f"  五邊形面: {len(pent_faces)} (期望 12)")

# 正方形面: 4-ring, 邊唔係三角形邊, 而且唔係五邊形面嘅子環
# Rhombicosidodecahedron 30 個正方形: 每個正方形嘅 4 邊都唔係三角形邊
# 但 13 腳本得 15 — 因為條件「唔含三角形邊」可能排除咗正確嘅?
# 實際: 正方形面嘅邊係「正方形-正方形共享」定「正方形-五邊形共享」?
# 每條非三角形邊: 屬於 1 正方形 + 1 五邊形 (或 2 正方形?)
# 非三角形邊數 = 120 - 60 = 60
# 正方形面 30×4 = 120 邊-面, 五邊形面 12×5 = 60 → 60 條非三角形邊 × 2 = 120 ✓
# 所以每條非三角形邊 = 1 正方形 + 1 五邊形
# 正方形面 = 4-ring 其中邊係非三角形邊, 而且唔係五邊形面
squares = []
rings4 = find_rings4()
for ring in rings4:
    ok = True
    for a, b in [(ring[0],ring[1]),(ring[1],ring[2]),(ring[2],ring[3]),(ring[3],ring[0])]:
        if (min(a,b), max(a,b)) in tri_edges:
            ok = False
            break
    if ok:
        squares.append(ring)
print(f"  正方形面: {len(squares)} (期望 30)")

# ============ 3. k 值分解 (修正) ============
log("\n=== 3. k 值分解 (修正) ===")
frust = set()
for u, v in edges:
    if color[u] == color[v]:
        frust.add((u, v))
print(f"  阻挫邊: {len(frust)}")
# 每節點阻挫邊數 (直接, 唔限面)
k_direct2 = Counter()
for a, b in frust:
    k_direct2[a] += 1; k_direct2[b] += 1
print(f"  直接 k 分佈: {dict(sorted(Counter(k_direct2[i] for i in range(60)).items()))}")

# ============ 4. random anchor 對照 (修正: 直接計 k) ============
log("\n=== 4. random anchor 對照 ===")
rng = np.random.default_rng(14)
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
    kk = [0]*60
    for i in range(60):
        kk[i] = sum(1 for v in adj[i] if col[v] == col[i])
    dist = tuple(sorted(Counter(kk).items()))
    kdist_hist[dist] += 1
print(f"  random anchor k 分佈變異: {len(kdist_hist)} 種")
for dist, cnt in kdist_hist.most_common(10):
    print(f"    {dist}: {cnt/N*100:.1f}%")
obs = tuple(sorted(Counter(k_direct).items()))
print(f"  冷斑 anchor 0: {obs}")
print(f"  出現率: {kdist_hist.get(obs, 0)/N*100:.1f}%")

# ============ 5. 對徑對 k (直接) ============
log("\n=== 5. 對徑對 k 分佈 (直接) ===")
pairs = []
for i in range(60):
    for j in range(i+1, 60):
        a = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if a > 170:
            pairs.append((i, j))
pair_k = Counter()
for i, j in pairs:
    pair_k[(k_direct[i], k_direct[j])] += 1
for key in sorted(pair_k):
    print(f"    k={key[0]}↔{key[1]}: {pair_k[key]} 對")

with open(os.path.join(OUT, "node57_kvalue_fix.txt"), "w") as f:
    f.write("\n".join(results) + "\n")
print(f"\n✅ 結果寫入 {OUT}/node57_kvalue_fix.txt")
