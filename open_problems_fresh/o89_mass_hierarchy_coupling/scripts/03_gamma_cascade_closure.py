#!/usr/bin/env python3
"""
O89-3: 質量層級第一性原理 — γ₁ 級聯閉合
===========================================
核心發現: 級聯因子 γ₁ = 4sin²(π/88) 決定所有 breaking scale
M_Planck × γ₁ⁿ 對應不同 breaking 步驟

★ M_GUT = M_Planck × γ₁  (n=1)
★ M_PS  = M_GUT × γ₁       (n=2)
★ M_R   = M_PS × γ₁        (n=3)
★ M_EW  = M_Planck × γ₁⁸ × N_d  (n=8, ×44)
"""

import numpy as np
import json, os

# ============================================================
# 1. IDCM 參數
# ============================================================
M_Planck = 1.2209e19
phi = (1 + np.sqrt(5)) / 2
N_d = 44
K_tree = 33
B = 4
N_gen = 3
L_5 = 11
L_4 = 7
L_6 = 18
L_7 = 29
F_5 = 5
F_6 = 8
F_7 = 13
F_8 = 21

# γ₁ exactly
gamma_1 = 4 * np.sin(np.pi / 88) ** 2
gamma_7 = 4 * np.sin(7 * np.pi / 88) ** 2
gamma_20 = 4 * np.sin(20 * np.pi / 88) ** 2
gamma_44 = 4 * np.sin(44 * np.pi / 88) ** 2

print("=" * 70)
print("O89-3: 質量層級第一性原理 — γ₁ 級聯閉合")
print("=" * 70)

# ============================================================
# 2. γ₁ 級聯
# ============================================================
print(f"\n## γ₁ 級聯因子")
print(f"  γ₁ = 4sin²(π/88) = {gamma_1:.10f}")
print(f"  γ₁⁻¹ = {1/gamma_1:.4f}")

print(f"\n## 級聯表")
print(f"{'n':<5} {'γ₁ⁿ':<20} {'M_Planck × γ₁ⁿ (GeV)':<25} {'Log10':<10} {'Target':<15} {'Ratio':<10}")
print("-" * 85)

targets = {
    1: ('M_GUT', 2e16),
    2: ('M_PS', 1e14),
    3: ('M_R', 1e12),
    4: ('M_int', 5e9),
    5: ('M_int', 2.5e7),
    6: ('M_int', 1.3e5),
    7: ('M_SUSY', 1e3),
    8: ('M_EW_base', 5.55),
    # 9 and below are sub-GeV
}

for n in range(1, 10):
    gamma_n = gamma_1 ** n
    M_pred = M_Planck * gamma_n
    logM = np.log10(M_pred)
    if n in targets:
        name, target = targets[n]
        ratio = M_pred / target
    else:
        name, target, ratio = '', 0, 0
    print(f"{n:<5} {gamma_n:<20.6e} {M_pred:<25.4e} {logM:<10.4f} {name:<15} {ratio:<10.4f}" if n in targets else
          f"{n:<5} {gamma_n:<20.6e} {M_pred:<25.4e} {logM:<10.4f}")

# ============================================================
# 3. EW scale: v_geom = 246.82 GeV
# ============================================================
print(f"\n\n## EW scale 閉合")
print(f"  v_geom (O59) = 246.82 GeV")
print(f"  v_geom / M_Planck = {246.82/M_Planck:.6e}")

# v_geom = M_Planck × γ₁⁸ × N_d
v_geom_pred_1 = M_Planck * gamma_1**8 * N_d
print(f"\n  v_geom = M_Planck × γ₁⁸ × N_d")
print(f"         = {M_Planck:.4e} × {gamma_1**8:.6e} × {N_d}")
print(f"         = {v_geom_pred_1:.4f} GeV")
print(f"  偏差: {abs(v_geom_pred_1 - 246.82)/246.82*100:.4f}%")

# v_geom = M_Planck × γ₁⁷ × γ₁ × N_d = same thing
# 8 = 2B, so v_geom = M_Planck × γ₁^(2B) × N_d

# Try: v_geom = M_Planck × γ₁⁷ × (γ₁ × N_d) = M_Planck × γ₁⁸ × N_d (same)

# What about including the d_tensor eigenvalue?
# λ_max = 52 - 29/66 = 51.5606
lambda_max = 52 - 29/66
print(f"\n  λ_max = 52 - 29/66 = {lambda_max:.6f} (O59 d_tensor)")
print(f"  v_geom / λ_max = {246.82/lambda_max:.4f}")

# Does v_geom/λ_max relate to something?
ratio_v = 246.82 / lambda_max
print(f"  v_geom/λ_max = {ratio_v:.4f} GeV")
print(f"  M_Planck × γ₁⁷ / λ_max = {M_Planck * gamma_1**7 / lambda_max:.4f} GeV")
print(f"  M_Planck × γ₁⁸ / λ_max = {M_Planck * gamma_1**8 / lambda_max:.4f} GeV")

# Let's try: v_geom = M_Planck × γ₁⁷ × (γ₁ × N_d) / (something)
# The 1.1% deviation: correction factor?
correction = 246.82 / (M_Planck * gamma_1**8 * N_d)
print(f"\n  v_geom / (M_Planck × γ₁⁸ × N_d) = {correction:.6f}")
print(f"  1/correction = {1/correction:.6f}")

