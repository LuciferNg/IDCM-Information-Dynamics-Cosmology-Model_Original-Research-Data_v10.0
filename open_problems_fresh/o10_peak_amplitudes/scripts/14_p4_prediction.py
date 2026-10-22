#!/usr/bin/env python3
"""
O10 14: P₄ 預測驗證 — Planck binned 高 ℓ (峰 8,9)
==================================================
P₄ 預測 = 3ε·F₄·φ⁻⁶ = 3ε·3·φ⁻⁶ ≈ 0.0775

峰位公式: ℓ_m = 44×(M−C(9−m,2)) + ((m−1)·9 mod 25)
  m=8: 44×33 + 13 = 1465
  m=9: 44×33 + 22 = 1474

Planck binned 覆蓋到 ℓ=2492 → 可以讀取
"""
import numpy as np, math, os
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

phi = (1 + 5**0.5) / 2
phi_inv = 1/phi
eps = phi_inv/4
F = [1, 1, 2, 3, 5, 8, 13, 21, 34]

DATA = os.path.join(os.path.dirname(__file__), "..", "..", "o9_high_ell_peaks", "data", "planck_tt.txt")
data = np.loadtxt(DATA)
l, val, err = data[:,0], data[:,1], data[:,2]
Dl = val * l*(l+1)/(2*np.pi)
Dl_err = err * l*(l+1)/(2*np.pi)

# IDCM 峰位公式
def idcm_ell(m):
    import math as _m
    N_int = 33 - _m.comb(9-m, 2)
    frac = ((m-1)*9) % 25
    return 44*N_int + frac

print("IDCM 峰位 m=1..9:")
for m in range(1, 10):
    print(f"  m={m}: ℓ={idcm_ell(m)}")

# 讀取高 ℓ 峰 8,9 高度
print()
print("Planck binned @ m=8,9 (IDCM 峰位):")
D1_idx = np.argmin(np.abs(l - 220))
D1 = Dl[D1_idx]
for m in [8, 9]:
    le = idcm_ell(m)
    idx = np.argmin(np.abs(l - le))
    D = Dl[idx]
    e = Dl_err[idx]
    ratio = D/D1
    print(f"  m={m}: ℓ={le} → binned ℓ={l[idx]:.0f}, D={D:.0f}±{e:.0f}, A_m/A₁={ratio:.4f}")

# P₄ = (A₈+A₉)/2
print()
idx8 = np.argmin(np.abs(l - idcm_ell(8)))
idx9 = np.argmin(np.abs(l - idcm_ell(9)))
P4_obs = (Dl[idx8] + Dl[idx9])/(2*D1)
P4_th = 3*eps * F[3] * phi_inv**6
print(f"P₄ 觀測 = ({Dl[idx8]:.0f}+{Dl[idx9]:.0f})/(2×{D1:.0f}) = {P4_obs:.4f}")
print(f"P₄ 預測 = 3ε·F₄·φ⁻⁶ = {P4_th:.4f}")
print(f"偏差 = {(P4_obs-P4_th)/P4_th*100:+.2f}%")

# 誤差
e8 = Dl_err[idx8]/D1
e9 = Dl_err[idx9]/D1
eP4 = 0.5*np.sqrt(e8**2 + e9**2)
sigma = abs(P4_obs-P4_th)/eP4
print(f"σ = {sigma:.2f}")

# 自動峰檢測高 ℓ 段 (1300-2000)
print()
print("高 ℓ 自動峰 (ℓ>1300):")
s = gaussian_filter1d(Dl, sigma=1.5)
pk, _ = find_peaks(s, distance=25)
for p in pk:
    if l[p] > 1300:
        print(f"  ℓ={l[p]:.0f}, D={Dl[p]:.0f}")
