#!/usr/bin/env python3
"""
O10 19: ACT DR6 完整 TT bandpowers + P₄ 盲測
==============================================
ACT DR6 TT: 45 bins, ℓ ∈ [598.5, ...]
單位: D_ℓ µK² (value column)
"""
import numpy as np, os, json
from astropy.io import fits

phi = (1 + 5**0.5) / 2
eps = phi**-1/4
F4 = 3
P4_th = 3*eps*F4*phi**-6

path = os.path.join(os.path.dirname(__file__), "..", "..", "o9_high_ell_peaks", "data", "act_dr6_cmb_sacc.fits")
hdul = fits.open(path)
tt = hdul['data:cl_00'].data

ell = tt['ell']
val = tt['value']
# 可能仲有 error? 睇 covariance
print("ACT DR6 TT 完整:")
for i in range(len(ell)):
    print(f"  bin {i:2d}: ℓ={ell[i]:7.1f}  D={val[i]:9.2f} µK²")

# ============ 峰位對比 ============
print("\n" + "=" * 72)
print("P₄ 盲測: ACT DR6 喺峰 8,9 位置 (1465/1474)")
print("=" * 72)
peaks = {1: 220, 2: 527, 3: 815, 4: 1121, 5: 1409, 6: 1340, 7: 1412, 8: 1465, 9: 1474}
for m, lp in peaks.items():
    if lp < ell[0] or lp > ell[-1]:
        print(f"  峰 {m} @ {lp}: 喺 ACT 範圍外 ({ell[0]:.0f}-{ell[-1]:.0f})")
        continue
    idx = np.argmin(np.abs(ell - lp))
    print(f"  峰 {m} @ {lp}: 最近 bin ℓ={ell[idx]:.0f}, D={val[idx]:.1f}")

# ACT 峰位置 (local maxima)
print("\nACT DR6 峰結構 (D_ℓ local maxima):")
for i in range(1, len(val)-1):
    if val[i] > val[i-1] and val[i] > val[i+1]:
        print(f"  峰 @ ℓ={ell[i]:.0f}, D={val[i]:.1f}")

# 對比 Planck D₁ 計算比率
print("\n" + "=" * 72)
print("A/A₁ 比率 (用 Planck D₁=5816 做基準, cross-experiment)")
print("=" * 72)
D1 = 5816
# 峰 6,7 (P₃ 已閉合) 喺 ACT?
for m in [6, 7, 8, 9]:
    lp = peaks[m]
    if lp < ell[0] or lp > ell[-1]:
        continue
    idx = np.argmin(np.abs(ell - lp))
    ratio = val[idx]/D1
    print(f"  峰 {m} @ ℓ={lp}: ACT D={val[idx]:.1f} → A/A₁ = {ratio:.4f}")

print(f"\nP₄ 預測 = {P4_th:.4f}")
print(f"P₃ 預測 = {3*eps*2*phi**-4:.4f}")

# 儲存
with open(os.path.join(os.path.dirname(__file__), "..", "data", "act_dr6_tt.json"), "w") as f:
    json.dump({"ell": ell.tolist(), "D": val.tolist()}, f, indent=1)
print("\n已儲存 -> data/act_dr6_tt.json")