# Check if correction is φ-related
print(f"  φ⁻¹ = {1/phi:.6f}")
print(f"  φ⁻² = {1/phi**2:.6f}")
print(f"  φ⁻⁴ = {1/phi**4:.6f}")

# ============================================================
# 4. 指數結構分析
# ============================================================
print(f"\n\n## 指數結構")
print(f"  n=1: M_GUT = M_Planck × γ₁¹")
print(f"  n=2: M_PS  = M_Planck × γ₁²")
print(f"  n=3: M_R   = M_Planck × γ₁³")
print(f"  n=8: M_EW  = M_Planck × γ₁⁸ × N_d")

print(f"\n  指數 1, 2, 3 嘅結構:")
print(f"    1 = 1 (單位)")
print(f"    2 = B/2 = 4/2")
print(f"    3 = ?")
print(f"    8 = 2B = 2×4 = N_d/5.5")

# 8 = 2B, 3 = ?, 2 = B/2, 1 = 1
# Check if 3 = (B-1) = 3? Yes!
print(f"\n    1 = 1")
print(f"    2 = B/2 = {B/2}")
print(f"    3 = B-1 = {B-1}")
print(f"    8 = 2B = {2*B}")

# ============================================================
# 5. 對比 Φ 比例
# ============================================================
print(f"\n\n## Φ 比例對比")
print(f"  γ₁ = {gamma_1:.10f}")
print(f"  φ⁻¹⁶ = {1/phi**16:.10f}")
print(f"  γ₁ / φ⁻¹⁶ = {gamma_1 / (1/phi**16):.4f}")
print(f"  γ₁² / φ⁻¹⁶ = {gamma_1**2 / (1/phi**16):.4f}")
print(f"  γ₁³ / φ⁻¹⁶ = {gamma_1**3 / (1/phi**16):.4f}")

# φ⁻¹⁶ / γ₁² = ?
print(f"\n  φ⁻¹⁶ / γ₁² = {(1/phi**16) / gamma_1**2:.4f} = F_proj = 17?")
print(f"  F_proj (O54) = 17")
print(f"  φ⁻¹⁶ / γ₁² = {1/phi**16/gamma_1**2:.4f}, F_proj = 17, ratio = {1/phi**16/gamma_1**2/17:.4f}")

# ============================================================
# 6. 完整級聯圖
# ============================================================
print(f"\n\n## 完整級聯圖")
print(f"  M_Planck = {M_Planck:.4e} GeV")
print(f"    ↓ × γ₁ = {gamma_1:.6f}")
print(f"  M_GUT = {M_Planck*gamma_1:.4e} GeV  (SU(12) → SU(4)×SU(3))")
print(f"    ↓ × γ₁ = {gamma_1:.6f}")
print(f"  M_PS = {M_Planck*gamma_1**2:.4e} GeV  (SU(4) → SU(2)_L×SU(2)_R)")
print(f"    ↓ × γ₁ = {gamma_1:.6f}")
print(f"  M_R = {M_Planck*gamma_1**3:.4e} GeV  (SU(2)_R×U(1) → U(1)_Y)")
print(f"    ↓ × γ₁⁵ × N_d = {gamma_1**5*N_d:.6f}")
print(f"  M_EW = {M_Planck*gamma_1**8*N_d:.4f} GeV  (EW Higgs v_geom)")

# Calculate the actual step between M_R and M_EW
print(f"\n  M_R 到 M_EW 嘅實際因子:")
print(f"  M_R / M_EW = {M_Planck*gamma_1**3 / 246.82:.4e}")
print(f"  log10(M_R/M_EW) = {np.log10(M_Planck*gamma_1**3/246.82):.4f}")
print(f"  γ₁^? = M_EW/M_R, n = log(M_EW/M_R)/log(γ₁) = {np.log(246.82/(M_Planck*gamma_1**3))/np.log(gamma_1):.4f}")

# ============================================================
# 7. 保存結果
# ============================================================
results = {
    'gamma_1': float(gamma_1),
    'cascade': {
        'M_Planck': M_Planck,
        'M_GUT': float(M_Planck * gamma_1),
        'M_PS': float(M_Planck * gamma_1**2),
        'M_R': float(M_Planck * gamma_1**3),
        'M_EW': float(M_Planck * gamma_1**8 * N_d),
        'v_geom_target': 246.82,
        'EW_deviation_pct': float(abs(M_Planck*gamma_1**8*N_d - 246.82)/246.82*100)
    },
    'exponents': {
        '1': 'unit',
        '2': 'B/2',
        '3': 'B-1',
        '8': '2B'
    },
    'phi_comparison': {
        'gamma_1': float(gamma_1),
        'phi_inv16': float(1/phi**16),
        'gamma1_over_phi_inv16': float(gamma_1 / (1/phi**16)),
        'phi_inv16_over_gamma1_sq': float((1/phi**16) / gamma_1**2),
        'F_proj': 17
    }
}

out_path = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o89_mass_hierarchy_coupling/data/03_gamma_cascade_closure.json'
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n✅ 結果已保存到 {out_path}")