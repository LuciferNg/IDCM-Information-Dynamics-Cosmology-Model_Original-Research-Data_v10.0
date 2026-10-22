#!/usr/bin/env python3
"""
O9-D8: m=4 (1013) 跨實驗不一致 — 誠實記錄
=============================================
Planck binned: 1013 係峰 (D=1079.5, 突出 4.4%)
ACT DR4 deep: 1000.5 係谷 (D=905.6), 1050 開始升, 1100 先係峰
SPT-3G: 1124 係峰 (bin 中心, 覆蓋 1099-1149)

→ m=4 喺 ACT DR4 消失? 定偏移?

物理檢查:
- Planck bin 寬 ~9 ℓ (高ℓ), ACT bin 寬 50 ℓ
- 峰 1013 如果真實, ACT 1000.5 bin (976-1025) 應該捕捉到
- 但 ACT 1000.5 = 905.6 係谷 → 唔似捕捉到峰

→ 可能 ACT DR4 嘅 m=4 被 bin 平滑 + 源剔除影響
→ 需要 ACT DR4 unbinned 或更高解析度數據確認
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
PYDIR = os.path.join(DATADIR, 'pyactlike', 'pyactlike', 'data')

print("="*78)
print("O9-D8: m=4 跨實驗不一致")
print("="*78)

# Planck
planck = np.loadtxt(os.path.join(DATADIR, 'planck_tt.txt'))
ell_p = planck[:,0]; c_p = planck[:,1]
d_p = c_p * ell_p*(ell_p+1)/(2*np.pi)
i4 = np.argmin(np.abs(ell_p-1013))
print("\n1. Planck m=4 區域:")
for i in range(i4-2, i4+4):
    mark = " ★" if d_p[i]>d_p[i-1] and d_p[i]>d_p[i+1] else ""
    print(f"   ℓ={ell_p[i]:.0f} D={d_p[i]:8.2f}{mark}")

# ACT DR4 deep
cl = np.loadtxt(os.path.join(PYDIR, 'cl_cmb_ap.dat'))
bval = cl[:,0]; X = cl[:,1]
bval_tt = bval[0:40]
D_tt = X[0:40]*bval_tt*(bval_tt+1)/(2*np.pi)
print("\n2. ACT DR4 deep m=4 區域:")
for i in range(len(bval_tt)):
    if 950 <= bval_tt[i] <= 1150:
        print(f"   ℓ={bval_tt[i]:.1f} D={D_tt[i]:8.1f}")

print("\n3. 對比:")
print("   Planck: 1013 峰 (D=1079.5), 1058 峰 (D=1129.8), 1121 峰 (D=1246.3)")
print("   ACT:    1000 谷 (D=905.6), 1050 升 (D=1084.1), 1100 峰 (D=1263.7)")
print("   → ACT 將 Planck 嘅 1013+1058 合併成一個上升斜坡 → 1100 峰")
print("   → 原因: ACT bin 寬 50 ℓ, Planck 高ℓ bin 寬 ~9 ℓ")
print("   → m=4 (1013) 太弱, 被 50 ℓ bin 平滑吞併")

print("\n4. 判決:")
print("   🟡 m=4 (1013) 存在性: Planck 確認, ACT 無法分辨 (bin 太粗)")
print("   ✅ m=5 (1121): 三數據源一致, Silk 阻尼轉折物理支持")
print("   → 用 ACT DR4 唔可以做 m=4 嘅獨立確認")
print("   → 需要 ACT DR4 unbinned / Planck unbinned / ACT DR6 高ℓ")
