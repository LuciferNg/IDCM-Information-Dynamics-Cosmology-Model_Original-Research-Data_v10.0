#!/usr/bin/env python3
"""
圖身份最終判定 — 精確邊長 (26.09°)
====================================
直方圖證實: 120 條邊 @ 26.09°, 下一層 @ 31.68°
閾值: 28° (26.09 同 31.68 之間)
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

THRESHOLD = 28.0  # 26.09 同 31.68 之間

adj = defaultdict(set)
edges_list = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < THRESHOLD:
            adj[i].add(j)
            adj[j].add(i)
            edges_list.append((i, j))

V = 60
E = len(edges_list)
print("=" * 66)
print(f"精確圖 (閾值 {THRESHOLD}°): V={V}, E={E}")
deg_dist = defaultdict(int)
for i in range(60):
    deg_dist[len(adj[i])] += 1
print(f"度數分佈: {dict(deg_dist)}")

# 搵所有 3-環, 4-環, 5-環
def find_cycles(n):
    cycles = set()
    for start in range(60):
        path = [start]
        visited = {start}
        def dfs(u, depth):
            if depth == n:
                if start in adj[u]:
                    cycles.add(tuple(sorted(path)))
                return
            for w in adj[u]:
                if w not in visited and w > start:
                    visited.add(w)
                    path.append(w)
                    dfs(w, depth+1)
                    path.pop()
                    visited.discard(w)
        dfs(start, 1)
    return cycles

tri = find_cycles(3)
sq = find_cycles(4)
pent = find_cycles(5)
print(f"\n3-環: {len(tri)}")
print(f"4-環: {len(sq)}")
print(f"5-環: {len(pent)}")

# 真正面 5-環 (冇弦)
face_pents = []
for cyc in pent:
    has_chord = False
    for i in range(5):
        for j in range(i+2, 5):
            if (i == 0 and j == 4) or (i == 3 and j == 4):
                continue
            if cyc[j] in adj[cyc[i]]:
                has_chord = True
                break
        if has_chord:
            break
    if not has_chord:
        face_pents.append(cyc)
print(f"真面 5-環 (冇弦): {len(face_pents)}")

# 邊嘅面佔用
edge_occ = defaultdict(list)
for cyc in tri:
    for i in range(3):
        e = tuple(sorted((cyc[i], cyc[(i+1)%3])))
        edge_occ[e].append('T')
for cyc in sq:
    for i in range(4):
        e = tuple(sorted((cyc[i], cyc[(i+1)%4])))
        edge_occ[e].append('S')
for cyc in face_pents:
    for i in range(5):
        e = tuple(sorted((cyc[i], cyc[(i+1)%5])))
        edge_occ[e].append('P')

occ_counts = defaultdict(int)
for e in edges_list:
    e = tuple(sorted(e))
    occ = ''.join(sorted(edge_occ[e]))
    occ_counts[occ] += 1
print(f"\n邊嘅面佔用分佈:")
for occ, cnt in sorted(occ_counts.items()):
    print(f"  {occ}: {cnt} 條邊")

# 判定
print(f"\n判定:")
if len(tri) == 20 and len(sq) == 30 and len(face_pents) == 12:
    print(f"  ✅ Rhombicosidodecahedron (小斜方截半二十面體)")
    print(f"  20Δ + 30□ + 12⬠ = 62 面")
    print(f"  Euler: V-E+F = {V}-{E}+62 = {V-E+62} ✅")
else:
    print(f"  ⚠️ 唔係標準 Rhombicosidodecahedron")
    print(f"  T={len(tri)} (20), S={len(sq)} (30), P={len(face_pents)} (12)")
    # 試其他組合: 30 個正方形 + 20 個六邊形?
    # 檢查 6-環
    hexa = find_cycles(6)
    face_hex = []
    for cyc in hexa:
        has_chord = False
        for i in range(6):
            for j in range(i+2, 6):
                if (i == 0 and j == 5) or (i == 4 and j == 5):
                    continue
                if cyc[j] in adj[cyc[i]]:
                    has_chord = True
                    break
            if has_chord:
                break
        if not has_chord:
            face_hex.append(cyc)
    print(f"  真面 6-環: {len(face_hex)}")

with open("data/graph_identity.txt", "w") as f:
    f.write(f"精確圖: V=60, E={E}, 閾值={THRESHOLD}°\n")
    f.write(f"度數: {dict(deg_dist)}\n")
    f.write(f"3-環={len(tri)}, 4-環={len(sq)}, 5-環={len(pent)}, 真面5={len(face_pents)}\n")
    if len(tri) == 20 and len(sq) == 30 and len(face_pents) == 12:
        f.write("身份: Rhombicosidodecahedron ✅\n")
print(f"\n已存: data/graph_identity.txt")
