#!/usr/bin/env python3
"""
O10 02: Planck binned 峰高度精確提取 + 文獻對比
================================================
用 Planck 2018 官方 binned TT 譜 (C_ℓ × 1e12) 提取真實峰高度,
重新審視文獻 A_m/A₁ 值 (5700/2600/1400/800 可能係近似)。
"""
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
import json, os

DATA = os.path.join(os.path.dirname(__file__), "..", "..", "o9_high_ell_peaks", "data", "planck_tt.txt")
OUT = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT, exist_ok=True)

data = np.loadtxt(DATA)
l, val, err = data[:,0], data[:,1], data[:,2]

# Planck binned: val = C_ℓ × 1e12 → D_ℓ = val × ℓ(ℓ+1)/2π (μK²)
Dl = val * l*(l+1)/(2*np.pi)
Dl_err = err * l*(l+1)/(2*np.pi)

# 平滑峰檢測
s = gaussian_filter1d(Dl, sigma=1.5)
pk, _ = find_peaks(s, distance=25)

print("=" * 70)
print("Planck 2018 binned TT 峰 (真實數據)")
print("=" * 70)
print(f"{'m':>3} | {'ℓ':>6} | {'D_ℓ':>8} | {'誤差':>6} | {'A_m/A₁':>8}")
print("-" * 70)

peaks = {}
for i, p in enumerate(pk):
    m = i + 1
    peaks[m] = {"ell": float(l[p]), "Dl": float(Dl[p]), "err": float(Dl_err[p])}
    ratio = Dl[p]/Dl[pk[0]] if m > 1 else 1.0
    print(f"{m:>3} | {l[p]:>6.0f} | {Dl[p]:>8.0f} | {Dl_err[p]:>6.0f} | {ratio:>8.4f}")

# IDCM 峰位讀數 (唔用自動峰, 用 IDCM 預測位)
print()
print("IDCM 峰位讀數:")
idcm_peaks = {1: 220, 2: 537, 3: 810, 4: 1014, 5: 1199, 6: 1340, 7: 1412}
print(f"{'m':>3} | {'IDCM ℓ':>7} | {'實際 ℓ':>6} | {'D_ℓ':>8} | {'A_m/A₁':>8}")
print("-" * 55)
idcm_read = {}
for m, lp in idcm_peaks.items():
    idx = np.argmin(np.abs(l - lp))
    D = Dl[idx]
    idcm_read[m] = {"ell": float(l[idx]), "Dl": float(D), "err": float(Dl_err[idx])}
    ratio = D / Dl[np.argmin(np.abs(l - 220))] if m > 1 else 1.0
    print(f"{m:>3} | {lp:>7} | {l[idx]:>6.0f} | {D:>8.0f} | {ratio:>8.4f}")

# 文獻值對比
print()
print("文獻 vs Planck binned:")
lit = {1: 5700, 2: 2600, 3: 1400, 4: 800}
for m in range(1, 5):
    if m in peaks:
        lit_r = lit[m]/lit[1]
        real_r = peaks[m]["Dl"]/peaks[1]["Dl"]
        print(f"  m={m}: 文獻 D={lit[m]} (A/A₁={lit_r:.4f}) | Planck binned D={peaks[m]['Dl']:.0f} (A/A₁={real_r:.4f}) | 差異 {(real_r-lit_r)/lit_r*100:+.1f}%")

# 儲存
out = {"peaks": peaks, "idcm_read": idcm_read, "literature": lit}
with open(os.path.join(OUT, "planck_binned_peaks.json"), "w") as f:
    json.dump(out, f, indent=2)
print("\n已儲存 -> data/planck_binned_peaks.json")
