#!/usr/bin/env python3
"""
O9-D3: m=4 (1013) 係真峰定 artifact — 三數據源交叉 + 形狀分析
=============================================================
核心問題: m=4 (1013) 弱峰 (D=1079.5) 係真峰定 binning artifact?

證據庫:
1. Planck binned bin-center: 1013 係局部極大 (D=1079.5)
2. SPT-3G: 峰位?
3. ACT DR4 deep: 500-600 區 (deep TT 最低 600)
4. IDCM 預言: 1014

方法: 睇相鄰 bin 形狀 + 幅度梯度, 判斷係咪真正嘅孤立峰
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
print("="*78)
print("O9-D3: m=4 (1013) 真峰分析")
print("="*78)

# Planck binned
planck = np.loadtxt(os.path.join(DATADIR, 'planck_tt.txt'))
ell_p = planck[:,0]; c_p = planck[:,1]; sig_p = planck[:,2]
d_p = c_p * ell_p*(ell_p+1)/(2*np.pi)

print("\n1. Planck binned m=4 區域 (880-1160):")
for i in range(len(ell_p)):
    if 880 <= ell_p[i] <= 1160:
        # 標記局部極大
        mark = ""
        if i>0 and i<len(ell_p)-1 and d_p[i]>d_p[i-1] and d_p[i]>d_p[i+1]:
            mark = "  ★LOCAL MAX"
        print(f"   ℓ={ell_p[i]:.0f}  D={d_p[i]:8.2f}{mark}")

print("\n2. 形態分析:")
# m=4 (1013) 同 m=5 (1121)
i4 = np.argmin(np.abs(ell_p-1013))
i5 = np.argmin(np.abs(ell_p-1121))
print(f"   m=4: ℓ={ell_p[i4]:.0f} D={d_p[i4]:.2f} (鄰近 {ell_p[i4-1]:.0f}={d_p[i4-1]:.2f}, {ell_p[i4+1]:.0f}={d_p[i4+1]:.2f})")
print(f"   m=5: ℓ={ell_p[i5]:.0f} D={d_p[i5]:.2f}")
# 深度 (峰到谷)
print(f"   1013 左邊谷: {d_p[i4-1]:.2f} → 1013 突出 {(d_p[i4]-d_p[i4-1])/d_p[i4]*100:.1f}%")
print(f"   1013 右邊谷: {d_p[i4+1]:.2f} → 1013 突出 {(d_p[i4]-d_p[i4+1])/d_p[i4]*100:.1f}%")

# 用第二導數判斷係峰定平台
print("\n3. 第二導數 (離散):")
def d2(i):
    if i<1 or i>len(d_p)-2: return 0
    return d_p[i+1] - 2*d_p[i] + d_p[i-1]
print(f"   1013 第二導數: {d2(i4):.2f} (負 = 峰)")
print(f"   1121 第二導數: {d2(i5):.2f} (負 = 峰)")

# 與鄰近第二導數比較
print("\n4. 邊界: 1013 鄰近 bin 有冇更深嘅峰?")
for i in range(i4-3, i4+4):
    if 0 < i < len(d_p)-1:
        print(f"   ℓ={ell_p[i]:.0f} D={d_p[i]:.2f} d2={d2(i):.2f}")
