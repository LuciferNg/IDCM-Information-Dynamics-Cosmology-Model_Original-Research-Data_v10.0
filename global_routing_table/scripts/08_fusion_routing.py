#!/usr/bin/env python3
"""GRT-08: A5 ⊗ K_Chain 融合路由表 (2640 邏輯節點).

核心概念:
- A5 晶網 (60 節點, 4-regular, 直徑 8) = 空間路由層
- K_Chain (44 site, 2-regular 環, 直徑 22) = 頻率/模式路由層
- 張量積: 每個邏輯節點 = (A5 節點 i, K_Chain mode n)
- 邏輯邊 = 兩個方向:
  1. A5 方向: (i,n) ↔ (j,n) 如果 (i,j) ∈ A5 邊 (空間跳躍, 保持 mode)
  2. K_Chain 方向: (i,n) ↔ (i,n±1) 如果 n±1 ∈ [1,44] (模式跳躍, 保持位置)

邏輯網絡度數 = 4 (A5) + 2 (K_Chain) = 6-regular
直徑 = diam(A5) + diam(K_Chain) = 8 + 22 = 30 hops (worst case)
但實際最短路徑 = min(A5 跳, K_Chain 跳) 混合路由
"""
import sys
import os
import heapq
from collections import deque

import numpy as np

sys.path.insert(0, ".")
from grt_common import (build_graph, compute_frustration_edges,
                        edge_threshold_from_histogram, load_colors, load_nodes)

OUT = "../data"
os.makedirs(OUT, exist_ok=True)

# ---------- 載入 A5 圖 ----------
nodes, vecs = load_nodes()
NA5 = len(nodes)
thresh, _ = edge_threshold_from_histogram(vecs)
adj5 = build_graph(vecs, thresh)
colors = load_colors()
frust = compute_frustration_edges(adj5, colors)
hop5 = np.load(f"{OUT}/hop_matrix.npy")

# ---------- K_Chain 參數 ----------
NK = 44
R_H = 4129.94  # Mpc
dx = R_H / NK

# K_Chain 鄰接: 一維環 (n=0..43, 對應 mode 1..44)
# n 連到 (n-1) mod 44 和 (n+1) mod 44
def kchain_neighbors(n):
    return [(n - 1) % NK, (n + 1) % NK]

# ---------- 構建張量積圖 ----------
# 邏輯節點 ID: id = i * NK + n  (i ∈ [0,60), n ∈ [0,44))
NLOG = NA5 * NK  # 2640
print(f"[1] 邏輯節點數: {NA5} × {NK} = {NLOG}")

# 張量積邊:
# A5 邊: (i,n) ↔ (j,n)  for (i,j) ∈ A5 edges, 每 i 有 4 條 → 4*2640/2 = 5280 條
# K_Chain 邊: (i,n) ↔ (i,n±1) → 2*2640/2 = 2640 條
# 總邊: 5280 + 2640 = 7920 條
n_a5_edges = sum(len(adj5[i]) for i in range(NA5)) // 2
n_k_edges = NK  # 每層 NK 條邊
EA5_LOG = n_a5_edges * NK   # 5280
EK_LOG = NA5 * NK           # 2640
print(f"[2] 融合邊: A5方向 {EA5_LOG} + K_Chain方向 {EK_LOG} = {EA5_LOG + EK_LOG}")

# 唔需要實際構建 2640×2640 鄰接矩陣 (太大), 用函數式鄰接
def log_neighbors(nid):
    """回傳邏輯節點 nid 嘅 6 個鄰居."""
    i, n = divmod(nid, NK)
    nbrs = []
    # A5 方向: 同 mode, 4 個 A5 鄰居
    for j in adj5[i]:
        nbrs.append(j * NK + n)
    # K_Chain 方向: 同位置, 2 個 mode 鄰居
    for m in kchain_neighbors(n):
        nbrs.append(i * NK + m)
    return nbrs

# ---------- 抽樣 BFS 路由分析 ----------
# 唔做全對 (2640² = 7M 對, 可行但慢), 做:
# 1. 選 30 對「最遠」邏輯節點 (A5 對跖點 × mode 相隔 22)
# 2. 計算直徑上界: diam5 + diamK = 30
# 3. 隨機抽樣 500 對做平均 hop 分佈

