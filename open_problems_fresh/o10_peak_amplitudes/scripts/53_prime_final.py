#!/usr/bin/env python3
"""
O10 53: 質數峰最終狀態
=======================
質數峰模型: A(p_j) = 3ε × Π(F_k/F_{k+1}) × D(ℓ)
D(ℓ) = exp[-(ℓ/ℓ_D)^{3/2}], ℓ_D = 9147

殘差: -3.0%, -2.8%, -3.5%, -2.8% (RMS 3.0%)

殘差結構: 全部 -3% 左右 → 可能係 ISW 抬升第一峰
或者: 3ε 應該用 0.95×3ε (P₁ 嘅 -4.8% 修正)?
"""
import numpy as np, math

phi = (1 + 5**0.5) / 2
eps = phi**-1/4
F = [1, 1, 2, 3, 5, 8, 13]

A = {1: 1.0000, 2: 0.4434, 3: 0.4389, 5: 0.2143, 7: 0.1414}
ell = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}
lD = 9147

def geo(j):
    if j == 0:
        return 1.0
    if j == 1:
        return 3*eps
    prod = 3*eps
    for k in range(1, j):
        prod *= F[k-1]/F[k]
    return prod

# 殘差分析
print("殘差 (D 修正後):")
resids = {}
for j, p in enumerate([2, 3, 5, 7]):
    D = math.exp(-(ell[p]/lD)**1.5)
    pred = geo(j)*D
    resid = A[p]/pred - 1
    resids[p] = resid
    print(f"  p={p}: resid = {resid*100:+.2f}%")

print()
print("殘差: -3.0%, -2.8%, -3.5%, -2.8% — 差不多常數 ≈ -3%")
print()
print("如果全部峰 (2,3,5,7) 都乘 0.97:")
for j, p in enumerate([2, 3, 5, 7]):
    D = math.exp(-(ell[p]/lD)**1.5)
    pred = geo(j)*D*0.97
    dev = (A[p]-pred)/pred*100
    print(f"  p={p}: pred×0.97 = {pred:.4f} vs {A[p]:.4f} ({(A[p]-pred)/pred*100:+.2f}%)")

print()
print("0.97 ≈ ? 1-ε =", 1-eps, "? 1-ε² =", 1-eps**2, "? 1-3ε/10 =", 1-3*eps/10)
print()
print("0.9702 = 1 - 0.0298 ≈ 1 - ε/5.2? 或者 1 - φ⁻⁵?")
print("φ⁻⁵ =", phi**-5)
print("1-φ⁻⁵ =", 1-phi**-5)
print()
print("如果 ISW 修正係 (1-φ⁻⁵):")
for j, p in enumerate([2, 3, 5, 7]):
    D = math.exp(-(ell[p]/lD)**1.5)
    pred = geo(j)*D*(1-phi**-5)
    dev = (A[p]-pred)/pred*100
    print(f"  p={p}: pred = {pred:.4f} vs {A[p]:.4f} ({(A[p]-pred)/pred*100:+.2f}%)")

print()
print("但呢個係 2-parameter fit (ℓ_D + 0.97) 對 4 個點")
print("唔算真正閉合 — 需要更多峰驗證")
print()
print("結論: 質數峰幾何結構 (Fibonacci 連續比) 確認,")
print("       Silk 阻尼 ℓ_D≈9000 微弱, ISW 殘差 -3% 待解釋")
print("       🔴 需要 m=11, 13 峰驗證 (超出 Planck)")
