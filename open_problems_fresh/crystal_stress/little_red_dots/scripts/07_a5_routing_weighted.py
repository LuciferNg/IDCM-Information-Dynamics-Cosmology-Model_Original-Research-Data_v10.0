#!/usr/bin/env python3
"""
A₅ 晶網路由修正 — 阻挫邊加權 (Weighted Shortest Paths)
=========================================================
物理: 阻挫邊 = 拓撲應力集中 → 路由成本更高 (cost=2 vs 1)
→ 加權 BC 會打破頂點傳遞對稱性!

修正後:
- 高 frust 節點 → 更高 BC → 更高應力集中 → 更大 LRD 質量
- 可計算應力張量場分佈
"""
import math, json, os
import numpy as np

CMB_DATA = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/cmb_cold_spot/data'
OUT_DIR = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/crystal_stress/little_red_dots/data'

# ============ 1. 載入 ============
nodes = []
with open(f'{CMB_DATA}/a5_nodes.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        nodes.append({'id': len(nodes), 'ra': float(p[0]), 'dec': float(p[1])})
N = len(nodes)

def ang_dist(ra1, dec1, ra2, dec2):
    r1, d1 = math.radians(ra1), math.radians(dec1)
    r2, d2 = math.radians(ra2), math.radians(dec2)
    cosd = math.sin(d1)*math.sin(d2) + math.cos(d1)*math.cos(d2)*math.cos(r1-r2)
    return math.degrees(math.acos(max(-1, min(1, cosd))))

# 冷斑節點
cold_spot = (209, -57)
cs_node = min(range(N), key=lambda i: ang_dist(cold_spot[0], cold_spot[1], nodes[i]['ra'], nodes[i]['dec']))
cosmos_node = 8

# ============ 2. 建圖 (阻挫邊 cost=2, 普通邊 cost=1) ============
# 距離矩陣
d_mat = np.zeros((N, N))
for i in range(N):
    for j in range(N):
        d_mat[i,j] = ang_dist(nodes[i]['ra'], nodes[i]['dec'], nodes[j]['ra'], nodes[j]['dec'])

# 阻挫邊 (32 條)
frust_set = set()
with open(f'{CMB_DATA}/frustration_edges.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        u, v = int(p[0]), int(p[1])
        frust_set.add((min(u,v), max(u,v)))

# 建鄰接表 (所有邊)
adj = {i: [] for i in range(N)}  # (neighbor, cost)
for i in range(N):
    # 對每個節點, 搵最近嘅 4 個鄰居
    cand = [(d_mat[i,j], j) for j in range(N) if j != i]
    cand.sort()
    for _, j in cand[:4]:
        key = (min(i,j), max(i,j))
        cost = 2 if key in frust_set else 1
        adj[i].append((j, cost))

# 確認度數
deg = [len(adj[i]) for i in range(N)]
print(f"度數: min={min(deg)}, max={max(deg)}, all 4? {all(d==4 for d in deg)}")

# ============ 3. Dijkstra 最短路徑 (加權) ============
def dijkstra(start, adj, N):
    # 返回到所有節點嘅最短距離 (cost sum)
    INF = 10**9
    dist = [INF]*N
    prev = [-1]*N
    dist[start] = 0
    visited = [False]*N
    for _ in range(N):
        u = min((i for i in range(N) if not visited[i]), key=lambda i: dist[i])
        visited[u] = True
        for v, c in adj[u]:
            if dist[u] + c < dist[v]:
                dist[v] = dist[u] + c
                prev[v] = u
    return dist, prev

# 所有節點對最短路徑
hop_w = np.zeros((N, N), dtype=float)  # 加權距離
for i in range(N):
    d, _ = dijkstra(i, adj, N)
    hop_w[i] = d

# 加權直徑
diameter_w = np.max(hop_w)
print(f"加權直徑: {diameter_w:.1f} (成本單位)")

# 無加權 hop 距離 (cost=1 全部)
hop_u = np.zeros((N, N), dtype=int)
for i in range(N):
    for j in range(N):
        # 用 Euclidean 距離近似: hop = 加權路徑入面嘅邊數
        # 直接 BFS (無加權)
        pass

# BFS 無加權
adj_u = {i: [v for v,_ in adj[i]] for i in range(N)}
def bfs(start):
    dist = [-1]*N
    q = [start]
    dist[start] = 0
    for u in q:
        for v in adj_u[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist

for i in range(N):
    hop_u[i] = bfs(i)

print(f"加權 hop 矩陣: min={hop_w.min():.1f}, max={hop_w.max():.1f}, mean={hop_w.mean():.1f}")

# ============ 4. 加權 Betweenness Centrality ============
# 對所有節點對 (s,t), 計算經過 v 嘅最短路徑比例
BC_w = {i: 0.0 for i in range(N)}
for s in range(N):
    for t in range(s+1, N):
        d_st = hop_w[s, t]
        for v in range(N):
            if v == s or v == t: continue
            if abs(hop_w[s, v] + hop_w[v, t] - d_st) < 0.01:
                BC_w[v] += 1.0

# 歸一化
BC_norm = {i: BC_w[i] / ((N-1)*(N-2)/2) for i in range(N)}

# ============ 5. 結果 ============
print(f"\n{'='*72}")
print("加權路由屬性 (阻挫邊 cost=2)")
print(f"{'='*72}")

# 計算 frust count
frust_count = {i: 0 for i in range(N)}
for u,v in frust_set:
    frust_count[u] += 1
    frust_count[v] += 1

print(f"{'Node':>5} {'RA':>8} {'Dec':>8} {'Frust':>5} {'HopCS':>5} {'BC_w':>8} {'frust+1':>7} {'BC×f':>8}")
for i in range(N):
    f = frust_count[i]
    h = hop_u[cs_node, i]
    bc = BC_norm[i]
    print(f"{i:>5} {nodes[i]['ra']:>8.1f} {nodes[i]['dec']:>8.1f} {f:>5} {h:>5} {bc:>8.4f} {f+1:>7} {bc*(f+1):>8.4f}")

print(f"\nCOSMOS 節點 {cosmos_node}:")
f = frust_count[cosmos_node]
bc = BC_norm[cosmos_node]
print(f"  Frust={f}, HopCS={hop_u[cs_node, cosmos_node]}, BC_w={bc:.4f}")

# 統計
print(f"\nBC 分佈: min={min(BC_norm.values()):.4f}, max={max(BC_norm.values()):.4f}, "
      f"mean={np.mean(list(BC_norm.values())):.4f}, std={np.std(list(BC_norm.values())):.4f}")

# BC vs frust 相關性
bc_vals = [BC_norm[i] for i in range(N)]
f_vals = [frust_count[i] for i in range(N)]
corr = np.corrcoef(bc_vals, f_vals)[0,1]
print(f"BC vs Frust 相關係數: {corr:.4f}")

# BC vs HopCS 相關性
h_vals = [hop_u[cs_node, i] for i in range(N)]
corr2 = np.corrcoef(bc_vals, h_vals)[0,1]
print(f"BC vs HopCS 相關係數: {corr2:.4f}")

# 應力張量近似: S(i) = BC(i) × (frust(i)+1) / hop(i)
S = {i: BC_norm[i] * (frust_count[i]+1) / max(1, hop_u[cs_node, i]) for i in range(N)}
print(f"\n應力張量 S = BC × (frust+1) / hop:")
for i in sorted(S.keys(), key=lambda i: S[i], reverse=True)[:10]:
    print(f"  節點 {i}: S={S[i]:.4f} (f={frust_count[i]}, h={hop_u[cs_node,i]}, BC={BC_norm[i]:.4f})")
print(f"  ...")
for i in sorted(S.keys(), key=lambda i: S[i])[:5]:
    print(f"  節點 {i}: S={S[i]:.4f} (f={frust_count[i]}, h={hop_u[cs_node,i]}, BC={BC_norm[i]:.4f})")

print(f"\nCOSMOS 節點 {cosmos_node}: S={S[cosmos_node]:.4f}")
print(f"  S 排名: {sorted(S.values(), reverse=True).index(S[cosmos_node])+1}/{N}")

# 保存
results = {
    'n_nodes': N, 'diameter_w': float(diameter_w),
    'cs_node': cs_node, 'cosmos_node': cosmos_node,
    'nodes': [{'id': i, 'ra': nodes[i]['ra'], 'dec': nodes[i]['dec'],
               'frust_count': frust_count[i], 'hop_from_cs': int(hop_u[cs_node, i]),
               'bc_weighted': BC_norm[i], 'stress_S': S[i]} for i in range(N)],
    'corr_bc_frust': corr, 'corr_bc_hop': corr2
}
os.makedirs(OUT_DIR, exist_ok=True)
with open(f'{OUT_DIR}/a5_routing_weighted.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved a5_routing_weighted.json")