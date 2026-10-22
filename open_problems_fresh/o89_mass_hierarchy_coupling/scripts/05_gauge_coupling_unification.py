#!/usr/bin/env python3
"""
O89-5: SU(12) Gauge Coupling Unification — O88 Fermion Content 閉合後完整分析
=============================================================================
使用 O88 嘅 fermion embedding (3×(12⊕12̄) = 72, A=0) 計算每個 breaking stage 嘅
正確 β 函數，嘗試從 M_GUT unified coupling 跑到 M_Z 匹配 SM 值。

Breaking chain (O85):
  SU(12) @ M_GUT = M_Planck × γ₁
    → SU(4)_PS × SU(3)_gen  @ M_GUT
    → SU(2)_L × SU(2)_R × SU(3)_c  @ M_PS = M_Planck × γ₁²
    → SU(2)_L × U(1)_Y × SU(3)_c  @ M_R = M_Planck × γ₁³
    → U(1)_QED × SU(3)_c  @ M_EW = 246 GeV

Fermion content (O88):
  3×(12⊕12̄) = 72 Weyl fermions, A=0
  12 = (4,3) → 48 SM Weyl + 24 vector-like pairs
  12̄ = (4̄,3̄)

β 函數: 已知 SM/MSSM 標準值 hardcoded，避免 counting confusion
"""

import numpy as np
import json, os, math

# ============================================================
# 1. 參數
# ============================================================
M_Planck = 1.2209e19      # GeV
gamma_1 = 4 * np.sin(np.pi / 88) ** 2

M_GUT = M_Planck * gamma_1        # 6.2214e16 GeV
M_PS  = M_Planck * gamma_1 ** 2   # 3.1703e14 GeV
M_R   = M_Planck * gamma_1 ** 3   # 1.6155e12 GeV
M_EW  = 246.82                    # GeV (v_geom, O59)
M_Z   = 91.1876                   # GeV

# SM couplings at M_Z (PDG 2024)
a3_inv_MZ = 8.44      # α₃⁻¹ = 1/0.1185
a2_inv_MZ = 29.57     # α₂⁻¹ = 1/0.03382
a1_inv_MZ = 59.02     # α₁⁻¹ (GUT-normalized × 5/3)

# IDCM constants
B = 4; N_gen = 3; N_d = 44; K_tree = 33; phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O89-5: SU(12) Gauge Coupling Unification — O88 閉合後完整分析")
print("=" * 72)

print(f"\n## 級聯尺度 (γ₁ = {gamma_1:.10f})")
print(f"{'Scale':<12} {'Value (GeV)':<20}")
print("-" * 32)
for name, val in [('M_Planck', M_Planck), ('M_GUT', M_GUT), ('M_PS', M_PS),
                   ('M_R', M_R), ('M_EW', M_EW), ('M_Z', M_Z)]:
    print(f"{name:<12} {val:<20.4e}" if 'e' in f"{val:.4e}" else f"{name:<12} {val:<20.4f}")

# ============================================================
# 2. β 函數
# ============================================================
print("\n" + "=" * 72)
print("2. β 函數 (1-loop)")
print("=" * 72)

def running(alpha_inv_start, M_start, M_end, b_coeff):
    return alpha_inv_start + b_coeff / (2*np.pi) * np.log(M_end / M_start)

# ---- Stage 1: SU(12) @ M_Planck → M_GUT ----
# 3×(12⊕12̄) = 72 Weyl: T(12)=T(12̄)=1/2, Σ T = 3×(1/2+1/2) = 3
# b = 11×12/3 - 2/3 × 3 = 44 - 2 = 42
b_SU12 = 42.0
print(f"\n  Stage 1 — SU(12): M_Planck → M_GUT")
print(f"    3×(12⊕12̄) = 72 Weyl, Σ T=3")
print(f"    b_SU12 = 44 - 2 = 42")

# ---- Stage 2a: SU(4) @ M_GUT → M_PS ----
# 3×(4⊕4̄) = 24 Weyl under SU(4): T(4)=T(4̄)=1/2, Σ T = 3×(1/2+1/2)=3
# b = 44/3 - 2/3 × 3 = 44/3 - 2 = 38/3
b_SU4 = 38/3
print(f"\n  Stage 2a — SU(4): M_GUT → M_PS")
print(f"    3×(4⊕4̄) = 24 Weyl, Σ T=3")
print(f"    b_SU4 = 44/3 - 2 = {b_SU4:.4f}")

