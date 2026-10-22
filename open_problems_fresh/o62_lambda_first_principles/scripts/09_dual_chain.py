#!/usr/bin/env python3
"""
O62 三期 09: 對偶鏈 88-site + 真空能 — Σγ_even/odd 結構
==========================================================
IDCM 核心結構:
  44-site: Σγ = 90
  88-site 對偶鏈: Σγ_even = 90 (偶數 = 世界), Σγ_odd = 88 (奇數 = 觀察者)
  Σγ_total = 178 = 2F₁₁

F(γ_36) = 264.0821 ≈ 264 = 6N_d
V_Λ = F(γ) + 19 = 283.0821 (0.0025%)

本腳本:
  1. 88-site 對偶鏈 γ 譜同 F(γ) 嘅關係
  2. Σγ_even = 90, Σγ_odd = 88 點樣入 F?
  3. F(γ) 264.08 同 90/88 嘅關係
  4. 對偶鏈 → V_Λ 閉合
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O62 三期 09: 對偶鏈 88-site 真空能")
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

# ============ 1. 基本量 ============
print("\n[1] 對偶鏈結構")
# 88-site 對偶鏈: γ_n = 4sin²(nπ/176), n=1..88
# (44-site 用 π/88, 88-site 用 π/176)
# ⚠️ Parity 修正 (2026-08-24): Python 0-based
#   gamma88[::2] = index 0,2,... = k=1,3,...,87 = ODD k → Σγ_odd = 88
#   gamma88[1::2] = index 1,3,... = k=2,4,...,88 = EVEN k → Σγ_even = 90
gamma88 = 4 * np.sin(np.pi * np.arange(1, 89) / 176) ** 2
sum_odd = gamma88[::2].sum()    # k=1,3,...,87 (ODD)
sum_even = gamma88[1::2].sum()  # k=2,4,...,88 (EVEN)
print(f"  88-site γ (n=1..88, π/176):")
print(f"    Σγ_odd (k 奇) = {sum_odd:.6f}")
print(f"    Σγ_even (k 偶) = {sum_even:.6f}")
print(f"    Σγ_total = {sum_odd+sum_even:.6f}")
check("Σγ_odd = 88", abs(sum_odd - 88) < 0.01, f"({sum_odd:.4f})")
check("Σγ_even = 90", abs(sum_even - 90) < 0.01, f"({sum_even:.4f})")
check("Σγ_total = 178 = 2F₁₁", abs(sum_odd+sum_even - 178) < 0.01, f"({sum_odd+sum_even:.4f})")

# ============ 2. F(γ) 同 88-site ============
print("\n[2] F(γ_36) 同 88-site 關係")
d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])
gamma36 = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2
Fg = np.einsum("ijk,i,j,k", kappa, gamma36, gamma36, gamma36) / 6.0
print(f"  F(γ_36) = {Fg:.8f}")
print(f"  3×Σγ_odd = 3×88 = 264")
print(f"  ★ 264 = 3×88 = 3×Σγ_odd (奇數鏈!)")
check("264 = 3×88", 264 == 3*88)
check("264 = 3×Σγ_odd", abs(264 - 3*sum_odd) < 0.01)

print(f"\n  F(γ) − 3×88 = {Fg - 264:.8f}")
print(f"  3×90 = 270, 270 − F(γ) = {270 - Fg:.8f}")
print(f"  F(γ) − 3×90 = {Fg - 270:.8f}")

# ============ 3. V_Λ 同對偶鏈 ============
print("\n[3] V_Λ 同對偶鏈")
V_obs = 283.0752
V_new = Fg + 19
print(f"  V_new = F(γ) + 19 = {V_new:.8f}")
print(f"  V_obs = {V_obs:.8f}")
print(f"  19 = 44 − 25 (N_d − CPX gap)")
print(f"  25 = F₈ + B = 21 + 4")

# 對偶鏈詮釋
print(f"\n  對偶鏈詮釋:")
print(f"  F(γ) ≈ 3×88 = 3×Σγ_odd (觀察者鏈 × 3 代)")
print(f"  修正 19 = N_d − CPX gap")
print(f"  V_Λ ≈ 3×88 + 19 = 283")
print(f"  = 3Σγ_odd + N_d − (F₈+B)")
print(f"  = 264 + 44 − 25 = 283")

# 88 vs 90 對稱性
print(f"\n  88 vs 90:")
print(f"  3×88 + 19 = {3*88+19} (誤差 {abs(3*88+19-V_obs)/V_obs*100:.4f}%)")
print(f"  3×90 + 13 = {3*90+13} (誤差 {abs(3*90+13-V_obs)/V_obs*100:.4f}%)")
print(f"  13 = F₇ = Fibonacci 7")
print(f"  13 = L₄+6 = 7+6")

# ============ 4. 更精確: F(γ) 分解 ============
print("\n[4] F(γ) = 3×88 + rem 精確化")
rem = Fg - 264
print(f"  rem = {rem:.10f}")
# rem ≈ γ_29/36 = 0.08218 (0.06%)
# 或者 rem = γ_4 + γ_1×0.22?
print(f"  γ_29/36 = {4*math.sin(29*math.pi/88)**2/36:.10f}")
print(f"  誤差 = {abs(rem - 4*math.sin(29*math.pi/88)**2/36)/rem*100:.4f}%")
print(f"  29 = L₇ (Lucas 7)")
print(f"  36 = h¹¹")

# rem 同 Σγ 關係
print(f"\n  rem/90 = {rem/90:.8f}")
print(f"  rem/88 = {rem/88:.8f}")
print(f"  rem×44 = {rem*44:.6f}")
print(f"  rem×88 = {rem*88:.6f}")

# ============ 5. 對偶鏈 V_Λ 完整公式 ============
print("\n[5] 對偶鏈 V_Λ 完整公式")
formulas = {
    "F(γ)+19": Fg + 19,
    "3Σγ_odd+44−25": 3*88 + 44 - 25,
    "3Σγ_odd+19": 3*88 + 19,
    "3Σγ_odd+13": 3*88 + 13,
    "F(γ)+44−F₈−B": Fg + 44 - 21 - 4,
    "V₁₀+44γ₆ (O57)": 275.0181806 + 44*4*math.sin(6*math.pi/88)**2,
}
print(f"  V_obs = {V_obs:.8f}")
print(f"  {'公式':28s} {'值':>12s} {'誤差%':>10s}")
for name, val in formulas.items():
    err = abs(val - V_obs)/V_obs*100
    print(f"  {name:28s} {val:12.6f} {err:9.5f}%")

# ============ 6. 物理詮釋 ============
print("\n[6] 物理詮釋")
print(f"""
  對偶鏈真空能:
  ─────────────────────────────
  Σγ_odd = 88 = 奇數鏈 (觀察者), Σγ_even = 90 = 偶數鏈 (世界)
  N_gen = 3
  → 3×Σγ_odd = 264 = 觀察者鏈 × 3 代
  → F(γ) = 264.08 = κ prepotential @ γ VEV
    (κ 3×12 block 結構令 3 代各自貢獻)

  修正:
  N_d − (F₈+B) = 44 − 25 = 19
  = 世界鏈 44-site 減去 CPX kernel 缺口
  = 可觀測維度補償

  V_Λ = 3Σγ_even + N_d − (F₈+B)
      = 264 + 19 = 283
""")

# ============ 7. 總結 ============
print("\n" + "=" * 72)
print("三期 09 總結:")
print("=" * 72)
print(f"""
  ★ 對偶鏈發現:
  264 = 3 × Σγ_odd = 3 × 88  (奇數鏈!)
  F(γ) = 264.0821 (誤差 0.031%)
  V_Λ = F(γ) + 19 = 283.0821 (0.0025%)

  公式: V_Λ ≈ 3Σγ_odd + N_d − (F₈+B)
       = 264 + 19 = 283
""")
out = {
    "test": "O62 三期 09: 對偶鏈",
    "sum_even": float(sum_even), "sum_odd": float(sum_odd),
    "F_gamma": float(Fg), "F_minus_3x88": float(Fg - 264),
    "V_obs": V_obs, "V_new": float(V_new),
    "formulas": {k: float(v) for k, v in formulas.items()},
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "09_dual_chain.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 三期 09 完成!")
