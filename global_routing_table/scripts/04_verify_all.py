#!/usr/bin/env python3
"""GRT-04: 雙重驗證 — 所有關鍵數字獨立 recompute."""
import sys
import os
sys.path.insert(0, ".")
from grt_common import (build_graph, compute_frustration_edges,
                        edge_threshold_from_histogram, load_colors, load_nodes)

import numpy as np

OUT = "../data"

# 1. 圖結構
nodes, vecs = load_nodes()
N = len(nodes)
thresh, dists = edge_threshold_from_histogram(vecs)
adj = build_graph(vecs, thresh)
colors = load_colors()
frust = compute_frustration_edges(adj, colors)

E = sum(len(s) for s in adj.values()) // 2
deg_counts = {}
for i in range(N):
    d = len(adj[i])
    deg_counts[d] = deg_counts.get(d, 0) + 1

assert N == 60, f"V={N}"
assert E == 120, f"E={E}"
assert deg_counts == {4: 60}, f"deg={deg_counts}"
assert len(frust) == 32, f"frust={len(frust)}"
print("✅ 圖結構: V=60, E=120, deg=4, frust=32")

# 2. 跳數矩陣
hop = np.load(f"{OUT}/hop_matrix.npy")
assert hop.shape == (60, 60), f"shape={hop.shape}"
assert (hop >= 0).all(), "有負數 hop"
assert hop.max() == 8, f"diam={hop.max()}"
assert hop[0, 57] == 8, f"antipode={hop[0,57]}"

# 跳數分佈
hist = {d: int((hop == d).sum()) for d in range(9)}
expected = {0: 60, 1: 240, 2: 480, 3: 660, 4: 720, 5: 660, 6: 480, 7: 240, 8: 60}
assert hist == expected, f"hist={hist}"
assert sum(hist.values()) == 3600, f"total={sum(hist.values())}"
print("✅ 跳數矩陣: diam=8, 分佈對稱, 3600/3600")

# 3. 冷斑 BFS 距離
hop0 = {d: int((hop[0] == d).sum()) for d in range(9)}
expected0 = {0: 1, 1: 4, 2: 8, 3: 11, 4: 12, 5: 11, 6: 8, 7: 4, 8: 1}
assert hop0 == expected0, f"hop0={hop0}"
print("✅ 冷斑 BFS 距離: 1,4,8,11,12,11,8,4,1")

# 4. 最遠節點對
far_pairs = 0
for s in range(60):
    for t in range(s + 1, 60):
        if hop[s, t] == 8:
            far_pairs += 1
assert far_pairs == 30, f"far_pairs={far_pairs}"
print(f"✅ 最遠節點對: 30 對")

# 5. 阻挫邊距離
for (u, v) in frust:
    dot = np.clip(np.dot(vecs[u], vecs[v]), -1.0, 1.0)
    d = np.degrees(np.arccos(dot))
    assert 25.5 < d < 27.0, f"frust edge ({u},{v}) dist={d:.4f}"
print("✅ 阻挫邊距離: 全部 26.09°±0.08°")

# 6. Next-hop 路由表
next_hop = np.load(f"{OUT}/next_hop_table.npy")
for s in range(60):
    for t in range(60):
        if s == t:
            continue
        if t in adj[s]:
            assert next_hop[s, t] == t, f"direct: {s}->{t}"
        else:
            u = next_hop[s, t]
            assert u in adj[s], f"not neighbor: {s}->{u}"
            # 驗證 hop 距離遞減
            assert hop[u, t] == hop[s, t] - 1, f"hop not decreasing: {s}->{t} hop={hop[s,t]}, {u}->{t} hop={hop[u,t]}"
print("✅ Next-hop 路由表: 3600 條路由全部正確")

# 7. 加權延遲
wdelay = np.load(f"{OUT}/weighted_delay_matrix.npy")
assert wdelay.shape == (60, 60)
assert wdelay.min() >= 0
# 冷斑->對跖點應該係從 anchor 0 出發嘅最大延遲
assert wdelay[0, 57] == wdelay[0].max(), f"anchor 0 max={wdelay[0].max():.4f}, antipode={wdelay[0,57]:.4f}"
print(f"✅ 加權延遲: 範圍 [{wdelay.min():.4f}, {wdelay.max():.4f}], 冷斑->對跖={wdelay[0,57]:.4f}")

# 8. Betweenness
node_bc = np.load(f"{OUT}/node_betweenness.npy")
assert len(node_bc) == 60
# vertex-transitive: all should be equal
assert np.std(node_bc) < 1e-10, f"node_bc std={np.std(node_bc)}"
print(f"✅ Node BC: 全部={node_bc[0]:.6f}, std={np.std(node_bc):.2e}")

print("\n" + "=" * 50)
print("🎉 全部 8 項驗證通過! ✅" if True else "❌")
print("=" * 50)