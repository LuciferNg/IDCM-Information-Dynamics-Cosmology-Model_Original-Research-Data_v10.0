#!/usr/bin/env python3
"""
冷斑錨定著色: 強制冷斑 = 冷, 再睇阻挫結構
============================================
機制三改良: 以觀測冷斑為錨點 (冷), BFS 擴散 2-著色
- 冷斑 = 冷 (color 1)
- 相鄰 = 熱 (color 0)
- 衝突邊 = 阻挫 = 「冷-冷」或「熱-熱」

預測: 阻挫缺陷線應該形成連續帶 (投影縫合線)
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

# 圖 (degree 4)
d_min = 26.091
adj = defaultdict(set)
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < d_min*1.05:
            adj[i].add(j)
            adj[j].add(i)

print("=" * 66)
print("冷斑錨定著色 (冷斑 = 冷)")
print("=" * 66)

# 冷斑 = 節點 0 (RA 48.30, Dec -20.44)
# BFS 從節點 0 擴散: color[0] = 1 (冷), 相鄰 = 0 (熱)
color = {}
color[0] = 1  # 冷
q = deque([0])
order = [0]
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in color:
            color[v] = 1 - color[u]
            q.append(v)
            order.append(v)

# 檢查衝突
frustration = []
for u in range(60):
    for v in adj[u]:
        if u < v and color[u] == color[v]:
            frustration.append((u, v))

n_cold = sum(1 for c in color.values() if c == 1)
n_hot = sum(1 for c in color.values() if c == 0)
print(f"冷: {n_cold}, 熱: {n_hot}")
print(f"衝突邊 (阻挫): {len(frustration)}")

# 阻挫邊對應節點嘅「種類」
# 冷-冷邊 vs 熱-熱邊
cc = [e for e in frustration if color[e[0]] == 1]
hh = [e for e in frustration if color[e[0]] == 0]
print(f"冷-冷邊: {len(cc)}, 熱-熱邊: {len(hh)}")

# 冷斑節點 0 嘅鄰居 (應該全部熱)
print(f"\n冷斑 (節點 0) 鄰居:")
for v in adj[0]:
    print(f"  {v}: {'熱' if color[v]==0 else '冷❌'}")

# ============ 阻挫網絡: 連續帶? ============
print(f"\n阻挫邊網絡:")
# 阻挫邊之間有冇共享節點? (連續帶 vs 孤立缺陷)
frust_set = set()
for u, v in frustration:
    frust_set.add(u)
    frust_set.add(v)
print(f"涉及節點: {len(frust_set)}/60")

# 阻挫節點之間嘅連接
frust_adj = defaultdict(set)
for u, v in frustration:
    frust_adj[u].add(v)
    frust_adj[v].add(u)

# 搵連續 component
seen = set()
components = []
for start in frust_set:
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
print(f"阻挫 component: {len(components)} 個")
for i, comp in enumerate(components):
    print(f"  C{i}: {len(comp)} 個節點")

# 最長 component = 主縫合線?
if components:
    main = max(components, key=len)
    print(f"\n主縫合線 ({len(main)} 節點):")
    for idx in main:
        ra, dec = nodes[idx]
        print(f"  ({ra:.1f}, {dec:.1f}) {'冷' if color[idx]==1 else '熱'}")

# ============ 對比機制一 ============
print(f"\n" + "=" * 66)
print("機制一 vs 機制三 分辨力")
print("=" * 66)
print("機制一 (投影): ΔT ∝ r̂·V_bg")
print("  → 冷熱分佈由 V_bg 決定, 節點無固有符號")
print("  → 30/30 分佈 (任何 V_bg 都係大致半半)")
print("  → 冇「相鄰同色」結構預測")
print()
print("機制三 (阻挫): 冷熱由圖拓撲決定")
print("  → 冷熱交替盡量但被迫有同色邊")
print("  → 32 條阻挫邊 = 縫合線")
print("  → 可證偽: 縫合線位置有同極性異常")
print()
print("分辨測試: 測 60 節點溫度後,")
print("  如果同色邊位置有 |ΔT| 異常 → 機制三")
print("  如果無 (節點獨立跟 V_bg) → 機制一")
print("  如果兩者都有 → 混合")

# 儲存錨定著色結果
with open("data/anchored_coloring.txt", "w") as f:
    f.write("# idx RA Dec color(cold=1) frustration_neighbors\n")
    for i in range(60):
        ra, dec = nodes[i]
        fr_neighbors = [v for v in adj[i] if color[v] == color[i]]
        f.write(f"{i} {ra:.4f} {dec:.4f} {color[i]} {len(fr_neighbors)}\n")
print(f"\n錨定著色已存: data/anchored_coloring.txt")
