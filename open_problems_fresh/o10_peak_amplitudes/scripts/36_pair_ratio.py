#!/usr/bin/env python3
"""
O10 36: 簡併對內部比率 — 2/3 結構發現
======================================
峰 4/5 比 = 0.6667 = 2/3 (unlensed + lensed 一致)
峰 2/3 比 = 0.992 ≈ 1 (完美簡併)

內部比率結構:
  P₁ (峰2,3): 比 ≈ 1 (真簡併)
  P₂ (峰4,5): 比 = 2/3 精確

檢查: 峰 6,7 比?
  (之前 CAMB unlensed: 峰6=0.0646, 峰7=0.0607 → 比 0.94)
"""
import camb
import numpy as np, math

phi = (1 + 5**0.5) / 2
eps = phi**-1/4

pars = camb.CAMBparams()
pars.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, tau=0.0544)
pars.InitPower.set_params(ns=0.9649, As=2.1e-9)
pars.set_for_lmax(3000)
res = camb.get_results(pars)
unl = res.get_cmb_power_spectra(raw_cl=True, spectra=['unlensed_scalar'])['unlensed_scalar']
ell = np.arange(len(unl))
Dl_unl = unl[:, 0] * ell * (ell + 1) / (2*np.pi) * 1e12
lens = res.get_cmb_power_spectra(spectra=['total'], CMB_unit='muK')['total']
Dl_lens = lens[:, 0]

peaks = {1: 221, 2: 536, 3: 814, 4: 1129, 5: 1419, 6: 1624, 7: 1812}

print("簡併對內部比率 (lensed):")
D1 = Dl_lens[np.argmin(np.abs(ell-221))]
for m, (a, b) in {1: (2,3), 2: (4,5), 3: (6,7)}.items():
    ia = np.argmin(np.abs(ell-peaks[a]))
    ib = np.argmin(np.abs(ell-peaks[b]))
    Aa, Ab = Dl_lens[ia]/D1, Dl_lens[ib]/D1
    r = Aa/Ab
    print(f"  P_{m}: 峰{a}={Aa:.4f}, 峰{b}={Ab:.4f}, 比 = {r:.4f}")

print()
print("候選結構:")
print(f"  2/3 = {2/3:.4f}")
print(f"  φ⁻¹ = {phi**-1:.4f}")
print(f"  3/4 = {0.75:.4f}")
print(f"  5/8 = {5/8:.4f}")
print(f"  √2/2 = {math.sqrt(2)/2:.4f}")

print()
print("峰 4/5 比 = 0.667 ≈ 2/3 → 每對內部有 2:3 結構?")
print("峰 2/3 比 = 0.98 ≈ 1 → 第一對真簡併")
print()
print("2/3 結構可能來源:")
print("  峰4 = 2×γ?, 峰5 = 3×γ? (2:3 比例)")
print("  或者: 峰 4,5 嘅「路徑重數」係 2,3 (唔係對平均 F₂=1)")

# 檢查: 如果用 峰4:峰5 = 2:3, 咁 P₂ 平均 = 2.5 units?
# P₂_th = 3εφ⁻² = 0.1771
# 峰4 = 2×0.1771/2.5 = 0.1417, 峰5 = 3×0.1771/2.5 = 0.2125
# 實際: 峰4 = 0.1856 (Planck 1013), 峰5 = 0.2143 (Planck 1121)
print()
print("如果峰4:峰5 = 2:3 (比例):")
P2 = 3*eps*phi**-2
f4 = 2*P2/2.5
f5 = 3*P2/2.5
print(f"  峰4 = 2×P₂/2.5 = {f4:.4f}, 峰5 = 3×P₂/2.5 = {f5:.4f}")
print(f"  Planck 峰4 (1013) = 0.1856, 峰5 (1121) = 0.2143")
print(f"  偏差: 峰4 {(0.1856-f4)/f4*100:+.1f}%, 峰5 {(0.2143-f5)/f5*100:+.1f}%")
