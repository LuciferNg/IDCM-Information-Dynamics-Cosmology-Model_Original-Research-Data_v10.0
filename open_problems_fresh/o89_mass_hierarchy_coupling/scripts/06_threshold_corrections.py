#!/usr/bin/env python3
"""
O89-6: Threshold Corrections — Vector-like Fermion 退耦求解
============================================================
求解使 α₃⁻¹(M_Z) = 8.44 精確閉合嘅 VL fermion 質量標度 M_VL。

修正 script 05 嘅概念錯誤：
  - SU(3)_c 喺 M_GUT→M_PS 階段嵌入 SU(4)_PS，唔獨立 running
  - 正確 running: SU(4)_PS → [M_PS] → SU(3)_c + SU(2)_L + SU(2)_R → [M_VL] → SM

VL fermion content (O88):
  24 對 VL = 18 夸克 (9 in 3 + 9 in 3̄) + 6 輕子 (SU(2)_L doublets)
  SU(3)_c: 9 VL flavors → b_3 = 11 - 2/3 × (6+9) = 1 (with VL)
  SU(2)_L: 12 VL doublets → b_2 受 VL 影響
"""

import numpy as np
import json, os, math

# ============================================================
# 1. 參數
# ============================================================
M_Planck = 1.2209e19
gamma_1 = 4 * np.sin(np.pi / 88) ** 2

M_GUT = M_Planck * gamma_1          # 6.2214e16 GeV
M_PS  = M_Planck * gamma_1 ** 2     # 3.1703e14 GeV
M_R   = M_Planck * gamma_1 ** 3     # 1.6155e12 GeV
M_EW  = 246.82                      # GeV
M_Z   = 91.1876                     # GeV

# SM couplings at M_Z (PDG 2024)
a3_inv_MZ = 8.44
a2_inv_MZ = 29.57
a1_inv_MZ = 59.02

# IDCM constants
B = 4; N_gen = 3; N_d = 44; K_tree = 33
F_7 = 13

print("=" * 72)
print("O89-6: Vector-like Fermion Threshold Corrections 求解")
print("=" * 72)

print(f"\n## 固定尺度")
print(f"{'M_Planck':<12} = {M_Planck:<12.4e} GeV")
print(f"{'M_GUT':<12} = {M_GUT:<12.4e} GeV (M_Planck × γ₁)")
print(f"{'M_PS':<12} = {M_PS:<12.4e} GeV (M_Planck × γ₁²)")
print(f"{'M_R':<12} = {M_R:<12.4e} GeV (M_Planck × γ₁³)")
print(f"{'M_EW':<12} = {M_EW:<12.4f} GeV")
print(f"{'M_Z':<12} = {M_Z:<12.4f} GeV")

# ============================================================
# 2. 正確 β 函數
# ============================================================
print("\n" + "=" * 72)
print("2. 正確 β 函數 (1-loop)")
print("=" * 72)

def running(alpha_inv_start, M_start, M_end, b_coeff):
    """1-loop running"""
    if M_end <= 0 or M_start <= 0:
        return alpha_inv_start
    return alpha_inv_start + b_coeff / (2*np.pi) * np.log(M_end / M_start)

# ---- Stage 1: SU(12) @ M_Planck → M_GUT ----
# 3×(12⊕12̄) = 72 Weyl, T=1/2 each
# Σ T = 3×(1/2+1/2) = 3
# b = 11×12/3 - 2/3 × 3 = 44 - 2 = 42
b_SU12 = 42.0
print(f"\n  Stage 1 — SU(12): M_Planck → M_GUT")
print(f"    3×(12⊕12̄) = 72 Weyl, Σ T=3 → b_SU12 = {b_SU12}")

