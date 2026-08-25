#!/usr/bin/env python3
"""GRT-01: A5 晶網全域路由表 — All-Pairs Shortest Paths.

計算 60 節點 Rhombicosidodecahedron 網絡嘅:
1. 鄰接矩陣 (Adjacency Matrix)
2. BFS 全對最短路徑跳數 (Hop Distance Matrix)
3. 直徑/半徑/離心度 (網絡拓撲特徵)
4. Backbone 標記: 阻挫邊 = 內部通道 (L1), 正常邊 = L2
5. Fibonacci ladder 加權延遲矩陣 (傳輸延遲 = hop × ladder 加權)
"""
import sys
from collections import deque
import os

import numpy as np

sys.path.insert(0, ".")
from grt_common import (build_graph, compute_frustration_edges,
                        edge_threshold_from_histogram, load_colors,
                        load_nodes)

# Output directory
OUT = "../data"
os.makedirs(OUT, exist_ok=True)

# ---------- 1. 載入 + 建圖 ----------
nodes, vecs = load_nodes()
N = len(nodes)
thresh, dists = edge_threshold_from_histogram(vecs)
adj = build_graph(vecs, thresh)
colors = load_colors()
frust = compute_frustration_edges(adj, colors)

deg_counts = {}
for i in range(N):
    d = len(adj[i])
    deg_counts[d] = deg_counts.get(d, 0) + 1
E = sum(len(s) for s in adj.values()) // 2
print(f"[1] 節點 V={N}, 邊 E={E}, 度數分佈={deg_counts}")
print(f"    threshold={thresh:.3f}° (histogram gap), 阻挫邊={len(frust)}")

assert N == 60 and E == 120 and deg_counts == {4: 60}, "圖結構唔符合 A5 晶網"

# ---------- 2. BFS 全對最短路徑 ----------
def bfs_all_pairs(adj, N):
    """Floyd-Warshall 等價但 BFS 更快 (unweighted). 回傳 hop matrix + 路徑數."""
    hop = np.full((N, N), -1, dtype=np.int16)
    paths = np.zeros((N, N), dtype=np.int64)
    for s in range(N):
        hop[s, s] = 0
        paths[s, s] = 1
        q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if hop[s, v] == -1:
                    hop[s, v] = hop[s, u] + 1
                    paths[s, v] = paths[s, u]
                    q.append(v)
                elif hop[s, v] == hop[s, u] + 1:
                    paths[s, v] += paths[s, u]
    return hop, paths

def adj_pairs(adj):
    """產生所有無向邊 (u,v), u<v."""
    seen = set()
    for u in adj:
        for v in adj[u]:
            if v > u and (u, v) not in seen:
                seen.add((u, v))
                yield (u, v)

hop, npaths = bfs_all_pairs(adj, N)
assert (hop >= 0).all(), "圖唔連通!"

# ---------- 3. 網絡拓撲特徵 ----------
diam = int(hop.max())
ecc = hop.max(axis=1)
radius = int(ecc.min())
center = [i for i in range(N) if ecc[i] == radius]
periph = [i for i in range(N) if ecc[i] == diam]
hist = {d: int((hop == d).sum()) for d in range(diam + 1)}
print(f"[2] 直徑={diam} hops, 半徑={radius}, 中心節點={center}, 周邊節點={periph}")
print(f"    跳數分佈: {hist}")

# ---------- 4. Backbone: 阻挫邊 = 內部通道 (L1) ----------
# 阻挫邊 = 同色相鄰 = 拓撲缺陷通道 (frustration seam)
# 正常邊 = 雙色相鄰 = 普通鏈路 (L2)
backbone_edges = set()
for (u, v) in frust:
    backbone_edges.add((u, v))
    backbone_edges.add((v, u))
print(f"[3] Backbone 邊 (阻挫/內部通道) = {len(backbone_edges)//2} 條, "
      f"正常邊 = {E - len(backbone_edges)//2} 條")

# ---------- 5. Fibonacci ladder 加權 ----------
# 6-level ladder: 節點幅度 A_d = F_{6-d} 由 anchor(冷斑節點 0) BFS 距離 d 決定
# 見 10_hot_spot_levels.py: F5=5 (冷斑), F4=3, F3=2 (由 anchor 向外遞減)
# 邊權重 w(u,v) = 1 / 平均幅度 = 延遲 (幅度大 = 帶寬大 = 延遲細)
from grt_common import FIB
hop_from_anchor = hop[0]          # 由冷斑節點 0 到各節點嘅 hop
# hop 分佈: 從 anchor 0 嘅 BFS 距離 (由 skill: 1,4,8,11,12,11,8,4,1 共 60, 直徑=8)
hop_dist = {d: int((hop_from_anchor == d).sum()) for d in range(diam + 1)}
print(f"[4] 冷斑節點0 BFS距離分佈: {hop_dist}")

# Fibonacci ladder: d=0→F5=8, d=1→F4=5, d=2→F3=3, d=3→F2=2, d≥4→F1=1
ladder = np.array([FIB[max(0, 5 - d)] for d in hop_from_anchor], dtype=float)
lvl_dist = {f"F{max(0,5-d)}": int((ladder == FIB[max(0,5-d)]).sum()) for d in set(hop_from_anchor.tolist())}
print(f"    幅度分佈: {lvl_dist}")

# 加權延遲矩陣: 最短路徑嘅總加權距離 (Dijkstra, weight = 1/幅度)
import heapq
def dijkstra_weighted(adj, weights, s):
    dist = {s: 0.0}
    pq = [(0.0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, np.inf):
            continue
        for v in adj[u]:
            nd = d + weights[(min(u, v), max(u, v))]
            if nd < dist.get(v, np.inf):
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist

edge_w = {}
for (u, v) in adj_pairs(adj):
    a = (ladder[u] + ladder[v]) / 2
    edge_w[(min(u, v), max(u, v))] = 1.0 / a

wdelay = np.zeros((N, N))
for s in range(N):
    d = dijkstra_weighted(adj, edge_w, s)
    for t in range(N):
        wdelay[s, t] = d[t]

np.save(f"{OUT}/hop_matrix.npy", hop)
np.save(f"{OUT}/path_count_matrix.npy", npaths)
np.save(f"{OUT}/weighted_delay_matrix.npy", wdelay)
np.save(f"{OUT}/ladder_amplitude.npy", ladder)
print(f"[5] 已保存: hop_matrix.npy, path_count_matrix.npy, weighted_delay_matrix.npy, ladder_amplitude.npy")
print(f"    加權延遲範圍: [{wdelay.min():.4f}, {wdelay.max():.4f}], 冷斑->對跖點={wdelay[0, 57]:.4f}")
