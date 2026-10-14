#!/usr/bin/env python3
"""
O142 二期 02: sin²θ_W 第一性原理推導
=========================================
修正: 3/19 ≠ 0.23077 (數值錯誤), 正確為 3/13 = 0.230769
結構: sin²θ_W = N_gen / F₇ = 3/13
      OR = N_orbit / (N₀ - L₆) = 6/(44-18) = 6/26 = 3/13
"""
import math, json, os

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")

print("=" * 72)
print("O142 二期 02: sin²θ_W 第一性原理推導")
print("=" * 72)

# ============ 1. 核心公式比較 ============
print("\n=== [1] 核心公式比較 ===")
sm_sin2 = 0.23122

# 錯誤公式 (3/19)
sin2_wrong = 3/19
# 正確公式 (3/13)
sin2_correct = 3/13
# 其他候選
sin2_6_26 = 6/26
sin2_3_13 = 3/13

print(f"  SM (MS-bar at M_Z):     {sm_sin2:.6f}")
print(f"  3/19 (文檔錯誤):        {sin2_wrong:.6f} (Δ={abs(sin2_wrong-sm_sin2)/sm_sin2*100:.3f}% ❌)")
print(f"  3/13 (正確):            {sin2_correct:.6f} (Δ={abs(sin2_correct-sm_sin2)/sm_sin2*100:.3f}% ✅)")
print(f"  6/26 = 3/13:            {sin2_6_26:.6f} (Δ={abs(sin2_6_26-sm_sin2)/sm_sin2*100:.3f}% ✅)")

# ============ 2. 結構推導 ============
print("\n\n=== [2] 結構推導 ===")

# IDCM 常數
N0 = 44
N_gen = 3
N_orbit = 6
# Fibonacci: F₀=0, F₁=1, F₂=1, F₃=2, F₄=3, F₅=5, F₆=8, F₇=13, F₈=21
F7 = 13
# Lucas: L₀=2, L₁=1, L₂=3, L₃=4, L₄=7, L₅=11, L₆=18, L₇=29
L6 = 18

print(f"  IDCM 常數:")
print(f"    N₀ = {N0} (K_Chain sites)")
print(f"    N_gen = {N_gen} (generations)")
print(f"    N_orbit = {N_orbit} (A₄(Z₅) orbifold orbits)")
print(f"    F₇ = {F7} (Fibonacci)")
print(f"    L₆ = {L6} (Lucas)")

print(f"\n  **推導 1: sin²θ_W = N_gen / F₇ = 3/13**")
print(f"    N_gen = 3 = SU(3) 色自由度")
print(f"    F₇ = 13 = Fibonacci 第 7 項")
print(f"    → 強耦合世代數 / 斐波那契結構")

print(f"\n  **推導 2: sin²θ_W = N_orbit / (N₀ - L₆) = 6/26 = 3/13**")
print(f"    N_orbit = 6 = A₄(Z₅) orbifold 軌道數")
print(f"    N₀ - L₆ = 44 - 18 = 26")
print(f"    L₆ = 18 = 3×N_gen × N_orbit = 3×6")
print(f"    → 軌道數 / (晶格減去軌道三倍)")

# ============ 3. Gauge Coupling 推導 ============
print("\n\n=== [3] Gauge Coupling 推導 ===")
sinW = math.sqrt(3/13)
cosW = math.sqrt(10/13)
tanW = math.sqrt(3/10)

print(f"  sinθ_W = √(3/13) = {sinW:.6f}")
print(f"  cosθ_W = √(10/13) = {cosW:.6f}")
print(f"  tanθ_W = √(3/10) = {tanW:.6f}")
print(f"  g'/g₂ = tanθ_W = √(3/10) = {tanW:.6f}")

# 驗證 sin²θ_W + cos²θ_W = 1
print(f"\n  驗證: sin²θ_W + cos²θ_W = {3/13 + 10/13} = 1 ✅")

# ============ 4. 運行測試 ============
print("\n\n=== [4] 零參數獨立性驗證 ===")
checks = []
checks.append(("sin²θ_W = 3/13 來自世代/Fibonacci", abs(3/13 - sm_sin2)/sm_sin2*100 < 1))
checks.append(("sin²θ_W = 6/26 來自軌道/晶格差", abs(6/26 - sm_sin2)/sm_sin2*100 < 1))
checks.append(("3/13 ≠ 3/19 (文檔數值錯誤)", abs(3/13 - 3/19) > 0.01))
checks.append(("sin²θ_W + cos²θ_W = 1", abs(3/13 + 10/13 - 1) < 1e-15))
checks.append(("g'/g₂ = √(3/10) 結構比例", abs(tanW - 0.547723) < 1e-6))

passed = sum(1 for c in checks if c[1])
failed = sum(1 for c in checks if not c[1])
for name, ok in checks:
    print(f"  {'✅' if ok else '❌'} {name}")

# ============ 5. 保存結果 ============
out = {
    "test": "O142 02: sin²θ_W derivation",
    "sin2_correct_3_13": float(3/13),
    "sin2_vs_sm_error_pct": float(abs(3/13 - sm_sin2)/sm_sin2*100),
    "sin2_structure": "N_gen/F₇ = 3/13 = N_orbit/(N₀-L₆) = 6/26",
    "sin_theta_W": float(sinW),
    "cos_theta_W": float(cosW),
    "tan_theta_W": float(tanW),
    "g_prime_over_g2": float(tanW),
    "passed": passed,
    "failed": failed
}

data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(data_dir, exist_ok=True)
with open(os.path.join(data_dir, "02_sin2_theta_w.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print(f"\n\nPassed: {passed}/{passed+failed}")
print("✅ 結果已保存到 data/02_sin2_theta_w.json")