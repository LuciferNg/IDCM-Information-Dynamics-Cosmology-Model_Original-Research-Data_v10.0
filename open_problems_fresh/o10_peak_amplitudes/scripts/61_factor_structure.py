#!/usr/bin/env python3
"""
O10 61: 0.970 因子結構鎖定 — M/(M+1) = 33/34 驗證
=================================================
候選: 0.9702 ≈ M/(M+1) = 33/34 = 0.970588 (M = K_Tree 層數, 34 = F₉)

完整公式: A(p_j) = 3ε × Π_{k=1}^{j-1}(F_k/F_{k+1}) × D(ℓ_p) × M/(M+1)
"""
import numpy as np, math

phi = (1 + 5**0.5) / 2
eps = phi**-1/4
F = [1, 1, 2, 3, 5, 8, 13]
M = 33  # K_Tree 層數
lD = 9147  # Silk 阻尼尺度 (之前 fit)

A = {2: 0.4434, 3: 0.4389, 5: 0.2143, 7: 0.1414}
ell = {2: 527, 3: 815, 5: 1121, 7: 1409}

def geo(j):
    prod = 3*eps
    for k in range(1, j):
        prod *= F[k-1]/F[k]
    return prod

print("=" * 72)
print("0.970 因子結構: M/(M+1) = 33/34")
print("=" * 72)

# 對比 0.9702 (fit) vs 33/34 (結構)
print(f"0.9702 (fit)  vs  M/(M+1) = {M/(M+1):.6f}")
print(f"偏差: {(M/(M+1)-0.9702)/0.9702*100:+.4f}%")
print(f"1-1/34 = {1-1/34:.6f}, 1-1/33 = {1-1/33:.6f}")
print()

# 用 M/(M+1) 驗證
print("完整模型 A(p_j) = 3ε·Π(F_k/F_{k+1})·D(ℓ)·M/(M+1):")
rms = 0
for j, p in enumerate([2, 3, 5, 7], start=1):
    D = math.exp(-(ell[p]/lD)**1.5)
    pred = geo(j)*D*M/(M+1)
    dev = (A[p]-pred)/pred*100
    rms += dev**2
    print(f"  p={p}: pred = {pred:.4f} vs {A[p]:.4f} ({(A[p]-pred)/pred*100:+.2f}%)")
print(f"  RMS = {math.sqrt(rms/4):.2f}%")
print()

# 對比: 冇 M/(M+1) 因子 (只用 0.97 fit)
print("對比 (冇因子, 純幾何×Silk):")
rms0 = 0
for j, p in enumerate([2, 3, 5, 7], start=1):
    D = math.exp(-(ell[p]/lD)**1.5)
    pred = geo(j)*D
    dev = (A[p]-pred)/pred*100
    rms0 += dev**2
    print(f"  p={p}: pred = {pred:.4f} vs {A[p]:.4f} ({(A[p]-pred)/pred*100:+.2f}%)")
print(f"  RMS = {math.sqrt(rms0/4):.2f}%")
print()

# 用 33/34 重 fit lD (2 參數: lD + M/(M+1) 結構)
print("=" * 72)
print("用 M/(M+1) 重 fit ℓ_D")
print("=" * 72)
from scipy.optimize import minimize_scalar

def rms_lD(lD_test):
    rms = 0
    for j, p in enumerate([2, 3, 5, 7], start=1):
        D = math.exp(-(ell[p]/lD_test)**1.5)
        pred = geo(j)*D*M/(M+1)
        rms += ((A[p]-pred)/pred)**2
    return math.sqrt(rms/4)

res = minimize_scalar(rms_lD, bounds=(3000, 20000), method='bounded')
lD_opt = res.x
print(f"最佳 ℓ_D = {lD_opt:.0f} (RMS = {res.fun*100:.2f}%)")
for j, p in enumerate([2, 3, 5, 7], start=1):
    D = math.exp(-(ell[p]/lD_opt)**1.5)
    pred = geo(j)*D*M/(M+1)
    dev = (A[p]-pred)/pred*100
    print(f"  p={p}: pred = {pred:.4f} vs {A[p]:.4f} ({(A[p]-pred)/pred*100:+.2f}%)")

print()
print("M/(M+1) = 33/34 = 0.9706 vs fit 0.9702: 偏差 0.04%")
print("33/34 有完整 IDCM 結構: M = K_Tree 層數, M+1 = 34 = F₉")
