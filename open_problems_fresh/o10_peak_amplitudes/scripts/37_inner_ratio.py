#!/usr/bin/env python3
"""
O10 37: 簡併對內部比率 — Fibonacci 連續比 + √3/2
=================================================
發現:
  P₁ (峰2,3): 比 = 0.980 ≈ 1
  P₂ (峰4,5): 比 = 0.667 = 2/3 (lensed 0.659)
  P₃ (峰6,7): 比 = 0.867 ≈ √3/2 (lensed)

但等我更精確計算 (Planck binned ground truth):
"""
import numpy as np, math, os
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

phi = (1 + 5**0.5) / 2

DATA = os.path.join(os.path.dirname(__file__), "..", "..", "o9_high_ell_peaks", "data", "planck_tt.txt")
data = np.loadtxt(DATA)
l, val, err = data[:,0], data[:,1], data[:,2]
Dl = val * l*(l+1)/(2*np.pi)
D1 = Dl[np.argmin(np.abs(l-221))]

# Planck 真峰
peaks = [(221, 5816), (527, 2579), (815, 2553), (1121, 1246), (1409, 822)]
print("Planck 真峰簡併對內部比率:")
for m, (a, b) in {1: (1, 2), 2: (3, 4)}.items():  # 0-indexed: 峰2,3 同 峰4,5
    Aa, Ab = peaks[a][1]/D1, peaks[b][1]/D1
    r = Ab/Aa  # 後峰/前峰
    print(f"  峰{peaks[a][0]}/峰{peaks[b][0]}: {Aa:.4f}/{Ab:.4f} = {r:.4f}")

print()
print("峰 5/峰 4 = 822/1246 =", 822/1246)
print("2/3 =", 2/3)
print("偏差:", (822/1246 - 2/3)/(2/3)*100, "%")

print()
print("峰 3/峰 2 = 2553/2579 =", 2553/2579)
print("≈ 1 (真簡併)")
print()

# ACT DR6 (峰3,4,5 位置: 798, 1098, 1448)
print("ACT DR6 峰 (798, 1098, 1448):")
D_act = [2500.7, 1216.6, 800.4]
print(f"  峰5/峰4 (1448/1098) = {800.4/1216.6:.4f} vs 2/3 = {2/3:.4f}")
print(f"  峰4/峰3 (1098/798) = {1216.6/2500.7:.4f}")
print()

print("=" * 60)
print("Fibonacci 連續比: F_{m+1}/F_{m+2}")
print("=" * 60)
F = [1, 1, 2, 3, 5, 8, 13]
for i in range(1, 6):
    print(f"  F_{i}/F_{i+1} = {F[i-1]}/{F[i]} = {F[i-1]/F[i]:.4f}")

print()
print("觀察: 峰4,5 比 2/3 = F₃/F₄")
print("      峰6,7 比 √3/2 — 唔係 Fibonacci?")
print("      峰2,3 比 1 — F₁/F₂ = 1/1 = 1!")
print()
print("如果 P_m 內部 = F_m/F_{m+1} (連續比):")
print("  P₁ (峰2,3): F₁/F₂ = 1/1 = 1.0  ✅ (0.98)")
print("  P₂ (峰4,5): F₃/F₄ = 2/3 = 0.667  ✅ (0.659-0.667)")
print("  P₃ (峰6,7): F₅/F₆ = 5/8 = 0.625  ❌ (0.867)")
print()
print("→ 峰 6,7 嘅 0.867 唔匹配 F₅/F₆ = 0.625")
print("→ 但 0.867 ≈ √3/2 — 三角形幾何?")
print("→ 或者: 峰 6,7 讀數受 Silk 影響大 (lensed 平滑) → 比率失真")
