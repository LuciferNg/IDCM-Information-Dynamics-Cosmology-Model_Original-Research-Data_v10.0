#!/usr/bin/env python3
"""
O10 42: 質數峰假設驗證 — m4 (1013) 同 m6 (1337) 係咪真消失?
=============================================================
Planck 自動峰: 221, 527, 815, 1121, 1409 (5 個)
IDCM 峰位:     221, 527, 815, 1013, 1121, 1337, 1400 (7 個)

檢查 m4 (1013) 同 m6 (1337):
  - 係咪局部極大 (但被峰檢測 threshold 濾走)?
  - 定係真平滑 (冇峰)?
"""
import numpy as np, math, os
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

DATA = os.path.join(os.path.dirname(__file__), "..", "..", "o9_high_ell_peaks", "data", "planck_tt.txt")
data = np.loadtxt(DATA)
l, val, err = data[:,0], data[:,1], data[:,2]
Dl = val * l*(l+1)/(2*np.pi)

# 檢查 1013 附近 (m4)
print("m4 (1013) 附近 Planck binned:")
for i in range(len(l)):
    if 990 <= l[i] <= 1040:
        print(f"  ℓ={l[i]:.0f}: D={Dl[i]:.0f}")

print()
print("m6 (1337) 附近:")
for i in range(len(l)):
    if 1310 <= l[i] <= 1360:
        print(f"  ℓ={l[i]:.0f}: D={Dl[i]:.0f}")

print()
print("自動峰檢測 (低 threshold):")
s = gaussian_filter1d(Dl, sigma=1.5)
pk, props = find_peaks(s, distance=15)
for p in pk:
    if 900 <= l[p] <= 1500:
        print(f"  ℓ={l[p]:.0f}: D={Dl[p]:.0f}, prominence={props['prominences'][list(pk).index(p)] if 'prominences' in props else '?'}")
