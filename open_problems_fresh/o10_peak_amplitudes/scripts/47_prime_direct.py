#!/usr/bin/env python3
"""
O10 47: 質數峰直接結構 — A(p) vs p
===================================
質數峰: p ∈ {1,2,3,5,7}, A = 1.0, 0.4434, 0.4389, 0.2143, 0.1414
ℓ = 221, 527, 815, 1121, 1409

直接測試:
  A(p) vs 1/p?
  A(p) vs φ^{-p}?
  A(p) vs F_p?
  A(p) vs (p-1)/p?
  A(p) vs 質數間隔?
"""
import numpy as np, math

phi = (1 + 5**0.5) / 2
eps = phi**-1/4
F = [1, 1, 2, 3, 5, 8, 13]

A = {1: 1.0000, 2: 0.4434, 3: 0.4389, 5: 0.2143, 7: 0.1414}
ell = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}

print("=" * 72)
print("質數峰直接結構")
print("=" * 72)

print("\n1. A(p) vs 1/p:")
for p in [1, 2, 3, 5, 7]:
    print(f"  p={p}: A={A[p]:.4f}, 1/p={1/p:.4f}, A×p={A[p]*p:.4f}")

print("\n2. A(p) vs φ^{-p}:")
for p in [1, 2, 3, 5, 7]:
    v = phi**(-p)
    print(f"  p={p}: φ^-p={v:.4f}, A/φ^-p = {A[p]/v:.4f}")

print("\n3. A(p) vs ℓ^{-1}:")
for p in [2, 3, 5, 7]:
    v = 221/ell[p]
    print(f"  p={p}: ℓ₁/ℓ_p={v:.4f}, A(p)/v={A[p]/v:.4f}")

print("\n4. A(p) vs ℓ^{-2}:")
for p in [2, 3, 5, 7]:
    v = (221/ell[p])**2
    print(f"  p={p}: (ℓ₁/ℓ_p)²={v:.4f}, A(p)/v={A[p]/v:.4f}")

print("\n5. A(p) vs sin/cos 結構 (K_Chain):")
for p in [1, 2, 3, 5, 7]:
    n = 5*p  # 質數×5?
    if n <= 44:
        c = math.cos(math.pi*n/88)
        print(f"  p={p}: cos(π·{n}/88) = {c:.4f}, A={A[p]:.4f}")

print("\n6. 質數間隔 (prime gaps):")
gaps = []
prev = 1
for p in [2, 3, 5, 7]:
    gaps.append(p - prev)
    prev = p
print(f"  gaps: {gaps} (質數間隔: 1, 1, 2, 2)")

print("\n7. A(p) vs F_p (Fibonacci):")
for p in [1, 2, 3, 5, 7]:
    print(f"  p={p}: F_{p}={F[p-1]}, A={A[p]:.4f}, A×F_p={A[p]*F[p-1]:.4f}")

print("\n8. A(p) × p:")
for p in [1, 2, 3, 5, 7]:
    print(f"  p={p}: A×p = {A[p]*p:.4f}")

print("\n9. A(p) / 3ε:")
for p in [1, 2, 3, 5, 7]:
    print(f"  p={p}: A/3ε = {A[p]/(3*eps):.4f}")

print()
print("A/3ε: 2.157, 0.957, 0.947, 0.462, 0.305")
print("注意 p=1 唔同 (A=1 基準)")
print()
print("如果 A(p)/3ε = 2×p 嘅函數?")
print("  0.957 (p=2), 0.947 (p=3), 0.462 (p=5), 0.305 (p=7)")
print("  2/p: 1.0, 0.667, 0.4, 0.286")
print("  A/3ε vs 2/p: 0.957/1.0, 0.947/0.667, 0.462/0.4, 0.305/0.286")
print("  = 0.957, 1.42, 1.16, 1.07 — 唔係常數")
print()
print("φ^{-(p-1)}: 1, 0.618, 0.382, 0.146, 0.0557")
print("A/φ^{-(p-1)}: 1, 0.717, 1.15, 1.47, 2.54 — 遞增!")
