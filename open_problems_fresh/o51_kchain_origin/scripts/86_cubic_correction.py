#!/usr/bin/env python3
"""
O51/86: Cubic Correction Term δ₃(ℓ) — K_Chain Kurtosis Derivation
=================================================================
Derivation of the cubic correction term δ₃(ℓ) = C₃×(ℓ-0.5)³×(1-4^{-ℓ})
from K_Chain spectrum's higher moments (excess kurtosis).

The linear correction δ₁(ℓ) = C₁×(ℓ-0.5)×(1-4^{-ℓ}) with C₁ = -0.16973
improves χ² from 42.23 → 18.09 (7-point DESI DR2), but residual χ²/dof=2.58 remains.

The cubic term captures the next-order odd-parity asymmetry around ℓ=0.5 (n=22),
derived structurally from the group-delay-weighted spectral kurtosis.
"""
import json, math, sys

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

# ============ Constants ============
R_H = 4129.94
N_d = 44
phi = (1 + math.sqrt(5)) / 2
eps = phi**(-1) / 4          # ε = φ⁻¹/4 ≈ 0.1545
rd_c = math.pi * R_H / 88 * 420/421  # rd_corrected = 147.0883
c_mpc_gyr = 306.601394
KMS = 977.8

print("=" * 70)
print("O51/86: Cubic Correction δ₃(ℓ) — K_Chain Kurtosis Derivation")
print("=" * 70)

# ============ 1. K_Chain Spectrum ============
print("\n--- 1. K_Chain Spectrum (n=1..44) ---")
omega = [2*math.sin(math.pi*n/(2*N_d)) for n in range(1, N_d+1)]
gamma = [4*math.sin(math.pi*n/(2*N_d))**2 for n in range(1, N_d+1)]
v_g = [math.cos(math.pi*n/(2*N_d)) for n in range(1, N_d+1)]  # group velocity

print(f"γ_n = 4sin²(πn/88), n=1..44")
print(f"v_g(n) = cos(πn/88)")
print(f"Σγ = {sum(gamma):.6f} (should be 90)")

# ============ 2. Energy-Weighted Spectral Moments ============
print("\n--- 2. Energy-Weighted Spectral Moments ---")
w = gamma  # energy weights
sum_w = sum(w)
mean = sum((n+1)*w[n] for n in range(N_d)) / sum_w
var = sum((n+1-mean)**2*w[n] for n in range(N_d)) / sum_w
skew = sum((n+1-mean)**3*w[n] for n in range(N_d)) / sum_w / var**1.5
kurt = sum((n+1-mean)**4*w[n] for n in range(N_d)) / sum_w / var**2 - 3

print(f"μ = {mean:.6f}  (spectral centroid)")
print(f"σ² = {var:.6f}  (variance)")
print(f"γ₁ = {skew:.6f}  (skewness, {'' if skew < 0 else '+'}{'right' if skew > 0 else 'left'}-skewed)")
print(f"γ₂ = {kurt:.6f}  (excess kurtosis, {'leptokurtic' if kurt > 0 else 'platykurtic'})")
print(f"σ/μ = {math.sqrt(var)/mean:.6f}")
print(f"σ²/μ² = {var/(mean**2):.6f}")

# ============ 3. Group-Delay-Weighted Spectral Moments ============
print("\n--- 3. Group-Delay-Weighted Spectral Moments (n=1..27, F_proj=17) ---")
n_cut = 27  # 44 - F_proj = 44 - 17
w_gd = [1/v_g[n] for n in range(n_cut)]  # group delay weights w_n = sec(πn/88)