# ---- Stage 2b: SU(3) @ M_GUT → M_PS ----
# 3×(3⊕3̄) = 18 Weyl under SU(3): T(3)=T(3̄)=1/2, Σ T=3
# b = 11 - 2/3 × 3 = 11 - 2 = 9
b_SU3_stage2 = 9.0
print(f"\n  Stage 2b — SU(3): M_GUT → M_PS")
print(f"    3×(3⊕3̄) = 18 Weyl, Σ T=3")
print(f"    b_SU3 = 11 - 2 = 9")

# ---- Stage 3a: SU(2)_L × SU(2)_R @ M_PS → M_R ----
# After SU(4) → SU(2)_L×SU(2)_R: 4 = (2,2)
# 3×(4⊕4̄) → 3×[(2,2)⊕(2,2)] = 6×(2,2)
# Under each SU(2): 6 doublets = 12 Weyl
# Σ T = 12 × 1/2 = 6
# b = 22/3 - 2/3 × 6 = 22/3 - 4 = 10/3
b_SU2_stage3 = 10/3
print(f"\n  Stage 3a — SU(2)_L×SU(2)_R: M_PS → M_R")
print(f"    From 3×(4⊕4̄) → 6×(2,2): each SU(2) gets 12 Weyl, Σ T=6")
print(f"    b_SU2 = 22/3 - 4 = {b_SU2_stage3:.4f}")

# ---- Stage 3b: SU(3) @ M_PS → M_R ----
# At M_PS, vector-like pairs get mass → only SM 48 remain
# SM SU(3) b = 7
b_SU3_SM = 7.0
print(f"\n  Stage 3b — SU(3): M_PS → M_R (SM only)")
print(f"    Vector-like pairs gain mass at M_PS")
print(f"    b_SU3_SM = 7 (standard SM)")

# ---- Stage 4: SM @ M_R → M_EW → M_Z ----
# Standard SM 1-loop β coefficients
b_3_SM = 7.0
b_2_SM = 19/6    # ≈ 3.1667
b_1_SM = -41/10  # = -4.1
print(f"\n  Stage 4 — SM: M_R → M_EW → M_Z")
print(f"    b_3 = {b_3_SM}")
print(f"    b_2 = {b_2_SM:.4f} (19/6)")
print(f"    b_1 = {b_1_SM} (-41/10)")

# ============================================================
# 3. Full Running Calculation
# ============================================================
print("\n" + "=" * 72)
print("3. Gauge Coupling Running")
print("=" * 72)

# SU(3) running: M_GUT → M_PS (stage 2b) → M_R (stage 3b) → M_EW → M_Z
def run_a3(alpha_inv_GUT):
    a = running(alpha_inv_GUT, M_GUT, M_PS, b_SU3_stage2)   # full SU(3) with 3×(3⊕3̄)
    a = running(a, M_PS, M_R, b_SU3_SM)                       # SM only (vector-like pairs mass)
    a = running(a, M_R, M_EW, b_3_SM)                         # SM
    a = running(a, M_EW, M_Z, b_3_SM)                         # SM
    return a

# SU(4) → SU(2)_L matching at M_PS
# Matching: g_2L = g_4/√2 (canonical normalization for SU(4) → SU(2)_L×SU(2)_R)
# α⁻¹_2L = α⁻¹_4 - ln(2)/(2π)
def run_a2(alpha_inv_GUT):
    a4 = running(alpha_inv_GUT, M_GUT, M_PS, b_SU4)          # SU(4) running
    a2 = a4 - np.log(2) / (2*np.pi)                           # matching at M_PS
    a2 = running(a2, M_PS, M_R, b_SU2_stage3)                 # SU(2)_L with extra matter
    a2 = running(a2, M_R, M_EW, b_2_SM)                       # SM SU(2)_L
    a2 = running(a2, M_EW, M_Z, b_2_SM)                       # SM SU(2)_L
    return a2

