#!/usr/bin/env python3
"""
O51/86b: Refined Cubic Correction Analysis — Fibonacci Factor F₅ = 5
=====================================================================
The structural C₃ = -0.048693 gives χ²=17.72. The optimal is C₃⁺ = -0.2435 = 5×C₃.
The factor 5 = F₅ suggests a Fibonacci structural factor in the cubic term.
Let's verify this with finer resolution and understand the nonlinear coupling.
"""
import json, math, numpy as np

R_H = 4129.94
N_d = 44
phi = (1 + math.sqrt(5)) / 2
rd_c = math.pi * R_H / 88 * 420/421
c_mpc_gyr = 306.601394
KMS = 977.8

# DESI DR2 7-point data
desi_data = [
    ('BGS',      0.295, 'DV', 7.942, 0.075),
    ('LRG1',     0.510, 'DM', 13.588, 0.167),
    ('LRG2',     0.706, 'DM', 17.351, 0.177),
    ('LRG3+ELG', 0.934, 'DM', 21.576, 0.152),
    ('ELG2',     1.321, 'DM', 27.601, 0.318),
    ('QSO',      1.484, 'DV', 26.055, 0.398),
    ('Lyα',      2.330, 'DM', 38.988, 0.531),
]

# Group delay spectral moments
n_cut = 27
gamma = [4*math.sin(math.pi*n/(2*N_d))**2 for n in range(N_d)]
v_g = [math.cos(math.pi*n/(2*N_d)) for n in range(N_d)]
w_gd = [1/v_g[n] for n in range(n_cut)]
w_weighted = [w_gd[n]*gamma[n] for n in range(n_cut)]
sum_w_w = sum(w_weighted)
mean_gd = sum((n+1)*w_weighted[n] for n in range(n_cut)) / sum_w_w
var_gd = sum((n+1-mean_gd)**2*w_weighted[n] for n in range(n_cut)) / sum_w_w
kurt_gd = sum((n+1-mean_gd)**4*w_weighted[n] for n in range(n_cut)) / sum_w_w / var_gd**2 - 3

w_even = sum(w_gd[i]*gamma[i] for i in range(0, n_cut, 2))
w_odd = sum(w_gd[i]*gamma[i] for i in range(1, n_cut, 2))
C_delay = (w_even - w_odd) / (w_even + w_odd)
beta1 = C_delay
beta3 = kurt_gd * var_gd / (mean_gd**2)

C1 = -beta1 * 2 * phi**(-1) * 5**0.5
C3_structural = -beta3 * 2 * phi**(-1) * 5**0.5

def D_lin(ell, C3_scale=0):
    delta1 = C1 * (ell - 0.5) * (1 - 4**(-ell))
    delta3 = C3_structural * C3_scale * (ell - 0.5)**3 * (1 - 4**(-ell))
    return R_H * (1 - 4**(-ell)) * (1 + 2*phi**(-1)*ell + delta1 + delta3)

def DH_from_D(D_func, z):
    dz = 1e-6
    ell = math.log(1+z, 4) if z > 0 else 0
    ell_p = math.log(1+z+dz, 4)
    ell_m = math.log(1+z-dz, 4) if z-dz > 0 else 0
    if z-dz <= 0: return 0
    return (D_func(ell_p) - D_func(ell_m)) / (2*dz)

def DV_from_DM(dm, dh, z):
    return (z * dm**2 * dh)**(1/3)

def compute_chi2(scale):
    chi2 = 0
    D_func = lambda ell: D_lin(ell, scale)
    for name, z, dtype, obs, err in desi_data:
        ell = math.log(1+z, 4)
        d_app = D_func(ell)
        if dtype == 'DM':
            pred = d_app / rd_c
        elif dtype == 'DV':
            dh = DH_from_D(D_func, z)
            pred = DV_from_DM(d_app, dh, z) / rd_c
        chi2 += ((pred - obs)/err)**2
    return chi2

# Fine scan around the structural value and the optimal
print("=" * 70)
print("Refined C₃ Scale Factor Analysis")
print("=" * 70)

# Scan 1: wide range to confirm minima
scales_wide = np.linspace(-10, 10, 401)
chi2_wide = np.array([compute_chi2(s) for s in scales_wide])
best_idx = np.argmin(chi2_wide)
best_scale = scales_wide[best_idx]
best_chi2 = chi2_wide[best_idx]

print(f"\nWide scan [-10, 10]:")
print(f"  Best scale factor: {best_scale:.6f}")
print(f"  Best C₃ = C₃_structural × {best_scale:.6f} = {C3_structural * best_scale:.6f}")
print(f"  χ² = {best_chi2:.2f}")