# Group-delay-weighted spectrum: w_n × γ_n
w_weighted = [w_gd[n]*gamma[n] for n in range(n_cut)]
sum_w_w = sum(w_weighted)
mean_gd = sum((n+1)*w_weighted[n] for n in range(n_cut)) / sum_w_w
var_gd = sum((n+1-mean_gd)**2*w_weighted[n] for n in range(n_cut)) / sum_w_w
skew_gd = sum((n+1-mean_gd)**3*w_weighted[n] for n in range(n_cut)) / sum_w_w / var_gd**1.5
kurt_gd = sum((n+1-mean_gd)**4*w_weighted[n] for n in range(n_cut)) / sum_w_w / var_gd**2 - 3

print(f"μ_gd = {mean_gd:.6f}")
print(f"σ²_gd = {var_gd:.6f}")
print(f"γ₁_gd = {skew_gd:.6f}  (group-delay-weighted skewness)")
print(f"γ₂_gd = {kurt_gd:.6f}  (group-delay-weighted excess kurtosis)")
print(f"σ_gd/μ_gd = {math.sqrt(var_gd)/mean_gd:.6f}")
print(f"σ²_gd/μ²_gd = {var_gd/(mean_gd**2):.6f}")

# ============ 4. Group Delay Asymmetry (C_delay) ============
print("\n--- 4. Group Delay Asymmetry (C_delay) ---")
w_even = sum(w_gd[i]*gamma[i] for i in range(0, n_cut, 2))
w_odd = sum(w_gd[i]*gamma[i] for i in range(1, n_cut, 2))
C_delay = (w_even - w_odd) / (w_even + w_odd)
print(f"C_delay = (Σw_even·γ − Σw_odd·γ) / (Σw·γ) = {C_delay:.6f}")

# ============ 5. RG Flow β-Function Coefficients ============
print("\n--- 5. RG Flow β-Function Coefficients ---")
# β₁ = C_delay (group delay asymmetry)
# β₂ = skewness_gd × σ_gd / μ_gd  (group-delay-weighted skewness contribution)
# β₃ = kurtosis_gd × σ²_gd / μ²_gd  (group-delay-weighted kurtosis contribution)

beta1 = C_delay
beta2 = skew_gd * math.sqrt(var_gd) / mean_gd
beta3 = kurt_gd * var_gd / (mean_gd**2)

print(f"β₁ = C_delay = {beta1:.6f}")
print(f"β₂ = γ₁_gd × σ_gd/μ_gd = {skew_gd:.4f} × {math.sqrt(var_gd)/mean_gd:.4f} = {beta2:.6f}")
print(f"β₃ = γ₂_gd × σ²_gd/μ²_gd = {kurt_gd:.4f} × {var_gd/(mean_gd**2):.6f} = {beta3:.6f}")

# ============ 6. Structural C₁ and C₃ ============
print("\n--- 6. Structural C₁ and C₃ ---")
# C₁ = -β₁ × 2φ⁻¹ × √5  (linear term)
# C₃ = -β₃ × 2φ⁻¹ × √5  (cubic term)
# The cubic term is δ₃(ℓ) = C₃ × (ℓ-0.5)³ × (1-4^{-ℓ})

C1 = -beta1 * 2 * phi**(-1) * 5**0.5
C3 = -beta3 * 2 * phi**(-1) * 5**0.5

print(f"C₁ = -β₁ × 2φ⁻¹ × √5 = -{beta1:.6f} × {2*phi**(-1):.6f} × {5**0.5:.6f} = {C1:.6f}")
print(f"C₃ = -β₃ × 2φ⁻¹ × √5 = -{beta3:.6f} × {2*phi**(-1):.6f} × {5**0.5:.6f} = {C3:.6f}")
print(f"\nC₁ (expected) = -0.16973")
check("C₁ ≈ -0.16973", abs(C1 - (-0.16973)) < 0.001, f"{C1:.6f} vs -0.16973")