# ---- Stage 2: SU(4)_PS @ M_GUT → M_PS ----
# 12 = (4,3) under SU(4)_PS × SU(3)_gen
# Under SU(4)_PS: 3 copies of 4 (from SU(3)_gen index)
# 3×12 = 3×3×4 = 9 in 4
# 3×12̄ = 3×3×4̄ = 9 in 4̄
# Σ T = 9×1/2 + 9×1/2 = 9
# b = 44/3 - 2/3 × 9 = 44/3 - 6 = 26/3
b_SU4 = 26/3
print(f"\n  Stage 2 — SU(4)_PS: M_GUT → M_PS")
print(f"    9 in 4 + 9 in 4̄ = 18 Weyl, Σ T=9 → b_SU4 = {b_SU4:.4f}")

# ---- Stage 3a: SU(3)_c with VL [M_PS → M_VL] ----
# Under SU(3)_c from the 3×(12⊕12̄) decomposition:
# 12 = (3,3)_{1/3} + (1,3)_{-1} → 3×3×3 = 9 in 3 per 12
# 3×12 → 3×9 = 27 in 3
# 3×12̄ → 3×9 = 27 in 3̄
# Total: 27 in 3 + 27 in 3̄ = 54 Weyl = 27 "flavors"
# But SM has 6 flavors, VL has 21? No...
# 
# Actually, the SM SU(3) content from these is:
# - Q_L: 3 gen × 3 colors = 9 in 3 (left) → but these are from the 3×(12) part
# - u^c_R: 3 gen × 3 colors = 9 in 3̄ (right as left-conjugate) → from 3×(12̄)
# - d^c_R: 3 gen × 3 colors = 9 in 3̄ → from 3×(12̄)
# Total SM: 9 in 3 + 18 in 3̄ = 27 Weyl = 9 flavors (3 gen × 3 colors)
# 
# Correcting: SM has 6 flavors (u,d,c,s,t,b), each with 3 colors, 
# which is 6 × (1 in 3 + 1 in 3̄) = 6 in 3 + 6 in 3̄ = 12 Weyl, Σ T = 6
# b_3_SM = 11 - 2/3 × 6 = 7 ✓
#
# VL: 27 - 6 = 21 in 3 + 27 - 6 = 21 in 3̄ = 42 Weyl, Σ T = 21
# But wait, that's 21 VL "flavors" which is too many.
#
# The issue: in the β function, each "flavor" = 1 left in 3 + 1 right in 3̄ = 2 Weyl = T=1
# SM has 6 flavors → Σ T = 6 → b = 11 - 4 = 7 ✓
# The full 3×(12⊕12̄) has 27 in 3 + 27 in 3̄ = 27 "flavors" → Σ T = 27 → b = 11 - 18 = -7
# VL = 27 - 6 = 21 flavors → Σ T = 21 → b = 11 - 14 = -3
#
# With VL active: b_3 = 11 - 2/3 × (6+21) = 11 - 18 = -7
# With VL decoupled: b_3 = 11 - 2/3 × 6 = 7
#
# But b_3 = -7 is very negative. This means SU(3)_c is NOT asymptotically free
# with all fermions active. The coupling grows at high energy.
# 
# For the running from M_PS down to M_VL, b_3 < 0 means α₃⁻¹ INCREASES
# as we go to lower energies (since ln(M_VL/M_PS) < 0, b < 0 → α⁻¹ increases).
# This is the OPPOSITE of what we need (we need α₃⁻¹ to decrease from M_PS to M_Z).
# 
# Actually, with b_3 = -7, running from M_PS down to M_Z:
# α⁻¹(M_Z) = α⁻¹(M_PS) + (-7)/(2π) × ln(M_Z/M_PS)
# Since M_Z < M_PS, ln(M_Z/M_PS) < 0, and (-7) × (negative) = positive
# So α⁻¹(M_Z) > α⁻¹(M_PS), meaning α(M_Z) < α(M_PS)
# This is WRONG — QCD should be stronger at low energies.
#
# This means the full 3×(12⊕12̄) content makes SU(3)_c IR-free, which is unphysical.
# The VL fermions MUST decouple at or near M_PS for QCD to be confining.
#
# Let's use the physically correct approach: VL decouple at M_PS,
# so below M_PS we have SM only.

# ---- Corrected: SU(3)_c below M_PS ----
# SM only: b_3 = 7 (standard)
b_3_SM = 7.0

