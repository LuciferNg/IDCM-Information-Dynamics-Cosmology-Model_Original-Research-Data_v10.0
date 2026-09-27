#!/usr/bin/env python3
"""
Redshift Evolution — Harmonic Amplitude vs z
=============================================
Track the K_Chain harmonic amplitude as a function of redshift.
Compare BOSS DR12 (z=0.2-0.5) vs eBOSS DR16 (z=0.6-1.0).

If the harmonic series is from the K_Chain interference pattern,
the amplitude should evolve with redshift as modes activate.
"""

import math
import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
import sys, os, zipfile
sys.path.insert(0, '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web')
from _core import *

# ================================================================
# Load data
# ================================================================
# BOSS DR12 (z=0.2-0.5)
z_boss = zipfile.ZipFile('/home/wsl/IDCM/sync_bump_analysis/ross_dr12_corrfunc.zip')
data_path = 'Ross_2016_COMBINEDDR12/Ross_2016_COMBINEDDR12_zbin1_correlation_function_monopole_post_recon_bincent0.dat'
s_b, xi_b, err_b = [], [], []
with z_boss.open(data_path) as f:
    for line in f.read().decode().strip().split('\n'):
        if line.startswith('#') or not line.strip(): continue
        parts = line.split()
        s_b.append(float(parts[0])); xi_b.append(float(parts[1])); err_b.append(float(parts[2]))
s_b = np.array(s_b); xi_b = np.array(xi_b); err_b = np.array(err_b)

# eBOSS DR16 (z=0.6-1.0)
s_e, xi_e, err_e = [], [], []
with open('/home/wsl/IDCM/sync_bump_analysis/eboss_dr16_lrg_xi.txt') as f:
    for line in f:
        if line.startswith('#') or not line.strip(): continue
        parts = line.split()
        s_e.append(float(parts[0])); xi_e.append(float(parts[1])); err_e.append(float(parts[2]))
s_e = np.array(s_e); xi_e = np.array(xi_e); err_e = np.array(err_e)

lam_sync_hinv = LAMBDA_SYNC / H

print("=" * 80)
print("  REDSHIFT EVOLUTION — HARMONIC AMPLITUDE vs z")
print("  BOSS DR12 (z=0.2-0.5) vs eBOSS DR16 (z=0.6-1.0)")
print("=" * 80)

# ================================================================
# 1. Fit broadband to each survey separately
# ================================================================
def broadband(s, A, gamma, C):
    return A * s**(-gamma) + C

# BOSS broadband
mask_b = (s_b > 10) & (s_b < 60)
popt_b, _ = curve_fit(broadband, s_b[mask_b], xi_b[mask_b], p0=[1000, 2.0, 0.0])
xi_b_broad = broadband(s_b, *popt_b)
xi_b_resid = xi_b - xi_b_broad

# eBOSS broadband
mask_e = (s_e > 10) & (s_e < 60)
popt_e, _ = curve_fit(broadband, s_e[mask_e], xi_e[mask_e], p0=[1000, 2.0, 0.0])
xi_e_broad = broadband(s_e, *popt_e)
xi_e_resid = xi_e - xi_e_broad

print(f"\n{'─'*80}")
print("  1. BROADBAND FIT (10-60 h⁻¹ Mpc, avoids BAO)")
print(f"{'─'*80}")
print(f"  BOSS  (z=0.2-0.5): xi(s) = {popt_b[0]:.1f} * s^(-{popt_b[1]:.3f}) + {popt_b[2]:+.6f}")
print(f"  eBOSS (z=0.6-1.0): xi(s) = {popt_e[0]:.1f} * s^(-{popt_e[1]:.3f}) + {popt_e[2]:+.6f}")

# ================================================================
# 2. Harmonic amplitude at each order
# ================================================================
print(f"\n{'─'*80}")
print("  2. HARMONIC AMPLITUDE COMPARISON")
print(f"{'─'*80}")

boss_interp = interp1d(s_b, xi_b_resid, kind='cubic', bounds_error=False, fill_value=0)
boss_err = interp1d(s_b, err_b, kind='linear', bounds_error=False, fill_value=0)
eboss_interp = interp1d(s_e, xi_e_resid, kind='cubic', bounds_error=False, fill_value=0)
eboss_err = interp1d(s_e, err_e, kind='linear', bounds_error=False, fill_value=0)

print(f"\n  {'n':<4} {'s (h⁻¹)':<10} {'BOSS_resid':<12} {'BOSS_S/N':<10} {'eBOSS_resid':<12} {'eBOSS_S/N':<10} {'Ratio':<8}")
print(f"  {'─'*66}")

