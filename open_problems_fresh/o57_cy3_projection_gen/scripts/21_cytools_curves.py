#!/usr/bin/env python3
"""
O57 三期 21: CYTools 真 Cycle Volumes（修正版）
=================================================
用正確 CYTools API:
  poly.triangulate() → FRST (reflexive default)
  tri.get_toric_variety() → ToricVariety
  tv.curves() → toric curves

目標:
  1. 攞到 155 個 toric curves (對應 adjacency?)
  2. 計 curves 嘅 volume (∫_C J)
  3. 檢查 volume 結構同 K_Chain 嘅關係
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O57 三期 21: CYTools 真 Cycle Volumes")
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
from cytools import Polytope

d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))

# ============ 1. Polytope + Triangulation ============
print("\n[1] Polytope + FRST")
poly = Polytope(d["vertices"])
print(f"  Polytope: dim={poly.dim()}, h11={poly.h11()}, h21={poly.h21()}")
check("h11 = 36", poly.h11() == 36)

tri = poly.triangulate()
print(f"  Triangulation: {type(tri).__name__}")
simps = tri.simplices()
print(f"  Simplices: {len(simps)}")
check("144 simplices", len(simps) == 144, f"({len(simps)})")

# ============ 2. Toric variety + curves ============
print("\n[2] Toric variety + curves")
tv = tri.get_toric_variety()
print(f"  ToricVariety: {type(tv).__name__}")

# curves: 用 curve_basis (2-dim cone generators)
curves = tv.curve_basis()
print(f"  Curve basis: {len(curves)}")
if len(curves) > 0:
    print(f"  頭 5 個 curves: {curves[:5]}")
    # 睇 curve 結構
    c0 = curves[0]
    print(f"  curve[0] type: {type(c0).__name__}")
check("32 curve basis", len(curves) == 32, f"({len(curves)})")

# ============ 3. Curve volumes ============
print("\n[3] Curve volumes")
# CYTools: 用 Kähler form J 計 volume
# volume(C) = ∫_C J
# 需要 Kähler 參數 (36 個 moduli)

# 標準做法: J = Σ t_i D_i (D_i = divisor)
# volume(C_j) = Σ t_i D_i·C_j = Σ t_i κ_ij
# κ_ij = D_i·C_j 係 curve-divisor intersection

# 我哋有 κ_ijk (36³) 從 O50:
# κ_ij = D_i·D_j·C? 唔, κ_ijk = D_i·D_j·D_k (三階)
# curve C_jk = D_j·D_k: volume = Σ_i t_i κ_ijk

# 用 O50 嘅 κ_ijk:
kappa_path = os.path.join(BASE, "open_problems_fresh", "o50_cy3_intersection", "data")
kappa_files = [f for f in os.listdir(kappa_path) if "kappa" in f.lower()]
print(f"  O50 kappa files: {kappa_files}")

# 載入 κ_ijk
kappa = None
for kf in kappa_files:
    try:
        kd = json.load(open(os.path.join(kappa_path, kf)))
        print(f"  {kf}: keys={list(kd.keys())[:5]}")
    except Exception as e:
        print(f"  {kf}: {e}")

# ============ 4. J* = I₃⊗J₁₂ 做 Kähler 參數 ============
print("\n[4] J* 做 Kähler 參數")
# O53: J* = I₃ ⊗ J₁₂ (3×12 block, 3 代等權)
# J* 係 36-dim 嘅 Kähler form
jstar_path = os.path.join(O53, "Jstar_36D.json")
if os.path.exists(jstar_path):
    jd = json.load(open(jstar_path))
    print(f"  Jstar keys: {list(jd.keys())}")
    if "Jstar_36D" in jd:
        Jstar = np.array(jd["Jstar_36D"])
        print(f"  Jstar shape: {Jstar.shape}")
        print(f"  Jstar norm: {np.linalg.norm(Jstar):.4f}")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("三期 21 總結:")
print("=" * 72)

results = {
    "test": "O57 三期 21: CYTools curves",
    "n_curves": len(curves),
    "simplices": len(simps),
    "h11": poly.h11(),
    "h21": poly.h21(),
    "passed": passed, "failed": failed
}
with open("data/21_cytools_curves.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 三期 21 完成!")
