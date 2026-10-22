#!/usr/bin/env python3
"""
O89-1: Φ比例質量層級分析
========================
檢查 M ∝ φ^(-2n) 嘅結構來源:
- M_GUT, M_PS, M_R, M_EW
- 比較 φ 比例 vs γ_n 比例 vs K_Tree 比例
"""

import numpy as np
import json, os, sys

# ============================================================
# 1. IDCM 固定參數
# ============================================================
M_Planck = 1.2209e19  # GeV
phi = (1 + np.sqrt(5)) / 2
N_d = 44
K_tree = 33
B = 4
N_gen = 3
L_5 = 11          # N_d/B
L_4 = 7           # φ⁴+φ⁻⁴
L_6 = 18          # φ⁶+φ⁻⁶
L_7 = 29          # φ⁷+φ⁻⁷
F_5 = 5
F_6 = 8
F_7 = 13
F_8 = 21
F_11 = 89

# K_Chain 模式能量
n_vals = np.arange(1, N_d + 1)
gamma_n = 4 * np.sin(n_vals * np.pi / 88) ** 2
gamma_1 = gamma_n[0]   # n=1
gamma_7 = gamma_n[6]   # n=7
gamma_20 = gamma_n[19] # n=20
gamma_44 = gamma_n[43] # n=44 (Nyquist)

# ============================================================
# 2. Φ比例層級
# ============================================================
print("=" * 70)
print("O89-1: Φ比例質量層級分析")
print("=" * 70)

phi_powers = [16, 8, 4, 2, 1]
targets = {
    'M_GUT': 2e16,
    'M_PS': 1e14,
    'M_R': 1e12,
    'M_EW': 246.82,
    'M_W': 80.38
}

print(f"\n## Φ比例: M = M_Planck / φ^n")
print(f"{'Scale':<10} {'φ^n':<10} {'φ^(-n)':<12} {'M_pred (GeV)':<20} {'M_target (GeV)':<20} {'Ratio':<10}")
print("-" * 82)

for n in phi_powers:
    phi_n = phi ** n
    M_pred = M_Planck / phi_n
    # Find closest target
    best_target = None
    best_ratio = float('inf')
    for name, val in targets.items():
        ratio = M_pred / val
        if abs(np.log10(ratio)) < abs(np.log10(best_ratio)):
            best_ratio = ratio
            best_target = name
    print(f"φ^(-{n:<2})  {phi_n:<10.4f} {1/phi_n:<12.6e} {M_pred:<20.4e} {targets[best_target]:<20.4e} {M_pred/targets[best_target]:<10.4f}")

print(f"\n## 關鍵觀察: 指數 16, 8, 4, 2 嘅結構來源")
print(f"   16 = ?")
print(f"   8  = 2B = 2×4")
print(f"   4  = B = 4")
print(f"   2  = B/2 = 2")

# ============================================================
# 3. γ_n比例層級
# ============================================================
print(f"\n\n## γ_n 比例: M = M_Planck × γ₁^n")
print(f"{'n':<5} {'γ₁ⁿ':<18} {'M_pred (GeV)':<20} {'Log10(M)':<12} {'Closest target':<20} {'Ratio':<10}")
print("-" * 85)

for n in range(1, 13):
    gamma_power = gamma_1 ** n
    M_pred = M_Planck * gamma_power
    logM = np.log10(M_pred)
    # Find closest target
    best_target = None
    best_ratio = float('inf')
    for name, val in targets.items():
        ratio = M_pred / val
        if abs(np.log10(ratio)) < abs(np.log10(best_ratio)):
            best_ratio = ratio
            best_target = name
    print(f"{n:<5} {gamma_power:<18.6e} {M_pred:<20.4e} {logM:<12.4f} {best_target:<20} {M_pred/targets[best_target]:<10.4f}")

# ============================================================
# 4. 混合比例: Φ × γ_n
# ============================================================
print(f"\n\n## 混合比例: M = M_Planck × φ^(-n) × γ_k")
print(f"  (M_Planck × φ^(-16) × γ_k 對 M_GUT)")
print(f"{'γ_k':<10} {'γ_k 值':<12} {'M_pred (GeV)':<20} {'M_GUT target':<15} {'Ratio':<10}")
print("-" * 67)

for k in [1, 7, 20, 44]:
    M_pred = M_Planck / (phi ** 16) * gamma_n[k-1]
    print(f"γ_{k:<2}      {gamma_n[k-1]:<12.6f} {M_pred:<20.4e} {2e16:<15.4e} {M_pred/2e16:<10.4f}")

print(f"\n  (M_Planck × φ^(-8) × γ_k 對 M_PS)")
print(f"{'γ_k':<10} {'γ_k 值':<12} {'M_pred (GeV)':<20} {'M_PS target':<15} {'Ratio':<10}")
print("-" * 67)
for k in [1, 7, 20, 44]:
    M_pred = M_Planck / (phi ** 8) * gamma_n[k-1]
    print(f"γ_{k:<2}      {gamma_n[k-1]:<12.6f} {M_pred:<20.4e} {1e14:<15.4e} {M_pred/1e14:<10.4f}")

# ============================================================
# 5. EW scale 嘅特殊地位
# ============================================================
print(f"\n\n## EW scale 分析: v_geom = 246.82 GeV (O59)")
print(f"  v_geom 來自 d_tensor 本徵值 λ_max = 51.5606")
print(f"  v_geom/M_Planck = {246.82/M_Planck:<.6e}")
print(f"  φ^(-?): n = log_φ(M_Planck/v_geom) = {np.log(M_Planck/246.82)/np.log(phi):.4f}")
print(f"  γ₁ⁿ:  γ₁^n = v_geom/M_Planck, n = log(v_geom/M_Planck)/log(γ₁) = {np.log(246.82/M_Planck)/np.log(gamma_1):.4f}")

# γ₁^8 = ?
gamma_1_8 = gamma_1 ** 8
print(f"  γ₁^8 = {gamma_1_8:.6e}, M_Planck × γ₁^8 = {M_Planck * gamma_1_8:.4e} GeV")
gamma_1_9 = gamma_1 ** 9
print(f"  γ₁^9 = {gamma_1_9:.6e}, M_Planck × γ₁^9 = {M_Planck * gamma_1_9:.4e} GeV")

# ============================================================
# 6. 保存結果
# ============================================================
results = {
    'M_Planck': M_Planck,
    'phi_hierarchy': {f'phi_-{n}': M_Planck / (phi ** n) for n in phi_powers},
    'gamma_hierarchy': {f'gamma_1^{n}': M_Planck * (gamma_1 ** n) for n in range(1, 13)},
    'targets': targets,
    'gamma_values': {f'gamma_{k}': float(gamma_n[k-1]) for k in [1, 7, 20, 44]},
    'v_geom': 246.82,
    'v_geom_M_Planck_ratio': 246.82 / M_Planck,
    'phi_power_for_EW': np.log(M_Planck/246.82) / np.log(phi),
    'gamma_power_for_EW': np.log(246.82/M_Planck) / np.log(gamma_1),
}

out_path = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o89_mass_hierarchy_coupling/data/01_phi_hierarchy.json'
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n✅ 結果已保存到 {out_path}")