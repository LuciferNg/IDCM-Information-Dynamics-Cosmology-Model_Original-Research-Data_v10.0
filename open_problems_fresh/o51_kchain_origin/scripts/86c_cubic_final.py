#!/usr/bin/env python3
"""
O51/86c: FINAL — Cubic Correction δ₃(ℓ) Analysis
=================================================
Synthesizing all findings from scripts 81-86b.
Correct K_Chain spectrum indexing (n=1..44).
"""
import json, math, numpy as np

R_H = 4129.94
N_d = 44
phi = (1 + math.sqrt(5)) / 2
rd_c = math.pi * R_H / 88 * 420/421
c_mpc_gyr = 306.601394
KMS = 977.8

# DESI DR2 7-point BAO data
desi_data = [
    ('BGS',      0.295, 'DV', 7.942, 0.075),
    ('LRG1',     0.510, 'DM', 13.588, 0.167),
    ('LRG2',     0.706, 'DM', 17.351, 0.177),
    ('LRG3+ELG', 0.934, 'DM', 21.576, 0.152),
    ('ELG2',     1.321, 'DM', 27.601, 0.318),
    ('QSO',      1.484, 'DV', 26.055, 0.398),
    ('Lyα',      2.330, 'DM', 38.988, 0.531),
]

# ============ K_Chain Spectrum (n=1..44, correct indexing) ============
gamma = [4*math.sin(math.pi*n/(2*N_d))**2 for n in range(1, N_d+1)]
v_g = [math.cos(math.pi*n/(2*N_d)) for n in range(1, N_d+1)]

n_cut = 27  # F_proj = 17 → n ≤ 27
w_gd = [1/v_g[n] for n in range(n_cut)]  # group delay weights, n=1..27

# Group-delay-weighted spectrum
w_weighted = [w_gd[n]*gamma[n] for n in range(n_cut)]
sum_w_w = sum(w_weighted)
mean_gd = sum((n+1)*w_weighted[n] for n in range(n_cut)) / sum_w_w
var_gd = sum((n+1-mean_gd)**2*w_weighted[n] for n in range(n_cut)) / sum_w_w
skew_gd = sum((n+1-mean_gd)**3*w_weighted[n] for n in range(n_cut)) / sum_w_w / var_gd**1.5
kurt_gd = sum((n+1-mean_gd)**4*w_weighted[n] for n in range(n_cut)) / sum_w_w / var_gd**2 - 3

# C_delay
w_even = sum(w_gd[i]*gamma[i] for i in range(0, n_cut, 2))
w_odd = sum(w_gd[i]*gamma[i] for i in range(1, n_cut, 2))
C_delay = (w_even - w_odd) / (w_even + w_odd)

# β-function coefficients
beta1 = C_delay
beta2 = skew_gd * math.sqrt(var_gd) / mean_gd
beta3 = kurt_gd * var_gd / (mean_gd**2)

# C coefficients
C1 = -beta1 * 2 * phi**(-1) * 5**0.5
C3_kurt = -beta3 * 2 * phi**(-1) * 5**0.5  # kurtosis-only
C3_RG = -(beta2**2 * beta1**3 + beta3 * beta1**3) / 6 * 2 * phi**(-1) * 5**0.5 * 8  # full RG

print("=" * 70)
print("O51/86c: Cubic Correction δ₃(ℓ) — FINAL ANALYSIS")
print("=" * 70)
print(f"\nK_Chain Spectrum Summary:")
print(f"  C_delay = {C_delay:.6f}")
print(f"  β₁ = {beta1:.6f}")
print(f"  β₂ = {beta2:.6f}  (skewness_gd={skew_gd:.4f}, σ_gd/μ_gd={math.sqrt(var_gd)/mean_gd:.4f})")
print(f"  β₃ = {beta3:.6f}  (kurtosis_gd={kurt_gd:.4f}, σ²_gd/μ²_gd={var_gd/(mean_gd**2):.6f})")
print(f"  C₁ = {C1:.6f}  (linear term)")
print(f"  C₃ (kurtosis-only) = {C3_kurt:.6f}")
print(f"  β₂²/β₃ = {beta2**2/beta3:.1f}  (skewness-squared cross-term dominates)")

# ============ D_app functions ============
def D_func_orig(ell):
    return R_H * (1 - 4**(-ell)) * (1 + 2*phi**(-1)*ell)

def D_func_lin(ell):
    delta1 = C1 * (ell - 0.5) * (1 - 4**(-ell))
    return R_H * (1 - 4**(-ell)) * (1 + 2*phi**(-1)*ell + delta1)

def D_func_cub(ell, C3_scale=1):
    delta1 = C1 * (ell - 0.5) * (1 - 4**(-ell))
    delta3 = C3_kurt * C3_scale * (ell - 0.5)**3 * (1 - 4**(-ell))
    return R_H * (1 - 4**(-ell)) * (1 + 2*phi**(-1)*ell + delta1 + delta3)

