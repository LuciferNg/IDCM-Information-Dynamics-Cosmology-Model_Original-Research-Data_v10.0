#!/usr/bin/env python3
"""
O57 七期 52: Curve Volumes Lucas 解碼 + SM 對齊（完整閉合）
=============================================================
七期 51 發現: 5 個細 curve volumes 有精確 Lucas 結構:
  V1 = 1.000        = φ⁰
  V2 = 9.472        = L₃φ + L₂
  V3 = 22.180       = L₄φ + L₃ + φ⁴
  V4 = 24.798       = L₅φ + L₄
  V5 = 40.125       = L₆φ + L₅
  V4 − V3 = φ² = 2.618 (0.03%)

目標:
  1. 完整解碼全部 volume 嘅 Lucas 結構
  2. 質量比 m_i/m_j = e^{V_j−V_i} 對比 SM
  3. 3 代對應
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 七期 52: Lucas 解碼 + SM 對齊")
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
print("\n[1] Curve volumes")
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
V = pos[:5]
print(f"  5 個細 volume: {V}")

# ============ 2. Lucas 解碼 ============
print("\n[2] Lucas 解碼")
L = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76]
def Ln(n):
    return L[n]

# 解碼每個 V
decoded = {
    "V1": ("φ⁰", 1.0),
    "V2": ("L₃φ+L₂", Ln(3)*phi + Ln(2)),
    "V3": ("L₄φ+L₃+φ⁴", Ln(4)*phi + Ln(3) + phi**4),
    "V4": ("L₅φ+L₄", Ln(5)*phi + Ln(4)),
    "V5": ("L₆φ+L₅", Ln(6)*phi + Ln(5)),
}
print(f"  {'V':>4s} {'值':>12s} {'解碼':>20s} {'計算':>12s} {'誤差':>10s}")
for i, (name, (expr, val)) in enumerate(decoded.items()):
    err = abs(V[i] - val)
    rel = err / V[i] * 100
    print(f"  {name} {V[i]:12.6f} {expr:>20s} {val:12.6f} {rel:9.3f}%")
    check(f"{name} 解碼", err < 0.01, f"({expr}, 誤差 {rel:.3f}%)")

# V4 - V3 = φ²?
d43 = V[3] - V[2]
check("V4−V3 = φ²", abs(d43 - phi**2) < 0.01, f"({d43:.6f} vs {phi**2:.6f})")

# ============ 3. 質量比 → SM ============
print("\n[3] 質量比 → SM")
m = np.exp(-V)
print(f"  質量: {m}")

# 模型質量比
print(f"\n  模型質量比 (m_i/m_j = e^{{V_j−V_i}}):")
ratios = {}
for i in range(5):
    for j in range(i+1, 5):
        r = m[i]/m[j]
        ratios[f"m{i+1}/m{j+1}"] = r
        print(f"    m{i+1}/m{j+1} = {r:.2e}  (V差 {V[j]-V[i]:.2f})")

# SM 質量比
print(f"\n  SM 質量比:")
sm = {"t": 172760, "b": 4180, "τ": 1776.86, "c": 1270, "μ": 105.66, "s": 93.4, "d": 4.67, "u": 2.16, "e": 0.511}
sm_pairs = [("t/e", 172760/0.511), ("t/μ", 172760/105.66), ("b/e", 4180/0.511),
            ("τ/e", 1776.86/0.511), ("t/τ", 172760/1776.86), ("b/τ", 4180/1776.86)]
for name, r in sm_pairs:
    print(f"    {name} = {r:.2e}")

# ============ 4. 最接近 SM 比 ============
print("\n[4] 模型比 ↔ SM 比")
# 模型: m1/m5 = 9.8e16, m1/m2 = 4780, m2/m3 = 3.3e5, m3/m4 = 13.7, m4/m5 = 4534
model_ratios = {
    "m1/m2": ratios["m1/m2"], "m1/m3": ratios["m1/m3"], "m1/m4": ratios["m1/m4"], "m1/m5": ratios["m1/m5"],
    "m2/m3": ratios["m2/m3"], "m2/m4": ratios["m2/m4"], "m2/m5": ratios["m2/m5"],
    "m3/m4": ratios["m3/m4"], "m3/m5": ratios["m3/m5"], "m4/m5": ratios["m4/m5"],
}
sm_ratios = {
    "t/e": 172760/0.511, "t/μ": 172760/105.66, "t/τ": 172760/1776.86,
    "b/e": 4180/0.511, "b/μ": 4180/105.66, "τ/e": 1776.86/0.511,
    "c/e": 1270/0.511, "μ/e": 105.66/0.511, "s/e": 93.4/0.511,
    "t/b": 172760/4180, "b/τ": 4180/1776.86, "c/μ": 1270/105.66,
}
print(f"\n  對數距離 (|ln(r_model) − ln(r_sm)|):")
best = []
for mr_name, mr in model_ratios.items():
    for sr_name, sr in sm_ratios.items():
        d = abs(math.log(mr) - math.log(sr))
        best.append((d, mr_name, sr_name, mr, sr))
best.sort()
print(f"  {'模型比':>8s} {'SM 比':>8s} {'Δln':>8s} {'r_model':>10s} {'r_sm':>10s}")
for d, mr_name, sr_name, mr, sr in best[:8]:
    print(f"  {mr_name:>8s} {sr_name:>8s} {d:8.3f} {mr:10.2e} {sr:10.2e}")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("七期 52 總結:")
print("=" * 72)
print(f"""
  Curve Volumes Lucas 解碼:
  ─────────────────────────────────
  1. V1 = φ⁰ (1.000)
  2. V2 = L₃φ+L₂ (9.472)
  3. V3 = L₄φ+L₃+φ⁴ (22.180)
  4. V4 = L₅φ+L₄ (24.798)
  5. V5 = L₆φ+L₅ (40.125)
  6. V4−V3 = φ² (2.618)

  {'✅ Lucas 結構閉合!' if all(abs(V[i]-val) < 0.01 for i, (_, val) in enumerate(decoded.values())) else '❌'}
""")

results = {
    "test": "O57 七期 52: Lucas 解碼",
    "V": [float(x) for x in V],
    "decoded": {k: [v[0], float(v[1])] for k, v in decoded.items()},
    "V4_minus_V3": float(d43),
    "phi2": float(phi**2),
    "passed": passed, "failed": failed
}
with open("data/52_lucas_decode.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 七期 52 完成!")