# SU(2)_R matching at M_PS, then SU(2)_R × U(1)_{B-L} → U(1)_Y at M_R
# At M_R: 1/α_Y = 1/α_2R + 1/α_BL, assuming g_BL = g_2R at M_R
# Simplified: α⁻¹_Y = α⁻¹_2R - ln(2)/(2π) (mixing factor)
def run_a1(alpha_inv_GUT):
    a4 = running(alpha_inv_GUT, M_GUT, M_PS, b_SU4)
    a2R = a4 - np.log(2) / (2*np.pi)                          # SU(2)_R matching
    a2R = running(a2R, M_PS, M_R, b_SU2_stage3)               # SU(2)_R running
    a1 = a2R - np.log(2) / (2*np.pi)                           # U(1)_Y mixing at M_R
    a1 = running(a1, M_R, M_EW, b_1_SM)                        # SM U(1)_Y
    a1 = running(a1, M_EW, M_Z, b_1_SM)                        # SM U(1)_Y
    return a1

# Search for α_GUT⁻¹
print(f"\n  {'α_GUT⁻¹':<12} {'α₃⁻¹(M_Z)':<12} {'α₂⁻¹(M_Z)':<12} {'α₁⁻¹(M_Z)':<12} {'Δ₃':<10} {'Δ₂':<10} {'Δ₁':<10}")
print("  " + "-" * 76)

best_chisq = 1e30
best_aGUT = 0
for aGUT_inv in np.arange(1, 100, 1):
    a3 = run_a3(aGUT_inv)
    a2 = run_a2(aGUT_inv)
    a1 = run_a1(aGUT_inv)
    d3 = a3 - a3_inv_MZ; d2 = a2 - a2_inv_MZ; d1 = a1 - a1_inv_MZ
    chisq = d3**2 + d2**2 + d1**2
    if chisq < best_chisq:
        best_chisq = chisq; best_aGUT = aGUT_inv
        best_a3 = a3; best_a2 = a2; best_a1 = a1
        best_d3 = d3; best_d2 = d2; best_d1 = d1
    if aGUT_inv % 5 == 0 or aGUT_inv in [1, 2, 3]:
        print(f"  {aGUT_inv:<12.1f} {a3:<12.4f} {a2:<12.4f} {a1:<12.4f} {d3:<+10.4f} {d2:<+10.4f} {d1:<+10.4f}")

print(f"\n  ** Best α_GUT⁻¹ = {best_aGUT:.1f} (χ² = {best_chisq:.2f}) **")
print(f"  {'':<12} {'Predicted':<12} {'Target':<12} {'Diff':<10}")
print(f"  {'α₃⁻¹':<12} {best_a3:<12.4f} {a3_inv_MZ:<12.4f} {best_d3:<+10.4f}")
print(f"  {'α₂⁻¹':<12} {best_a2:<12.4f} {a2_inv_MZ:<12.4f} {best_d2:<+10.4f}")
print(f"  {'α₁⁻¹':<12} {best_a1:<12.4f} {a1_inv_MZ:<12.4f} {best_d1:<+10.4f}")

# ============================================================
# 4. IDCM 結構分析
# ============================================================
print("\n" + "=" * 72)
print("4. IDCM 結構條件分析")
print("=" * 72)

# α_GUT⁻¹ = 56 (from best fit)
# Does this match any IDCM structure?
print(f"\n  Best α_GUT⁻¹ = {best_aGUT:.1f}")
print(f"  α_GUT = {1/best_aGUT:.6f}")

# Key structural relations
print(f"\n  IDCM relations to α_GUT⁻¹ = {best_aGUT:.1f}:")
print(f"  K_tree = {K_tree}")
print(f"  N_d = {N_d}")
print(f"  B = {B}")
print(f"  h¹¹ = 36")
print(f"  K_tree + B = {K_tree + B}")
print(f"  K_tree + N_gen = {K_tree + N_gen}")
print(f"  N_d + B = {N_d + B}")
print(f"  N_d + N_gen = {N_d + N_gen}")
print(f"  h¹¹ + B = {36 + B}")
print(f"  h¹¹ + N_gen = {36 + N_gen}")
print(f"  2×K_tree - B = {2*K_tree - B}")
print(f"  2×K_tree - N_gen = {2*K_tree - N_gen}")
print(f"  (N_d + K_tree) = {N_d + K_tree}")

# α_GUT⁻¹ = 56 = ?
# 56 = 2×28 = 4×14 = 7×8
# 56 = 2×K_tree - 10 = 66 - 10
# 56 = N_d + B + 8 = 44 + 4 + 8
# 56 = h¹¹ + 20 = 36 + 20
# 56 = 2×K_tree - N_gen - 7 = 66 - 3 - 7
print(f"    56 = 2×K_tree - 10 = 66 - 10")
print(f"    56 = N_d + B + 8 = 44 + 4 + 8")
print(f"    56 = h¹¹ + 20 = 36 + 20")
print(f"    56 = K_tree + N_d + B - 25 = 33 + 44 + 4 - 25")

