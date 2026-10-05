#!/usr/bin/env python3
"""
精確圖重新驗證 — 錨定著色 + 阻挫邊 (閾值 28°)
================================================
之前用 d_min×1.05 = 27.4° 計嘅 32 條阻挫邊可能唔準
而家距離直方圖確認: 真正邊長 26.09°, 下一層 31.68°
用精確閾值 28° 重新計錨定著色
"""
import numpy as np
import math
from collections import defaultdict, deque

nodes = []
with open("data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))

vecs = []
for ra, dec in nodes:
    r, d = math.radians(ra), math.radians(dec)
    vecs.append(np.array([math.cos(d)*math.cos(r),
                          math.cos(d)*math.sin(r),
                          math.sin(d)]))
vecs = np.array(vecs)

THRESHOLD = 28.0
adj = defaultdict(set)
edges_list = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < THRESHOLD:
            adj[i].add(j)
            adj[j].add(i)
            edges_list.append((i, j))

print("=" * 66)
print(f"精確圖 (閾值 {THRESHOLD}°): {len(edges_list)} 條邊")
deg_dist = defaultdict(int)
for i in range(60):
    deg_dist[len(adj[i])] += 1
print(f"度數分佈: {dict(deg_dist)}")

# ============ 錨定著色 (冷斑 = 節點 0 = 冷) ============
color = {}
color[0] = 1  # 冷
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in color:
            color[v] = 1 - color[u]
            q.append(v)

n_cold = sum(1 for c in color.values() if c == 1)
n_hot = sum(1 for c in color.values() if c == 0)
print(f"\n冷: {n_cold}, 熱: {n_hot}")

frustration = []
for u in range(60):
    for v in adj[u]:
        if u < v and color[u] == color[v]:
            frustration.append((u, v))
print(f"阻挫邊: {len(frustration)}")

cc = [e for e in frustration if color[e[0]] == 1]
hh = [e for e in frustration if color[e[0]] == 0]
print(f"冷-冷: {len(cc)}, 熱-熱: {len(hh)}")

# 冷斑鄰居
print(f"\n冷斑 (節點 0) 鄰居顏色:")
for v in sorted(adj[0]):
    print(f"  {v}: {'冷❌' if color[v]==1 else '熱'}")

# ============ 阻挫邊座標 ============
print(f"\n阻挫邊 (RA, Dec 座標):")
with open("data/frustration_edges.txt", "w") as f:
    f.write("# u v color_u color_v ra_u dec_u ra_v dec_v\n")
    for u, v in frustration:
        ra_u, dec_u = nodes[u]
        ra_v, dec_v = nodes[v]
        f.write(f"{u} {v} {color[u]} {color[v]} {ra_u:.4f} {dec_u:.4f} {ra_v:.4f} {dec_v:.4f}\n")
        print(f"  ({ra_u:.1f}°, {dec_u:.1f}°) ↔ ({ra_v:.1f}°, {dec_v:.1f}°)  {'冷-冷' if color[u]==1 else '熱-熱'}")

# 阻挫網絡 component
frust_set = set()
for u, v in frustration:
    frust_set.add(u)
    frust_set.add(v)
print(f"\n阻挫涉及節點: {len(frust_set)}/60")

frust_adj = defaultdict(set)
for u, v in frustration:
    frust_adj[u].add(v)
    frust_adj[v].add(u)

seen = set()
components = []
for start in frust_set:
    if start in seen:
        continue
    comp = []
    q = deque([start])
    seen.add(start)
    while q:
        u = q.popleft()
        comp.append(u)
        for v in frust_adj[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    components.append(comp)
print(f"阻挫 component: {len(components)} 個")
for i, comp in enumerate(components):
    print(f"  C{i}: {len(comp)} 節點")

# 主縫合線
if components:
    main = max(components, key=len)
    print(f"\n主縫合線 ({len(main)} 節點):")
    for idx in main:
        ra, dec = nodes[idx]
        print(f"  ({ra:.1f}, {dec:.1f}) {'冷' if color[idx]==1 else '熱'}")

# 儲存著色
with open("data/anchored_coloring.txt", "w") as f:
    f.write("# idx RA Dec color(cold=1) frustration_neighbors\n")
    for i in range(60):
        ra, dec = nodes[i]
        fr = [v for v in adj[i] if color[v] == color[i]]
        f.write(f"{i} {ra:.4f} {dec:.4f} {color[i]} {len(fr)}\n")

print(f"\n✅ 精確圖數據已存: data/frustration_edges.txt + data/anchored_coloring.txt")
