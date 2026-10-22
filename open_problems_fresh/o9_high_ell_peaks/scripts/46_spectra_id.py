#!/usr/bin/env python3
"""
O9-D3: ACT DR4 spectra 正確辨識 + TE/EE 峰位
=================================================
spectra 0: max 4.36e-2 → TT (匹配 Planck ℓ=600 C≈4.4e-2)
spectra 1: max 9.0e-4 → ?
spectra 2: max 3.84e-2 → ? (太大, 可能係 TE?)
spectra 3: max 4.4e-3 → ?
spectra 4: max 9.5e-4 → ?

檢查每個 spectra 嘅峰位置 (D_ℓ 空間) 去判斷:
- TT 峰: 220, 537, 815, 1013, 1121...
- TE 峰: 極化峰 (TT 峰之間, π/2 相移)
- EE 峰: 極化峰

標準: TE/EE 第一個峰喺 ℓ≈400 (極化第一個峰)
       TT 第一個峰喺 ℓ≈220 (但 ACT 最低 350)
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
PYDIR = os.path.join(DATADIR, 'pyactlike', 'pyactlike', 'data')

print("="*80)
print("O9-D3: spectra 辨識")
print("="*80)

binning = np.loadtxt(os.path.join(PYDIR, 'Binning.dat'))
l_low, l_high, l_center = binning[:,0], binning[:,1], binning[:,2]
cl = np.loadtxt(os.path.join(PYDIR, 'cl_cmb_ap.dat'))
n_bins = len(binning)

# 每個 spectra 轉 D_ℓ 後睇峰
for i in range(5):
    spec = cl[i*n_bins:(i+1)*n_bins]
    C = spec[:,1]
    D = C * l_center*(l_center+1)/(2*np.pi)
    # 搵峰 (局部極大)
    peaks = []
    for j in range(1, len(D)-1):
        if D[j] > D[j-1] and D[j] > D[j+1] and D[j] > 0:
            peaks.append((l_center[j], D[j]))
    # 前 4 個峰
    print(f"\nspectra {i}:")
    print(f"   峰: ", end="")
    for l, v in peaks[:6]:
        print(f"ℓ={l:.0f}({v:.1f}) ", end="")
    print()
    print(f"   D 範圍: [{D.min():.2f}, {D.max():.2f}]")
