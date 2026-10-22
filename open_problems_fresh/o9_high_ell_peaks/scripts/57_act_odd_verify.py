#!/usr/bin/env python3
"""
O9-D13: ACT DR4 正確數據 — 奇峰 3/14, 1/7 重驗證
====================================================
用正確 deep 數據重做振幅級聯驗證:
- 偶峰: A₂/A₁=(2/3)², A₄/A₁=(3/7)², A₆/A₁=(4/11)²
- 奇峰: A₃≈(2/3)², A₅=3/14, A₇=1/7

ACT DR4 deep TT: 40 bins, ℓ=600-4125
m=3 (810), m=5 (1121), m=7 (1412) — 只有 3 個奇峰!
冇偶峰 (m=2/4/6 喺 ℓ<600)
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
PYDIR = os.path.join(DATADIR, 'pyactlike', 'pyactlike', 'data')

print("="*80)
print("O9-D13: ACT DR4 奇峰重驗證")
print("="*80)

cl = np.loadtxt(os.path.join(PYDIR, 'cl_cmb_ap.dat'))
bval = cl[:, 0]; X = cl[:, 1]; Xerr = cl[:, 2]
nbintt = 40
bval_tt = bval[0:nbintt]
tt_d = X[0:nbintt]
D_tt = tt_d * bval_tt*(bval_tt+1)/(2*np.pi)
err_tt = Xerr[0:nbintt] * bval_tt*(bval_tt+1)/(2*np.pi)

# 峰位附近 bin
print("\n1. ACT DR4 deep TT 峰位附近:")
for l, v, e in zip(bval_tt, D_tt, err_tt):
    if 780 <= l <= 1420:
        print(f"   ℓ={l:7.1f}  D={v:8.2f} ± {e:6.2f}")

# 峰振幅 (用最近 bin)
print("\n2. 峰振幅:")
idcm_l = {3: 810, 5: 1121, 7: 1412}
amp = {}
for m, pred in idcm_l.items():
    j = np.argmin(np.abs(bval_tt - pred))
    amp[m] = (D_tt[j], err_tt[j], bval_tt[j])
    print(f"   m={m}: ℓ={bval_tt[j]:.1f} D={D_tt[j]:.2f} ± {err_tt[j]:.2f}")

# 奇峰比
print("\n3. 奇峰比 (ACT DR4):")
A3, e3, _ = amp[3]
A5, e5, _ = amp[5]
A7, e7, _ = amp[7]
r53 = A5/A3
r75 = A7/A5
re53 = np.sqrt((e5/A5)**2 + (e3/A3)**2)
re75 = np.sqrt((e7/A7)**2 + (e5/A5)**2)

print(f"   A₅/A₃ = {r53:.4f} ± {re53:.4f}")
print(f"   A₇/A₅ = {r75:.4f} ± {re75:.4f}")

# 母函數預言
print("\n4. 母函數預言 (用 A₃ 做基準):")
print(f"   A₃ ≈ (2/3)² 相對 A₁ → A₃ = 0.4444×A₁")
print(f"   A₅ = 3/14 → A₅/A₃ = (3/14)/(4/9) = 27/56 = 0.4821")
print(f"   A₇ = 1/7 → A₇/A₅ = (1/7)/(3/14) = 2/3 = 0.6667")
p53 = 27/56
p75 = 2/3
d53 = abs(r53-p53)/p53*100
d75 = abs(r75-p75)/p75*100
s53 = abs(r53-p53)/re53
s75 = abs(r75-p75)/re75
print(f"   A₅/A₃ = {r53:.4f} vs 預言 27/56 = {p53:.4f} → dev {d53:.1f}% ({s53:.1f}σ)")
print(f"   A₇/A₅ = {r75:.4f} vs 預言 2/3 = {p75:.4f} → dev {d75:.1f}% ({s75:.1f}σ)")
