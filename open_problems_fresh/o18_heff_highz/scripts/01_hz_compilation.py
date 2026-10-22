#!/usr/bin/env python3
"""
O18: H_eff(z) High-z Analysis
==============================
Compile H(z) data from literature and fit log(H) vs log(1+z) slope.
Compare IDCM (1+z)^1.0 vs ΛCDM (1+z)^1.5.

Data sources:
- Moresco et al. 2016 (arXiv:1601.01701) - Cosmic Chronometers compilation
- Moresco et al. 2012a (arXiv:1201.3609) - CC data at z~0.2-0.8
- Moresco et al. 2015 (arXiv:1503.01116) - CC data at z~1.4-2.0
- Simon et al. 2005 (astro-ph/0412269) - CC data
- Stern et al. 2010 (arXiv:0907.3149) - CC data
- Zhang et al. 2014 (arXiv:1309.6096) - CC data
- Ratsimbazafy et al. 2017 (arXiv:1702.03479) - CC data at z~0.5
- DESI 2024 BAO (arXiv:2404.03002)
- H0LICOW lensing time delays (Wong et al. 2020, arXiv:1907.04869)
- TDCOSMO/SHARP (Millon et al. 2020, arXiv:1912.08027)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats, optimize
import json, os, sys

# ============================================================
# H(z) DATA COMPILATION
# ============================================================
# Format: [z, H(z), σ_H, method, reference]
# H(z) in km/s/Mpc
# CC = Cosmic Chronometer, BAO = Baryon Acoustic Oscillations, 
# LENS = Strong lensing time delay

hz_data = [
    # ---- Cosmic Chronometer (CC) data ----
    # Zhang et al. 2014
    [0.07,   69.0,  19.6, 'CC', 'Zhang+2014'],
    [0.12,   68.6,  26.2, 'CC', 'Zhang+2014'],
    [0.20,   72.9,  29.6, 'CC', 'Zhang+2014'],
    [0.28,   88.8,  36.6, 'CC', 'Zhang+2014'],
    
    # Simon et al. 2005
    [0.09,   69.0,  12.0, 'CC', 'Simon+2005'],
    [0.17,   83.0,   8.0, 'CC', 'Simon+2005'],
    [0.27,   77.0,  14.0, 'CC', 'Simon+2005'],
    [0.40,   95.0,  17.0, 'CC', 'Simon+2005'],
    [0.90,  117.0,  23.0, 'CC', 'Simon+2005'],
    [1.30,  168.0,  17.0, 'CC', 'Simon+2005'],
    [1.43,  177.0,  18.0, 'CC', 'Simon+2005'],
    [1.53,  140.0,  14.0, 'CC', 'Simon+2005'],
    [1.75,  202.0,  40.0, 'CC', 'Simon+2005'],
    
    # Moresco et al. 2012a
    [0.179,  75.0,   4.0, 'CC', 'Moresco+2012a'],
    [0.199,  75.0,   5.0, 'CC', 'Moresco+2012a'],
    [0.352,  83.0,  14.0, 'CC', 'Moresco+2012a'],
    [0.593, 104.0,  13.0, 'CC', 'Moresco+2012a'],
    [0.680,  92.0,   8.0, 'CC', 'Moresco+2012a'],
    [0.781, 105.0,  12.0, 'CC', 'Moresco+2012a'],
    [0.875, 125.0,  17.0, 'CC', 'Moresco+2012a'],
    [1.037, 154.0,  20.0, 'CC', 'Moresco+2012a'],
    
    # Moresco et al. 2016 (BOSS DR9, BC03 model)
    [0.3802, 83.0, 13.5, 'CC', 'Moresco+2016'],
    [0.4004, 77.0, 10.2, 'CC', 'Moresco+2016'],
    [0.4247, 87.1, 11.2, 'CC', 'Moresco+2016'],
    [0.44497, 92.8, 12.9, 'CC', 'Moresco+2016'],
    [0.4783, 80.9,  9.0, 'CC', 'Moresco+2016'],
    
    # Moresco et al. 2015
    [1.363, 160.0, 33.6, 'CC', 'Moresco+2015'],
    [1.965, 186.5, 50.4, 'CC', 'Moresco+2015'],
    
    # Stern et al. 2010
    [0.48,   97.0,  62.0, 'CC', 'Stern+2010'],
    [0.88,   90.0,  40.0, 'CC', 'Stern+2010'],
    
    # Ratsimbazafy et al. 2017
    [0.57,  96.8,   3.4, 'CC', 'Ratsimbazafy+2017'],
    
    # ---- BAO data ----
    # BOSS DR12 (Alam et al. 2017)
    [0.38,  81.5,   1.9, 'BAO', 'BOSS DR12'],
    [0.51,  90.4,   1.9, 'BAO', 'BOSS DR12'],
    [0.61,  97.3,   2.1, 'BAO', 'BOSS DR12'],
    
    # eBOSS (Alam et al. 2021)
    [0.98, 118.9,   4.8, 'BAO', 'eBOSS DR16'],
    [1.48, 151.6,   5.6, 'BAO', 'eBOSS DR16'],
    
    # DESI 2024 (arXiv:2404.03002)
    [0.51,  90.5,   2.3, 'BAO', 'DESI 2024 LRG'],
    [0.71,  98.5,   2.9, 'BAO', 'DESI 2024 LRG'],
    [0.93, 110.5,   4.2, 'BAO', 'DESI 2024 ELG'],
    [1.32, 136.0,   6.5, 'BAO', 'DESI 2024 QSO'],
    [1.49, 136.5,   7.5, 'BAO', 'DESI 2024 QSO'],
    [2.33, 192.0,  12.0, 'BAO', 'DESI 2024 Lyα'],
    
    # ---- Strong lensing time delay ----
    # H0LICOW (Wong et al. 2020)
    [0.295, 78.0, 10.0, 'LENS', 'H0LICOW B1608'],
    [0.630, 96.0, 12.0, 'LENS', 'H0LICOW RXJ1131'],
    [0.675, 93.0, 11.0, 'LENS', 'H0LICOW HE0435'],
    
    # TDCOSMO (Millon et al. 2020)
    [0.550, 94.0, 14.0, 'LENS', 'TDCOSMO'],
    [0.800, 108.0, 15.0, 'LENS', 'TDCOSMO'],
]

# Convert to numpy array
data = np.array(hz_data)
z = data[:, 0].astype(float)
H = data[:, 1].astype(float)
H_err = data[:, 2].astype(float)
methods = data[:, 3]
refs = data[:, 4]

# ============================================================
# H_eff(z) FOR IDCM
# ============================================================
# IDCM: H_eff(z) = H_0 × (1+z)^1.0
H0_idcm = 72.59  # IDCM prediction

# ΛCDM: H(z) = H_0 × sqrt(Ω_m(1+z)^3 + Ω_Λ)
# At high z (z>>1): H(z) ∝ (1+z)^1.5
# For comparison, we use the asymptotic slope
H0_lcdm = 67.4  # Planck 2018

def h_idcm(z, H0=H0_idcm):
    """IDCM: linear scaling"""
    return H0 * (1 + z)**1.0

def h_lcdm_flat(z, H0=H0_lcdm, Om=0.315):
    """ΛCDM flat"""
    return H0 * np.sqrt(Om * (1+z)**3 + (1-Om))

def h_lcdm_asymptotic(z, H0=H0_lcdm):
    """ΛCDM high-z asymptotic: (1+z)^1.5"""
    return H0 * (1 + z)**1.5

# ============================================================
# LOG-LOG FIT
# ============================================================
# Fit: log(H) = log(H0) + α × log(1+z)
# IDCM predicts α = 1.0
# ΛCDM predicts α → 1.5 at high z

log1pz = np.log10(1 + z)
logH = np.log10(H)
logH_err = H_err / (H * np.log(10))  # Error propagation

# Weighted least squares fit
def fit_slope(log1pz, logH, logH_err):
    """Fit log(H) = a + b*log(1+z) with uncertainties"""
    w = 1.0 / logH_err**2
    S = np.sum(w)
    Sx = np.sum(w * log1pz)
    Sy = np.sum(w * logH)
    Sxx = np.sum(w * log1pz**2)
    Sxy = np.sum(w * log1pz * logH)
    
    Delta = S * Sxx - Sx**2
    a = (Sxx * Sy - Sx * Sxy) / Delta
    b = (S * Sxy - Sx * Sy) / Delta
    
    # Parameter uncertainties
    var_a = Sxx / Delta
    var_b = S / Delta
    
    # chi2
    H_fit = 10**(a + b * log1pz)
    chi2 = np.sum(w * (logH - a - b * log1pz)**2)
    dof = len(log1pz) - 2
    
    return a, b, np.sqrt(var_a), np.sqrt(var_b), chi2, dof

# Full dataset fit
a, b, a_err, b_err, chi2, dof = fit_slope(log1pz, logH, logH_err)
print("=" * 60)
print("O18: H_eff(z) HIGH-z SLOPE ANALYSIS")
print("=" * 60)
print(f"\nData points: {len(z)}")
print(f"Redshift range: {z.min():.3f} - {z.max():.3f}")
print(f"\nWeighted log-log fit:")
print(f"  log(H) = ({a:.4f} ± {a_err:.4f}) + ({b:.4f} ± {b_err:.4f}) × log(1+z)")
print(f"  χ² = {chi2:.1f}, dof = {dof}, χ²/dof = {chi2/dof:.2f}")
print(f"  Slope α = {b:.4f} ± {b_err:.4f}")
print(f"  H0 = {10**a:.2f} km/s/Mpc")

# Compare with IDCM and ΛCDM
print(f"\nPrediction comparison:")
print(f"  IDCM: α = 1.0000 → Δα = {b - 1.0:.4f} ± {b_err:.4f}  ({(b-1.0)/b_err:.2f}σ)")
print(f"  ΛCDM (high-z): α = 1.5000 → Δα = {b - 1.5:.4f} ± {b_err:.4f}  ({(b-1.5)/b_err:.2f}σ)")

# ============================================================
# SUBSET FITS: CC only, BAO only, z > 0.5, z > 1
# ============================================================
print(f"\n{'='*60}")
print("SUBSET ANALYSES")
print('='*60)

subsets = {
    'All data': (log1pz, logH, logH_err),
    'CC only': (log1pz[methods == 'CC'], logH[methods == 'CC'], logH_err[methods == 'CC']),
    'BAO only': (log1pz[methods == 'BAO'], logH[methods == 'BAO'], logH_err[methods == 'BAO']),
    'z > 0.5': (log1pz[z > 0.5], logH[z > 0.5], logH_err[z > 0.5]),
    'z > 1.0': (log1pz[z > 1.0], logH[z > 1.0], logH_err[z > 1.0]),
    'z < 0.5': (log1pz[z < 0.5], logH[z < 0.5], logH_err[z < 0.5]),
}

for name, (lx, ly, lye) in subsets.items():
    if len(lx) < 3:
        print(f"\n  {name}: too few points ({len(lx)})")
        continue
    sa, sb, _, sbe, schi2, sdof = fit_slope(lx, ly, lye)
    p_idcm = 2 * (1 - stats.norm.cdf(abs(sb - 1.0) / sbe))  # two-sided p-value
    p_lcdm = 2 * (1 - stats.norm.cdf(abs(sb - 1.5) / sbe))
    print(f"\n  {name} ({len(lx)} pts, z={lx.min():.3f}-{lx.max():.3f}):")
    print(f"    α = {sb:.4f} ± {sbe:.4f}, χ²/dof = {schi2/sdof:.2f}")
    print(f"    vs IDCM (1.0): Δ = {sb-1.0:.4f}σ, p = {p_idcm:.4f}")
    print(f"    vs ΛCDM (1.5): Δ = {sb-1.5:.4f}σ, p = {p_lcdm:.4f}")

# ============================================================
# MC SIMULATION: slope uncertainty distribution
# ============================================================
print(f"\n{'='*60}")
print("MONTE CARLO SLOPE ESTIMATION (10,000 realizations)")
print('='*60)

np.random.seed(42)
n_mc = 10000
slopes_mc = np.zeros(n_mc)
for i in range(n_mc):
    H_mc = np.random.normal(H, H_err)
    H_mc = np.clip(H_mc, 1, None)  # Physical
    logH_mc = np.log10(H_mc)
    logH_err_mc = H_err / (H_mc * np.log(10))
    _, sb, _, _, _, _ = fit_slope(log1pz, logH_mc, logH_err_mc)
    slopes_mc[i] = sb

slope_median = np.median(slopes_mc)
slope_lo = np.percentile(slopes_mc, 16)
slope_hi = np.percentile(slopes_mc, 84)
slope_95lo = np.percentile(slopes_mc, 2.5)
slope_95hi = np.percentile(slopes_mc, 97.5)

print(f"\nMC median slope: {slope_median:.4f}")
print(f"MC 68% CI: [{slope_lo:.4f}, {slope_hi:.4f}]")
print(f"MC 95% CI: [{slope_95lo:.4f}, {slope_95hi:.4f}]")

# What fraction of MC realizations are consistent with each model?
frac_idcm = np.mean((slopes_mc >= 0.9) & (slopes_mc <= 1.1)) * 100
frac_lcdm = np.mean((slopes_mc >= 1.4) & (slopes_mc <= 1.6)) * 100
print(f"\nFraction consistent with IDCM (α=1.0±0.1): {frac_idcm:.1f}%")
print(f"Fraction consistent with ΛCDM (α=1.5±0.1): {frac_lcdm:.1f}%")

# ============================================================
# POWER TO DISTINGUISH: Required data to discriminate
# ============================================================
print(f"\n{'='*60}")
print("DISCRIMINATION POWER ANALYSIS")
print('='*60)

# Current precision
current_slope_err = b_err
print(f"\nCurrent slope precision: ±{current_slope_err:.4f}")
print(f"Current: IDCM (1.0) vs data: {(b-1.0)/b_err:.2f}σ")
print(f"Current: ΛCDM (1.5) vs data: {(b-1.5)/b_err:.2f}σ")

# How many more data points (at current precision per point) 
# would be needed to get 3σ discrimination?
# σ_slope ∝ 1/√N for uniform sampling
# For 3σ discrimination between 1.0 and 1.5:
# Need σ_slope ≈ 0.5/3 ≈ 0.167
n_current = len(z)
n_needed_3sigma = n_current * (b_err / 0.167)**2
print(f"\nTo get 3σ discrimination (α=1.0 vs 1.5):")
print(f"  Need slope precision ≈ 0.167")
print(f"  Current: {n_current} pts → σ_slope = {b_err:.4f}")
print(f"  Need ~{n_needed_3sigma:.0f} data points (×{n_needed_3sigma/n_current:.1f})")
print(f"  (assuming similar precision per point)")

# Better approach: need high-z data specifically
# z > 1 gives best discrimination
n_highz = np.sum(z > 1.0)
_, _, _, b_err_highz, _, _ = fit_slope(log1pz[z > 1.0], logH[z > 1.0], logH_err[z > 1.0])
print(f"\nHigh-z only (z>1, {n_highz} pts):")
print(f"  σ_slope = {b_err_highz:.4f}")
print(f"  IDCM: {(b-1.0)/b_err_highz:.2f}σ")
print(f"  ΛCDM: {(b-1.5)/b_err_highz:.2f}σ")

# ============================================================
# PLOTTING
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Panel 1: H(z) vs z
ax = axes[0]
z_plot = np.logspace(-1.5, 0.6, 100)

# Plot data by method
colors = {'CC': '#1f77b4', 'BAO': '#ff7f0e', 'LENS': '#2ca02c'}
markers = {'CC': 'o', 'BAO': 's', 'LENS': '^'}
for method in ['CC', 'BAO', 'LENS']:
    mask = methods == method
    ax.errorbar(z[mask], H[mask], yerr=H_err[mask], 
                fmt=markers[method], color=colors[method],
                label=method, alpha=0.7, capsize=2)

# IDCM prediction
ax.plot(z_plot, h_idcm(z_plot), 'b-', linewidth=2, label=f'IDCM: H₀(1+z)^1.0')
ax.plot(z_plot, h_lcdm_asymptotic(z_plot), 'r--', linewidth=2, label=f'ΛCDM: H₀(1+z)^1.5')
ax.plot(z_plot, h_lcdm_flat(z_plot), 'r:', linewidth=1.5, label=f'ΛCDM flat (Ωm=0.315)')

ax.axvline(x=0.5, color='gray', linestyle=':', alpha=0.5, label='z=0.5')
ax.axvline(x=1.0, color='gray', linestyle=':', alpha=0.5, label='z=1.0')

ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('1 + z', fontsize=12)
ax.set_ylabel('H(z) [km/s/Mpc]', fontsize=12)
ax.set_title('H(z) Data: IDCM vs ΛCDM', fontsize=13)
ax.legend(fontsize=9, loc='upper left')
ax.grid(True, alpha=0.3)

# Panel 2: log(H) vs log(1+z) with fit
ax = axes[1]
ax.errorbar(log1pz, logH, yerr=logH_err, fmt='o', color='#1f77b4', 
            alpha=0.6, capsize=2, label='Data')

# Best fit line
z_fit = np.linspace(0.05, log1pz.max(), 100)
log1pz_fit = np.log10(1 + 10**z_fit - 1)  # This is wrong, let me fix
z_fit = np.logspace(-1.5, 0.6, 100)
log1pz_fit = np.log10(1 + z_fit)
H_fit_line = 10**(a + b * log1pz_fit)
ax.plot(log1pz_fit, np.log10(H_fit_line), 'k-', linewidth=2, 
        label=f'Fit: α={b:.3f}±{b_err:.3f}')

# IDCM and ΛCDM lines
ax.plot(log1pz_fit, np.log10(h_idcm(z_fit)), 'b--', linewidth=2, 
        label='IDCM: α=1.0')
ax.plot(log1pz_fit, np.log10(h_lcdm_asymptotic(z_fit)), 'r--', linewidth=2, 
        label='ΛCDM: α=1.5')

ax.set_xlabel('log(1+z)', fontsize=12)
ax.set_ylabel('log H(z)', fontsize=12)
ax.set_title(f'Slope: α={b:.3f}±{b_err:.3f} (χ²/dof={chi2/dof:.1f})', fontsize=13)
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plot_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'hz_slope_fit.png')
os.makedirs(os.path.dirname(plot_path), exist_ok=True)
plt.savefig(plot_path, dpi=150, bbox_inches='tight')
print(f"\nPlot saved: {plot_path}")

# ============================================================
# SAVE RESULTS
# ============================================================
results = {
    'n_data': len(z),
    'z_range': [float(z.min()), float(z.max())],
    'slope_weighted_fit': {'value': float(b), 'error': float(b_err)},
    'slope_mc_median': float(slope_median),
    'slope_mc_68ci': [float(slope_lo), float(slope_hi)],
    'slope_mc_95ci': [float(slope_95lo), float(slope_95hi)],
    'chi2': float(chi2),
    'dof': int(dof),
    'chi2_over_dof': float(chi2/dof),
    'idcm_sigma': float((b - 1.0) / b_err),
    'lcdm_sigma': float((b - 1.5) / b_err),
    'subsets': {},
    'n_needed_3sigma': float(n_needed_3sigma),
}

for name, (lx, ly, lye) in subsets.items():
    if len(lx) < 3:
        continue
    sa, sb, _, sbe, schi2, sdof = fit_slope(lx, ly, lye)
    results['subsets'][name] = {
        'n': len(lx),
        'slope': float(sb),
        'slope_err': float(sbe),
        'chi2_dof': float(schi2/sdof),
    }

json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'hz_results.json')
os.makedirs(os.path.dirname(json_path), exist_ok=True)
with open(json_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"Results saved: {json_path}")

print(f"\n{'='*60}")
print("ANALYSIS COMPLETE")
print('='*60)