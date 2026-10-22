#!/usr/bin/env python3
"""
O10 01: CAMB 峰高度提取 (Planck 2018 參數)
==========================================
讀取 raw + lensed D_ℓ 喺 IDCM 峰位 (220/537/810/1014) 嘅高度,
以及自動峰檢測, 做 IDCM 峰幅度公式嘅精確基準。
"""
import numpy as np
import camb
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
import json, os

OUT = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT, exist_ok=True)

# Planck 2018 fiducial
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, tau=0.0544)
pars.set_dark_energy()
pars.InitPower.set_params(ns=0.9649, As=2e-09)
pars.set_for_lmax(2600)

results = camb.get_results(pars)

# CAMB 2.0: CMB_unit='muK' 直接返回 D_ℓ (μK²), columns = TT, EE, BB, TE
raw = results.get_cmb_power_spectra(raw_cl=True, spectra=['unlensed_scalar'])['unlensed_scalar']
lens = results.get_cmb_power_spectra(spectra=['total'], CMB_unit='muK')['total']

def to_Dl(spectrum, tt_col=0, is_raw=True):
    ell = np.arange(len(spectrum))
    if is_raw:
        # raw_cl=True 時 spectrum 係 C_ℓ, 要轉 D_ℓ (μK²)
        Dl = spectrum[:, tt_col] * ell * (ell + 1) / (2 * np.pi) * 1e12
    else:
        # CMB_unit='muK' 已係 D_ℓ μK²
        Dl = spectrum[:, tt_col]
    return ell, Dl

ell_r, Dl_r = to_Dl(raw, 0, is_raw=True)
ell_l, Dl_l = to_Dl(lens, 0, is_raw=False)  # CMB_unit='muK' 已係 D_ℓ μK²

# IDCM 峰位
idcm_peaks = {1: 220, 2: 537, 3: 810, 4: 1014, 5: 1199, 6: 1340, 7: 1412}

def read_height(ell, Dl, l_target, window=25):
    """喺 l_target ± window 內讀最高點"""
    idx = np.where(np.abs(ell - l_target) <= window)[0]
    if len(idx) == 0:
        return None, None
    j = idx[np.argmax(Dl[idx])]
    return int(ell[j]), float(Dl[j])

print("=" * 78)
print("CAMB D_ℓ 峰高度 (Planck 2018 參數)")
print("=" * 78)
print(f"{'峰':>3} | {'IDCM ℓ':>7} | {'raw ℓ':>6} {'raw D_ℓ':>10} | {'lens ℓ':>7} {'lens D_ℓ':>10}")
print("-" * 78)

heights = {"raw": {}, "lens": {}}
for m, lp in idcm_peaks.items():
    lr, hr = read_height(ell_r, Dl_r, lp)
    ll_, hl = read_height(ell_l, Dl_l, lp)
    heights["raw"][m] = {"idcm_ell": lp, "found_ell": lr, "Dl": hr}
    heights["lens"][m] = {"idcm_ell": lp, "found_ell": ll_, "Dl": hl}
    lr_s = f"{lr:>6}" if lr else "   -- "
    ll_s = f"{ll_:>7}" if ll_ else "    -- "
    hr_s = f"{hr:>10.1f}" if hr else "        --"
    hl_s = f"{hl:>10.1f}" if hl else "        --"
    print(f"{m:>3} | {lp:>7} | {lr_s} {hr_s} | {ll_s} {hl_s}")

# 自動峰檢測 (平滑後) — 確認峰 1-4 位置
smooth = gaussian_filter1d(Dl_r, sigma=3)
pk, _ = find_peaks(smooth, distance=30)
print("\n自動峰檢測 (raw, sigma=3):", [int(ell_r[p]) for p in pk[:6]])

# 峰高度比率
print("\n峰高度比率 A_m/A₁:")
for m in range(2, 8):
    if m in heights["raw"] and heights["raw"][1]["Dl"]:
        r_raw = heights["raw"][m]["Dl"] / heights["raw"][1]["Dl"]
        r_lens = heights["lens"][m]["Dl"] / heights["lens"][1]["Dl"]
        print(f"  m={m}: raw {r_raw:.4f} | lens {r_lens:.4f}")

# 文獻 Planck 值 (SESSION_START)
lit = {1: 5700, 2: 2600, 3: 1400, 4: 800}
print("\n文獻 Planck 2018 D_ℓ:", lit)
print("文獻比率:", {m: round(lit[m]/lit[1], 4) for m in range(2, 5)})

# 儲存
out = {
    "planck_params": {"H0": 67.36, "ombh2": 0.02237, "omch2": 0.1200, "tau": 0.0544, "ns": 0.9649, "As": 2.099e-09},
    "heights": heights,
    "literature": lit,
}
with open(os.path.join(OUT, "camb_peak_heights.json"), "w") as f:
    json.dump(out, f, indent=2)
print("\n已儲存 -> data/camb_peak_heights.json")
