#!/usr/bin/env python3
"""
IDCM CMB 完整峰序列 — 結構搜索
================================
峰位置 (Planck 2018 TT): ℓ₁=220.1, ℓ₂=537, ℓ₃=810, ℓ₄=1014

已知: ℓ₁ = 5×44 = 220 (0.05%)
目標: 完整峰序列結構公式

思路: 峰位置 = 44 × N_m, N_m = 有效模式數
N_m = 5.002, 12.205, 18.409, 23.045

整數部分: 5, 12, 18, 23 (差 7, 6, 5 遞減!)
"""
import math
import itertools

phi = (1 + 5**0.5) / 2
phi_inv = 1 / phi
eps = phi_inv / 4
kappa = 1 / 16
Nd = 44
M = 33
B = 4
CY3 = 134

# 峰位置 (Planck 2018 TT)
l_obs = [220.1, 537.0, 810.0, 1014.0]
l_err = [0.5, 2.0, 3.0, 5.0]
N_obs = [l / 44 for l in l_obs]

print("=" * 72)
print("IDCM CMB 完整峰序列 — 結構搜索")
print("=" * 72)

print("\n[1] 數據")
print("-" * 72)
print(f"峰位置: {l_obs}")
print(f"N_m = ℓ_m/44: {[f'{n:.5f}' for n in N_obs]}")
print(f"整數部分: {[int(n) for n in N_obs]}")
print(f"小數部分: {[f'{n-int(n):.4f}' for n in N_obs]}")
diffs = [N_obs[i+1]-N_obs[i] for i in range(3)]
print(f"N 差: {[f'{d:.4f}' for d in diffs]}")
ddiffs = [diffs[i+1]-diffs[i] for i in range(2)]
print(f"二次差: {[f'{d:.4f}' for d in ddiffs]}")
print(f"峰間距 Δℓ: {[f'{l_obs[i+1]-l_obs[i]}' for i in range(3)]}")
print(f"Δℓ/44: {[f'{(l_obs[i+1]-l_obs[i])/44:.4f}' for i in range(3)]}")

print("\n[2] 整數序列分析: 5, 12, 18, 23")
print("-" * 72)
print("差: 7, 6, 5 (每步 -1)")
print("N_int(m) = 5 + 7(m-1) - (m-1)(m-2)/2 = (17m - m² - 6)/2")
for m in range(1, 6):
    N = (17*m - m*m - 6) / 2
    print(f"  m={m}: N_int = {N}")
print("→ 頂點: m=8,9 → N=33 = K_Tree 深度 M! 強結構信號")
print()
print("小數部分: 0.002, 0.205, 0.409, 0.046")
print("m=2,3: 0.205, 0.409 ≈ (m-1)/3 × φ⁻¹ = 0.206, 0.412 ✅")
print("m=4: 0.046 ≈ 1/22 = 1/(N_d/2)?")
print()

print("[3] 候選公式測試 (m=1..4)")
print("-" * 72)
candidates = {}

# A: N_m = N_int + (m-1)φ⁻¹/3
def cand_A(m):
    return (17*m - m*m - 6)/2 + (m-1)*phi_inv/3
candidates["A: N_int + (m-1)φ⁻¹/3"] = cand_A

# B: N_m = N_int + φ⁻¹×(m-1)(4-m)/3  (m=4 時消失)
def cand_B(m):
    return (17*m - m*m - 6)/2 + phi_inv*(m-1)*(4-m)/3
candidates["B: N_int + φ⁻¹(m-1)(4-m)/3"] = cand_B

# C: N_m = N_int + (m-1)(m-2)(m-3)/6 × φ⁻¹? (m≥4 先有)
def cand_C(m):
    return (17*m - m*m - 6)/2 + (m-1)*(m-2)*(m-3)/6 * phi_inv
candidates["C: N_int + C(m-1,3)φ⁻¹"] = cand_C

# D: N_m = 5 + 7(m-1) - C(m-1,2) + φ⁻¹×(m-1)/3 (m≤3), m=4: +1/22
def cand_D(m):
    base = 5 + 7*(m-1) - (m-1)*(m-2)/2
    if m <= 3:
        return base + (m-1)*phi_inv/3
    else:
        return base + 1/22
candidates["D: N_int + φ⁻¹(m-1)/3 (m≤3) + 1/22 (m=4)"] = cand_D

