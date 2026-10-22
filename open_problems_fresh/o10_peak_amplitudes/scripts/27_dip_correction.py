#!/usr/bin/env python3
"""
O10 27: P₂ 嘅 D>1 殘留 — dip 校正 + lensing 效應
==================================================
unlensed P₂ 需要 D=1.037 (>1, Silk 解釋唔到)

假設: 峰 4,5 之間嘅 dip 唔夠深 (lensing 平滑)
  → 峰高讀數包含「谷底」抬升
  → 用 peak-to-dip 振幅 (峰 - 谷) 重算

Planck 真峰 + 谷:
  峰2 @ 527 (2579), 峰3 @ 815 (2553)
  峰4 @ 1121 (1246), 峰5 @ 1409 (822)
  谷: 410 (1738), 680 (1761), 1022 (1032), 1319 (719)
"""
import numpy as np, math, os
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

phi = (1 + 5**0.5) / 2
eps = phi**-1/4
F = [1, 1, 2, 3, 5, 8]

DATA = os.path.join(os.path.dirname(__file__), "..", "..", "o9_high_ell_peaks", "data", "planck_tt.txt")
data = np.loadtxt(DATA)
l, val, err = data[:,0], data[:,1], data[:,2]
Dl = val * l*(l+1)/(2*np.pi)
Dl_err = err * l*(l+1)/(2*np.pi)
D1 = Dl[np.argmin(np.abs(l-221))]

s = gaussian_filter1d(Dl, sigma=1.5)
pk, _ = find_peaks(s, distance=25)
tr, _ = find_peaks(-s, distance=25)

peaks = [(l[p], Dl[p]) for p in pk if l[p] > 100 and Dl[p] > 200]
troughs = [(l[p], Dl[p]) for p in tr if l[p] > 100 and Dl[p] > 100]

print("Planck 峰:", [(f"ℓ={le:.0f}", f"D={D:.0f}") for le, D in peaks])
print("Planck 谷:", [(f"ℓ={le:.0f}", f"D={D:.0f}") for le, D in troughs])

print()
print("=" * 72)
print("峰-谷振幅 (dip-corrected)")
print("=" * 72)
# 峰-谷配對: 峰 m 之前嘅谷
peak_dip = {}
for i, (le, D) in enumerate(peaks):
    # 搵峰之前最近嘅谷
    prev_tr = [t for t in troughs if t[0] < le]
    if prev_tr:
        tr_ = max(prev_tr, key=lambda x: x[0])
        peak_dip[i+1] = (D - tr_[1])/D1
        print(f"  峰{i+1} @ {le:.0f} ({D:.0f}) - 谷 @ {tr_[0]:.0f} ({tr_[1]:.0f}) = {(D-tr_[1])/D1:.4f}")

print()
print("簡併對 (峰-谷):")
P1_pd = (peak_dip[2] + peak_dip[3])/2
P2_pd = (peak_dip[4] + peak_dip[5])/2
P1_th, P2_th = 3*eps, 3*eps*phi**-2
print(f"  P₁ (峰2,3 dip) = {P1_pd:.4f} vs {P1_th:.4f} → {(P1_pd-P1_th)/P1_th*100:+.2f}%")
print(f"  P₂ (峰4,5 dip) = {P2_pd:.4f} vs {P2_th:.4f} → {(P2_pd-P2_th)/P2_th*100:+.2f}%")

# 峰-谷比率結構
print()
print("峰-谷比率 (每峰):")
for i in range(1, 6):
    ratio = peak_dip[i]/peak_dip[1]
    print(f"  峰{i}: dip/D₁ = {peak_dip[i]:.4f}")

print()
print("=" * 72)
print("對比: 峰高讀數 vs 峰-谷讀數")
print("=" * 72)
A_peak = {1: 1.0, 2: 0.4434, 3: 0.4389, 4: 0.2143, 5: 0.1414}
for i in range(1, 6):
    print(f"  峰{i}: 峰高 {A_peak[i]:.4f} vs dip {peak_dip[i]:.4f}")

# 關鍵: 峰-谷振幅比率
print()
print("峰-谷比率 A_dip(m)/A_dip(1):")
for i in range(2, 6):
    r = peak_dip[i]/peak_dip[1]
    print(f"  m={i}: {r:.4f}")
print("對比 Fibonacci 階梯 (簡併對平均):")
print(f"  P₁/3ε = {1:.4f}")
print(f"  P₂/3ε = {phi**-2:.4f} (φ⁻²)")
