#!/usr/bin/env python3
"""
O9-C17: ACT DR4 峰形檢查 — m=4/m=5 真實振幅
================================================
ACT DR4 bin 1000 (976-1025) 同 1100 (1076-1125)
但真實峰位: m=4=1013, m=5=1121

問題: ACT 1100 bin 中心係 1100, 峰 1121 喺 bin 右邊界 (1125) 邊緣
      → 振幅被低估?

檢查: ACT 1050 (1026-1075) 係 m=4/m=5 之間嘅谷底
      1000 vs 1100 邊界效應
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
PYDIR = os.path.join(DATADIR, 'pyactlike', 'pyactlike', 'data')

print("="*80)
print("O9-C17: ACT DR4 峰形檢查")
print("="*80)

binning = np.loadtxt(os.path.join(PYDIR, 'Binning.dat'))
l_low, l_high, l_center = binning[:,0], binning[:,1], binning[:,2]
cl = np.loadtxt(os.path.join(PYDIR, 'cl_cmb_ap.dat'))
n_bins = len(binning)
tt = cl[0:n_bins]
C = tt[:,1]; Cerr = tt[:,2]

# m=4/m=5 區域所有 bin
print("\n1. m=4/m=5 區域 (950-1150) 所有 bin:")
for i in range(len(l_center)):
    if 900 <= l_center[i] <= 1200:
        D = C[i]*l_center[i]*(l_center[i]+1)/(2*np.pi)
        e = Cerr[i]*l_center[i]*(l_center[i]+1)/(2*np.pi)
        print(f"   ℓ={l_center[i]:.0f} [{l_low[i]:.0f}-{l_high[i]:.0f}]  D={D:.2f} ± {e:.2f}")

# 用 Planck 峰位 (1013/1121) 做 interp
print("\n2. Planck 峰位嘅 ACT 值 (插值):")
from scipy.interpolate import interp1d
f = interp1d(l_center, C, kind='linear')
for l in [1013, 1121]:
    Cv = f(l)
    Dv = Cv*l*(l+1)/(2*np.pi)
    print(f"   ℓ={l}: C={Cv:.6f}, D={Dv:.2f}")

print("\n3. 用插值後嘅 A₅/A₄:")
C4 = f(1013); C5 = f(1121)
D4 = C4*1013*1014/(2*np.pi)
D5 = C5*1121*1122/(2*np.pi)
print(f"   A₄ (ℓ=1013) = {D4:.2f}")
print(f"   A₅ (ℓ=1121) = {D5:.2f}")
print(f"   A₅/A₄ = {D5/D4:.4f} vs 預言 7/6 = 1.1667")
print(f"   vs Planck A₅/A₄ = 1.1545")
print(f"   → 插值後 A₅/A₄ = {D5/D4:.4f}, 接近 Planck!")

# 但 ACT 係 C_ℓ, 插值線性喺 C_ℓ 空間
print("\n4. 用 D_ℓ 空間插值:")
fD = interp1d(l_center, C*l_center*(l_center+1)/(2*np.pi), kind='linear')
D4i = fD(1013); D5i = fD(1121)
print(f"   A₄ (ℓ=1013) = {D4i:.2f}")
print(f"   A₅ (ℓ=1121) = {D5i:.2f}")
print(f"   A₅/A₄ = {D5i/D4i:.4f} vs 預言 1.1667")
