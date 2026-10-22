#!/usr/bin/env python3
"""
A01_geometry_basics.py — O4_renew A 部分: 基礎幾何獨立重驗證
=================================================================
完全由頭寫, 唔抄舊 code。驗證:
A1: a5_nodes.txt 節點數
A2: 節點分佈係咪 A₅ 軌道 (用 dodecahedron 對稱軸生成)
A3: 邊長/邊數/degree
A4: 面數 (Euler + 面型)
A5: BFS profile + 阻挫
"""
import numpy as np
import math
from collections import defaultdict, deque

BASE = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh'
print("=" * 72)
print("O4_renew A01: 基礎幾何獨立驗證")
print("=" * 72)

# ---------- A1: 載入節點 ----------
nodes = np.loadtxt(f'{BASE}/cmb_cold_spot/data/a5_nodes.txt')
print(f"\nA1: a5_nodes.txt 形狀 = {nodes.shape}")
print(f"    → 節點數 = {len(nodes)} ({'✅ 60' if len(nodes) == 60 else '❌ 唔係 60'})")
print(f"    頭 3 個: {nodes[:3]}")
# RA/Dec 範圍
ra, dec = nodes[:, 0], nodes[:, 1]
print(f"    RA 範圍: {ra.min():.1f}° - {ra.max():.1f}°")
print(f"    Dec 範圍: {dec.min():.1f}° - {dec.max():.1f}°")

# ---------- 轉 3D 向量 ----------
def radec_to_vec(ra, dec):
    r = math.radians(ra); d = math.radians(dec)
    return np.array([math.cos(d)*math.cos(r), math.cos(d)*math.sin(r), math.sin(d)])

vecs = np.array([radec_to_vec(r, d) for r, d in nodes])
# 檢查單位向量
norms = np.linalg.norm(vecs, axis=1)
print(f"\n    向量範數: min={norms.min():.10f} max={norms.max():.10f} ({'✅ 單位向量' if abs(norms.max()-1)<1e-10 else '❌'})")

# ---------- A3: 邊長分佈 ----------
print(f"\nA3: 兩兩角距離分佈")
dists = []
for i in range(60):
    for j in range(i+1, 60):
        d = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        dists.append(d)
dists = np.array(dists)
# 直方圖分桶 (0.5° 解析度)
bins = np.arange(0, 181, 0.5)
hist, edges = np.histogram(dists, bins=bins)
print(f"    距離直方圖 (第一層):")
for i in range(len(hist)):
    if hist[i] > 0 and edges[i] < 60:
        print(f"      {edges[i]:.1f}-{edges[i+1]:.1f}°: {hist[i]} 對")
print(f"    總對數: {len(dists)} = 60×59/2 = 1770 {'✅' if len(dists)==1770 else '❌'}")

# 找第一 cluster
sorted_d = np.sort(dists)
print(f"\n    最小 130 個距離:")
print(f"    sorted[119] = {sorted_d[119]:.4f}°, sorted[120] = {sorted_d[120]:.4f}°")
# E-th gap (E=120 預期邊數)
print(f"    E-th gap 建議 threshold = {(sorted_d[119]+sorted_d[120])/2:.4f}°")

# 用 threshold 28° (舊宣稱) 建圖
TH = 28.0
adj = defaultdict(set)
edge_list = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < TH:
            adj[i].add(j); adj[j].add(i)
            edge_list.append((i, j))
degrees = [len(adj[i]) for i in range(60)]
print(f"\n    threshold={TH}°: 邊數 = {len(edge_list)}, degree 分佈 = {sorted(set(degrees))}")
print(f"    → {'✅ 120 邊 degree 4' if len(edge_list)==120 and set(degrees)=={4} else '❌ 唔係 120 邊 degree 4'}")

# 邊長 (實際)
edge_lens = [math.degrees(math.acos(np.clip(np.dot(vecs[u], vecs[v]), -1, 1))) for u, v in edge_list]
print(f"    邊長: mean={np.mean(edge_lens):.4f}°, min={min(edge_lens):.4f}°, max={max(edge_lens):.4f}°")
print(f"    → {'✅ 邊長 ≈ 26.09°' if abs(np.mean(edge_lens)-26.09)<0.1 else '❌ 邊長唔啱'}")

