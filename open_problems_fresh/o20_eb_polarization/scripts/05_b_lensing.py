#!/usr/bin/env python3
"""
O20-E: B lensing 峰分析
========================
B lensing 峰: CAMB lensed BB 譜峰檢測 + IDCM 結構對比
"""
import numpy as np
import os
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

O9_DATA = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o9_high_ell_peaks/data"
O20_DIR = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o20_eb_polarization"
OUT_DIR = os.path.join(O20_DIR, "data")

import camb
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, tau=0.0544)
pars.InitPower.set_params(ns=0.9649, As=2.1e-9)
pars.set_for_lmax(2500)
results = camb.get_results(pars)
lensed = results.get_cmb_power_spectra(spectra=['total'], CMB_unit='muK')
lmax = 2500
ell = np.arange(lmax+1)

lens_bb = lensed['total'][:lmax+1, 2]  # lensed BB D_ℓ μK²

print("=" * 80)
print("O20-E: B lensing 峰分析")
print("=" * 80)

# BB 峰檢測
print(f"\n1. CAMB lensed BB 譜:")
print(f"   BB D_ℓ 範圍: [{lens_bb[50:2000].min():.2f}, {lens_bb[50:2000].max():.2f}] μK²")

for sigma in [3, 5, 8, 12]:
    smooth = gaussian_filter1d(lens_bb, sigma=sigma)
    peaks, _ = find_peaks(smooth[50:], distance=30, height=0.01)
    bb_peaks = peaks + 50
    print(f"   sigma={sigma}: {[f'{p:.0f}' for p in bb_peaks]}")

# 用 sigma=5 (最穩定)
smooth = gaussian_filter1d(lens_bb, sigma=5)
peaks, _ = find_peaks(smooth[50:], distance=30, height=0.01)
bb_peaks = peaks + 50
print(f"\n2. BB 峰 (sigma=5): {[f'{p:.0f}' for p in bb_peaks]}")

# BB 主峰
if len(bb_peaks) > 0:
    bb_main = bb_peaks[0]
    print(f"\n3. BB 主峰: ℓ ≈ {bb_main:.0f}")
    print(f"   IDCM ℓ_sync = 44, 2ℓ_sync = 88")
    print(f"   22ℓ_sync = 968, 23ℓ_sync = 1012")
    print(f"   BB 主峰 vs 22ℓ_sync: dev={(bb_main-968)/968*100:+.2f}%")
    print(f"   BB 主峰 vs 23ℓ_sync: dev={(bb_main-1012)/1012*100:+.2f}%")
    
    # BB mod 44
    print(f"\n4. BB 峰 mod 44:")
    for l in bb_peaks:
        n_int = l // 44
        n_frac = l % 44
        print(f"   ℓ={l:.0f} = 44×{n_int:.0f} + {n_frac:.0f}")

# BB 峰值位置 vs EE 結構
print(f"\n5. BB 峰 vs EE 結構公式:")
# EE n_int: 8, 15, 22, 29, 36, 43, 50
ee_n = np.array([8, 15, 22, 29, 36, 43, 50])
for l in bb_peaks:
    n = l // 44
    nearest_ee = ee_n[np.argmin(np.abs(ee_n - n))]
    print(f"   BB ℓ={l:.0f} (n_int={n}) → nearest EE n={nearest_ee}")

# BB 峰間距
if len(bb_peaks) > 1:
    bb_spacing = np.diff(bb_peaks)
    print(f"\n6. BB 峰間距: {bb_spacing}")
    print(f"   平均: {bb_spacing.mean():.1f}")
    print(f"   44 倍數: {[f'{s/44:.2f}' for s in bb_spacing]}")

# 保存
import json
results = {
    'bb_peaks': [float(l) for l in bb_peaks],
    'bb_mod_44': [{'ℓ': float(l), 'n_int': int(l//44), 'phase': int(l%44)} for l in bb_peaks],
}
with open(os.path.join(OUT_DIR, 'b_lensing_peaks.json'), 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n★ 結果已保存到: {os.path.join(OUT_DIR, 'b_lensing_peaks.json')}")