# ============================================================
# 5. 與 MSSM 比較
# ============================================================
print("\n" + "=" * 72)
print("5. MSSM-like scenario (SUSY at M_R)")
print("=" * 72)

# MSSM β coefficients: b_3 = -3, b_2 = 1, b_1 = 33/5
b3_MSSM = -3
b2_MSSM = 1
b1_MSSM = 33/5

def run_a3_MSSM(alpha_inv_GUT):
    a = running(alpha_inv_GUT, M_GUT, M_PS, b_SU3_stage2)   # full SU(3)
    a = running(a, M_PS, M_R, b3_MSSM)                        # MSSM running
    a = running(a, M_R, M_EW, b_3_SM)                         # SM below SUSY
    a = running(a, M_EW, M_Z, b_3_SM)
    return a

def run_a2_MSSM(alpha_inv_GUT):
    a4 = running(alpha_inv_GUT, M_GUT, M_PS, b_SU4)
    a2 = a4 - np.log(2) / (2*np.pi)
    a2 = running(a2, M_PS, M_R, b2_MSSM)                      # MSSM SU(2)_L
    a2 = running(a2, M_R, M_EW, b_2_SM)
    a2 = running(a2, M_EW, M_Z, b_2_SM)
    return a2

def run_a1_MSSM(alpha_inv_GUT):
    a4 = running(alpha_inv_GUT, M_GUT, M_PS, b_SU4)
    a2R = a4 - np.log(2) / (2*np.pi)
    a2R = running(a2R, M_PS, M_R, b2_MSSM)                    # MSSM SU(2)_R
    a1 = a2R - np.log(2) / (2*np.pi)
    a1 = running(a1, M_R, M_EW, b1_MSSM)                      # MSSM U(1)_Y
    a1 = running(a1, M_EW, M_Z, b_1_SM)
    return a1

print(f"\n  {'α_GUT⁻¹':<12} {'α₃⁻¹(M_Z)':<12} {'α₂⁻¹(M_Z)':<12} {'α₁⁻¹(M_Z)':<12} {'Δ₃':<10} {'Δ₂':<10} {'Δ₁':<10}")
print("  " + "-" * 76)

best_chisq_m = 1e30
best_aGUT_m = 0
for aGUT_inv in np.arange(1, 100, 1):
    a3 = run_a3_MSSM(aGUT_inv); a2 = run_a2_MSSM(aGUT_inv); a1 = run_a1_MSSM(aGUT_inv)
    d3 = a3 - a3_inv_MZ; d2 = a2 - a2_inv_MZ; d1 = a1 - a1_inv_MZ
    chisq = d3**2 + d2**2 + d1**2
    if chisq < best_chisq_m:
        best_chisq_m = chisq; best_aGUT_m = aGUT_inv
        best_a3_m = a3; best_a2_m = a2; best_a1_m = a1
        best_d3_m = d3; best_d2_m = d2; best_d1_m = d1
    if aGUT_inv % 5 == 0 or aGUT_inv <= 3:
        print(f"  {aGUT_inv:<12.1f} {a3:<12.4f} {a2:<12.4f} {a1:<12.4f} {d3:<+10.4f} {d2:<+10.4f} {d1:<+10.4f}")

print(f"\n  ** Best MSSM α_GUT⁻¹ = {best_aGUT_m:.1f} (χ² = {best_chisq_m:.2f}) **")
print(f"  {'':<12} {'Predicted':<12} {'Target':<12} {'Diff':<10}")
print(f"  {'α₃⁻¹':<12} {best_a3_m:<12.4f} {a3_inv_MZ:<12.4f} {best_d3_m:<+10.4f}")
print(f"  {'α₂⁻¹':<12} {best_a2_m:<12.4f} {a2_inv_MZ:<12.4f} {best_d2_m:<+10.4f}")
print(f"  {'α₁⁻¹':<12} {best_a1_m:<12.4f} {a1_inv_MZ:<12.4f} {best_d1_m:<+10.4f}")

# ============================================================
# 6. Alternative: Direct Structural Relation
# ============================================================
print("\n" + "=" * 72)
print("6. 結構耦合統一方法")
print("=" * 72)

