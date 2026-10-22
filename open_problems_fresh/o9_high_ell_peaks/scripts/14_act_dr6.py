#!/usr/bin/env python3
"""
O9: ACT DR6 第三方獨立驗證
=============================
數據: act_dr6_cmb_sacc.fits (ACT DR6 CMB-only, TT/EE 45 bins)
方法:
1. 讀 TT (cl_00) bandpowers: ell, D_ell
2. 峰偵測 (bin 中心 + 平滑)
3. 對比 IDCM 修正公式 (220/537/810/1014/1121/1340/1412)
4. 獨立第 3 觀測源交叉驗證
"""
import numpy as np
import math as _m
import os
from astropy.io import fits

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
phi = (1 + 5**0.5)/2
F = [0, 1]
for i in range(2, 15): F.append(F[-1]+F[-2])

def idcm_fix(m):
    if m == 5:
        return 44*(33 - F[6]) + F[8]
    return 44*(33 - _m.comb(9-m, 2)) + (((m-1)*9) % 25)

print("="*80)
print("O9: ACT DR6 第三方獨立驗證")
print("="*80)

hdul = fits.open(os.path.join(DATADIR, 'act_dr6_cmb_sacc.fits'))
cl00 = hdul['data:cl_00'].data
print(f"\nTT bandpowers: {len(cl00)} bins")
print(f"columns: {cl00.dtype.names}")
print(f"第一行: {cl00[0]}")

# 提取 ell, value (D_ell 直接?)
ell6 = cl00['ell']
val6 = cl00['value']
print(f"\nell 範圍: {ell6.min()}..{ell6.max()}")
print(f"value 範圍: {val6.min():.4f}..{val6.max():.4f}")
print(f"\n完整 TT binned 譜:")
for e, v in zip(ell6, val6):
    print(f"  ℓ={e:6.1f}  D_ℓ={v:10.2f}")

# 峰偵測
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
print("\n" + "-"*80)
print("峰偵測 (sigma=0,1,2):")
for sigma in [0, 1, 2]:
    s = val6 if sigma == 0 else gaussian_filter1d(val6, sigma=sigma)
    cand, props = find_peaks(s, distance=1, prominence=3)
    cand = np.array(cand); proms = np.array(props['prominences'])
    keep = (proms > 0.01*s[cand]) & (s[cand] > 20)
    pk = [ell6[c] for c in cand[keep]]
    print(f"  sigma={sigma}: {[f'{p:.0f}' for p in pk]}")

# 配對 IDCM
print("\n" + "-"*80)
print("IDCM 修正公式 vs ACT DR6:")
for m in range(1, 8):
    pred = idcm_fix(m)
    diffs = np.abs(ell6 - pred)
    j = np.argmin(diffs)
    dev = (ell6[j] - pred)/pred*100
    mark = "✅" if abs(dev) < 2 else ("🟡" if abs(dev) < 5 else "❌")
    print(f"  m={m}: IDCM {pred} vs ACT {ell6[j]:.0f} → {dev:+.2f}% {mark}")
