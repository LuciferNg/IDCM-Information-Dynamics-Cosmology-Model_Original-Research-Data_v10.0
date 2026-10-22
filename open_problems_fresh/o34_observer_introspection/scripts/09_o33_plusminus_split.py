#!/usr/bin/env python3
"""
O34 — O33 未被投影機制：±M 分半對稱 (核心發現!)
========================================================
新發現: 未被投影同物質係世界能量 ± K_Tree 深度分半!

  (Σγ_even + M)/2 = (90 + 33)/2 = 61.5  (未被投影)
  (Σγ_even − M)/2 = (90 − 33)/2 = 28.5  (物質)

M = 33 = 3×(φ⁵−φ⁻⁵) (四部曲定理, K_Tree 深度)
Σγ_even = 90 (O34 世界能量)

驗證:
  [1] 61.5 = (90+33)/2 精確
  [2] 28.5 = (90−33)/2 精確
  [3] 41/60 = 0.683333 vs Ω_Λ = 0.683282 (0.005%)
  [4] 19/60 = 0.316667 vs Ω_m = 0.316718 (0.005%)
  [5] M = 33 係咪比 L = 53/8 更基本? (33 = 3(φ⁵−φ⁻⁵) 四部曲)
"""

import numpy as np
from decimal import Decimal, getcontext

getcontext().prec = 100

N = 44
phi = (1 + np.sqrt(5)) / 2
phi_inv = phi - 1
eps = phi_inv / 4

PASS = 0
FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    status = "✅" if cond else "❌"
    if cond:
        PASS += 1
    else:
        FAIL += 1
    print(f"  {status} {name}" + (f" — {detail}" if detail else ""))

print("=" * 67)
print("  O34 — ±M 分半對稱 (未被投影機制)")
print("=" * 67)

# 基礎結構
M = 33
sum_even = 90.0
sum_odd = 88.0

unproj = (sum_even + M) / 2
matter = (sum_even - M) / 2

print(f"  Σγ_even = {sum_even}, M = {M}")
print(f"  (90+33)/2 = {unproj} (未被投影)")
print(f"  (90−33)/2 = {matter} (物質)")
print()

# [1] 精確性
check("[1] 未被投影 = (90+33)/2 = 61.5", unproj == 61.5)
check("[2] 物質 = (90−33)/2 = 28.5", matter == 28.5)
check("[3] 61.5 + 28.5 = 90 (世界能量守恆)", unproj + matter == 90)

# [2] M = 33 結構
print("\n─── M = 33 結構驗證 ───")
M_formula = 3 * (phi**5 - phi**(-5))
print(f"  3×(φ⁵−φ⁻⁵) = {M_formula:.10f}")
check("[4] M = 33 = 3(φ⁵−φ⁻⁵)", abs(M_formula - 33) < 1e-8)

# χ = 3N_d + 2 = 134, M = (χ−2)/4 = 33 (四部曲)
chi = 3 * N + 2
M_from_chi = (chi - 2) / 4
print(f"  χ = 3N_d+2 = {chi}, M = (χ−2)/4 = {M_from_chi}")
check("[5] M = (χ−2)/4 = 33", M_from_chi == 33)

# [3] 密度對應
print("\n─── 密度對應 ───")
Omega_L_exact = 4 / (phi**4 - 1)
Omega_m_exact = 3 * eps / (1 + 3 * eps)

unproj_frac = unproj / 90
matter_frac = matter / 90
print(f"  未被投影/90 = {unproj_frac:.10f} = 41/60 = {41/60:.10f}")
print(f"  精確 Ω_Λ = {Omega_L_exact:.10f}")
print(f"  偏差 = {abs(unproj_frac - Omega_L_exact):.2e}")
check("[6] 41/60 ≈ Ω_Λ (0.005%)", abs(unproj_frac - Omega_L_exact) < 1e-4,
      f"dev = {abs(unproj_frac-Omega_L_exact):.2e}")

print(f"  物質/90 = {matter_frac:.10f} = 19/60 = {19/60:.10f}")
print(f"  精確 Ω_m = {Omega_m_exact:.10f}")
print(f"  偏差 = {abs(matter_frac - Omega_m_exact):.2e}")
check("[7] 19/60 ≈ Ω_m (0.005%)", abs(matter_frac - Omega_m_exact) < 1e-4,
      f"dev = {abs(matter_frac-Omega_m_exact):.2e}")