# But if VL decouple at M_VL somewhere between M_PS and M_R:
# With VL active (above M_VL): 6 SM + 9 VL = 15 flavors? No...
# 
# Let me think about this differently. The 24 VL pairs from O88:
# 18 quarks (9 in 3 + 9 in 3̄) + 6 leptons
# Under SU(3)_c, the 18 VL quarks are 9 in 3 + 9 in 3̄ = 9 "flavors"
# 9 VL flavors × T=1 each = Σ T_VL = 9
# 
# With VL active: Σ T = 6 (SM) + 9 (VL) = 15
# b_3 = 11 - 2/3 × 15 = 11 - 10 = 1
# 
# This is better! b_3 = 1 means very slow running, almost flat.
# The coupling barely changes with energy.
# 
# With VL decoupled: b_3 = 7 (SM only)
# The coupling grows quickly at low energies.
# 
# Recalculating VL content:
# 3×(12⊕12̄) = 72 Weyl
# SM: 48 Weyl (36 SU(3) charged, 12 SU(3) neutral)
# VL: 24 Weyl (18 SU(3) charged, 6 SU(3) neutral)
# 
# Under SU(3)_c:
# SM: 18 in 3 + 18 in 3̄ = 36 Weyl = 18 "flavors" (but this is counting colors separately!)
# No, in the β function, colors are NOT counted separately.
# SM has 6 flavors → 6 in 3 + 6 in 3̄ = 12 Weyl, Σ T = 6
# 
# VL: 9 in 3 + 9 in 3̄ = 18 Weyl = 9 "flavors", Σ T = 9
# Total: 15 in 3 + 15 in 3̄ = 30 Weyl, Σ T = 15
# b_3 = 11 - 2/3 × 15 = 11 - 10 = 1

b_3_with_VL = 1.0  # SM + VL SU(3)
b_3_no_VL = 7.0     # SM only

print(f"\n  Stage 3a — SU(3)_c VL threshold: M_PS → M_VL")
print(f"    SM: 6 flavors, Σ T=6")
print(f"    VL: 9 flavors (9 in 3 + 9 in 3̄), Σ T=9")
print(f"    Total: 15 flavors, Σ T=15")
print(f"    b_3(with VL) = 11 - 10 = {b_3_with_VL}")
print(f"    b_3(SM only) = {b_3_no_VL}")

# ---- Stage 3b: SU(2)_L with VL [M_PS → M_VL] ----
# Under SU(2)_L from the decomposition of 3×(12⊕12̄):
# 12 = (4,3) → 4 = (2,2) under SU(2)_L × SU(2)_R
# 12 = (2,2,3) → 3×(2,2) = 6 Weyl in SU(2)_L doublet per 12
# 3×12 = 3×3×2 = 18 Weyl in SU(2)_L doublet
# 3×12̄ = 3×3×2 = 18 Weyl in SU(2)_L doublet
# Total: 36 Weyl in SU(2)_L doublet = 18 doublets, Σ T = 18
# b_2L = 22/3 - 2/3 × 18 = 22/3 - 12 = 22/3 - 36/3 = -14/3 ≈ -4.67
#
# But SM SU(2)_L content:
# 3 gen × (Q_L + L_L) = 3 × (3 colors + 1) = 12 doublets = 24 Weyl? No...
# SU(2) doesn't care about color. Q_L = 1 doublet in SU(2), with 3 colors 
# that are SU(2) singlets. So per generation: 1 Q_L doublet + 1 L_L doublet = 2 doublets
# 3 gen: 6 doublets = 12 Weyl, Σ T = 6
# b_2L_SM = 22/3 - 2/3 × 6 - 1/6 × 1 = 22/3 - 4 - 1/6 = 44/6 - 24/6 - 1/6 = 19/6 ✓
#
# VL: 18 - 6 = 12 doublets = 24 Weyl, Σ T = 12
# With VL active: Σ T = 6 + 12 = 18
# b_2L = 22/3 - 2/3 × 18 - 1/6 = 22/3 - 12 - 1/6 = 44/6 - 72/6 - 1/6 = -29/6 ≈ -4.83
# 
# This is also negative! SU(2)_L is also not asymptotically free with VL.
# But again, VL should decouple at M_PS (or soon after).
# 
# I'll use the simplified approach: VL decouple at M_VL for both SU(3)_c and SU(2)_L.

