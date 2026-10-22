#!/usr/bin/env python3
"""
O10 07: Fibonacci 階梯 — 完整閉合驗證 + 偏差分析
================================================
核心公式: P_m = 3ε × F_m × φ^(-2(m-1))
  簡併對平均振幅 P_m = (A_{2m} + A_{2m+1})/2

驗證基準:
  1. CAMB lensed @ IDCM 峰位 (高解析度)
  2. Planck binned @ 自動峰位 (ground truth)
  3. CAMB lensed @ 自動峰位 (獨立讀法)
"""
import numpy as np, math, json, os

phi = (1 + 5**0.5) / 2
phi_inv = 1/phi
eps = phi_inv/4
F = [1, 1, 2, 3, 5, 8, 13]

def S_theory(m):
    """Fibonacci 階梯結構因子"""
    return F[m-1] * phi_inv**(2*(m-1))

def P_theory(m):
    return 3*eps * S_theory(m)

print("=" * 72)
print("Fibonacci 階梯: P_m = 3ε × F_m × φ^(-2(m-1))")
print("=" * 72)
print(f"{'m':>2} | {'F_m':>3} | {'φ^(-2(m-1))':>12} | {'S_th':>8} | {'3ε·S_th':>9}")
print("-" * 72)
for m in range(1, 5):
    print(f"{m:>2} | {F[m-1]:>3} | {phi_inv**(2*(m-1)):>12.5f} | {S_theory(m):>8.5f} | {P_theory(m):>9.5f}")

# ============ 基準 1: CAMB lensed @ IDCM 峰位 ============
print()
print("=" * 72)
print("基準 1: CAMB lensed @ IDCM 峰位")
print("=" * 72)
A_idcm = {1: 1.0, 2: 0.4523, 3: 0.4430, 4: 0.1820, 5: 0.1839, 6: 0.1282, 7: 0.1423}
for m in range(1, 4):
    P_obs = (A_idcm[2*m] + A_idcm[2*m+1])/2
    P_th = P_theory(m)
    dev = (P_obs - P_th)/P_th*100
    D = P_obs/P_th
    print(f"  P_{m} = {P_obs:.4f} | 理論 {P_th:.4f} | 偏差 {dev:+.3f}% | D={D:.4f}")

# ============ 基準 2: Planck binned @ 自動峰位 ============
print()
print("=" * 72)
print("基準 2: Planck binned @ 自動峰位 (ground truth)")
print("=" * 72)
# 自動峰: ℓ=221(5816), 527(2579), 815(2553), 1121(1246), 1409(822)
# 誤差: 165, 49, 39, 18, 13
D_pl = {1: 5816, 2: 2579, 3: 2553, 4: 1246, 5: 822}
e_pl = {1: 165, 2: 49, 3: 39, 4: 18, 5: 13}
print(f"{'m':>2} | {'P_obs':>8} | {'P_th':>8} | {'偏差':>8} | {'σ':>6}")
print("-" * 50)
for m in range(1, 3):
    P_obs = (D_pl[2*m] + D_pl[2*m+1])/(2*D_pl[1])
    e_obs = 0.5*np.sqrt((e_pl[2*m]/D_pl[1])**2 + (e_pl[2*m+1]/D_pl[1])**2 + (D_pl[2*m]*e_pl[1]/D_pl[1]**2)**2 + (D_pl[2*m+1]*e_pl[1]/D_pl[1]**2)**2)
    P_th = P_theory(m)
    dev = (P_obs - P_th)/P_th*100
    sigma = abs(P_obs - P_th)/e_obs
    print(f"{m:>2} | {P_obs:>8.4f} | {P_th:>8.4f} | {dev:>+7.2f}% | {sigma:>6.2f}")

# ============ 基準 3: CAMB lensed @ 自動峰位 ============
print()
print("=" * 72)
print("基準 3: CAMB lensed @ 自動峰位")
print("=" * 72)
# CAMB lensed 自動峰: 之前 detect 到 220(5460), 536(2470), 813(2421), 989(1040), 1174(1099), 1365(730), 1422(779)
D_camb = {1: 5460, 2: 2470, 3: 2421, 4: 1040, 5: 1099, 6: 730, 7: 779}
for m in range(1, 4):
    P_obs = (D_camb[2*m] + D_camb[2*m+1])/(2*D_camb[1])
    P_th = P_theory(m)
    dev = (P_obs - P_th)/P_th*100
    print(f"  P_{m} = {P_obs:.4f} | 理論 {P_th:.4f} | 偏差 {dev:+.3f}%")

print()
print("=" * 72)
print("偏差模式分析")
print("=" * 72)
print("CAMB@IDCM:  D₁=0.966, D₂=1.033, D₃=1.000")
print("CAMB@auto:  ?")
print("Planck bin: ?")
print()
print("如果 D₁<1 但 D₂>1: 可能 P₂ 受到相鄰峰合併 (peak merging)")
print("或: IDCM 峰位 (537/810) 同自動峰 (527/815) 有系統偏移")