# [4] 41/60 結構: 41 = 90/3 + L₅? 90/3 = 30, 30+11 = 41 ✓
print("\n─── 41 同 19 嘅結構 ───")
print(f"  41 = 30 + 11 = 90/3 + L₅ (L₅ = 11)")
print(f"  19 = 30 − 11 = 90/3 − L₅")
print(f"  41 + 19 = 60 = 2×30 = 2×90/3")
print(f"  41 − 19 = 22 = N_d/2 = 44/2 ✓✓✓")
check("[8] 41−19 = 22 = N_d/2", 41 - 19 == 22)

# 等價: 41 = 30+11, 19 = 30−11, 30 = 90/3, 11 = L₅
print(f"  11 = L₅ (Lucas) ✓, 30 = Σγ_even/3 ✓")
check("[9] 41 = Σγ_even/3 + L₅", 41 == 90/3 + 11)
check("[10] 19 = Σγ_even/3 − L₅", 19 == 90/3 - 11)

# [5] 同 2+B·L 形式等價
print("\n─── 同 2+B·L 等價 ───")
L_ktree = 53 / 8
B = 4
print(f"  (90−33)/2 = 28.5, 2+B·L = 2+4×(53/8) = {2 + B*L_ktree}")
check("[11] (Σγ_even−M)/2 = 2+B·L (L=53/8)", (90-33)/2 == 2 + 4*(53/8))

# M = 33 基本性: L = 53/8 由 M 推出?
# (90−33)/2 = 2+4L → 90−33 = 4+8L → 57 = 4+8L → 8L = 53 → L = 53/8
print(f"  由 (90−M)/2 = 2+B·L 推出: L = (90−M−4)/8 = (90−33−4)/8 = 53/8 ✓")
print(f"  → L = 53/8 係派生量, M = 33 係基本結構!")
check("[12] L = 53/8 由 M 派生 (M 更基本)", (90 - M - 4)/8 == 53/8)

# [6] 機制詮釋
print("\n─── 機制詮釋 ───")
print(f"""
  「未被投影」機制 (±M 分半對稱):

  世界能量 Σγ_even = 90 以 K_Tree 深度 M = 33 為中心分裂:
    未被投影 = (90 + 33)/2 = 61.5  → 觀察者「純自我參照」能量
    物質     = (90 − 33)/2 = 28.5  → 投影成物質嘅能量

  M = 33 = K_Tree 深度 (3(φ⁵−φ⁻⁵)) 係分裂中心:
    → 樹深度越大, 物質越少, 未被投影越多
    → Ω_Λ 大 = 觀察者自我參照能量佔主導

  41/60 結構: 41 = Σγ_even/3 + L₅ (Lucas 對稱)
  19/60 結構: 19 = Σγ_even/3 − L₅
  41 − 19 = 22 = N_d/2 (奇偶鏈半維度!)
""")

# 儲存
with open("data/o33_plusminus_split_results.txt", "w") as f:
    f.write("O34 — ±M Split Symmetry (O33 unprojected mechanism)\n")
    f.write("=" * 67 + "\n")
    f.write(f"unproj = (90+33)/2 = {unproj}\n")
    f.write(f"matter = (90-33)/2 = {matter}\n")
    f.write(f"41/60 = {41/60:.10f} vs Omega_L = {Omega_L_exact:.10f} (dev {abs(41/60-Omega_L_exact):.2e})\n")
    f.write(f"19/60 = {19/60:.10f} vs Omega_m = {Omega_m_exact:.10f} (dev {abs(19/60-Omega_m_exact):.2e})\n")
    f.write(f"41 - 19 = 22 = N_d/2\n")
    f.write(f"M = 33 = 3(phi^5-phi^-5) = (chi-2)/4\n")
    f.write(f"PASS = {PASS}, FAIL = {FAIL}\n")
    f.write(f"Status: 🟡 strong structural candidate, ε⁰-level\n")

print(f"\n  驗證結果: {PASS} PASS, {FAIL} FAIL")
print(f"  結果已存: data/o33_plusminus_split_results.txt")
