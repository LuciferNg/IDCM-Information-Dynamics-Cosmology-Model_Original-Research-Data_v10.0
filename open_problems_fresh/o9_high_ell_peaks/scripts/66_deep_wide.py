#!/usr/bin/env python3
"""
O9-D7: ACT DR4 wide vs deep 峰位偏移 — 根源分析
==================================================
deep TT: 800.5/1100.5/1400.5
wide TT: 800.5/1150.5/1450.5

deep 同 wide 喺 m=3 一致 (800.5), 但 m=5/7 差 50 ℓ!
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
PYDIR = os.path.join(DATADIR, 'pyactlike', 'pyactlike', 'data')

print("="*78)
print("O9-D7: ACT DR4 deep vs wide")
print("="*78)

cl = np.loadtxt(os.path.join(PYDIR, 'cl_cmb_ap.dat'))
bval = cl[:,0]; X = cl[:,1]; Xerr = cl[:,2]
nbintt, nbinw = 40, 130

bval_tt = bval[0:nbintt]
tt_d = X[0:nbintt] * bval_tt*(bval_tt+1)/(2*np.pi)
err_d = Xerr[0:nbintt] * bval_tt*(bval_tt+1)/(2*np.pi)
bval_w = bval[nbinw:nbinw+nbintt]
tt_w = X[nbinw:nbinw+nbintt] * bval_w*(bval_w+1)/(2*np.pi)
err_w = Xerr[nbinw:nbinw+nbintt] * bval_w*(bval_w+1)/(2*np.pi)

print("\n1. deep vs wide TT 全譜:")
print(f"   {'ℓ':>7} {'deep D':>9} {'wide D':>9} {'diff':>7}")
for i in range(len(bval_tt)):
    if 600 < bval_tt[i] < 1600:
        diff = (tt_w[i]-tt_d[i])/tt_d[i]*100
        print(f"   {bval_tt[i]:7.1f} {tt_d[i]:9.1f} {tt_w[i]:9.1f} {diff:+6.1f}%")

print("\n2. 峰位比較:")
def peaks(b, D, lo=600, hi=1600):
    return [(b[j], D[j]) for j in range(1, len(D)-1)
            if lo < b[j] < hi and D[j] > D[j-1] and D[j] > D[j+1] and D[j] > 100]
pd = peaks(bval_tt, tt_d)
pw = peaks(bval_w, tt_w)
print(f"   deep: {[round(l) for l, v in pd]}")
print(f"   wide: {[round(l) for l, v in pw]}")

print("\n3. 偏移分析:")
print(f"   m=3: deep {pd[0][0]:.1f} vs wide {pw[0][0]:.1f} → Δ={pw[0][0]-pd[0][0]:+.0f}")
print(f"   m=5: deep {pd[1][0]:.1f} vs wide {pw[1][0]:.1f} → Δ={pw[1][0]-pd[1][0]:+.0f}")
print(f"   m=7: deep {pd[2][0]:.1f} vs wide {pw[2][0]:.1f} → Δ={pw[2][0]-pd[2][0]:+.0f}")

print("\n4. 可能原因:")
print("   a) deep (15mJy) vs wide (100mJy) 源剔除差異 → 標定/殘差")
print("   b) 兩者 window function 唔同 (coadd_bpwf 15mJy vs 100mJy)")
print("   c) 信噪比差異: deep S/N 高, 峰位更準")
print("   → deep 應該更可信 (S/N 高), 用 deep 做基準正確")
