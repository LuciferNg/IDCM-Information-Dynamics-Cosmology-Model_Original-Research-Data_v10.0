#!/usr/bin/env python3
"""
Rhombicosidodecahedron 完整驗證
=================================
頂點配置: 每頂點 1Δ + 2□ + 1⬠
- 20 三角形: ✅ 已確認 (每頂點 1 個)
- 30 正方形: ✅ 已確認
- 12 五邊形: 待驗證 — 由 5 個正方形圍繞嘅 5-環

Rhombicosidodecahedron 面結構:
- 每個五邊形面被 5 個正方形包圍
- 每個正方形面被 2Δ + 2⬠ 包圍
- 每個三角形面被 3 個正方形包圍

關鍵: 一個 5-環係「面」若且唯若:
- 環上每條邊都屬於一個正方形 (正方形鏈)
- 或者: 5-環內部冇其他頂點

用「5-環 + 每條邊有正方形」嚟搵真五邊形
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

# 正方形邊集合
sq_edges = set()
for cyc in sq:
    for i in range(4):
        e = tuple(sorted((cyc[i], cyc[(i+1)%4])))
        sq_edges.add(e)

# 真五邊形: 5-環, 其中每條邊都係正方形嘅一部分
print("=" * 66)
print("Rhombicosidodecahedron 五邊形驗證")
print("=" * 66)
print(f"三角形: {len(tri)}, 正方形: {len(sq)}, 5-環: {len(pent)}")
print(f"正方形邊: {len(sq_edges)} (120 條邊中)")

# 5-環中每條邊屬於正方形嘅數
pent_with_sq_edges = []
for cyc in pent:
    sq_edge_count = 0
    for i in range(5):
        e = tuple(sorted((cyc[i], cyc[(i+1)%5])))
        if e in sq_edges:
            sq_edge_count += 1
    pent_with_sq_edges.append((cyc, sq_edge_count))

# 統計
from collections import Counter
counts = Counter(c for _, c in pent_with_sq_edges)
print(f"\n5-環按正方形邊數分佈: {dict(sorted(counts.items()))}")

# 全部 5 條邊都係正方形邊嘅 5-環 = 五邊形面候選
candidates = [cyc for cyc, c in pent_with_sq_edges if c == 5]
print(f"\n全正方形邊 5-環: {len(candidates)} 個")

# 去重 (相鄰 5-環可能共享)
# 檢查候選係咪真正嘅「面」 — 冇弦
face_pents = []
for cyc in candidates:
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
print(f"冇弦全正方形邊 5-環 (真五邊形面): {len(face_pents)}")

# 檢查 Euler
F = len(tri) + len(sq) + len(face_pents)
V, E = 60, len(edges_list)
print(f"\nEuler 驗證:")
print(f"  F = {len(tri)} + {len(sq)} + {len(face_pents)} = {F}")
print(f"  V - E + F = {V} - {E} + {F} = {V - E + F}")

if len(tri) == 20 and len(sq) == 30 and len(face_pents) == 12 and V - E + F == 2:
    print(f"\n  ✅✅ Rhombicosidodecahedron 完全確認!")
    print(f"  20Δ + 30□ + 12⬠ = 62 面")
    print(f"  頂點配置: 每頂點 1Δ + 2□ + 1⬠")
else:
    print(f"\n  ⚠️ 未完全確認")
    print(f"  預期: 20Δ + 30□ + 12⬠ = 62, Euler=2")
    print(f"  實際: {len(tri)}Δ + {len(sq)}□ + {len(face_pents)}⬠ = {F}, Euler={V-E+F}")

with open("data/graph_identity.txt", "w") as f:
    f.write(f"V=60, E={E}, deg=4\n")
    f.write(f"三角形={len(tri)}, 正方形={len(sq)}, 5-環={len(pent)}\n")
    f.write(f"全正方形邊 5-環: {len(candidates)}\n")
    f.write(f"真五邊形面: {len(face_pents)}\n")
    f.write(f"F={F}, Euler={V-E+F}\n")
    if len(tri) == 20 and len(sq) == 30 and len(face_pents) == 12 and V - E + F == 2:
        f.write("身份: Rhombicosidodecahedron ✅\n")
    else:
        f.write("身份: 待定 — 五邊形面唔閉合\n")
print(f"\n已存: data/graph_identity.txt")
