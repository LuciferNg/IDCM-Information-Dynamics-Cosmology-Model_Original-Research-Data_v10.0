#!/usr/bin/env python3
"""
O89-7: 2-loop RGE + Threshold Corrections — Gauge Coupling 精確閉合
====================================================================
[修正版] unified coupling 定義喺 M_GUT，唔跑 SU(12) 由 M_Planck 落。

Scenario 2: α_GUT⁻¹=47, M_VL=2e13 GeV ≈ √(M_PS × M_R)

2-loop RGE: dαᵢ⁻¹/dt = bᵢ/(2π) + Σⱼ bᵢⱼαⱼ/(8π²)
"""

import numpy as np
import json, os, math

M_Planck = 1.2209e19
gamma_1 = 4 * np.sin(np.pi / 88) ** 2
M_GUT = M_Planck * gamma_1
M_PS  = M_Planck * gamma_1 ** 2
M_R   = M_Planck * gamma_1 ** 3
M_EW  = 246.82
M_Z   = 91.1876

a3_t = 8.44; a2_t = 29.57; a1_t = 59.02

# 1-loop β coefficients
b1_1L = -41/10; b2_1L = 19/6; b3_1L = 7

# 2-loop β matrix (SM, MS-bar, GUT-normalized)
B = np.array([
    [199/50,   27/10,   44/5 ],
    [ 9/10,    13/6,     4   ],
    [11/10,     3/2,    -26  ]
])

def run_2loop(alpha_inv_start, M_start, M_end, steps=1000):
    """2-loop RGE: dα⁻¹/dt = b/(2π) + B·α/(8π²)"""
    a = np.array(alpha_inv_start, dtype=float)
    b = np.array([b1_1L, b2_1L, b3_1L])
    if M_end <= 0 or M_start <= 0: return a
    dt = np.log(M_end / M_start) / steps
    for _ in range(steps):
        alpha = 1.0 / a
        a += (b / (2*np.pi) + (B @ alpha) / (8*np.pi**2)) * dt
    return a

def run_1loop(alpha_inv_start, M_start, M_end, b_coeff):
    if M_end <= 0 or M_start <= 0: return alpha_inv_start
    return alpha_inv_start + b_coeff / (2*np.pi) * np.log(M_end / M_start)

print("=" * 72)
print("O89-7: 2-loop RGE + Threshold — 修正版")
print("=" * 72)

# ============================================================
# 2-parameter scan: α_GUT⁻¹, M_VL
# ============================================================
print("\n## 2-parameter scan (α_GUT⁻¹, M_VL) — 2-loop SM + 1-loop VL threshold")

best_chisq = 1e30
best_aGUT = 0; best_MVL = 0

for aGUT_inv in np.arange(30, 80, 0.5):
    # SU(4)_PS: M_GUT → M_PS
    b_SU4 = 26/3
    a4p = run_1loop(aGUT_inv, M_GUT, M_PS, b_SU4)
    a3p = a4p
    a2p = a4p - np.log(2) / (2*np.pi)
    
    for log_MVL in np.arange(np.log10(M_PS), np.log10(M_R) - 1, -0.1):
        MVL = 10**log_MVL
        
        # VL threshold: M_PS → M_VL
        a3v = run_1loop(a3p, M_PS, MVL, 1.0)       # b₃=1 with VL
        a2v = run_1loop(a2p, M_PS, MVL, -29/6)     # b₂=-29/6 with VL
        
        # SM: M_VL → M_R (1-loop)
        a2r = run_1loop(a2v, MVL, M_R, b2_1L)
        a3r = run_1loop(a3v, MVL, M_R, b3_1L)
        
        # SU(2)_R → U(1)_Y matching at M_R
        a2R_ps = a2p
        a2R_mr = run_1loop(a2R_ps, M_PS, M_R, -29/6)
        a1r = a2R_mr - np.log(2) / (2*np.pi)
        
        # SM: M_R → M_Z (2-loop)
        a_start = np.array([a1r, a2r, a3r])
        a_end = run_2loop(a_start, M_R, M_Z, steps=2000)
        
        d1 = a_end[0] - a1_t; d2 = a_end[1] - a2_t; d3 = a_end[2] - a3_t
        chisq = d1**2 + d2**2 + d3**2
        
        if chisq < best_chisq:
            best_chisq = chisq
            best_aGUT = aGUT_inv
            best_MVL = MVL
            best_a = a_end.copy()
            best_d = np.array([d1, d2, d3])
            # Save intermediate values
            a4p_best = a4p; a3v_best = a3v; a2v_best = a2v
            a2r_best = a2r; a3r_best = a3r; a1r_best = a1r
            a2p_best = a2p

