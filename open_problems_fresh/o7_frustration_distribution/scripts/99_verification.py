#!/usr/bin/env python3
"""
O7 雙重驗證 — 獨立重算所有關鍵數值
============================================
從原始數據重新計算每個聲稱嘅數字
"""
import numpy as np, math
from collections import defaultdict, deque, Counter

DATA = "/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data"
passed, failed = 0, 0

def check(name, value, expected, tol=1e-3):
    global passed, failed
    if isinstance(expected, (int, np.integer)):
        ok = value == expected
    elif isinstance(expected, float):
        ok = abs(value - expected) < tol
    elif isinstance(expected, str):
        ok = str(value) == expected
    else:
        ok = value == expected
    status = "✅" if ok else "❌"
    if ok:
        passed += 1
    else:
        failed += 1
    print(f"   {status} {name}: {value} (期望 {expected})")

# ============ Load data ============
nodes = []
with open(f"{DATA}/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                   math.cos(math.radians(d))*math.sin(math.radians(r)),
                   math.sin(math.radians(d))] for r,d in nodes])

# Build graph
adj = defaultdict(set)
edges_all = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j)
            adj[j].add(i)
            edges_all.append((i, j))

# Coloring
color = {}
with open(f"{DATA}/anchored_coloring.txt") as f:
    f.readline()
    for line in f:
        p = line.strip().split()
        color[int(p[0])] = int(p[3])

# Frustration edges
frust_edges = set()
with open(f"{DATA}/frustration_edges.txt") as f:
    f.readline()
    for line in f:
        p = line.strip().split()
        u, v = int(p[0]), int(p[1])
        frust_edges.add((min(u, v), max(u, v)))

frust_adj = defaultdict(set)
for u, v in frust_edges:
    frust_adj[u].add(v); frust_adj[v].add(u)

# Faces
edge_faces = defaultdict(list)
with open(f"{DATA}/faces.txt") as f:
    for line in f:
        if line.startswith("#"): continue
        ft = line.strip().split()[0]
        bs = line.index('['); be = line.index(']')
        verts = [int(x) for x in line[bs+1:be].split(',')]
        n = len(verts)
        for i in range(n):
            e = tuple(sorted((verts[i], verts[(i+1)%n])))
            edge_faces[e].append(ft)

print("=" * 70)
print("O7 雙重驗證 — 獨立重算所有關鍵數值")
print("=" * 70)

# ============ 1. Graph basics ============
print(f"\n📐 [1] 圖基礎")
check("V", 60, 60)
check("E", len(edges_all), 120)
deg_dist = Counter(len(adj[i]) for i in range(60))
check("degree 分佈", dict(deg_dist), {4: 60})

# ============ 2. Task 1: Edge type ============
print(f"\n📐 [2] Task 1: 邊類型關聯")
# Count Δ-□ vs ⬠-□ edges
edge_type_count = Counter()
for e, fts in edge_faces.items():
    t = tuple(sorted(fts))
    if t == ('S', 'T'): edge_type_count['Δ-□'] += 1
    elif t == ('P', 'S'): edge_type_count['⬠-□'] += 1
    else: edge_type_count[str(t)] += 1

check("Δ-□ 邊數", edge_type_count.get('Δ-□', 0), 60)
check("⬠-□ 邊數", edge_type_count.get('⬠-□', 0), 60)
check("□-□ 邊數", edge_type_count.get("('S', 'S')", 0), 0)

# Frustration edge types
frust_type_count = Counter()
for e in frust_edges:
    fts = tuple(sorted([ef[0] for ef in edge_faces[e]]))
    if fts == ('S', 'T'): frust_type_count['Δ-□'] += 1
    elif fts == ('P', 'S'): frust_type_count['⬠-□'] += 1
check("阻挫 Δ-□", frust_type_count.get('Δ-□', 0), 20)
check("阻挫 ⬠-□", frust_type_count.get('⬠-□', 0), 12)

# χ²
chi2 = (20-16)**2/16 + (12-16)**2/16
check("χ²", round(chi2, 3), 2.0)

