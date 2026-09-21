#!/usr/bin/env python3
"""
O57 五期 42: CYTools 32-dim Divisor/Curve Volumes 完整分析
============================================================
用 divisor basis (32-dim) 座標:
  compute_divisor_volumes(t32) → 36 個 divisor volumes
  compute_curve_volumes(t32)  → 32 個 curve volumes

然後 e^{-V} 質量譜分析
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 五期 42: 32-dim Volumes 完整分析")
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
from cytools.config import enable_experimental_features
enable_experimental_features()

# ============ 1. 建立 ============
print("\n[1] CY 建立")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
basis = cy.divisor_basis()
print(f"  divisor basis: {basis}")

# 36-dim → 32-dim (basis 提取)
def to32(t36):
    return np.array([t36[b - 1] for b in basis])

# ============ 2. φ 冪次 32-dim ============
print("\n[2] φ 冪次 32-dim volumes")
t36_phi = phi ** (35 - np.arange(36))
t32 = to32(t36_phi)

dv = np.array(cy.compute_divisor_volumes(t32))
cv = np.array(cy.compute_curve_volumes(t32))
print(f"  Divisor volumes: n_pos={np.sum(dv>0)}, n_neg={np.sum(dv<0)}")
print(f"  Curve volumes: n_pos={np.sum(cv>0)}, n_neg={np.sum(cv<0)}")
print(f"  Divisor volumes: {dv}")
print(f"  Curve volumes: {cv}")

# ============ 3. e^-V 質量譜 ============
print("\n[3] e^-V 質量譜")
for label, vols in [("divisor", dv), ("curve", cv)]:
    pos = vols[vols > 1e-10]
    print(f"\n  --- {label} volumes ---")
    print(f"  positive: {len(pos)}")
    if len(pos) > 1:
        print(f"  range: {pos.max()/pos.min():.2e}")
        print(f"  values: {np.sort(pos)}")
        masses = np.exp(-pos)
        ms = np.sort(masses)[::-1]
        n_finite = np.sum(ms > 1e-30)
        print(f"  e^-V masses: {ms}")
        print(f"  finite: {n_finite}")

# ============ 4. 世代結構 ============
print("\n[4] Divisor 世代結構")
# divisor volumes 對應 36 個 prime divisors, 但 CYTools 返回順序?
# 應該對應 prime_toric_divisors
ptd = cy.prime_toric_divisors()
print(f"  prime_toric_divisors: {ptd}")
print(f"  len: {len(ptd)}")
if len(dv) == 36:
    for g in range(3):
        sub = dv[g*12:(g+1)*12]
        print(f"  Gen{g+1}: pos={np.sum(sub>0)}, min={sub.min():.4f}, max={sub.max():.4f}")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("五期 42 總結:")
print("=" * 72)
print(f"""
  CYTools 32-dim Volumes:
  ─────────────────────────────────
  1. Divisor volumes: {np.sum(dv>0)} positive / {len(dv)}
  2. Curve volumes: {np.sum(cv>0)} positive / {len(cv)}
  3. e^-V 質量譜: 睇上面

  睇上面輸出
""")

results = {
    "test": "O57 五期 42: 32-dim Volumes",
    "dv_pos": int(np.sum(dv > 0)),
    "cv_pos": int(np.sum(cv > 0)),
    "passed": passed, "failed": failed
}
with open("data/42_volumes_32d.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 五期 42 完成!")