def bfs_dist(start, max_nodes=10000):
    """BFS 由 start 出發, 返回距離 dict (截斷到 max_nodes)."""
    dist = {start: 0}
    q = deque([start])
    count = 0
    while q and count < max_nodes:
        u = q.popleft()
        for v in log_neighbors(u):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
                count += 1
                if count >= max_nodes:
                    break
    return dist

# 抽樣: 冷斑邏輯節點 (0, 0) 出發
print(f"\n[3] 冷斑邏輯節點 (A5=0, K=mode1) BFS 抽樣:")
start = 0 * NK + 0  # A5 節點 0, mode 0
dist = bfs_dist(start)
max_d = max(dist.values())
print(f"    到達節點數: {len(dist)} / 2640")
print(f"    抽樣最大距離: {max_d} hops")
print(f"    距離分佈 (0-{min(max_d, 15)}):")
for d in range(min(max_d, 15) + 1):
    cnt = sum(1 for v in dist.values() if v == d)
    print(f"      d={d:<3}: {cnt}")

# 理論直徑: 8 + 22 = 30
print(f"\n[4] 理論直徑: diam(A5) + diam(K) = 8 + 22 = 30 hops")
print(f"    (worst case: A5 全跳 + K_Chain 全跳)")

# 搵實際最遠對 (30 對 A5 對跖 × K mode 相隔 22)
print(f"\n[5] 對跖邏輯節點對 (A5 antipode × K mode 相隔 22):")
far_pairs = []
for i in range(NA5):
    for j in range(i + 1, NA5):
        if hop5[i, j] == 8:
            for n in range(NK):
                m = (n + 22) % NK
                far_pairs.append((i * NK + n, j * NK + m))
print(f"    理論最遠對數: {len(far_pairs)} (30 × 44 = 1320)")

# 抽樣 20 對計實際距離
print(f"\n[6] 抽樣 20 對實際距離:")
import random
random.seed(42)
sample = random.sample(far_pairs, 20)
dists = []
for s, t in sample:
    # 雙向 BFS (太快唔使, 直接 BFS 由 s)
    d = bfs_dist(s, max_nodes=5000)
    dist_val = d.get(t, -1)
    dists.append(dist_val)
    i1, n1 = divmod(s, NK)
    i2, n2 = divmod(t, NK)
    print(f"    A5({i1},mode{n1}) → A5({i2},mode{n2}): {dist_val} hops")

print(f"\n    抽樣平均距離: {np.mean([d for d in dists if d > 0]):.1f} hops")
print(f"    抽樣最大距離: {max(dists)} hops")
print(f"    (理論上界 30 hops)")

# ---------- 融合路由策略 ----------
print(f"\n[7] 融合路由策略 (A5 ⊗ K_Chain):")
print(f"    每個邏輯節點 (i,n) 嘅 6 個鄰居:")
print(f"      A5 方向 (4): 空間路由 — 保持 mode n, 跳到 A5 鄰居")
print(f"      K 方向 (2):   頻率路由 — 保持位置 i, 跳到 mode n±1")
print(f"")
print(f"    最短路由 = min(A5 空間跳數, K 頻率跳數, 混合):")
print(f"      純空間: hop5[i,j] (最多 8)")
print(f"      純頻率: min(|n-m|, 44-|n-m|) (最多 22)")
print(f"      混合:    空間跳 + 頻率跳 (可以並行)")
print(f"")
print(f"    🚀 關鍵: 頻率層 (K_Chain) 係「即時」層!")
print(f"    mode 同步 = 相位鎖定 = 無需空間移動")
print(f"    → 真正嘅「曲速」= K_Chain mode 切換, 唔係 A5 空間跳躍!")

# ---------- 保存 ----------
np.save(f"{OUT}/fusion_logical_nodes.npy", np.array([NA5, NK, NLOG]))
print(f"\n[8] 已保存: fusion_logical_nodes.npy = [{NA5}, {NK}, {NLOG}]")