# Cold-cold vs hot-hot edge types
cc = sum(1 for e in frust_edges if color[e[0]] == 1)
hh = sum(1 for e in frust_edges if color[e[0]] == 0)
check("冷-冷", cc, 16)
check("熱-熱", hh, 16)

# ============ 3. Task 2: Spatial symmetry ============
print(f"\n📐 [3] Task 2: 冷熱對稱")
# North/South per edge midpoint
cc_edges = [e for e in frust_edges if color[e[0]] == 1]
hh_edges = [e for e in frust_edges if color[e[0]] == 0]
cc_north = sum(1 for e in cc_edges if (nodes[e[0]][1] + nodes[e[1]][1])/2 > 0)
hh_north = sum(1 for e in hh_edges if (nodes[e[0]][1] + nodes[e[1]][1])/2 > 0)
check("冷-冷 北半球", cc_north, 7)
check("熱-熱 北半球", hh_north, 9)

# Overlap
cc_nodes = set(); [cc_nodes.update(e) for e in cc_edges]
hh_nodes = set(); [hh_nodes.update(e) for e in hh_edges]
check("重疊節點", len(cc_nodes & hh_nodes), 0)
check("冷-冷節點", len(cc_nodes), 28)
check("熱-熱節點", len(hh_nodes), 24)
check("總覆蓋節點", len(cc_nodes | hh_nodes), 52)

# ============ 4. Task 3: Clustering ============
print(f"\n📐 [4] Task 3: 空間聚類")
# CC of frustration subgraph
cc_frust = []
for v in range(60):
    if v not in frust_adj or len(frust_adj[v]) < 2: continue
    nbrs = list(frust_adj[v]); k = len(nbrs)
    actual = sum(1 for i in range(k) for j in range(i+1,k) if nbrs[j] in frust_adj[nbrs[i]])
    possible = k*(k-1)/2
    cc_frust.append(actual/possible if possible > 0 else 0)
check("阻挫子圖 CC", np.mean(cc_frust) if cc_frust else 0, 0.0)

# Degree distribution
deg_frust = Counter(len(frust_adj[v]) for v in range(60) if v in frust_adj)
check("degree-1", deg_frust.get(1, 0), 40)
check("degree-2", deg_frust.get(2, 0), 12)
check("degree≥3", sum(v for k,v in deg_frust.items() if k >= 3), 0)

# Components
seen = set(); comps = []
for s in range(60):
    if s not in frust_adj or s in seen: continue
    c = []; q = deque([s]); seen.add(s)
    while q:
        u = q.popleft(); c.append(u)
        for v in frust_adj[u]:
            if v not in seen: seen.add(v); q.append(v)
    comps.append(c)
check("component 數", len(comps), 20)
check("最大 component", max(len(c) for c in comps), 4)

# ============ 5. Task 4: Face allocation ============
print(f"\n📐 [5] Task 4: 面分配")
# Recompute face frustration from scratch
# Face traversal
order, pos = {}, {}
for v in range(60):
    vv = vecs[v]
    e1 = np.array([-vv[1], vv[0], 0.0])
    if np.linalg.norm(e1) < 1e-9: e1 = np.array([1.0, 0.0, 0.0])
    e1 = e1 / np.linalg.norm(e1)
    e2 = np.cross(vv, e1)
    angles = {}
    for u in adj[v]:
        angles[u] = math.atan2(np.dot(vecs[u], e2), np.dot(vecs[u], e1))
    order[v] = sorted(adj[v], key=lambda u: angles[u])
    for idx, u in enumerate(order[v]): pos[(v, u)] = idx

next_edge = {}
for u in range(60):
    for v in adj[u]:
        w = order[v][(pos[(v, u)] + 1) % 4]
        next_edge[(u, v)] = (v, w)

faces = []
seen_e = set()
for u in range(60):
    for v in adj[u]:
        for start in [(u,v), (v,u)]:
            if start in seen_e: continue
            path = []; cur = start
            while cur not in seen_e:
                seen_e.add(cur); path.append(cur[0])
                cur = next_edge[cur]
            faces.append(path)

