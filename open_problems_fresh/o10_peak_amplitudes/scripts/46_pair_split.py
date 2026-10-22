#!/usr/bin/env python3
"""
O10 46: 對內分配 — 3:2 反轉 Fibonacci 驗證
===========================================
對 1 (2,3): 1:1 (F₁:F₂)
對 2 (5,7): 3:2 (F₄:F₃ 反轉?)

A(5) = P₂ × 3/5, A(7) = P₂ × 2/5?
"""
import numpy as np, math

phi = (1 + 5**0.5) / 2
eps = phi**-1/4
F = [1, 1, 2, 3, 5, 8, 13]

# 質數峰
A = {1: 1.0000, 2: 0.4434, 3: 0.4389, 5: 0.2143, 7: 0.1414}

P1 = 3*eps
P2 = 3*eps*phi**-2

print("=" * 72)
print("對內分配驗證")
print("=" * 72)

# 對 1: 1:1
A2p = P1/2
A3p = P1/2
print(f"對 1 (1:1): A2 pred = {A2p:.4f} vs {A[2]:.4f} ({(A[2]-A2p)/A2p*100:+.1f}%)")
print(f"           A3 pred = {A3p:.4f} vs {A[3]:.4f} ({(A[3]-A3p)/A3p*100:+.1f}%)")

# 對 2: 3:2 (A5:A7 = 3:2)
A5p = P2*3/5
A7p = P2*2/5
print(f"對 2 (3:2): A5 pred = {A5p:.4f} vs {A[5]:.4f} ({(A[5]-A5p)/A5p*100:+.1f}%)")
print(f"            A7 pred = {A7p:.4f} vs {A[7]:.4f} ({(A[7]-A7p)/A7p*100:+.1f}%)")

print()
print("3:2 = F₄:F₃? F₄=3, F₃=2 ✓")
print("1:1 = F₁:F₂? F₁=1, F₂=1 ✓")
print()
print("對 m 分配 = F_{2m}:F_{2m-1}?")
print("  對 1: F₂:F₁ = 1:1 ✓")
print("  對 2: F₄:F₃ = 3:2 ✓")
print()
print("🎯 對 m 內: 峰 2m-1 (前) : 峰 2m (後) = F_{2m}:F_{2m-1}!")
print("  即: A(峰_{2m-1}) = P_m × F_{2m}/(F_{2m}+F_{2m-1})")
print("      A(峰_{2m})   = P_m × F_{2m-1}/(F_{2m}+F_{2m-1})")

# 完整驗證
print()
print("完整驗證:")
for m, (a, b, P_m) in {1: (2, 3, P1), 2: (5, 7, P2)}.items():
    F_hi = F[2*m]       # F₂, F₄
    F_lo = F[2*m-1]     # F₁, F₃
    Aa = P_m * F_hi/(F_hi+F_lo)
    Ab = P_m * F_lo/(F_hi+F_lo)
    print(f"  對{m}: 峰{a} = P_{m}×F_{2*m}/(F_{2*m}+F_{2*m-1}) = {Aa:.4f} vs {A[a]:.4f}")
    print(f"        峰{b} = P_{m}×F_{2*m-1}/(F_{2*m}+F_{2*m-1}) = {Ab:.4f} vs {A[b]:.4f}")

print()
print("但注意: P₁, P₂ 本身有偏差 (-4.8%, +0.45%)")
print("用 obs 平均重算:")
P1_obs = (A[2]+A[3])/2
P2_obs = (A[5]+A[7])/2
for m, (a, b, P_obs) in {1: (2, 3, P1_obs), 2: (5, 7, P2_obs)}.items():
    F_hi = F[2*m]
    F_lo = F[2*m-1]
    Aa = P_obs * F_hi/(F_hi+F_lo)
    Ab = P_obs * F_lo/(F_hi+F_lo)
    print(f"  對{m}: 峰{a} pred {Aa:.4f} vs {A[a]:.4f} ({(A[a]-Aa)/Aa*100:+.2f}%)")
    print(f"        峰{b} pred {Ab:.4f} vs {A[b]:.4f} ({(A[b]-Ab)/Ab*100:+.2f}%)")
