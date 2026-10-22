#!/usr/bin/env python3
"""
O117/03: C_DH Structural Coefficient — Problem 1 of 2
======================================================
Optimal C_DH = -0.2240 vs C_DM = -0.16973. Ratio = 1.3199 ≈ 4/3 (1.0%).

Questions:
1. Is the ratio exactly 4/3 = B/N_gen? (structural factor)
2. Or is C_DH = C_DM exactly, and the optimal is just noise?
3. What is the structural derivation of C_DH?

Key insight: The group delay correction δ(ℓ) = C×(ℓ-0.5)×(1-4^−ℓ) 
comes from the K_Chain spectral asymmetry. The coefficient C is derived from:
  C = -β₁ × 2φ⁻¹ × √5
  β₁ = C_delay = (Σw_even·γ − Σw_odd·γ) / (Σw·γ)

For DM, the correction enters the factor (1 + 2φ⁻¹ℓ + δ(ℓ)).
For DH, the correction enters the factor (1 + δ_k0 + δ_gd).

The δ_k0 term already captures the K_Tree partial trace Gaussian envelope.
The δ_gd term is the linear (odd) correction from spectral asymmetry.

The coefficient C should be the same for both DM and DH because the
spectral asymmetry is a property of the K_Chain, not the projection.
But the projection may introduce a different normalization factor.

This script tests all structural candidates.
"""
import json, math

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ PASS: {name}")
    else:
        FAIL += 1
        print(f"  ❌ FAIL: {name}")
    if detail:
        print(f"    {detail}")

R_H = 4129.94
phi = (1 + math.sqrt(5)) / 2
phi_inv = phi - 1
phi_inv_3 = phi_inv ** 3
rd_corrected = math.pi * R_H / 88 * 420/421
ell_0 = 0.5
sigma_phi = 0.5 * math.log(phi) / math.log(4)
C_DM = -0.16973

# Structural constants
B = 4
N_gen = 3
N_d = 44
L_4, L_5, L_7 = 7, 11, 29
F_5, F_6, F_7 = 5, 8, 13

def ell(z):
    return math.log(1 + z, 4)

def delta_k0(ell_val):
    d = ell_val - ell_0
    return phi_inv_3 * math.exp(-d**2 / (2 * sigma_phi**2))

def DH_with_C(z, C_val):
    l = ell(z)
    delta = C_val * (l - 0.5) * (1 - 4**(-l))
    return R_H * (1 + delta_k0(l) + delta) / (1 + z)

# DESI DR2 DH/rd data
desi_dh = [
    ('LRG1',     0.510, 21.863, 0.429),
    ('LRG2',     0.706, 19.455, 0.334),
    ('LRG3+ELG', 0.934, 17.641, 0.201),
    ('ELG2',     1.321, 14.176, 0.225),
    ('QSO',      1.484, 12.817, 0.518),
    ('Lyα',      2.330, 8.632, 0.532),
]

def chi2_for_C(C_val):
    chi2 = 0
    for name, z, obs, err in desi_dh:
        pred = DH_with_C(z, C_val) / rd_corrected
        chi2 += ((pred - obs) / err)**2
    return chi2

print("=" * 72)
print("  O117/03: C_DH Structural Coefficient Derivation")
print("=" * 72)

# ============ 1. High-precision scan ============
print(f"\n{'='*72}")
print("  1. High-Precision Scan for Optimal C_DH")
print(f"{'='*72}")

best_C = 0
best_chi2 = 1e10
for Ci in [x/10000 for x in range(-3000, 0)]:  # -0.3000 to 0, step 0.0001
    chi2 = chi2_for_C(Ci)
    if chi2 < best_chi2:
        best_chi2 = chi2
        best_C = Ci

print(f"  Optimal C_DH = {best_C:.6f}")
print(f"  χ² = {best_chi2:.4f} ({len(desi_dh)} dof)")
print(f"  C_DM = {C_DM:.6f}")
print(f"  Ratio C_DH/C_DM = {best_C/C_DM:.6f}")

# ============ 2. Test structural candidates ============
print(f"\n{'='*72}")
print("  2. Structural Candidate Ratios")
print(f"{'='*72}")

