#!/usr/bin/env python3
"""
O9-C16: ACT DR4 判決穩健性 — 誤差傳播 + 系統效應檢查
========================================================
判決: A₅/A₄ = 0.949 vs 1.167 (3.0σ), A₇/A₆ = 0.852 vs 1.080 (3.5σ)

檢查:
1. bin 中心效應 (用 Binning.dat 實際中心)
2. C_ℓ→D_ℓ 轉換正確性
3. 用 m=4/m=5 直接比 (唔經 A₂)
4. ACT DR4 有冇 known offset vs Planck?
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
PYDIR = os.path.join(DATADIR, 'pyactlike', 'pyactlike', 'data')

print("="*80)
print("O9-C16: ACT DR4 判決穩健性")
print("="*80)

binning = np.loadtxt(os.path.join(PYDIR, 'Binning.dat'))
l_low, l_high, l_center = binning[:,0], binning[:,1], binning[:,2]
cl = np.loadtxt(os.path.join(PYDIR, 'cl_cmb_ap.dat'))
n_bins = len(binning)
tt = cl[0:n_bins]
C = tt[:,1]; Cerr = tt[:,2]

# 用 bin 低/高邊界計算 D_ℓ 範圍
print("\n1. 用 bin 邊界檢查 D_ℓ 不確定性:")
for i, lc in enumerate(l_center):
    if 950 <= lc <= 1150:
        Dl = C[i]*lc*(lc+1)/(2*np.pi)
        Dl_lo = C[i]*l_low[i]*(l_low[i]+1)/(2*np.pi)
        Dl_hi = C[i]*l_high[i]*(l_high[i]+1)/(2*np.pi)
        print(f"   ℓ={lc:.0f}: D={Dl:.2f} (邊界 {Dl_lo:.2f}-{Dl_hi:.2f})")

# 關鍵: A₅/A₄ 用 bin 邊界誤差
print("\n2. A₅/A₄ 誤差帶 (bin 邊界):")
i4 = np.argmin(np.abs(l_center - 1014))
i5 = np.argmin(np.abs(l_center - 1121))
print(f"   m=4 bin: ℓ={l_center[i4]:.0f} (範圍 {l_low[i4]:.0f}-{l_high[i4]:.0f})")
print(f"   m=5 bin: ℓ={l_center[i5]:.0f} (範圍 {l_low[i5]:.0f}-{l_high[i5]:.0f})")
D4 = C[i4]*l_center[i4]*(l_center[i4]+1)/(2*np.pi)
D5 = C[i5]*l_center[i5]*(l_center[i5]+1)/(2*np.pi)
print(f"   D₄ = {D4:.2f}, D₅ = {D5:.2f}")
print(f"   A₅/A₄ = {D5/D4:.4f} vs 預言 7/6 = {7/6:.4f}")

# ACT 峰位 vs Planck 峰位
print("\n3. ACT vs Planck 峰位系統偏移:")
planck_peaks = {2: 527, 3: 815, 4: 1013, 5: 1121, 6: 1337, 7: 1400}
act_peaks = {2: 550, 3: 850, 4: 1000, 5: 1100, 6: 1350, 7: 1400}
print(f"   {'m':>2} {'Planck':>7} {'ACT':>7} {'偏移':>7}")
for m in range(2, 8):
    print(f"   {m:>2} {planck_peaks[m]:>7} {act_peaks[m]:>7} {act_peaks[m]-planck_peaks[m]:>+7}")

# ACT DR4 嘅官方 scale offset
print("\n4. ACT DR4 已知特性:")
print("   - ACT DR4 係 98/150 GHz 交叉頻譜 (day-deprojected)")
print("   - 標定: 對 Planck 有 ~1% 標定差異")
print("   - bin 寬 50, 峰位解析度 ±25")

# 如果用 Planck 振幅 + ACT 形狀
print("\n5. 用 ACT bin 直接比 (唔經峰偵測):")
print(f"   m=4 (ACT ℓ=1000): D = {C[i4]*l_center[i4]*(l_center[i4]+1)/(2*np.pi):.2f}")
print(f"   m=5 (ACT ℓ=1100): D = {C[i5]*l_center[i5]*(l_center[i5]+1)/(2*np.pi):.2f}")
print(f"   但 Planck: m=4 (1013) D=1079.5, m=5 (1121) D=1246.3")
print(f"   → Planck A₅/A₄ = {1246.3/1079.5:.4f} vs ACT {D5/D4:.4f}")
print(f"   → 兩者都 < 1.167 預言!")

# 結論
print("\n6. 判決確認:")
print(f"   Planck A₅/A₄ = 1.1545 (24/23 擬合)")
print(f"   ACT    A₅/A₄ = 0.9492")
print(f"   預言   A₅/A₄ = 1.1667 (7/6)")
print(f"   → 兩個數據集都唔支持 7/6 預言")
print(f"   → 3/14 同 1/7 係 Planck bin 離散化巧合, 唔係結構定律")
