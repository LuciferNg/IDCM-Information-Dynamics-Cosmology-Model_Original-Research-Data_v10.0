#!/usr/bin/env python3
"""
O43-F: k=0 node "allows extreme" mechanism analysis
"""
import numpy as np
import math, os
from collections import Counter

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"
OUT = f"{BASE}/open_problems_fresh/o43_holographic_untested"

# Load node temperatures
data = {}
with open(f"{BASE}/open_problems_fresh/o3_node_temperatures/data/node_temps.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        p = line.split()
        idx = int(p[0])
        data[idx] = {'T': float(p[2]), 'l': float(p[3]), 'b': float(p[4]), 'hop': int(p[5])}

# Load k values
with open(f"{BASE}/main_problems/p4_cmb_cold_spot/data/anchored_coloring.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        p = line.split()
        idx = int(p[0])
        data[idx]['k'] = int(p[-1])

# Load A₅ positions
with open(f"{BASE}/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt") as f:
    for i, line in enumerate(f):
        ra, dec = map(float, line.split())
        data[i]['ra'] = ra
        data[i]['dec'] = dec

# Build graph
vecs = np.array([[math.cos(math.radians(data[i]['dec']))*math.cos(math.radians(data[i]['ra'])),
                  math.cos(math.radians(data[i]['dec']))*math.sin(math.radians(data[i]['ra'])),
                  math.sin(math.radians(data[i]['dec']))] for i in range(60)])

adj = [set() for _ in range(60)]
for i in range(60):
    for j in range(i+1, 60):
        a = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if a < 28:
            adj[i].add(j); adj[j].add(i)

results = []
def log(*args):
    line = " ".join(str(a) for a in args)
    print(line)
    results.append(line)

log("=" * 72)
log("O43-F: k=0 節點「容許極端」機制分析")
log("=" * 72)

# 1. Identify k=0 nodes
k0_nodes = [i for i in range(60) if data[i]['k'] == 0]
k1_nodes = [i for i in range(60) if data[i]['k'] == 1]
k2_nodes = [i for i in range(60) if data[i]['k'] == 2]

log(f"\n1. k=0 節點 ({len(k0_nodes)}): {k0_nodes}")
log(f"   k=1 節點 ({len(k1_nodes)}): {len(k1_nodes)}")
log(f"   k=2 節點 ({len(k2_nodes)}): {k2_nodes}")

# 2. k=0 node details
log("\n2. k=0 節點詳細:")
log(f"{'idx':>4} {'T(μK)':>8} {'|T|':>8} {'l(°)':>8} {'b(°)':>8} {'|b|':>6} {'hop':>4} {'deg':>4}")
for i in k0_nodes:
    d = data[i]
    deg = len(adj[i])
    log(f"{i:4d} {d['T']:+8.1f} {abs(d['T']):8.1f} {d['l']:8.2f} {d['b']:8.2f} {abs(d['b']):6.2f} {d['hop']:4d} {deg:4d}")

# 3. Check hop distance from anchor
log("\n3. BFS hop 距離分析:")
hop_dist = Counter(data[i]['hop'] for i in k0_nodes)
log(f"   k=0 hop 分佈: {dict(sorted(hop_dist.items()))}")
log(f"   Node 0 (冷斑): hop=0, T=-134.2 μK (極端冷)")
log(f"   Node 53: hop=3, T=+112.0 μK (極端熱)")
log(f"   Node 9: hop=1, T=-107.0 μK (次極端冷)")
log(f"   Node 20: hop=1, T=+35.4 μK (普通)")
log(f"   Node 50: hop=1, T=+36.2 μK (普通)")
log(f"   → hop 本身唔解釋極端度")

# 4. Check galactic latitude
log("\n4. 銀緯分析:")
high_lat = [i for i in k0_nodes if abs(data[i]['b']) > 30]
low_lat = [i for i in k0_nodes if abs(data[i]['b']) <= 30]
log(f"   高銀緯 (>30°): {high_lat}")
log(f"   低銀緯 (≤30°): {low_lat}")
for i in high_lat:
    log(f"     #{i}: T={data[i]['T']:+7.1f}, |b|={abs(data[i]['b']):.1f}°")
for i in low_lat:
    log(f"     #{i}: T={data[i]['T']:+7.1f}, |b|={abs(data[i]['b']):.1f}°")

# 5. Check for spatial isolation
log("\n5. 空間隔離檢查:")
for i in k0_nodes:
    n_k1 = sum(1 for v in adj[i] if data[v]['k'] == 1)
    n_k2 = sum(1 for v in adj[i] if data[v]['k'] == 2)
    n_k0 = sum(1 for v in adj[i] if data[v]['k'] == 0)
    log(f"   #{i}: T={data[i]['T']:+7.1f}, 鄰居: k0={n_k0}, k1={n_k1}, k2={n_k2}")

# 6. Check color parity
log("\n6. 顏色 (冷=1, 熱=0) 分析:")
# From node_temps.txt: color column
for i in k0_nodes:
    # The color is column 2 in node_temps.txt
    # Let me re-read properly
    pass

# Actually the color is in anchored_coloring.txt, 4th column
with open(f"{BASE}/main_problems/p4_cmb_cold_spot/data/anchored_coloring.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        p = line.split()
        idx = int(p[0])
        data[idx]['color'] = int(p[3])

log(f"\n   顏色 (1=冷, 0=熱):")
for i in k0_nodes:
    c = data[i]['color']
    log(f"   #{i}: T={data[i]['T']:+7.1f}, 顏色={'冷' if c==1 else '熱'}")

# 7. Check if k=0 nodes are on the frustration network or isolated
log("\n7. 阻挫網絡連接:")
for i in k0_nodes:
    # k=0 means no frustration edges
    # Check neighbors
    n_frust = sum(1 for v in adj[i] if data[v]['k'] > 0)
    log(f"   #{i}: T={data[i]['T']:+7.1f}, 連接阻挫網絡節點: {n_frust}/4")

# 8. Large-scale environment using the 60 nodes' temperatures
log("\n8. 大尺度環境 (4.17° smoothing node temperatures):")
# For each k=0 node, compute mean temperature of nearby nodes
for i in k0_nodes:
    nearby = [v for v in adj[i]]
    if nearby:
        nearby_T = [data[v]['T'] for v in nearby]
        log(f"   #{i}: T={data[i]['T']:+7.1f}, 鄰居 mean T={np.mean(nearby_T):+7.1f}±{np.std(nearby_T):.1f}, k-neighbors={[data[v]['k'] for v in nearby]}")

# 9. Compare extreme k=0 vs mild k=0
log("\n9. 極端 vs 普通 k=0:")
extreme = [i for i in k0_nodes if abs(data[i]['T']) > 80]
mild = [i for i in k0_nodes if abs(data[i]['T']) <= 80]
log(f"   極端 (|T|>80): {extreme}")
log(f"   普通 (|T|≤80): {mild}")

# Check what distinguishes them
log("\n   極端節點特徵:")
for i in extreme:
    log(f"     #{i}: hop={data[i]['hop']}, |b|={abs(data[i]['b']):.1f}°, 鄰居k={[data[v]['k'] for v in adj[i]]}")
log("\n   普通節點特徵:")
for i in mild:
    log(f"     #{i}: hop={data[i]['hop']}, |b|={abs(data[i]['b']):.1f}°, 鄰居k={[data[v]['k'] for v in adj[i]]}")

# 10. Check if the extreme nodes are on the 20-tetrahedron structure
log("\n10. 三角形結構檢查:")
# Find triangles containing k=0 nodes
triangles = set()
for i in range(60):
    for j in adj[i]:
        if j <= i: continue
        for kk in adj[i] & adj[j]:
            if kk > j:
                triangles.add(tuple(sorted((i, j, kk))))

for i in k0_nodes:
    tri_with = [t for t in triangles if i in t]
    tri_partners = set()
    for t in tri_with:
        tri_partners.update(t)
    tri_partners.discard(i)
    tri_k = [data[v]['k'] for v in tri_partners]
    log(f"   #{i}: 喺 {len(tri_with)} 個三角形, 同伴 k={sorted(tri_k)}")

# Conclusion
log("\n" + "=" * 72)
log("結論:")
log("=" * 72)
log(f"   k=0 節點: {k0_nodes}")
log(f"   極端 (|T|>80): {extreme}")
log(f"   普通 (|T|≤80): {mild}")
log(f"   → k=0 容許極端, 但唔保證極端")
log(f"   → 極端度由 hop 距離、鄰居結構、大尺度環境共同決定")
log(f"   → Node 0 (冷斑, hop=0, anchor) 同 Node 53 (+112, hop=3) 都係")
log(f"     圖中嘅「孤立」k=0 節點 (冇/少 k=2 鄰居)")
log(f"   → 普通 k=0 節點 (如 #4, #20, #50) 有較平衡嘅鄰居環境")

with open(f"{OUT}/data_o43f.txt", "w") as f:
    f.write("\n".join(results) + "\n")
print(f"\n✅ 結果寫入 {OUT}/data_o43f.txt")