print(f"\n  ** Best 2-loop fit **")
print(f"  α_GUT⁻¹ = {best_aGUT:.1f}")
print(f"  M_VL = {best_MVL:.2e} GeV")
print(f"  χ² = {best_chisq:.4f}")
print(f"\n  Intermediate values:")
print(f"    α₄⁻¹(M_PS) = {a4p_best:.2f}")
print(f"    α₃⁻¹(M_VL) = {a3v_best:.2f}")
print(f"    α₂⁻¹(M_VL) = {a2v_best:.2f}")
print(f"    α₃⁻¹(M_R) = {a3r_best:.2f}")
print(f"    α₂⁻¹(M_R) = {a2r_best:.2f}")
print(f"    α₁⁻¹(M_R) = {a1r_best:.2f}")
print(f"\n  {'':<12} {'Predicted':<12} {'Target':<12} {'Δ':<10} {'%':<8}")
print(f"  {'α₁⁻¹':<12} {best_a[0]:<12.4f} {a1_t:<12.4f} {best_d[0]:<+10.4f} {abs(best_d[0])/a1_t*100:<8.2f}")
print(f"  {'α₂⁻¹':<12} {best_a[1]:<12.4f} {a2_t:<12.4f} {best_d[1]:<+10.4f} {abs(best_d[1])/a2_t*100:<8.2f}")
print(f"  {'α₃⁻¹':<12} {best_a[2]:<12.4f} {a3_t:<12.4f} {best_d[2]:<+10.4f} {abs(best_d[2])/a3_t*100:<8.2f}")

# ============================================================
# M_VL structural relation
# ============================================================
geo_mean = np.sqrt(M_PS * M_R)
print(f"\n  M_VL / √(M_PS × M_R) = {best_MVL / geo_mean:.4f}")
print(f"  √(M_PS × M_R) = {geo_mean:.2e}")

# ============================================================
# Compare with 1-loop result
# ============================================================
print("\n" + "=" * 72)
print("1-loop vs 2-loop comparison")
print("=" * 72)

# 1-loop with same parameters
a3v_1 = run_1loop(a4p_best, M_PS, best_MVL, 1.0)
a2v_1 = run_1loop(a2p_best, M_PS, best_MVL, -29/6)
a2r_1 = run_1loop(a2v_1, best_MVL, M_R, b2_1L)
a3r_1 = run_1loop(a3v_1, best_MVL, M_R, b3_1L)
a2R_mr_1 = run_1loop(a2p_best, M_PS, M_R, -29/6)
a1r_1 = a2R_mr_1 - np.log(2)/(2*np.pi)
a1_1 = run_1loop(a1r_1, M_R, M_Z, b1_1L)
a2_1 = run_1loop(a2r_1, M_R, M_Z, b2_1L)
a3_1 = run_1loop(a3r_1, M_R, M_Z, b3_1L)

print(f"\n  {'':<12} {'1-loop':<12} {'2-loop':<12} {'Target':<12} {'1-loop Δ':<10} {'2-loop Δ':<10}")
print("  " + "-" * 68)
print(f"  {'α₁⁻¹':<12} {a1_1:<12.4f} {best_a[0]:<12.4f} {a1_t:<12.4f} {a1_1-a1_t:<+10.4f} {best_d[0]:<+10.4f}")
print(f"  {'α₂⁻¹':<12} {a2_1:<12.4f} {best_a[1]:<12.4f} {a2_t:<12.4f} {a2_1-a2_t:<+10.4f} {best_d[1]:<+10.4f}")
print(f"  {'α₃⁻¹':<12} {a3_1:<12.4f} {best_a[2]:<12.4f} {a3_t:<12.4f} {a3_1-a3_t:<+10.4f} {best_d[2]:<+10.4f}")

# ============================================================
# Save
# ============================================================
results = {
    'scales': {
        'M_Planck': M_Planck, 'M_GUT': M_GUT, 'M_PS': M_PS,
        'M_VL': float(best_MVL), 'M_R': M_R, 'M_Z': M_Z
    },
    'best_fit': {
        'alpha_GUT_inv': float(best_aGUT),
        'M_VL': float(best_MVL),
        'M_VL_over_geo_mean_MPS_MR': float(best_MVL / geo_mean),
        'a1_inv_MZ': float(best_a[0]), 'a2_inv_MZ': float(best_a[1]), 'a3_inv_MZ': float(best_a[2]),
        'd1': float(best_d[0]), 'd2': float(best_d[1]), 'd3': float(best_d[2]),
        'd1_pct': float(abs(best_d[0])/a1_t*100),
        'd2_pct': float(abs(best_d[1])/a2_t*100),
        'd3_pct': float(abs(best_d[2])/a3_t*100),
        'chisq': float(best_chisq)
    },
    'intermediate': {
        'a4_inv_PS': float(a4p_best), 'a3_inv_VL': float(a3v_best),
        'a2_inv_VL': float(a2v_best), 'a3_inv_R': float(a3r_best),
        'a2_inv_R': float(a2r_best), 'a1_inv_R': float(a1r_best)
    },
    'status': '🟢' if best_chisq < 5 else '🟡',
    'conclusion': (
        f"2-loop RGE + VL threshold: α_GUT⁻¹={best_aGUT:.1f}, "
        f"M_VL={best_MVL:.2e}≈√(M_PS×M_R), χ²={best_chisq:.2f}. "
        f"α₁⁻¹ {abs(best_d[0])/a1_t*100:.1f}%, "
        f"α₂⁻¹ {abs(best_d[1])/a2_t*100:.1f}%, "
        f"α₃⁻¹ {abs(best_d[2])/a3_t*100:.1f}%"
    )
}

out_path = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o89_mass_hierarchy_coupling/data/07_twoloop_closure.json'
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n✅ 結果已保存到 {out_path}")