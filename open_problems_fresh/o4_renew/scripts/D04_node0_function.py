#!/usr/bin/env python3
"""
D04_node0_function.py — 冷斑節點 0 喺 A₅ 網絡嘅功能定位
=================================================================
分析 node 0 (冷斑) 喺 60 節點網絡嘅拓撲功能角色:
1. 度數/鄰居
2. 阻挫邊數 (k 值) + ΔE
3. 中心性 (betweenness, closeness, eigenvector)
4. BFS 層位置
5. 同 ΔE=0 節點關係
6. 喺「路由/通信」框架嘅角色
"""
import numpy as np
import math
from collections import defaultdict, deque
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as astro_u

BASE = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh'
print("=" * 72)
print("O4_renew D04: 冷斑節點 0 功能定位")
print("=" * 72)

# ---------- 圖 ----------
nodes = np.loadtxt(f'{BASE}/cmb_cold_spot/data/a5_nodes.txt')
def radec_to_vec(ra, dec):
    r = math.radians(ra); d = math.radians(dec)
    return np.array([math.cos(d)*math.cos(r), math.cos(d)*math.sin(r), math.sin(d)])
vecs = np.array([radec_to_vec(r, d) for r, d in nodes])

adj = defaultdict(set)
edges = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j); adj[j].add(i)
            edges.append((i, j))

# ---------- 1. 度數 + 鄰居 ----------
print(f"\n=== 1. node 0 鄰居 ===")
nbrs = sorted(adj[0])
print(f"    degree = {len(nbrs)} (全部節點都係 4)")
print(f"    鄰居: {nbrs}")
for nb in nbrs:
    ang = math.degrees(math.acos(np.clip(np.dot(vecs[0], vecs[nb]), -1, 1)))
    print(f"      node {nb}: 角距離 {ang:.4f}°, ICRS ({nodes[nb][0]:.2f}°, {nodes[nb][1]:.2f}°)")

# ---------- 2. 阻挫角色 ----------
print(f"\n=== 2. node 0 阻挫角色 ===")
# 2-colouring
color = {0: 1}
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in color:
            color[v] = 1 - color[u]
            q.append(v)
# k = 阻挫邊數
k0 = sum(1 for nb in nbrs if color[nb] == color[0])
print(f"    color = {color[0]} (1=冷色, 0=熱色)")
print(f"    阻挫邊 k = {k0} (4 條邊中)")
print(f"    阻挫邊: {[nb for nb in nbrs if color[nb]==color[0]]}")
print(f"    正常邊: {[nb for nb in nbrs if color[nb]!=color[0]]}")
# ΔE
dE = 4 - 2*k0
print(f"    ΔE = 4-2k = {dE} ({'零能量' if dE==0 else '要能量'})")

# ---------- 3. 中心性 ----------
print(f"\n=== 3. 中心性 ===")
# BFS 距離全部
all_dist = {}
for s in range(60):
    d = {s: 0}
    q = deque([s])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in d:
                d[v] = d[u] + 1
                q.append(v)
    all_dist[s] = d

# closeness
def closeness(s):
    total = sum(all_dist[s].values())
    return (60-1) / total
# betweenness (Brandes)
def betweenness():
    CB = np.zeros(60)
    for s in range(60):
        S = []
        P = defaultdict(list)
        sigma = np.zeros(60); sigma[s] = 1
        d_s = {s: 0}
        q = deque([s])
        while q:
            v = q.popleft()
            S.append(v)
            for w in adj[v]:
                if w not in d_s:
                    d_s[w] = d_s[v] + 1
                    q.append(w)
                if d_s[w] == d_s[v] + 1:
                    sigma[w] += sigma[v]
                    P[w].append(v)
        delta = np.zeros(60)
        while S:
            w = S.pop()
            for v in P[w]:
                delta[v] += sigma[v]/sigma[w] * (1 + delta[w])
            if w != s:
                CB[w] += delta[w]
    return CB / 2  # 無向圖

CB = betweenness()
cl = np.array([closeness(s) for s in range(60)])
# eigenvector centrality
A = np.zeros((60, 60))
for u, v in edges:
    A[u, v] = 1; A[v, u] = 1
w, V = np.linalg.eigh(A)
ev_centrality = np.abs(V[:, -1])  # 最大特徵值對應

print(f"    node 0: betweenness = {CB[0]:.4f}")
print(f"    node 0: closeness = {cl[0]:.4f}")
print(f"    node 0: eigenvector = {ev_centrality[0]:.4f}")
print(f"    全體 betweenness 範圍: {CB.min():.4f} - {CB.max():.4f}")
print(f"    全體 closeness 範圍: {cl.min():.4f} - {cl.max():.4f}")
print(f"    全體 eigenvector 範圍: {ev_centrality.min():.4f} - {ev_centrality.max():.4f}")
# rank
print(f"    node0 betweenness rank: {int(np.sum(CB > CB[0]))+1}/60")
print(f"    node0 closeness rank: {int(np.sum(cl > cl[0]))+1}/60")
print(f"    node0 eigenvector rank: {int(np.sum(ev_centrality > ev_centrality[0]))+1}/60")

# ---------- 4. BFS 層 ----------
print(f"\n=== 4. node 0 喺自己 BFS 嘅位置 ===")
print(f"    node 0 係 BFS root (d=0)")
# antipode
d0 = all_dist[0]
antipode = max(d0, key=d0.get)
print(f"    antipode = node {antipode}, 距離 {d0[antipode]} hops")

# ---------- 5. 同 ΔE=0 關係 ----------
print(f"\n=== 5. node 0 vs ΔE=0 節點 ===")
k_count = np.zeros(60, dtype=int)
for (u, v) in edges:
    if color[u] == color[v]:
        k_count[u] += 1; k_count[v] += 1
deltaE0 = np.where(k_count == 2)[0]
print(f"    ΔE=0 節點: {deltaE0}")
print(f"    node 0 係咪 ΔE=0? {'✅ 係' if k_count[0]==2 else '❌ 唔係 (k='+str(k_count[0])+')'}")
print(f"    node 0 嘅 k = {k_count[0]}")

# ---------- 6. 對跖點 ----------
print(f"\n=== 6. 對跖點 (antipode) ===")
print(f"    node {antipode} 係 node 0 嘅 antipode")
print(f"    BFS 距離 = {d0[antipode]} hops")
print(f"    k(node {antipode}) = {k_count[antipode]}")

# ---------- 7. 冷斑喺路由框架嘅角色 ----------
print(f"\n=== 7. 功能總結 ===")
print(f"    node 0 (冷斑):")
print(f"      - BFS root (anchor)")
print(f"      - degree 4, k={k_count[0]} 阻挫邊")
print(f"      - betweenness {CB[0]:.3f} (rank {int(np.sum(CB>CB[0]))+1}/60)")
print(f"      - closeness {cl[0]:.4f} (rank {int(np.sum(cl>cl[0]))+1}/60)")
print(f"      - eigenvector {ev_centrality[0]:.4f} (rank {int(np.sum(ev_centrality>ev_centrality[0]))+1}/60)")

with open(f'{BASE}/o4_renew/data/D04_node0_function.txt', 'w') as f:
    f.write("# O4_renew D04: node 0 功能定位\n")
    f.write(f"nbrs={nbrs} k={k_count[0]} color={color[0]}\n")
    f.write(f"betweenness={CB[0]:.4f} closeness={cl[0]:.4f} eigenvector={ev_centrality[0]:.4f}\n")
    f.write(f"antipode={antipode}\n")
print(f"\n✅ 已存: data/D04_node0_function.txt")