# ============ 7. DESI DR2 7-Point Data ============
print("\n--- 7. DESI DR2 7-Point BAO Data ---")
# DESI DR2: 7 tracers
# D_M/rd: LRG1, LRG2, LRG3+ELG, ELG2, Lyα
# D_V/rd: BGS, QSO
desi_data = [
    ('BGS',      0.295, 'DV', 7.942, 0.075),
    ('LRG1',     0.510, 'DM', 13.588, 0.167),
    ('LRG2',     0.706, 'DM', 17.351, 0.177),
    ('LRG3+ELG', 0.934, 'DM', 21.576, 0.152),
    ('ELG2',     1.321, 'DM', 27.601, 0.318),
    ('QSO',      1.484, 'DV', 26.055, 0.398),
    ('Lyα',      2.330, 'DM', 38.988, 0.531),
]

# ============ 8. D_app Formula ============
def D_orig(ell):
    """Original D_app formula (Formula 60, linear projection)"""
    return R_H * (1 - 4**(-ell)) * (1 + 2*phi**(-1)*ell)

def D_lin(ell):
    """D_app with linear group delay correction"""
    delta1 = C1 * (ell - 0.5) * (1 - 4**(-ell))
    return R_H * (1 - 4**(-ell)) * (1 + 2*phi**(-1)*ell + delta1)

def D_cubic(ell):
    """D_app with linear + cubic group delay correction"""
    delta1 = C1 * (ell - 0.5) * (1 - 4**(-ell))
    delta3 = C3 * (ell - 0.5)**3 * (1 - 4**(-ell))
    return R_H * (1 - 4**(-ell)) * (1 + 2*phi**(-1)*ell + delta1 + delta3)

def D_cubic_scaled(ell, scale=1.0):
    """D_app with linear + cubic correction, scale factor for C₃"""
    delta1 = C1 * (ell - 0.5) * (1 - 4**(-ell))
    delta3 = C3 * scale * (ell - 0.5)**3 * (1 - 4**(-ell))
    return R_H * (1 - 4**(-ell)) * (1 + 2*phi**(-1)*ell + delta1 + delta3)

def DV_from_DM(dm, dh, z):
    """Compute D_V from D_M and D_H"""
    return (z * dm**2 * dh)**(1/3)

def DH_from_D(D_func, z):
    """D_H = dD_app/dz"""
    dz = 1e-6
    ell = math.log(1+z, 4) if z > 0 else 0
    ell_p = math.log(1+z+dz, 4)
    ell_m = math.log(1+z-dz, 4) if z-dz > 0 else 0
    if z-dz <= 0:
        return 0
    return (D_func(ell_p) - D_func(ell_m)) / (2*dz)

# Compute χ² for all three versions
def compute_chi2(D_func, label):
    chi2 = 0
    print(f"\n{label}:")
    print(f"{'Sample':<12} {'z':<6} {'Type':<4} {'D/rd':<10} {'DESI':<10} {'dev%':<10} {'σ':<8}")
    print("-" * 60)
    for name, z, dtype, obs, err in desi_data:
        ell = math.log(1+z, 4)
        d_app = D_func(ell)
        
        if dtype == 'DM':
            pred = d_app / rd_c
        elif dtype == 'DV':
            dh = DH_from_D(D_func, z)
            pred = DV_from_DM(d_app, dh, z) / rd_c
        
        sigma = (pred - obs) / err
        chi2 += sigma**2
        dev = (pred/obs - 1)*100
        print(f"{name:<12} {z:<6.3f} {dtype:<4} {pred:<10.3f} {obs:<10.3f} {dev:>+8.2f}% {sigma:>+6.2f}")
    
    print(f"χ² = {chi2:.2f} ({len(desi_data)} dof), χ²/dof = {chi2/len(desi_data):.2f}")
    return chi2

chi2_orig = compute_chi2(D_orig, "Original (no correction)")
chi2_lin = compute_chi2(D_lin, "Linear correction (C₁ only)")
chi2_cub = compute_chi2(D_cubic, "Cubic correction (C₁ + C₃)")

