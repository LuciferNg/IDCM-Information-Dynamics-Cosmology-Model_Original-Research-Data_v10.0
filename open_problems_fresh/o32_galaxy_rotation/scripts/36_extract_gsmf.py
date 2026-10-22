#!/usr/bin/env python3
"""
O32-36: 從 GAMA StellarMasses FITS 提取質量函數
===================================================
方法: 1/V_max, z < 0.1, nQ > 2, logM_bins [7.5, 12.0]
"""
import numpy as np
import json
import math
from astropy.io import fits
from astropy.cosmology import FlatLambdaCDM

# GAMA DR3 星體質量目錄
FITS_PATH = "data/obs_data/StellarMasses.fits"
OUT_PATH = "data/obs_data/gama_gsmf_binned.csv"

# 宇宙學 (H0=70, Ωm=0.3, GAMA 用)
cosmo = FlatLambdaCDM(H0=70, Om0=0.3)

# GAMA 面積 (180 deg²)
AREA_DEG2 = 180.0
AREA_SR = AREA_DEG2 * (np.pi/180)**2  # 球面度
AREA_FRAC = AREA_SR / (4*np.pi)  # 全天空比例

print("="*78)
print("GAMA StellarMasses 質量函數提取")
print("="*78)

# 讀取 FITS
print(f"\n讀取: {FITS_PATH}")
hdul = fits.open(FITS_PATH)
data = hdul[1].data
print(f"總行數: {len(data)}")

# 篩選條件
print("\n--- 篩選 ---")
nQ = data['nQ']
z = data['Z']
logm = data['logmstar']
zmax = data['zmax_19p8']

# nQ > 2 (good quality)
mask_nq = nQ > 2
print(f"nQ > 2: {mask_nq.sum()}")

# z < 0.1 (local universe)
mask_z = (z < 0.1) & (z > 0.001)
print(f"z < 0.1: {mask_z.sum()}")

# logmstar valid
mask_m = np.isfinite(logm)
print(f"logm valid: {mask_m.sum()}")

# zmax valid
mask_zm = np.isfinite(zmax) & (zmax > 0.001)
print(f"zmax valid: {mask_zm.sum()}")

# Combined
mask = mask_nq & mask_z & mask_m & mask_zm
print(f"最終篩選: {mask.sum()} 個星系")

z_f = z[mask]
logm_f = logm[mask]
zmax_f = zmax[mask]

# 質量函數 binning
logM_bins = np.arange(7.5, 12.25, 0.25)
logM_centers = (logM_bins[:-1] + logM_bins[1:]) / 2

print(f"\n--- 質量函數計算 (1/V_max) ---")
print(f"Bins: {len(logM_bins)-1} 個 (logM = {logM_bins[0]:.1f}-{logM_bins[-1]:.1f})")

results = []
c = 299792.458  # km/s

for i in range(len(logM_bins)-1):
    m_low = logM_bins[i]
    m_high = logM_bins[i+1]
    m_center = logM_centers[i]
    
    # 呢個 bin 嘅星系
    in_bin = (logm_f >= m_low) & (logm_f < m_high)
    n_gal = in_bin.sum()
    
    if n_gal == 0:
        results.append({'logM_center': m_center, 'N': 0, 'phi': 0, 'phi_err': 0})
        continue
    
    # 1/V_max 方法
    V_max_sum = 0.0
    for j in np.where(in_bin)[0]:
        z_gal = z_f[j]
        zm = zmax_f[j]
        # 有效 z_max = min(z_max_survey, z_max_galaxy)
        z_eff = min(zm, 0.1)
        if z_eff <= z_gal:
            continue
        # 同移距離
        d_min = cosmo.comoving_distance(z_gal).value
        d_max = cosmo.comoving_distance(z_eff).value
        # 同移體積 (Mpc³)
        V = (4*np.pi/3) * (d_max**3 - d_min**3) * AREA_FRAC
        V_max_sum += 1.0 / V
    
    # 質量函數 φ = Σ(1/V_max) / ΔlogM
    phi = V_max_sum / 0.25
    phi_err = phi / math.sqrt(n_gal) if n_gal > 0 else 0
    
    results.append({
        'logM_center': float(m_center),
        'N': int(n_gal),
        'phi': float(phi),
        'phi_err': float(phi_err)
    })
    print(f"  logM={m_center:.2f}: N={n_gal:>5d}, φ={phi:.4e} ± {phi_err:.4e}")

# 保存
import csv
with open(OUT_PATH, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['logM_center', 'N', 'phi', 'phi_err'])
    w.writeheader()
    w.writerows(results)
print(f"\n已存: {OUT_PATH}")

# 對比 GAMA 雙 Schechter
print("\n--- 對比 GAMA 雙 Schechter (Wright+2017) ---")
M_STAR = 10**10.78
PHI1, ALPHA1 = 2.93e-3, -0.62
PHI2, ALPHA2 = 0.63e-3, -1.50

def gama_schechter(M):
    s1 = PHI1 * (M/M_STAR)**ALPHA1 * np.exp(-M/M_STAR)
    s2 = PHI2 * (M/M_STAR)**ALPHA2 * np.exp(-M/M_STAR)
    return s1 + s2

chi2 = 0
count = 0
print(f"{'logM':>6} {'IDCM_ext':>12} {'GAMA_fit':>12} {'χ²':>10}")
for r in results:
    if r['N'] < 5: 
        continue
    M = 10**r['logM_center']
    phi_gama = gama_schechter(M)
    err = r['phi_err']
    chi2_i = (r['phi'] - phi_gama)**2 / err**2 if err > 0 else 0
    chi2 += chi2_i
    count += 1
    print(f"{r['logM_center']:>6.2f} {r['phi']:>12.4e} {phi_gama:>12.4e} {chi2_i:>10.2f}")

print(f"\nχ² = {chi2:.1f}, dof = {count}, χ²/dof = {chi2/count:.2f}")

hdul.close()
print("\n完成!")