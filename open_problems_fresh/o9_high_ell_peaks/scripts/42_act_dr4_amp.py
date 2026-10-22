#!/usr/bin/env python3
"""
O9-C15: ACT DR4 振幅級聯驗證 — m=4/m=5 獨立分辨
===================================================
ACT DR4 有 1000 (m=4) 同 1100 (m=5) 分開 bin!
驗證母函數:
A₄/A₁=(3/7)², A₅/A₁=3/14, A₆/A₁=(4/11)², A₇/A₁=1/7

注意: ACT DR4 冇 m=1 (220, 最低 350)
      但可以用 A₃ (850) 做基準? 或者用 Planck A₁ 做外部基準?
      
ACT DR4 振幅相對值: A_m/A_n 可以直接比較母函數預言!
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
PYDIR = os.path.join(DATADIR, 'pyactlike', 'pyactlike', 'data')

print("="*80)
print("O9-C15: ACT DR4 振幅級聯驗證")
print("="*80)

binning = np.loadtxt(os.path.join(PYDIR, 'Binning.dat'))
l_center = binning[:,2]
cl = np.loadtxt(os.path.join(PYDIR, 'cl_cmb_ap.dat'))
n_bins = len(binning)
tt = cl[0:n_bins]  # TT
D_tt = tt[:,1] * l_center*(l_center+1)/(2*np.pi)
err_tt = tt[:,2] * l_center*(l_center+1)/(2*np.pi)

# ACT DR4 峰 (局部極大, 只喺 300-1600)
print("\n1. ACT DR4 峰 (300-1600):")
peaks = []
for i in range(1, len(D_tt)-1):
    if 300 < l_center[i] < 1600 and D_tt[i] > D_tt[i-1] and D_tt[i] > D_tt[i+1] and D_tt[i] > 100:
        peaks.append((l_center[i], D_tt[i], err_tt[i]))
        print(f"   ★ ℓ={l_center[i]:.0f}  D={D_tt[i]:.2f} ± {err_tt[i]:.2f}")

# 峰位同 IDCM 對應
print("\n2. ACT DR4 峰 → IDCM m 對應:")
idcm_l = {2: 537, 3: 810, 4: 1014, 5: 1121, 6: 1340, 7: 1412}
act_amp = {}
for m, pred in idcm_l.items():
    j = np.argmin(np.abs(l_center - pred))
    act_amp[m] = (D_tt[j], err_tt[j], l_center[j])
    print(f"   m={m}: ACT ℓ={l_center[j]:.0f} D={D_tt[j]:.2f}±{err_tt[j]:.2f}")

# 振幅比 (用 ACT 內部, 唔使 A₁)
print("\n3. ACT DR4 內部振幅比:")
# A₄/A₂, A₅/A₂, A₆/A₂, A₇/A₂ (用 m=2 做基準, 因為 ACT 冇 m=1)
A2, e2, _ = act_amp[2]
preds = {
    4: (3/7)**2 / (2/3)**2,   # (9/14)²
    5: (3/14) / (4/9),        # 27/56
    6: (4/11)**2 / (2/3)**2,  # (6/11)²
    7: (1/7) / (4/9),         # 9/28
}
for m, p in preds.items():
    A, e, l = act_amp[m]
    r = A/A2
    rel_err = np.sqrt((e/A)**2 + (e2/A2)**2)
    dev = abs(r - p)/p*100
    sigma = abs(r-p)/rel_err
    print(f"   A{m}/A₂ = {r:.4f} ± {rel_err:.4f} vs 預言 {p:.4f} → dev={dev:.1f}% ({sigma:.1f}σ)")

# 用 m=3 做基準 (ACT 峰 850)
print("\n4. 用 m=3 (850) 做基準:")
A3, e3, _ = act_amp[3]
preds3 = {
    4: (3/7)**2 / (2/3)**2,
    5: (3/14) / (2/3)**2,
    6: (4/11)**2 / (2/3)**2,
    7: (1/7) / (2/3)**2,
}
for m, p in preds3.items():
    A, e, l = act_amp[m]
    r = A/A3
    rel_err = np.sqrt((e/A)**2 + (e3/A3)**2)
    dev = abs(r - p)/p*100
    sigma = abs(r-p)/rel_err
    print(f"   A{m}/A₃ = {r:.4f} ± {rel_err:.4f} vs 預言 {p:.4f} → dev={dev:.1f}% ({sigma:.1f}σ)")

# 直接: A₅/A₄ (關鍵 — m=4/m=5 獨立!)
print("\n5. 關鍵: A₅/A₄ (m=4/m=5 獨立分辨):")
A4, e4, _ = act_amp[4]
A5, e5, _ = act_amp[5]
r54 = A5/A4
rel_err = np.sqrt((e5/A5)**2 + (e4/A4)**2)
p54 = (3/14)/(3/7)**2
dev = abs(r54 - p54)/p54*100
sigma = abs(r54-p54)/rel_err
print(f"   A₅/A₄ = {r54:.4f} ± {rel_err:.4f} vs 預言 {p54:.4f} → dev={dev:.1f}% ({sigma:.1f}σ)")
print(f"   預言: A₅/A₄ = (3/14)/(3/7)² = (3/14)/(9/49) = 3/14 × 49/9 = 7/6 ≈ 1.167")

# 直接: A₇/A₆
print(f"\n6. 關鍵: A₇/A₆:")
A6, e6, _ = act_amp[6]
A7, e7, _ = act_amp[7]
r76 = A7/A6
rel_err = np.sqrt((e7/A7)**2 + (e6/A6)**2)
p76 = (1/7)/(4/11)**2
dev = abs(r76 - p76)/p76*100
sigma = abs(r76-p76)/rel_err
print(f"   A₇/A₆ = {r76:.4f} ± {rel_err:.4f} vs 預言 {p76:.4f} → dev={dev:.1f}% ({sigma:.1f}σ)")
print(f"   預言: A₇/A₆ = (1/7)/(4/11)² = (1/7)/(16/121) = 121/112 ≈ 1.080")
