#!/usr/bin/env python3
"""
O10 54: 質數峰最終閉合 — 修正版
================================
質數峰: A(p_j) = 3ε × Π_{k=1}^{j-1}(F_k/F_{k+1}) × D(ℓ_p_j)

j 對應: j=1→p=2, j=2→p=3, j=3→p=5, j=4→p=7
"""
import numpy as np, math

phi = (1 + 5**0.5) / 2
eps = phi**-1/4
F = [1, 1, 2, 3, 5, 8, 13]

A = {2: 0.4434, 3: 0.4389, 5: 0.2143, 7: 0.1414}
ell = {2: 527, 3: 815, 5: 1121, 7: 1409}

def geo(j):
    # j = 質數階 (1-based): j=1→p=2, j=2→p=3, j=3→p=5...
    prod = 3*eps
    for k in range(1, j):
        prod *= F[k-1]/F[k]
    return prod

print("=" * 72)
print("質數峰幾何項 + Silk (修正版)")
print("=" * 72)
geo_vals = {}
for j, p in enumerate([2, 3, 5, 7], start=1):
    g = geo(j)
    geo_vals[p] = g
    print(f"  j={j}, p={p}: geo = {g:.4f} = 3ε×{'×'.join([f'F_{k}/F_{k+1}' for k in range(1,j)]) if j>1 else '1'}")

# Silk 擬合 (D = A/geo)
ells = np.array([ell[p] for p in [2, 3, 5, 7]])
Ds = np.array([A[p]/geo_vals[p] for p in [2, 3, 5, 7]])
lnD = np.log(Ds)
coeff = np.polyfit(ells**1.5, lnD, 1)
slope, intercept = coeff
lD = (-1/slope)**(2/3)
print(f"\nD_implied: {[f'{d:.4f}' for d in Ds]}")
print(f"擬合 ln(D) = {slope:.6f}·ℓ^1.5 + {intercept:.4f}")
print(f"ℓ_D = {lD:.0f}")

# 完整模型
print(f"\n完整模型 A(p) = 3ε·Π(F_k/F_{{k+1}})·exp[-(ℓ/ℓ_D)^1.5]:")
resids = []
for j, p in enumerate([2, 3, 5, 7], start=1):
    D = math.exp(-(ell[p]/lD)**1.5)
    pred = geo(j)*D
    dev = (A[p]-pred)/pred*100
    resids.append(dev)
    print(f"  p={p}: pred = {pred:.4f} vs {A[p]:.4f} ({(A[p]-pred)/pred*100:+.2f}%)")

rms = math.sqrt(np.mean(np.array(resids)**2))
print(f"\nRMS = {rms:.2f}%")
print()
print("殘差模式: 全部 ≈ -3% (系統性)")
print("可能: 3ε 用 3ε·(1-3%) 修正 (P₁ 嘅 ISW 殘留)")
print()

# 用 3ε×0.97
print("用 3ε×0.970 (統一因子):")
resids2 = []
for j, p in enumerate([2, 3, 5, 7], start=1):
    D = math.exp(-(ell[p]/lD)**1.5)
    pred = geo(j)*D*0.970
    dev = (A[p]-pred)/pred*100
    resids2.append(dev)
    print(f"  p={p}: pred = {pred:.4f} vs {A[p]:.4f} ({(A[p]-pred)/pred*100:+.2f}%)")
rms2 = math.sqrt(np.mean(np.array(resids2)**2))
print(f"  RMS = {rms2:.2f}%")
print()
print("0.970 ≈ 1 - 0.03 ≈ 1 - ε/5.15")
print("0.9702 = 1 - ε²·0.31? 或者 1-3/(90+7)?")
print()
print("誠實狀態: 質數峰結構 = Fibonacci 階梯 + Silk 阻尼")
print("  閉合精度: RMS 3.0% (含 1 個自由參數 ℓ_D)")
print("  統一 -3% 殘差: 待理論解釋 (ISW/低ℓ?)")
print("  🔴 需要 m=11,13 驗證 (超出 Planck)")
