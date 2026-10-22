#!/usr/bin/env python3
"""
O10 06: 簡併對階梯結構 — 決定性驗證
====================================
驗證: S(m) = P_m/3ε 嘅結構

候選階梯:
  A) 用戶: S(m) = φ^{-2(m-1)} = (1, φ⁻², φ⁻⁴)  ← 數值上 D_m > 1, 物理矛盾?
  B) 發現: S(m) = F_m·φ^{-2(m-1)} = (1, φ⁻², 2φ⁻⁴)  ← Fibonacci 階梯
  C) 其他: 2φ⁻⁴ 直接?

物理約束: Silk 阻尼 D_m = exp[-(ℓ_m/ℓ_D)^{3/2}] < 1
          => 純幾何項 S_pure(m) ≥ P_m/3ε 先合理
"""
import numpy as np, math

phi = (1 + 5**0.5) / 2
phi_inv = 1/phi
eps = phi_inv/4

# CAMB lensed @ IDCM 峰位 (As=2.1e-9)
A = {1: 1.0, 2: 0.4523, 3: 0.4430, 4: 0.1820, 5: 0.1839, 6: 0.1282, 7: 0.1423}
ell = {1: 220, 2: 537, 3: 810, 4: 1014, 5: 1199, 6: 1340, 7: 1412}

# 簡併對平均
P = {}
P[1] = (A[2] + A[3]) / 2      # pair (2,3)
P[2] = (A[4] + A[5]) / 2      # pair (4,5)
P[3] = (A[6] + A[7]) / 2      # pair (6,7)
ell_P = {1: (ell[2]+ell[3])/2, 2: (ell[4]+ell[5])/2, 3: (ell[6]+ell[7])/2}

print("=" * 70)
print("簡併對 P_m (CAMB lensed @ IDCM 峰位)")
print("=" * 70)
for i in range(1, 4):
    print(f"  P_{i} (pair {2*i},{2*i+1}): avg = {P[i]:.4f}, <ℓ> = {ell_P[i]:.0f}")

print()
print("S(m) = P_m/3ε:")
S_obs = {i: P[i]/(3*eps) for i in range(1, 4)}
for i in range(1, 4):
    print(f"  S({i}) = {S_obs[i]:.5f}")

print()
print("=" * 70)
print("候選階梯驗證")
print("=" * 70)

print("\n[A] 用戶階梯 S(m) = φ^(-2(m-1)) = (1, φ⁻², φ⁻⁴):")
for i in range(1, 4):
    S_c = phi_inv**(2*(i-1))
    D = S_obs[i]/S_c
    print(f"  S({i}) = {S_c:.5f} | 觀測 {S_obs[i]:.5f} | 偏差 {(S_obs[i]-S_c)/S_c*100:+.2f}% | 有效阻尼 D={D:.4f}")

print("\n[B] Fibonacci 階梯 S(m) = F_m·φ^(-2(m-1)) = (1, φ⁻², 2φ⁻⁴):")
F = [1, 1, 2, 3, 5, 8]
for i in range(1, 4):
    S_c = F[i-1] * phi_inv**(2*(i-1))
    D = S_obs[i]/S_c
    print(f"  S({i}) = {S_c:.5f} | 觀測 {S_obs[i]:.5f} | 偏差 {(S_obs[i]-S_c)/S_c*100:+.3f}% | 有效阻尼 D={D:.4f}")

print("\n[C] 修正階梯 S(m) = (m-1)·φ^(-2(m-1)) (m≥2):")
for i in range(1, 4):
    S_c = max(i-1, 1) * phi_inv**(2*(i-1)) if i > 1 else 1.0
    D = S_obs[i]/S_c
    print(f"  S({i}) = {S_c:.5f} | 觀測 {S_obs[i]:.5f} | 偏差 {(S_obs[i]-S_c)/S_c*100:+.3f}% | 有效阻尼 D={D:.4f}")

print()
print("=" * 70)
print("物理一致性: 有效阻尼 D_m 必須 ≤ 1")
print("=" * 70)
print("  [A] D =", [round(S_obs[i]/phi_inv**(2*(i-1)), 4) for i in range(1, 4)])
print("  [B] D =", [round(S_obs[i]/(F[i-1]*phi_inv**(2*(i-1))), 4) for i in range(1, 4)])
print()
print("  [A] D₃ = 2.0 > 1 → 物理矛盾 (φ⁻⁴ 過度抑制, Silk 無法放大)")
print("  [B] D₁≈0.97, D₂≈1.03, D₃≈1.00 → D₂ 略 >1 (可接受誤差?)")
print()

# 用 Planck binned 交叉驗證
print("=" * 70)
print("Planck binned 交叉驗證 (峰位 527/815/1121/1409)")
print("=" * 70)
# Planck binned 比率 (自動峰): 0.4434, 0.4389, 0.2143, 0.1414
Pb = {1: (0.4434+0.4389)/2, 2: (0.2143+0.1414)/2}
for i in [1, 2]:
    S_pb = Pb[i]/(3*eps)
    S_cA = phi_inv**(2*(i-1))
    S_cB = F[i-1]*phi_inv**(2*(i-1))
    print(f"  P_{i} = {Pb[i]:.4f} | S_obs = {S_pb:.5f}")
    print(f"    [A] φ^(-2(m-1)) = {S_cA:.5f} → 偏差 {(S_pb-S_cA)/S_cA*100:+.2f}%")
    print(f"    [B] F_m·φ^(-2(m-1)) = {S_cB:.5f} → 偏差 {(S_pb-S_cB)/S_cB*100:+.2f}%")
