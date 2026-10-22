#!/usr/bin/env python3
"""
O9-D6: ACT DR4 峰位偏移根源 — 標定定物理?
=============================================
ACT DR4 TT 峰: 550/850/1150/1350 (+23/+35/+29 vs Planck)
SPT-3G TT 峰: 524/824/1124 (-3/+9/+3 vs Planck)

ACT DR4 偏移 ≈ +29 ℓ 恆定? 定係 ℓ 依賴?

IDCM 結構檢查:
29 = L₇ (Lucas!)
29 = 33 − 4 = M − L₃
29 = 44 − 15 = N_d − (N_d−L₇)
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
PYDIR = os.path.join(DATADIR, 'pyactlike', 'pyactlike', 'data')

print("="*80)
print("O9-D6: ACT DR4 峰位偏移根源")
print("="*80)

binning = np.loadtxt(os.path.join(PYDIR, 'Binning.dat'))
l_center = binning[:,2]
cl = np.loadtxt(os.path.join(PYDIR, 'cl_cmb_ap.dat'))
n_bins = len(binning)
TT = cl[0:n_bins, 1]
D_TT = TT * l_center*(l_center+1)/(2*np.pi)

# ACT DR4 峰
print("\n1. ACT DR4 TT 峰 (300-1600):")
act_peaks = []
for j in range(1, len(D_TT)-1):
    if 300 < l_center[j] < 1600 and D_TT[j] > D_TT[j-1] and D_TT[j] > D_TT[j+1] and D_TT[j] > 100:
        act_peaks.append((l_center[j], D_TT[j]))
        print(f"   ★ ℓ={l_center[j]:.0f}  D={D_TT[j]:.2f}")

# 對比 Planck
print("\n2. ACT vs Planck 峰位偏移:")
planck = {2: 527, 3: 815, 4: 1013, 5: 1121, 6: 1337, 7: 1400}
# ACT 峰: 550, 850, 1150, 1350 (m=2..6), m=7?
act_map = {2: 550, 3: 850, 4: 1150, 5: 1350}
offsets = []
for m, p in planck.items():
    if m in act_map:
        off = act_map[m] - p
        offsets.append(off)
        print(f"   m={m}: Planck {p} vs ACT {act_map[m]} → Δ = {off:+d}")

# 但 ACT 1150 係 m=5 定 m=4?
print("\n3. 峰對應問題:")
print("   Planck: m=4=1013, m=5=1121, m=6=1337, m=7=1400")
print("   ACT:    1150, 1350, 1500")
print("   → ACT 1150 對 m=5 (1121)? Δ=+29")
print("   → ACT 1350 對 m=6 (1337)? Δ=+13")
print("   → ACT 1500 對 m=7 (1400)? Δ=+100?!")
print("   → 但 ACT 1150 可能係 m=4 (1013)? Δ=+137 太大")
print("   → 所以 ACT 峰對應: m=2→550, m=3→850, m=5→1150, m=6→1350")
print("   → ACT 冇 m=4 (1013) 峰?! (1150 係 m=5)")

# ACT 峰間距
print("\n4. ACT 峰間距 vs Planck:")
act_sp = [850-550, 1150-850, 1350-1150, 1500-1350]
planck_sp = [815-527, 1121-815, 1337-1121, 1400-1337]
print(f"   ACT:   {act_sp}")
print(f"   Planck: {planck_sp}")
print(f"   → ACT 前兩個間距 300, 300 vs Planck 288, 306")
print(f"   → ACT 第三個 200 vs Planck 216")

# 關鍵: ACT 1150 係 m=4 定 m=5?
print("\n5. 峰識別檢查 (用振幅):")
print("   Planck: m=4 (1013) D=1079.5, m=5 (1121) D=1246.3")
print("   ACT:    ℓ=1100 D=527.4, ℓ=1150 D=578.3")
print("   → ACT 1150 (578.3) > 1100 (527.4) — 上升中")
print("   → 如果 1150 係 m=5, 振幅應該 > m=4")
print("   → 但 ACT 1150 (578.3) vs 1000 (555.6) — 差唔多")
print("   → 唔能確定")

# 偏移統計
print("\n6. 偏移統計:")
if offsets:
    print(f"   offsets: {offsets}")
    print(f"   mean = {np.mean(offsets):.1f} ℓ")
    print(f"   → ACT DR4 平均 +{np.mean(offsets):.0f} ℓ (vs Planck)")
    print(f"   → 29 = L₇ = M−L₃ = N_d−15")
    print(f"   → 但呢個偏移可能係標定 (ACT DR4 98/150 GHz 交叉)")