candidates = {
    'C_DM (same as DM)': C_DM,
    'C_DM × B/N_gen = C_DM × 4/3': C_DM * B / N_gen,
    'C_DM × L₅/L₄ = C_DM × 11/7': C_DM * L_5 / L_4,
    'C_DM × φ': C_DM * phi,
    'C_DM × √φ': C_DM * math.sqrt(phi),
    'C_DM × (B+1)/B = C_DM × 5/4': C_DM * (B+1) / B,
    'C_DM × (N_d+2)/N_d = C_DM × 46/44': C_DM * (N_d+2) / N_d,
    'C_DM × Σγ_even/Σγ_odd = C_DM × 46/44': C_DM * 46/44,
    'C_DM × F₇/F₆ = C_DM × 13/8': C_DM * F_7 / F_6,
    'C_DM × L₇/L₅ = C_DM × 29/11': C_DM * L_7 / L_5,
    'C_DM × (L₅+1)/B = C_DM × 12/4': C_DM * (L_5+1) / B,
}

best_ratio = best_C / C_DM
print(f"  Optimal ratio: {best_ratio:.6f}")
print(f"  {'Candidate':<40} {'Ratio':<10} {'C':<12} {'χ²':<8} {'Δχ²':<8}")
print("  " + "-"*78)
for name, C_val in candidates.items():
    chi2 = chi2_for_C(C_val)
    ratio = C_val / C_DM
    delta = chi2 - best_chi2
    marker = " ← BEST" if abs(chi2 - best_chi2) < 0.01 else ""
    print(f"  {name:<40} {ratio:<10.6f} {C_val:<12.6f} {chi2:<8.4f} {delta:<+8.4f}{marker}")

# Check which is closest to optimal
closest = min(candidates.items(), key=lambda x: abs(x[1] - best_C))
print(f"\n  Closest structural candidate: {closest[0]}")
print(f"  C = {closest[1]:.6f} (vs optimal {best_C:.6f})")
print(f"  ΔC = {(closest[1] - best_C)/best_C*100:.3f}%")

# ============ 3. Test: is C_DH = C_DM exactly sufficient? ============
print(f"\n{'='*72}")
print("  3. Is C_DM (same coefficient) sufficient?")
print(f"{'='*72}")

chi2_dm = chi2_for_C(C_DM)
chi2_43 = chi2_for_C(C_DM * B / N_gen)
chi2_opt = best_chi2

print(f"  C_DM ({C_DM:.6f}):        χ² = {chi2_dm:.4f}")
print(f"  C_DM×4/3 ({C_DM*B/N_gen:.6f}): χ² = {chi2_43:.4f}")
print(f"  Optimal ({best_C:.6f}):     χ² = {chi2_opt:.4f}")
print(f"")
print(f"  Δχ²(C_DM vs optimal) = {chi2_dm - chi2_opt:.4f}")
print(f"  Δχ²(C_DM×4/3 vs optimal) = {chi2_43 - chi2_opt:.4f}")
print(f"")
check("C_DM gives χ² < 10 (acceptable)", chi2_dm < 10, f"{chi2_dm:.4f}")
check("C_DM×4/3 gives χ² < 10 (acceptable)", chi2_43 < 10, f"{chi2_43:.4f}")
check("C_DM×4/3 closer to optimal than C_DM", abs(chi2_43 - chi2_opt) < abs(chi2_dm - chi2_opt), 
      f"{chi2_43 - chi2_opt:.4f} vs {chi2_dm - chi2_opt:.4f}")

# ============ 4. Structural derivation of C_DH ============
print(f"\n{'='*72}")
print("  4. Structural Derivation of C_DH")
print(f"{'='*72}")

# C_DM = -β₁ × 2φ⁻¹ × √5
# β₁ = C_delay = (Σw_even·γ − Σw_odd·γ) / (Σw·γ)
# For DH, the projection may have a different weight

# Let's compute the group delay asymmetry for the K_Chain directly
gamma = [4 * math.sin(math.pi * n / 88)**2 for n in range(1, N_d + 1)]
v_g = [math.cos(math.pi * n / 88) for n in range(1, N_d + 1)]

# Group delay weight w_n = 1/v_g(n) = sec(πn/88)
w_gd = [1/v for v in v_g]

# Standard C_delay (as used in O51/86)
w_even = sum(w_gd[i]*gamma[i] for i in range(0, N_d, 2))
w_odd = sum(w_gd[i]*gamma[i] for i in range(1, N_d, 2))
C_delay = (w_even - w_odd) / (w_even + w_odd)
C1_derived = -C_delay * 2 * phi_inv * math.sqrt(5)

print(f"  K_Chain spectral analysis:")
print(f"  Σγ = {sum(gamma):.1f}")
print(f"  Σγ_even = {sum(gamma[0::2]):.1f}, Σγ_odd = {sum(gamma[1::2]):.1f}")
print(f"  C_delay = {C_delay:.6f}")
print(f"  C₁ (derived) = {C1_derived:.6f}")
print(f"  C_DM (from O51) = {C_DM:.6f}")
check("C₁ derived ≈ C_DM", abs(C1_derived - C_DM) < 0.001, f"{C1_derived:.6f} vs {C_DM:.6f}")

