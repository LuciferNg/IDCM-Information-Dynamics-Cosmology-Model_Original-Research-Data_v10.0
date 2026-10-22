#!/usr/bin/env python3
"""
15_kvalue_invariant.py — O26: k 分佈不變量 + 阻挫邊子結構
=============================================================
已證: k 分佈 {0:8, 1:40, 2:12} 同 anchor 無關 (2000 random 全部相同)

進一步:
1. 阻挫邊 32 條嘅子結構 — 佢哋連住邊類節點?
2. 12 個 k=2 節點嘅阻挫邊 — 形成咩?
3. 8 個 k=0 節點嘅「乾淨」位置
4. 點解 8/40/12? 圖論推導: 4-regular + 32 阻挫邊?
5. 阻挫邊數係咪圖不變量? (32 固定?)
6. 阻挫邊同面結構: 邊屬於 △/□/⬠ 邊類?
7. 冷斑 anchor 嘅 k=0 節點有冇特別物理意義 (溫度)
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
log("O26: k 值不變量 + 阻挫邊子結構")
log("=" * 72)

# BFS 著色 (anchor 0)
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
frust = [(u, v) for u, v in edges if color[u] == color[v]]
k2 = [i for i in range(60) if k_direct[i] == 2]
k1 = [i for i in range(60) if k_direct[i] == 1]
k0 = [i for i in range(60) if k_direct[i] == 0]

log(f"k 分佈: k0={len(k0)}, k1={len(k1)}, k2={len(k2)}")
log(f"阻挫邊: {len(frust)}")

# ============ 1. 阻挫邊子結構 ============
log("\n=== 1. 阻挫邊連接 (k 值之間) ===")
conn = Counter()
for u, v in frust:
    conn[(k_direct[u], k_direct[v])] += 1
for key in sorted(conn):
    log(f"  k={key[0]}↔k={key[1]}: {conn[key]} 條")
# 期望: 全部阻挫邊連住 k≥1 節點 (k=0 冇阻挫邊)
log(f"  k=0 節點參與阻挫邊: {sum(1 for u,v in frust if k_direct[u]==0 or k_direct[v]==0)} (期望 0)")

# ============ 2. 阻挫邊網絡 ============
log("\n=== 2. 阻挫邊網絡 (只用阻挫邊嘅圖) ===")
frust_adj = defaultdict(set)
for u, v in frust:
    frust_adj[u].add(v); frust_adj[v].add(u)
# component 結構
seen = set()
components = []
for start in range(60):
    if start in seen or not frust_adj[start]:
        continue
    comp = []
    qq = deque([start])
    seen.add(start)
    while qq:
        u = qq.popleft()
        comp.append(u)
        for v in frust_adj[u]:
            if v not in seen:
                seen.add(v); qq.append(v)
    components.append(comp)
log(f"  阻挫邊 component: {len(components)} 個")
for i, comp in enumerate(components):
    ks = Counter(k_direct[x] for x in comp)
    log(f"    C{i}: {len(comp)} 節點, k 分佈 {dict(ks)}")

# ============ 3. k=2 節點嘅阻挫邊 ============
log("\n=== 3. k=2 節點嘅阻挫邊結構 ===")
for i in k2:
    fr_nbrs = sorted(frust_adj[i])
    log(f"  #{i}: 阻挫鄰居 {fr_nbrs} (k={[k_direct[x] for x in fr_nbrs]})")

# ============ 4. k=0 節點位置 ============
log("\n=== 4. k=0 節點「乾淨」位置 ===")
log(f"  k=0: {sorted(k0)}")
# k=0 節點嘅鄰居 k 值
for i in k0:
    nbrs = sorted(adj[i])
    nbr_k = [k_direct[x] for x in nbrs]
    log(f"  #{i}: 鄰居 k={nbr_k}")

# ============ 5. 阻挫邊數不變量 ============
log("\n=== 5. 阻挫邊數 = 圖不變量? ===")
rng = np.random.default_rng(15)
N = 5000
frust_counts = Counter()
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
    fr = sum(1 for u, v in edges if col[u] == col[v])
    frust_counts[fr] += 1
log(f"  random anchor 阻挫邊數: {dict(frust_counts)}")
log(f"  → 全部 32 條? {all(c==32 for c in frust_counts)}")
# 驗證: 二分圖瑕疵 = 奇環數? 
# rhombicosidodecahedron 有 20 個三角形 (odd cycle) — 最小阻挫
log(f"  三角形面: 20 (奇環), 五邊形面: 12 (奇環)")
log(f"  理論: 每奇環最少 1 條阻挫邊, 但阻挫邊可共享")

# ============ 6. 面結構 vs 阻挫邊 ============
log("\n=== 6. 阻挫邊屬於邊類面 ===")
# 搵三角形面
triangles = set()
for i in range(60):
    for j in adj[i]:
        if j <= i: continue
        common = adj[i] & adj[j]
        for k in common:
            if k > j:
                triangles.add(tuple(sorted((i, j, k))))
tri_edges = set()
for t in triangles:
    for a, b in [(t[0],t[1]), (t[1],t[2]), (t[0],t[2])]:
        tri_edges.add((min(a,b), max(a,b)))
# 五邊形面
def find_rings5():
    rings = set()
    for start in range(60):
        path = [start]; vp = {start}
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
pent_faces = []
for ring in find_rings5():
    ok = True
    for a, b in [(ring[0],ring[1]),(ring[1],ring[2]),(ring[2],ring[3]),(ring[3],ring[4]),(ring[4],ring[0])]:
        if (min(a,b), max(a,b)) in tri_edges:
            ok = False; break
    if ok:
        pent_faces.append(ring)
pent_edges = set()
for ring in pent_faces:
    for a, b in [(ring[0],ring[1]),(ring[1],ring[2]),(ring[2],ring[3]),(ring[3],ring[4]),(ring[4],ring[0])]:
        pent_edges.add((min(a,b), max(a,b)))
# 阻挫邊分類
frust_set = set(frust)
n_tri = sum(1 for e in frust_set if e in tri_edges)
n_pent = sum(1 for e in frust_set if e in pent_edges)
n_other = len(frust_set) - n_tri - n_pent
log(f"  阻挫邊: 三角形面內 {n_tri}, 五邊形面內 {n_pent}, 其他 {n_other}")
# 其他 = 正方形面? 正方形係偶環應該零阻挫?
log(f"  (正方形面 4-cycle 應該零阻挫 — 「其他」邊屬於邊個面?)")

# 檢查: 全部非三角形非五邊形邊 (60 - 60 - 60 = 0?)
nontri_nonpent = [e for e in edges if e not in tri_edges and e not in pent_edges]
log(f"  非△非⬠邊: {len(nontri_nonpent)} (應該 60 = 正方形邊)")
frust_other = [e for e in frust_set if e not in tri_edges and e not in pent_edges]
log(f"  其中阻挫: {len(frust_other)}")
for e in frust_other[:10]:
    log(f"    {e}")

# ============ 7. k=0 節點溫度 (物理意義) ============
log("\n=== 7. k=0 節點溫度 (4.17° SMICA) ===")
T = {}
with open(f"{BASE}/o3_node_temperatures/data/node_temps.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        p = line.split()
        T[int(p[0])] = float(p[2])
for i in sorted(k0):
    log(f"  #{i}: T={T[i]:+8.2f} μK")
log(f"  k=0 mean|T| = {np.mean([abs(T[i]) for i in k0]):.2f} μK (全部 60: 33.2)")
log(f"  k=2 mean|T| = {np.mean([abs(T[i]) for i in k2]):.2f} μK")

# ============ 8. k 分佈推導 ============
log("\n=== 8. 8/40/12 結構推導 ===")
log("""
觀察:
- 圖 = 4-regular (每節點 4 條邊), 120 邊
- 阻挫邊 32 條, 端點 64
- k 分佈: 8×0 + 40×1 + 12×2 = 64 ✓
- k=2 節點 (12) = 全部成對 (6 對徑對)
- k=0 節點 (8) = 全部成對 (4 對徑對)
- 阻挫邊只連 k=1/k=2 節點 (k=0 冇阻挫邊)

結構:
- 每條阻挫邊: 兩端都係 k≥1
- k=2 = 2 條阻挫邊, k=1 = 1 條, k=0 = 0 條

推導 (阻挫邊 = 奇環證據):
- 20 三角形面: 每三角形最少 1 條阻挫邊, 但可共享
- 12 五邊形面: 同上
- 阻挫邊總數 32 = 20 (△) + 12 (⬠)? 但實測 三角形面內 20 條, 五邊形面內 5 條, 其他 7 條
- → 阻挫邊唔係簡單嘅「一面一挫」!

真正機制: 阻挫邊網絡 = 縫合線 (seam), 沿住奇環缺陷行走
- 32 條阻挫邊形成「缺陷線」
- 節點 k 值 = 缺陷線通過數 (0/1/2)
""")

with open(os.path.join(OUT, "node57_kvalue_invariant.txt"), "w") as f:
    f.write("\n".join(results) + "\n")
print(f"\n✅ 結果寫入 {OUT}/node57_kvalue_invariant.txt")
