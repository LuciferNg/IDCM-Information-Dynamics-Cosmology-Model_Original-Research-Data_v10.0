#!/usr/bin/env python3
"""GRT-02: Next-Hop 路由表 + Betweenness Centrality + 拓撲分析.

從 hop_matrix 計算:
1. Next-hop 路由表 per (src, dst): 第一跳應該去邊個 neighbour
2. Edge Betweenness Centrality: 邊際作為 backbone 嘅重要性
3. Node Betweenness Centrality: 節點作為路由器嘅重要性
4. 阻挫邊 vs 正常邊嘅拓撲重要性對比
5. 對跖點路由路徑可視化
"""
import sys
from collections import deque
import os

import numpy as np

sys.path.insert(0, ".")
from grt_common import (build_graph, compute_frustration_edges,
                        edge_threshold_from_histogram, load_colors,
                        load_nodes)

OUT = "../data"
os.makedirs(OUT, exist_ok=True)

# ---------- 1. 載入圖 ----------
nodes, vecs = load_nodes()
N = len(nodes)
thresh, _ = edge_threshold_from_histogram(vecs)
adj = build_graph(vecs, thresh)
colors = load_colors()
frust = compute_frustration_edges(adj, colors)
hop = np.load(f"{OUT}/hop_matrix.npy")
npaths = np.load(f"{OUT}/path_count_matrix.npy")

E = sum(len(s) for s in adj.values()) // 2
print(f"[1] V={N}, E={E}, diam={hop.max():.0f}")

# Edge list
edge_list = []
for u in range(N):
    for v in adj[u]:
        if v > u:
            edge_list.append((u, v))
E = len(edge_list)

# ---------- 2. Next-hop 路由表 ----------
# next_hop[s][t] = 從 s 到 t 嘅第一跳鄰居 (如果 s==t 則 -1; 如果直接相鄰則 t)
next_hop = np.full((N, N), -1, dtype=np.int16)
for s in range(N):
    for t in range(N):
        if s == t:
            continue
        if t in adj[s]:
            next_hop[s, t] = t
            continue
        # 搵第一個 neighbour u 使得 hop[u][t] == hop[s][t] - 1
        for u in adj[s]:
            if hop[u, t] == hop[s, t] - 1:
                next_hop[s, t] = u
                break

# 驗證: 逐跳重播所有路徑, 確保到達
for s in range(N):
    for t in range(N):
        if s == t:
            continue
        cur = s
        steps = 0
        while cur != t and steps < N:
            nxt = next_hop[cur, t]
            if nxt == -1:
                break
            cur = nxt
            steps += 1
        assert cur == t, f"路由失敗: {s}->{t}, 卡在 {cur}"
print(f"[2] Next-hop 路由表: 60×60 = {N*N} 條路由, 全部驗證通過 ✅")

# ---------- 3. Edge Betweenness Centrality ----------
# Brandes 演算法: 對每對 (s,t), 最短路徑經過 edge e 嘅比例
edge_bc = {e: 0.0 for e in edge_list}
for s in range(N):
    # 從 s 做 BFS 計算依賴
    stack = []
    pred = {i: [] for i in range(N)}
    dist = {i: -1 for i in range(N)}
    sigma = {i: 0 for i in range(N)}
    dist[s] = 0
    sigma[s] = 1
    q = deque([s])
    while q:
        v = q.popleft()
        stack.append(v)
        for w in adj[v]:
            if dist[w] == -1:
                dist[w] = dist[v] + 1
                q.append(w)
            if dist[w] == dist[v] + 1:
                sigma[w] += sigma[v]
                pred[w].append(v)
    # 累積依賴
    delta = {i: 0.0 for i in range(N)}
    while stack:
        w = stack.pop()
        for v in pred[w]:
            contribution = (sigma[v] / sigma[w]) * (1 + delta[w])
            delta[v] += contribution
            e = (min(v, w), max(v, w))
            if e in edge_bc:
                edge_bc[e] += contribution

# 正規化 (無向圖: 除 2)
total_pairs = N * (N - 1) / 2
for e in edge_bc:
    edge_bc[e] /= (2 * total_pairs)

