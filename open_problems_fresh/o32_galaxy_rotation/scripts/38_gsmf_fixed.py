#!/usr/bin/env python3
"""
O32-38: 修正 GAMA 質量函數 — 直接用星體質量分佈對比
=======================================================
1/V_max 實作複雜, 改用原始質量分佈 + 形狀對比
"""
import numpy as np
import json, csv, math
from astropy.io import fits
from astropy.cosmology import FlatLambdaCDM

cosmo = FlatLambdaCDM(H0=70, Om0=0.3)
AREA_FRAC = 180.0 / 41253.0  # GAMA 面積 / 全天空

print("="*78)
print("GAMA 星體質量分佈 — IDCM 形狀對比")
print("="*78)

# 讀取 FITS
hdul = fits.open("data/obs_data/StellarMasses.fits")
data = hdul[1].data
nQ, z, logm = data['nQ'], data['Z'], data['logmstar']
zmax = data['zmax_19p8']

# 篩選
mask = (nQ > 2) & (z > 0.001) & (z < 0.1) & np.isfinite(logm) & np.isfinite(zmax) & (zmax > 0.001)
z_f, logm_f, zmax_f = z[mask], logm[mask], zmax[mask]
print(f"篩選後: {mask.sum()} 個星系")

# 1/V_max 修正
valid = []
for i in range(len(z_f)):
    z_eff = min(zmax_f[i], 0.1)
    if z_eff <= z_f[i]:
        continue
    d_min = cosmo.comoving_distance(z_f[i]).value
    d_max = cosmo.comoving_distance(z_eff).value
    V = (4*np.pi/3) * (d_max**3 - d_min**3) * AREA_FRAC
    if V > 0:
        valid.append({'logM': logm_f[i], 'w': 1.0/V, 'z': z_f[i], 'zmax': zmax_f[i]})

print(f"有效 V_max: {len(valid)} 個星系")

# 檢查 zmax 分佈
zmax_all = np.array([v['zmax'] for v in valid])
print(f"zmax 範圍: {zmax_all.min():.3f}-{zmax_all.max():.3f}, 中位數: {np.median(zmax_all):.3f}")

# 檢查 zmax 高於 0.1 嘅比例
print(f"zmax > 0.1: {(zmax_all > 0.1).sum()}/{len(zmax_all)} ({(zmax_all > 0.1).mean()*100:.1f}%)")

# 高質量 bin 嘅 zmax
high_z = np.array([v['zmax'] for v in valid if v['logM'] > 10.5])
if len(high_z) > 0:
    print(f"高質量端 (logM>10.5) zmax: 中位數 {np.median(high_z):.3f}")

# ===== 質量函數 binning =====
logM_bins = np.arange(7.5, 12.25, 0.25)
logM_c = (logM_bins[:-1] + logM_bins[1:]) / 2

results = []
for i in range(len(logM_bins)-1):
    in_bin = [(v['logM'] >= logM_bins[i]) and (v['logM'] < logM_bins[i+1]) for v in valid]
    weights = [v['w'] for j, v in enumerate(valid) if in_bin[j]]
    n = sum(in_bin)
    if n == 0:
        continue
    phi = sum(weights) / 0.25
    phi_err = phi / math.sqrt(n) if n > 0 else 0
    results.append({'logM': logM_c[i], 'N': n, 'phi': phi, 'phi_err': phi_err, 'w': weights})

# 輸出
print(f"\n{'logM':>6} {'N':>6} {'φ':>12} {'err':>12}")
for r in results:
    if r['N'] > 0:
        print(f"{r['logM']:>6.2f} {r['N']:>6d} {r['phi']:>12.4e} {r['phi_err']:>12.4e}")

# 保存
with open('data/obs_data/gama_gsmf_v2.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['logM', 'N', 'phi', 'phi_err'])
    w.writeheader()
    for r in results:
        w.writerow({'logM': r['logM'], 'N': r['N'], 'phi': r['phi'], 'phi_err': r['phi_err']})

# ===== IDCM 形狀對比 =====
MC = 1.8924e12
ALPHA = 4/3
M_STAR_GAMA = 10**10.78

# 歸一化到 logM=10.0
norm_r = min(results, key=lambda r: abs(r['logM'] - 10.0))
norm_phi = norm_r['phi']
M_norm = 10**norm_r['logM']

def idcm_shape(M):
    return M**(-ALPHA) * np.exp(-M/MC)

def gama_fit(M):
    s1 = 2.93e-3 * (M/M_STAR_GAMA)**(-0.62) * np.exp(-M/M_STAR_GAMA)
    s2 = 0.63e-3 * (M/M_STAR_GAMA)**(-1.50) * np.exp(-M/M_STAR_GAMA)
    return s1 + s2

scale = norm_phi / gama_fit(M_norm)
idcm_scale = norm_phi / idcm_shape(M_norm)

print(f"\n--- IDCM 形狀對比 (歸一化 @ logM={norm_r['logM']:.1f}) ---")
print(f"{'logM':>6} {'GAMA φ':>12} {'GAMA fit':>12} {'IDCM':>12} {'O/C':>8}")
good = []
for r in results:
    if r['N'] < 5:
        continue
    M = 10**r['logM']
    phi_g = gama_fit(M) * scale
    phi_i = idcm_shape(M) * idcm_scale
    ratio = r['phi'] / phi_i if phi_i > 0 else 0
    good.append({'logM': r['logM'], 'phi_obs': r['phi'], 'phi_idcm': phi_i, 'ratio': ratio})
    print(f"{r['logM']:>6.2f} {r['phi']:>12.4e} {phi_g:>12.4e} {phi_i:>12.4e} {ratio:>8.2f}")

# 斜率 (低質量端)
low = [g for g in good if 8.0 <= g['logM'] <= 9.5]
if len(low) >= 3:
    logM_arr = np.array([g['logM'] for g in low])
    logPhi_arr = np.log10(np.array([g['phi_obs'] for g in low]))
    slope = np.polyfit(logM_arr, logPhi_arr, 1)[0]
    print(f"\n低質量端 slope (GAMA 數據): {slope:.3f}")
    print(f"IDCM 理論 slope: {-ALPHA:.3f}")

# χ² 形狀
chi2 = 0
count = 0
for r in results:
    if r['N'] < 5:
        continue
    M = 10**r['logM']
    phi_i = idcm_shape(M) * idcm_scale
    err = max(r['phi_err'], 0.05 * r['phi'])
    chi2 += (r['phi'] - phi_i)**2 / err**2
    count += 1
print(f"\nIDCM 形狀 χ²: χ² = {chi2:.1f}, dof = {count}, χ²/dof = {chi2/count:.2f}")

hdul.close()
print("\n完成!")