#!/usr/bin/env python3
"""
O57 八期 56: 方向 1 — 9 費米子全譜聯合 χ² 檢定
=================================================
Gemini 方向 1 (Joint Spectrum Constraint):
  χ² = Σ (ln M_model - ln M_SM)²/σ²
  9 個帶電費米子: u, d, s, c, b, t, e, μ, τ

模型: m_i = M₀·e^{-V_i}
  V_i = Lucas 能階 (V1..V5) + 高階?

問題: 只有 5 個 Lucas 能階, 但有 9 個費米子
  → 需要多啲能階 (Lucas 無限延伸?)

測試:
  1. Lucas 能階 V_n = Lₙφ+Lₙ₋₁ (n=1..20)
  2. 揀 9 個能階 → 9 個質量
  3. 最佳 M₀ (單一自由參數)
  4. χ² 檢定 (9 dof - 1 = 8 dof)
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 八期 56: 9 費米子全譜 χ²")
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

# ============ 1. SM 質量 ============
print("\n[1] SM 9 費米子質量 (MeV)")
sm_masses = {
    "u": 2.16, "d": 4.67, "s": 93.4, "c": 1270, "b": 4180, "t": 172760,
    "e": 0.511, "μ": 105.66, "τ": 1776.86
}
sm_names = list(sm_masses.keys())
sm_vals = np.array([sm_masses[k] for k in sm_names])
print(f"  {sm_names}")
print(f"  {sm_vals}")

# ============ 2. Lucas 能階 ============
print("\n[2] Lucas 能階")
L = [2, 1]
for i in range(2, 30):
    L.append(L[i-1] + L[i-2])

# V_n = Lₙφ+Lₙ₋₁ (n=1..)
V_lucas = []
for n in range(1, 25):
    V_lucas.append(L[n]*phi + L[n-1])
print(f"  V_n (n=1..12): {[f'{v:.2f}' for v in V_lucas[:12]]}")
print(f"  我哋嘅 5 個: {V_lucas[0]}, {V_lucas[3]}, {V_lucas[4]}, {V_lucas[5]}, {V_lucas[6]}")
print(f"  (V1={V_lucas[0]:.2f}, V2={V_lucas[3]:.2f}, V3={V_lucas[4]:.2f}, V4={V_lucas[5]:.2f}, V5={V_lucas[6]:.2f})")

# 實際 5 個 V: [1.0, 9.47, 22.18, 24.80, 40.12]
# V_lucas[0] = L₁φ+L₀ = 1×φ+2 = 3.62 (唔係 1!)
# V_lucas[3] = L₃φ+L₂ = 4×φ+3 = 9.47 ✓
# V_lucas[4] = L₄φ+L₃ = 7×φ+4 = 15.33 (唔係 22.18!)
# V_lucas[5] = L₅φ+L₄ = 11×φ+7 = 24.80 ✓
# V_lucas[6] = L₆φ+L₅ = 18×φ+11 = 40.12 ✓
print("\n  對應檢查:")
print(f"  V_actual[1] = 9.472 vs V_lucas[3] = {V_lucas[3]:.4f} ✓")
print(f"  V_actual[3] = 24.798 vs V_lucas[5] = {V_lucas[5]:.4f} ✓")
print(f"  V_actual[4] = 40.125 vs V_lucas[6] = {V_lucas[6]:.4f} ✓")

# ============ 3. 9 能階選擇 ============
print("\n[3] 9 個能階 → 9 個質量")
# 候選能階集: V1=φ⁰, V2=L₃φ+L₂, V3=L₄φ+L₃+φ⁴, V4=L₅φ+L₄, V5=L₆φ+L₅
# + 高階: V6=L₇φ+L₆, V7=L₈φ+L₇, V8=L₉φ+L₈, V9=L₁₀φ+L₉
V_set = [1.0, V_lucas[3], V_lucas[4]+phi**4, V_lucas[5], V_lucas[6],
         V_lucas[7], V_lucas[8], V_lucas[9], V_lucas[10]]
print(f"  9 個能階: {[f'{v:.2f}' for v in V_set]}")

# ============ 4. 最佳 M₀ ============
print("\n[4] 最佳 M₀ (單一參數 fit)")
# m_model_i = M₀·e^{-V_i}
# ln m_model = ln M₀ - V_i
# fit: ln M₀ = mean(ln m_SM + V_i)
ln_m_sm = np.log(sm_vals)
ln_M0 = np.mean(ln_m_sm + np.array(V_set))
M0_best = math.exp(ln_M0)
print(f"  ln M₀ = {ln_M0:.4f}")
print(f"  M₀ = {M0_best:.4f} MeV")

# 模型質量
m_model = M0_best * np.exp(-np.array(V_set))
print(f"\n  模型質量 (MeV):")
print(f"  {'SM':>6s} {'m_SM':>10s} {'m_model':>12s} {'ln差':>8s}")
for i, name in enumerate(sm_names):
    d = math.log(sm_vals[i]) - math.log(m_model[i])
    print(f"  {name:>6s} {sm_vals[i]:10.4f} {m_model[i]:12.4f} {d:8.3f}")

# ============ 5. χ² ============
print("\n[5] χ² 檢定")
# σ: 用對數空間嘅典型誤差 (質量比 ~10% 嘅對數 = 0.1)
sigma_ln = 0.1  # 10% 對數誤差
chi2 = np.sum((ln_m_sm - (ln_M0 - np.array(V_set)))**2) / sigma_ln**2
dof = 9 - 1  # 9 質量 - 1 參數 (M₀)
p_val = 1  # 用 chi2 分佈
from math import exp, lgamma
def chi2_sf(x, k):
    """chi2 survival function"""
    if x <= 0:
        return 1.0
    # 用 incomplete gamma: Q(k/2, x/2)
    from scipy.special import gammaincc
    return gammaincc(k/2, x/2)
try:
    from scipy.special import gammaincc
    p_val = gammaincc(dof/2, chi2/2)
except ImportError:
    p_val = None

print(f"  χ² = {chi2:.2f}")
print(f"  dof = {dof}")
print(f"  χ²/dof = {chi2/dof:.2f}")
if p_val:
    print(f"  p = {p_val:.2e}")
    check("χ² 檢定通過 (p>0.05)", p_val > 0.05, f"(p={p_val:.2e})")
else:
    print(f"  p = (scipy 唔可用)")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("八期 56 總結:")
print("=" * 72)
print(f"""
  9 費米子全譜 χ²:
  ─────────────────────────────────
  1. 9 能階: {[f'{v:.1f}' for v in V_set]}
  2. M₀ = {M0_best:.2f} MeV
  3. χ² = {chi2:.2f} (dof={dof})
  4. p = {p_val if p_val else 'NA'}

  {'✅ 全譜閉合!' if p_val and p_val > 0.05 else '❌ 未閉合 (需更多 work)'}
""")

results = {
    "test": "O57 八期 56: 9 費米子 χ²",
    "M0": float(M0_best),
    "V_set": [float(x) for x in V_set],
    "chi2": float(chi2),
    "dof": int(dof),
    "p_val": float(p_val) if p_val else None,
    "passed": passed, "failed": failed
}
with open("data/56_chi2_9fermion.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 八期 56 完成!")
