#!/usr/bin/env python3
"""
O62 十期 63: anomaly 真特徵 — star-cone 結構
==============================================
anomaly: 有共同 simplex (star>0) 但有共同 edge 都列 SR

再試: anomaly pairs 嘅共同 simplex 係咪全部「同一類型」?
  或者: 佢哋嘅共同 simplex 數量 (edge star) 特別少?

對照: 正常 pairs vs anomaly 嘅 edge star 分佈
"""
import sys, os, json
import numpy as np
from itertools import combinations
from collections import Counter

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 十期 63: anomaly star 分佈")
print("=" * 72)

d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
simplices = d["simplices"]
sr_sage = d["sr_ideal"]
sr_set = set(tuple(sorted(p)) for p in sr_sage)

faces_1d = set()
for s in simplices:
    for e in combinations(s, 2):
        faces_1d.add(tuple(sorted(e)))
no_edge = set()
for i in range(36):
    for j in range(i+1, 36):
        if (i, j) not in faces_1d:
            no_edge.add((i, j))
anomaly = sorted((sr_set - no_edge) & set(combinations(range(36), 2)))

normal = []
for i in range(36):
    for j in range(i+1, 36):
        if (i, j) in faces_1d and (i, j) not in sr_set:
            normal.append((i, j))

def edge_star(i, j):
    return sum(1 for s in simplices if i in set(s) and j in set(s))

print(f"[1] edge star 分佈")
anom_star = Counter(edge_star(i, j) for (i, j) in anomaly)
norm_star = Counter(edge_star(i, j) for (i, j) in normal)
print(f"  anomaly edge star: {dict(sorted(anom_star.items()))}")
print(f"  normal edge star: {dict(sorted(norm_star.items()))}")
print(f"  anomaly mean: {np.mean([edge_star(i,j) for (i,j) in anomaly]):.1f}")
print(f"  normal mean: {np.mean([edge_star(i,j) for (i,j) in normal]):.1f}")

# ============ 1. 共同 simplex 嘅「類型」 ============
print("\n[2] 共同 simplex 內容分析")
for (i, j) in anomaly[:5]:
    common = [s for s in simplices if i in set(s) and j in set(s)]
    print(f"  ({i},{j}): {len(common)} simplices")
    for s in common:
        print(f"    {s}")

# ============ 2. 另一假設: anomaly = 高-star 點對 (star ≥ 20) ============
print("\n[3] anomaly 點嘅 star")
star = {}
for s in simplices:
    for v in s:
        star[v] = star.get(v, 0) + 1
anom_pts = set()
for (i, j) in anomaly:
    anom_pts.add(i); anom_pts.add(j)
print(f"  anomaly 點嘅 star: {[(p, star.get(p,0)) for p in sorted(anom_pts)]}")

# ============ 3. 總結 ============
print("\n" + "=" * 72)
print("十期 63 總結:")
print("=" * 72)
out = {
    "test": "O62 十期 63: star 分佈",
    "anom_star": dict(sorted(anom_star.items())),
    "norm_star": dict(sorted(norm_star.items())),
    "anom_mean": float(np.mean([edge_star(i,j) for (i,j) in anomaly])),
    "norm_mean": float(np.mean([edge_star(i,j) for (i,j) in normal])),
    "anom_pt_star": {str(p): star.get(p,0) for p in sorted(anom_pts)},
    "passed": 0, "failed": 0
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "63_star_dist.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("完成")
