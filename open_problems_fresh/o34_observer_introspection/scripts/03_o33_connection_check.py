#!/usr/bin/env python3
"""O34 ↔ O33 連接快速檢查"""
import numpy as np

phi = (1 + 5**0.5) / 2

Omega_L = 4 / (phi**4 - 1)
unprojected_frac = 61.5 / 90

print("=== O34 ↔ O33 連接檢查 ===")
print(f"Ω_Λ = 4/(φ⁴−1) = {Omega_L:.8f}")
print(f"未被投影能量比例 = 61.5/90 = {unprojected_frac:.8f}")
print(f"Ω_m = 1 − Ω_Λ = {1-Omega_L:.8f}")
print(f"物質能量 = 28.5/90 = {28.5/90:.8f}")
print()

gamma88 = np.array([4*np.sin(np.pi*k/176)**2 for k in range(1, 89)])
# 正確對偶配對: γ_k + γ_{88−k}, k=1..87, 自配對 k=44
# pairs[i] = γ_{i+1} + γ_{87−i} (i=0..42 → k=1..43)
pairs = gamma88[:43] + gamma88[86:43:-1]
print("=== 88-site 配對 γ_k + γ_{88−k} (k=1..43) ===")
print(f"前 5 個配對和: {[f'{p:.6f}' for p in pairs[:5]]}")
print(f"配對和全部 = 4? {np.allclose(pairs, 4)}")
print(f"43 對 × 4 = {43*4}")
print(f"剩餘: γ_44 = {gamma88[43]:.6f} (中點, =2?), γ_88 = {gamma88[87]:.6f} (Nyquist, =4?)")
print(f"Σγ_88 = 43×4 + γ_44 + γ_88 = {43*4 + gamma88[43] + gamma88[87]:.6f}")
print(f"Σγ_88 (直接) = {np.sum(gamma88):.6f}")
print()

# 44-site 對照: γ_n + γ_{44−n} = 4, n=1..21, 自配對 n=22
gamma44 = np.array([4*np.sin(np.pi*n/88)**2 for n in range(1, 45)])
pairs44 = gamma44[:21] + gamma44[42:21:-1]
print("=== 44-site 配對 γ_n + γ_{44−n} (n=1..21) ===")
print(f"配對和全部 = 4? {np.allclose(pairs44, 4)}")
print(f"21 對 × 4 = {21*4}")
print(f"剩餘: γ_22 = {gamma44[21]:.6f} (中點, =2?), γ_44 = {gamma44[43]:.6f} (Nyquist, =4?)")
print(f"Σγ_44 = 21×4 + γ_22 + γ_44 = {21*4 + gamma44[21] + gamma44[43]:.6f}")
print(f"Σγ_44 (直接) = {np.sum(gamma44):.6f}")
print()

# 結構閉合: 兩個鏈嘅配對和
print("=== 配對結構閉合 ===")
print(f"44-site: 21×4 + 2 + 4 = 90")
print(f"88-site: 43×4 + 2 + 4 = 178")
print(f"178 − 90 = 88 = 2N = 觀察者能量")
print(f"90 − 88 = 2 = γ_22(44-site) − γ_44(88-site) = 2 − 2?")
print(f"  γ_22(44-site) = {gamma44[21]:.6f}, γ_44(88-site) = {gamma88[43]:.6f}")
print(f"  差 = {gamma44[21] - gamma88[43]:.6f}")
print(f"觀察者能量 88 = 88-site 鏈嘅「對偶修正」")
print(f"  = (43×4+2+4) − (21×4+2+4) = 22×4 = 88 ✓ (22 = N/2)")

ratio_obs_total = 88 / 178
print(f"觀察者/全鏈 = 88/178 = {ratio_obs_total:.8f}")
print(f"Ω_Λ = {Omega_L:.8f}")
print(f"88/178 vs Ω_Λ 差 = {abs(ratio_obs_total - Omega_L):.6f}")
print()

print(f"88 × φ⁻³ = {88*phi**-3:.4f}")
print(f"88 × φ⁻⁴ = {88*phi**-4:.4f}")
print(f"90 × φ⁻¹ = {90*phi**-1:.4f}")
print(f"90 × φ⁻² = {90*phi**-2:.4f}")
print(f"61.5 vs 90×φ⁻² = {90*phi**-2:.4f}")
print()

gamma_half = np.array([4*np.sin(np.pi*(2*n+1)/176)**2 for n in range(44)])
print("=== 觀察者譜邊界 ===")
print(f"γ_{{0.5}} (n=0) = {4*np.sin(np.pi*1/176)**2:.8f}")
print(f"γ_{{43.5}} (n=43) = {gamma_half[-1]:.8f}")
print(f"γ_{{44}} (Nyquist) = {4*np.sin(np.pi*88/176)**2:.8f}")
print()

# 關鍵: 觀察者 88 vs 未被投影 61.5 有冇結構關係?
# 61.5 = 90 − 28.5 (物質 28.5/90)
# 物質 = 28.5 = ?
print("=== 物質能量 28.5 結構 ===")
print(f"28.5 = 90 − 61.5")
print(f"28.5 × 2 = 57")
print(f"28.5 × 4 = 114")
print(f"28.5 / 90 = 0.316666... ≈ 1 − Ω_Λ = {1-Omega_L:.6f}")
print(f"28.5 = 57/2 = 3×19/2")
print(f"88 − 28.5 = {88-28.5} = 59.5")
print(f"90 − 88 = 2 (觀察者同世界嘅差)")