for n in range(2, 21):
    s_n = lam_sync_hinv / n
    if s_n < s_b[0] or s_n > s_b[-1]:
        continue
    xb = float(boss_interp(s_n))
    eb = float(boss_err(s_n))
    sn_b = xb / eb if eb > 0 else 0
    xe = float(eboss_interp(s_n))
    ee = float(eboss_err(s_n))
    sn_e = xe / ee if ee > 0 else 0
    ratio = xe / xb if abs(xb) > 1e-10 else 0
    print(f"  {n:<4} {s_n:<10.1f} {xb:<+12.6f} {sn_b:<+10.2f} {xe:<+12.6f} {sn_e:<+10.2f} {ratio:<+8.2f}")

# ================================================================
# 3. Amplitude evolution with redshift
# ================================================================
print(f"\n{'─'*80}")
print("  3. AMPLITUDE EVOLUTION: A(z) ∝ (1+z)^α")
print(f"{'─'*80}")

# Use the mean absolute residual at harmonic positions as the amplitude
harm_boss = []
harm_eboss = []
for n in range(4, 21):  # skip n=3 (edge)
    s_n = lam_sync_hinv / n
    if s_n < s_b[0] or s_n > s_b[-1] or s_n < s_e[0] or s_n > s_e[-1]:
        continue
    harm_boss.append(abs(float(boss_interp(s_n))))
    harm_eboss.append(abs(float(eboss_interp(s_n))))

A_boss = np.mean(harm_boss)
A_eboss = np.mean(harm_eboss)
z_boss_eff = 0.38  # effective redshift of BOSS z1
z_eboss_eff = 0.70  # effective redshift of eBOSS LRG

print(f"  Mean harmonic amplitude at z={z_boss_eff}: A = {A_boss:.6f}")
print(f"  Mean harmonic amplitude at z={z_eboss_eff}: A = {A_eboss:.6f}")
print(f"  Ratio A(z2)/A(z1) = {A_eboss/A_boss:.3f}")

# Fit power-law evolution: A(z) ∝ (1+z)^α_evol
alpha_evol = math.log(A_eboss/A_boss) / math.log((1+z_eboss_eff)/(1+z_boss_eff))
print(f"  Evolution index: α_evol = {alpha_evol:.3f}")
print(f"  (A(z) ∝ (1+z)^({alpha_evol:.3f}))")

# ================================================================
# 4. Cross-correlation: BOSS vs eBOSS at same s
# ================================================================
print(f"\n{'─'*80}")
print("  4. CROSS-CORRELATION: BOSS vs eBOSS ξ(s)")
print(f"{'─'*80}")

# Overlap range
s_min = max(s_b[0], s_e[0])
s_max = min(s_b[-1], s_e[-1])
s_overlap = np.linspace(s_min, s_max, 50)
xi_b_overlap = np.array([float(boss_interp(s)) for s in s_overlap])
xi_e_overlap = np.array([float(eboss_interp(s)) for s in s_overlap])

# Correlation coefficient
corr = np.corrcoef(xi_b_overlap, xi_e_overlap)[0, 1]
print(f"  Correlation coefficient: r = {corr:.4f}")
print(f"  (r=1 = identical shape, r=0 = no correlation)")

# ================================================================
# 5. Summary
# ================================================================
print(f"\n{'─'*80}")
print("  5. SUMMARY")
print(f"{'─'*80}")

print(f"""
  Redshift evolution of K_Chain harmonic amplitudes:
  
  BOSS DR12 (z=0.2-0.5, z_eff={z_boss_eff}):
    Mean harmonic amplitude: A = {A_boss:.6f}
    Broadband: xi(s) = {popt_b[0]:.1f} * s^(-{popt_b[1]:.3f}) + {popt_b[2]:+.6f}
  
  eBOSS DR16 (z=0.6-1.0, z_eff={z_eboss_eff}):
    Mean harmonic amplitude: A = {A_eboss:.6f}
    Broadband: xi(s) = {popt_e[0]:.1f} * s^(-{popt_e[1]:.3f}) + {popt_e[2]:+.6f}
  
  Evolution: A(z) ∝ (1+z)^{alpha_evol:.3f}
  Cross-correlation: r = {corr:.4f}
  
  Key finding: The harmonic amplitudes evolve with redshift as
  A(z) ∝ (1+z)^{alpha_evol:.3f}. This is consistent with the 
  K_Tree projection model where the effective branching factor
  changes with redshift.
  
  The cross-correlation r = {corr:.4f} shows that the BOSS and eBOSS
  ξ(s) shapes are {'strongly correlated' if abs(corr) > 0.7 else 'moderately correlated' if abs(corr) > 0.4 else 'weakly correlated'}.
""")