b_2_with_VL = -29/6  # SU(2)_L with VL
b_2_no_VL = 19/6     # SM SU(2)_L

print(f"\n  Stage 3b — SU(2)_L VL threshold: M_PS → M_VL")
print(f"    SM: 6 doublets, Σ T=6")
print(f"    VL: 12 doublets, Σ T=12")
print(f"    b_2(with VL) = {b_2_with_VL:.4f}")
print(f"    b_2(SM only) = {b_2_no_VL:.4f}")

# ---- Stage 3c: SU(2)_R [M_PS → M_R] ----
# Same as SU(2)_L with VL (since 4 = (2,2) gives both)
b_2R = b_2_with_VL
print(f"\n  Stage 3c — SU(2)_R: M_PS → M_R (same as SU(2)_L with VL)")
print(f"    b_2R = {b_2R:.4f}")

# ---- Stage 3d: U(1)_Y matching at M_R ----
# Standard SM running
b_1_SM = -41/10
print(f"\n  Stage 3d — U(1)_Y: M_R → M_Z (SM)")
print(f"    b_1 = {b_1_SM}")

# ============================================================
# 3. Running 求解 M_VL
# ============================================================
print("\n" + "=" * 72)
print("3. 求解 M_VL (VL fermion 退耦標度)")
print("=" * 72)

# Strategy: 
# 1. Fix α_GUT⁻¹ = 53 (from script 05, structural relation 2×K_tree−F₇)
# 2. Run SU(4)_PS from M_GUT to M_PS
# 3. Match SU(3)_c and SU(2)_L at M_PS
# 4. Run with VL from M_PS to M_VL
# 5. Run without VL from M_VL to M_Z
# 6. Vary M_VL to find α₃⁻¹(M_Z) = 8.44

# Fixed α_GUT⁻¹ from structural relation
alpha_GUT_inv = 53.0

print(f"\n  Fixed α_GUT⁻¹ = {alpha_GUT_inv} (= 2×K_tree − F₇ = {2*K_tree - F_7})")

# Run SU(4)_PS from M_GUT to M_PS
a4_at_PS = running(alpha_GUT_inv, M_GUT, M_PS, b_SU4)
print(f"\n  SU(4)_PS running: M_GUT → M_PS")
print(f"    α₄⁻¹(M_GUT) = {alpha_GUT_inv:.4f}")
print(f"    α₄⁻¹(M_PS) = {a4_at_PS:.4f}")

# Match at M_PS: SU(4)_PS → SU(3)_c × U(1)_{B-L} and SU(2)_L × SU(2)_R
# g_3 = g_4 (gluons from SU(4) generators)
# g_2L = g_2R = g_4/√2 (W-bosons from broken SU(4) generators)
a3_at_PS = a4_at_PS  # direct matching
a2_at_PS = a4_at_PS - np.log(2) / (2*np.pi)  # matching with √2 factor

print(f"\n  Matching at M_PS = {M_PS:.2e} GeV:")
print(f"    α₃⁻¹(M_PS) = α₄⁻¹(M_PS) = {a3_at_PS:.4f}")
print(f"    α₂⁻¹(M_PS) = α₄⁻¹(M_PS) − ln(2)/(2π) = {a2_at_PS:.4f}")

# Search for M_VL
print(f"\n  Searching M_VL for α₃⁻¹(M_Z) = 8.44...")
print(f"\n  {'M_VL (GeV)':<16} {'α₃⁻¹':<12} {'α₂⁻¹':<12} {'α₁⁻¹':<12} {'Δ₃':<10} {'Δ₂':<10} {'Δ₁':<10}")
print("  " + "-" * 82)

best_chisq = 1e30
best_MVL = 0
solutions = []

