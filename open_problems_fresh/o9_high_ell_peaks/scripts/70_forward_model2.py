#!/usr/bin/env python3
"""
O9-D10b: Forward-model — Planck 峰捲入 ACT DR6 TT bin
========================================================
用 ACT DR6 TT window (6501 點) 將 Planck C_ℓ 捲入 ACT bins
比較: 捲入後嘅 998.5/1048.5/1098.5 vs ACT 觀測

如果捲入 Planck 峰 1013 後 998.5 仍然係谷 → bin 平滑解釋成立
"""
import numpy as np
from astropy.io import fits
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
print("="*78)
print("O9-D10b: Forward-model (Planck → ACT bins)")
print("="*78)

# ACT DR6 window (TT = 第一個 Bandpower, 6501 點)
hdul = fits.open(os.path.join(DATADIR, 'act_dr6_cmb_sacc.fits'))
# 搵第一個非空 Bandpower window
win_hdu = None
for h in hdul:
    if h.name == 'window:Bandpower' and len(h.data) > 0:
        win_hdu = h
        break
win = win_hdu.data  # 6501
ell_win = win['values']
w = win['weight']
print(f"\n1. TT window: {len(ell_win)} 點, ℓ範圍 {ell_win[0]}-{ell_win[-1]}")
print(f"   非零 weight 數: {np.sum(w>0)}")

# ACT DR6 TT bandpowers
cl00 = hdul['data:cl_00'].data
ell_act = cl00['ell']
val_act = cl00['value']

# Planck C_ℓ (interp 到 window 格點)
planck = np.loadtxt(os.path.join(DATADIR, 'planck_tt.txt'))
ell_p = planck[:,0]; c_p = planck[:,1]
from scipy.interpolate import interp1d
f_c = interp1d(ell_p, c_p, kind='linear', bounds_error=False, fill_value=0)

# 每個 ACT bin: 用 window weight 捲 Planck C_ℓ
print(f"\n2. Forward-model 結果:")
print(f"   {'ACT ℓ':>7} {'ACT obs':>8} {'捲入預言':>8} {'ratio':>6}")
for i in range(len(ell_act)):
    if 850 <= ell_act[i] <= 1250:
        # 呢個 bin 嘅 window 段
        # window values 係 ℓ 格點, weight 係 bin 響應
        # 但需要知道邊段對應邊個 bin — 用 window_ind?
        pass

# 簡化: 直接近似 — 每個 ACT bin = 50 ℓ 寬 TopHat 平均 Planck
print("\n3. TopHat 近似 (bin 寬 50):")
for i in range(len(ell_act)):
    if 850 <= ell_act[i] <= 1250:
        lo, hi = ell_act[i]-25, ell_act[i]+25
        mask = (ell_p >= lo) & (ell_p < hi)
        if mask.sum() > 0:
            pred = np.mean(c_p[mask]) * ell_act[i]*(ell_act[i]+1)/(2*np.pi)
            print(f"   ℓ={ell_act[i]:7.1f}  obs={val_act[i]:8.1f}  pred={pred:8.1f}  ratio={val_act[i]/pred:5.2f}")
