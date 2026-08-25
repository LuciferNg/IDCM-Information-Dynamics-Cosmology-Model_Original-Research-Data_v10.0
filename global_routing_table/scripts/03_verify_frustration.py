#!/usr/bin/env python3
"""GRT-03: 阻挫邊驗證 + 正確 Backbone 分析.

從 anchored_coloring.txt 讀取 BFS 著色, 從圖邊界計算真正阻挫邊.
"""
import sys
sys.path.insert(0, ".")
from grt_common import (ang_deg, build_graph, edge_threshold_from_histogram,
                        load_frustration_edges, load_nodes)

nodes, vecs = load_nodes()
N = len(nodes)
thresh, _ = edge_threshold_from_histogram(vecs)
adj = build_graph(vecs, thresh)
frust_file = load_frustration_edges()

# 從 anchored_coloring.txt 讀取顏色
COLOR_PATH = "../../open_problems_fresh/cmb_cold_spot/data/anchored_coloring.txt"
colors = {}
with open(COLOR_PATH) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        idx = int(parts[0])
        color = int(parts[3])
        colors[idx] = color

print(f"顏色載入: 冷={sum(1 for c in colors.values() if c==1)}, 熱={sum(1 for c in colors.values() if c==0)}")

# 正確阻挫邊: 圖邊界中同色相鄰
true_frust = set()
for u in range(N):
    for v in adj[u]:
        if v > u and colors[u] == colors[v]:
            true_frust.add((u, v))

print(f"真正阻挫邊 (圖邊界 + 同色): {len(true_frust)} 條")
for u, v in sorted(true_frust):
    d = ang_deg(vecs[u], vecs[v])
    print(f"  ({u:2d},{v:2d}) dist={d:.4f}°")

# 檢查邊界分佈
norm_edges = []
for u in range(N):
    for v in adj[u]:
        if v > u and (u, v) not in true_frust:
            norm_edges.append((u, v))
print(f"正常邊: {len(norm_edges)} 條")

# 驗證: 每個 odd face 至少 1 條阻挫邊
# 阻挫邊總數 = 20Δ + 12⬠ = 32 (by skill)
print(f"預期阻挫邊: 32 (20Δ + 12⬠), 實際: {len(true_frust)}")
if len(true_frust) == 32:
    print("✅ 阻挫邊數量正確!")
else:
    print(f"⚠️ 偏差: {len(true_frust) - 32}")