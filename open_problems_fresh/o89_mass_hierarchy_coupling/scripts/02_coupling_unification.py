#!/usr/bin/env python3
"""
O89-2: SU(12) → SM Gauge Coupling Unification
===============================================
計算 SU(12) breaking chain 下嘅 coupling running:
- 1-loop β function 估算
- SU(12) → SU(4)×SU(3) → SU(2)_L×SU(2)_R×SU(3) → SU(2)_L×U(1)_Y×SU(3)_c → SM
- 比較 M_GUT, M_PS, M_R 下嘅 coupling 值
"""

import numpy as np
import json, os

# ============================================================
# 1. 參數
# ============================================================
M_Planck = 1.2209e19
M_GUT = 6.22e16   # M_Planck × γ₁
M_PS = 3.17e14    # M_Planck × γ₁²
M_R = 1.62e12     # M_Planck × γ₁³
M_EW = 246.82     # v_geom (O59)

# SM couplings at M_Z (PDG)
alpha_1_inv_MZ = 59.0      # U(1)_Y, sin²θ_W = 0.231
alpha_2_inv_MZ = 29.5      # SU(2)_L
alpha_3_inv_MZ = 8.5       # SU(3)_c

# ============================================================
# 2. 1-loop β 函數
# ============================================================
# β(g) = -b g³/(16π²), d(α⁻¹)/dt = b/(2π)
# t = ln(μ)

def running(alpha_inv_start, M_start, M_end, b_coeff):
    """1-loop running: α⁻¹(M_end) = α⁻¹(M_start) + b/(2π) × ln(M_end/M_start)"""
    return alpha_inv_start + b_coeff / (2*np.pi) * np.log(M_end / M_start)

print("=" * 70)
print("O89-2: SU(12) → SM Gauge Coupling Unification")
print("=" * 70)

# ============================================================
# 3. β 係數 (SU(N) groups)
# ============================================================
# 1-loop: b = 11/3 N - 2/3 n_f - 1/6 n_s
# For pure gauge: b = 11N/3
# For SU(N) with n_f fermions in fundamental: b = 11N/3 - 2n_f/3

# SU(12) at M_Planck
b_SU12_pure = 11 * 12 / 3  # 44
# With fermions (12 fundamental reps × 3 generations? Actually complicated)
# We'll use pure gauge as first approximation

# SU(4): b_4 = 11*4/3 = 44/3 ≈ 14.67
# SU(3): b_3 = 11*3/3 = 11
# SU(2): b_2 = 11*2/3 = 22/3 ≈ 7.33
# U(1): b_1 = 0 (pure gauge, but depends on matter content)

# With SM matter content (3 generations):
# Standard Model: b_3 = 7, b_2 = 19/6, b_1 = -41/10 (GUT normalized)
# MSSM: b_3 = -3, b_2 = 1, b_1 = 33/5

# For our SU(12) breaking chain, we need the beta coefficients at each stage
# Since we don't know the full matter content, let's do a simplified analysis

print(f"\n## 級聯尺度")
print(f"{'Scale':<10} {'Value (GeV)':<20} {'Log10':<10}")
print("-" * 40)
for name, val in [('M_Planck', M_Planck), ('M_GUT', M_GUT), ('M_PS', M_PS), ('M_R', M_R), ('M_EW', M_EW)]:
    print(f"{name:<10} {val:<20.4e} {np.log10(val):<10.4f}")

print(f"\n## γ₁ 級聯 (cascade factor)")
print(f"  γ₁ = 4sin²(π/88) = {4*np.sin(np.pi/88)**2:.6f}")
print(f"  M_GUT/M_Planck = γ₁ = {M_GUT/M_Planck:.6f}")
print(f"  M_PS/M_GUT = γ₁ = {M_PS/M_GUT:.6f}")
print(f"  M_R/M_PS = γ₁ = {M_R/M_PS:.6f}")

# ============================================================
# 4. Coupling 匹配條件
# ============================================================
print(f"\n## Coupling 匹配 (gauge coupling unification)")

# At M_GUT: SU(12) → SU(4) × SU(3)
# g_4 = g_3 = g_12 (unified)
# At M_PS: SU(4) → SU(2)_L × SU(2)_R
# g_2L = g_2R = g_4 (unified)
# At M_R: SU(2)_R × U(1)_{B-L} → U(1)_Y
# g_Y = g_2R * g_BL / sqrt(g_2R² + g_BL²) (mixing)
# At M_EW: SU(2)_L × U(1)_Y → U(1)_QED
# e = g_2L * sinθ_W = g_Y * cosθ_W

# Simple check: if all couplings unify at M_GUT
alpha_GUT = 1/24  # typical GUT value
alpha_3_at_MZ = running(1/alpha_GUT, M_GUT, 91.2, 7)  # SM b_3 = 7
alpha_2_at_MZ = running(1/alpha_GUT, M_GUT, 91.2, 19/6)  # SM b_2 = 19/6
alpha_1_at_MZ = running(1/alpha_GUT, M_GUT, 91.2, -41/10)  # SM b_1 = -41/10

print(f"\n  SM running from M_GUT = {M_GUT:.2e} GeV to M_Z:")
print(f"  {'':<5} {'α⁻¹(GUT)':<12} {'α⁻¹(M_Z)':<12} {'Target':<12} {'Diff':<10}")
for name, inv_a, target in [('α₃⁻¹', alpha_3_at_MZ, alpha_3_inv_MZ), 
                              ('α₂⁻¹', alpha_2_at_MZ, alpha_2_inv_MZ),
                              ('α₁⁻¹', alpha_1_at_MZ, alpha_1_inv_MZ)]:
    print(f"  {name:<5} {1/alpha_GUT:<12.4f} {inv_a:<12.4f} {target:<12.4f} {inv_a - target:<10.4f}")

