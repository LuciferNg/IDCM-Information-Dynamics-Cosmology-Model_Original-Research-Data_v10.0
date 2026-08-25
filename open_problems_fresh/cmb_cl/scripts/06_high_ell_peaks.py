#!/usr/bin/env python3
"""
CMB C_ℓ 開放位: 高 ℓ 峰 m=5,6,7 驗證 (CAMB raw)
==================================================
IDCM 公式: ℓ_m = 44×(M−C(9−m,2)) + ((m−1)×9 mod 25)
m=5: 44×(33−C(4,2)) + (4×9 mod 25) = 44×27 + 11 = 1199
m=6: 44×(33−C(3,2)) + (5×9 mod 25) = 44×30 + 20 = 1340
m=7: 44×(33−C(2,2)) + (6×9 mod 25) = 44×32 + 4  = 1412

用 CAMB 2.0 API (get_cmb_power_spectra(pars) + total)
"""
import numpy as np
import camb
import math as _m

# Planck 2018 參數
H0 = 67.36
pars = camb.CAMBparams()
pars.set_cosmology(H0=H0, ombh2=0.02237, omch2=0.1200, tau=0.0544)
pars.InitPower.set_params(ns=0.9649, As=2.1e-9)
pars.set_for_lmax(3000, lens_potential_accuracy=0)

results = camb.get_results(pars)
# CAMB 2.0: 用 unlensed_scalar (raw 譜, 唔含 lensing 平滑)
powers = results.get_cmb_power_spectra(raw_cl=True)
TT = powers['unlensed_scalar'][:, 0]  # TT spectrum in muK^2
lmax = len(TT) - 1
ell = np.arange(lmax + 1)

# D_l = l(l+1)C_l/2π
Dl = TT * ell * (ell + 1) / (2 * np.pi)

# 峰檢測: 局部極大值 (細 sigma 保留峰位)
from scipy.ndimage import gaussian_filter1d
Dl_smooth = gaussian_filter1d(Dl, sigma=3)

print("=" * 60)
print("CAMB raw C_ℓ 高 ℓ 峰 (900-2000)")
print("=" * 60)

# IDCM 公式
M, Nd = 33, 44
def idcm_peak(m):
    N_int = M - _m.comb(9-m, 2)
    frac = ((m-1)*9) % 25
    return 44*N_int + frac

# 全範圍峰檢測 (300-2000)
peaks = []
for l in range(300, 2000):
    if Dl_smooth[l] > Dl_smooth[l-1] and Dl_smooth[l] > Dl_smooth[l+1]:
        y0, y1, y2 = Dl_smooth[l-1], Dl_smooth[l], Dl_smooth[l+1]
        if y1 > y0 and y1 > y2:
            denom = (y0 - 2*y1 + y2)
            if abs(denom) > 1e-12:
                delta = 0.5 * (y0 - y2) / denom
            else:
                delta = 0
            peaks.append(l + delta)

print(f"偵測到峰: {[f'{p:.0f}' for p in peaks]}")
print()

# IDCM 預測 (m=1..7)
print("IDCM 公式預測:")
for m in range(1, 8):
    pred = idcm_peak(m)
    print(f"  m={m}: ℓ = {pred}")

print()
print("比對 (峰 vs IDCM):")
for m in range(1, 8):
    pred = idcm_peak(m)
    if not peaks:
        continue
    diffs = np.abs(np.array(peaks) - pred)
    idx = np.argmin(diffs)
    closest = peaks[idx]
    dev = abs(closest - pred)/pred*100
    mark = "✅" if dev < 2 else ("🟡" if dev < 5 else "❌")
    print(f"  m={m}: IDCM {pred} vs CAMB {closest:.0f} → {dev:.2f}% {mark}")

# 高 ℓ 區詳細 (m=5,6,7)
print()
print("高 ℓ 區 (1100-1600) 峰:")
high_peaks = [p for p in peaks if 1100 < p < 1600]
print(f"  {[f'{p:.0f}' for p in high_peaks]}")
for m in [5, 6, 7]:
    pred = idcm_peak(m)
    if high_peaks:
        diffs = np.abs(np.array(high_peaks) - pred)
        idx = np.argmin(diffs)
        closest = high_peaks[idx]
        dev = abs(closest - pred)/pred*100
        mark = "✅" if dev < 2 else ("🟡" if dev < 5 else "❌")
        print(f"  m={m}: IDCM {pred} vs CAMB {closest:.0f} → {dev:.2f}% {mark}")

print()
print("⚠️ 誠實記錄: CAMB total 譜含 lensing 平滑, 高 ℓ 峰喺 damping tail 好弱")
print("  m=5,6,7 係 IDCM 外推, 需要 ACT DR4/SPT-3G 原始譜最終驗證")
