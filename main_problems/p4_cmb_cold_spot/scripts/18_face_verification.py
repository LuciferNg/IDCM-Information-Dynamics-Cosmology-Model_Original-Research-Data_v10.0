#!/usr/bin/env python3
"""
18_face_verification.py — 面遍歷 (Face Traversal) 完整驗證
============================================================
方法: 標準多面體面遍歷演算法
- 每個頂點嘅鄰居按切平面極角排序
- 每條有向邊 (u→v): 下一個面邊 = (v→w), w = v 嘅鄰居中 u 嘅下一個
- 遍歷直到返返起點 → 一個面
- 每條無向邊有 2 個方向 → 2 個面

驗證目標 (Gemini Euler 論證):
1. F = 62 = 20Δ + 30□ + 12⬠
2. V - E + F = 60 - 120 + 62 = 2 ✅
3. 阻挫飽和: 每個奇面 (Δ, ⬠) 啱啱 1 條阻挫邊 → 總共 32 = 20 + 12
"""
import numpy as np
import math
from collections import defaultdict, deque

# ============ 載入節點 + 建圖 ============
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

V, E = 60, len(edges_list)
print("=" * 66)
print("面遍歷驗證 (Face Traversal)")
print("=" * 66)
print(f"V = {V}, E = {E}, degree = 4 (全部)")

# ============ 1. 每頂點鄰居極角排序 ============
order = {}      # v -> [neighbors in angular order]
pos = {}        # (v, u) -> index in order[v]
for v in range(60):
    vv = vecs[v]
    # 切平面基底
    e1 = np.array([-vv[1], vv[0], 0.0])
    if np.linalg.norm(e1) < 1e-9:
        e1 = np.array([1.0, 0.0, 0.0])
    e1 = e1 / np.linalg.norm(e1)
    e2 = np.cross(vv, e1)
    angles = {}
    for u in adj[v]:
        angles[u] = math.atan2(np.dot(vecs[u], e2), np.dot(vecs[u], e1))
    order[v] = sorted(adj[v], key=lambda u: angles[u])
    for idx, u in enumerate(order[v]):
        pos[(v, u)] = idx

# ============ 2. 面遍歷 ============
next_edge = {}
for u in range(60):
    for v in adj[u]:
        # 有向邊 u→v: 喺 v 度揀 u 嘅下一個鄰居 (順時針)
        idx_u = pos[(v, u)]
        w = order[v][(idx_u + 1) % 4]
        next_edge[(u, v)] = (v, w)

faces = []          # list of vertex lists (cyclic order)
seen_directed = set()
for (u, v) in edges_list:
    for start in [(u, v), (v, u)]:
        if start in seen_directed:
            continue
        path = []
        cur = start
        while cur not in seen_directed:
            seen_directed.add(cur)
            path.append(cur[0])
            cur = next_edge[cur]
        faces.append(path)

# 去重 (唔同面有唔同頂點集)
unique_faces = {}
for face in faces:
    key = frozenset(face)
    unique_faces[key] = face
face_list = list(unique_faces.values())

tri = [f for f in face_list if len(f) == 3]
sq = [f for f in face_list if len(f) == 4]
pent = [f for f in face_list if len(f) == 5]
other = [f for f in face_list if len(f) not in (3, 4, 5)]

print(f"\n面數: 三角形 {len(tri)}, 正方形 {len(sq)}, 五邊形 {len(pent)}")
if other:
    print(f"其他: {[(len(f), f) for f in other]}")

# ============ 3. Euler 驗證 ============
F = len(face_list)
print(f"\nEuler 驗證:")
print(f"  F = {len(tri)} + {len(sq)} + {len(pent)} = {F}")
print(f"  V - E + F = {V} - {E} + {F} = {V - E + F}")
chi = V - E + F
print(f"  χ = {chi} {'✅ 球面拓撲!' if chi == 2 else '❌'}")

# 面邊總數 = 2E?
edge_inc = sum(len(f) for f in face_list)
print(f"  面-邊總數 = {edge_inc} = 2E = {2*E} {'✅' if edge_inc == 2*E else '❌'}")

