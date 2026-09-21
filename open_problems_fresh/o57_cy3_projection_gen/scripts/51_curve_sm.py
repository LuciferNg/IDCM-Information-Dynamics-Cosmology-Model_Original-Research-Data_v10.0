#!/usr/bin/env python3
"""
O57 七期 51: Curve Volumes 5 質量 → SM 對齊
==============================================
Gemini 苗頭: 用五期 curve volumes 5 個有限質量對 SM 粒子

五期 43: φ^(35-i) curve volumes:
  V = [1.00, 9.47, 22.18, 24.80, 40.12]
  m = e^-V = [0.368, 7.7e-5, 2.3e-10, 1.7e-11, 3.8e-18]

SM 質量 (MeV):
  e = 0.511, μ = 105.66, τ = 1776.86
  u = 2.16, d = 4.67, s = 93.4, c = 1270, b = 4180, t = 172760

測試:
  1. ln|V| 對比 SM ln(m)
  2. 5 個質量態 → 邊啲 SM 粒子?
  3. 3 代結構 (e,μ,τ) + 2 個 heavy (t,b)?
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
DATA = os.path.join(BASE, "data")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 七期 51: Curve Volumes → SM 對齊")
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

# ============ 1. Curve volumes ============
print("\n[1] Curve volumes (φ^(35-i))")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
basis = cy.divisor_basis()
t36 = phi ** (35 - np.arange(36))
t32 = np.array([t36[b-1] for b in basis])
cv = np.array(cy.compute_curve_volumes(t32))
pos = np.sort(cv[cv > 1e-10])
print(f"  Positive: {len(pos)}, range: {pos.max()/pos.min():.2e}")
print(f"  細 volumes (top 10): {pos[:10]}")

# ============ 2. 5 個有限質量 ============
print("\n[2] 5 個最小 volume → 質量")
V_small = pos[:5]
m = np.exp(-V_small)
print(f"  V: {V_small}")
print(f"  m = e^-V: {m}")
print(f"  ln(V): {np.log(V_small)}")
print(f"  ln(m): {np.log(m)}")

# ============ 3. SM 對比 ============
print("\n[3] SM 對比")
sm = {
    "e": 0.511, "μ": 105.66, "τ": 1776.86,
    "u": 2.16, "d": 4.67, "s": 93.4, "c": 1270, "b": 4180, "t": 172760
}
sm_sorted = sorted(sm.items(), key=lambda x: x[1])
print(f"  SM 質量 (sorted): {[(k, v) for k, v in sm_sorted]}")

# 對數比對
print("\n  ln(m_model) vs ln(m_SM):")
print(f"  {'model':>10s} {'ln(m)':>10s} {'SM':>6s} {'ln(SM)':>10s} {'Δln':>8s}")
for i, (V, mm) in enumerate(zip(V_small, m)):
    ln_mm = math.log(mm)
    # 揾最接近嘅 SM
    best = min(sm.items(), key=lambda kv: abs(math.log(kv[1]) - ln_mm))
    print(f"  m{i+1:3d}      {ln_mm:10.2f} {best[0]:>6s} {math.log(best[1]):10.2f} {abs(math.log(best[1])-ln_mm):8.2f}")

# ============ 4. 階層比對 ============
print("\n[4] 階層比對")
# 模型: m1/m5 = e^{V5-V1}
ratio_model = m[0]/m[-1]
ratio_sm = 172760/0.511
print(f"  模型 m1/m5 = {ratio_model:.2e}")
print(f"  SM t/e   = {ratio_sm:.2e}")
print(f"  比率比   = {ratio_model/ratio_sm:.2e}")
check("模型階層 > SM 階層", ratio_model > ratio_sm, f"({ratio_model:.1e} vs {ratio_sm:.1e})")

# ============ 5. 3 代結構? ============
print("\n[5] 3 代結構 (5 個質量)")
# 5 個質量: 可能係 3 輕子 + 2 重夸克?
# 或者 3 代 × (輕子/夸克)?
m_sorted = np.sort(m)[::-1]
print(f"  質量 (desc): {m_sorted}")
gaps = np.diff(np.log(m_sorted))
print(f"  ln-gaps: {gaps}")
print(f"  最大 gap: {gaps.max():.2f} at position {np.argmax(gaps)+1}")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("七期 51 總結:")
print("=" * 72)
print(f"""
  Curve Volumes → SM 對齊:
  ─────────────────────────────────
  1. 5 個最小 volume: {V_small}
  2. 質量: {m}
  3. 最接近 SM: 睇上面
  4. 階層比: {ratio_model:.1e} vs SM {ratio_sm:.1e}

  {'✅ 階層方向正確!' if ratio_model > ratio_sm else '❌ 階層唔夠'}
""")

results = {
    "test": "O57 七期 51: Curve → SM",
    "V_small": [float(x) for x in V_small],
    "masses": [float(x) for x in m],
    "ratio_model": float(ratio_model),
    "ratio_sm": float(ratio_sm),
    "passed": passed, "failed": failed
}
with open("data/51_curve_sm.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 七期 51 完成!")
