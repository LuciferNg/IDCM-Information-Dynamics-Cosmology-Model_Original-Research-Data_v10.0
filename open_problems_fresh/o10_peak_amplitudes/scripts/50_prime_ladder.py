#!/usr/bin/env python3
"""
O10 50: 質數峰對數間隔分析
===========================
ln(A): p=1: 0, p=2: -0.813, p=3: -0.824, p=5: -1.540, p=7: -1.956

ln(A) vs p?
ln(A) vs ℓ?
ln(A) vs 質數階 j (1,2,3,4,5)?
"""
import numpy as np, math

phi = (1 + 5**0.5) / 2
eps = phi**-1/4

A = {1: 1.0000, 2: 0.4434, 3: 0.4389, 5: 0.2143, 7: 0.1414}
ell = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}
primes = [1, 2, 3, 5, 7]

lnA = {p: math.log(A[p]) for p in primes}
print("ln(A):")
for p in primes:
    print(f"  p={p}: lnA = {lnA[p]:.4f}")

print()
print("ln(A) vs 質數階 j (j=1..5):")
lnA_j = [lnA[p] for p in primes]
print(f"  lnA_j = {[f'{v:.4f}' for v in lnA_j]}")
# 差分
diffs = [lnA_j[i+1]-lnA_j[i] for i in range(4)]
print(f"  差分: {[f'{v:.4f}' for v in diffs]}")

print()
print("差分: -0.813, -0.011, -0.717, -0.416")
print("有趣: -0.813 ≈ ln(0.443), -0.011 ≈ 0, -0.717, -0.416")
print()
print("差分 vs Fibonacci 比對數:")
import math as m
print(f"  ln(1/2) = {m.log(0.5):.4f}")
print(f"  ln(2/3) = {m.log(2/3):.4f}")
print(f"  ln(3/5) = {m.log(3/5):.4f}")
print(f"  ln(φ⁻¹) = {m.log(phi**-1):.4f}")
print(f"  ln(φ⁻²) = {m.log(phi**-2):.4f}")
print(f"  ln(3ε) = {m.log(3*eps):.4f}")
print()
print("差分匹配:")
print(f"  d₁ = -0.813 vs ln(3ε) = {m.log(3*eps):.4f} ({-0.813 - m.log(3*eps):+.4f})")
print(f"  d₂ = -0.011 vs ln(1) = 0")
print(f"  d₃ = -0.717 vs ln(1/2) = {m.log(0.5):.4f} ({-0.717 - m.log(0.5):+.4f})")
print(f"  d₄ = -0.416 vs ln(2/3) = {m.log(2/3):.4f} ({-0.416 - m.log(2/3):+.4f})")
print()
print("d₁ 比 ln(3ε) 深 -0.045 (ISW 影響第一峰)")
print("d₂ ≈ 0 (峰2→3 無衰減)")
print("d₃ ≈ ln(1/2) 偏深 -0.024")
print("d₄ ≈ ln(2/3) 偏深 +0.021")
print()
print("結構: 質數峰遞減 = 3ε(起始) × 1 × 1/2 × 2/3 ...")
print("      即 A(p_{j+1})/A(p_j) = F_j/F_{j+1} (Fibonacci 連續比)")

# 用質數階做精確擬合
print()
print("=" * 72)
print("質數階模型: A(p_j) = 3ε·Π_{k=1}^{j-1} F_k/F_{k+1}")
print("=" * 72)
F = [1, 1, 2, 3, 5, 8, 13]
pred = {}
prod = 1.0
for j, p in enumerate(primes):
    if j == 0:
        pred[p] = 1.0
    elif j == 1:
        pred[p] = 3*eps
    else:
        prod *= F[j-2]/F[j-1]
        pred[p] = 3*eps*prod
    print(f"  p={p} (j={j}): pred {pred[p]:.4f} vs {A[p]:.4f} ({(A[p]-pred[p])/pred[p]*100:+.2f}%)")

print()
print("但 p=1 (j=0) 係基準 1, 唔係 3ε")
print("p=2 (j=1) = 3ε, p=3 (j=2) = 3ε×1, p=5 (j=3) = 3ε×1/2, p=7 (j=4) = 3ε×1/2×2/3")
print()
print("A(5) = 3ε×1/2 = 0.2318 vs 0.2143 (-7.5%)")
print("A(7) = 3ε×1/2×2/3 = 0.1545 vs 0.1414 (-8.5%)")
print()
print("系統性 -7~8%: 可能係 ISW/低 ℓ 效應嘅殘留")
print("或者質數 5,7 有額外 0.92-0.93 因子")
