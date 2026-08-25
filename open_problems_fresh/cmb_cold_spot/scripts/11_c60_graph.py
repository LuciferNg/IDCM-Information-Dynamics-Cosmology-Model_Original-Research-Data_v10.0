#!/usr/bin/env python3
"""
Gemini 機制三驗證: 60 節點 = C60 截角二十面體圖?
====================================================
Gemini 建議: 冷熱符號由 C60 圖嘅幾何阻挫決定
- C60 = 截角二十面體 = 12 個五邊形 + 20 個六邊形
- 五邊形 = 奇數環 → 唔可以二分著色 → 必然有阻挫
- 阻挫缺陷線 = 「冷-冷」或「熱-熱」相鄰 = 可觀測預測!

關鍵數學事實: A₅ 群 (60 元素) 喺 C60 嘅 60 個頂點上係正則作用
(regular action, simply transitive) — 即係冷斑軌道 = C60 圖!
"""
import numpy as np
import math
from collections import defaultdict, deque

print("=" * 66)
print("60 節點圖結構驗證 (C60 截角二十面體)")
print("=" * 66)

# 載入節點
nodes = []
with open("data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))

N = len(nodes)
print(f"節點數: {N} (C60 應該 60)")

# 轉單位向量
vecs = []
for ra, dec in nodes:
    r, d = math.radians(ra), math.radians(dec)
    vecs.append(np.array([math.cos(d)*math.cos(r),
                          math.cos(d)*math.sin(r),
                          math.sin(d)]))

def ang_deg(v1, v2):
    dot = np.clip(np.dot(v1, v2), -1, 1)
    return math.degrees(math.acos(dot))

# ============ 1. 最近鄰距離 ============
print("\n[1] 兩兩角距離分佈")
dists = []
for i in range(N):
    for j in range(i+1, N):
        dists.append(ang_deg(vecs[i], vecs[j]))
dists = np.array(dists)
print(f"最小距離: {dists.min():.3f}°")
print(f"前 10 個最小: {np.sort(dists)[:10]}")

# C60 邊長: 五邊形邊同六邊形邊嘅角距離
# 如果係 C60, 最近鄰距離應該係單一值 (邊長)
# 用 DBSCAN-like: 最近鄰距離 = 最小距離 × (1+5%)
d_min = dists.min()
edge_thresh = d_min * 1.05

# ============ 2. 圖結構 ============
print(f"\n[2] 圖結構 (邊 = 角距離 < {edge_thresh:.3f}°)")
adj = defaultdict(set)
for i in range(N):
    for j in range(i+1, N):
        if ang_deg(vecs[i], vecs[j]) < edge_thresh:
            adj[i].add(j)
            adj[j].add(i)

degrees = {i: len(adj[i]) for i in range(N)}
deg_counts = defaultdict(int)
for d in degrees.values():
    deg_counts[d] += 1
print(f"度數分佈: {dict(deg_counts)}")
print(f"(C60 應該全部 degree=3)")

if len(deg_counts) == 1 and list(deg_counts.keys())[0] == 3:
    print("✅ 3-regular 圖! 符合 C60!")
else:
    print("⚠️ 唔係 3-regular, 檢查閾值")
    # 試更大閾值
    for mult in [1.1, 1.2, 1.3, 1.5]:
        th = d_min * mult
        adj2 = defaultdict(set)
        for i in range(N):
            for j in range(i+1, N):
                if ang_deg(vecs[i], vecs[j]) < th:
                    adj2[i].add(j)
                    adj2[j].add(i)
        degc = defaultdict(int)
        for i in range(N):
            degc[len(adj2[i])] += 1
        print(f"  閾值 {mult}: {dict(degc)}")

# ============ 3. 環結構: 五邊形/六邊形 ============
print(f"\n[3] 環結構檢查")
# 用 BFS 搵最短環 (girth)
def shortest_cycle(start):
    """BFS 搵包含 start 嘅最短環"""
    dist = {start: 0}
    parent = {start: None}
    q = deque([start])
    best_cycle = None
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                parent[v] = u
                q.append(v)
            elif parent[u] != v:
                # 搵到環 (u-v 係非樹邊)
                cycle_len = dist[u] + dist[v] + 1
                if best_cycle is None or cycle_len < best_cycle:
                    best_cycle = cycle_len
    return best_cycle

# C60 girth = 5 (最細係五邊形)
girth = min(shortest_cycle(i) for i in range(min(N, 20)))
print(f"Girth (最短環): {girth}")
print(f"(C60 嘅 girth 應該 = 5: 五邊形)")

# 搵所有 5-ring 同 6-ring (局部)
print(f"\n[4] 五邊形/六邊形計數")
def find_rings(n_ring):
    rings = []
    for start in range(N):
        # DFS 深度 n_ring 搵環
        path = [start]
        visited_path = {start}
        def dfs(u, depth):
            if depth == n_ring:
                if start in adj[u]:
                    rings.append(tuple(sorted(path)))
                return
            for v in adj[u]:
                if v not in visited_path:
                    visited_path.add(v)
                    path.append(v)
                    dfs(v, depth+1)
                    path.pop()
                    visited_path.discard(v)
        dfs(start, 1)
    return set(rings)

rings5 = find_rings(5)
rings6 = find_rings(6)
print(f"5-環 (五邊形): {len(rings5)} 個")
print(f"6-環 (六邊形): {len(rings6)} 個")
print(f"(C60: 12 個五邊形 + 20 個六邊形)")

# ============ 4. 二分性檢查 (二部圖?) ============
print(f"\n[5] 二分性檢查 (二部圖 = 完美冷熱交替)")
color = {}
bipartite = True
for start in range(N):
    if start in color:
        continue
    color[start] = 0
    q = deque([start])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in color:
                color[v] = 1 - color[u]
                q.append(v)
            elif color[v] == color[u]:
                bipartite = False
                print(f"  ❌ 衝突邊: 節點 {u}-{v} 同色 (阻挫!)")
                break
    if not bipartite:
        break

if bipartite:
    print("  ✅ 圖係二分圖 → 可以完美冷熱交替")
else:
    print(f"  ❌ 圖唔係二分圖 → 必然有幾何阻挫")
    print(f"  (因為有奇數環 = 五邊形)")

# ============ 5. 色數 ============
print(f"\n[6] 色數 (chromatic number)")
# 貪婪著色
remaining = set(range(N))
chromatic = 1
while remaining:
    # 搵最大獨立集 (貪婪)
    independent = set()
    available = set(remaining)
    while available:
        v = min(available, key=lambda x: len(adj[x] & available))
        independent.add(v)
        available -= adj[v]
        available.discard(v)
    remaining -= independent
    chromatic += 1
    if chromatic > 4:
        break
print(f"色數 ≥ {chromatic-1} (C60 色數 = 3)")

# ============ 6. 阻挫預測 ============
print(f"\n[7] 阻挫缺陷線預測")
# 如果冷熱係「盡量交替」, 阻挫發生喺五邊形
# 每個五邊形最少 1 條同色邊 → 12 個五邊形 → 最少 12 條缺陷邊?
print(f"12 個五邊形 × 最少 1 條同色邊 = 最少 12 條「冷-冷/熱-熱」邊")
print(f"呢啲邊就係投影縫合線 — CMB 上嘅異常帶!")
print(f"可證偽: 如果 60 節點嘅溫度 pattern 冇呢啲同色對, IDCM 錯")

# 將結果存檔
with open("data/c60_graph_analysis.txt", "w") as f:
    f.write(f"節點數: {N}\n")
    f.write(f"度數分佈: {dict(deg_counts)}\n")
    f.write(f"Girth: {girth}\n")
    f.write(f"五邊形: {len(rings5)}, 六邊形: {len(rings6)}\n")
    f.write(f"二分圖: {'是' if bipartite else '否 (有阻挫)'}\n")
    f.write(f"色數: ≥{chromatic-1}\n")
print(f"\n分析已存: data/c60_graph_analysis.txt")
