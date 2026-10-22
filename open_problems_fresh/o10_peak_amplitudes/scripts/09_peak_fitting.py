#!/usr/bin/env python3
"""
O10 09: 精確峰擬合 + 幾何平均 vs 算術平均
==========================================
問題: unlensed P₂/3ε = 0.4068 > φ⁻² = 0.382 (6.5% 偏差, D₂>1 物理矛盾)

可能原因:
  1. 算術平均受 outlier (A₅=0.1979) 影響 → 試幾何平均
  2. IDCM 峰位 vs 真實峰位偏移 → 試自動峰
  3. 峰 5 (ℓ=1184) 讀數受相鄰結構污染 → 檢查譜形狀
"""
import camb
import numpy as np
import math
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

phi = (1 + 5**0.5) / 2
phi_inv = 1/phi
eps = phi_inv/4
F = [1, 1, 2, 3, 5, 8, 13]

pars = camb.CAMBparams()
pars.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, tau=0.0544)
pars.InitPower.set_params(ns=0.9649, As=2.1e-9)
pars.set_for_lmax(3000)
res = camb.get_results(pars)

unl = res.get_cmb_power_spectra(raw_cl=True, spectra=['unlensed_scalar'])['unlensed_scalar']
ell = np.arange(len(unl))
Dl = unl[:, 0] * ell * (ell + 1) / (2*np.pi) * 1e12

# 自動峰檢測 (unlensed)
s = gaussian_filter1d(Dl, sigma=3)
pk, _ = find_peaks(s, distance=30)
print("unlensed 自動峰:", [int(ell[p]) for p in pk[:8]])
print("unlensed 自動峰高度:", [f"{Dl[p]:.0f}" for p in pk[:8]])

# 峰位: 221, 536, 814, 1129, 1427 (CAMB 自動)
# 對比 IDCM: 220, 537, 810, 1014, 1199, 1340, 1412
# 注意: CAMB 得 5 個峰 (814 之後係 1129, 1427), IDCM 有 7 個
# → CAMB unlensed 峰 4 = 1129 (IDCM 話 1014), 峰 5 = 1427 (IDCM 話 1199/1340/1412)
print()
print("關鍵: CAMB unlensed 只 detect 5 個峰 (221, 536, 814, 1129, 1427)")
print("IDCM 預測 7 個峰 (220, 537, 810, 1014, 1199, 1340, 1412)")
print("→ 高 ℓ 區 (1100-1450) 峰結構同 IDCM 有分歧 (已知 O9 問題)")
print()

# 用自動峰做簡併對:
# P_1 = (536, 814), P_2 = (1129, ?), P_3 = ?
# 自動峰得 5 個 → 只有 P_1 完整, P_2 得一個峰
auto_pk = [int(ell[p]) for p in pk[:6]]
auto_D = [Dl[p] for p in pk[:6]]
print("自動峰簡併對分析:")
D1 = auto_D[1]  # 第一個峰 (221 之後)
P1_a = (auto_D[2] + auto_D[3])/2  # (536, 814)
print(f"  P_1 = ({auto_D[2]:.0f}+{auto_D[3]:.0f})/2 / {D1:.0f} = {P1_a/D1:.4f}")
P1_g = math.sqrt(auto_D[2]*auto_D[3]) / D1
print(f"  P_1 幾何 = sqrt({auto_D[2]:.0f}×{auto_D[3]:.0f})/{D1:.0f} = {P1_g:.4f}")
print(f"  理論 3ε = {3*eps:.4f}")
print()

# IDCM 峰位讀數 (每對兩個峰分開)
print("IDCM 峰位讀數 (unlensed) — 每對內部分析:")
A = {}
idcm = {1: 220, 2: 537, 3: 810, 4: 1014, 5: 1199, 6: 1340, 7: 1412}
for m, lp in idcm.items():
    idx = np.argmin(np.abs(ell-lp))
    A[m] = Dl[idx]/Dl[np.argmin(np.abs(ell-220))]
    print(f"  m={m}: ℓ={lp} → A={A[m]:.4f}")

print()
print("每對: 算術 vs 幾何 vs 理論:")
S_fib = {1: 1.0, 2: phi_inv**2, 3: 2*phi_inv**4}
for m in range(1, 4):
    ar = (A[2*m] + A[2*m+1])/2
    gm = math.sqrt(A[2*m]*A[2*m+1])
    th = 3*eps*S_fib[m]
    print(f"  P_{m}: 算術={ar:.4f} | 幾何={gm:.4f} | 理論={th:.4f}")
    print(f"    算術偏差 {(ar-th)/th*100:+.2f}% | 幾何偏差 {(gm-th)/th*100:+.2f}%")
