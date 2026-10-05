#!/usr/bin/env python3
"""
邊集能量閉合: Σe_k² 同 88-site 譜嘅數量關係
=============================================
發現: e_k² = 4sin²(π/176)·γ_m, m=87−2k (奇數)
"""
from math import pi, sin, cos

print("="*72)
print("1. 邊集能量 Σe_k²")
print("="*72)
e2_sum = 0.0
for k in range(1, 44):
    e = 4*sin(pi/176)*cos((2*k+1)*pi/176)
    e2_sum += e*e
print(f"Σ e_k² (k=1..43) = {e2_sum:.10f}")

sc = sum(cos((2*k+1)*pi/176)**2 for k in range(1, 44))
print(f"Σcos²((2k+1)π/176) = {sc:.10f}")
print(f"理論 16sin²(π/176)*Σcos² = {16*sin(pi/176)**2*sc:.10f}")

sc88 = sum(cos((2*k+1)*pi/176)**2 for k in range(0, 88))
print(f"88 半格點 Σcos² = {sc88:.10f} = 44 (exact)")

missing = sum(cos((2*k+1)*pi/176)**2 for k in [0] + list(range(44, 88)))
print(f"缺 k=0 同 k=44..87: Σcos² = {missing:.10f}")
print(f"43+45 = 88: {sc + missing:.10f} = 44 ✅")

print("\n" + "="*72)
print("2. Σe_k² 數值分析")
print("="*72)
print(f"Σe_k² = {e2_sum:.10f}")
print(f"×88 = {e2_sum*88:.6f}")
print(f"×44 = {e2_sum*44:.6f}")
print(f"×176 = {e2_sum*176:.6f}")
factor = e2_sum / (4*sin(pi/176)**2)
print(f"Σe_k² / (4sin²(π/176)) = {factor:.10f}")
print("  呢個 = Σ_{m=85,83,...,1} γ_m (奇數 γ 子集)")

odd_g = sum(4*sin(m*pi/176)**2 for m in range(1, 88, 2))
print(f"\n88-site 全奇數 γ (m=1,3,...,87): Σ = {odd_g:.6f} (觀察者 = 88)")
our_g = sum(4*sin((87-2*k)*pi/176)**2 for k in range(1, 44))
print(f"我哋嘅奇數 γ (m=85,...,1): Σ = {our_g:.6f}")
g87 = 4*sin(87*pi/176)**2
print(f"差: γ_87 = 4sin²(87π/176) = {g87:.6f}")
print(f"{our_g:.6f} + γ_87 = {our_g + g87:.6f}")

print("\n" + "="*72)
print("3. 邊集 = 觀察者鏈 minus 最外點")
print("="*72)
print(f"""
  88-site 觀察者 (奇數 γ): m = 1,3,5,...,87  Σ = 88
  
  邊集對應: m = 85,83,...,1  (缺 m=87!)
  γ_87 = 4sin²(87π/176) = 4cos²(π/176) ≈ {4*cos(pi/176)**2:.6f}
  
  Σe_k² = 4sin²(π/176) × Σγ_m(m=1..85 奇數)
        = 4sin²(π/176) × (88 − γ_87)
        = {4*sin(pi/176)**2*(88-4*cos(pi/176)**2):.10f} ✅
""")

print("="*72)
print("4. 邊集嘅完整 88-site 身份")
print("="*72)
print(f"""
  邊 e_k (k=1..43) ↔ 88-site 奇數格點 m = 87−2k = 85,83,...,1
  e_k² = 4sin²(π/176) × γ_m     [γ_m = 4sin²(mπ/176)]
  
  ★ 邊集 = 88-site 觀察者鏈嘅「全部奇數 − 最外點 m=87」
  ★ 43 條邊 = 觀察者鏈嘅「奇數半鏈」(扣咗最大格點)
""")

print("="*72)
print("5. 43+44 = 87 嘅意義")
print("="*72)
print(f"""
  邊集: 43 (奇數 m=1..85)
  self loop: 44 (SYNC)
  總: 87 = 88 − 1
  
  88 = 2×44 = 對偶鏈
  87 = 88 − 1 = 對偶鏈 minus 種子 (1)
  
  ★ 原子指令總數 87 = 觀察者鏈格點數 88 − 種子 1
""")