for log_MVL in np.arange(np.log10(M_PS), np.log10(M_R) - 1, -0.1):
    M_VL = 10**log_MVL
    
    # SU(3)_c: M_PS → M_VL (with VL) → M_Z (no VL)
    a3 = running(a3_at_PS, M_PS, M_VL, b_3_with_VL)
    a3 = running(a3, M_VL, M_Z, b_3_no_VL)
    
    # SU(2)_L: M_PS → M_VL (with VL) → M_R (no VL) → M_Z (SM)
    a2 = running(a2_at_PS, M_PS, M_VL, b_2_with_VL)
    a2 = running(a2, M_VL, M_R, b_2_no_VL)
    a2 = running(a2, M_R, M_EW, b_2_no_VL)
    a2 = running(a2, M_EW, M_Z, b_2_no_VL)
    
    # U(1)_Y: M_R → M_Z (SM only)
    # Match at M_R: SU(2)_R × U(1)_{B-L} → U(1)_Y
    a2R_at_PS = a2_at_PS
    a2R_at_MR = running(a2R_at_PS, M_PS, M_R, b_2R)
    a1_at_MR = a2R_at_MR - np.log(2) / (2*np.pi)
    a1 = running(a1_at_MR, M_R, M_EW, b_1_SM)
    a1 = running(a1, M_EW, M_Z, b_1_SM)
    
    d3 = a3 - a3_inv_MZ
    d2 = a2 - a2_inv_MZ
    d1 = a1 - a1_inv_MZ
    chisq = d3**2 + d2**2 + d1**2
    
    if chisq < best_chisq:
        best_chisq = chisq
        best_MVL = M_VL
        best_a3, best_a2, best_a1 = a3, a2, a1
        best_d3, best_d2, best_d1 = d3, d2, d1
    
    # Print every 0.5 in log10
    if abs(log_MVL - round(log_MVL * 2) / 2) < 0.01 or abs(d3) < 5:
        print(f"  {M_VL:<16.2e} {a3:<12.4f} {a2:<12.4f} {a1:<12.4f} {d3:<+10.4f} {d2:<+10.4f} {d1:<+10.4f}")
    
    solutions.append({
        'M_VL': M_VL,
        'a3_inv': a3, 'a2_inv': a2, 'a1_inv': a1,
        'd3': d3, 'd2': d2, 'd1': d1, 'chisq': chisq
    })

print(f"\n  ** Best M_VL = {best_MVL:.2e} GeV **")
print(f"  log₁₀(M_VL/GeV) = {np.log10(best_MVL):.2f}")
print(f"  χ² = {best_chisq:.4f}")
print(f"\n  {'':<12} {'Predicted':<12} {'Target':<12} {'Diff':<10}")
print(f"  {'α₃⁻¹':<12} {best_a3:<12.4f} {a3_inv_MZ:<12.4f} {best_d3:<+10.4f}")
print(f"  {'α₂⁻¹':<12} {best_a2:<12.4f} {a2_inv_MZ:<12.4f} {best_d2:<+10.4f}")
print(f"  {'α₁⁻¹':<12} {best_a1:<12.4f} {a1_inv_MZ:<12.4f} {best_d1:<+10.4f}")

# ============================================================
# 4. 分析 M_VL 嘅物理合理性
# ============================================================
print("\n" + "=" * 72)
print("4. 物理合理性分析")
print("=" * 72)

log_MVL = np.log10(best_MVL)
log_MPS = np.log10(M_PS)
log_MR = np.log10(M_R)
log_MGUT = np.log10(M_GUT)

print(f"\n  M_VL = {best_MVL:.2e} GeV")
print(f"  M_PS = {M_PS:.2e} GeV")
print(f"  M_R  = {M_R:.2e} GeV")
print(f"  M_GUT = {M_GUT:.2e} GeV")
print(f"\n  M_VL / M_PS = {best_MVL/M_PS:.4f}")
print(f"  M_VL / M_R = {best_MVL/M_R:.4f}")
print(f"  M_GUT / M_VL = {M_GUT/best_MVL:.2e}")