print(f"\n{'=' * 70}")
print("χ² Summary:")
print(f"  Original:     {chi2_orig:.2f}")
print(f"  Linear:       {chi2_lin:.2f}  (improvement: {(1-chi2_lin/chi2_orig)*100:.1f}%)")
print(f"  Linear+Cubic: {chi2_cub:.2f}  (improvement: {(1-chi2_cub/chi2_orig)*100:.1f}%)")
print(f"  Cubic improvement over linear: {(1-chi2_cub/chi2_lin)*100:.1f}%")
print(f"{'=' * 70}")

# ============ 9. C₃ Scale Factor Optimization ============
print("\n--- 9. C₃ Scale Factor Optimization ---")
# Find the optimal scale factor for C₃ that minimizes χ²
# This is a diagnostic — the structural value should be close to optimal
import numpy as np

scales = np.linspace(-5, 5, 201)
chi2s = []
for s in scales:
    chi2 = 0
    for name, z, dtype, obs, err in desi_data:
        ell = math.log(1+z, 4)
        d_app = D_cubic_scaled(ell, s)
        if dtype == 'DM':
            pred = d_app / rd_c
        elif dtype == 'DV':
            dh = DH_from_D(D_cubic_scaled, z)
            pred = DV_from_DM(d_app, dh, z) / rd_c
        chi2 += ((pred - obs)/err)**2
    chi2s.append(chi2)

best_idx = np.argmin(chi2s)
best_scale = scales[best_idx]
best_chi2 = chi2s[best_idx]
C3_opt = C3 * best_scale

print(f"Optimal C₃ scale factor: {best_scale:.4f}")
print(f"Optimal C₃ value: {C3_opt:.6f}")
print(f"Structural C₃: {C3:.6f}")
print(f"χ² at optimal: {best_chi2:.2f} (vs linear {chi2_lin:.2f})")
print(f"Ratio C₃_opt / C₃_structural = {best_scale:.4f}")

# ============ 10. Residual Analysis ============
print("\n--- 10. Residual Analysis of Cubic Correction ---")
print(f"{'z':<6} {'ℓ':<6} {'(ℓ-0.5)³':<12} {'δ₁(%)':<10} {'δ₃(%)':<10} {'total δ(%)':<12} {'residual(lin)':<14} {'residual(cub)':<14}")
print("-" * 74)
for name, z, dtype, obs, err in desi_data:
    ell = math.log(1+z, 4)
    d_orig = D_orig(ell)
    d_lin = D_lin(ell)
    d_cub = D_cubic(ell)
    
    delta1_pct = C1 * (ell - 0.5) * (1 - 4**(-ell)) * 100
    delta3_pct = C3 * (ell - 0.5)**3 * (1 - 4**(-ell)) * 100
    delta_total_pct = (d_cub/d_orig - 1)*100
    
    if dtype == 'DM':
        res_lin = (d_lin/rd_c / obs - 1)*100
        res_cub = (d_cub/rd_c / obs - 1)*100
    else:
        dh_lin = DH_from_D(D_lin, z)
        dh_cub = DH_from_D(D_cubic, z)
        dv_lin = DV_from_DM(d_lin, dh_lin, z) / rd_c
        dv_cub = DV_from_DM(d_cub, dh_cub, z) / rd_c
        res_lin = (dv_lin / obs - 1)*100
        res_cub = (dv_cub / obs - 1)*100
    
    print(f"{z:<6.3f} {ell:<6.3f} {(ell-0.5)**3:<+12.6f} {delta1_pct:<+10.3f} "
          f"{delta3_pct:<+10.3f} {delta_total_pct:<+12.3f} {res_lin:<+14.2f}% {res_cub:<+14.2f}%")

# ============ 11. H_eff(0) Consistency Check ============
print("\n--- 11. H_eff(0) Consistency Check ---")
def H_eff(D_func, z):
    dz = 1e-6
    ell = math.log(1+z, 4) if z > 0 else 0
    ell_p = math.log(1+z+dz, 4)
    ell_m = math.log(1+z-dz, 4) if z-dz > 0 else 0
    dD = (D_func(ell_p) - D_func(ell_m)) / (2*dz) if z-dz > 0 else 0
    return c_mpc_gyr / dD * KMS if dD > 0 else 0

