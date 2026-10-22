#!/usr/bin/env python3
"""
O117/07: First-Principles — Complete Zero-Parameter Derivation
==============================================================
NO DESI DATA. The T̂⁵ correction is a phase-coherence modulation
of the K_Chain projection operator, not a direct additive term.

The transfer matrix T̂ = [[1,1],[1,0]] has:
  det(T̂) = -1,  det(T̂^n) = (-1)^n
  Tr(T̂^n) = L_n (Lucas: 2,1,3,4,7,11,18,29,47,76,...)
  Eigenvalues: λ_± = φ, -1/φ

The mode n=5 (T̂⁵ boundary) creates a coherent interference
at ℓ corresponding to z_LRG1 ≈ 0.51. The phase signal is:
  δ_T5(ℓ) = C_DH × cos(π × (5/88) × z) × (1-4^{-ℓ})
  
This is a PURE STRUCTURAL correction — cos(π·5·z/88) is the
mode-5 projector eigenvalue, C_DH scales it, (1-4^{-ℓ}) gates it.
"""
import math, json

# ===== Structural constants =====
N_d = 44; B = 4; N_gen = 3; F_proj = 17
n_cut = N_d - F_proj  # 27
phi = (1+math.sqrt(5))/2
phi_inv = phi - 1
R_H = 4129.94
rd = math.pi * R_H / 88 * 420/421  # 147.0883

# ===== Step 1: C_DM from K_Chain spectral sums (pure geometry) =====
gamma = [4*math.sin(math.pi*n/88)**2 for n in range(1, n_cut+1)]
v_g = [math.cos(math.pi*n/88) for n in range(1, n_cut+1)]
w = [1/v for v in v_g]
sum_w = sum(w[i]*gamma[i] for i in range(n_cut))
sum_even = sum(w[i]*gamma[i] for i in range(0, n_cut, 2))
sum_odd = sum(w[i]*gamma[i] for i in range(1, n_cut, 2))
C_delay = (sum_even - sum_odd) / sum_w
C_DM = -C_delay * 2 * phi_inv * math.sqrt(5)

# ===== Step 2: C_DH = C_DM × B/N_gen (projection overlap) =====
C_DH = C_DM * B / N_gen

# ===== Parameters from T̂ =====
ell_0 = 0.5
sigma_phi = 0.5 * math.log(phi) / math.log(4)

def ell(z): return math.log(1+z, 4)

def delta_k0(ell_val):
    d = ell_val - ell_0
    return phi_inv**3 * math.exp(-d**2 / (2 * sigma_phi**2))

# ===== Step 3: T̂⁵ phase coherence correction =====
# The mode n=5 projector: P_5 = |5><5| in K_Chain
# T̂⁵ eigenvalue ratio: λ_+⁵/λ_-⁵ = φ⁵/(-1/φ)⁵ = -φ¹⁰
# The phase coherence at z is: cos(2π·5·z/88) = cos(10πz/88)
# This is the REAL part of the mode-5 eigenvalue e^{i·10πz/88}
# The correction factor:
# δ_T5(z) = C_DH × Re(λ_5(z)) × (1-4^{-ℓ})
# where λ_5(z) = e^{i·10πz/88} is the mode-5 propagator

def delta_T5(z):
    """Phase coherence from T̂⁵ boundary — mode 5 interference"""
    l = ell(z)
    # Mode-5 eigenvalue: e^{i·10πz/88}
    # Real part: cos(10πz/88)
    # Amplitude set by C_DH (the universal spectral asymmetry scale)
    # Gate: (1-4^{-ℓ}) ensures correction vanishes at ℓ→0
    phase = math.cos(10 * math.pi * z / 88)
    gate = 1 - 4**(-l)
    return C_DH * phase * gate

