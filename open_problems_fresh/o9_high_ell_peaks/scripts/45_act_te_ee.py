#!/usr/bin/env python3
"""
O9-D2: ACT DR4 峰位偏移根源 + TE/EE 極化驗證
=================================================
ACT DR4 峰位 vs Planck: +13..+35 ℓ 系統偏移
問題:
1. 呢個偏移係標定定 bin 效應?
2. ACT DR4 TE/EE 極化峰位 vs IDCM 預言 (π/2 相移)?

ACT DR4 數據: cl_cmb_ap.dat 260 行 = 52 bins × 5 spectra
需要確認 spectra 順序 (TT, TE, EE, TB, EB?)
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
PYDIR = os.path.join(DATADIR, 'pyactlike', 'pyactlike', 'data')

print("="*80)
print("O9-D2: ACT DR4 峰位偏移 + 極化")
print("="*80)

binning = np.loadtxt(os.path.join(PYDIR, 'Binning.dat'))
l_center = binning[:,2]
cl = np.loadtxt(os.path.join(PYDIR, 'cl_cmb_ap.dat'))
n_bins = len(binning)

# 每個 spectra 嘅第一行數值 (判斷係咩 spectrum)
print("\n1. 5 個 spectra 特徵:")
for i in range(5):
    spec = cl[i*n_bins:(i+1)*n_bins]
    # C_ℓ 值範圍同正負
    vals = spec[:,1]
    print(f"   spectra {i}: 值範圍 [{vals.min():.3e}, {vals.max():.3e}], 正數比例 {np.mean(vals>0)*100:.0f}%")
    # 對比第一個 bin 嘅值
    print(f"      第一個 bin (ℓ={l_center[0]:.0f}): {vals[0]:.3e}")

# 分析: TT 應該最大, TE 中間, EE 較小
print("\n2. 判斷: TT (最大振幅), TE (中間), EE (較小)")
# 睇每 spectrum 峰值
for i in range(5):
    spec = cl[i*n_bins:(i+1)*n_bins]
    vals = spec[:,1]
    print(f"   spectra {i}: max C_ℓ = {vals.max():.3e}")

# 比較 Planck TT 已知值: ℓ=600 附近 C≈4.4e-2 (第一個 bin)
print("\n3. 已知: Planck TT C_ℓ(600) ≈ 4.4e-2")
print("   spectra 0 第一個 bin:", cl[0, 1])
