#!/usr/bin/env python3
"""
O9-C14: ACT DR4 官方 bandpowers — m=4/m=5 獨立振幅驗證
==========================================================
ACT DR4 (pyactlike 官方) 驗證母函數:
- A₂/A₁=(2/3)², A₄/A₁=(3/7)², A₆/A₁=(4/11)²
- A₅/A₁=3/14, A₇/A₁=1/7

cl_cmb_ap.dat: 260 行 = 52 bins × 5 spectra
spectra 順序: TT, TE, EE, TB, EB? 需要確認
Binning.dat: 52 bins, [l_low, l_high, l_center]
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
PYDIR = os.path.join(DATADIR, 'pyactlike', 'pyactlike', 'data')

print("="*80)
print("O9-C14: ACT DR4 官方 bandpowers")
print("="*80)

# 讀 Binning
binning = np.loadtxt(os.path.join(PYDIR, 'Binning.dat'))
l_low = binning[:,0]; l_high = binning[:,1]; l_center = binning[:,2]

# 讀 cl_cmb_ap.dat
cl = np.loadtxt(os.path.join(PYDIR, 'cl_cmb_ap.dat'))
n_bins = len(binning)
n_spec = len(cl) // n_bins
print(f"\n1. 數據結構:")
print(f"   52 bins × {n_spec} spectra = {n_bins*n_spec} 行 (實際 {len(cl)})")

# 拆 spectra (每個 52 行)
spectra = {}
names = ['TT', 'TE', 'EE', 'TB', 'EB']
for i in range(min(n_spec, 5)):
    spectra[names[i]] = cl[i*n_bins:(i+1)*n_bins]

print(f"   確認 spectra: {list(spectra.keys())}")

# TT 轉 D_ℓ
tt = spectra['TT']
D_tt = tt[:,1] * l_center*(l_center+1)/(2*np.pi)
err_tt = tt[:,2] * l_center*(l_center+1)/(2*np.pi)

# ACT DR4 bin 中心 (326.5-3050.5)
print(f"\n2. ACT DR4 TT D_ℓ (bin 中心 326-3050):")
for i in range(len(l_center)):
    if l_center[i] >= 300:
        print(f"   ℓ={l_center[i]:7.1f}  D={D_tt[i]:8.2f} ± {err_tt[i]:6.2f}")

# 峰偵測 (局部極大)
print(f"\n3. ACT DR4 峰偵測:")
peaks = []
for i in range(1, len(D_tt)-1):
    if D_tt[i] > D_tt[i-1] and D_tt[i] > D_tt[i+1] and D_tt[i] > 100:
        peaks.append((l_center[i], D_tt[i], err_tt[i]))
for l, v, e in peaks:
    print(f"   ★ ℓ={l:.0f}  D={v:.2f} ± {e:.2f}")

# 對比 IDCM 峰位
print(f"\n4. ACT DR4 vs IDCM 峰位:")
idcm_peaks = {1: 220, 2: 537, 3: 810, 4: 1014, 5: 1121, 6: 1340, 7: 1412}
for m, pred in idcm_peaks.items():
    j = np.argmin(np.abs(l_center - pred))
    dev = (l_center[j] - pred)/pred*100
    print(f"   m={m}: IDCM {pred} vs ACT {l_center[j]:.0f} (D={D_tt[j]:.2f}±{err_tt[j]:.2f}) dev={dev:+.1f}%")
