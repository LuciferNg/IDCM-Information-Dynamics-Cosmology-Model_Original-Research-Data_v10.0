#!/usr/bin/env python3
"""
O9-D10: ACT DR4 正確解析 v2 — deep+wide, TT/TE/EE
====================================================
X_data (260):
  [0:40]    = deep TT (40 bins)
  [40:85]   = deep TE (45 bins)
  [85:130]  = deep EE (45 bins)
  [130:170] = wide TT (40 bins)
  [170:215] = wide TE (45 bins)
  [215:260] = wide EE (45 bins)

bval 係 bin 中心? (like.py 讀 self.bval)
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
PYDIR = os.path.join(DATADIR, 'pyactlike', 'pyactlike', 'data')

print("="*80)
print("O9-D10: ACT DR4 正確解析 v2")
print("="*80)

# 讀原始數據
cl = np.loadtxt(os.path.join(PYDIR, 'cl_cmb_ap.dat'))
print(f"\n1. 數據形狀: {cl.shape}")
print(f"   第 1 欄 (bval): {cl[:,0][:5]} ... {cl[:,0][-5:]}")
print(f"   第 2 欄 (X_data): {cl[:,1][:5]} ...")
print(f"   第 3 欄 (X_sig): {cl[:,2][:5]} ...")

# bval 係 bin 中心
bval = cl[:, 0]
X = cl[:, 1]
Xerr = cl[:, 2]

# 拆 spectra
nbintt, nbinte, nbinee = 40, 45, 45
nbinw = 130

tt_d = X[0:nbintt]
te_d = X[nbintt:nbintt+nbinte]
ee_d = X[nbintt+nbinte:nbintt+nbinte+nbinee]
tt_w = X[nbinw:nbinw+nbintt]
te_w = X[nbinw+nbintt:nbinw+nbintt+nbinte]
ee_w = X[nbinw+nbintt+nbinte:nbinw+nbintt+nbinte+nbinee]

# bval 對應 (deep 前 130)
bval_d = bval[0:nbintt+nbinte+nbinee]
bval_tt = bval_d[0:nbintt]
bval_te = bval_d[nbintt:nbintt+nbinte]
bval_ee = bval_d[nbintt+nbinte:nbintt+nbinte+nbinee]

print(f"\n2. TT deep: {nbintt} bins, 範圍 {bval_tt[0]:.1f} - {bval_tt[-1]:.1f}")
print(f"   TE deep: {nbinte} bins, 範圍 {bval_te[0]:.1f} - {bval_te[-1]:.1f}")
print(f"   EE deep: {nbinee} bins, 範圍 {bval_ee[0]:.1f} - {bval_ee[-1]:.1f}")

# D_ℓ 轉換
D_tt = tt_d * bval_tt*(bval_tt+1)/(2*np.pi)
D_te = te_d * bval_te*(bval_te+1)/(2*np.pi)
D_ee = ee_d * bval_ee*(bval_ee+1)/(2*np.pi)

# TT 峰
print(f"\n3. TT deep 峰 (600-1600):")
for j in range(1, len(D_tt)-1):
    if 600 < bval_tt[j] < 1600 and D_tt[j] > D_tt[j-1] and D_tt[j] > D_tt[j+1] and D_tt[j] > 100:
        print(f"   ★ ℓ={bval_tt[j]:.1f}  D={D_tt[j]:.2f} ± {Xerr[j]*bval_tt[j]*(bval_tt[j]+1)/(2*np.pi):.2f}")
