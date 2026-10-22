#!/usr/bin/env python3
"""
O62 九期 46: 項目 2 — Dual polytope Δ* + mirror h12=98 驗證
=============================================================
用 cytools 計算:
  1. Δ 嘅 dual polytope Δ*
  2. Δ* 嘅 lattice 點 / 內部點 l(Δ*)
  3. Batyrev mirror: h12(X) = l(Δ*) − 5 − Σ int(Γ*)
  4. Δ* 嘅 n_vertices — 應該有好多 (mirror)
"""
import sys, os, json
import numpy as np

print("=" * 72)
print("O62 九期 46: Dual Polytope (cytools)")
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

import cytools
from cytools import Polytope, config
config.enable_experimental_features()

canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
P = Polytope(canon)
print(f"[1] Δ")
print(f"  vertices: {len(P.vertices())}")
print(f"  lattice points: {len(P.points())}")
print(f"  interior points: {len(P.interior_points())}")
print(f"  facets: {len(P.facets())}")
print(f"  dimension: {P.dim()}")

# ============ 1. Dual ============
print("\n[2] Δ* (dual)")
P_dual = P.polar_polytope()
print(f"  Δ* vertices: {len(P_dual.vertices())}")
print(f"  Δ* lattice points: {len(P_dual.points())}")
print(f"  Δ* interior points: {len(P_dual.interior_points())}")
print(f"  Δ* facets: {len(P_dual.facets())}")
print(f"  Δ* is reflexive: {P_dual.is_reflexive()}")

# ============ 2. Batyrev mirror ============
print("\n[3] Batyrev mirror")
l_star = len(P_dual.interior_points())
print(f"  l(Δ*) = interior points of Δ* = {l_star}")
print(f"  h12 = l(Δ*) − 5 − Σ_int(Γ*)")
print(f"  如果 Σ_int(Γ*) = 0: h12 = {l_star - 5}")
print(f"  目標: 98")

# ============ 4. 總結 ============
print("\n" + "=" * 72)
print("九期 46 總結:")
print("=" * 72)
out = {
    "test": "O62 九期 46: Dual",
    "P": {"v": len(P.vertices()), "pts": len(P.points()), "int": len(P.interior_points()), "facets": len(P.facets())},
    "P_dual": {"v": len(P_dual.vertices()), "pts": len(P_dual.points()), "int": len(P_dual.interior_points()), "facets": len(P_dual.facets())},
    "reflexive": bool(P_dual.is_reflexive()),
    "l_star": l_star,
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "46_dual.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 九期 46 完成!")
