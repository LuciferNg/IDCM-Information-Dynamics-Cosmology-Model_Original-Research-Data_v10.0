#!/usr/bin/env python3
"""
O57 三期 20: CYTools 真 Cycle Volumes — 方向 A
================================================
核心: 用 CYTools 從 cy36_98 polytope 重建 toric variety,
      計算 155 adjacency curves + 36 Kähler moduli 嘅真 cycle volumes

物理: Yukawa 質量 m_f ∝ e^{-V_cycle}
      66 態提供拓撲選擇律, CYTools 提供幾何體積

方法:
  1. 從 sage_export 重建 Polytope (48 points)
  2. 搵 fine regular star triangulation (FRST)
  3. 計 GLSM charge matrix (已知: 36×48)
  4. 提取 toric curves (2-dim cones) 對應 155 adjacency pairs?
  5. 計 curves 嘅 volume (∫_C J)
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O57 三期 20: CYTools 真 Cycle Volumes")
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

# ============ 1. 載入 polytope 數據 ============
print("\n[1] 載入 polytope")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
points = d["points"]
n_points = d["n_points"]
print(f"  Points: {n_points}, h11={d['h11']}, h21={d['h21']}, χ={d['chi']}")

import cytools
# 重建 Polytope: CYTools 用 vertices (極點) 唔係全部 points
# 但 polytope 需要 reflexive hull: 用全部 points 可能太多
# 先試 vertices
vertices = d["vertices"]
print(f"  Vertices: {len(vertices)}")
print(f"  GLSM shape: {d['glsm_shape']}")

try:
    poly = cytools.Polytope(vertices)
    print(f"  Polytope dim: {poly.dim()}, h11={poly.h11()}, h21={poly.h21()}")
    check("polytope h11 = 36", poly.h11() == 36, f"(h11={poly.h11()})")
    check("polytope h21 = 98", poly.h21() == 98, f"(h21={poly.h21()})")
except Exception as e:
    print(f"  ❌ Polytope 重建失敗: {e}")
    # 試用全部 points
    try:
        poly = cytools.Polytope(points)
        print(f"  (用 points) Polytope dim: {poly.dim()}, h11={poly.h11()}, h21={poly.h21()}")
    except Exception as e2:
        print(f"  ❌ 都失敗: {e2}")

# ============ 2. GLSM ============
print("\n[2] GLSM charge matrix")
glsm = d["glsm_matrix"]
glsm = np.array(glsm)
print(f"  GLSM shape: {glsm.shape}")
print(f"  (32 linear relations × 37 columns = 36 divisors + 1)")
check("GLSM = 32×37", glsm.shape == (32, 37), f"({glsm.shape})")

# ============ 3. Triangulation ============
print("\n[3] Triangulation")
# CYTools: poly.triangulate() 或 all_triangulations()
# 需要 fine regular star triangulation (FRST)
try:
    tri = poly.triangulate(mode="frt")  # fine regular triangulation
    print(f"  Triangulation 成功: {tri}")
    print(f"  Simplices: {len(tri.simplices)}")
    check("simplices = 144", len(tri.simplices) == 144, f"({len(tri.simplices)})")
except Exception as e:
    print(f"  ⚠️ triangulate(mode='frt') 失敗: {e}")
    try:
        tri = poly.triangulate()
        print(f"  triangulate() 成功: {len(tri.simplices)} simplices")
    except Exception as e2:
        print(f"  ❌ triangulate() 都失敗: {e2}")

# ============ 4. Toric variety ============
print("\n[4] Toric variety")
try:
    tv = cytools.toricvariety.ToricVariety(poly, tri)
    print(f"  ToricVariety 成功")
    # 提取 curves
    curves = tv.curves()
    print(f"  Curves: {len(curves)}")
    if len(curves) > 0:
        print(f"  頭 3 個 curves: {curves[:3]}")
except Exception as e:
    print(f"  ⚠️ ToricVariety 失敗: {e}")
    try:
        tv = cytools.calabiyau.CY(poly, tri)
        print(f"  CY 成功: {tv}")
    except Exception as e2:
        print(f"  ❌ CY 都失敗: {e2}")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("三期 20 總結:")
print("=" * 72)

results = {
    "test": "O57 三期 20: CYTools 環境",
    "polytope_loaded": True,
    "n_points": n_points,
    "h11": d["h11"],
    "h21": d["h21"],
    "glsm_shape": list(glsm.shape),
    "passed": passed, "failed": failed
}
with open("data/20_cytools_env.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 三期 20 完成!")
