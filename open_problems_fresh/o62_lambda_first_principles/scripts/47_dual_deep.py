#!/usr/bin/env python3
"""
O62 九期 47: Dual 深入 — M:48 N:85 + mirror 驗證
==================================================
Δ: 6v/48pts/7facets, Δ*: 7v/85pts/6facets

M:48, N:85 = O58 嘅「Canonical (M:48, N:85)」!
驗證:
  1. 48 = Δ lattice points (M)
  2. 85 = Δ* lattice points (N)
  3. Batyrev: h11(X) 同 h12(X) 嘅正確公式 (用 faces)
  4. 7 facets ↔ 7 dual vertices 對應
"""
import sys, os, json
import numpy as np

print("=" * 72)
print("O62 九期 47: Dual 深入 M:48 N:85")
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
P_dual = P.polar_polytope()

print("[1] M:48, N:85 確認")
n_M = len(P.points())
n_N = len(P_dual.points())
print(f"  M = Δ 點數 = {n_M}")
print(f"  N = Δ* 點數 = {n_N}")
check("M = 48", n_M == 48, f"({n_M})")
check("N = 85", n_N == 85, f"({n_N})")

print("\n[2] Batyrev 正確公式")
# Batyrev: h11(X) = l(Δ) − 4 − Σ_int(Γ) + Σ_int(Θ)
# 其中 Θ = codim-2 faces 嘅內部點...
# 簡單版本 (favorable): h11 = l(Δ) − 4 − Σ int(Γ)
# l(Δ) = interior points 數 (polytope 內部, 唔喺任何 face)
l_delta = len(P.interior_points())
print(f"  l(Δ) = interior(Δ) = {l_delta}")
# 但 sage export: interior_mask 得 point 0 係 True!
# 即 l(Δ) = 1 (只有原點係「strict interior」)
# 咁 h11 = 1 − 4 − ... = 負? 唔啱!

# 正確: l(Δ) 定義係「polytope 內部 lattice 點」= 唔喺任何 facet 上
# cytools interior_points = 呢個? 得 1 個 → 原點 (0,0,0,0)
# 但 Batyrev 用嘅 l(Δ) 係「所有內部點」包括 faces 內部?

# 用 points_not_interior_to_facets?
pts_int = P.points_interior_to_facets()
pts_not_facet = P.points_not_interior_to_facets()
print(f"  points_interior_to_facets: {len(pts_int)}")
print(f"  points_not_interior_to_facets: {len(pts_not_facet)}")

# 標準 Batyrev 公式:
# h11(X) = l(Δ) − 4 − Σ_{faces Γ} l*(Γ) + Σ_{codim2 Θ} l*(Θ)
# 其中 l(Δ) = # interior lattice points of Δ
# 對 4D reflexive: h11 = l(Δ) − 5 + Σ l*(faces) − Σ l*(edges)
# 標準公式 (Batyrev 1994):
# h11 = l(Δ) − 5 + Σ_{θ ∈ faces(3)} l*(θ) − Σ_{θ ∈ faces(2)} l*(θ)
# h12 = l(Δ*) − 5 + Σ_{θ ∈ faces(3)} l*(θ*) − Σ_{θ ∈ faces(2)} l*(θ*)

# cytools 有 h11/h12 methods!
print(f"\n  cytools P.h11() = {P.h11()}")
print(f"  cytools P.h12() = {P.h12()}")
print(f"  cytools P_dual.h11() = {P_dual.h11()}")
print(f"  cytools P_dual.h12() = {P_dual.h12()}")
check("P.h11 = 36", P.h11() == 36, f"({P.h11()})")
check("P.h12 = 98", P.h12() == 98, f"({P.h12()})")
check("P_dual mirror: h11=98, h12=36", P_dual.h11() == 98 and P_dual.h12() == 36, f"({P_dual.h11()},{P_dual.h12()})")

print("\n[3] Facets 對應")
facets_P = P.facets()
facets_dual = P_dual.facets()
print(f"  Δ facets: {len(facets_P)}")
print(f"  Δ* facets: {len(facets_dual)}")
# PolytopeFace 有 points() method?
try:
    fp_pts = [len(f.points()) for f in facets_P]
    fd_pts = [len(f.points()) for f in facets_dual]
except Exception:
    fp_pts = [len(f.ambient_indices()) for f in facets_P]
    fd_pts = [len(f.ambient_indices()) for f in facets_dual]
print(f"  Δ facets 點數: {fp_pts}")
print(f"  Δ* facets 點數: {fd_pts}")

# ============ 4. 總結 ============
print("\n" + "=" * 72)
print("九期 47 總結:")
print("=" * 72)
out = {
    "test": "O62 九期 47: M48 N85",
    "M": n_M, "N": n_N,
    "h11": int(P.h11()), "h12": int(P.h12()),
    "h11_dual": int(P_dual.h11()), "h12_dual": int(P_dual.h12()),
    "l_delta": l_delta,
    "facets_P": [len(f) for f in facets_P] if False else fp_pts,
    "facets_dual": [len(f) for f in facets_dual] if False else fd_pts,
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "47_dual_deep.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 九期 47 完成!")
