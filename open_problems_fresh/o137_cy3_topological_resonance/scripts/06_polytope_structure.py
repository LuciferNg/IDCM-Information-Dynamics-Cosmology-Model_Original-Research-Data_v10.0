#!/usr/bin/env python3
"""
O137 Phase 2a: 分析 polytope triangulation 結構
=================================================
目標: 確定 4 個 boundary (apex) 點, 建立 toric adjacency 圖,
      為 cycle 長度推導做準備。

數據: cy36_98_sage_export.json
  - 48 點 (6 vertices, 42 interior)
  - 144 simplices (4D, 每個 5 點) = B×h11 = 4×36?
"""
import json, numpy as np
from collections import Counter

d = json.load(open('/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o53_cy3_reality/data/polytopes/cy36_98_sage_export.json'))

pts = np.array(d['points'])            # 48×4
sx = np.array(d['simplices'])          # 144×5
sr = np.array(d['sr_ideal'])           # 484×2
verts_coords = d['vertices']           # 6 vertices as coordinate arrays
interior = np.array(d['interior_mask'], dtype=bool)  # 48 bools
n = len(pts)

# vertices as indices: match coordinates
vert_idx = [int(np.where((pts == c).all(axis=1))[0][0]) for c in verts_coords]
verts = vert_idx

print("=" * 72)
print("O137 Phase 2a: Polytope Triangulation 結構分析")
print("=" * 72)

# [1] interior_mask
n_int = int(interior.sum())
print(f"\n[1] 點結構: {n} 點, {n_int} interior, {len(verts)} vertices")
print(f"    interior 點: {[i for i,v in enumerate(interior) if v]}")
print(f"    vertices indices: {verts}")

# [2] simplex 覆蓋度 (每個點喺幾多個 simplices 度出現)
freq = Counter()
for s in sx:
    for p in s:
        freq[p] += 1
print(f"\n[2] 點喺 simplices 嘅出現頻率:")
freq_sorted = sorted(freq.items(), key=lambda x: -x[1])
for idx, f in freq_sorted:
    is_v = "V" if idx in verts else " "
    print(f"    pt {idx:2d}{is_v}: {f:3d}  {'★' if f >= 36 else ''}")

# [3] 假設: 144 = 4 apex × 36 → apex 每個喺 36 個 simplices
# 檢查有冇點出現頻率 = 36
apex_candidates = [i for i, f in freq.items() if f == 36]
print(f"\n[3] 出現頻率 = 36 嘅點 (apex 候選): {apex_candidates}")
if len(apex_candidates) == 4:
    print("    ✓ 確認 4-apex star triangulation: 144 = 4×36 = B×h11")

# [4] 非 apex 點嘅數量 = 48 − 4 = 44 = Nd
non_apex = [i for i in range(n) if i not in apex_candidates]
print(f"\n[4] 非 apex 點: {len(non_apex)} = Nd = 44 ✓" if len(non_apex) == 44 else f"[4] 非 apex 點: {len(non_apex)}")
print(f"    非 apex indices: {non_apex}")

# [5] adjacency: 兩個點相鄰 ⟺ 共同 simplex
adj = np.zeros((n, n), dtype=int)
for s in sx:
    for a in s:
        for b in s:
            if a != b:
                adj[a, b] += 1
print(f"\n[5] adjacency (共同 simplex 數):")
print(f"    總邊數 (adj>0): {(adj > 0).sum() // 2}")
deg = (adj > 0).sum(axis=1)
for i in range(n):
    is_a = "A" if i in apex_candidates else " "
    print(f"    pt {i:2d}{is_a}: degree {deg[i]:2d}")

# [6] sr_ideal 檢查: 484 = 22² pairs
print(f"\n[6] sr_ideal: {len(sr)} pairs = 22² = {22*22} ✓" if len(sr) == 484 else f"[6] sr_ideal: {len(sr)}")
# sr pairs 有冇 apex 點?
sr_pts = set(sr.flatten())
print(f"    sr_ideal 涉及嘅點數: {len(sr_pts)}")
print(f"    sr 涉及 apex: {[p for p in sr_pts if p in apex_candidates]}")

# [7] 保存結果
np.save('/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o137_cy3_topological_resonance/data/adjacency.npy', adj)
json.dump({'apex': apex_candidates, 'non_apex': non_apex},
          open('/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o137_cy3_topological_resonance/data/polytope_structure.json', 'w'))
print("\n結果已保存 data/adjacency.npy + data/polytope_structure.json")