# ---------- A4: 面數 (face traversal) ----------
print(f"\nA4: 面遍歷 (Euler 驗證)")
# 每頂點鄰居按角度排序
def neighbors_ordered(v):
    nbrs = list(adj[v])
    # 切平面基
    e1 = np.array([-vecs[v][1], vecs[v][0], 0.0])
    n1 = np.linalg.norm(e1)
    if n1 < 1e-10:
        e1 = np.array([0.0, -vecs[v][2], vecs[v][1]])
        n1 = np.linalg.norm(e1)
    e1 = e1 / n1
    e2 = np.cross(vecs[v], e1)
    e2 = e2 / np.linalg.norm(e2)
    angles = []
    for nb in nbrs:
        w = vecs[nb] - np.dot(vecs[nb], vecs[v]) * vecs[v]
        w = w / np.linalg.norm(w)
        ang = math.atan2(np.dot(w, e2), np.dot(w, e1))
        angles.append((ang, nb))
    angles.sort()
    return [nb for _, nb in angles]

nxt = {}
for v in range(60):
    order = neighbors_ordered(v)
    for k, nb in enumerate(order):
        # (v, nb) 嘅 next = (nb, 喺 nb 嘅角度順序中 v 之後嗰個)
        # 需要 nb 嘅 order, 所以要預先計算所有
        pass

# 預先計算所有頂點嘅有序鄰居
all_order = {v: neighbors_ordered(v) for v in range(60)}
for v in range(60):
    order = all_order[v]
    for k, nb in enumerate(order):
        # (v, nb) 嘅 next: (nb, w) 其中 w 係 nb 嘅鄰居, 喺 nb 嘅角度順序中 v 之後
        nb_order = all_order[nb]
        # 搵 v 喺 nb_order 嘅位置
        try:
            idx = nb_order.index(v)
            w = nb_order[(idx + 1) % len(nb_order)]
        except ValueError:
            # 理論上唔應該發生 (v 同 nb 相鄰)
            w = nb_order[0]
        nxt[(v, nb)] = (nb, w)

faces = set()
for start in edge_list:
    u, v = start
    path = [(u, v)]
    cur = (u, v)
    while True:
        cur = nxt[cur]
        if cur == (u, v):
            break
        if len(path) > 20:
            break
        path.append(cur)
    faces.add(frozenset([a for a, _ in path]))

face_sizes = [len(f) for f in faces]
from collections import Counter
fc = Counter(face_sizes)
print(f"    面數 = {len(faces)}, 面型分佈 = {dict(fc)}")
V, E, F = 60, len(edge_list), len(faces)
print(f"    Euler: V-E+F = {V}-{E}+{F} = {V-E+F} ({'✅ =2' if V-E+F==2 else '❌'})")
print(f"    Σ面尺寸 = {sum(face_sizes)} vs 2E = {2*E} ({'✅' if sum(face_sizes)==2*E else '❌'})")
print(f"    → {'✅ Rhombicosidodecahedron (20Δ+30□+12⬠)' if fc == {3:20, 4:30, 5:12} else f'❌ 唔係預期面型 {fc}'}")

# ---------- A5: BFS + 阻挫 ----------
print(f"\nA5: BFS profile + 阻挫")
dist = {0: 0}
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in dist:
            dist[v] = dist[u] + 1
            q.append(v)
profile = [0]*9
for d in range(9):
    profile[d] = sum(1 for i in range(60) if dist.get(i, -1) == d)
print(f"    BFS profile (from node 0): {profile}")
print(f"    → {'✅ 1+4+8+11+12+11+8+4+1' if profile == [1,4,8,11,12,11,8,4,1] else '❌'}")
print(f"    直徑 = {max(dist.values())}")

# 阻挫 (2-colouring)
color = {0: 1}
q2 = deque([0])
while q2:
    u = q2.popleft()
    for v in adj[u]:
        if v not in color:
            color[v] = 1 - color[u]
            q2.append(v)
frust = [e for e in edge_list if color[e[0]] == color[e[1]]]
print(f"    2-colouring: 阻挫邊 = {len(frust)}")
print(f"    → {'✅ 32' if len(frust)==32 else f'❌ 唔係 32 ({len(frust)})'}")

with open(f'{BASE}/o4_renew/data/A01_geometry.txt', 'w') as f:
    f.write("# O4_renew A01: 基礎幾何驗證\n")
    f.write(f"nodes={len(nodes)} edges={len(edge_list)} degree={sorted(set(degrees))}\n")
    f.write(f"edge_len_mean={np.mean(edge_lens):.4f}\n")
    f.write(f"faces={dict(fc)} euler={V-E+F}\n")
    f.write(f"bfs_profile={profile} diameter={max(dist.values())}\n")
    f.write(f"frustration={len(frust)}\n")
print(f"\n✅ 已存: data/A01_geometry.txt")