# E: 峰間距 = 7.2, 6.2, 4.58 (二次差 -1, -φ)
def cand_E(m):
    if m == 1:
        return 5.00227
    # Δ: 7.2, 6.2, 6.2-φ=4.582...
    N = 5.00227
    d = 7.2
    for k in range(2, m+1):
        N += d
        d -= 1.0 if k == 2 else phi
    return N
candidates["E: Δ二次差 (-1, -φ)"] = cand_E

# F: 峰位置 = (m-φ_m)×301, φ_m 結構
def cand_F(m):
    # φ_m = φ⁻¹/2 = 0.309 (m=3 完美)
    # 試 φ_m = φ⁻¹×sin(πm/6)?
    phi_m = phi_inv * math.sin(math.pi * m / 6) ** 2
    return (m - phi_m) * 301
candidates["F: (m-φ⁻¹sin²(πm/6))×301"] = cand_F

# G: 峰位置 = 44 × (m² + 4m - (m-1)(m-2)(m-3)/6×?)  
def cand_G(m):
    return 44 * (m*m + 4*m - (m-1)*(m-2)*(m-3)/6 * 3)
candidates["G: 44×(m²+4m-C(m-1,3)×3)"] = cand_G

# H: 峰間距遞減 (7.2, 6.2, 4.64) = 44 × (8-m) + 44×φ⁻¹×g(m)?
def cand_H(m):
    # Δ_m = 7.2, 6.2, 4.64
    # Δ = 8-m + 0.2, 0.2, -0.36?
    if m == 1:
        return 5.00227
    deltas = [7.2, 6.2, 4.64, 2.14, 0.0]
    return 5.00227 + sum(deltas[:m-1])
candidates["H: Δ=[7.2,6.2,4.64,...]"] = cand_H

# I: N_m = -0.643m² + 9.247m - 3.633 (最小二乘 fit)
def cand_I(m):
    return -0.6425*m*m + 9.247*m - 3.6325
candidates["I: 最小二乘二次"] = cand_I

# J: 峰位置 = 44×(F_{m+4} - C(m-1,2))?  F: 5,8,13,21
def cand_J(m):
    F = [1,1,2,3,5,8,13,21,34,55]
    return F[m+4] - (m-1)*(m-2)//2
candidates["J: F_{m+4} - C(m-1,2)"] = cand_J

# K: N_m = 5 + 7(m-1) - C(m-1,2) + φ⁻¹×(m-1)/3 - (m-1)(m-2)(m-3)/6×φ
def cand_K(m):
    base = 5 + 7*(m-1) - (m-1)*(m-2)/2 + (m-1)*phi_inv/3
    return base - (m-1)*(m-2)*(m-3)/6 * phi
candidates["K: A + C(m-1,3)×φ 修正"] = cand_K

# L: N_m = 5×φ^0... 試: N_m = 5 + 7(m-1) - (m-1)(m-2)/2 + φ⁻¹×(m-1)(3-m)/2
def cand_L(m):
    base = 5 + 7*(m-1) - (m-1)*(m-2)/2
    return base + phi_inv*(m-1)*(3-m)/2
candidates["L: N_int + φ⁻¹(m-1)(3-m)/2"] = cand_L

print(f"{'公式':50s} {'ℓ₁':>8s} {'ℓ₂':>8s} {'ℓ₃':>8s} {'ℓ₄':>8s} {'RMS':>8s}")
print("-" * 100)
results = []
for name, fn in candidates.items():
    preds = [44*fn(m) for m in range(1, 5)]
    rms = math.sqrt(sum((preds[i]-l_obs[i])**2 for i in range(4))/4)
    marks = []
    for i in range(4):
        dev = abs(preds[i]-l_obs[i])/l_obs[i]*100
        marks.append(f"{preds[i]:7.1f}({dev:.1f}%)")
    results.append((rms, name, preds, marks))
results.sort()
for rms, name, preds, marks in results:
    print(f"{name:50s} {marks[0]:>8s} {marks[1]:>9s} {marks[2]:>9s} {marks[3]:>9s} RMS={rms:6.1f}")

print()
print("[4] 最佳公式詳細")
print("-" * 72)
best = results[0]
print(f"最佳: {best[1]}")
for i in range(4):
    dev = abs(best[2][i]-l_obs[i])/l_obs[i]*100
    sig = abs(best[2][i]-l_obs[i])/l_err[i]
    print(f"  m={i+1}: 預測 {best[2][i]:.2f} vs {l_obs[i]} → {dev:.2f}% ({sig:.1f}σ)")
