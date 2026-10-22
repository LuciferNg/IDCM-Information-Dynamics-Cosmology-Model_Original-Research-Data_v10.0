#!/usr/bin/env python3
"""
O10 52: 質數峰 + Silk — 修正版
===============================
模型: A(p_j) = 3ε × Π_{k=1}^{j-1}(F_k/F_{k+1}) × D(ℓ_p)

質數峰: p_1=1, p_2=2, p_3=3, p_4=5, p_5=7
幾何項:
  j=0 (p=1): 1.0 (基準)
  j=1 (p=2): 3ε
  j=2 (p=3): 3ε × F₁/F₂ = 3ε × 1
  j=3 (p=5): 3ε × F₁/F₂ × F₂/F₃ = 3ε × 1/2
  j=4 (p=7): 3ε × 1/2 × F₃/F₄ = 3ε × 1/2 × 2/3
"""
import numpy as np, math

phi = (1 + 5**0.5) / 2
eps = phi**-1/4
F = [1, 1, 2, 3, 5, 8, 13]

A = {1: 1.0000, 2: 0.4434, 3: 0.4389, 5: 0.2143, 7: 0.1414}
ell = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}
primes = [1, 2, 3, 5, 7]

# 幾何項
def geo(j):
    if j == 0:
        return 1.0
    if j == 1:
        return 3*eps
    prod = 3*eps
    # k=1..j-1: F_k/F_{k+1}
    for k in range(1, j):
        prod *= F[k-1]/F[k]
    return prod

print("=" * 72)
print("質數峰幾何項 (Fibonacci 階梯)")
print("=" * 72)
geo_vals = {}
for j, p in enumerate(primes):
    g = geo(j)
    geo_vals[p] = g
    D_implied = A[p]/g
    print(f"  p={p} (j={j}): geo = {g:.4f}, A = {A[p]:.4f}, D_implied = {D_implied:.4f}")

print()
print("D_implied: p=2: 0.957, p=3: 0.947, p=5: 0.925, p=7: 0.915")
print("遞減 — Silk 阻尼尾!")
print()

# 擬合 D(ℓ) = exp[-(ℓ/ℓ_D)^{3/2}]
ells = np.array([ell[p] for p in [2, 3, 5, 7]])
Ds = np.array([A[p]/geo_vals[p] for p in [2, 3, 5, 7]])
lnD = np.log(Ds)
l15 = ells**1.5
coeff = np.polyfit(l15, lnD, 1)
slope, intercept = coeff
lD = (-1/slope)**(2/3)
print(f"擬合: ln(D) = {slope:.6f}·ℓ^1.5 + {intercept:.4f}")
print(f"ℓ_D = {lD:.0f}")
print()

# 完整模型
print("完整模型 A(p) = geo × D(ℓ):")
rms = 0
for p in [2, 3, 5, 7]:
    D = math.exp(-(ell[p]/lD)**1.5)
    pred = geo_vals[p]*D
    dev = (A[p]-pred)/pred*100
    rms += dev**2
    print(f"  p={p}: pred = {pred:.4f} vs {A[p]:.4f} ({(A[p]-pred)/pred*100:+.2f}%)")
print(f"  RMS = {math.sqrt(rms/4):.2f}%")