# ============================================================
# 5. 用 γ₁ 級聯 + MSSM β 函數
# ============================================================
print(f"\n\n## MSSM running (if SUSY at M_R ~ TeV)")
# MSSM β: b_3 = -3, b_2 = 1, b_1 = 33/5
# SUSY threshold at M_R ~ 1.6 TeV

alpha_GUT_MSSM = 1/25
M_SUSY = M_R  # ~1.6 TeV

# MSSM running from M_GUT to M_SUSY
a3_inv_SUSY = running(1/alpha_GUT_MSSM, M_GUT, M_SUSY, -3)
a2_inv_SUSY = running(1/alpha_GUT_MSSM, M_GUT, M_SUSY, 1)
a1_inv_SUSY = running(1/alpha_GUT_MSSM, M_GUT, M_SUSY, 33/5)

# SM running from M_SUSY to M_Z
a3_inv_MZ = running(a3_inv_SUSY, M_SUSY, 91.2, 7)
a2_inv_MZ = running(a2_inv_SUSY, M_SUSY, 91.2, 19/6)
a1_inv_MZ = running(a1_inv_SUSY, M_SUSY, 91.2, -41/10)

print(f"  M_GUT = {M_GUT:.2e} GeV, M_SUSY = {M_SUSY:.2e} GeV")
print(f"  {'':<5} {'α⁻¹(GUT)':<12} {'α⁻¹(SUSY)':<12} {'α⁻¹(M_Z)':<12} {'Target':<12} {'Diff':<10}")
for name, inv_a, target in [('α₃⁻¹', a3_inv_MZ, alpha_3_inv_MZ),
                              ('α₂⁻¹', a2_inv_MZ, alpha_2_inv_MZ),
                              ('α₁⁻¹', a1_inv_MZ, alpha_1_inv_MZ)]:
    print(f"  {name:<5} {1/alpha_GUT_MSSM:<12.4f} {'':<12} {inv_a:<12.4f} {target:<12.4f} {inv_a - target:<10.4f}")

# ============================================================
# 6. EW scale 嘅特殊地位
# ============================================================
print(f"\n\n## EW scale 結構分析")
print(f"  v_geom = 246.82 GeV (O59)")
print(f"  v_geom 來自 d_tensor 本徵值 λ_max = 51.5606")
print(f"  λ_max = 52 - 29/66 = N_d + 2B - L₇/C(12,2)")
print(f"  v_geom = M_Planck × (λ_max × 某個因子?)")

# Try: v_geom relates to M_Planck via d_tensor structure
# From O59: λ_max = 51.5606, and v_geom = 246.82 GeV
# The factor: v_geom / M_Planck = 2.02e-17
# λ_max: M_Planck factor = 2.02e-17 / 51.5606 = 3.92e-19

# Check γ₁⁷:
gamma_1 = 4 * np.sin(np.pi/88)**2
gamma_1_7 = gamma_1 ** 7
print(f"  γ₁⁷ = {gamma_1_7:.6e}")
print(f"  M_Planck × γ₁⁷ = {M_Planck * gamma_1_7:.4e} GeV = {M_Planck * gamma_1_7:.4f} GeV")
print(f"  v_geom / (M_Planck × γ₁⁷) = {246.82 / (M_Planck * gamma_1_7):.4f}")
print(f"  v_geom / (M_Planck × γ₁⁷ × γ₁) = {246.82 / (M_Planck * gamma_1_7 * gamma_1):.4f}")

# Try different approach: EW scale = K_Chain × d_tensor
# v_geom = M_Planck × (some structural combination)
print(f"\n  v_geom / M_Planck = {246.82/M_Planck:.6e}")
print(f"  γ₁⁷ = {gamma_1_7:.6e}, ratio = {246.82/M_Planck/gamma_1_7:.4f}")
print(f"  γ₁⁸ = {gamma_1**8:.6e}, ratio = {246.82/M_Planck/(gamma_1**8):.4f}")
print(f"  γ₁⁷ / γ₁ = γ₁⁶ = {gamma_1**6:.6e}")

# ============================================================
# 7. 保存結果
# ============================================================
results = {
    'cascade_scales': {
        'M_Planck': M_Planck,
        'M_GUT': M_GUT,
        'M_PS': M_PS,
        'M_R': M_R,
        'M_EW': M_EW,
        'cascade_factor': float(gamma_1),
        'M_GUT_M_Planck_ratio': float(M_GUT/M_Planck),
        'M_PS_M_GUT_ratio': float(M_PS/M_GUT),
        'M_R_M_PS_ratio': float(M_R/M_PS)
    },
    'coupling_running': {
        'SM_from_GUT': {
            'alpha_3_inv': float(alpha_3_at_MZ),
            'alpha_2_inv': float(alpha_2_at_MZ),
            'alpha_1_inv': float(alpha_1_at_MZ),
        },
        'MSSM_like': {
            'alpha_3_inv': float(a3_inv_MZ),
            'alpha_2_inv': float(a2_inv_MZ),
            'alpha_1_inv': float(a1_inv_MZ),
        }
    }
}

out_path = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o89_mass_hierarchy_coupling/data/02_coupling_unification.json'
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n✅ 結果已保存到 {out_path}")