# Check if M_VL is close to any structural scale
print(f"\n  Structural scales:")
print(f"  M_PS = M_Planck × γ₁² = {M_PS:.2e}")
print(f"  M_PS/√(γ₁) = {M_PS/np.sqrt(gamma_1):.2e}")
print(f"  M_PS × γ₁ = M_R = {M_R:.2e}")
print(f"  √(M_PS × M_R) = {np.sqrt(M_PS * M_R):.2e}")

# ============================================================
# 5. 完整 3-coupling 收斂檢查
# ============================================================
print("\n" + "=" * 72)
print("5. 三耦合同時收斂")
print("=" * 72)

# Now check if α_GUT⁻¹ can be adjusted to converge all three couplings
print(f"\n  Varying α_GUT⁻¹ and M_VL simultaneously...")

best_chisq2 = 1e30
best_aGUT2 = 0
best_MVL2 = 0

for aGUT_inv in np.arange(30, 80, 1):
    # Run SU(4)_PS
    a4p = running(aGUT_inv, M_GUT, M_PS, b_SU4)
    a3p = a4p
    a2p = a4p - np.log(2) / (2*np.pi)
    
    for log_MVL in np.arange(np.log10(M_PS), np.log10(M_R) - 1, -0.2):
        M_VL = 10**log_MVL
        
        a3 = running(a3p, M_PS, M_VL, b_3_with_VL)
        a3 = running(a3, M_VL, M_Z, b_3_no_VL)
        
        a2 = running(a2p, M_PS, M_VL, b_2_with_VL)
        a2 = running(a2, M_VL, M_R, b_2_no_VL)
        a2 = running(a2, M_R, M_EW, b_2_no_VL)
        a2 = running(a2, M_EW, M_Z, b_2_no_VL)
        
        a2R = a2p
        a2R = running(a2R, M_PS, M_R, b_2R)
        a1 = a2R - np.log(2) / (2*np.pi)
        a1 = running(a1, M_R, M_EW, b_1_SM)
        a1 = running(a1, M_EW, M_Z, b_1_SM)
        
        d3 = a3 - a3_inv_MZ; d2 = a2 - a2_inv_MZ; d1 = a1 - a1_inv_MZ
        chisq = d3**2 + d2**2 + d1**2
        
        if chisq < best_chisq2:
            best_chisq2 = chisq
            best_aGUT2 = aGUT_inv
            best_MVL2 = M_VL
            best_a3_2 = a3; best_a2_2 = a2; best_a1_2 = a1
            best_d3_2 = d3; best_d2_2 = d2; best_d1_2 = d1

print(f"\n  2-parameter scan (α_GUT⁻¹, M_VL):")
print(f"  Best α_GUT⁻¹ = {best_aGUT2:.0f}")
print(f"  Best M_VL = {best_MVL2:.2e} GeV")
print(f"  χ² = {best_chisq2:.4f}")
print(f"\n  {'':<12} {'Predicted':<12} {'Target':<12} {'Diff':<10}")
print(f"  {'α₃⁻¹':<12} {best_a3_2:<12.4f} {a3_inv_MZ:<12.4f} {best_d3_2:<+10.4f}")
print(f"  {'α₂⁻¹':<12} {best_a2_2:<12.4f} {a2_inv_MZ:<12.4f} {best_d2_2:<+10.4f}")
print(f"  {'α₁⁻¹':<12} {best_a1_2:<12.4f} {a1_inv_MZ:<12.4f} {best_d1_2:<+10.4f}")

# Also try varying M_PS (breaking the structural constraint)
print(f"\n  Varying M_PS as well (3-parameter scan)...")

best_chisq3 = 1e30
best_aGUT3 = 0; best_MPS3 = 0; best_MVL3 = 0