def DH_from_z(Dfunc, z):
    dz = 1e-6
    ell = math.log(1+z, 4)
    ell_p = math.log(1+z+dz, 4)
    ell_m = math.log(1+z-dz, 4) if z-dz > 0 else 0
    if z-dz <= 0: return 0
    return (Dfunc(ell_p) - Dfunc(ell_m)) / (2*dz)

def DV_from_DM(dm, dh, z):
    return (z * dm**2 * dh)**(1/3)

def compute_chi2(Dfunc):
    chi2 = 0
    for name, z, dtype, obs, err in desi_data:
        ell = math.log(1+z, 4)
        d_app = Dfunc(ell)
        if dtype == 'DM':
            pred = d_app / rd_c
        else:
            dh = DH_from_z(Dfunc, z)
            pred = DV_from_DM(d_app, dh, z) / rd_c
        chi2 += ((pred - obs)/err)**2
    return chi2

def compute_chi2_scale(C3_scale):
    return compute_chi2(lambda e: D_func_cub(e, C3_scale))

# ============ χ² Scan ============
print(f"\n{'=' * 70}")
print("χ² Scan for C₃ Scale Factor")
print("=" * 70)

scales = np.linspace(-5, 25, 601)
chi2s = np.array([compute_chi2_scale(s) for s in scales])
best_idx = np.argmin(chi2s)
best_scale = scales[best_idx]

chi2_lin = compute_chi2(D_func_lin)
chi2_cub_kurt = compute_chi2(lambda e: D_func_cub(e, 1))
chi2_cub_opt = compute_chi2(lambda e: D_func_cub(e, best_scale))

print(f"\n{'scale':<8} {'χ²':<10} {'Δχ²':<10} {'χ²/dof':<8}")
print("-" * 36)
for s in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]:
    chi2 = compute_chi2(lambda e: D_func_cub(e, s))
    print(f"{s:<8.0f} {chi2:<10.2f} {chi2-chi2_lin:<+10.2f} {chi2/7:<8.2f}")

print(f"\nBest scale: {best_scale:.4f}")
print(f"Best C₃ = C₃_kurt × {best_scale:.4f} = {C3_kurt * best_scale:.6f}")
print(f"χ² at best: {chi2_cub_opt:.2f}")

# Check Fibonacci values
print(f"Fibonacci scale factors:")
for fib in [1, 2, 3, 5, 8, 13]:
    chi2 = compute_chi2(lambda e: D_func_cub(e, fib))
    print(f"  F_x={fib:<2}: chi2={chi2:.2f}")

# ============ Detailed Per-Bin Report ============
print(f"\n{'=' * 70}")
print("Per-Bin Residual Report")
print("=" * 70)

def print_residuals(label, Dfunc):
    print(f"\n{label}:")
    print(f"{'Sample':<12} {'z':<6} {'ell':<6} {'pred':<8} {'DESI':<8} {'dev%':<10} {'sig':<8}")
    print("-" * 58)
    for name, z, dtype, obs, err in desi_data:
        ell = math.log(1+z, 4)
        d_app = Dfunc(ell)
        if dtype == 'DM':
            pred = d_app / rd_c
        else:
            dh = DH_from_z(Dfunc, z)
            pred = DV_from_DM(d_app, dh, z) / rd_c
        dev = (pred/obs - 1)*100
        sigma = (pred - obs)/err
        print(f"{name:<12} {z:<6.3f} {ell:<6.3f} {pred:<8.3f} {obs:<8.3f} {dev:>+8.2f}% {sigma:>+6.2f}")

print_residuals("Original (no correction)", D_func_orig)
print_residuals("Linear only (C1)", D_func_lin)
print_residuals("Cubic (structural C3)", lambda e: D_func_cub(e, 1))
print_residuals("Cubic (optimal C3)", lambda e: D_func_cub(e, best_scale))

# ============ H_eff(0) Check ============
print(f"\n{'=' * 70}")
print("H_eff(0) Consistency Check")
print("=" * 70)

def H_eff_from_Dfunc(Dfunc, z=0.001):
    dz = 1e-6
    ell = math.log(1+z, 4)
    ell_p = math.log(1+z+dz, 4)
    ell_m = math.log(1+z-dz, 4) if z-dz > 0 else 0
    dD = (Dfunc(ell_p) - Dfunc(ell_m)) / (2*dz) if z-dz > 0 else 0
    return c_mpc_gyr / dD * KMS if dD > 0 else 0

H0_orig = H_eff_from_Dfunc(D_func_orig)
H0_lin = H_eff_from_Dfunc(D_func_lin)
H0_cub = H_eff_from_Dfunc(lambda e: D_func_cub(e, 1))
H0_opt = H_eff_from_Dfunc(lambda e: D_func_cub(e, best_scale))

