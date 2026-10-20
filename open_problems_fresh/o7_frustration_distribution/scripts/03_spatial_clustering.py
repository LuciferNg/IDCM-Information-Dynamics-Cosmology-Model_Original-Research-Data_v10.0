#!/usr/bin/env python3
"""
O7 Task 3: 空間聚類 — 阻挫邊聚類係數 vs 隨機圖對照
====================================================================
方法:
1. 阻挫邊子圖嘅聚類係數 (global + local)
2. 阻挫邊子圖嘅 component 分析
3. 隨機對照 A: 隨機著色 10000 次 (保留圖結構, 隨機分配冷熱)
4. 隨機對照 B: 隨機選 32 條邊 (保留邊數, 隨機選)
5. 阻挫邊子圖嘅 degree 分佈 vs 隨機
"""
import numpy as np
import math
import random
from collections import defaultdict, Counter, deque

DATA = "/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data"
random.seed(42)

# ============ 1. 載入數據 ============
nodes = []
with open(f"{DATA}/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))

# 建圖
vecs = []
for ra, dec in nodes:
    r, d = math.radians(ra), math.radians(dec)
    vecs.append(np.array([math.cos(d)*math.cos(r),
                          math.cos(d)*math.sin(r),
                          math.sin(d)]))
vecs = np.array(vecs)

THRESHOLD = 28.0
adj = defaultdict(set)
edges_all = []
for i in range(60):
    for j in range(i+1, 60):
        dot = np.clip(np.dot(vecs[i], vecs[j]), -1, 1)
        if math.degrees(math.acos(dot)) < THRESHOLD:
            adj[i].add(j)
            adj[j].add(i)
            edges_all.append((i, j))

# 阻挫邊
frust_edges = set()
with open(f"{DATA}/frustration_edges.txt") as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split()
        u, v = int(parts[0]), int(parts[1])
        frust_edges.add((u, v) if u < v else (v, u))

# 著色
color = {}
with open(f"{DATA}/anchored_coloring.txt") as f:
    f.readline()
    for line in f:
        parts = line.strip().split()
        idx, c = int(parts[0]), int(parts[3])
        color[idx] = c

print("=" * 70)
print("O7 Task 3: 阻挫邊聚類分析")
print("=" * 70)
print(f"節點: 60, 邊: {len(edges_all)}, 阻挫邊: {len(frust_edges)}")

# ============ 2. 阻挫邊子圖 ============
# 子圖 = 只由阻挫邊構成嘅圖
frust_adj = defaultdict(set)
for u, v in frust_edges:
    frust_adj[u].add(v)
    frust_adj[v].add(u)

frust_nodes = set(frust_adj.keys())
print(f"\n阻挫邊涉及節點: {len(frust_nodes)}/60")

# 子圖 degree 分佈
frust_deg = {v: len(frust_adj[v]) for v in frust_nodes}
deg_counts = Counter(frust_deg.values())
print(f"阻挫子圖 degree 分佈: {dict(sorted(deg_counts.items()))}")
print(f"阻挫子圖 平均 degree: {np.mean(list(frust_deg.values())):.2f}")

# ============ 3. 聚類係數 (Clustering Coefficient) ============
print(f"\n{'='*70}")
print("📐 [3.1] 阻挫邊子圖聚類係數")
print(f"{'='*70}")

def clustering_coefficient(adj_dict, node_set):
    """局部聚類係數: 節點鄰居之間嘅實際邊數 / 可能邊數"""
    ccs = []
    for v in node_set:
        neighbors = list(adj_dict[v])
        k = len(neighbors)
        if k < 2:
            ccs.append(0.0)
            continue
        # 計鄰居之間嘅邊數
        actual = 0
        for i in range(k):
            for j in range(i+1, k):
                if neighbors[j] in adj_dict[neighbors[i]]:
                    actual += 1
        possible = k * (k - 1) / 2
        ccs.append(actual / possible)
    return ccs

# 阻挫子圖上嘅聚類
cc_frust = clustering_coefficient(frust_adj, frust_nodes)
cc_global = np.mean(cc_frust) if cc_frust else 0.0
print(f"   阻挫子圖局部聚類係數:")
for v in sorted(frust_nodes):
    cc_v = clustering_coefficient(frust_adj, {v})[0]
    if cc_v > 0:
        print(f"     節點 {v}: CC={cc_v:.4f} (deg={len(frust_adj[v])})")
print(f"   阻挫子圖 平均 CC = {cc_global:.4f}")

# 全圖聚類係數 (for reference)
cc_full = clustering_coefficient(adj, set(range(60)))
cc_full_global = np.mean(cc_full)
print(f"\n   全圖 (60節點, 120邊) 平均 CC = {cc_full_global:.4f}")

# ============ 4. Component 分析 ============
print(f"\n{'='*70}")
print("📐 [3.2] 阻挫邊 Component 結構")
print(f"{'='*70}")

seen = set()
components = []
for start in frust_nodes:
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

print(f"   Component 數: {len(components)}")
comp_sizes = sorted([len(c) for c in components], reverse=True)
print(f"   Component 大小: {comp_sizes}")
largest = max(components, key=len)
print(f"   最大 component: {len(largest)} 節點")
print(f"   最大 component 佔阻挫節點: {len(largest)/len(frust_nodes)*100:.1f}%")
print(f"   最大 component 佔全圖: {len(largest)/60*100:.1f}%")

# 每 component 嘅冷-冷 / 熱-熱 組成
for i, comp in enumerate(components):
    cold_ct = sum(1 for v in comp if color[v] == 1)
    hot_ct = sum(1 for v in comp if color[v] == 0)
    print(f"   C{i}: {len(comp)} 節點 (冷={cold_ct}, 熱={hot_ct})")

# 阻挫邊嘅連通性: 阻挫子圖係咪 bipartite?
frust_color = {}
is_bipartite = True
for start in frust_nodes:
    if start in frust_color:
        continue
    frust_color[start] = 0
    q = deque([start])
    while q:
        u = q.popleft()
        for v in frust_adj[u]:
            if v not in frust_color:
                frust_color[v] = 1 - frust_color[u]
                q.append(v)
            elif frust_color[v] == frust_color[u]:
                is_bipartite = False
print(f"\n   阻挫子圖係二分圖: {'是 🟢' if is_bipartite else '否 🟡'}")

# ============ 5. 隨機對照 A: 隨機著色 ============
print(f"\n{'='*70}")
print("📐 [3.3] 隨機對照 A: 隨機著色 (保留圖結構)")
print(f"{'='*70}")

n_trials = 10000
rng = np.random.RandomState(42)

# 隨機著色: 隨機分配 30 冷 / 30 熱
results_randcolor = []
for trial in range(n_trials):
    # 隨機排列冷熱標籤
    perm_colors = np.zeros(60, dtype=int)
    perm_colors[rng.choice(60, 30, replace=False)] = 1
    perm_color = {i: perm_colors[i] for i in range(60)}

    # 計阻挫邊
    rand_frust = set()
    for u, v in edges_all:
        if perm_color[u] == perm_color[v]:
            rand_frust.add((u, v))

    # 阻挫子圖
    rand_frust_adj = defaultdict(set)
    for u, v in rand_frust:
        rand_frust_adj[u].add(v)
        rand_frust_adj[v].add(u)

    rand_frust_nodes = set(rand_frust_adj.keys())

    # 聚類係數
    if len(rand_frust_nodes) >= 3:
        ccs = clustering_coefficient(rand_frust_adj, rand_frust_nodes)
        mean_cc = np.mean(ccs)
    else:
        mean_cc = 0.0

    # Component 數
    seen_r = set()
    comps_r = 0
    for start in rand_frust_nodes:
        if start in seen_r:
            continue
        comps_r += 1
        q = deque([start])
        seen_r.add(start)
        while q:
            u = q.popleft()
            for v in rand_frust_adj[u]:
                if v not in seen_r:
                    seen_r.add(v)
                    q.append(v)

    # 最大 component
    max_comp = 0
    seen_r2 = set()
    for start in rand_frust_nodes:
        if start in seen_r2:
            continue
        comp = []
        q = deque([start])
        seen_r2.add(start)
        while q:
            u = q.popleft()
            comp.append(u)
            for v in rand_frust_adj[u]:
                if v not in seen_r2:
                    seen_r2.add(v)
                    q.append(v)
        max_comp = max(max_comp, len(comp))

    results_randcolor.append({
        'n_frust': len(rand_frust),
        'n_nodes': len(rand_frust_nodes),
        'cc': mean_cc,
        'n_comp': comps_r,
        'max_comp': max_comp
    })

# 分析隨機結果
cc_rand = [r['cc'] for r in results_randcolor]
ncomp_rand = [r['n_comp'] for r in results_randcolor]
maxcomp_rand = [r['max_comp'] for r in results_randcolor]
nfrust_rand = [r['n_frust'] for r in results_randcolor]

print(f"   隨機著色 {n_trials} 次:")
print(f"   阻挫邊數: 平均 {np.mean(nfrust_rand):.1f} ± {np.std(nfrust_rand):.1f} (範圍 {min(nfrust_rand)}-{max(nfrust_rand)})")
print(f"   阻挫節點: 平均 {np.mean([r['n_nodes'] for r in results_randcolor]):.1f}")
print(f"   平均 CC:   {np.mean(cc_rand):.4f} ± {np.std(cc_rand):.4f}")
print(f"   Component 數: 平均 {np.mean(ncomp_rand):.1f} ± {np.std(ncomp_rand):.1f}")
print(f"   最大 Component: 平均 {np.mean(maxcomp_rand):.1f} ± {np.std(maxcomp_rand):.1f}")

# 與真實值比較
cc_pctile = sum(1 for r in cc_rand if r <= cc_global) / n_trials * 100
ncomp_pctile = sum(1 for r in ncomp_rand if r <= len(components)) / n_trials * 100
maxcomp_pctile = sum(1 for r in maxcomp_rand if r <= len(largest)) / n_trials * 100

print(f"\n   真實阻挫邊聚類 vs 隨機著色:")
print(f"   真實 CC         = {cc_global:.4f}  (百分位 {cc_pctile:.1f}% {'🟡聚類' if cc_pctile>95 else '🟢隨機'})")
print(f"   真實 Component  = {len(components)}  (百分位 {ncomp_pctile:.1f}% {'🟡多' if ncomp_pctile>95 else '🟢正常'})")
print(f"   真實最大 Comp   = {len(largest)}  (百分位 {maxcomp_pctile:.1f}% {'🟡大' if maxcomp_pctile>95 else '🟢正常'})")

# ============ 6. 隨機對照 B: 隨機選邊 ============
print(f"\n{'='*70}")
print("📐 [3.4] 隨機對照 B: 隨機選 32 條邊 (保留邊數)")
print(f"{'='*70}")

results_randedge = []
for trial in range(n_trials):
    rand_edges = set(rng.choice(len(edges_all), 32, replace=False))
    rand_edge_set = {edges_all[i] for i in rand_edges}

    rand_frust_adj = defaultdict(set)
    for u, v in rand_edge_set:
        rand_frust_adj[u].add(v)
        rand_frust_adj[v].add(u)

    rand_frust_nodes = set(rand_frust_adj.keys())

    if len(rand_frust_nodes) >= 3:
        ccs = clustering_coefficient(rand_frust_adj, rand_frust_nodes)
        mean_cc = np.mean(ccs)
    else:
        mean_cc = 0.0

    # Component
    seen_r = set()
    comps_r = 0
    max_comp = 0
    for start in rand_frust_nodes:
        if start in seen_r:
            continue
        comps_r += 1
        comp = []
        q = deque([start])
        seen_r.add(start)
        while q:
            u = q.popleft()
            comp.append(u)
            for v in rand_frust_adj[u]:
                if v not in seen_r:
                    seen_r.add(v)
                    q.append(v)
        max_comp = max(max_comp, len(comp))

    results_randedge.append({
        'cc': mean_cc,
        'n_comp': comps_r,
        'max_comp': max_comp,
        'n_nodes': len(rand_frust_nodes)
    })

cc_rande = [r['cc'] for r in results_randedge]
ncomp_rande = [r['n_comp'] for r in results_randedge]
maxcomp_rande = [r['max_comp'] for r in results_randedge]
nodes_rande = [r['n_nodes'] for r in results_randedge]

print(f"   隨機選邊 {n_trials} 次:")
print(f"   平均節點: {np.mean(nodes_rande):.1f} ± {np.std(nodes_rande):.1f}")
print(f"   平均 CC:   {np.mean(cc_rande):.4f} ± {np.std(cc_rande):.4f}")
print(f"   Component 數: 平均 {np.mean(ncomp_rande):.1f} ± {np.std(ncomp_rande):.1f}")
print(f"   最大 Component: 平均 {np.mean(maxcomp_rande):.1f} ± {np.std(maxcomp_rande):.1f}")

cc_pctile_e = sum(1 for r in cc_rande if r <= cc_global) / n_trials * 100
ncomp_pctile_e = sum(1 for r in ncomp_rande if r <= len(components)) / n_trials * 100
maxcomp_pctile_e = sum(1 for r in maxcomp_rande if r <= len(largest)) / n_trials * 100

print(f"\n   真實阻挫邊 vs 隨機選邊:")
print(f"   真實 CC         = {cc_global:.4f}  (百分位 {cc_pctile_e:.1f}% {'🟡聚類' if cc_pctile_e>95 else '🟢隨機'})")
print(f"   真實 Component  = {len(components)}  (百分位 {ncomp_pctile_e:.1f}% {'🟡多' if ncomp_pctile_e>95 else '🟢正常'})")
print(f"   真實最大 Comp   = {len(largest)}  (百分位 {maxcomp_pctile_e:.1f}% {'🟡大' if maxcomp_pctile_e>95 else '🟢正常'})")

# ============ 7. 阻挫邊嘅「邊聚類」= 三角形閉合 ============
print(f"\n{'='*70}")
print("📐 [3.5] 阻挫邊三角形閉合 (transitivity)")
print(f"{'='*70}")

# 三角形: 3 條邊全部係阻挫邊
triangles = []
for u in range(60):
    for v in frust_adj[u]:
        if v <= u:
            continue
        for w in frust_adj[u]:
            if w <= v:
                continue
            if w in frust_adj[v]:
                triangles.append((u, v, w))

print(f"   阻挫邊三角形 (全阻挫3-cycle): {len(triangles)}")

# 三角形: 2 條阻挫邊 + 1 條正常邊
tri_2frust = []
for u in range(60):
    for v in frust_adj[u]:
        if v <= u:
            continue
        for w in adj[u] - frust_adj[u]:
            if w in frust_adj[v] or w in adj[v] - frust_adj[v]:
                tri_2frust.append((u, v, w))
# 粗略計數
tri_2frust_count = 0
for u in range(60):
    for v in frust_adj[u]:
        if v <= u:
            continue
        for w in adj[u]:
            if w <= u or w == v:
                continue
            if w in frust_adj[v]:
                # 全部 3 條邊: u-v (frust), u-w (?), v-w (?)
                e_uw = (u, w) if u < w else (w, u)
                e_vw = (v, w) if v < w else (w, v)
                n_frust = 1 + (1 if e_uw in frust_edges else 0) + (1 if e_vw in frust_edges else 0)
                if n_frust == 2 and (e_uw not in frust_edges or e_vw not in frust_edges):
                    tri_2frust_count += 1

print(f"   含 2 條阻挫邊嘅三角形: {tri_2frust_count}")

# 隨機對照: 三角形中阻挫邊數
print(f"\n   隨機對照 (隨機選 32 邊, 10000 次, 三角形中阻挫邊數):")
rand_tri_frust = []
for trial in range(n_trials):
    rand_edges = set(rng.choice(len(edges_all), 32, replace=False))
    rand_edge_set = {edges_all[i] for i in rand_edges}
    # 全阻挫三角形
    n_tri = 0
    for u, v, w in triangles:  # 用全圖三角形
        e1 = (u, v) if u < v else (v, u)
        e2 = (u, w) if u < w else (w, u)
        e3 = (v, w) if v < w else (w, v)
        if e1 in rand_edge_set and e2 in rand_edge_set and e3 in rand_edge_set:
            n_tri += 1
    rand_tri_frust.append(n_tri)

print(f"   隨機全阻挫三角形: 平均 {np.mean(rand_tri_frust):.3f} ± {np.std(rand_tri_frust):.3f}")
print(f"   真實全阻挫三角形: {len(triangles)}")
tri_p = sum(1 for r in rand_tri_frust if r >= len(triangles)) / n_trials
print(f"   百分位: {tri_p*100:.1f}% {'🟡聚類' if tri_p<0.05 else '🟢隨機'}")

# ============ 8. 總結 ============
print(f"\n{'='*70}")
print("📋 總結")
print(f"{'='*70}")
print(f"   阻挫子圖: {len(frust_nodes)} 節點, {len(frust_edges)} 邊")
print(f"   阻挫子圖 degree: {dict(sorted(deg_counts.items()))}")
print(f"   阻挫子圖平均 CC: {cc_global:.4f}  (隨機著色: {np.mean(cc_rand):.4f} ± {np.std(cc_rand):.4f})")
print(f"   阻挫子圖 CC 百分位 (隨機著色): {cc_pctile:.1f}%")
print(f"   阻挫子圖 CC 百分位 (隨機選邊): {cc_pctile_e:.1f}%")
print(f"   阻挫子圖 Component: {len(components)} 個")
print(f"   阻挫子圖最大 Component: {len(largest)} 節點 ({len(largest)/len(frust_nodes)*100:.1f}% 阻挫節點)")
print(f"   全阻挫三角形: {len(triangles)} 個")
print(f"   二分圖: {'✅' if is_bipartite else '❌'}")