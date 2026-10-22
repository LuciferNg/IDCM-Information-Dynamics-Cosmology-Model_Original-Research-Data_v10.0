#!/usr/bin/env python3
"""
O9-C12: ACT DR6 高精度振幅驗證 (3/14 同 1/7 唔係湊數?)
=========================================================
用 ACT DR6 (bin 寬 50, 高精度) 驗證:
- A₅/A₁ = 3/14 = 0.2143
- A₇/A₁ = 1/7 = 0.1429
- 偶峰: (2/3)², (3/7)², (4/11)²

方法: ACT DR6 TT bandpowers 喺峰位附近嘅值
注意: ACT DR6 bin 中心同 Planck 唔同, 需要對齊
"""
import numpy as np
import os
from astropy.io import fits

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

print("="*80)
print("O9-C12: ACT DR6 振幅驗證")
print("="*80)

hdul = fits.open(os.path.join(DATADIR, 'act_dr6_cmb_sacc.fits'))
cl00 = hdul['data:cl_00'].data
ell6 = cl00['ell']; val6 = cl00['value']

# ACT DR6 峰位 (bin 中心)
print("\n1. ACT DR6 TT 全譜:")
for e, v in zip(ell6, val6):
    if 500 <= e <= 1500:
        print(f"   ℓ={e:7.1f}  D={v:8.2f}")

# ACT DR6 峰偵測 (bin 中心局部極大)
print("\n2. ACT DR6 峰偵測:")
peaks6 = []
for i in range(1, len(val6)-1):
    if val6[i] > val6[i-1] and val6[i] > val6[i+1] and val6[i] > 100:
        peaks6.append((ell6[i], val6[i]))
for l, v in peaks6:
    print(f"   ★ ℓ={l:.1f}  D={v:.2f}")

# 對比
print("\n3. ACT DR6 vs IDCM 峰位:")
idcm_peaks = {1: 220, 2: 537, 3: 810, 4: 1014, 5: 1121, 6: 1340, 7: 1412}
for m, pred in idcm_peaks.items():
    # 最近 ACT bin
    j = np.argmin(np.abs(ell6 - pred))
    dev = (ell6[j] - pred)/pred*100
    print(f"   m={m}: IDCM {pred} vs ACT {ell6[j]:.1f} (D={val6[j]:.2f}) dev={dev:+.1f}%")

# 振幅比 (ACT 峰 vs ACT 峰)
print("\n4. ACT DR6 振幅級聯 (用 ACT 自己嘅峰):")
if len(peaks6) >= 5:
    # 搵最接近 IDCM 峰位嘅 ACT bin 做振幅
    act_amp = {}
    for m, pred in idcm_peaks.items():
        j = np.argmin(np.abs(ell6 - pred))
        act_amp[m] = val6[j]
    A1 = act_amp[1]
    print(f"   A₁ (ACT ℓ≈{ell6[np.argmin(np.abs(ell6-220))]:.0f}) = {A1:.1f}")
    for m in [2, 3, 4, 5, 6, 7]:
        r = act_amp[m]/A1
        pred_r = {
            2: (2/3)**2, 3: (2/3)**2, 4: (3/7)**2,
            5: 3/14, 6: (4/11)**2, 7: 3/21,
        }[m]
        dev = abs(r - pred_r)/pred_r*100
        print(f"   A{m}/A₁ = {r:.4f} (ACT) vs {pred_r:.4f} (母函數) dev={dev:.1f}%")

# 統計: ACT 峰誤差
print("\n5. ACT 誤差 (cl_00 有 err 欄?):")
print(f"   欄位: {cl00.dtype.names}")
