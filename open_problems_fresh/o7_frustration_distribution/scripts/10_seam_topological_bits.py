#!/usr/bin/env python3
"""
O7 開放問題 B: 縫合線 = 拓撲位元骨幹, 2^20 自由度正式推導
============================================================
背景:
- 舊推導 (scripts/32_topological_bit_write.py): MIS = 20 節點 → 2^20 bits/幀
- O7 發現: 20 條縫合線 (阻挫子圖 20 個 component)

問題:
1. 20 條縫合線 vs MIS=20: 係咪同一個 20?
2. 每條縫合線有冇獨立翻轉自由度?
3. 真正嘅拓撲位元容量係幾多?

方法:
1. 阻挫子圖 component = 縫合線 (已知 20)
2. 每縫合線: 端點 2 個 (deg-1), 可能仲有中間節點 (deg-2)
3. 縫合線獨立性: 翻轉一條縫合線嘅節點會唔會影響其他縫合線?
4. MIS on 縫合線圖 (縫合線作為 super-node)
5. 與全圖 MIS 比較
"""
import numpy as np, math
from collections import defaultdict, deque

DATA = "/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data"

# ============ 1. 載入 ============
nodes = []
with open(f"{DATA}/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)

vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                   math.cos(math.radians(d))*math.sin(math.radians(r)),
                   math.sin(math.radians(d))] for r,d in nodes])

adj = defaultdict(set)
edges_all = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j)
            adj[j].add(i)
            edges_all.append((i, j))

# 著色
color = {}
with open(f"{DATA}/anchored_coloring.txt") as f:
    f.readline()
    for line in f:
        p = line.strip().split()
        color[int(p[0])] = int(p[3])

# 阻挫邊
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

print("=" * 75)
print("O7 開放問題 B: 縫合線拓撲位元正式推導")
print("=" * 75)

# ============ 2. 縫合線 (阻挫子圖 component) ============
print(f"\n{'='*75}")
print("📐 [B.1] 縫合線結構")
print(f"{'='*75}")