# Scan 2: fine around the best
delta = 0.5
scales_fine = np.linspace(best_scale - delta, best_scale + delta, 201)
chi2_fine = np.array([compute_chi2(s) for s in scales_fine])
best_idx2 = np.argmin(chi2_fine)
best_scale2 = scales_fine[best_idx2]
best_chi2_2 = chi2_fine[best_idx2]

print(f"\nFine scan [{best_scale-delta:.2f}, {best_scale+delta:.2f}]:")
print(f"  Best scale factor: {best_scale2:.6f}")
print(f"  Best C₃: {C3_structural * best_scale2:.6f}")
print(f"  χ² = {best_chi2_2:.2f}")

# Check if the scale is exactly 5 = F₅
print(f"\nClosest integer/Fibonacci values:")
for fib in [1, 2, 3, 5, 8, 13]:
    chi2_fib = compute_chi2(fib)
    dev = abs(fib - best_scale2)
    print(f"  Fₓ={fib}: χ²={chi2_fib:.2f}, deviation from best={dev:.4f}")

# Print χ² as function of scale around the Fibonacci values
print(f"\nχ² vs scale factor (near F₅=5):")
for s in [4.0, 4.5, 4.8, 4.9, 5.0, 5.1, 5.2, 5.5, 6.0]:
    chi2 = compute_chi2(s)
    print(f"  scale={s:.1f}: χ²={chi2:.2f}")

# ============ POLYNOMIAL MODEL OF RESIDUALS ============
print(f"\n{'=' * 70}")
print("Polynomial Residual Model — Direct Fit")
print("=" * 70)

# The residual after linear correction: r(ℓ) = (D_corr - D_DESI) / D_DESI
# Model: r(ℓ) = A₃ × (ℓ-0.5)³ × (1-4^{-ℓ})
# A₃ is the "effective" cubic coefficient from the data

residuals = []
for name, z, dtype, obs, err in desi_data:
    ell = math.log(1+z, 4)
    d_lin = D_lin(ell, 0)
    if dtype == 'DM':
        pred = d_lin / rd_c
    else:
        dh = DH_from_D(lambda e: D_lin(e, 0), z)
        pred = DV_from_DM(d_lin, dh, z) / rd_c
    res = (pred/obs - 1)  # fractional residual
    residuals.append((ell, res, err/obs))

print(f"{'z':<6} {'ℓ':<8} {'residual':<12} {'envelope*':<14} {'A₃_eff':<10}")
print("-" * 50)
for (name, z, _, _, _), (ell, res, rel_err) in zip(desi_data, residuals):
    envelope = (ell - 0.5)**3 * (1 - 4**(-ell))
    A3_eff = res / envelope if abs(envelope) > 1e-10 else 0
    print(f"{z:<6.3f} {ell:<8.4f} {res:<+12.4f} {envelope:<+14.6f} {A3_eff:<+10.4f}")

# Weighted average of A₃_eff
A3_vals = [res / ((ell - 0.5)**3 * (1 - 4**(-ell))) 
           for (ell, res, _) in residuals 
           if abs((ell - 0.5)**3 * (1 - 4**(-ell))) > 1e-10]
weights = [1/rel_err**2 for (_, _, rel_err) in residuals 
           if abs((ell - 0.5)**3 * (1 - 4**(-ell))) > 1e-10]

A3_avg = sum(a*w for a, w in zip(A3_vals, weights)) / sum(weights)
print(f"\nWeighted mean A₃_eff = {A3_avg:.4f}")
print(f"Structural C₃ = {C3_structural:.6f}")
print(f"Ratio A₃_eff / C₃_structural = {A3_avg/C3_structural:.4f}")

# ============ RG Flow Third-Order Term ============
print(f"\n{'=' * 70}")
print("RG Flow Third-Order Expansion")
print("=" * 70)

# The full δ(ℓ) correction from RG flow:
# dg/dℓ = β₁g + β₂g² + β₃g³
# The solution g(ℓ) = β₁ℓ + β₂β₁²ℓ²/2 + (β₂²β₁³ + β₃β₁³)ℓ³/6 + O(ℓ⁴)
# 
# The cubic term in the δ(ℓ) expansion comes from the ℓ³ term in g(ℓ):
# δ₃(ℓ) = -(β₂²β₁³ + β₃β₁³) × ℓ³/6 × 2φ⁻¹ × √5 × (ℓ-0.5)/ℓ_adj ...
# 
# But the actual form is δ₃(ℓ) = C₃ × (ℓ-0.5)³ × (1-4^{-ℓ})
# The cubic term in the RG flow has both β₂² and β₃ contributions

# Let's compute the full ℓ³ coefficient from RG flow
beta2 = -0.234812  # from the script output