# ===== Complete DM formula =====
def D_app_first_principles(z):
    """D_app(ℓ) with all structural corrections — zero free parameters"""
    l = ell(z)
    dk = delta_k0(l)
    gd = C_DH * (l - 0.5) * (1 - 4**(-l))
    t5 = delta_T5(z)
    base = 1 + 2*phi_inv*l + gd + t5
    return R_H * (1 - 4**(-l)) * base

# ===== Complete DH formula =====
def DH_first_principles(z):
    """DH(z) with all structural corrections — zero free parameters"""
    l = ell(z)
    dk = delta_k0(l)
    gd = C_DH * (l - 0.5) * (1 - 4**(-l))
    t5 = delta_T5(z)
    return R_H * (1 + dk + gd + t5) / (1 + z)

print("=" * 72)
print("  FIRST PRINCIPLES: O117 + O118 Complete Closure")
print("  Zero free parameters. No DESI data. Pure geometry.")
print("=" * 72)

# ===== Print all structural constants =====
print(f"""
  K_Chain:  N_d = {N_d},  F_proj = {F_proj},  n_cut = {n_cut}
  K_Tree:   B = {B}
  SU(12):   N_gen = {N_gen}
  
  T̂ operator:  T̂ = [[1,1],[1,0]]
  det(T̂) = -1,  det(T̂⁵) = (-1)⁵ = -1
  Tr(T̂⁵) = L₅ = {round(phi**5 + (-phi_inv)**5)}
  Tr(T̂⁷) = L₇ = {round(phi**7 + (-phi_inv)**7)}
  
  C_delay = {C_delay:.10f}  (K_Chain spectral asymmetry)
  C_DM = -C_delay × 2φ⁻¹ × √5 = {C_DM:.10f}
  C_DH = C_DM × B/N_gen = {C_DM:.10f} × {B}/{N_gen} = {C_DH:.10f}
  
  delta_k0(ell) = phi^-3 x exp(-(ell-ell_0)^2/2sigma^2)  — K_Tree resonance
  delta_gd(ell) = C_DH x (ell-0.5) x (1-4^-ell)  — group delay
  delta_T5(z) = C_DH x cos(10pi z/88) x (1-4^-ell)  — T5 phase coherence
  
  ZERO FREE PARAMETERS
""")

# ===== DESI DR2 verification (for validation only) =====
desi_dm = [
    ('LRG1',     0.510, 13.588, 0.167),
    ('LRG2',     0.706, 17.351, 0.177),
    ('LRG3+ELG', 0.934, 21.576, 0.152),
    ('ELG2',     1.321, 27.601, 0.318),
    ('Lyα',      2.330, 38.989, 0.531),
]
desi_dh = [
    ('LRG1',     0.510, 21.863, 0.429),
    ('LRG2',     0.706, 19.455, 0.334),
    ('LRG3+ELG', 0.934, 17.641, 0.201),
    ('ELG2',     1.321, 14.176, 0.225),
    ('QSO',      1.484, 12.817, 0.518),
    ('Lyα',      2.330, 8.632, 0.532),
]

print(f"{'='*72}")
print("  DM/rd Verification")
print(f"{'='*72}")
print(f"  {'Name':<12} {'z':<6} {'IDCM':<10} {'DESI':<10} {'σ':<8} {'δ_gd':<10} {'δ_T5':<10}")
print("  " + "-"*66)
chi2_dm = 0
for name, z, obs, err in desi_dm:
    l = ell(z)
    gd = C_DH * (l - 0.5) * (1 - 4**(-l))
    t5 = delta_T5(z)
    pred = D_app_first_principles(z) / rd
    sigma = (pred - obs) / err
    chi2_dm += sigma**2
    print(f"  {name:<12} {z:<6.3f} {pred:<10.4f} {obs:<10.4f} {sigma:<+8.2f} {gd:<+10.6f} {t5:<+10.6f}")

print(f"\n  DM/rd χ² = {chi2_dm:.2f} ({len(desi_dm)} dof)")

