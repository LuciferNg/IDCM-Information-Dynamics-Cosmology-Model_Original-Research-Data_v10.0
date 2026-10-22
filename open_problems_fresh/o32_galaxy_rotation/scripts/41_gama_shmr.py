#!/usr/bin/env python3
"""
O32-41: GAMA SHMR — MagPhys + G3CFoFGroup cross-match
========================================================
MagPhys: mass_stellar_best_fit (星體質量)
G3CFoFGroup: VelDisp, MassProxy (暈質量)
IDCM 預言: f_peak = 1/L₇ = 1/29 ≈ 3.45%
"""
import numpy as np
import json
from astropy.io import fits

print("="*78)
print("GAMA SHMR — 星體 vs 暈質量關係")
print("="*78)

# 讀取 MagPhys (星體質量)
print("\n讀取 MagPhys...")
mp = fits.open("data/obs_data/MagPhys.fits")[1].data
mp_cataid = mp['CATAID']
mp_logm = np.log10(mp['mass_stellar_best_fit'])
print(f"MagPhys: {len(mp)} 星系")

# 讀取 G3CGal (星系目錄, 有 GroupID)
print("讀取 G3CGal...")
gal = fits.open("data/obs_data/G3CGal.fits")[1].data
gal_cataid = gal['CATAID']
gal_groupid = gal['GroupID']
gal_z = gal['Z']
print(f"G3CGal: {len(gal)} 星系")

# 讀取 G3CFoFGroup (群目錄, 有 VelDisp, MassProxy)
print("讀取 G3CFoFGroup...")
grp = fits.open("data/obs_data/G3CFoFGroup.fits")[1].data
grp_groupid = grp['GroupID']
grp_veldisp = grp['VelDisp']
grp_massproxy = grp['MassProxy']
grp_z = grp['IterCenZ']
print(f"G3CFoFGroup: {len(grp)} 群")

# Cross-match: CATAID → GroupID → VelDisp+MassProxy
print("\n--- Cross-match ---")
# 建立 CATAID → GroupID lookup
cataid_to_group = dict(zip(gal_cataid, gal_groupid))
# 建立 GroupID → VelDisp/MassProxy/Z lookup
group_to_props = dict(zip(grp_groupid, zip(grp_veldisp, grp_massproxy, grp_z)))

# 匹配
matched = 0
shmr_data = {'logM_star': [], 'logM_halo_vel': [], 'logM_halo_mass': [], 'z': []}
for i in range(len(mp)):
    cid = mp_cataid[i]
    if cid not in cataid_to_group:
        continue
    gid = cataid_to_group[cid]
    if gid <= 0 or gid not in group_to_props:
        continue
    vel, mass, z = group_to_props[gid]
    if vel <= 0 or vel > 2000 or mass <= 0:
        continue
    m_star = mp_logm[i]
    if not np.isfinite(m_star) or m_star < 7:
        continue
    # 用 MassProxy 做 halo 質量 (Msun 直接單位)
    m_halo = np.log10(mass)  # MassProxy 係 Msun
    shmr_data['logM_star'].append(m_star)
    shmr_data['logM_halo_vel'].append(np.log10(vel))
    shmr_data['logM_halo_mass'].append(m_halo)
    shmr_data['z'].append(z)
    matched += 1

print(f"匹配: {matched} 個星系-群對")

# SHMR bins
logM_halo_bins = np.arange(10.5, 15.5, 0.5)
logM_halo_c = (logM_halo_bins[:-1] + logM_halo_bins[1:]) / 2

print(f"\n{'logM_halo':>10} {'N':>6} {'<logM_star>':>12} {'ε_SF':>10} {'IDCM ε':>10} {'O/C':>10}")
for i in range(len(logM_halo_bins)-1):
    m_star_arr = np.array([shmr_data['logM_star'][j] for j in range(matched) 
                          if logM_halo_bins[i] <= shmr_data['logM_halo_mass'][j] < logM_halo_bins[i+1]])
    m_halo_arr = np.array([shmr_data['logM_halo_mass'][j] for j in range(matched) 
                          if logM_halo_bins[i] <= shmr_data['logM_halo_mass'][j] < logM_halo_bins[i+1]])
    if len(m_star_arr) < 5:
        continue
    mean_logM_star = np.mean(m_star_arr)
    mean_logM_halo = np.mean(m_halo_arr)
    eps_obs = 10**(mean_logM_star - mean_logM_halo)
    # IDCM 預言
    M_halo = 10**mean_logM_halo
    x = M_halo / (1.8924e12 / 3)  # M_peak = M_c/3
    eps_idcm = 2 * (1/29) / (x**(-5/3) + x**(1/0.618))
    ratio = eps_obs / eps_idcm if eps_idcm > 0 else 0
    print(f"{mean_logM_halo:>10.2f} {len(m_star_arr):>6d} {mean_logM_star:>12.2f} {eps_obs:>10.4f} {eps_idcm:>10.4f} {ratio:>10.2f}")

print("\n完成!")