# ℓ³ coefficient from RG flow: (β₂²β₁³ + β₃β₁³)/6
# = β₁³(β₂² + β₃)/6
cubic_rg = beta1**3 * (beta2**2 + beta3) / 6
print(f"β₁ = {beta1:.6f}")
print(f"β₂ = {beta2:.6f}")
print(f"β₃ = {beta3:.6f}")
print(f"\nRG flow ℓ³ coefficient:")
print(f"  β₂²β₁³ = {beta2**2 * beta1**3:.6f}")
print(f"  β₃β₁³ = {beta3 * beta1**3:.6f}")
print(f"  Sum = {beta2**2 * beta1**3 + beta3 * beta1**3:.6f}")
print(f"  Divided by 6 = {cubic_rg:.6f}")

# The ratio of the β₂² term to the β₃ term
ratio_beta2sq_to_beta3 = beta2**2 / beta3
print(f"\n  β₂²/β₃ = {ratio_beta2sq_to_beta3:.2f}")
print(f"  (β₂²+β₃)/β₃ = {1 + ratio_beta2sq_to_beta3:.2f}")
print(f"  → The β₂² term is {ratio_beta2sq_to_beta3:.1f}× the β₃ term")
print(f"  → The β₂² cross-term dominates the cubic correction!")

# The full C₃ including the β₂² cross-term:
# C₃_full = -(β₂²β₁³ + β₃β₁³) × 2φ⁻¹ × √5 × scale_factor
# where scale_factor converts the ℓ³ coefficient to the (ℓ-0.5)³ form
# 
# At ℓ=1: (ℓ-0.5)³ = 0.125, ℓ³ = 1.0
# The ratio ℓ³/(ℓ-0.5)³ at ℓ=1 is 8
# So the effective C₃ with the full RG cubic is:
# C₃_RG = -(β₂²β₁³ + β₃β₁³)/6 × 2φ⁻¹ × √5 × 8

C3_RG_full = -cubic_rg * 2 * phi**(-1) * 5**0.5 * 8
print(f"\nC₃ (structural, kurtosis only) = {C3_structural:.6f}")
print(f"C₃ (RG full, incl β₂² cross-term) = {C3_RG_full:.6f}")
print(f"Ratio C₃_RG / C₃_structural = {C3_RG_full/C3_structural:.4f}")

# Check if this matches the optimal F₅=5
print(f"\nOptimal scale factor (from χ² scan) = {best_scale2:.4f}")
print(f"RG full cubic / structural kurtosis = {C3_RG_full/C3_structural:.4f}")

# ============ Final Summary ============
chi2_lin = compute_chi2(0)
chi2_cub_struct = compute_chi2(1)
chi2_cub_RG_full = compute_chi2(C3_RG_full/C3_structural)
chi2_cub_opt = compute_chi2(best_scale2)

print(f"\n{'=' * 70}")
print("Final χ² Summary")
print("=" * 70)
print(f"  Original (no correction):         χ² = 42.23")
print(f"  Linear only (C₁):                 χ² = {chi2_lin:.2f}")
print(f"  Cubic (structural, kurtosis only): χ² = {chi2_cub_struct:.2f}")
print(f"  Cubic (RG full, β₂²+β₃):          χ² = {chi2_cub_RG_full:.2f}")
print(f"  Cubic (optimal scale={best_scale2:.4f}):      χ² = {chi2_cub_opt:.2f}")
print(f"")
print(f"Key insight: β₂²/β₃ = {ratio_beta2sq_to_beta3:.1f}")
print(f"The β₂² (skewness-squared) cross-term dominates the cubic correction")
print(f"over the pure β₃ (kurtosis) term by {ratio_beta2sq_to_beta3:.1f}×")
print(f"")
print(f"C₃ (structural, kurtosis-only) = {C3_structural:.6f}")
print(f"C₃ (RG full, β₂²+β₃) = {C3_RG_full:.6f}")
print(f"C₃ (optimal) = {C3_structural * best_scale2:.6f}")

result = {
    'C3_structural': round(C3_structural, 6),
    'C3_RG_full': round(C3_RG_full, 6),
    'C3_optimal': round(C3_structural * best_scale2, 6),
    'optimal_scale': round(best_scale2, 4),
    'chi2_linear': round(chi2_lin, 2),
    'chi2_cubic_structural': round(chi2_cub_struct, 2),
    'chi2_cubic_RG_full': round(chi2_cub_RG_full, 2),
    'chi2_cubic_optimal': round(chi2_cub_opt, 2),
    'beta2sq_beta3_ratio': round(ratio_beta2sq_to_beta3, 1),
    'beta1': round(beta1, 6),
    'beta2': round(beta2, 6),
    'beta3': round(beta3, 6),
    'kurtosis_gd': round(kurt_gd, 6),
}

with open('data/86b_cubic_refined.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"\n✅ 結果 -> data/86b_cubic_refined.json")