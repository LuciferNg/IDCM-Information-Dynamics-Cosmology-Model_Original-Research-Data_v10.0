#!/usr/bin/env python3
"""
O10 24: 峰 5 異常 — 峰-谷結構分析
==================================
峰 5 @ 1121 三實驗一致偏高 (+21% vs 簡併預期)
檢查: 峰 5 係咪「吸咗」峰 4 能量 (峰谷唔夠深)?

Planck 數據:
  峰4 @ 1013 (A=0.1856), 谷 @ ? , 峰5 @ 1121 (A=0.2143)
  峰6 @ 1337 (A=0.1303), 谷 @ ? , 峰7 @ 1400 (A=0.1427)
"""
import numpy as np, math, os
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

phi = (1 + 5**0.5) / 2
eps = phi**-1/4

DATA = os.path.join(os.path.dirname(__file__), "..", "..", "o9_high_ell_peaks", "data", "planck_tt.txt")
data = np.loadtxt(DATA)
l, val, err = data[:,0], data[:,1], data[:,2]
Dl = val * l*(l+1)/(2*np.pi)
D1 = Dl[np.argmin(np.abs(l-221))]

# 峰-谷分析 900-1450
print("Planck ℓ 900-1450 (峰4/5/6/7 區域):")
for i in range(len(l)):
    if 900 <= l[i] <= 1450:
        marker = ""
        if l[i] in [1013, 1121, 1337, 1400]:
            marker = " ← IDCM 峰位"
        print(f"  ℓ={l[i]:.0f}: D={Dl[i]:.0f} ({Dl[i]/D1:.4f}){marker}")
