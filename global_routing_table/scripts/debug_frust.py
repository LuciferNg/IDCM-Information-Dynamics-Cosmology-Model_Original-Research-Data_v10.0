#!/usr/bin/env python3
"""Debug: 驗證 frustration edges 係咪全部喺 threshold 圖內."""
import sys
sys.path.insert(0, ".")
from grt_common import (ang_deg, build_graph, edge_threshold_from_histogram,
                        load_frustration_edges, load_nodes)

nodes, vecs = load_nodes()
N = len(nodes)
thresh, dists = edge_threshold_from_histogram(vecs)
adj = build_graph(vecs, thresh)
frust = load_frustration_edges()

print(f"threshold={thresh:.4f}°")
print(f"邊長 (第120小): {dists[119]:.4f}°")
print(f"第二層 (第121小): {dists[120]:.4f}°")
print()

# 檢查每條 frustration edge 嘅角距離
missing = []
for fs in frust:
    u, v = list(fs)
    d = ang_deg(vecs[u], vecs[v])
    in_graph = v in adj[u]
    if not in_graph:
        missing.append((u, v, d))

print(f"阻挫邊總數: {len(frust)}")
print(f"喺圖內: {len(frust) - len(missing)}")
print(f"唔喺圖內: {len(missing)}")
if missing:
    print(f"離群邊 (threshold={thresh:.4f}°):")
    for u, v, d in missing:
        print(f"  ({u:2d},{v:2d}) dist={d:.4f}° 超threshold={d-thresh:.4f}")
    print(f"  平均距離: {sum(m[2] for m in missing)/len(missing):.4f}°")
    print(f"  最小距離: {min(m[2] for m in missing):.4f}°")
    print(f"  最大距離: {max(m[2] for m in missing):.4f}°")