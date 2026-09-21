#!/usr/bin/env python3
"""
O57 五期 41: CYTools 內建 Curve/Divisor Volumes
=================================================
用 CalabiYau.compute_curve_volumes() / compute_divisor_volumes()
直接計真實幾何 volumes!

然後: e^{-V_curve} 或 e^{-V_divisor} 質量譜
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 五期 41: CYTools 內建 Volumes")
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

# ============ 1. 建立 CY ============
print("\n[1] 建立 CY")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
print(f"  CY: h11={cy.h11()}, h12={cy.h12()}")

# ============ 2. Divisor volumes ============
print("\n[2] Divisor volumes (用 J*)")
jd = json.load(open(os.path.join(O53, "Jstar_36D.json")))
Jstar = np.array(jd.get("Jstar_36D", jd))

for name, t in [("J*", Jstar), ("φ^(35-i)", phi**(35-np.arange(36)))]:
    try:
        print(f"\n  --- {name} ---")
        dv = cy.compute_divisor_volumes(t)
        print(f"  divisor volumes: {dv}")
        cv = cy.compute_curve_volumes(t)
        print(f"  curve volumes: {cv}")
        cyv = cy.compute_cy_volume(t)
        print(f"  CY volume: {cyv}")
    except Exception as e:
        print(f"  ⚠️ {name}: {type(e).__name__}: {e}")

# ============ 3. 質量譜 ============
print("\n[3] e^-V 質量譜")
t = phi ** (35 - np.arange(36))
try:
    dv = np.array(cy.compute_divisor_volumes(t))
    print(f"  Divisor volumes: {dv}")
    pos = dv[dv > 1e-10]
    if len(pos) > 1:
        c = 1.0 / math.sqrt(pos.min())
        dvn = dv * c**2  # divisor volume 都係二次型?
        masses = np.exp(-dvn[dvn > 1e-10])
        ms = np.sort(masses)[::-1]
        print(f"  歸一化 e^-V masses: {ms}")
        print(f"  Finite: {np.sum(ms > 1e-30)}")
except Exception as e:
    print(f"  ⚠️: {e}")

# ============ 4. 總結 ============
print("\n" + "=" * 72)
print("五期 41 總結:")
print("=" * 72)
print(f"""
  CYTools 內建 Volumes:
  ─────────────────────────────────
  1. compute_divisor_volumes / compute_curve_volumes
  2. 用 J* 同 φ 冪次試
  3. e^-V 質量譜

  睇上面輸出
""")

results = {
    "test": "O57 五期 41: CYTools Volumes",
    "passed": passed, "failed": failed
}
with open("data/41_cytools_volumes.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 五期 41 完成!")