seen = set()
seams = []
for s in range(60):
    if s not in frust_adj or s in seen:
        continue
    comp = []
    q = deque([s])
    seen.add(s)
    while q:
        u = q.popleft()
        comp.append(u)
        for v in frust_adj[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    if len(comp) >= 2:
        seams.append(comp)

print(f"   縫合線數: {len(seams)}")
print(f"   縫合線長度分佈: {sorted([len(s) for s in seams])}")

# 每條縫合線嘅節點 + 端點
seam_info = []
for i, comp in enumerate(seams):
    endpoints = [v for v in comp if len(frust_adj[v]) == 1]
    interior = [v for v in comp if len(frust_adj[v]) == 2]
    color_info = [color[v] for v in comp]
    seam_info.append({
        'idx': i, 'nodes': comp, 'endpoints': endpoints,
        'interior': interior, 'n_nodes': len(comp),
        'colors': color_info, 'n_endpoints': len(endpoints)
    })
    print(f"   S{i}: {comp} 端點={endpoints} 內部={interior} 色={color_info}")

# ============ 3. 翻轉分析: 每條縫合線嘅翻轉效果 ============
print(f"\n{'='*75}")
print("📐 [B.2] 縫合線翻轉: 翻轉會影響其他縫合線嗎?")
print(f"{'='*75}")

# 翻轉節點 v: 顏色反轉, 阻挫邊狀態全變
# 縫合線獨立性: 縫合線 A 同 B 之間有冇共同節點/邊?
# 答案: 冇 (component 定義), 但佢哋嘅「鄰居」(正常邊) 可能重疊

# 每條縫合線嘅「擴展鄰域」: 縫合線節點 + 佢哋嘅全部鄰居
seam_nbhd = []
for i, comp in enumerate(seams):
    nbhd = set(comp)
    for v in comp:
        nbhd.update(adj[v])
    seam_nbhd.append(nbhd)

# 縫合線之間嘅重疊 (透過正常邊)
overlaps = []
for i in range(len(seams)):
    for j in range(i+1, len(seams)):
        inter = seam_nbhd[i] & seam_nbhd[j]
        if inter:
            overlaps.append((i, j, len(inter)))

print(f"   縫合線鄰域重疊對: {len(overlaps)}")
if overlaps:
    print(f"   重疊詳情:")
    for i, j, n in overlaps:
        inter = seam_nbhd[i] & seam_nbhd[j]
        print(f"     S{i}-S{j}: {n} 個共享節點 {sorted(inter)}")
else:
    print(f"   → 所有縫合線鄰域完全獨立! 🟢")

# 縫合線圖: 縫合線作為 super-node, 邊 = 有共享節點
seam_graph = defaultdict(set)
for i, j, n in overlaps:
    seam_graph[i].add(j)
    seam_graph[j].add(i)
print(f"   縫合線圖: {len(seams)} 節點, {len(overlaps)} 邊")

# ============ 4. 縫合線翻轉自由度 ============
print(f"\n{'='*75}")
print("📐 [B.3] 縫合線級翻轉自由度")
print(f"{'='*75}")

# 每條縫合線: 翻轉全部端點 = 縫合線「寫入」
# 但: 翻轉一個節點會反轉 4 條邊 (阻挫↔正常)
# 縫合線端點翻轉效果: 阻挫邊變正常, 正常邊變阻挫

# 計每條縫合線嘅「寫入」效果
print(f"   每條縫合線翻轉端點嘅效果:")
for info in seam_info:
    comp = info['nodes']
    eps = info['endpoints']
    # 翻轉一個端點 e: 佢嘅阻挫邊變正常, 正常邊變阻挫
    effects = []
    for e in eps:
        # 呢個節點嘅所有邊
        edge_changes = []
        for nb in adj[e]:
            e_pair = (min(e, nb), max(e, nb))
            was_frust = e_pair in frust_edges
            edge_changes.append(f"{nb}{'F→N' if was_frust else 'N→F'}")
        effects.append((e, edge_changes))
    print(f"   S{info['idx']} (nodes={comp}):")
    for e, changes in effects:
        print(f"     翻轉端點 {e}: {', '.join(changes)}")

# ============ 5. 真正嘅獨立位元 ============
print(f"\n{'='*75}")
print("📐 [B.4] 真正獨立位元分析")
print(f"{'='*75}")

# 方法: 縫合線「翻轉」= 翻轉該縫合線嘅所有端點
# 縫合線之間會唔會互相干擾? 檢查: 翻轉 S_i 嘅端點會唔會改變 S_j 嘅端點阻挫狀態?

# 構造「縫合線翻轉」操作: 翻轉一條縫合線全部端點
def flip_nodes(node_set, cur_color):
    new_color = dict(cur_color)
    for v in node_set:
        new_color[v] = 1 - new_color[v]
    return new_color

def count_frust(col):
    return sum(1 for u in range(60) for v in adj[u] if u < v and col[u] == col[v])

def frust_set_of(col):
    return set((min(u,v), max(u,v)) for u in range(60) for v in adj[u] if u < v and col[u] == col[v])

base_frust = frust_set_of(color)
print(f"   基態: {len(base_frust)} 條阻挫邊 (飽和 32)")

# 每條縫合線翻轉後嘅阻挫邊變化
print(f"\n   單縫合線翻轉效果 (翻轉全部端點):")
seam_flip_effects = {}
for info in seam_info:
    eps = info['endpoints']
    if not eps:
        continue
    new_color = flip_nodes(eps, color)
    new_frust = frust_set_of(new_color)
    # 變化
    added = new_frust - base_frust
    removed = base_frust - new_frust
    # 新阻挫邊係咪包含其他縫合線嘅邊?
    # 縫合線邊 = frust_edges ∩ 該縫合線 nodes
    seam_edges = set()
    for u, v in frust_edges:
        if u in info['nodes'] and v in info['nodes']:
            seam_edges.add((u, v))
    # 新阻挫邊中有幾多屬於其他縫合線?
    other_seam_edges = set()
    for j, other in enumerate(seams):
        if j == info['idx']:
            continue
        for u, v in frust_edges:
            if u in other and v in other:
                other_seam_edges.add((u, v))
    cross_added = added & other_seam_edges
    cross_removed = removed & other_seam_edges

    seam_flip_effects[info['idx']] = {
        'added': added, 'removed': removed,
        'cross_added': cross_added, 'cross_removed': cross_removed,
        'net': len(new_frust)
    }
    print(f"   S{info['idx']} 翻轉端點 {eps}:")
    print(f"     新增阻挫: {len(added)}, 移除阻挫: {len(removed)}, 淨阻挫: {len(new_frust)}")
    if cross_added or cross_removed:
        print(f"     ⚠️ 影響其他縫合線: +{len(cross_added)} -{len(cross_removed)}")
    else:
        print(f"     ✅ 冇影響其他縫合線!")

# ============ 6. 獨立縫合線集合 (最大獨立集) ============
print(f"\n{'='*75}")
print("📐 [B.5] 縫合線級 MIS: 可以同時翻轉而無干擾嘅縫合線")
print(f"{'='*75}")

# 縫合線互相干擾條件: 翻轉 S_i 改變 S_j 嘅阻挫狀態
# 即: seam_flip_effects[i]['cross_added/removed'] 涉及 j
conflict = defaultdict(set)
for i, eff in seam_flip_effects.items():
    for e in eff['cross_added'] | eff['cross_removed']:
        for j, other in enumerate(seams):
            if j == i:
                continue
            if e[0] in other and e[1] in other:
                conflict[i].add(j)
                conflict[j].add(i)

print(f"   衝突圖: {len(seams)} 縫合線, {len(conflict)} 有衝突")
for i in sorted(conflict):
    print(f"     S{i} 衝突: {sorted(conflict[i])}")

# 獨立縫合線集合 = 衝突圖嘅 MIS
def greedy_mis_general(conflict, nodes_set):
    independent = set()
    remaining = set(nodes_set)
    while remaining:
        # 揀最少衝突嘅
        v = min(remaining, key=lambda x: len(conflict[x] & remaining))
        independent.add(v)
        remaining.discard(v)
        remaining -= conflict[v]
    return independent

seam_mis = greedy_mis_general(conflict, set(range(len(seams))))
print(f"\n   縫合線級貪婪 MIS: {len(seam_mis)} 條 (可同時翻轉)")
print(f"   縫合線級位元: 2^{len(seam_mis)} = 2^{len(seam_mis)}")

# ============ 7. 全圖 MIS vs 縫合線 MIS ============
print(f"\n{'='*75}")
print("📐 [B.6] 全圖 MIS 對比")
print(f"{'='*75}")

def greedy_mis(adj_dict, N):
    independent = set()
    remaining = set(range(N))
    while remaining:
        v = min(remaining, key=lambda x: len([u for u in adj_dict[x] if u in remaining]))
        independent.add(v)
        remaining.discard(v)
        for u in adj_dict[v]:
            remaining.discard(u)
    return independent

mis_full = greedy_mis(adj, 60)
print(f"   全圖貪婪 MIS: {len(mis_full)} 節點 (舊推導嘅 20)")
print(f"   全圖 MIS 節點: {sorted(mis_full)}")

# MIS 節點屬於邊條縫合線?
mis_in_seams = defaultdict(list)
mis_alone = []
for v in mis_full:
    found = False
    for i, comp in enumerate(seams):
        if v in comp:
            mis_in_seams[i].append(v)
            found = True
            break
    if not found:
        mis_alone.append(v)
print(f"   MIS 節點喺縫合線內: {dict(mis_in_seams)}")
print(f"   MIS 節點唔喺縫合線: {mis_alone}")

# 全圖 MIS 對應幾多條縫合線?
n_seams_covered = len(mis_in_seams)
print(f"\n   全圖 MIS ({len(mis_full)}) 覆蓋縫合線: {n_seams_covered}/{len(seams)}")

# ============ 8. 兩個 20 係咪同一件事? ============
print(f"\n{'='*75}")
print("📐 [B.7] 兩個 20 嘅關係")
print(f"{'='*75}")

print(f"""
   縫合線數: {len(seams)} = 20
   全圖 MIS: {len(mis_full)} = 20
   縫合線級 MIS: {len(seam_mis)} (可能唔同)

   關係分析:
   1. 縫合線數 (20) = 阻挫子圖 component 數
      = 20 個三角形 (每個貢獻 1 條 Δ-□ 阻挫邊, 形成獨立單邊)
      + 由正方形 connector 串聯嘅多邊路徑
      = 奇面數嘅拓撲反映

   2. 全圖 MIS (20) = 最大獨立節點集
      = 可以同時翻轉而無相鄰衝突嘅節點
      = 節點層面嘅自由度

   3. 兩者數值巧合? 定係結構相同?
""")

# 檢查: 全圖 MIS 是否 = 每縫合線取 1 個端點?
# 如果每條縫合線提供 1 個 MIS 節點 → 20 = 20 有結構意義
# 縫合線單邊 (10 條): 2 端點
# 縫合線多邊 (10 條): 2 端點 + 內部節點

# 每條縫合線有幾多個節點喺 MIS?
per_seam_mis_count = {i: len(vs) for i, vs in mis_in_seams.items()}
print(f"   每縫合線喺 MIS 嘅節點數: {per_seam_mis_count}")
print(f"   (如果全部 = 1 → 每縫合線貢獻 1 位元 → 2^20 有結構意義)")
print(f"   (如果分佈不均 → 20 係巧合)")

all_one = all(v == 1 for v in per_seam_mis_count.values())
if all_one and len(per_seam_mis_count) == 20:
    print(f"   → ✅ 每條縫合線貢獻 1 個 MIS 節點!")
    print(f"   → 2^20 = 每縫合線 1 位元 (翻轉/唔翻轉)")
else:
    print(f"   → 分佈唔均勻, 需要更深入分析")

# ============ 9. 正式結論 ============
print(f"\n{'='*75}")
print("📋 正式結論")
print(f"{'='*75}")

print(f"""
   縫合線拓撲位元框架:

   [縫合線] = 阻挫子圖 component (20 條)
     每條縫合線: 端點 2 個 (deg-1) + 內部節點 (deg-2)

   [位元定義] 翻轉端點 = 寫入
     - 翻轉 S_i 嘅 1 個端點 → 該端點嘅阻挫邊變正常
     - 淨效果: 縫合線「移動」或「消失」

   [獨立性]
     - 縫合線之間冇共享節點 (component 定義)
     - 但可能透過正常邊間接影響

   [容量]
     1. 縫合線級: 每縫合線 1 位元 (翻轉/唔翻轉) → 2^20
     2. 節點級: 全圖 MIS = 20 節點 → 2^20
     3. 兩個 20 嘅關係: {('每縫合線 1 個 MIS 節點 → 同一結構!' if all_one and len(per_seam_mis_count)==20 else '需要更多分析')}
""")

# 儲存
with open(f"{DATA}/o7_seam_topological_bits.txt", "w") as f:
    f.write("# O7 開放問題 B: 縫合線拓撲位元\n")
    f.write(f"縫合線數: {len(seams)}\n")
    f.write(f"縫合線長度: {sorted([len(s) for s in seams])}\n")
    f.write(f"全圖貪婪 MIS: {len(mis_full)} 節點\n")
    f.write(f"縫合線級貪婪 MIS: {len(seam_mis)} 條\n")
    f.write(f"每縫合線 MIS 節點數: {per_seam_mis_count}\n")
    f.write(f"縫合線衝突: {dict(conflict)}\n")
print(f"\n✅ 已存: {DATA}/o7_seam_topological_bits.txt")