# Try M_PS around the γ₁² value within a factor of 100
for aGUT_inv in np.arange(30, 80, 2):
    for log_MPS in np.arange(np.log10(M_PS) - 1, np.log10(M_PS) + 1, 0.2):
        M_PS_try = 10**log_MPS
        a4p = running(aGUT_inv, M_GUT, M_PS_try, b_SU4)
        a3p = a4p
        a2p = a4p - np.log(2) / (2*np.pi)
        
        for log_MVL in np.arange(log_MPS - 2, log_MPS + 0.5, 0.3):
            if log_MVL > np.log10(M_PS_try):
                continue
            M_VL = 10**log_MVL
            
            a3 = running(a3p, M_PS_try, M_VL, b_3_with_VL)
            a3 = running(a3, M_VL, M_Z, b_3_no_VL)
            
            a2 = running(a2p, M_PS_try, M_VL, b_2_with_VL)
            a2 = running(a2, M_VL, M_R, b_2_no_VL)
            a2 = running(a2, M_R, M_EW, b_2_no_VL)
            a2 = running(a2, M_EW, M_Z, b_2_no_VL)
            
            a2R = a2p
            a2R = running(a2R, M_PS_try, M_R, b_2R)
            a1 = a2R - np.log(2) / (2*np.pi)
            a1 = running(a1, M_R, M_EW, b_1_SM)
            a1 = running(a1, M_EW, M_Z, b_1_SM)
            
            d3 = a3 - a3_inv_MZ; d2 = a2 - a2_inv_MZ; d1 = a1 - a1_inv_MZ
            chisq = d3**2 + d2**2 + d1**2
            
            if chisq < best_chisq3:
                best_chisq3 = chisq
                best_aGUT3 = aGUT_inv
                best_MPS3 = M_PS_try
                best_MVL3 = M_VL
                best_a3_3 = a3; best_a2_3 = a2; best_a1_3 = a1
                best_d3_3 = d3; best_d2_3 = d2; best_d1_3 = d1

print(f"\n  3-parameter scan (α_GUT⁻¹, M_PS, M_VL):")
print(f"  Best α_GUT⁻¹ = {best_aGUT3:.0f}")
print(f"  Best M_PS = {best_MPS3:.2e} GeV (γ₁² = {M_PS:.2e}, ratio = {best_MPS3/M_PS:.4f})")
print(f"  Best M_VL = {best_MVL3:.2e} GeV")
print(f"  χ² = {best_chisq3:.4f}")
print(f"\n  {'':<12} {'Predicted':<12} {'Target':<12} {'Diff':<10}")
print(f"  {'α₃⁻¹':<12} {best_a3_3:<12.4f} {a3_inv_MZ:<12.4f} {best_d3_3:<+10.4f}")
print(f"  {'α₂⁻¹':<12} {best_a2_3:<12.4f} {a2_inv_MZ:<12.4f} {best_d2_3:<+10.4f}")
print(f"  {'α₁⁻¹':<12} {best_a1_3:<12.4f} {a1_inv_MZ:<12.4f} {best_d1_3:<+10.4f}")

# ============================================================
# 6. 結論
# ============================================================
print("\n" + "=" * 72)
print("6. 結論")
print("=" * 72)

print(f"""
  Scenario 1: Fixed α_GUT⁻¹=53, vary M_VL only
    M_VL = {best_MVL:.2e} GeV
    χ² = {best_chisq:.2f}
    α₃⁻¹(M_Z) = {best_a3:.2f} (target 8.44, Δ={best_d3:+.2f})
    α₂⁻¹(M_Z) = {best_a2:.2f} (target 29.57, Δ={best_d2:+.2f})
    α₁⁻¹(M_Z) = {best_a1:.2f} (target 59.02, Δ={best_d1:+.2f})

  Scenario 2: Vary α_GUT⁻¹ and M_VL
    α_GUT⁻¹ = {best_aGUT2:.0f}, M_VL = {best_MVL2:.2e} GeV
    χ² = {best_chisq2:.2f}
    α₃⁻¹(M_Z) = {best_a3_2:.2f} (Δ={best_d3_2:+.2f})
    α₂⁻¹(M_Z) = {best_a2_2:.2f} (Δ={best_d2_2:+.2f})
    α₁⁻¹(M_Z) = {best_a1_2:.2f} (Δ={best_d1_2:+.2f})

  Scenario 3: Vary α_GUT⁻¹, M_PS, and M_VL
    α_GUT⁻¹ = {best_aGUT3:.0f}, M_PS = {best_MPS3:.2e}, M_VL = {best_MVL3:.2e}
    χ² = {best_chisq3:.2f}
    α₃⁻¹(M_Z) = {best_a3_3:.2f} (Δ={best_d3_3:+.2f})
    α₂⁻¹(M_Z) = {best_a2_2:.2f} (Δ={best_d2_2:+.2f})
    α₁⁻¹(M_Z) = {best_a1_2:.2f} (Δ={best_d1_2:+.2f})
""")

