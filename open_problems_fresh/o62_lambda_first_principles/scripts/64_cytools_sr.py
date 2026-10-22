#!/usr/bin/env python3
"""
O62 十期 64: anomaly — cone face 結構最終測試
=============================================
hypothesis: anomaly pairs 有共同 simplex 但冇共同「edge 作為 cone face」
  即: edge (i,j) 存在 (喺 simplex 內) 但唔係任何 maximal cone 嘅 1-face?
  唔對 — simplex 嘅任何 subset 都係 face

最終方法: 直接睇 anomaly 對應嘅 κ_iij 同 κ_ijj 值!
  如果 anomaly 嘅 κ_iij = κ_ijj = 0 全部 → 就係「兩同零」SR
  但已知 (1,3): 8/6 唔係零...

等等 — 重新諗! κ_iij 嘅 i 同 j 係「index in kappa 36」,
但 point 36 存在! kappa 36 可能唔包含 point 36 嘅相交!

檢查: anomaly (1,3) 嘅 κ_113 = 8, κ_133 = 6 — 非零!
  咁點解 sage 列 SR?!
  
最終測試: cytools 直接計 SR ideal
"""
import sys, os, json
import numpy as np
from itertools import combinations

print("=" * 72)
print("O62 十期 64: cytools SR 對照")
print("=" * 72)

import cytools
from cytools import Polytope, config
config.enable_experimental_features()

canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
P = Polytope(canon)
tri = P.triangulate(backend="qhull")

# cytools 有冇 star / sr_ideal 相關?
print("[1] cytools Triangulation methods")
methods = [m for m in dir(tri) if not m.startswith('_')]
print(f"  {methods}")

# 試 sr_ideal / sr_generators?
for m in ["sr_ideal", "sr_generators", "stanley_reisner", "star", "faces"]:
    if hasattr(tri, m):
        print(f"  tri.{m} exists!")
        try:
            r = getattr(tri, m)()
            print(f"    -> {r}")
        except Exception as e:
            print(f"    error: {e}")

# cytools Polytope 有冇 faces?
print("\n[2] Polytope faces")
for m in ["faces", "facets", "triangulations"]:
    if hasattr(P, m):
        print(f"  P.{m} exists")

# ============ 用 STAR 計 SR ============
print("\n[3] 用 star 計 SR (star-based)")
# toric SR: x_i x_j = 0 如果 {i,j} 唔係任何 cone 嘅 face
# 即冇共同 maximal cone
simps = tri.simplices()
cones3 = set()
for s in simps:
    for f in combinations(s, 4):
        cones3.add(tuple(sorted(f)))
print(f"  maximal cones (4D): {len(cones3)}")

# pair 有共同 cone?
sr_cone = set()
for i in range(48):
    for j in range(i+1, 48):
        if not any(i in c and j in c for c in cones3):
            sr_cone.add((i, j))
print(f"  冇共同 cone pairs: {len(sr_cone)}")

# 同 sage 對照 (active only)
d = json.load(open("/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o53_cy3_reality/data/polytopes/cy36_98_sage_export.json"))
sr_sage = set(tuple(sorted(p)) for p in d["sr_ideal"])
sr_active = set((i,j) for (i,j) in sr_cone if i < 36 and j < 36)
print(f"  sage unique: {len(sr_sage)}")
print(f"  cone-based active: {len(sr_active)}")
print(f"  sage ∩ cone: {len(sr_sage & sr_active)}")
print(f"  sage − cone: {len(sr_sage - sr_active)}")
print(f"  cone − sage: {len(sr_active - sr_sage)}")

# ============ 總結 ============
print("\n" + "=" * 72)
print("十期 64 總結:")
print("=" * 72)
out = {
    "test": "O62 十期 64: cytools SR",
    "n_cones": len(cones3),
    "sr_cone": len(sr_cone),
    "sage_n": len(sr_sage),
    "inter": len(sr_sage & sr_active),
    "sage_only": len(sr_sage - sr_active),
    "cone_only": len(sr_active - sr_sage),
    "passed": 0, "failed": 0
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "64_cytools_sr.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("完成")
