#!/usr/bin/env python3
"""
O137 Phase 5b: Δ* 點分類 — 44 個 facet-interior points ↔ K_Chain 44 sites?
============================================================================
Δ* 有 85 點: 1 origin + 84 boundary。
Batyrev: Σl*(facets_Δ*) = 85 - 5 - h21(mirror) = 85 - 5 - 36 = 44 = Nd ★

Hypothesis: Δ* 有 44 個「facet-strictly-interior」points ↔ K_Chain 44 sites。
方法: 每個 boundary point p, 判斷佢屬於邊個 facets, 睇下係咪
strictly interior to a facet (唔係 vertex, 唔係 edge-interior)。
"""
import json, numpy as np, itertools, math
from cytools import Polytope
from cytools.config import enable_experimental_features

enable_experimental_features()
BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
d = json.load(open(f'{BASE}/o53_cy3_reality/data/polytopes/cy36_98_sage_export.json'))
pts = np.array(d['points'])
p = Polytope(pts.tolist())
p_dual = p.dual()
pts_dual = np.array(p_dual.points())

print("=" * 76)
print("O137 Phase 5b: Δ* 點分類")
print("=" * 76)

# [1] vertices
try:
    verts = np.array(p_dual.vertices())
    print(f"Δ* vertices: {verts.shape[0]} 個")
    print(f"  {verts}")
except Exception as e:
    print(f"vertices err: {e}")
    verts = None

# [2] 分類 boundary points
is_origin = (pts_dual == 0).all(axis=1)
print(f"\norigin: {is_origin.sum()}, boundary: {(~is_origin).sum()}")

# [3] 每個 boundary point 嘅「facet membership」— 用 dual pairing
# point q ∈ Δ* 喺 facet θ_p (對應原始點 p) 上 ⟺ ⟨p, q⟩ = -1
# point q 係 facet-interior ⟺ 佢 belong 到至少一個 facet 且唔係任何 facet 嘅 vertex/edge
P = pts @ pts_dual.T  # 48×85

# 每個 boundary q: 佢喺邊啲 facets 上 (⟨p_i, q⟩ = -1 嘅 i)
facet_membership = {}
for j in range(pts_dual.shape[0]):
    if is_origin[j]:
        continue
    members = [i for i in range(48) if P[i, j] == -1]
    facet_membership[j] = members

# 統計
n_facet_pts = sum(1 for m in facet_membership.values() if len(m) >= 1)
print(f"\nboundary points 喺 ≥1 facet 上: {n_facet_pts}")

# facets per point 分佈
lens = [len(m) for m in facet_membership.values()]
from collections import Counter
print(f"facet membership 數分佈: {dict(Counter(lens))}")

# [4] 邊啲點係「strictly interior to a facet」?
# 一個 point 喺 facet 上 strictly interior ⟺ 佢只屬於 1 個 facet (唔喺 edges 上)
# 實際上: 4D polytope 嘅 facet 係 3D。point 喺 2 個 facets 上 = 喺 edge 上 (codim 2)
# point 喺 3 個 facets 上 = vertex (codim 3)
strict_facet = [j for j, m in facet_membership.items() if len(m) == 1]
print(f"\nstrictly-interior-to-facet points (membership=1): {len(strict_facet)}")
print(f"  → 預期 44 = Nd: {len(strict_facet) == 44}")

# [5] 如果係 44, print 佢哋嘅座標同對應 facet
if len(strict_facet) == 44:
    print(f"\n44 個 facet-interior points 同佢哋嘅 facet (原始點):")
    for j in strict_facet:
        m = facet_membership[j][0]
        print(f"  q={pts_dual[j]} ↔ facet of pt {m} (mode {m})")
else:
    print(f"\n實際 {len(strict_facet)} ≠ 44, 需要其他分類")

# [6] 備用: 2-facet points (membership=2 = edge-interior) 等
print(f"\nmembership=2 (edge-interior?): {lens.count(2)}")
print(f"membership=3 (vertex?): {lens.count(3)}")
print(f"membership≥4: {sum(1 for l in lens if l >= 4)}")

json.dump({'n_dual': pts_dual.shape[0],
           'strict_facet_count': len(strict_facet),
           'membership_dist': dict(Counter(lens))},
          open(f'{BASE}/o137_cy3_topological_resonance/data/mirror_facets.json', 'w'), indent=1)
print("\n已保存 data/mirror_facets.json")
