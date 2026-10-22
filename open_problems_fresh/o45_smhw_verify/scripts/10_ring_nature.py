#!/usr/bin/env python3
"""
O45 — 閉合攻堅 5: 正環性質驗證 + 核心去卷積 (2026-09-12)
==========================================================
1. 三 map (SMICA/NILC/Commander) 冷斑徑向剖面 → 正環係咪真 CMB
2. 核心去卷積: smooth 後半幅 θ_1/2 → 內稟核心 σ_eff vs O42 3.68°
3. 正環幅度/位置 vs IDCM 數字關係 (保守掃描, 標明湊數風險)
"""
import os, json
import numpy as np
import healpy as hp

PROJECT = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
CACHE = os.path.join(PROJECT, 'open_problems_fresh/o5_catalog_compare/data/smooth_cache')
OUTDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

COLD = (209.0, -57.0)
SIGMA_SM = 4.17/2.355

maps = {
    'SMICA': os.path.join(CACHE, 'smica2_smooth4.17.fits'),
    'NILC': os.path.join(CACHE, 'nilc2_smooth4.17.fits'),
    'Commander': os.path.join(CACHE, 'commander_smooth4.17.fits'),
}

v0 = hp.ang2vec(COLD[0], COLD[1], lonlat=True)
bins = np.arange(0, 25.001, 0.5)

profiles = {}
print("三 map 冷斑徑向剖面 (4.17° smooth):")
print(f"  {'θ(°)':>6} ", end='')
for name in maps:
    print(f"{name:>10}", end='')
print()

for name, path in maps.items():
    m = hp.read_map(path)
    nside = hp.get_nside(m)
    v = hp.pix2vec(nside, np.arange(hp.nside2npix(nside)))
    ang = np.degrees(np.arccos(np.clip(v[0]*v0[0]+v[1]*v0[1]+v[2]*v0[2], -1, 1)))
    T = m * 1e6
    prof = []
    for i in range(len(bins)-1):
        mask = (ang >= bins[i]) & (ang < bins[i+1])
        if mask.sum() >= 5:
            prof.append(float(np.mean(T[mask])))
        else:
            prof.append(np.nan)
    profiles[name] = np.array(prof)

th_mid = (bins[:-1] + bins[1:]) / 2
for i in range(0, len(th_mid), 2):
    print(f"  {th_mid[i]:>6.2f} ", end='')
    for name in maps:
        v = profiles[name][i]
        print(f"{v:>10.2f}", end='')
    print()

# 正環對比
print("\n正環區域 (θ=10-20°) 三 map:")
for name in maps:
    mask = (th_mid >= 10) & (th_mid < 20)
    vals = profiles[name][mask]
    print(f"  {name:>9}: mean={np.nanmean(vals):>7.2f} μK, max={np.nanmax(vals):>7.2f} μK, "
          f"峰值θ={th_mid[mask][np.nanargmax(vals)]:.1f}°")

# 核心去卷積 (SMICA)
print("\n核心去卷積 (SMICA, 半幅 θ_1/2):")
sm = profiles['SMICA']
half_idx = np.where(sm < -67.1)[0]
if len(half_idx):
    theta_half = th_mid[half_idx].max()
    sigma_obs = theta_half / np.sqrt(2*np.log(2))
    sigma_eff = np.sqrt(max(sigma_obs**2 - SIGMA_SM**2, 0))
    print(f"  半幅 θ_1/2 = {theta_half:.2f}°")
    print(f"  σ_obs = {sigma_obs:.3f}°")
    print(f"  σ_eff = √({sigma_obs:.3f}² − {SIGMA_SM:.3f}²) = {sigma_eff:.3f}°")
    print(f"  vs O42 內稟 σ_int = {8.66/2.355:.3f}° (dev {abs(sigma_eff-8.66/2.355)/(8.66/2.355)*100:.1f}%)")
    print(f"  vs R8 σ = {SIGMA_SM:.3f}°")
    print(f"  核心高斯 FWHM = {2.355*sigma_eff:.2f}° vs O42 8.66°")

# 正環 IDCM 數字關係 (保守)
print("\n正環數字關係 (SMICA, 保守掃描 — 標明湊數風險):")
ring_mask = (th_mid >= 12) & (th_mid < 18)
ring_T = profiles['SMICA'][ring_mask]
ring_th = th_mid[ring_mask]
ring_peak = np.nanmax(ring_T)
ring_peak_th = ring_th[np.nanargmax(ring_T)]
A = 134.2
print(f"  正環峰值 = {ring_peak:.2f} μK @ θ={ring_peak_th:.2f}°")
print(f"  peak/|A| = {ring_peak/A:.4f}")
print(f"  峰值 vs A×2/L₄ (2/7): {A*2/7:.2f} (dev {abs(ring_peak-A*2/7)/(A*2/7)*100:.2f}%)")
print(f"  峰值 vs A×L₅/40 (11/40): {A*11/40:.2f} (dev {abs(ring_peak-A*11/40)/(A*11/40)*100:.2f}%)")
print(f"  峰值 vs A×3/11: {A*3/11:.2f} (dev {abs(ring_peak-A*3/11)/(A*3/11)*100:.2f}%)")
print(f"  峰值 vs A×φ⁻² (0.382): {A*0.382:.2f} (dev {abs(ring_peak-A*0.382)/(A*0.382)*100:.2f}%)")
print(f"  峰值 vs 背景水平 (60節點 mean|T|=36.18): dev {abs(ring_peak-36.18)/36.18*100:.1f}%")
print(f"  位置 vs 15.0° = L₆+L₄: dev {abs(ring_peak_th-15.0)/15.0*100:.2f}%")
print(f"  位置 vs 3.6×R8: {3.6*4.17:.2f} dev {abs(ring_peak_th-3.6*4.17)/(3.6*4.17)*100:.2f}%")
print(f"  位置 vs 8.66×φ: {8.66*1.618:.2f} dev {abs(ring_peak_th-8.66*1.618)/(8.66*1.618)*100:.2f}%")

# 儲存
out = {
    'product': 'O45 closure-5: ring nature + core deconvolution',
    'date': '2026-09-12',
    'radial_profiles': {name: {'theta': th_mid.tolist(), 'T': prof.tolist()}
                        for name, prof in profiles.items()},
    'ring_10_20deg': {name: {'mean': float(np.nanmean(profiles[name][(th_mid>=10)&(th_mid<20)])),
                             'max': float(np.nanmax(profiles[name][(th_mid>=10)&(th_mid<20)]))}
                      for name in maps},
    'core_deconvolution': {
        'theta_half': float(theta_half), 'sigma_obs': float(sigma_obs),
        'sigma_eff': float(sigma_eff), 'O42_sigma_int': float(8.66/2.355),
        'FWHM_eff': float(2.355*sigma_eff)},
    'ring_peak': {'T': float(ring_peak), 'theta': float(ring_peak_th),
                  'A_ratio': float(ring_peak/A)},
}
with open(os.path.join(OUTDIR, '07_ring_nature.json'), 'w') as f:
    json.dump(out, f, indent=2)
print(f"\n儲存: {OUTDIR}/07_ring_nature.json")