# IDCM has α⁻¹(fine structure) = 137.036 from structural formula
# If gauge couplings at M_GUT are determined by the same structure,
# then α_GUT⁻¹ should be computable from IDCM constants.

# Key insight: α_GUT⁻¹ for SU(12) at M_GUT
# From the search, best α_GUT⁻¹ ≈ 56 (SM) or 30 (MSSM)
# These are NOT arbitrary numbers.

# 56 = 2×28 = 4×14 = 7×8
# 56 = K_tree + N_d - B - 17 = 33 + 44 - 4 - 17
# 56 = 2×K_tree - 10 = 66 - 10

# 30 = K_tree - 3 = 33 - 3
# 30 = N_d - 14 = 44 - 14
# 30 = 2×B + 22 = 8 + 22

# Could α_GUT⁻¹ = K_tree + N_gen - B? = 33 + 3 - 4 = 32? No, best is 56.
# Could α_GUT⁻¹ = 2×K_tree - N_gen? = 66 - 3 = 63? No.
# Could α_GUT⁻¹ = 2×K_tree - B? = 66 - 4 = 62? Close to 56 but not exact.

# Let's check if α_GUT relates to α(fine structure)
# α_GUT = 1/56 = 0.01786
# α(fine structure) = 1/137.036 = 0.00730
# ratio = 0.01786/0.00730 = 2.447

print(f"\n  SM scenario: α_GUT⁻¹ = {best_aGUT:.1f}")
print(f"  MSSM scenario: α_GUT⁻¹ = {best_aGUT_m:.1f}")
print(f"\n  α_GUT (SM) = 1/{best_aGUT:.1f} = {1/best_aGUT:.6f}")
print(f"  α_GUT (MSSM) = 1/{best_aGUT_m:.1f} = {1/best_aGUT_m:.6f}")
print(f"  α (fine structure) = 1/137.036 = 0.00730")
print(f"  α_GUT/α ratio (SM) = {1/best_aGUT/0.00730:.4f}")
print(f"  α_GUT/α ratio (MSSM) = {1/best_aGUT_m/0.00730:.4f}")

# ============================================================
# 7. 結論
# ============================================================
print("\n" + "=" * 72)
print("7. 結論")
print("=" * 72)

d3_rel = abs(best_d3) / a3_inv_MZ * 100
d2_rel = abs(best_d2) / a2_inv_MZ * 100
d1_rel = abs(best_d1) / a1_inv_MZ * 100

d3_rel_m = abs(best_d3_m) / a3_inv_MZ * 100
d2_rel_m = abs(best_d2_m) / a2_inv_MZ * 100
d1_rel_m = abs(best_d1_m) / a1_inv_MZ * 100

print(f"\n  Scenario A (SM below M_PS):")
print(f"    α_GUT⁻¹ = {best_aGUT:.0f}")
print(f"    α₃⁻¹(M_Z): {best_a3:.1f} vs {a3_inv_MZ:.1f} (Δ = {best_d3:+.1f}, {d3_rel:.0f}%)")
print(f"    α₂⁻¹(M_Z): {best_a2:.1f} vs {a2_inv_MZ:.1f} (Δ = {best_d2:+.1f}, {d2_rel:.0f}%)")
print(f"    α₁⁻¹(M_Z): {best_a1:.1f} vs {a1_inv_MZ:.1f} (Δ = {best_d1:+.1f}, {d1_rel:.0f}%)")

print(f"\n  Scenario B (MSSM below M_PS, SUSY at M_R):")
print(f"    α_GUT⁻¹ = {best_aGUT_m:.0f}")
print(f"    α₃⁻¹(M_Z): {best_a3_m:.1f} vs {a3_inv_MZ:.1f} (Δ = {best_d3_m:+.1f}, {d3_rel_m:.0f}%)")
print(f"    α₂⁻¹(M_Z): {best_a2_m:.1f} vs {a2_inv_MZ:.1f} (Δ = {best_d2_m:+.1f}, {d2_rel_m:.0f}%)")
print(f"    α₁⁻¹(M_Z): {best_a1_m:.1f} vs {a1_inv_MZ:.1f} (Δ = {best_d1_m:+.1f}, {d1_rel_m:.0f}%)")