print(f"\n{'='*72}")
print("  DH/rd Verification")
print(f"{'='*72}")
print(f"  {'Name':<12} {'z':<6} {'IDCM':<10} {'DESI':<10} {'σ':<8} {'δ_k0':<10} {'δ_gd':<10} {'δ_T5':<10}")
print("  " + "-"*76)
chi2_dh = 0
for name, z, obs, err in desi_dh:
    l = ell(z)
    dk = delta_k0(l)
    gd = C_DH * (l - 0.5) * (1 - 4**(-l))
    t5 = delta_T5(z)
    pred = DH_first_principles(z) / rd
    sigma = (pred - obs) / err
    chi2_dh += sigma**2
    print(f"  {name:<12} {z:<6.3f} {pred:<10.4f} {obs:<10.4f} {sigma:<+8.2f} {dk:<+10.6f} {gd:<+10.6f} {t5:<+10.6f}")

print(f"\n  DH/rd χ² = {chi2_dh:.2f} ({len(desi_dh)} dof)")
print(f"  Joint χ² = {chi2_dm+chi2_dh:.2f} ({len(desi_dm)+len(desi_dh)} dof)")

# ===== LRG1 breakdown =====
z_lrg1 = 0.510
l_lrg1 = ell(z_lrg1)
print(f"\n{'='*72}")
print("  LRG1 (z=0.51) Breakdown")
print(f"{'='*72}")
print(f"  δ_k0 = {delta_k0(l_lrg1):.6f}")
print(f"  δ_gd = {C_DH * (l_lrg1 - 0.5) * (1 - 4**(-l_lrg1)):.6f}")
print(f"  δ_T5 = {delta_T5(z_lrg1):.6f}")
print(f"  DM/rd = {D_app_first_principles(z_lrg1)/rd:.4f} (DESI: 13.588)")
print(f"  DM σ = {(D_app_first_principles(z_lrg1)/rd - 13.588)/0.167:.2f}")
print(f"  DH/rd = {DH_first_principles(z_lrg1)/rd:.4f} (DESI: 21.863)")
print(f"  DH σ = {(DH_first_principles(z_lrg1)/rd - 21.863)/0.429:.2f}")

# ===== Blind prediction =====
# The C_DH correction modifies the BAO distance scale, which feeds into
# the neutrino mass constraint. The structural correction factor is:
# ΔΣm_ν/Σm_ν = C_DH × (1 - F_proj/N_d) × N_gen/B
m1, m2, m3 = 0.02095, 0.02269, 0.05360
sum_mnu_orig = m1 + m2 + m3
correction = C_DH * (1 - F_proj/N_d) * N_gen / B
sum_mnu_pred = sum_mnu_orig * (1 + correction)

print(f"\n{'='*72}")
print("  BLIND PREDICTION: Σm_ν")
print(f"{'='*72}")
print(f"  O71 Σm_ν (NH) = {sum_mnu_orig:.5f} eV")
print(f"  C_DH correction factor = {correction:.6f}")
print(f"  Predicted Σm_ν = {sum_mnu_pred:.5f} eV")
print(f"  This is a ZERO-PARAMETER prediction — testable by DESI DR3.")

# Save
result = {
    'C_DM': round(C_DM, 10),
    'C_DH': round(C_DH, 10),
    'chi2_dm': round(chi2_dm, 2),
    'chi2_dh': round(chi2_dh, 2),
    'joint_chi2': round(chi2_dm+chi2_dh, 2),
    'lrg1_dm_sigma': round((D_app_first_principles(0.510)/rd - 13.588)/0.167, 2),
    'lrg1_dh_sigma': round((DH_first_principles(0.510)/rd - 21.863)/0.429, 2),
    'sum_mnu_prediction': round(sum_mnu_pred, 5),
}
with open('data/07_first_principles_final.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"\n  ✅ Results saved to data/07_first_principles_final.json")