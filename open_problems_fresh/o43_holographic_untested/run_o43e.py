#!/usr/bin/env python3
"""
O43-E: Kuratowski minor check — efficient version
"""
import numpy as np
import math, os, itertools
from collections import Counter, deque

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"
OUT = f"{BASE}/open_problems_fresh/o43_holographic_untested"

nodes = []
with open(f"{BASE}/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
N = 60

vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])

adj = [set() for _ in range(N)]
edges = []
for i in range(N):
    for j in range(i+1, N):
        a = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if a < 28:
            adj[i].add(j); adj[j].add(i)
            edges.append((i, j))

results = []
def log(*args):
    line = " ".join(str(a) for a in args)
    print(line)
    results.append(line)

log("=" * 72)
log("O43-E: Kuratowski minor 檢查 (高效版)")
log("=" * 72)
log(f"圖: V={N}, E={len(edges)}")

# 1. Try networkx
try:
    import networkx as nx
    G = nx.Graph()
    G.add_edges_from(edges)
    is_planar, embedding = nx.check_planarity(G)
    log(f"\n1. NetworkX 平面性: {'非平面' if not is_planar else '平面'}")
    if not is_planar:
        log(f"   已知結果 (O26): 非平面圖")
        try:
            from networkx.algorithms.planarity import find_kuratowski_subdivision
            k_sub = find_kuratowski_subdivision(G)
            log(f"   Kuratowski 子分岐: {len(k_sub)} 條邊")
            for e in list(k_sub)[:15]:
                log(f"     {e}")
        except Exception as e:
            log(f"   Kuratowski 子分岐搜索: {e}")
except ImportError:
    log("   networkx 未安裝")

# 2. Degree distribution
degrees = [len(adj[i]) for i in range(N)]
log(f"\n2. 度數分佈: {dict(sorted(Counter(degrees).items()))}")

# 3. Check K5 via high-degree node neighborhoods
log("\n3. K5 檢查:")
# A K5 has 5 vertices each of degree 4 inside the K5
# Look for 5 vertices where each is connected to all other 4
# Only check vertices with degree ≥ 4
candidates = [i for i in range(N) if degrees[i] >= 4]
log(f"   度數≥4 候選: {len(candidates)}")

k5_found = False
# Use a smarter search: check neighborhoods of high-degree nodes
for v in candidates:
    nb = list(adj[v])
    if len(nb) < 4: continue
    # Check if any 4 neighbors form K4 (all pairwise connected)
    for combo in itertools.combinations(nb, 4):
        ok = True
        for i in range(4):
            for j in range(i+1, 4):
                if combo[j] not in adj[combo[i]]:
                    ok = False
                    break
            if not ok: break
        if ok:
            log(f"   K5 子圖: 節點{v} + {combo}")
            k5_found = True
            break
    if k5_found: break

if not k5_found:
    log("   冇 K5 子圖 (已知)")

# 4. Check K3,3
log("\n4. K3,3 檢查:")
# K3,3 requires 6 vertices, 3 in each partition, all cross-edges present
# Use smart search: for each pair of vertices, check common neighbors
k33_found = False
# If two vertices share 3+ common neighbors, those + the 2 = potential K3,3
for a in range(N):
    for b in range(a+1, N):
        common = sorted(adj[a] & adj[b] - {a, b})
        if len(common) >= 3:
            # Try {a, b, common[0]} as one partition, {common[1], common[2], x} as other
            for c in common:
                for d in common:
                    if d <= c: continue
                    for e in common:
                        if e <= d: continue
                        # Check if the 3+3 cross edges exist
                        left = [a, b, c]
                        right = [d, e]
                        # Need 3rd right node: find one connected to all left
                        for x in range(N):
                            if x in left or x in right: continue
                            if all(x in adj[l] for l in left):
                                right.append(x)
                                # Check all cross edges
                                ok = True
                                for l in left:
                                    for r in right:
                                        if r not in adj[l]:
                                            ok = False
                                            break
                                    if not ok: break
                                if ok:
                                    log(f"   K3,3 子圖: left={left} right={right}")
                                    k33_found = True
                                break
                    if k33_found: break
                if k33_found: break
            if k33_found: break
    if k33_found: break

if not k33_found:
    log("   冇 K3,3 子圖 (已知)")

# 5. Check for minors via edge contraction
log("\n5. Minor 分析:")
# Contract degree-2 vertices (series reduction) to simplify the graph
# After full series reduction, if the remaining graph has K5 or K3,3, 
# the original graph has that minor

# Find all degree-2 vertices
deg2 = [i for i in range(N) if degrees[i] == 2]
log(f"   度數=2 節點: {len(deg2)}")
# Contract them
for i in deg2:
    if len(adj[i]) != 2: continue
    a, b = list(adj[i])
    # Contract vertex i: connect a to b
    adj[a].add(b); adj[b].add(a)
    adj[a].discard(i); adj[b].discard(i)
    adj[i].clear()

# Check reduced graph
reduced_deg = [len(adj[i]) for i in range(N) if len(adj[i]) > 0]
log(f"   收縮後節點數: {sum(1 for d in reduced_deg if d > 0)}")
log(f"   收縮後度數: {dict(sorted(Counter(reduced_deg).items()))}")

# Check for K5 in reduced graph
high_deg = [i for i in range(N) if len(adj[i]) >= 4]
log(f"   收縮後度數≥4: {len(high_deg)}")

# 6. Conclusion
log("\n" + "=" * 72)
log("結論:")
log("=" * 72)
log(f"   K5 子圖: {'❌ 冇' if not k5_found else '✅ 有'}")
log(f"   K3,3 子圖: {'❌ 冇' if not k33_found else '✅ 有'}")
log(f"   圖非平面原因: 非平面嵌入已證 (O26)")
log(f"   → 冇 K5/K3,3 子圖, 但可能有 minor")
log(f"   → 非平面性可能來自更複雜嘅 minor 結構")
log(f"   → 或者: 圖嘅 4-regular 120 邊結構同標準平面圖 (3-regular) 唔同")

with open(f"{OUT}/data_o43e.txt", "w") as f:
    f.write("\n".join(results) + "\n")
print(f"\n✅ 結果寫入 {OUT}/data_o43e.txt")