H0_orig = H_eff(D_orig, 0.001)
H0_lin = H_eff(D_lin, 0.001)
H0_cub = H_eff(D_cubic, 0.001)

print(f"H_eff(0) original:    {H0_orig:.4f} km/s/Mpc")
print(f"H_eff(0) linear:      {H0_lin:.4f} km/s/Mpc (Δ={H0_lin-H0_orig:.4f})")
print(f"H_eff(0) cubic:       {H0_cub:.4f} km/s/Mpc (Δ={H0_cub-H0_orig:.4f})")
check("H_eff(0) preserved (cubic)", abs(H0_cub - 72.59) < 0.1, f"{H0_cub:.4f}")

# ============ 12. Structural Meaning of C₃ ============
print("\n--- 12. Structural Meaning of C₃ ---")
print(f"""
C₃ = {C3:.6f} = -β₃ × 2φ⁻¹ × √5

Structural derivation chain:
  β₃ = γ₂_gd × σ²_gd/μ²_gd = {kurt_gd:.4f} × {var_gd/(mean_gd**2):.6f} = {beta3:.6f}
  where γ₂_gd = excess kurtosis of group-delay-weighted K_Chain spectrum
  σ²_gd/μ²_gd = relative variance of the spectral distribution
  2φ⁻¹ = 1.23607 = projection elongation factor
  √5 = 2.23607 = Fibonacci structural constant

Physical meaning:
  The linear term C₁ captures the mean asymmetry (odd moment) of the
  group-delay-weighted spectrum. The cubic term C₃ captures the
  tail-asymmetry (excess kurtosis × relative variance) — how much the
  spectral asymmetry itself changes across the mode index range n=1..27.

  A {'' if kurt_gd < 0 else 'positive'} excess kurtosis indicates the spectrum
  has {'heavier' if kurt_gd > 0 else 'lighter'} tails than Gaussian, meaning
  the group delay correction needs {'more' if kurt_gd > 0 else 'less'} higher-order
  curvature at extreme ℓ values.

  Since C₃ {'' if C3 < 0 else '> 0'}, the cubic term {'adds to' if C3 < 0 else 'subtracts from'}
  the linear correction at ℓ > 0.5 and {'subtracts from' if C3 < 0 else 'adds to'}
  it at ℓ < 0.5 — this {'flattens' if C3 < 0 else 'steepens'} the residual pattern.
""")

# ============ Summary ============
print(f"\n{'=' * 70}")
print(f"Summary: {PASS}/{PASS+FAIL}")
print(f"{'=' * 70}")

result = {
    'desi_7pt_chi2_orig': round(chi2_orig, 2),
    'desi_7pt_chi2_lin': round(chi2_lin, 2),
    'desi_7pt_chi2_cubic': round(chi2_cub, 2),
    'improvement_lin_pct': round((1-chi2_lin/chi2_orig)*100, 1),
    'improvement_cubic_pct': round((1-chi2_cub/chi2_orig)*100, 1),
    'C1': round(C1, 6),
    'C3_structural': round(C3, 6),
    'C3_optimal': round(C3_opt, 6),
    'C3_optimal_scale': round(best_scale, 4),
    'beta1': round(beta1, 6),
    'beta3': round(beta3, 6),
    'kurtosis_gd': round(kurt_gd, 6),
    'skewness_gd': round(skew_gd, 6),
    'var_gd': round(var_gd, 6),
    'mean_gd': round(mean_gd, 6),
    'H0_orig': round(H0_orig, 4),
    'H0_lin': round(H0_lin, 4),
    'H0_cub': round(H0_cub, 4),
    'pass': PASS,
    'fail': FAIL
}

with open('data/86_cubic_correction.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"✅ 結果 -> data/86_cubic_correction.json")