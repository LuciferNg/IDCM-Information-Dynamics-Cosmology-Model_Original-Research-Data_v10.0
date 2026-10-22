#!/usr/bin/env python3
"""
19_graph_final.py — O26: 圖論 4 連發 (快速版)
=================================================
1. 20 三角形互不相交
2. 12 vs 8 三角形 k2 分佈
3. k2-k2 對徑交換對
4. 平面性: K5/K3,3 子圖 (快速搜索)
"""
import numpy as np
import math
import itertools
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

color = {0: 1}
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in color:
            color[v] = 1 - color[u]
            q.append(v)
k = [0]*60
for i in range(60):
    k[i] = sum(1 for v in adj[i] if color[v] == color[i])
frust = set()
for i in range(60):
    for j in adj[i]:
        if i < j and color[i] == color[j]:
            frust.add((i, j))

triangles = set()
for i in range(60):
    for j in adj[i]:
        if j <= i: continue
        for kk in adj[i] & adj[j]:
            if kk > j:
                triangles.add(tuple(sorted((i, j, kk))))
tri_edges = set()
for t in triangles:
    for a, b in [(t[0],t[1]),(t[1],t[2]),(t[0],t[2])]:
        tri_edges.add((min(a,b), max(a,b)))

results = []
def log(*args):
    line = " ".join(str(a) for a in args)
    print(line, flush=True)
    results.append(line)

log("=" * 72)
log("O26: 圖論最終 4 連發 (快速版)")
log("=" * 72)

# ============ 1. 三角形互不相交 ============
log("\n=== 1. 三角形互不相交證明 ===")
shared = 0
tri_list = list(triangles)
for i in range(len(tri_list)):
    for j in range(i+1, len(tri_list)):
        if set(tri_list[i]) & set(tri_list[j]):
            shared += 1
            if shared <= 5:
                log(f"  共享: {tri_list[i]} & {tri_list[j]}")
log(f"  共享節點三角形對: {shared} (0 = 完全不相交)")
tri_count = Counter()
for t in triangles:
    for x in t:
        tri_count[x] += 1
tc_dist = Counter(tri_count.values())
log(f"  節點-三角形隸屬分佈: {dict(sorted(tc_dist.items()))}")

# ============ 2. 三角形 k 分佈 ============
log("\n=== 2. 三角形 k 值分佈 ===")
k2set = set(x for x in range(60) if k[x] == 2)
k0set = set(x for x in range(60) if k[x] == 0)
tri_k2 = sum(1 for t in triangles if any(x in k2set for x in t))
tri_k0 = sum(1 for t in triangles if any(x in k0set for x in t))
log(f"  含 k=2 節點三角形: {tri_k2}/20")
log(f"  含 k=0 節點三角形: {tri_k0}/20")
for i in sorted(k0set):
    tris = [t for t in triangles if i in t]
    if tris:
        log(f"  k=0 #{i}: 喺 {len(tris)} 個三角形 {tris}")
pure = [t for t in triangles if not any(x in k2set for x in t)]
log(f"  純 k1 三角形 ({len(pure)}):")
for t in pure:
    log(f"    {t}: k={[k[x] for x in t]}")

# ============ 3. 三角形 hop 結構 ============
log("\n=== 3. 三角形 hop 結構 ===")
hop = [0]*60
qq = deque([0])
while qq:
    u = qq.popleft()
    for v in adj[u]:
        if hop[v] == 0 and v != 0:
            hop[v] = hop[u] + 1
            qq.append(v)
hop_dist = Counter()
for t in triangles:
    hs = tuple(sorted(hop[x] for x in t))
    hop_dist[hs] += 1
log(f"  三角形 hop 組合: {dict(sorted(hop_dist.items()))}")

# ============ 4. 對徑交換對 ============
log("\n=== 4. k2-k2 對徑交換對 ===")
def antip(x):
    best = None; ba = 1e9
    for y in range(60):
        if y == x: continue
        dd = math.degrees(math.acos(np.clip(np.dot(vecs[x], vecs[y]), -1, 1)))
        if dd > 170 and dd < ba:
            ba = dd; best = y
    return best
for a, b in [(12, 19), (45, 46)]:
    ap_a, ap_b = antip(a), antip(b)
    log(f"  #{a}↔#{b}: #{a}→對徑#{ap_a}, #{b}→對徑#{ap_b}")
    # 對徑伴侶之間有冇邊?
    has_edge = (min(ap_a, ap_b), max(ap_a, ap_b)) in set(edges)
    log(f"    對徑後 #{ap_a}↔#{ap_b} 有邊? {has_edge}")
    # 交叉: ap_a 同 b, ap_b 同 a
    d1 = math.degrees(math.acos(np.clip(np.dot(vecs[ap_a], vecs[b]), -1, 1)))
    d2 = math.degrees(math.acos(np.clip(np.dot(vecs[ap_b], vecs[a]), -1, 1)))
    log(f"    交叉距離: #{ap_a}-#{b} = {d1:.2f}°, #{ap_b}-#{a} = {d2:.2f}°")

# ============ 5. K5/K3,3 ============
log("\n=== 5. K5/K3,3 子圖 (快速) ===")
k5 = []
for i in range(60):
    for combo in itertools.combinations(list(adj[i]), 4):
        if all(combo[a] in adj[combo[b]] for a in range(4) for b in range(a+1, 4)):
            k5.append((i,) + combo)
            break
    if k5: break
log(f"  K5: {k5 if k5 else '冇'}")
k33 = []
for i in range(60):
    for combo in itertools.combinations(list(adj[i]), 3):
        if all(not (combo[a] in adj[combo[b]]) for a in range(3) for b in range(a+1, 3)):
            common = set(adj[combo[0]]) & set(adj[combo[1]]) & set(adj[combo[2]]) - {i}
            if len(common) >= 2:
                k33.append((i, combo, list(common)[:2]))
                break
    if k33: break
log(f"  K3,3: {k33 if k33 else '冇'}")
log(f"  → 冇子圖 K5/K3,3; 非平面性需要 minor 檢查 (若適用)")

with open(f"{OUT}/node57_graph_final.txt", "w") as f:
    f.write("\n".join(results) + "\n")
print(f"\n✅ 結果寫入 {OUT}/node57_graph_final.txt")
