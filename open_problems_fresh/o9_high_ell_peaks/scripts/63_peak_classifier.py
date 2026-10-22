#!/usr/bin/env python3
"""
O9-D4: 聲學峰 vs 阻尼尾平台 — 第二導數判別器
================================================
發現: 1013/1121 係真峰 (第二導數負), 但 1058/1085/1157 都係局部極大
判斷: 邊 D 係真聲學峰, 邊 D 係阻尼尾連鎖小波?

判別器: 第二導數幅度 + 峰突出度 (相對於左右谷)
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
planck = np.loadtxt(os.path.join(DATADIR, 'planck_tt.txt'))
ell_p = planck[:,0]; c_p = planck[:,1]
d_p = c_p * ell_p*(ell_p+1)/(2*np.pi)

print("="*78)
print("O9-D4: 聲學峰 vs 阻尼尾平台判別")
print("="*78)

# 所有局部極大 + 第二導數 + 突出度
print("\n局部極大 (900-1200) 分析:")
for i in range(1, len(d_p)-1):
    if 900 <= ell_p[i] <= 1200:
        if d_p[i] > d_p[i-1] and d_p[i] > d_p[i+1]:
            d2 = d_p[i+1] - 2*d_p[i] + d_p[i-1]
            # 突出度 = min(左右谷差)/pe
            lvalley = d_p[i-1]; rvalley = d_p[i+1]
            prominence = (d_p[i] - max(lvalley, rvalley)) / d_p[i] * 100
            print(f"   ℓ={ell_p[i]:.0f}  D={d_p[i]:7.1f}  d2={d2:8.1f}  突出={prominence:5.1f}%")

print("\n判別準則:")
print("   真峰: 突出 > 3% 且 d2 強負 (谷→峰→谷 明顯)")
print("   阻尼尾小波: 突出 < 3% 或 d2 弱")

print("\nIDCM 預言標記:")
print("   m=4 → 1014, m=5 → 1121")