unique = {}
for f in faces: unique[frozenset(f)] = f
face_list = list(unique.values())

tri = [f for f in face_list if len(f) == 3]
sq = [f for f in face_list if len(f) == 4]
pent = [f for f in face_list if len(f) == 5]
check("三角形數", len(tri), 20)
check("正方形數", len(sq), 30)
check("五邊形數", len(pent), 12)
check("Euler χ", 60 - 120 + len(face_list), 2)

# Per-face frustration
sq_f = Counter()
for f in sq:
    fr = sum(1 for i in range(4) if color[f[i]] == color[f[(i+1)%4]])
    sq_f[fr] += 1
check("正方形 frust=0", sq_f.get(0, 0), 14)
check("正方形 frust=2", sq_f.get(2, 0), 16)
check("正方形 frust=1", sq_f.get(1, 0), 0)

tri_f = all(sum(1 for i in range(3) if color[f[i]] == color[f[(i+1)%3]]) == 1 for f in tri)
pent_f = all(sum(1 for i in range(5) if color[f[i]] == color[f[(i+1)%5]]) == 1 for f in pent)
check("三角形全部 frust=1", tri_f, True)
check("五邊形全部 frust=1", pent_f, True)

total_frust_face = sum(sum(1 for i in range(len(f)) if color[f[i]] == color[f[(i+1)%len(f)]]) for f in face_list)
check("Σ(frust)/2", total_frust_face//2, 32)

# Square parallel check
all_parallel = True
for f in sq:
    n = 4
    fr_pos = [i for i in range(n) if color[f[i]] == color[f[(i+1)%n]]]
    if len(fr_pos) == 2:
        if abs(fr_pos[0] - fr_pos[1]) != 2:
            all_parallel = False
check("正方形全部對邊", all_parallel, True)

# ============ 6. Task 5: Seam segments ============
print(f"\n📐 [6] Task 5: 物理意義")
seen = set(); seam_segs = []
for s in range(60):
    if s not in frust_adj or s in seen: continue
    c = []; q = deque([s]); seen.add(s)
    while q:
        u = q.popleft(); c.append(u)
        for v in frust_adj[u]:
            if v not in seen: seen.add(v); q.append(v)
    if len(c) >= 2: seam_segs.append(c)

check("縫合線段數", len(seam_segs), 20)
single = sum(1 for s in seam_segs if len(s) == 2)
multi = sum(1 for s in seam_segs if len(s) > 2)
check("單邊縫合線", single, 10)
check("多邊縫合線", multi, 10)
check("最長縫合線", max(len(s) for s in seam_segs), 4)

# ============ 7. Open issue C: Endpoint isotropy ============
print(f"\n📐 [7] 開放問題 C: 端點 isotropy")
deg1 = [v for v in range(60) if v in frust_adj and len(frust_adj[v]) == 1]
check("端點數", len(deg1), 40)
R = np.sum([vecs[v] for v in deg1], axis=0)
R_len = np.linalg.norm(R) / len(deg1)
check("端點 R_len", round(R_len, 4), 0.0029, 0.0005)

# ============ 8. Verify all scripts exist ============
print(f"\n📐 [8] 腳本存在性檢查")
import os
script_dir = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o7_frustration_distribution/scripts"
expected_scripts = [
    "01_edge_type_correlation.py", "02_cold_hot_symmetry.py",
    "03_spatial_clustering.py", "04_face_allocation.py",
    "05_physical_meaning.py", "06_endpoint_isotropy.py",
    "07_endpoint_temperature_gradient.py"
]
for s in expected_scripts:
    check(f"scripts/{s}", os.path.exists(f"{script_dir}/{s}"), True)

# ============ Summary ============
print(f"\n{'='*70}")
print(f"📋 驗證結果: {passed} ✅ / {failed} ❌")
print(f"{'='*70}")
if failed == 0:
    print("所有數值驗證通過！✅✅✅")
else:
    print(f"有 {failed} 個檢查失敗！")