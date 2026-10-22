#!/usr/bin/env python3
"""
O9-C13: SPT-3G 振幅級聯驗證 (母函數獨立檢驗)
===============================================
用 SPT-3G D1 TT 150x150 bandpowers 驗證母函數:
A₂/A₁=(2/3)², A₃/A₁≈(2/3)², A₄/A₁=(3/7)², A₅/A₁=3/14, A₆/A₁=(4/11)², A₇/A₁=1/7

注意: SPT-3G bin 中心 424-2974, 冇 m=1 (220)
      用 m=2 (524) 做參考基準代替 A₁
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

print("="*80)
print("O9-C13: SPT-3G 振幅級聯驗證")
print("="*80)

# SPT-3G TT 150x150
bdp = np.loadtxt(os.path.join(DATADIR, 'spt3g_tne_bdp.txt'))
specs = [
    ('TT 90x90',52), ('TE 90x90',72), ('EE 90x90',72), ('TT 90x150',52),
    ('TE 90x150',72), ('TE 150x90',72), ('EE 90x150',72), ('TT 90x220',52),
    ('TE 90x220',72), ('TE 220x90',72), ('EE 90x220',72), ('TT 150x150',52),
    ('TE 150x150',72), ('EE 150x150',72), ('TT 150x220',52), ('TE 150x220',72),
    ('TE 220x150',72), ('EE 150x220',72), ('TT 220x220',52), ('TE 220x220',72),
    ('EE 220x220',72),
]
data = {}
idx = 0
for name, n in specs:
    data[name] = bdp[idx:idx+n]
    idx += n

win = np.loadtxt(os.path.join(DATADIR, 'spt_tt150_windows.txt'))
ell_w = win[:, 0]
W = win[:, 1:]
bin_centers = np.array([(ell_w * W[:,b]).sum()/W[:,b].sum() for b in range(W.shape[1])])
tt150 = data['TT 150x150']

# SPT-3G 峰表 (bin 中心局部極大)
print("\n1. SPT-3G TT150 峰:")
peaks = []
for i in range(1, len(tt150)-1):
    if tt150[i] > tt150[i-1] and tt150[i] > tt150[i+1] and tt150[i] > 100:
        peaks.append((bin_centers[i], tt150[i]))
        print(f"   ★ ℓ={bin_centers[i]:.0f}  D={tt150[i]:.1f}")

# 振幅級聯驗證 (用 SPT 峰)
print("\n2. SPT-3G 振幅級聯:")
if len(peaks) >= 4:
    # SPT 峰: 524, 824, 1124, 1424, 1724, 2024
    spt_peaks = {round(l): v for l, v in peaks}
    # 用 m=2 (524) 做基準 (因為冇 m=1)
    if 524 in spt_peaks:
        A2 = spt_peaks[524]
        print(f"   A₂ (ℓ=524) = {A2:.1f}")
        # 預言: A₃/A₂ ≈ 1 (兩個都 (2/3)² 相對 A₁)
        # A₄/A₂ = (3/7)²/(2/3)² = (9/14)²
        # A₅/A₂ = (3/14)/(4/9) = 27/56
        # A₆/A₂ = (4/11)²/(2/3)² = (6/11)²
        # A₇/A₂ = (1/7)/(4/9) = 9/28
        preds = {
            3: 1.0,  # A₃/A₂ ≈ 1
            4: (9/14)**2,
            5: 27/56,
            6: (6/11)**2,
            7: 9/28,
        }
        for m, r in preds.items():
            # 搵 SPT 峰接近 IDCM m 峰位
            idcm_l = {3: 810, 4: 1014, 5: 1121, 6: 1340, 7: 1412}[m]
            closest_l = min(spt_peaks.keys(), key=lambda l: abs(l - idcm_l))
            obs_r = spt_peaks[closest_l]/A2
            dev = abs(obs_r - r)/r*100
            print(f"   A{m}/A₂ = {obs_r:.4f} (ℓ={closest_l:.0f}) vs 預言 {r:.4f} dev={dev:.1f}%")

# 直接母函數檢查 (用 A₂ 做基準)
print("\n3. 母函數 A_m/A₁ 轉換 (A₂=0.4434A₁):")
A2_ratio = (2/3)**2  # 0.4444
print(f"   A₁ 推算 = A₂/{(2/3)**2:.4f}")