print(f"H_eff(0) original:    {H0_orig:.4f} km/s/Mpc")
print(f"H_eff(0) linear:      {H0_lin:.4f}")
print(f"H_eff(0) cubic (str): {H0_cub:.4f} (Δ={H0_cub-H0_orig:.4f})")
print(f"H_eff(0) cubic (opt): {H0_opt:.4f} (Δ={H0_opt-H0_orig:.4f})")

# ============ Structural Meaning ============
print(f"\n{'=' * 70}")
print("STRUCTURAL MEANING OF C₃")
print("=" * 70)
print(f"""
Cubic Correction Term:
  delta3(ell) = C3 x (ell-0.5)^3 x (1-4^{{-ell}})

Structural Derivation:
  C3 = -beta3 x 2*phi^{-1} x sqrt(5) = -{beta3:.6f} x {2*phi**(-1):.6f} x {5**0.5:.6f} = {C3_kurt:.6f}

  where:
  beta3 = gamma2_gd x sigma2_gd/mu2_gd = {kurt_gd:.4f} x {var_gd/(mean_gd**2):.6f} = {beta3:.6f}
  gamma2_gd = excess kurtosis of group-delay-weighted K_Chain spectrum
  sigma2_gd/mu2_gd = relative variance of the spectral distribution
  2*phi^{-1} = 1.23607 = projection elongation factor
  sqrt(5) = 2.23607 = Fibonacci structural constant

RG Flow Cross-Term Correction:
  The full cubic correction is dominated by the beta2^2 (skewness-squared) term:
  beta2^2/beta3 = {beta2**2/beta3:.1f}x

  C3(RG) = -(beta2^2*beta1^3 + beta3*beta1^3)/6 x 2*phi^{-1} x sqrt(5) x 8 = {C3_RG:.6f}

Residual Pattern:
  After linear correction (C1 = {C1:.6f}):
  - LRG1 (z=0.51, ell=0.30): residual -3.75%  -> need more positive correction
  - Lya   (z=2.33, ell=0.87): residual +2.24%  -> need more negative correction

  The cubic term (ell-0.5)^3 has the right sign structure:
  - ell<0.5: (ell-0.5)^3 < 0 -> with C3<0 gives delta3>0 (adds to D_app) OK
  - ell>0.5: (ell-0.5)^3 > 0 -> with C3<0 gives delta3<0 (subtracts from D_app) OK

chi2 Impact:
  Original (no correction):    42.23
  Linear (C1 only):            18.09  (57.2% improvement)
  Cubic (structural C3):       {chi2_cub_kurt:.2f}  ({(1-chi2_cub_kurt/42.23)*100:.1f}% improvement)
  Cubic (optimal C3x{best_scale:.2f}):  {chi2_cub_opt:.2f}  ({(1-chi2_cub_opt/42.23)*100:.1f}% improvement)

Conclusion:
  The cubic correction delta3(ell) is structurally small (|C3/C1| = {abs(C3_kurt/C1):.4f})
  because the group-delay-weighted spectrum has moderate excess kurtosis
  (gamma2 = {kurt_gd:.4f}). The total chi2 improvement from adding the cubic term is
  {chi2_lin-chi2_cub_kurt:.2f} points (structural) to {chi2_lin-chi2_cub_opt:.2f} points (optimal).

  The residual pattern is NOT fully captured by a single cubic term -- the
  residuals are not a pure (ell-0.5)^3 function. The LRG1 outlier at -3.75%
  dominates the chi2, suggesting a more complex effect (e.g., mode-specific
  impedance at the SYNC transition around z=0.6) rather than a simple
  higher-order odd-parity term.
""")

result = {
    'C1': round(C1, 6),
    'C3_kurtosis': round(C3_kurt, 6),
    'C3_RG_full': round(C3_RG, 6),
    'C3_optimal': round(C3_kurt * best_scale, 6),
    'optimal_scale': round(best_scale, 4),
    'chi2_original': 42.23,
    'chi2_linear': round(chi2_lin, 2),
    'chi2_cubic_structural': round(chi2_cub_kurt, 2),
    'chi2_cubic_optimal': round(chi2_cub_opt, 2),
    'beta1': round(beta1, 6),
    'beta2': round(beta2, 6),
    'beta3': round(beta3, 6),
    'kurtosis_gd': round(kurt_gd, 6),
    'skewness_gd': round(skew_gd, 6),
    'beta2sq_beta3_ratio': round(beta2**2/beta3, 1),
    'C3_C1_ratio': round(abs(C3_kurt/C1), 4),
    'H0_orig': round(H0_orig, 4),
    'H0_cubic': round(H0_cub, 4),
}

with open('data/86c_cubic_final.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"✅ 結果 -> data/86c_cubic_final.json")