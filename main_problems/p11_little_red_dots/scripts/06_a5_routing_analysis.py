#!/usr/bin/env python3
"""
A₅ 晶網路由屬性計算 — Betweenness Centrality + Hop Distance + 應力張量
========================================================================
從 60 節點 + 120 邊 + 32 阻挫邊重建路由圖，計算每個節點嘅拓撲屬性。

然後檢查: LRD 質量標度同節點路由屬性 (Hop distance, BC, 度數) 有冇關聯。

先建圖，再計算。
"""
import math, json, os
import numpy as np

CMB_DATA = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/cmb_cold_spot/data'
OUT_DIR = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p11_little_red_dots/data'

# ============ 1. 載入 60 節點 ============
nodes = []
with open(f'{CMB_DATA}/a5_nodes.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        nodes.append({'id': len(nodes), 'ra': float(p[0]), 'dec': float(p[1])})
N = len(nodes)
print(f"節點: {N}")

# 搵 Cold Spot 節點 (最接近冷斑位置 209°, -57°)
def ang_dist(ra1, dec1, ra2, dec2):
    r1, d1 = math.radians(ra1), math.radians(dec1)
    r2, d2 = math.radians(ra2), math.radians(dec2)
    cosd = math.sin(d1)*math.sin(d2) + math.cos(d1)*math.cos(d2)*math.cos(r1-r2)
    return math.degrees(math.acos(max(-1, min(1, cosd))))

cold_spot = (209, -57)
min_d = 999
cs_node = 0
for n in nodes:
    d = ang_dist(cold_spot[0], cold_spot[1], n['ra'], n['dec'])
    if d < min_d:
        min_d = d
        cs_node = n['id']
print(f"冷斑最接近節點: {cs_node} (RA={nodes[cs_node]['ra']:.1f}, Dec={nodes[cs_node]['dec']:.1f}, d={min_d:.2f}°)")

# 搵 COSMOS 場最近節點
cosmos_field = (150.1, 2.2)
min_d_cosmos = 999
cosmos_node = 0
for n in nodes:
    d = ang_dist(cosmos_field[0], cosmos_field[1], n['ra'], n['dec'])
    if d < min_d_cosmos:
        min_d_cosmos = d
        cosmos_node = n['id']
print(f"COSMOS 場最近節點: {cosmos_node} (RA={nodes[cosmos_node]['ra']:.1f}, Dec={nodes[cosmos_node]['dec']:.1f}, d={min_d_cosmos:.2f}°)")

# ============ 2. 建圖 ============
# 用角距離判斷邊連接: 2 個節點如果係相鄰, 佢哋嘅角距離係固定嘅
# Rhombicosidodecahedron: 邊長 = 同一大圓上嘅固定角距
# 從 frustration_edges 搵邊: 每條邊由 RA1/Dec1 -> RA2/Dec2

# 先建立所有節點對嘅角距離矩陣
d_mat = np.zeros((N, N))
for i in range(N):
    for j in range(N):
        d_mat[i,j] = ang_dist(nodes[i]['ra'], nodes[i]['dec'], nodes[j]['ra'], nodes[j]['dec'])

# 從 frustration_edges.txt 搵已知邊 (有 node ID!)
edges = []
with open(f'{CMB_DATA}/frustration_edges.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        u, v = int(p[0]), int(p[1])
        edges.append((u, v, True))

# 搵其餘邊: rhombicosidodecahedron 每個節點度數=4
adj = {i: set() for i in range(N)}
frust_adj = {i: set() for i in range(N)}
for i, j, is_frust in edges:
    adj[i].add(j); adj[j].add(i)
    if is_frust:
        frust_adj[i].add(j); frust_adj[j].add(i)

# 補齊到度數 4
for i in range(N):
    cand = [(d_mat[i,j], j) for j in range(N) if j != i and j not in adj[i]]
    cand.sort()
    for _, j in cand:
        if len(adj[i]) >= 4: break
        if j not in adj[i]:
            adj[i].add(j); adj[j].add(i)
            edges.append((i, j, False))

# 重建邊列表 (保留 frust flag)
edge_set = set()
all_edges = []
frust_set = set()
for i, j, is_frust in edges:
    key = (min(i,j), max(i,j))
    if key not in edge_set:
        edge_set.add(key)
        all_edges.append((i, j, is_frust))
        if is_frust:
            frust_set.add(key)

# 重新計算 frust_counts
frust_counts = {i: 0 for i in range(N)}
for i, j, is_frust in all_edges:
    if is_frust:
        frust_counts[i] += 1
        frust_counts[j] += 1

print(f"邊: {len(all_edges)} (應 120)")

# ============ 3. 計算度數 ============
degrees = {i: len(adj[i]) for i in range(N)}
frust_counts = {i: 0 for i in range(N)}
for i, j, is_frust in all_edges:
    if is_frust:
        frust_counts[i] += 1
        frust_counts[j] += 1

print(f"\n度數分佈: {sorted(set(degrees.values()))}")
print(f"阻挫邊計數分佈: {sorted(set(frust_counts.values()))}")

# ============ 4. BFS 最短路由 ============
# 從每個節點 BFS 到所有其他節點
def bfs(start, adj, N):
    dist = [-1]*N
    q = [start]
    dist[start] = 0
    for u in q:
        for v in adj[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist

# 所有節點對最短距離
hop_dist = np.zeros((N, N), dtype=int)
for i in range(N):
    hop_dist[i] = bfs(i, adj, N)

diameter = np.max(hop_dist)
print(f"路由直徑: {diameter} hops")

# 從冷斑節點到所有節點嘅 hop 距離
hop_from_cs = hop_dist[cs_node]
print(f"從冷斑節點到各節點: min={hop_from_cs.min()}, max={hop_from_cs.max()}, mean={hop_from_cs.mean():.2f}")

# 從 COSMOS 節點到冷斑嘅 hop
hop_cs_to_cosmos = hop_dist[cs_node, cosmos_node]
print(f"冷斑→COSMOS 節點: {hop_cs_to_cosmos} hops")

# ============ 5. Betweenness Centrality ============
# 對所有節點對 (s,t), 計算經過 v 嘅最短路徑比例
BC = {i: 0.0 for i in range(N)}
for s in range(N):
    for t in range(s+1, N):
        # 所有 s→t 嘅最短路徑上嘅節點
        d_st = hop_dist[s, t]
        for v in range(N):
            if v == s or v == t: continue
            if hop_dist[s, v] + hop_dist[v, t] == d_st:
                BC[v] += 1.0

# 歸一化: BC / (N-1)(N-2)/2
BC_norm = {i: BC[i] / ((N-1)*(N-2)/2) for i in range(N)}

# ============ 6. 結果 ============
print(f"\n{'='*72}")
print("60 節點路由屬性")
print(f"{'='*72}")
print(f"{'Node':>5} {'RA':>8} {'Dec':>8} {'Deg':>4} {'Frust':>5} {'HopCS':>5} {'BC':>8}")
for i in range(N):
    print(f"{i:>5} {nodes[i]['ra']:>8.1f} {nodes[i]['dec']:>8.1f} {degrees[i]:>4} {frust_counts[i]:>5} {hop_from_cs[i]:>5} {BC_norm[i]:>8.4f}")

# 特別關注 COSMOS 節點
print(f"\nCOSMOS 場最近節點 {cosmos_node}:")
print(f"  Degree={degrees[cosmos_node]}, Frust={frust_counts[cosmos_node]}, HopCS={hop_from_cs[cosmos_node]}, BC={BC_norm[cosmos_node]:.4f}")

# Check if COSMOS node is special
print(f"\nCOSMOS 節點屬性排名:")
deg_rank = sorted([(degrees[i], i) for i in range(N)], reverse=True)
frust_rank = sorted([(frust_counts[i], i) for i in range(N)], reverse=True)
bc_rank = sorted([(BC_norm[i], i) for i in range(N)], reverse=True)
print(f"  Degree: rank {[pos for pos,(val,nid) in enumerate(deg_rank) if nid==cosmos_node][0]+1}/{N}")
print(f"  Frust:  rank {[pos for pos,(val,nid) in enumerate(frust_rank) if nid==cosmos_node][0]+1}/{N}")
print(f"  BC:     rank {[pos for pos,(val,nid) in enumerate(bc_rank) if nid==cosmos_node][0]+1}/{N}")

# Save
results = {
    'n_nodes': N, 'diameter': int(diameter),
    'cs_node': int(cs_node), 'cosmos_node': int(cosmos_node),
    'hop_cs_to_cosmos': int(hop_cs_to_cosmos),
    'nodes': [{'id': i, 'ra': nodes[i]['ra'], 'dec': nodes[i]['dec'],
               'degree': degrees[i], 'frust_count': frust_counts[i],
               'hop_from_cs': int(hop_from_cs[i]), 'bc': BC_norm[i]} for i in range(N)],
    'hop_dist_matrix': hop_dist.tolist()
}
os.makedirs(OUT_DIR, exist_ok=True)
with open(f'{OUT_DIR}/a5_routing_properties.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved a5_routing_properties.json")