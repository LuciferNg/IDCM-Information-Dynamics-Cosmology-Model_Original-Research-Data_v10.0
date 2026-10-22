#!/usr/bin/env python3
"""
O117/08: EXACT implementation of user's T̂⁵ formula
====================================================
User's formula: H(z) = H_base(z) × [1 + Re(det(T̂⁵)) × sin(6πz/88)]
Re(det(T̂⁵)) = det(T̂)⁵ = (-1)⁵ = -1

In DH form: DH(z) = DH_base(z) / [1 - sin(6πz/88)]

This is applied to the DM formula as a phase modulation of
the projection operator. The DM formula becomes:
D_app(ℓ) = R_H × (1-4^{-ℓ}) × (1 + 2φ⁻¹ℓ + δ_gd(ℓ)) / [1 - sin(6πz/88)]
"""
import math, json

N_d = 44; B = 4; N_gen = 3; F_proj = 17; n_cut = N_d - F_proj
phi = (1+math.sqrt(5))/2; phi_inv = phi - 1
R_H = 4129.94; rd = math.pi * R_H / 88 * 420/421

# Step 1: C_DM from K_Chain spectrum
gamma = [4*math.sin(math.pi*n/88)**2 for n in range(1, n_cut+1)]
v_g = [math.cos(math.pi*n/88) for n in range(1, n_cut+1)]
w = [1/v for v in v_g]
sum_w = sum(w[i]*gamma[i] for i in range(n_cut))
sum_even = sum(w[i]*gamma[i] for i in range(0, n_cut, 2))
sum_odd = sum(w[i]*gamma[i] for i in range(1, n_cut, 2))
C_delay = (sum_even - sum_odd) / sum_w
C_DM = -C_delay * 2 * phi_inv * math.sqrt(5)
C_DH = C_DM * B / N_gen

ell_0 = 0.5; sigma_phi = 0.5 * math.log(phi) / math.log(4)
def ell(z): return math.log(1+z, 4)
def delta_k0(el): return phi_inv**3 * math.exp(-(el-ell_0)**2/(2*sigma_phi**2))

# T̂⁵ phase coherence: δ_H(z) = Re(det(T̂⁵)) × sin(6πz/88) = -sin(6πz/88)
def T5_correction(z):
    return -math.sin(6*math.pi*z/88)

# DM: D_app with T̂⁵ correction in denominator  
# H(z) = H_base × [1 + δ_H], so DH = DH_base / [1 + δ_H]
# The 1/(1+z) in DH comes from the time dilation, so the T̂⁵ correction
# MODULATES the effective expansion rate
def D_app_T5(z):
    l = ell(z)
    gd = C_DH * (l - 0.5) * (1 - 4**(-l))
    base = R_H * (1 - 4**(-l)) * (1 + 2*phi_inv*l + gd)
    t5 = T5_correction(z)
    return base / (1 + t5)

def DH_T5(z):
    l = ell(z)
    dk = delta_k0(l)
    gd = C_DH * (l - 0.5) * (1 - 4**(-l))
    base = R_H * (1 + dk + gd) / (1 + z)
    t5 = T5_correction(z)
    return base / (1 + t5)

print("=" * 72)
print("  FIRST PRINCIPLES: T̂⁵ Phase Coherence (exact user formula)")
print("=" * 72)
print(f"  C_DM = {C_DM:.10f}  (K_Chain spectral operator)")
print(f"  C_DH = C_DM × B/N_gen = {C_DH:.10f}")
print(f"  det(T̂⁵) = (-1)⁵ = -1, Re(det(T̂⁵)) = -1")
print(f"  δ_H(z) = -sin(6πz/88)")
print(f"  D_app → D_app / [1 - sin(6πz/88)]")
print(f"  DH → DH / [1 - sin(6πz/88)]")
print()

# DM/rd
desi_dm = [('LRG1',0.510,13.588,0.167),('LRG2',0.706,17.351,0.177),
           ('LRG3+ELG',0.934,21.576,0.152),('ELG2',1.321,27.601,0.318),
           ('Lyα',2.330,38.989,0.531)]
print(f"  {'Name':<12} {'z':<6} {'IDCM':<10} {'DESI':<10} {'σ':<8} {'δ_H':<10}")
chi2_dm = 0
for n,z,o,e in desi_dm:
    p = D_app_T5(z)/rd; s=(p-o)/e; chi2_dm+=s**2; t5 = T5_correction(z)
    print(f"  {n:<12} {z:<6.3f} {p:<10.4f} {o:<10.4f} {s:<+8.2f} {t5:<+10.6f}")
print(f"  DM/rd χ² = {chi2_dm:.2f} ({len(desi_dm)} dof)")

# DH/rd
desi_dh = [('LRG1',0.510,21.863,0.429),('LRG2',0.706,19.455,0.334),
           ('LRG3+ELG',0.934,17.641,0.201),('ELG2',1.321,14.176,0.225),
           ('QSO',1.484,12.817,0.518),('Lyα',2.330,8.632,0.532)]
print(f"\n  {'Name':<12} {'z':<6} {'IDCM':<10} {'DESI':<10} {'σ':<8} {'δ_H':<10}")
chi2_dh = 0
for n,z,o,e in desi_dh:
    p = DH_T5(z)/rd; s=(p-o)/e; chi2_dh+=s**2; t5 = T5_correction(z)
    print(f"  {n:<12} {z:<6.3f} {p:<10.4f} {o:<10.4f} {s:<+8.2f} {t5:<+10.6f}")
print(f"  DH/rd χ² = {chi2_dh:.2f} ({len(desi_dh)} dof)")
print(f"  Joint χ² = {chi2_dm+chi2_dh:.2f} ({len(desi_dm)+len(desi_dh)} dof)")

# LRG1
z0 = 0.510
print(f"\n  LRG1 DM/rd: {D_app_T5(z0)/rd:.4f} vs DESI 13.588, σ = {(D_app_T5(z0)/rd-13.588)/0.167:.2f}")
print(f"  LRG1 DH/rd: {DH_T5(z0)/rd:.4f} vs DESI 21.863, σ = {(DH_T5(z0)/rd-21.863)/0.429:.2f}")

# Compare with/without T̂⁵
def D_app_no_T5(z):
    l = ell(z); gd = C_DH * (l-0.5)*(1-4**(-l))
    return R_H*(1-4**(-l))*(1+2*phi_inv*l+gd)

print(f"\n  Without T̂⁵: DM/rd = {D_app_no_T5(z0)/rd:.4f}")
print(f"  With T̂⁵:    DM/rd = {D_app_T5(z0)/rd:.4f}")
print(f"  DESI:        DM/rd = 13.588")
print(f"  Improvement: {abs(D_app_no_T5(z0)/rd-13.588)-abs(D_app_T5(z0)/rd-13.588):.4f}")

r = {'C_DM':round(C_DM,10),'C_DH':round(C_DH,10),'chi2_dm':round(chi2_dm,2),
     'chi2_dh':round(chi2_dh,2),'joint_chi2':round(chi2_dm+chi2_dh,2)}
with open('data/08_T5_exact.json','w') as f: json.dump(r,f,indent=2)
print(f"\n  ✅ Results saved to data/08_T5_exact.json")