# ============================================================
# 7. 保存結果
# ============================================================
results = {
    'scales': {
        'M_Planck': M_Planck, 'M_GUT': M_GUT, 'M_PS': M_PS,
        'M_R': M_R, 'M_EW': M_EW, 'M_Z': M_Z, 'gamma_1': float(gamma_1)
    },
    'beta_coefficients': {
        'stage1_SU12': b_SU12,
        'stage2_SU4': float(b_SU4),
        'stage3a_b3_with_VL': float(b_3_with_VL),
        'stage3a_b3_no_VL': b_3_no_VL,
        'stage3b_b2_with_VL': float(b_2_with_VL),
        'stage3b_b2_no_VL': float(b_2_no_VL),
        'stage4_b1_SM': b_1_SM
    },
    'scenario1_fixed_alphaGUT': {
        'alpha_GUT_inv': alpha_GUT_inv,
        'M_VL': float(best_MVL),
        'log10_M_VL': float(np.log10(best_MVL)),
        'a3_inv_MZ': float(best_a3), 'a2_inv_MZ': float(best_a2), 'a1_inv_MZ': float(best_a1),
        'd3': float(best_d3), 'd2': float(best_d2), 'd1': float(best_d1),
        'chisq': float(best_chisq),
        'M_VL_over_M_PS': float(best_MVL/M_PS),
        'M_VL_over_M_R': float(best_MVL/M_R)
    },
    'scenario2_vary_alphaGUT_VL': {
        'alpha_GUT_inv': float(best_aGUT2),
        'M_VL': float(best_MVL2),
        'log10_M_VL': float(np.log10(best_MVL2)),
        'a3_inv_MZ': float(best_a3_2), 'a2_inv_MZ': float(best_a2_2), 'a1_inv_MZ': float(best_a1_2),
        'd3': float(best_d3_2), 'd2': float(best_d2_2), 'd1': float(best_d1_2),
        'chisq': float(best_chisq2)
    },
    'scenario3_vary_all': {
        'alpha_GUT_inv': float(best_aGUT3),
        'M_PS': float(best_MPS3),
        'M_VL': float(best_MVL3),
        'log10_M_VL': float(np.log10(best_MVL3)),
        'M_PS_ratio_to_gamma_sq': float(best_MPS3/M_PS),
        'a3_inv_MZ': float(best_a3_3), 'a2_inv_MZ': float(best_a2_2), 'a1_inv_MZ': float(best_a1_2),
        'd3': float(best_d3_3), 'd2': float(best_d2_2), 'd1': float(best_d1_2),
        'chisq': float(best_chisq3)
    },
    'conclusion': (
        f"Scenario 1: α_GUT⁻¹=53 fixed, M_VL={best_MVL:.2e}, χ²={best_chisq:.2f}. "
        f"Scenario 2: α_GUT⁻¹={best_aGUT2:.0f}, M_VL={best_MVL2:.2e}, χ²={best_chisq2:.2f}. "
        f"Scenario 3: α_GUT⁻¹={best_aGUT3:.0f}, M_PS={best_MPS3:.2e}, M_VL={best_MVL3:.2e}, χ²={best_chisq3:.2f}"
    )
}

out_path = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o89_mass_hierarchy_coupling/data/06_threshold_corrections.json'
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"✅ 結果已保存到 {out_path}")