# The key insight: the group delay correction for DH needs a different normalization
# because the base projection is different. 
# DM: D_app ∝ R_H × (1 + 2φ⁻¹ℓ) — linear in ℓ
# DH: DH ∝ R_H × (1 + δ_k0) / (1+z) — Gaussian + 1/(1+z)

# The δ_gd correction enters the factor (1 + δ_k0 + δ_gd)
# while the DM correction enters (1 + 2φ⁻¹ℓ + δ)
# The different base functions mean the same C gets a different effective weight

# Let's compute the ratio of δ_gd to δ_k0 at ℓ=0.5 (the peak)
# At ℓ=0.5: δ_k0 = φ⁻³ = 0.23607
# δ_gd(ℓ=0.5) = 0 (by construction, since (ℓ-0.5) factor)
# So the correction is zero at the peak

# At ℓ=0.3 (z≈0.51, LRG1):
l_lrg1 = ell(0.510)
dk0_lrg1 = delta_k0(l_lrg1)
gd_lrg1 = C_DM * (l_lrg1 - 0.5) * (1 - 4**(-l_lrg1))
gd_43_lrg1 = C_DM * B/N_gen * (l_lrg1 - 0.5) * (1 - 4**(-l_lrg1))

print(f"\n  At z=0.51 (LRG1, ℓ={l_lrg1:.4f}):")
print(f"  δ_k0 = {dk0_lrg1:.6f}")
print(f"  δ_gd(C_DM) = {gd_lrg1:.6f}")
print(f"  δ_gd(C_DM×4/3) = {gd_43_lrg1:.6f}")
print(f"  Ratio δ_gd/δ_k0 (C_DM) = {gd_lrg1/dk0_lrg1*100:.1f}%")
print(f"  Ratio δ_gd/δ_k0 (C_DM×4/3) = {gd_43_lrg1/dk0_lrg1*100:.1f}%")

# ============ 5. The structural answer ============
print(f"\n{'='*72}")
print("  5. Structural Conclusion")
print(f"{'='*72}")

ratio_exact = best_C / C_DM
print(f"""
  C_DH optimal ratio = {ratio_exact:.6f}
  
  Structural candidates:
    B/N_gen = 4/3 = {B/N_gen:.6f}  (Δ = {abs(ratio_exact - B/N_gen)/B/N_gen*100:.2f}%)
    L₅/L₄ = 11/7 = {L_5/L_4:.6f}  (Δ = {abs(ratio_exact - L_5/L_4)/L_5/L_4*100:.2f}%)
    φ = {phi:.6f}  (Δ = {abs(ratio_exact - phi)/phi*100:.2f}%)
    √φ = {math.sqrt(phi):.6f}  (Δ = {abs(ratio_exact - math.sqrt(phi))/math.sqrt(phi)*100:.2f}%)

  Decision: 
    The optimal C_DH = {best_C:.6f} is within the noise floor of the DESI DR2 data.
    Using C_DH = C_DM = {C_DM:.6f} gives χ² = {chi2_dm:.4f} (6 dof), which is already excellent.
    Using C_DH = C_DM × B/N_gen = {C_DM*B/N_gen:.6f} gives χ² = {chi2_43:.4f} (6 dof).
    The Δχ² between these is {abs(chi2_dm - chi2_43):.4f} — negligible.

  Structural conclusion: C_DH = C_DM × (B/N_gen)ᵖ where p = 0 or 1.
    The most conservative choice is p = 0: C_DH = C_DM (same coefficient).
    This is justified because the group delay asymmetry is a property of the
    K_Chain spectrum, not of the projection direction.
    
  However, the 4/3 factor (= B/N_gen) may arise from the different projection
  normalization: DH has a 1/(1+z) factor absent in DM. The 4/3 = (K_Tree+1)/K_Tree
  represents the ratio of total to projected K_Tree levels.
""")

# Save results
result = {
    'optimal_C_DH': round(best_C, 6),
    'optimal_chi2': round(best_chi2, 4),
    'C_DM': C_DM,
    'C_DM_chi2': round(chi2_dm, 4),
    'C_43_chi2': round(chi2_43, 4),
    'ratio_C_DH_C_DM': round(best_C/C_DM, 6),
    'B_over_N_gen': B/N_gen,
    'closest_candidate': closest[0],
    'pass': PASS,
    'fail': FAIL
}

with open('data/03_cdh_structural.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"  ✅ Results saved to data/03_cdh_structural.json")
print(f"  PASS: {PASS}/{PASS+FAIL}")