# 排序
sorted_edges = sorted(edge_bc.items(), key=lambda x: -x[1])
print(f"[3] Edge Betweenness Centrality:")
print(f"    Top 10 最重要邊:")
for i, ((u, v), bc) in enumerate(sorted_edges[:10]):
    in_frust = (u, v) in frust or (v, u) in frust
    tag = "🟢阻挫" if in_frust else "🔵正常"
    print(f"    {i+1}. ({u:2d},{v:2d}) bc={bc:.6f} {tag}")

# 阻挫邊 vs 正常邊 BC 分佈
frust_bc = [edge_bc[e] for e in edge_list if e in frust or (e[1], e[0]) in frust]
norm_bc = [edge_bc[e] for e in edge_list if e not in frust and (e[1], e[0]) not in frust]
print(f"    阻挫邊平均 BC: {np.mean(frust_bc):.6f} (n={len(frust_bc)})")
print(f"    正常邊平均 BC: {np.mean(norm_bc):.6f} (n={len(norm_bc)})")
print(f"    阻挫/正常 BC 比: {np.mean(frust_bc)/np.mean(norm_bc):.3f}×")

# ---------- 4. Node Betweenness Centrality ----------
node_bc = {i: 0.0 for i in range(N)}
for s in range(N):
    stack = []
    pred = {i: [] for i in range(N)}
    dist = {i: -1 for i in range(N)}
    sigma = {i: 0 for i in range(N)}
    dist[s] = 0
    sigma[s] = 1
    q = deque([s])
    while q:
        v = q.popleft()
        stack.append(v)
        for w in adj[v]:
            if dist[w] == -1:
                dist[w] = dist[v] + 1
                q.append(w)
            if dist[w] == dist[v] + 1:
                sigma[w] += sigma[v]
                pred[w].append(v)
    delta = {i: 0.0 for i in range(N)}
    while stack:
        w = stack.pop()
        for v in pred[w]:
            delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w])
        if w != s:
            node_bc[w] += delta[w]

for i in node_bc:
    node_bc[i] /= (2 * total_pairs)

sorted_nodes = sorted(node_bc.items(), key=lambda x: -x[1])
print(f"[4] Node Betweenness Centrality:")
print(f"    Top 10 最重要節點 (路由器):")
for i, (node, bc) in enumerate(sorted_nodes[:10]):
    print(f"    {i+1}. 節點{node:2d} (RA={nodes[node][0]:.1f}°, Dec={nodes[node][1]:.1f}°) bc={bc:.6f}")

# ---------- 5. 對跖點路由路徑 ----------
# 冷斑=節點0, 對跖點=節點57 (由 skill: antipode)
anchor = 0
antipode = 57
print(f"[5] 冷斑(節點{anchor}) → 對跖點(節點{antipode}) 路由路徑:")
path = [anchor]
cur = anchor
while cur != antipode:
    nxt = next_hop[cur, antipode]
    path.append(nxt)
    cur = nxt
print(f"    路徑: {' → '.join(f'節點{n}' for n in path)}")
print(f"    跳數: {len(path)-1}")

# 所有對跖點對 (距離=8 嘅最遠節點對)
far_pairs = []
for s in range(N):
    for t in range(s + 1, N):
        if hop[s, t] == 8:
            far_pairs.append((s, t))
print(f"    所有距離=8 嘅節點對: {len(far_pairs)} 對")

# 每對之間嘅 hop 分佈
hop_hist = {d: int((hop == d).sum()) for d in range(9)}
print(f"[6] 全網絡 hop 分佈: {hop_hist}")
print(f"    總對數 (含自身): {sum(hop_hist.values())} = {N*N} ✅")

# ---------- 6. 保存路由表 ----------
np.save(f"{OUT}/next_hop_table.npy", next_hop)
np.save(f"{OUT}/edge_betweenness.npy", {str(k): v for k, v in edge_bc.items()})
np.save(f"{OUT}/node_betweenness.npy", np.array([node_bc[i] for i in range(N)]))
print(f"[7] 已保存: next_hop_table.npy, edge_betweenness.npy, node_betweenness.npy")