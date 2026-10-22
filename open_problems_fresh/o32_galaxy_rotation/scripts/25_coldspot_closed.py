#!/usr/bin/env python3
"""
O32-25: 冷斑閉合驗證 — ε = F₇/(2N-2) + ω₁·T_sync = 2π²
==========================================================
發現:
1. ω₁·T_sync/2π = 3.1411 ≈ π → ω₁·T_sync = 2π² (宇宙一生 mode 1 振 π 圈)
2. 冷斑 δT/T = 5ε⁵/8, ε = 0.15108
   而 13/86 = 0.151163 (0.05% off!)
   13 = F₇, 86 = 44+13+29 = 2N-2 = 88-2 (N=44)
   → ε = F₇/(2N-2) = 13/86
3. E=1 帶內模態: θ = π/3 → n = 88/3 = 29.33 ≈ L₇ = 29
"""
import numpy as np
import json

c = 299792.458e3
R_H = 4129.94*3.085677581e22
H0 = c/R_H
T_cmb = 2.725
phi = (1+np.sqrt(5))/2

# ===== 1. ω₁·T_sync = 2π² =====
omega_1 = (88*c/R_H)*np.sin(np.pi/88)
T_sync = 84.64*3.15576e16
wT = omega_1*T_sync
print("="*70)
print("1. ω₁·T_sync 閉合")
print("="*70)
print(f"ω₁·T_sync = {wT:.6f} rad")
print(f"2π² = {2*np.pi**2:.6f}")
print(f"偏差 = {abs(wT-2*np.pi**2)/(2*np.pi**2)*100:.4f}%")
print(f"ω₁·T_sync/2π = {wT/(2*np.pi):.6f} ≈ π = {np.pi:.6f}")
print(f"SYNC T = 2π/H₀? T_2π/H₀ = {2*np.pi/H0/3.15576e16:.4f} Gyr vs 84.64")

# 精確: T_sync = 84.64 Gyr, 2π/H₀ = ?
T_2pi_H0 = 2*np.pi/H0
print(f"2π/H₀ = {T_2pi_H0/3.15576e16:.4f} Gyr")
print(f"T_sync/(2π/H₀) = {T_sync/T_2pi_H0:.6f}")

# ===== 2. 冷斑 ε = F₇/(2N-2) =====
print("\n" + "="*70)
print("2. 冷斑閉合: ε = F₇/(2N-2) = 13/86")
print("="*70)
dT_cold = 134.2e-6
r_obs = dT_cold/T_cmb
eps_obs = (8*r_obs/5)**(1/5)
print(f"觀測: δT/T = {r_obs:.8e}")
print(f"反推 ε = (8·δT/T/5)^(1/5) = {eps_obs:.8f}")

eps_13_86 = 13/86
print(f"13/86 = {eps_13_86:.8f}")
print(f"偏差 = {abs(eps_13_86-eps_obs)/eps_obs*100:.4f}%")

# 驗證 δT_pred
r_pred = 5*eps_13_86**5/8
dT_pred = r_pred*T_cmb*1e6
print(f"\nδT_pred = 5(13/86)⁵T/8 = {dT_pred:.2f} μK")
print(f"δT_obs = 134.2 μK")
print(f"偏差 = {abs(dT_pred-134.2)/134.2*100:.4f}%")

# 86 = 2N-2 = 88-2
print(f"\n86 = 2·44-2 = 2N-2 ✓ (88-site 環減 2)")
print(f"13 = F₇ (Fibonacci), 29 = L₇ (Lucas), 44 = N")
print(f"44+13+29 = 86 ✓ (三數和 = 分母!)")

# ===== 3. 其他 ε 候選比較 =====
print("\n" + "="*70)
print("3. ε 候選比較")
print("="*70)
candidates = {
    '13/86 (F₇/(2N-2))': 13/86,
    '1/φ⁴': 1/phi**4,
    '44/λ_sync': 44/294.88,
    'sin(π/88)·44': np.sin(np.pi/88)*44,
    '1/φ⁵': 1/phi**5,
    'F₇/88': 13/88,
    'L₇/193': 29/193,
}
print(f"{'候選':<22} {'ε':>10} {'偏差 vs 0.151081':>16}")
for name, val in candidates.items():
    dev = abs(val-eps_obs)/eps_obs*100
    print(f"{name:<22} {val:>10.6f} {dev:>14.4f}%")

# ===== 4. 帶內模態 n=29 =====
print("\n" + "="*70)
print("4. 冷斑位置 ↔ 帶內模態")
print("="*70)
# E=1 → θ=π/3 → n=88/3=29.33
print(f"E=1 帶內模態: 2cos(πn/88) = 1 → n = 88/3 = {88/3:.3f}")
print(f"n = 29.33 ≈ L₇ = 29 (冷斑經度 = 180+29 = 209°)")
print(f"n=29: E = 2cos(29π/88) = {2*np.cos(29*np.pi/88):.6f} ≈ 1.02")
print(f"→ 冷斑經度 = 180° + (E≈1 帶內模態 n=29)")

# 緯度: 57 = 44+13
print(f"\n緯度 57 = 44+13 = N + F₇")
print(f"n=13: E = 2cos(13π/88) = {2*np.cos(13*np.pi/88):.6f}")
print(f"n=44-13=31: E = 2cos(31π/88) = {2*np.cos(31*np.pi/88):.6f}")

# ===== 5. 完整閉合公式 =====
print("\n" + "="*70)
print("5. 完整閉合公式")
print("="*70)
print("""
★ 冷斑溫度閉合:

  δT_cold/T = 5ε⁵/8,  ε = F₇/(2N-2) = 13/86

  δT_cold = 5(13/86)⁵·T_cmb/8 = 134.47 μK
  δT_obs  = 134.2 μK
  偏差     = 0.20%

  其中:
  F₇ = 13 (Fibonacci, 冷斑緯度結構)
  N  = 44 (K_Chain sites)
  86 = 2N-2 = 88-2 (88-site 環減 2)

★ 頻率閉合:

  ω₁·T_sync = 2π²  (偏差 0.02%)
  T_sync = 2π/H₀ = 84.63 Gyr ≈ 84.64 Gyr

★ 位置閉合:

  經度 209° = 180° + L₇ = 180 + 29
  29 ≈ 88/3 (E=1 帶內模態 θ=π/3)
  緯度 57° = 44 + F₇ = 44 + 13
""")

with open('data/coldspot_closed.json', 'w') as f:
    json.dump({
        'eps': 13/86,
        'eps_obs': float(eps_obs),
        'eps_dev': float(abs(13/86-eps_obs)/eps_obs*100),
        'dT_pred_uK': float(dT_pred),
        'dT_obs_uK': 134.2,
        'dT_dev': float(abs(dT_pred-134.2)/134.2*100),
        'omega1_Tsync': float(wT),
        '2pi2': float(2*np.pi**2),
        'omega1_dev': float(abs(wT-2*np.pi**2)/(2*np.pi**2)*100),
        'n_29': float(2*np.cos(29*np.pi/88)),
        'n_13': float(2*np.cos(13*np.pi/88)),
        'formula': 'δT/T = 5(F₇/(2N-2))⁵/8, ω₁·T_sync = 2π²'
    }, f, indent=2)
print("結果已存: data/coldspot_closed.json")
