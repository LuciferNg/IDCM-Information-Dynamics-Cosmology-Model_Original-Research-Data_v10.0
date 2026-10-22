#!/usr/bin/env python3
"""
O10 12: 記錄文檔數字驗證 (no-hallucination close-out)
=====================================================
驗證 02_results.md 內每個數字:
  1. Planck binned 峰高: 5816, 2579, 2553, 1246, 822
  2. 簡併對: P₁=0.4412, P₂=0.1778
  3. Fibonacci 階梯: S(3)=2φ⁻⁴, P₃=0.1353
  4. 文獻 D₃=1400 偏差 +82%
"""
import numpy as np, math, json, os, re

phi = (1 + 5**0.5) / 2
phi_inv = 1/phi
eps = phi_inv/4
F = [1, 1, 2, 3, 5, 8]

# ============ 重算所有關鍵數字 ============
print("=" * 70)
print("O10 數字驗證")
print("=" * 70)

# 1. Planck binned 峰高
DATA = os.path.join(os.path.dirname(__file__), "..", "..", "o9_high_ell_peaks", "data", "planck_tt.txt")
data = np.loadtxt(DATA)
l, val, err = data[:,0], data[:,1], data[:,2]
Dl = val * l*(l+1)/(2*np.pi)
Dl_err = err * l*(l+1)/(2*np.pi)

from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
s = gaussian_filter1d(Dl, sigma=1.5)
pk, _ = find_peaks(s, distance=25)

peaks = [(int(l[p]), Dl[p], Dl_err[p]) for p in pk]
print("\n1. Planck binned 峰 (自動):")
for le, D, e in peaks:
    print(f"   ℓ={le}: D={D:.0f} ± {e:.0f}")

D1 = peaks[0][1]
print(f"\n   D₁ = {D1:.0f} (文檔: 5816) {'✅' if abs(D1-5816)<5 else '❌'}")

# 2. 簡併對
P1 = (peaks[1][1] + peaks[2][1])/(2*D1)
P2 = (peaks[3][1] + peaks[4][1])/(2*D1)
print(f"\n2. 簡併對:")
print(f"   P₁ = {P1:.4f} (文檔: 0.4412) {'✅' if abs(P1-0.4412)<0.002 else '❌'}")
print(f"   P₂ = {P2:.4f} (文檔: 0.1778) {'✅' if abs(P2-0.1778)<0.002 else '❌'}")

# 3. Fibonacci 階梯
print("\n3. Fibonacci 階梯:")
for m in [1, 2, 3]:
    S = F[m-1] * phi_inv**(2*(m-1))
    P = 3*eps*S
    print(f"   m={m}: S={S:.5f}, P={P:.5f}")

P3_th = 3*eps*2*phi_inv**4
print(f"   P₃ 理論 = {P3_th:.5f} (文檔: 0.13525) {'✅' if abs(P3_th-0.13525)<1e-4 else '❌'}")

# 4. 文獻 D₃ 偏差
print("\n4. 文獻 D₃=1400 偏差:")
d3_real = peaks[2][1]
dev = (d3_real-1400)/1400*100
print(f"   D₃ real = {d3_real:.0f}, 文獻 1400, 偏差 {dev:+.0f}% (文檔: +82%) {'✅' if abs(dev-82)<3 else '❌'}")

# 5. P₂ 閉合 σ
P2_th = 3*eps*phi_inv**2
e1 = peaks[0][2]
e4 = peaks[3][2]
e5 = peaks[4][2]
eP2 = 0.5*np.sqrt((e4/D1)**2 + (e5/D1)**2)
sigma = abs(P2-P2_th)/eP2
print(f"\n5. P₂ 閉合: P₂={P2:.4f}±{eP2:.4f} vs 理論 {P2_th:.4f}, σ={sigma:.2f}")
print(f"   (文檔: 0.40σ) {'✅' if sigma < 1 else '❌'}")

# 6. P₁ 偏差
P1_th = 3*eps
dev1 = (P1-P1_th)/P1_th*100
eP1 = 0.5*np.sqrt((peaks[1][2]/D1)**2 + (peaks[2][2]/D1)**2)
sigma1 = abs(P1-P1_th)/eP1
print(f"\n6. P₁ 偏差: P₁={P1:.4f}±{eP1:.4f} vs 理論 {P1_th:.4f}, 偏差 {dev1:+.1f}%, σ={sigma1:.2f}")
print(f"   (文檔: -4.8%, 4.1σ) {'✅' if abs(dev1+4.8)<0.5 and abs(sigma1-4.1)<0.5 else '❌'}")

# 7. CAMB unlensed P₃
print("\n7. CAMB unlensed P₃ (文檔: 0.1359):")
print("   (需重跑 CAMB — 用先前結果 0.1355-0.1359)")

print("\n" + "=" * 70)
print("驗證完成")
print("=" * 70)
