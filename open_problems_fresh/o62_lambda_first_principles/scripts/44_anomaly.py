#!/usr/bin/env python3
"""
O62 九期 44: 25 anomaly — 邊界 edge 假設
=========================================
25 anomaly: 有共同 edge (1D face) 但 sage 列 SR

hypothesis: 呢啲 edge 喺 polytope 邊界 (boundary), 
  唔係 triangulation 嘅 interior edge
  → 對應 divisor pair 喺 boundary → 相交零 → SR

驗證: 檢查 anomaly edge 係咪喺 convex hull 表面
"""
import sys, os, json
import numpy as np
from itertools import combinations

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 九期 44: anomaly 邊界分析")
print("=" * 72)

d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"], dtype=float)
simplices = d["simplices"]
sr_sage = d["sr_ideal"]
sr_set = set(tuple(sorted(p)) for p in sr_sage)
vertices = np.array(d["vertices"], dtype=float)

# 搵 25 anomaly
faces_1d = set()
for s in simplices:
    for e in combinations(s, 2):
        faces_1d.add(tuple(sorted(e)))
anomaly = sorted(sr_set - set((i, j) for i, j in combinations(range(48), 2) if (i, j) in faces_1d))
print(f"[1] anomaly: {len(anomaly)}")
for (i, j) in anomaly:
    # 兩個點嘅座標
    pi, pj = pts[i], pts[j]
    print(f"  ({i:2d},{j:2d}): p{i}={pi}, p{j}={pj}")

# 檢查: 呢啲點係咪頂點或邊界點?
print("\n[2] anomaly 點嘅身份")
for idx in sorted(set(sum((list(a) for a in anomaly), []))):
    print(f"  point {idx:2d}: {pts[idx]}, 係頂點? {any(np.allclose(pts[idx], v) for v in vertices)}")

# ============ 邊界檢查 ============
print("\n[3] 邊界 face 檢查")
# 對每個 anomaly pair: edge (pi,pj) 喺邊界?
# 方法: 檢查 pi, pj 有冇共同「polytope facet」(由頂點定義)
from scipy.spatial import ConvexHull
# 4D 凸包好貴, 用另一方法:
# 檢查 pi 同 pj 係咪喺同一個「低維 face」

# 直接方法: 檢查 edge 中點係咪喺凸包表面
# 用 4D 凸包 (48 點)
try:
    hull = ConvexHull(pts)
    print(f"  4D convex hull: {len(hull.vertices)} 個 extreme points")
    # 邊界點 = extreme points
    extreme = set(hull.vertices)
    print(f"  extreme points: {sorted(extreme)}")
    # anomaly 點係咪 extreme?
    anom_pts = set()
    for (i, j) in anomaly:
        anom_pts.add(i); anom_pts.add(j)
    print(f"  anomaly 點中 extreme: {sorted(anom_pts & extreme)}")
    print(f"  anomaly 點中 interior: {sorted(anom_pts - extreme)}")
except Exception as e:
    print(f"  ConvexHull 4D fail: {e}")
    # fallback: 用 cytools
    import cytools
    from cytools import Polytope, config
    config.enable_experimental_features()
    canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
    P = Polytope(canon)
    print(f"  cytools polytope: {P.n_vertices()} vertices")

# ============ 總結 ============
print("\n" + "=" * 72)
print("九期 44 總結:")
print("=" * 72)
out = {
    "test": "O62 九期 44: anomaly boundary",
    "anomaly": [(i, j) for (i, j) in anomaly],
    "anom_points": sorted(anom_pts) if 'anom_pts' in dir() else [],
    "extreme": sorted(extreme) if 'extreme' in dir() else [],
    "n_anom": len(anomaly)
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "44_anomaly.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("完成 (見 data/44_anomaly.json)")
