#!/usr/bin/env python3
"""
O62 十期 56: 25 anomaly 深入 — edge 結構分析
=============================================
anomaly = 有共同 edge (1D face) 但列 SR

hypothesis: 呢啲 edge 存在 (喺某 simplex 內) 
  但唔喺任何「2D face (3點)」入面 → isolated edge
  或者: edge 只喺低維 face, 對應 divisor pair 喺 boundary

驗證:
  1. anomaly edge 係咪喺任何 2D face?
  2. anomaly edge 嘅 star (幾多 simplex 包含)?
  3. anomaly 對應嘅 κ 值?
"""
import sys, os, json
import numpy as np
from itertools import combinations

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 十期 56: 25 anomaly edge 結構")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
simplices = d["simplices"]
sr_sage = d["sr_ideal"]
sr_set = set(tuple(sorted(p)) for p in sr_sage)
pts = np.array(d["points"], dtype=float)
kappa36 = np.array(json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))["kappa"])[:36,:36,:36]

# faces
faces_1d = set()
faces_2d = set()
for s in simplices:
    for e in combinations(s, 2):
        faces_1d.add(tuple(sorted(e)))
    for t in combinations(s, 3):
        faces_2d.add(tuple(sorted(t)))

# no-edge pairs
no_edge = set()
for i in range(36):
    for j in range(i+1, 36):
        if (i, j) not in faces_1d:
            no_edge.add((i, j))
anomaly = sorted(sr_set - no_edge)
print(f"[1] anomaly: {len(anomaly)} 個")
print(f"  {anomaly}")

# ============ 1. Edge 喺 2D face? ============
print("\n[2] anomaly edge 喺 2D face?")
in_2d = 0
not_2d = []
for (i, j) in anomaly:
    # edge (i,j) 喺 2D face 如果 ∃k: (i,j,k) ∈ faces_2d
    has_2d = any(k != i and k != j and tuple(sorted((i, j, k))) in faces_2d for k in range(48))
    if has_2d:
        in_2d += 1
    else:
        not_2d.append((i, j))
print(f"  喺 2D face: {in_2d}")
print(f"  唔喺 2D face (isolated edge?): {len(not_2d)}")
if not_2d:
    print(f"    {not_2d}")

# ============ 2. Edge star ============
print("\n[3] anomaly edge 嘅 simplex 數 (star)")
edge_star = {}
for (i, j) in anomaly:
    n = sum(1 for s in simplices if i in set(s) and j in set(s))
    edge_star[(i, j)] = n
    print(f"  ({i:2d},{j:2d}): {n} simplices")

# ============ 3. κ 值 ============
print("\n[4] anomaly 對應 κ")
for (i, j) in anomaly:
    if i < 36 and j < 36:
        # κ_iij or κ_ijj (有兩同)
        k_ij = kappa36[i, i, j] if i < j else kappa36[j, j, i]
        print(f"  ({i:2d},{j:2d}): κ_iij = {k_ij}, κ_ijj = {kappa36[i,j,j] if j<36 else '?'}")

# ============ 4. 總結 ============
print("\n" + "=" * 72)
print("十期 56 總結:")
print("=" * 72)
out = {
    "test": "O62 十期 56: anomaly edge",
    "anomaly": anomaly,
    "in_2d": in_2d, "not_2d": not_2d,
    "edge_star": {f"({i},{j})": n for (i, j), n in edge_star.items()},
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "56_anomaly_edge.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十期 56 完成!")
