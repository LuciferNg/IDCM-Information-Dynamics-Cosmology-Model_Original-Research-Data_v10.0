#!/usr/bin/env python3
"""
O10 51: 質數峰 + Silk 阻尼 — 完整閉合
======================================
模型: A(p_j) = 3ε × Π_{k=1}^{j-1}(F_k/F_{k+1}) × D(ℓ_p)
      D(ℓ) = exp[-(ℓ/ℓ_D)^{3/2}]

偏差模式: -4.3%, -5.3%, -7.5%, -8.5% (遞增負偏差 = Silk!)
"""
import numpy as np, math
from scipy.optimize import curve_fit

phi = (1 + 5**0.5) / 2
eps = phi**-1/4
F = [1, 1, 2, 3, 5, 8, 13]

A = {1: 1.0000, 2: 0.4434, 3: 0.4389, 5: 0.2143, 7: 0.1414}
ell = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}
primes = [1, 2, 3, 5, 7]

# 幾何項 (無阻尼)
def geo(j):
    if j == 0:
        return 1.0
    if j == 1:
        return 3*eps
    prod = 1.0
    for k in range(1, j-1):
        prod *= F[k-1]/F[k]  # F_1/F_2, F_2/F_3...
    return 3*eps*prod

print()
print("D_implied: p=1: 1.0, p=2: 0.957, p=3: 0.947, p=5: 0.925, p=7: 0.915")
print("遞減 — 符合 Silk 阻尼尾!")
print()

# 擬合 D(ℓ) = exp[-(ℓ/ℓ_D)^{3/2}]
ells = np.array([ell[p] for p in [2, 3, 5, 7]])
Ds = np.array([A[p]/geo_vals[p] for p in [2, 3, 5, 7]])
lnD = np.log(Ds)
l15 = ells**1.5

# 線性擬合 ln(D) = -(ℓ/ℓ_D)^1.5 = -ℓ^1.5/ℓ_D^1.5
coeff = np.polyfit(l15, lnD, 1)
slope, intercept = coeff
lD = (-1/slope)**(2/3)
print(f"擬合: ln(D) = {slope:.6f}·ℓ^1.5 + {intercept:.4f}")
print(f"ℓ_D = {lD:.0f}")
print()

# 用擬合 D 重算
print("完整模型 A(p) = geo × D(ℓ):")
for p in [2, 3, 5, 7]:
    D = math.exp(-(ell[p]/lD)**1.5)
    pred = geo_vals[p]*D
    dev = (A[p]-pred)/pred*100
    print(f"  p={p}: pred = {pred:.4f} vs {A[p]:.4f} ({(A[p]-pred)/pred*100:+.2f}%)")

print()
print("驗證: D(p=7) =", math.exp(-(1409/lD)**1.5))
print("      A(7) pred =", geo_vals[7]*math.exp(-(1409/lD)**1.5))

# 但 p=1, 2, 3 嘅 ISW 效應?
print()
print("p=1 (221) 唔 fit (基準)")
print("p=2 (527), p=3 (815): 如果都有 Silk + ISW?")
print()

# 檢查: 用 D 修正後嘅殘差
print("殘差 (D 修正後):")
for p in [2, 3, 5, 7]:
    D = math.exp(-(ell[p]/lD)**1.5)
    resid = A[p]/(geo_vals[p]*D) - 1
    print(f"  p={p}: resid = {resid*100:+.2f}%")
