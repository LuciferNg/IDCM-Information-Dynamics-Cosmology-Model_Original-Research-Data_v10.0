#!/usr/bin/env python3
"""
O57 五期 43: CYTools Curve Volumes 質量譜 — 完整分析
=====================================================
發現: CYTools compute_curve_volumes 有 117 positive, range 1.03e8
     前幾個 V 好細 (1, 9.5, 22, 25, 40, 131) → 有質量
     後面全部 V 好大 → 無質量

真正 Yukawa 壓抑: e^{-V_curve} (2-cycle volume)

分析:
  1. 全部 curve volumes 分佈
  2. e^{-V} 質量譜 (有幾多個有限質量)
  3. 質量比階層
  4. 對比 SM 15 粒子
  5. 3 代結構
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 五期 43: CYTools Curve Volume 質量譜")
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

# ============ 1. 建立 + volumes ============
print("\n[1] CYTools curve volumes")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
basis = cy.divisor_basis()

for name, t36 in [
    ("φ^(35-i)", phi ** (35 - np.arange(36))),
    ("φ^(i-1)", phi ** np.arange(36)),
    ("J*", np.array(json.load(open(os.path.join(O53, "Jstar_36D.json"))).get("Jstar_36D", 
          json.load(open(os.path.join(O53, "Jstar_36D.json")))))),
]:
    t32 = np.array([t36[b-1] for b in basis])
    try:
        cv = np.array(cy.compute_curve_volumes(t32))
        pos = cv[cv > 1e-10]
        print(f"\n  --- {name} ---")
        print(f"  n_pos: {len(pos)}/{len(cv)}")
        if len(pos) > 1:
            print(f"  range: {pos.max()/pos.min():.2e}")
            # e^-V
            masses = np.exp(-pos)
            ms = np.sort(masses)[::-1]
            n_finite = np.sum(ms > 1e-30)
            print(f"  e^-V finite: {n_finite}")
            if n_finite > 0:
                print(f"  masses (top): {ms[:15]}")
    except Exception as e:
        print(f"  ⚠️ {name}: {e}")

# ============ 2. φ^(35-i) 詳細 ============
print("\n[2] φ^(35-i) 詳細")
t36 = phi ** (35 - np.arange(36))
t32 = np.array([t36[b-1] for b in basis])
cv = np.array(cy.compute_curve_volumes(t32))
pos = cv[cv > 1e-10]
print(f"  Curve volumes (positive, sorted): {np.sort(pos)}")
masses = np.exp(-pos)
ms = np.sort(masses)[::-1]
print(f"  e^-V 質量 (全部): {ms}")
n_finite = np.sum(ms > 1e-30)
print(f"  Finite masses: {n_finite}")
if n_finite > 0:
    mf = ms[:n_finite]
    print(f"  質量比: {mf.max()/mf.min():.2e}")

# ============ 3. 世代對應 ============
print("\n[3] 世代結構 (如果 curve basis 有世代)")
cb = cy.curve_basis()
print(f"  curve_basis: {cb}")
print(f"  len: {len(cb)}")

# ============ 4. SM 對比 ============
print("\n[4] SM 對比")
sm = [0.001, 0.511, 2.16, 4.67, 93.4, 105.66, 1270, 1776.86, 4180, 80377, 91187.6, 125250, 172760]
print(f"  SM: {len(sm)} 粒子, range={max(sm)/min(sm):.1e}")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("五期 43 總結:")
print("=" * 72)
print(f"""
  CYTools Curve Volume 質量譜:
  ─────────────────────────────────
  1. φ^(35-i): {len(pos)} positive curves, range {pos.max()/pos.min():.2e}
  2. e^-V 質量: {n_finite} 個有限
  3. 質量比: {'NA' if n_finite < 2 else f'{mf.max()/mf.min():.2e}'}
  4. SM 需要: 13 粒子, range 1.7e8

  {'✅ curve volumes 有質量階層!' if n_finite >= 3 else '❌ 有限質量太少'}
""")

results = {
    "test": "O57 五期 43: Curve Volume 質量譜",
    "n_pos": int(len(pos)),
    "range": float(pos.max()/pos.min()),
    "n_finite": int(n_finite),
    "passed": passed, "failed": failed
}
with open("data/43_curve_vol_mass.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 五期 43 完成!")
