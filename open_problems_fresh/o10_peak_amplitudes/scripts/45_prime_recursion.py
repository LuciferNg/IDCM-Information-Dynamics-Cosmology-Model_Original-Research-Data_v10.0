#!/usr/bin/env python3
"""
O10 45: 質數峰遞歸 — A(p_{j+1}) = A(p_j) × F_j/F_{j+1}
=======================================================
質數峰順序: p_1=1, p_2=2, p_3=3, p_4=5, p_5=7
高度: A(1)=1, A(2)=0.4434, A(3)=0.4389, A(5)=0.2143, A(7)=0.1414

觀察連續比:
  A(2)/A(1) = 0.4434 ≈ 3ε = 0.4635 (-4.3%)
  A(3)/A(2) = 0.9899 ≈ 1
  A(5)/A(3) = 0.4883 ≈ 1/2
  A(7)/A(5) = 0.6598 ≈ 2/3

結構: A(p_{j+1}) = A(p_j) × r_j
  r_1 = 3ε (質數 1→2)
  r_2 = 1 (質數 2→3)
  r_3 = 1/2 (質數 3→5)
  r_4 = 2/3 (質數 5→7)

r_j 模式: 3ε, 1, 1/2, 2/3
  = 3ε, F₁/F₁, F₂/F₃, F₃/F₄?
  或者: 3ε, F_{j-1}/F_j?
"""
import numpy as np, math

phi = (1 + 5**0.5) / 2
eps = phi**-1/4
F = [1, 1, 2, 3, 5, 8, 13]

# 質數峰
A = {1: 1.0000, 2: 0.4434, 3: 0.4389, 5: 0.2143, 7: 0.1414}
primes = [1, 2, 3, 5, 7]

print("=" * 72)
print("質數峰遞歸 r_j = A(p_{j+1})/A(p_j)")
print("=" * 72)
r = {}
for j in range(len(primes)-1):
    pj, pj1 = primes[j], primes[j+1]
    r[j] = A[pj1]/A[pj]
    print(f"  r_{j+1} (質數 {pj}→{pj1}): {r[j]:.4f}")

print()
print("r_j 候選結構:")
print(f"  r₁ = {r[0]:.4f} vs 3ε = {3*eps:.4f}")
print(f"  r₂ = {r[1]:.4f} vs 1 = {1.0:.4f}")
print(f"  r₃ = {r[2]:.4f} vs 1/2 = {0.5:.4f}")
print(f"  r₄ = {r[3]:.4f} vs 2/3 = {2/3:.4f}")
print()

# Fibonacci 連續比表
print("Fibonacci 連續比 F_k/F_{k+1}:")
for k in range(1, 6):
    print(f"  F_{k}/F_{k+1} = {F[k-1]}/{F[k]} = {F[k-1]/F[k]:.4f}")

print()
print("匹配:")
print(f"  r₂ = 1 = F₁/F₁ (或 1)")
print(f"  r₃ = 1/2 = F₂/F₃")
print(f"  r₄ = 2/3 = F₃/F₄")
print()

# 完整遞歸假設: r_1 = 3ε, r_j = F_{j-1}/F_j (j≥2)
print("假設: A(p₁) = 1, A(p₂) = 3ε, A(p_{j+1}) = A(p_j) × F_{j-1}/F_j (j≥2)")
pred = {1: 1.0}
pred[2] = 3*eps
for j in range(2, 5):
    pred[primes[j]] = pred[primes[j-1]] * F[j-2]/F[j-1]

for p in primes:
    if p in pred:
        dev = (A[p]-pred[p])/pred[p]*100
        print(f"  A({p}): pred {pred[p]:.4f} vs obs {A[p]:.4f} → {dev:+.2f}%")

print()
print("注意: A(2) = 0.4434 vs 3ε = 0.4635 → -4.3% (ISW?)")
print("A(3) pred = 3ε×1 = 0.4635 vs 0.4389 → -5.3%")
print()

# 修正: A(2), A(3) 都受 ISW? 定係本身 = 3ε×0.95?
# 或者: A(2), A(3) 平均 = 3ε 先啱 (0.4412 vs 0.4635 = -4.8%)
print("另一假設: 質數對 (2,3) 平均 = 3ε, (5,7) 平均 = 3εφ⁻²")
P1 = (A[2]+A[3])/2
P2 = (A[5]+A[7])/2
print(f"  P₁ = {P1:.4f} vs 3ε = {3*eps:.4f} ({-4.8}%)")
print(f"  P₂ = {P2:.4f} vs 3εφ⁻² = {3*eps*phi**-2:.4f} (+{0.45}%)")
print()
print("→ 孿生質數對 (2,3) 同 (5,7) 先係 Fibonacci 階梯嘅基本單元!")
print("→ 峰高 = P_m × 對內分配 (1:1 同 2:3)")
print()

# 對內分配
print("對內分配:")
print("  (2,3): A2:A3 = 0.4434:0.4389 = 1.010:1 ≈ 1:1")
print("  (5,7): A5:A7 = 0.2143:0.1414 = 1.515:1 ≈ 3:2")
print()
print("F₁:F₂ = 1:1 ✅ (對 1)")
print("F₃:F₄ = 2:3 ❌ (對 2 係 3:2 反轉)")
print("F₄:F₅ = 3:5 ❌")
print()
print("對 2 係 3:2 = F₄:F₃ (反轉)")
print("或者: A5:A7 = 3:2, 即 A5 大過 A7 1.5 倍")
