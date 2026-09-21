#!/usr/bin/env python3
"""
O57 三期 22: CYTools Curve Basis + Kähler Cone + Intersection
===============================================================
用 CYTools ToricVariety 完整 API:
  tv.curve_basis() → curves
  tv.kahler_cone() → Kähler cone (inequalities)
  tv.mori_cone() → Mori cone (dual)
  tv.intersection_numbers() → κ_ijk
  tv.effective_cone() → effective cone
  tv.sr_ideal() → SR ideal

目標:
  1. Curve 數量 (對比 155 adjacency)
  2. Kähler cone 不等式結構
  3. Intersection numbers κ_ijk (對比 O50)
  4. 用 J* = I₃⊗J₁₂ 計 curve volumes
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O57 三期 22: CYTools Curve/Kähler/Intersection")
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

poly = Polytope(d["vertices"])
tri = poly.triangulate()
tv = tri.get_toric_variety()
print(f"  ToricVariety: dim={tv.dim()}")

# ============ 1. Curve basis ============
print("\n[1] Curve basis")
curves = tv.curve_basis()
print(f"  Curves: {len(curves)}")
print(f"  頭 3 個: {curves[:3]}")
if len(curves) > 0:
    c0 = curves[0]
    print(f"  curve[0] type: {type(c0).__name__}")
    print(f"  curve[0] attrs: {[a for a in dir(c0) if not a.startswith('_')][:20]}")

# ============ 2. Divisor basis ============
print("\n[2] Divisor basis")
divs = tv.divisor_basis()
print(f"  Divisors: {len(divs)}")
check("32 divisors (basis)", len(divs) == 32, f"({len(divs)})")

# ============ 3. Kähler cone ============
print("\n[3] Kähler cone (只印維度, 唔計 extremal rays — 36-dim 太慢)")
try:
    kc = tv.kahler_cone()
    print(f"  Kähler cone dim: {kc.dim()}")
    # 唔好 call extremal_rays (d=36 卡死!)
    # 用 dual_cone 檢查結構
    check("Kähler cone 32-dim (divisor basis)", kc.dim() == 32, f"({kc.dim()})")
except Exception as e:
    print(f"  ⚠️ kahler_cone 失敗: {e}")

# ============ 4. Mori cone ============
print("\n[4] Mori cone (只印維度)")
try:
    mc = tv.mori_cone()
    print(f"  Mori cone dim: {mc.dim()}")
except Exception as e:
    print(f"  ⚠️ mori_cone 失敗: {e}")

# ============ 5. Intersection numbers ============
print("\n[5] Intersection numbers")
try:
    inter = tv.intersection_numbers()
    print(f"  Intersection: {type(inter).__name__}")
    # 可能係 function 或 dict
    if callable(inter):
        # 試計 D_i·D_j·D_k
        test = inter(0, 1, 2)
        print(f"  κ_012 = {test}")
    else:
        print(f"  type: {type(inter)}")
except Exception as e:
    print(f"  ⚠️ intersection_numbers 失敗: {e}")

# ============ 6. SR ideal ============
print("\n[6] SR ideal")
try:
    sr = tv.sr_ideal()
    print(f"  SR ideal: {len(sr)} generators")
    print(f"  頭 3: {sr[:3]}")
    check("484 sr generators", len(sr) == 484, f"({len(sr)})")
except Exception as e:
    print(f"  ⚠️ sr_ideal 失敗: {e}")

# ============ 7. 總結 ============
print("\n" + "=" * 72)
print("三期 22 總結:")
print("=" * 72)

results = {
    "test": "O57 三期 22: CYTools 結構",
    "n_curves": len(curves),
    "n_divisors": len(divs),
    "passed": passed, "failed": failed
}
with open("data/22_cytools_structure.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 三期 22 完成!")
