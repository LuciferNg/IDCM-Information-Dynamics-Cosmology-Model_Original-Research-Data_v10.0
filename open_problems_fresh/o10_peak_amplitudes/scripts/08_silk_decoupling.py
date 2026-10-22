#!/usr/bin/env python3
"""
O10 08: Silk 阻尼解耦 — 純幾何反彈振幅提取
===========================================
方法:
  1. CAMB unlensed (聲波 + Silk, 冇 lensing 平滑) vs lensed (聲波 + Silk + lensing)
  2. 擬合 Silk 阻尼 D(ℓ) = exp[-(ℓ/ℓ_D)^{3/2}]
  3. 剝離阻尼 → 純幾何反彈 S(m)
  4. 驗證: S(m) = φ^(-2(m-1)) (用戶) vs F_m·φ^(-2(m-1)) (Fibonacci)

物理約束: 阻尼 D ≤ 1 (Silk 只衰減)
"""
import camb
import numpy as np
import math
from scipy.optimize import curve_fit
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

phi = (1 + 5**0.5) / 2
phi_inv = 1/phi
eps = phi_inv/4
F = [1, 1, 2, 3, 5, 8, 13]

# ============ CAMB 生成 ============
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, tau=0.0544)
pars.InitPower.set_params(ns=0.9649, As=2.1e-9)
pars.set_for_lmax(3000)
res = camb.get_results(pars)

# unlensed scalar (C_l) — 聲波 + Silk, 冇 lensing
unl = res.get_cmb_power_spectra(raw_cl=True, spectra=['unlensed_scalar'])['unlensed_scalar']
# lensed total (D_l μK²)
lens = res.get_cmb_power_spectra(spectra=['total'], CMB_unit='muK')['total']

ell = np.arange(len(unl))
Dl_unl = unl[:, 0] * ell * (ell + 1) / (2*np.pi) * 1e12  # μK²
Dl_lens = lens[:, 0]

# ============ IDCM 峰位讀數 (unlensed) ============
idcm_peaks = {1: 220, 2: 537, 3: 810, 4: 1014, 5: 1199, 6: 1340, 7: 1412}

def read_height(Dl, l_target, window=15):
    idx = np.where(np.abs(ell - l_target) <= window)[0]
    j = idx[np.argmax(Dl[idx])]
    return int(ell[j]), float(Dl[j])

print("=" * 72)
print("CAMB unlensed D_ℓ @ IDCM 峰位 (聲波+Silk, 冇 lensing)")
print("=" * 72)
A_unl = {}
for m, lp in idcm_peaks.items():
    le, D = read_height(Dl_unl, lp)
    A_unl[m] = D / Dl_unl[np.argmin(np.abs(ell-220))]
    print(f"  m={m}: ℓ={le} D={D:.0f} | A_m/A₁={A_unl[m]:.4f}")

# 簡併對平均 (unlensed)
print()
print("簡併對平均 P_m (unlensed):")
P_unl = {}
ell_P = {}
for m in range(1, 4):
    P_unl[m] = (A_unl[2*m] + A_unl[2*m+1])/2
    ell_P[m] = (idcm_peaks[2*m] + idcm_peaks[2*m+1])/2
    print(f"  P_{m} = {P_unl[m]:.4f} @ <ℓ>={ell_P[m]:.0f}")

print()
print("=" * 72)
print("Silk 解耦: P_obs = P_fluid × D(ℓ),  D(ℓ) = exp[-(ℓ/ℓ_D)^{3/2}]")
print("=" * 72)

# 假設 P_fluid = 3ε × S(m):
#   用戶階梯: S_u(m) = φ^{-2(m-1)} = (1, 0.382, 0.146)
#   Fib 階梯: S_f(m) = F_m·φ^{-2(m-1)} = (1, 0.382, 0.292)
S_user = {1: 1.0, 2: phi_inv**2, 3: phi_inv**4}
S_fib  = {1: 1.0, 2: phi_inv**2, 3: 2*phi_inv**4}

for label, S in [("用戶 φ^(-2(m-1))", S_user), ("Fibonacci F_m·φ^(-2(m-1))", S_fib)]:
    print(f"\n[{label}]")
    print(f"  所需阻尼 D_m = P_obs/(3ε·S(m)):")
    ok = True
    for m in range(1, 4):
        D_req = P_unl[m]/(3*eps*S[m])
        status = "✅" if D_req <= 1.02 else "❌ 物理矛盾 (D>1)"
        if D_req > 1.02: ok = False
        print(f"    m={m}: D = {D_req:.4f} {status}")
    if ok:
        # 擬合 ℓ_D
        print("  → 所有 D ≤ 1, 可擬合 ℓ_D:")
        for m in range(1, 4):
            D_req = P_unl[m]/(3*eps*S[m])
            if D_req <= 1:
                lD = ell_P[m] / (-math.log(D_req))**(2/3)
                print(f"    m={m}: ℓ_D = {lD:.0f}")

print()
print("=" * 72)
print("無阻尼極限檢查: 純幾何 S(m) 必須 ≥ P_obs/3ε")
print("=" * 72)
for m in range(1, 4):
    S_min = P_unl[m]/(3*eps)
    print(f"  m={m}: P/3ε = {S_min:.5f}")
    print(f"    φ^(-2(m-1)) = {S_user[m]:.5f}  {'✅ 可加阻尼' if S_user[m] >= S_min else '❌ 需要放大'}")
    print(f"    F_m·φ^(-2(m-1)) = {S_fib[m]:.5f}  {'✅ 可加阻尼' if S_fib[m] >= S_min else '❌ 需要放大'}")

# ============ lensed 對比 ============
print()
print("=" * 72)
print("lensed vs unlensed 簡併對 (lensing 效應)")
print("=" * 72)
A_lens = {}
for m, lp in idcm_peaks.items():
    le, D = read_height(Dl_lens, lp)
    A_lens[m] = D / Dl_lens[np.argmin(np.abs(ell-220))]
for m in range(1, 4):
    P_lens = (A_lens[2*m] + A_lens[2*m+1])/2
    P_fib = 3*eps*S_fib[m]
    dev = (P_lens-P_fib)/P_fib*100
    print(f"  P_{m}: lensed {P_lens:.4f} | unlensed {P_unl[m]:.4f} | Fib理論 {P_fib:.4f} | lensed偏差 {dev:+.3f}%")