# ============ 4. 邊類型: 三角形-正方形 vs 五邊形-正方形 ============
edge_faces = defaultdict(list)  # edge -> [face_type]
for f in face_list:
    ft = 'T' if len(f) == 3 else ('S' if len(f) == 4 else ('P' if len(f) == 5 else '?'))
    n = len(f)
    for i in range(n):
        e = tuple(sorted((f[i], f[(i+1) % n])))
        edge_faces[e].append(ft)

ts_edges = sum(1 for e, ft in edge_faces.items() if sorted(ft) == ['S', 'T'])
ps_edges = sum(1 for e, ft in edge_faces.items() if sorted(ft) == ['P', 'S'])
bad_edges = sum(1 for e, ft in edge_faces.items() if sorted(ft) not in (['S','T'], ['P','S']))
print(f"\n邊類型:")
print(f"  三角形-正方形邊: {ts_edges} (預期 60)")
print(f"  五邊形-正方形邊: {ps_edges} (預期 60)")
print(f"  其他: {bad_edges}")

# ============ 5. 錨定著色 + 阻挫飽和 ============
color = {}
color[0] = 1  # 冷
q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in color:
            color[w] = 1 - color[u]
            q.append(w)

n_cold = sum(1 for c in color.values() if c == 1)
n_hot = sum(1 for c in color.values() if c == 0)
print(f"\n錨定著色: 冷 {n_cold} / 熱 {n_hot}")

# 每面阻挫邊數
tri_frust = []
pent_frust = []
sq_frust = []
total_frust = 0
for f in face_list:
    n = len(f)
    fr = 0
    for i in range(n):
        e = (f[i], f[(i+1) % n])
        if color[e[0]] == color[e[1]]:
            fr += 1
    total_frust += fr
    if n == 3:
        tri_frust.append(fr)
    elif n == 4:
        sq_frust.append(fr)
    elif n == 5:
        pent_frust.append(fr)

from collections import Counter
print(f"\n阻挫飽和分析 (每面同色邊數):")
print(f"  三角形面: {dict(Counter(tri_frust))}  (奇環 → ≥1, 飽和 = 1)")
print(f"  正方形面: {dict(Counter(sq_frust))}  (偶環 → 可 0, 完美著色 = 0)")
print(f"  五邊形面: {dict(Counter(pent_frust))}  (奇環 → ≥1, 飽和 = 1)")
print(f"  阻挫邊總數: {total_frust} = 20Δ×1 + 12⬠×1 {'✅ 完全飽和!' if total_frust == 32 else '❌'}")

# ============ 6. 判定 ============
print(f"\n判定:")
if chi == 2 and len(tri) == 20 and len(sq) == 30 and len(pent) == 12 and total_frust == 32:
    print(f"  ✅✅ Rhombicosidodecahedron 完全確認!")
    print(f"  20Δ + 30□ + 12⬠ = 62 面, χ = 2")
    print(f"  32 阻挫邊 = 20 (Δ) + 12 (⬠) = 奇面下界 完全飽和")
    print(f"  正方形完美 2-著色 (0 阻挫)")
    print(f"  → 錨定著色 = 基態 (Ground State Energy Bound)")
else:
    print(f"  ⚠️ 有偏差: χ={chi}, Δ={len(tri)}, □={len(sq)}, ⬠={len(pent)}, 阻挫={total_frust}")

# 儲存面資料
with open("data/faces.txt", "w") as f:
    f.write(f"# V={V} E={E} F={F} chi={chi}\n")
    f.write(f"# 三角形 {len(tri)}, 正方形 {len(sq)}, 五邊形 {len(pent)}\n")
    f.write(f"# 阻挫邊總數 {total_frust} (飽和)\n")
    f.write(f"# face_type vertices... color\n")
    for face in face_list:
        n = len(face)
        ft = 'T' if n == 3 else ('S' if n == 4 else 'P')
        cols = [color[x] for x in face]
        fr = sum(1 for i in range(n) if color[face[i]] == color[face[(i+1)%n]])
        f.write(f"{ft} {face} colors={cols} frust={fr}\n")
print(f"\n✅ 面資料已存: data/faces.txt")