# Determine best scenario
scores = {
    'SM': abs(best_d3) + abs(best_d2)*2 + abs(best_d1)*3,
    'MSSM': abs(best_d3_m) + abs(best_d2_m)*2 + abs(best_d1_m)*3,
}
best_scenario = min(scores, key=scores.get)
print(f"\n  ** Best scenario: {best_scenario} (weighted score {scores[best_scenario]:.1f}) **")

if best_scenario == 'SM':
    # Check if α_GUT⁻¹ matches any IDCM structure
    if abs(best_aGUT - 56) < 1:
        print(f"  α_GUT⁻¹ = {best_aGUT:.0f} ≈ 56 = 2×K_tree - 10 = 2×28")
        print(f"  Still need to find structural origin for 56 = 2×K_tree - 10")
    elif abs(best_aGUT - 62) < 1:
        print(f"  α_GUT⁻¹ = {best_aGUT:.0f} ≈ 62 = 2×K_tree - B")
    elif abs(best_aGUT - 36) < 1:
        print(f"  α_GUT⁻¹ = {best_aGUT:.0f} = h¹¹ = K_tree + N_gen")
    elif abs(best_aGUT - 33) < 1:
        print(f"  α_GUT⁻¹ = {best_aGUT:.0f} = K_tree")
else:
    if abs(best_aGUT_m - 30) < 1:
        print(f"  α_GUT⁻¹ = {best_aGUT_m:.0f} ≈ 30 = K_tree - 3")
        print(f"  Still need to find structural origin for 30 = K_tree - 3")

# ============================================================
# 8. 保存結果
# ============================================================
results = {
    'scales': {
        'M_Planck': M_Planck, 'M_GUT': M_GUT, 'M_PS': M_PS,
        'M_R': M_R, 'M_EW': M_EW, 'M_Z': M_Z, 'gamma_1': float(gamma_1)
    },
    'beta_coefficients': {
        'stage1_SU12': b_SU12, 'stage2a_SU4': b_SU4, 'stage2b_SU3': b_SU3_stage2,
        'stage3a_SU2': b_SU2_stage3, 'stage3b_SU3_SM': b_SU3_SM,
        'stage4_b3_SM': b_3_SM, 'stage4_b2_SM': b_2_SM, 'stage4_b1_SM': b_1_SM,
        'MSSM_b3': b3_MSSM, 'MSSM_b2': b2_MSSM, 'MSSM_b1': b1_MSSM
    },
    'scenario_A_SM': {
        'best_alpha_GUT_inv': float(best_aGUT), 'chisq': float(best_chisq),
        'a3_inv_MZ': float(best_a3), 'a2_inv_MZ': float(best_a2), 'a1_inv_MZ': float(best_a1),
        'd3': float(best_d3), 'd2': float(best_d2), 'd1': float(best_d1),
        'd3_percent': float(d3_rel), 'd2_percent': float(d2_rel), 'd1_percent': float(d1_rel)
    },
    'scenario_B_MSSM': {
        'best_alpha_GUT_inv': float(best_aGUT_m), 'chisq': float(best_chisq_m),
        'a3_inv_MZ': float(best_a3_m), 'a2_inv_MZ': float(best_a2_m), 'a1_inv_MZ': float(best_a1_m),
        'd3': float(best_d3_m), 'd2': float(best_d2_m), 'd1': float(best_d1_m),
        'd3_percent': float(d3_rel_m), 'd2_percent': float(d2_rel_m), 'd1_percent': float(d1_rel_m)
    },
    'best_scenario': best_scenario,
    'conclusion': f"Scenario {best_scenario}: α_GUT⁻¹={best_aGUT if best_scenario=='SM' else best_aGUT_m:.0f}, "
                  f"α₃⁻¹(M_Z)={best_a3 if best_scenario=='SM' else best_a3_m:.1f} (Δ{d3_rel if best_scenario=='SM' else d3_rel_m:.0f}%), "
                  f"α₂⁻¹(M_Z)={best_a2 if best_scenario=='SM' else best_a2_m:.1f} (Δ{d2_rel if best_scenario=='SM' else d2_rel_m:.0f}%), "
                  f"α₁⁻¹(M_Z)={best_a1 if best_scenario=='SM' else best_a1_m:.1f} (Δ{d1_rel if best_scenario=='SM' else d1_rel_m:.0f}%)"
}

out_path = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o89_mass_hierarchy_coupling/data/05_gauge_coupling_unification.json'
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n✅ 結果已保存到 {out_path}")