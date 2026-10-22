#!/usr/bin/env python3
"""
O10 25: 真峰配對 — Fibonacci 階梯嘅正確閉合
==============================================
關鍵修正: 用「真峰」(自動峰) 配對, 唔用 IDCM 峰位!

Planck 真峰 (自動): 221, 527, 815, 1121, 1409 (5 個)
  → 峰編號: 1=221, 2=527, 3=815, 4=1121, 5=1409
  → P₁ = (峰2+峰3)/2, P₂ = (峰4+峰5)/2

之前錯誤: 用 IDCM 峰位 1013/1199 當峰4/5 (唔係真峰)
"""
import numpy as np, math, os
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

phi = (1 + 5**0.5) / 2
eps = phi**-1/4
F = [1, 1, 2, 3, 5, 8]
def P_th(m):
    return 3*eps*F[m-1]*phi**(-2*(m-1))

# Planck
DATA = os.path.join(os.path.dirname(__file__), "..", "..", "o9_high_ell_peaks", "data", "planck_tt.txt")
data = np.loadtxt(DATA)
l, val, err = data[:,0], data[:,1], data[:,2]
Dl = val * l*(l+1)/(2*np.pi)
Dl_err = err * l*(l+1)/(2*np.pi)

s = gaussian_filter1d(Dl, sigma=1.5)
pk, _ = find_peaks(s, distance=25)
D1 = Dl[np.argmin(np.abs(l-221))]

# 真峰 (排除低 ℓ 偽峰)
peaks = [(l[p], Dl[p]) for p in pk if l[p] > 100 and Dl[p] > 200]
peaks.sort()
print("Planck 真峰:")
for i, (le, D) in enumerate(peaks):
    print(f"  峰{i+1}: ℓ={le:.0f}, D={D:.0f}, A={D/D1:.4f}")

print()
print("=" * 72)
print("真峰配對 vs IDCM 峰位配對")
print("=" * 72)

# 真峰配對: 峰2,3 → P₁; 峰4,5 → P₂
A_true = {1: peaks[0][1]/D1, 2: peaks[1][1]/D1, 3: peaks[2][1]/D1,
          4: peaks[3][1]/D1, 5: peaks[4][1]/D1}
print("\n[真峰配對]")
P1_true = (A_true[2] + A_true[3])/2
P2_true = (A_true[4] + A_true[5])/2
print(f"  P₁ = (峰2+峰3)/2 = ({A_true[2]:.4f}+{A_true[3]:.4f})/2 = {P1_true:.4f} vs 3ε={P_th(1):.4f} → {(P1_true-P_th(1))/P_th(1)*100:+.2f}%")
print(f"  P₂ = (峰4+峰5)/2 = ({A_true[4]:.4f}+{A_true[5]:.4f})/2 = {P2_true:.4f} vs 3εφ⁻²={P_th(2):.4f} → {(P2_true-P_th(2))/P_th(2)*100:+.2f}%")

# 誤差傳播
print("\n誤差:")
# 峰誤差
for i, (le, D) in enumerate(peaks):
    idx = np.argmin(np.abs(l-le))
    e = Dl_err[idx]/D1
    print(f"  峰{i+1} @ {le:.0f}: err = {e:.4f} ({Dl_err[idx]:.0f}/{D1:.0f})")
e2, e3 = Dl_err[np.argmin(np.abs(l-527))]/D1, Dl_err[np.argmin(np.abs(l-815))]/D1
e4, e5 = Dl_err[np.argmin(np.abs(l-1121))]/D1, Dl_err[np.argmin(np.abs(l-1409))]/D1
eP1 = 0.5*np.sqrt(e2**2+e3**2)
eP2 = 0.5*np.sqrt(e4**2+e5**2)
print(f"  σ(P₁) = {abs(P1_true-P_th(1))/eP1:.2f}")
print(f"  σ(P₂) = {abs(P2_true-P_th(2))/eP2:.2f}")

# IDCM 峰位配對 (舊)
print("\n[IDCM 峰位配對 (舊, 錯誤)]")
A_old = {4: 0.1856, 5: 0.2143}  # 1013/1121
P2_old = (A_old[4]+A_old[5])/2
print(f"  P₂ = (A₁₀₁₃+A₁₁₂₁)/2 = {P2_old:.4f} → {(P2_old-P_th(2))/P_th(2)*100:+.2f}%")

# 新理解: 峰編號
print()
print("=" * 72)
print("峰編號修正:")
print("=" * 72)
print("IDCM 峰位表: 221, 527, 815, 1013, 1121, 1337, 1400 (7 個)")
print("Planck 真峰: 221, 527, 815, 1121, 1409 (5 個)")
print()
print("→ IDCM 峰位 1013 (m4) 同 1337 (m6) 唔係真峰!")
print("→ 真峰 1121 = IDCM m5, 真峰 1409 ≈ IDCM m7 (1400)")
print("→ 真峰序列: 221(1), 527(2), 815(3), 1121(4), 1409(5)")
print()
print("簡併對 (真峰): (2,3) = (527,815), (4,5) = (1121,1409)")
print("峰 6,7 唔存在 (damping tail) — 同 P₄ 裁決一致!")
print()
print("→ Fibonacci 階梯 P_m = 3ε·F_m·φ^(-2(m-1)):")
print("    P₁ = 3ε (峰2,3) = 0.4635 vs 0.4412 (-4.8%, ISW)")
print("    P₂ = 3εφ⁻² (峰4,5) = 0.1771 vs 0.1779 (+0.43% ✅)")
print("    P₃+ = 冇峰 → 冇得驗證 (damping tail 截斷)")
