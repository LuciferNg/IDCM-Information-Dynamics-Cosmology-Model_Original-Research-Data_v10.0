#!/usr/bin/env python3
"""
O9-D5: m=5 (1121) 真峰性 — 三數據源判別器
=============================================
Planck 判別: 1121 突出只有 0.7% → 疑似阻尼尾小波
但 SPT-3G 同 ACT DR4 點睇?

注意: 高ℓ 嘅 bin 寬大 + 阻尼背景, 突出度會低估
需要三數據一致先可判決
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
PYDIR = os.path.join(DATADIR, 'pyactlike', 'pyactlike', 'data')

print("="*78)
print("O9-D5: m=5 三數據源判別")
print("="*78)

# 1. SPT-3G TT 150x150 (之前 script 21 用嘅數據)
# 用 SPT 峰位: 524/824/1124/1424
# SPT bandpower 52 bins, bin 中心 ~500-3000, 峰間距 6 bins
# 1124 對應 bin ~16?

# 2. ACT DR4 deep TT
print("\n1. ACT DR4 deep TT (600-1600):")
cl = np.loadtxt(os.path.join(PYDIR, 'cl_cmb_ap.dat'))
bval = cl[:,0]; X = cl[:,1]; Xerr = cl[:,2]
bval_tt = bval[0:40]
D_tt = X[0:40] * bval_tt*(bval_tt+1)/(2*np.pi)
err_tt = Xerr[0:40] * bval_tt*(bval_tt+1)/(2*np.pi)

for j in range(1, len(D_tt)-1):
    if 600 < bval_tt[j] < 1600:
        mark = ""
        if D_tt[j] > D_tt[j-1] and D_tt[j] > D_tt[j+1]:
            # 突出度
            prom = (D_tt[j] - max(D_tt[j-1], D_tt[j+1])) / D_tt[j] * 100
            d2 = D_tt[j+1] - 2*D_tt[j] + D_tt[j-1]
            mark = f"  ★ 突出={prom:.1f}% d2={d2:.1f}"
        print(f"   ℓ={bval_tt[j]:6.1f}  D={D_tt[j]:7.1f} ± {err_tt[j]:6.1f}{mark}")

print("\n2. ACT DR4 峰判別:")
print("   800.5 (m=3): 突出度?")
print("   1100.5 (m=5): 突出度?")
print("   1400.5 (m=7): 突出度?")
# 詳細睇 1100 附近
for j in range(len(D_tt)):
    if 950 <= bval_tt[j] <= 1250:
        prom = 0
        if 0 < j < len(D_tt)-1 and D_tt[j] > D_tt[j-1] and D_tt[j] > D_tt[j+1]:
            prom = (D_tt[j] - max(D_tt[j-1], D_tt[j+1]))/D_tt[j]*100
        print(f"   ℓ={bval_tt[j]:6.1f}  D={D_tt[j]:7.1f}  突出={prom:5.1f}%")
