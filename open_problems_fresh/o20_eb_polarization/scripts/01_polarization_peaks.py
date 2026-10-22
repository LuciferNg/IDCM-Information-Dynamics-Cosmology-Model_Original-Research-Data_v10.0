#!/usr/bin/env python3
"""
O20: E/B 極化峰位置結構推導
=============================
核心假設: 極化峰 = TT 峰之間嘅 π/2 相移 (midpoint)
IDCM: ℓ_E(m) = (ℓ_T(m) + ℓ_T(m+1))/2

測試:
1. CAMB 生成 TT/TE/EE 譜 → 峰檢測
2. 中點假設驗證 (π/2 相移)
3. 結構公式: ℓ_E = 44×(M−C(9−m,2)) + ((m−1)×9 mod 25) + Δℓ_m/2
4. Planck binned TE/EE → 峰檢測
5. ACT DR6 TE/EE → 峰檢測
6. SPT-3G D1 TE/EE → 峰檢測
7. B lensing 峰分析
"""
import numpy as np
import math as _m
import os, sys
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

# ── 路徑 ──
O9_DATA = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o9_high_ell_peaks/data"
O20_DIR = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o20_eb_polarization"
OUT_DIR = os.path.join(O20_DIR, "data")
os.makedirs(OUT_DIR, exist_ok=True)

# ── IDCM 常數 ──
phi = (1 + 5**0.5)/2
F = [0, 1]
for i in range(2, 15): F.append(F[-1] + F[-2])  # F[1]=1, F[2]=1, F[3]=2, F[4]=3, F[5]=5, F[6]=8, F[7]=13, F[8]=21
L = [2, 1, 3, 4, 7, 11, 18, 29]  # Lucas: L₀=2, L₁=1, L₂=3, L₃=4, L₄=7, L₅=11
Nd = 44  # 2N_d = K_Chain 44-site
M = 33   # K_Tree depth

def idcm_tt(m):
    """IDCM TT 峰位公式 (含 m=5 fix)"""
    if m == 5:
        return 44 * (33 - F[6]) + F[8]  # 1121
    C = _m.comb(9 - m, 2) if 9 - m >= 2 else 0
    return 44 * (M - C) + (((m - 1) * 9) % 25)

def idcm_tt_predictions():
    """IDCM TT 峰位 m=1..7"""
    return {m: idcm_tt(m) for m in range(1, 8)}

# ══════════════════════════════════════════════
# 1. CAMB 生成 TT/TE/EE 譜
# ══════════════════════════════════════════════
print("=" * 80)
print("O20: E/B 極化峰位置結構推導")
print("=" * 80)

print("\n" + "-" * 80)
print("1. CAMB 2.0.1 TT/TE/EE 譜生成 + 峰檢測")
print("-" * 80)

import camb
# Planck 2018 fiducial
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, tau=0.0544)
pars.InitPower.set_params(ns=0.9649, As=2.1e-9)
pars.set_for_lmax(2500)

results = camb.get_results(pars)
# Raw (unlensed) spectra
raw = results.get_cmb_power_spectra(raw_cl=True)
# Lensed spectra
lensed = results.get_cmb_power_spectra(spectra=['total'], CMB_unit='muK')

# 提取譜
lmax = 2500
ell = np.arange(lmax + 1)

# Raw spectra: columns = TT, EE, BB, TE (CAMB 2.0 returns (lmax+1, 4) array)
raw_tt = raw['unlensed_scalar'][:lmax+1, 0]  # raw TT C_ℓ (K²)
raw_ee = raw['unlensed_scalar'][:lmax+1, 1]  # raw EE C_ℓ (K²)
raw_bb = raw['unlensed_scalar'][:lmax+1, 2]  # raw BB (tensor=0)
raw_te = raw['unlensed_scalar'][:lmax+1, 3]  # raw TE C_ℓ (K²)

# Lensed spectra (D_ℓ in μK²) — already D_ℓ format
lens_tt = lensed['total'][:lmax+1, 0]  # lensed TT D_ℓ μK²
lens_ee = lensed['total'][:lmax+1, 1]  # lensed EE D_ℓ μK²
lens_bb = lensed['total'][:lmax+1, 2]  # lensed BB D_ℓ μK² (lensing B)
lens_te = lensed['total'][:lmax+1, 3]  # lensed TE D_ℓ μK²

# Convert raw C_ℓ to D_ℓ for peak detection
raw_tt_dl = raw_tt * ell * (ell + 1) / (2 * np.pi) * 1e12  # K² → μK²
raw_ee_dl = raw_ee * ell * (ell + 1) / (2 * np.pi) * 1e12
raw_te_dl = raw_te * ell * (ell + 1) / (2 * np.pi) * 1e12

# 峰檢測函數
def detect_peaks(ell, d_ell, sigma=3, min_dist=15, min_height=50, invert=False):
    """檢測 C_ℓ 譜峰位置"""
    v = -d_ell if invert else d_ell
    smooth = gaussian_filter1d(v, sigma=sigma)
    peaks, props = find_peaks(smooth, distance=min_dist, height=min_height)
    # 精確位置: 原始資料中嘅局部極大 (未平滑)
    refined = []
    for p in peaks:
        window = slice(max(0, p-3), min(len(ell), p+3))
        if invert:
            idx = np.argmin(d_ell[window])
        else:
            idx = np.argmax(d_ell[window])
        refined.append(ell[window.start + idx])
    return np.array(refined), np.array(peaks), smooth

# ── Raw TT 峰檢測 ──
raw_tt_peaks, raw_tt_idx, _ = detect_peaks(ell, raw_tt_dl, sigma=3, min_dist=30, min_height=100)
# 只取 ℓ>50
raw_tt_peaks = raw_tt_peaks[raw_tt_peaks > 50]
print(f"\n   CAMB raw TT 峰: {[f'{l:.0f}' for l in raw_tt_peaks]}")

# ── Raw EE 峰檢測 ──
raw_ee_peaks, raw_ee_idx, _ = detect_peaks(ell, raw_ee_dl, sigma=3, min_dist=30, min_height=10)
raw_ee_peaks = raw_ee_peaks[raw_ee_peaks > 50]
print(f"   CAMB raw EE 峰: {[f'{l:.0f}' for l in raw_ee_peaks]}")

# ── Raw TE 峰檢測 ──
# TE 有正負交替: 峰 = 正極大 + 負極小 (絕對值)
raw_te_peaks, raw_te_idx, _ = detect_peaks(ell, np.abs(raw_te_dl), sigma=3, min_dist=30, min_height=5)
raw_te_peaks = raw_te_peaks[raw_te_peaks > 50]
print(f"   CAMB raw TE 峰: {[f'{l:.0f}' for l in raw_te_peaks]}")

# ── Lensed TT 峰檢測 ──
lens_tt_peaks, lens_tt_idx, _ = detect_peaks(ell, lens_tt, sigma=3, min_dist=30, min_height=100)
lens_tt_peaks = lens_tt_peaks[lens_tt_peaks > 50]
print(f"   CAMB lensed TT 峰: {[f'{l:.0f}' for l in lens_tt_peaks]}")

# ── Lensed EE 峰檢測 ──
lens_ee_peaks, lens_ee_idx, _ = detect_peaks(ell, lens_ee, sigma=3, min_dist=30, min_height=10)
lens_ee_peaks = lens_ee_peaks[lens_ee_peaks > 50]
print(f"   CAMB lensed EE 峰: {[f'{l:.0f}' for l in lens_ee_peaks]}")

# ── Lensed BB 峰檢測 (lensing B) ──
lens_bb_peaks, lens_bb_idx, _ = detect_peaks(ell, lens_bb, sigma=3, min_dist=30, min_height=0.1)
lens_bb_peaks = lens_bb_peaks[lens_bb_peaks > 50]
print(f"   CAMB lensed BB 峰: {[f'{l:.0f}' for l in lens_bb_peaks]}")

# ── Lensed TE 峰檢測 ──
lens_te_peaks, lens_te_idx, _ = detect_peaks(ell, np.abs(lens_te), sigma=3, min_dist=30, min_height=5)
lens_te_peaks = lens_te_peaks[lens_te_peaks > 50]
print(f"   CAMB lensed TE 峰: {[f'{l:.0f}' for l in lens_te_peaks]}")

# ══════════════════════════════════════════════
# 2. 中點假設驗證 (π/2 相移)
# ══════════════════════════════════════════════
print("\n" + "-" * 80)
print("2. π/2 相移假設: EE 峰 = 相鄰 TT 峰中點?")
print("-" * 80)

tt_pred = idcm_tt_predictions()
print(f"\n   IDCM TT 峰 (m=1..7):")
for m in range(1, 8):
    print(f"     m={m}: ℓ={tt_pred[m]}")

# EE 中點預測
print(f"\n   EE 中點預測 (IDCM):")
ee_mid_pred = {}
for m in range(1, 7):
    mid = (tt_pred[m] + tt_pred[m+1]) / 2.0
    ee_mid_pred[m] = mid
    print(f"     EE_{m} = (TT{m}+TT{m+1})/2 = ({tt_pred[m]}+{tt_pred[m+1]})/2 = {mid:.1f}")

# 撈 CAMB EE 峰匹配 EE 中點
print(f"\n   CAMB raw EE 峰 vs IDCM 中點預測:")
for m in range(1, 7):
    mid = ee_mid_pred[m]
    if len(raw_ee_peaks) > 0:
        j = np.argmin(np.abs(raw_ee_peaks - mid))
        dev = (raw_ee_peaks[j] - mid) / mid * 100
        match = "✅" if abs(dev) < 2 else "🟡" if abs(dev) < 5 else "🔴"
        print(f"     EE_{m}: IDCM {mid:.1f} vs CAMB {raw_ee_peaks[j]:.0f} (dev={dev:+.2f}%) {match}")

print(f"\n   CAMB lensed EE 峰 vs IDCM 中點預測:")
for m in range(1, 7):
    mid = ee_mid_pred[m]
    if len(lens_ee_peaks) > 0:
        j = np.argmin(np.abs(lens_ee_peaks - mid))
        dev = (lens_ee_peaks[j] - mid) / mid * 100
        match = "✅" if abs(dev) < 2 else "🟡" if abs(dev) < 5 else "🔴"
        print(f"     EE_{m}: IDCM {mid:.1f} vs CAMBlens {lens_ee_peaks[j]:.0f} (dev={dev:+.2f}%) {match}")

# TE 中點預測 (TE 峰同 EE 峰位置相近)
print(f"\n   CAMB raw TE 峰 vs IDCM 中點預測:")
for m in range(1, 7):
    mid = ee_mid_pred[m]
    if len(raw_te_peaks) > 0:
        j = np.argmin(np.abs(raw_te_peaks - mid))
        dev = (raw_te_peaks[j] - mid) / mid * 100
        match = "✅" if abs(dev) < 2 else "🟡" if abs(dev) < 5 else "🔴"
        print(f"     TE_{m}: IDCM {mid:.1f} vs CAMB {raw_te_peaks[j]:.0f} (dev={dev:+.2f}%) {match}")

# ══════════════════════════════════════════════
# 3. Planck binned TE/EE 峰檢測
# ══════════════════════════════════════════════
print("\n" + "-" * 80)
print("3. Planck 2018 binned TE/EE 峰檢測")
print("-" * 80)

def load_planck_binned(filename):
    """Load Planck binned data: ℓ, C_ℓ, σ"""
    cols = np.loadtxt(os.path.join(O9_DATA, filename))
    ell_b = cols[:, 0]
    c_ell = cols[:, 1]
    d_ell = c_ell * ell_b * (ell_b + 1) / (2 * np.pi)  # C_ℓ μK² → D_ℓ μK²
    return ell_b, c_ell, d_ell

# Planck EE
planck_ee_ell, planck_ee_c, planck_ee_d = load_planck_binned('planck_ee.txt')
planck_ee_peaks, _, _ = detect_peaks(planck_ee_ell, planck_ee_d, sigma=2, min_dist=20, min_height=5)
planck_ee_peaks = planck_ee_peaks[planck_ee_peaks > 50]
print(f"\n   Planck binned EE 峰: {[f'{l:.0f}' for l in planck_ee_peaks]}")

# Planck TE (absolute value for peak detection)
planck_te_ell, planck_te_c, planck_te_d = load_planck_binned('planck_te.txt')
planck_te_peaks, _, _ = detect_peaks(planck_te_ell, np.abs(planck_te_d), sigma=2, min_dist=20, min_height=10)
planck_te_peaks = planck_te_peaks[planck_te_peaks > 50]
print(f"   Planck binned TE 峰: {[f'{l:.0f}' for l in planck_te_peaks]}")

# Planck TT
planck_tt_ell, planck_tt_c, planck_tt_d = load_planck_binned('planck_tt.txt')
planck_tt_peaks, _, _ = detect_peaks(planck_tt_ell, planck_tt_d, sigma=2, min_dist=20, min_height=100)
planck_tt_peaks = planck_tt_peaks[planck_tt_peaks > 50]
print(f"   Planck binned TT 峰: {[f'{l:.0f}' for l in planck_tt_peaks]}")

# Planck EE vs IDCM 中點
print(f"\n   Planck EE 峰 vs IDCM 中點預測:")
for m in range(1, 7):
    mid = ee_mid_pred[m]
    if len(planck_ee_peaks) > 0:
        j = np.argmin(np.abs(planck_ee_peaks - mid))
        dev = (planck_ee_peaks[j] - mid) / mid * 100
        match = "✅" if abs(dev) < 2 else "🟡" if abs(dev) < 5 else "🔴"
        print(f"     EE_{m}: IDCM {mid:.1f} vs Planck {planck_ee_peaks[j]:.0f} (dev={dev:+.2f}%) {match}")

print(f"\n   Planck TE 峰 vs IDCM 中點預測:")
for m in range(1, 7):
    mid = ee_mid_pred[m]
    if len(planck_te_peaks) > 0:
        j = np.argmin(np.abs(planck_te_peaks - mid))
        dev = (planck_te_peaks[j] - mid) / mid * 100
        match = "✅" if abs(dev) < 2 else "🟡" if abs(dev) < 5 else "🔴"
        print(f"     TE_{m}: IDCM {mid:.1f} vs Planck {planck_te_peaks[j]:.0f} (dev={dev:+.2f}%) {match}")

# ══════════════════════════════════════════════
# 4. ACT DR6 TE/EE 峰檢測
# ══════════════════════════════════════════════
print("\n" + "-" * 80)
print("4. ACT DR6 TE/EE 峰檢測")
print("-" * 80)

from astropy.io import fits
hdul = fits.open(os.path.join(O9_DATA, 'act_dr6_cmb_sacc.fits'))
cl00 = hdul['data:cl_00'].data  # TT
cl0e = hdul['data:cl_0e'].data  # TE
clee = hdul['data:cl_ee'].data  # EE

act_tt_peaks, _, _ = detect_peaks(cl00['ell'], cl00['value'], sigma=2, min_dist=20, min_height=50)
act_te_peaks, _, _ = detect_peaks(cl0e['ell'], np.abs(cl0e['value']), sigma=2, min_dist=20, min_height=5)
act_ee_peaks, _, _ = detect_peaks(clee['ell'], clee['value'], sigma=2, min_dist=20, min_height=5)

print(f"\n   ACT DR6 TT 峰: {[f'{l:.0f}' for l in act_tt_peaks]}")
print(f"   ACT DR6 TE 峰: {[f'{l:.0f}' for l in act_te_peaks]}")
print(f"   ACT DR6 EE 峰: {[f'{l:.0f}' for l in act_ee_peaks]}")

print(f"\n   ACT DR6 EE 峰 vs IDCM 中點預測:")
for m in range(1, 7):
    mid = ee_mid_pred[m]
    if len(act_ee_peaks) > 0:
        j = np.argmin(np.abs(act_ee_peaks - mid))
        dev = (act_ee_peaks[j] - mid) / mid * 100
        match = "✅" if abs(dev) < 2 else "🟡" if abs(dev) < 5 else "🔴"
        print(f"     EE_{m}: IDCM {mid:.1f} vs ACT {act_ee_peaks[j]:.0f} (dev={dev:+.2f}%) {match}")

# ══════════════════════════════════════════════
# 5. SPT-3G D1 TE/EE 峰檢測
# ══════════════════════════════════════════════
print("\n" + "-" * 80)
print("5. SPT-3G D1 TE/EE 峰檢測")
print("-" * 80)

# 讀 window functions
win = np.loadtxt(os.path.join(O9_DATA, 'spt_tt150_windows.txt'))
ell_w = win[:, 0]
W = win[:, 1:]
bin_centers = np.array([(ell_w * W[:, b]).sum() / W[:, b].sum() for b in range(W.shape[1])])

# 讀 SPT-3G bdp
bdp = np.loadtxt(os.path.join(O9_DATA, 'spt3g_tne_bdp.txt'))
# Spectrum structure: 21 spectra
# TT 90x90(52), TE 90x90(72), EE 90x90(72), TT 90x150(52), TE 90x150(72),
# TE 150x90(72), EE 90x150(72), TT 90x220(52), TE 90x220(72), TE 220x90(72),
# EE 90x220(72), TT 150x150(52), TE 150x150(72), EE 150x150(72), TT 150x220(52),
# TE 150x220(72), TE 220x150(72), EE 150x220(72), TT 220x220(52), TE 220x220(72),
# EE 220x220(72)
specs = [
    ('TT 90x90',52), ('TE 90x90',72), ('EE 90x90',72), ('TT 90x150',52),
    ('TE 90x150',72), ('TE 150x90',72), ('EE 90x150',72), ('TT 90x220',52),
    ('TE 90x220',72), ('TE 220x90',72), ('EE 90x220',72), ('TT 150x150',52),
    ('TE 150x150',72), ('EE 150x150',72), ('TT 150x220',52), ('TE 150x220',72),
    ('TE 220x150',72), ('EE 150x220',72), ('TT 220x220',52), ('TE 220x220',72),
    ('EE 220x220',72),
]
data = {}
idx = 0
for name, n in specs:
    data[name] = bdp[idx:idx+n]
    idx += n

# 150x150 頻譜 (最高 S/N 嘅極化頻譜)
def detect_spt_peaks(values, bin_c, min_height=5):
    """SPT bin 峰檢測 (直接鄰居比較)"""
    peaks = []
    for i in range(1, len(values)-1):
        if values[i] > values[i-1] and values[i] > values[i+1] and values[i] > min_height:
            peaks.append(bin_c[i])
    return np.array(peaks)

spt_tt150 = data['TT 150x150']
spt_te150 = data['TE 150x150']
spt_ee150 = data['EE 150x150']

spt_tt_peaks = detect_spt_peaks(spt_tt150, bin_centers, min_height=100)
spt_te_peaks = detect_spt_peaks(np.abs(spt_te150), bin_centers, min_height=5)
spt_ee_peaks = detect_spt_peaks(spt_ee150, bin_centers, min_height=5)

print(f"\n   SPT-3G TT150 峰: {[f'{l:.0f}' for l in spt_tt_peaks]}")
print(f"   SPT-3G TE150 峰: {[f'{l:.0f}' for l in spt_te_peaks]}")
print(f"   SPT-3G EE150 峰: {[f'{l:.0f}' for l in spt_ee_peaks]}")

print(f"\n   SPT-3G EE150 峰 vs IDCM 中點預測:")
for m in range(1, 7):
    mid = ee_mid_pred[m]
    if len(spt_ee_peaks) > 0:
        j = np.argmin(np.abs(spt_ee_peaks - mid))
        dev = (spt_ee_peaks[j] - mid) / mid * 100
        match = "✅" if abs(dev) < 2 else "🟡" if abs(dev) < 5 else "🔴"
        print(f"     EE_{m}: IDCM {mid:.1f} vs SPT {spt_ee_peaks[j]:.0f} (dev={dev:+.2f}%) {match}")

print(f"\n   SPT-3G TE150 峰 vs IDCM 中點預測:")
for m in range(1, 7):
    mid = ee_mid_pred[m]
    if len(spt_te_peaks) > 0:
        j = np.argmin(np.abs(spt_te_peaks - mid))
        dev = (spt_te_peaks[j] - mid) / mid * 100
        match = "✅" if abs(dev) < 2 else "🟡" if abs(dev) < 5 else "🔴"
        print(f"     TE_{m}: IDCM {mid:.1f} vs SPT {spt_te_peaks[j]:.0f} (dev={dev:+.2f}%) {match}")

# ══════════════════════════════════════════════
# 6. 結構公式候選
# ══════════════════════════════════════════════
print("\n" + "-" * 80)
print("6. 極化峰結構公式候選")
print("-" * 80)

# 候選 A: 簡單中點
# ℓ_E(m) = (ℓ_T(m) + ℓ_T(m+1))/2
print(f"\n   候選 A: ℓ_E(m) = (ℓ_T(m) + ℓ_T(m+1))/2 (π/2 相移)")
for m in range(1, 7):
    mid = ee_mid_pred[m]
    print(f"     m={m}: ℓ_E = {mid:.1f}")

# 候選 B: 基於 K_Chain 相位偏移
# 如果 TT 峰 = 44 × N_int + phase, 極化峰 = 44 × N_int + phase + Δℓ/2
# 但 Δℓ 唔係常數, 所以中點最簡單

# 候選 C: 用結構常數表達
# 如果 44 = 基本角頻率, 極化峰間距可能係 44 × 某常數
print(f"\n   候選 C: EE 峰間距分析")
ee_spacing = np.diff(list(ee_mid_pred.values()))
print(f"     EE 峰間距: {[f'{s:.1f}' for s in ee_spacing]}")
print(f"     平均間距: {np.mean(ee_spacing):.1f}")
print(f"     44 倍數: {[f'{s/44:.2f}' for s in ee_spacing]}")

# ══════════════════════════════════════════════
# 7. B lensing 峰分析
# ══════════════════════════════════════════════
print("\n" + "-" * 80)
print("7. B lensing 峰 (ℓ≈1000)")
print("-" * 80)

# Lensed BB (CAMB)
print(f"\n   CAMB lensed BB 峰: {[f'{l:.0f}' for l in lens_bb_peaks]}")
# B lensing 主峰通常喺 ℓ≈1000
if len(lens_bb_peaks) > 0:
    bb_main = lens_bb_peaks[0] if len(lens_bb_peaks) > 0 else 0
    print(f"   主峰: ℓ≈{bb_main:.0f}")
    # IDCM 對比
    print(f"   IDCM ℓ_sync = 44, 2ℓ_sync = 88, 22ℓ_sync = 968, 23ℓ_sync = 1012")
    print(f"   968 vs {bb_main:.0f} (dev={(bb_main-968)/968*100:+.2f}%)")
    print(f"   1012 vs {bb_main:.0f} (dev={(bb_main-1012)/1012*100:+.2f}%)")

# ══════════════════════════════════════════════
# 8. 總結表
# ══════════════════════════════════════════════
print("\n" + "=" * 80)
print("總結: 極化峰位置 (IDCM 中點預測 vs 多實驗)")
print("=" * 80)

print(f"\n{'EE峰':>8} {'IDCM中點':>10} {'CAMBraw':>8} {'CAMBlen':>8} {'Planck':>8} {'ACT':>8} {'SPT':>8} {'狀態':>6}")
print("-" * 70)
for m in range(1, 7):
    mid = ee_mid_pred[m]
    # 收集各數據源
    best_d = "?"
    best_dev = 999
    for name, peaks in [('CAMBraw', raw_ee_peaks), ('CAMBl', lens_ee_peaks),
                         ('Planck', planck_ee_peaks), ('ACT', act_ee_peaks),
                         ('SPT', spt_ee_peaks)]:
        if len(peaks) > 0:
            j = np.argmin(np.abs(peaks - mid))
            d = peaks[j]
            if abs(d - mid) < best_dev:
                best_dev = abs(d - mid)
                best_d = f"{d:.0f}"
    # 對齊輸出
    raw_s = f"{raw_ee_peaks[np.argmin(np.abs(raw_ee_peaks - mid))]:.0f}" if len(raw_ee_peaks) > 0 else "─"
    lens_s = f"{lens_ee_peaks[np.argmin(np.abs(lens_ee_peaks - mid))]:.0f}" if len(lens_ee_peaks) > 0 else "─"
    p_s = f"{planck_ee_peaks[np.argmin(np.abs(planck_ee_peaks - mid))]:.0f}" if len(planck_ee_peaks) > 0 else "─"
    a_s = f"{act_ee_peaks[np.argmin(np.abs(act_ee_peaks - mid))]:.0f}" if len(act_ee_peaks) > 0 else "─"
    s_s = f"{spt_ee_peaks[np.argmin(np.abs(spt_ee_peaks - mid))]:.0f}" if len(spt_ee_peaks) > 0 else "─"
    # 判定
    devs = []
    for name, peaks, s in [('CAMBraw', raw_ee_peaks, raw_s), ('CAMBl', lens_ee_peaks, lens_s),
                            ('Planck', planck_ee_peaks, p_s), ('ACT', act_ee_peaks, a_s),
                            ('SPT', spt_ee_peaks, s_s)]:
        if s != "─":
            d = float(s) - mid
            devs.append(abs(d)/mid*100)
    status = "✅" if all(d < 2 for d in devs) else "🟡" if any(d < 5 for d in devs) else "🔴"
    if len(devs) == 0: status = "🔴"
    print(f"   EE_{m}  {mid:8.1f}  {raw_s:>8} {lens_s:>8} {p_s:>8} {a_s:>8} {s_s:>8} {status:>6}")

print(f"\n{'TE峰':>8} {'IDCM中點':>10} {'CAMBraw':>8} {'CAMBlen':>8} {'Planck':>8} {'ACT':>8} {'SPT':>8} {'狀態':>6}")
print("-" * 70)
for m in range(1, 7):
    mid = ee_mid_pred[m]
    raw_s = f"{raw_te_peaks[np.argmin(np.abs(raw_te_peaks - mid))]:.0f}" if len(raw_te_peaks) > 0 else "─"
    lens_s = f"{lens_te_peaks[np.argmin(np.abs(lens_te_peaks - mid))]:.0f}" if len(lens_te_peaks) > 0 else "─"
    p_s = f"{planck_te_peaks[np.argmin(np.abs(planck_te_peaks - mid))]:.0f}" if len(planck_te_peaks) > 0 else "─"
    a_s = f"{act_te_peaks[np.argmin(np.abs(act_te_peaks - mid))]:.0f}" if len(act_te_peaks) > 0 else "─"
    s_s = f"{spt_te_peaks[np.argmin(np.abs(spt_te_peaks - mid))]:.0f}" if len(spt_te_peaks) > 0 else "─"
    devs = []
    for s in [raw_s, lens_s, p_s, a_s, s_s]:
        if s != "─":
            d = float(s) - mid
            devs.append(abs(d)/mid*100)
    status = "✅" if all(d < 2 for d in devs) else "🟡" if any(d < 5 for d in devs) else "🔴"
    if len(devs) == 0: status = "🔴"
    print(f"   TE_{m}  {mid:8.1f}  {raw_s:>8} {lens_s:>8} {p_s:>8} {a_s:>8} {s_s:>8} {status:>6}")

# 保存結果
import json
results = {
    'ee_mid_pred': {str(m): float(v) for m, v in ee_mid_pred.items()},
    'camb_raw_ee_peaks': [float(v) for v in raw_ee_peaks],
    'camb_lensed_ee_peaks': [float(v) for v in lens_ee_peaks],
    'camb_raw_te_peaks': [float(v) for v in raw_te_peaks],
    'camb_lensed_te_peaks': [float(v) for v in lens_te_peaks],
    'planck_ee_peaks': [float(v) for v in planck_ee_peaks],
    'planck_te_peaks': [float(v) for v in planck_te_peaks],
    'act_ee_peaks': [float(v) for v in act_ee_peaks],
    'act_te_peaks': [float(v) for v in act_te_peaks],
    'spt_ee_peaks': [float(v) for v in spt_ee_peaks],
    'spt_te_peaks': [float(v) for v in spt_te_peaks],
    'camb_lensed_bb_peaks': [float(v) for v in lens_bb_peaks],
}
with open(os.path.join(OUT_DIR, 'polarization_peaks.json'), 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n   結果已保存到: {os.path.join(OUT_DIR, 'polarization_peaks.json')}")
print("\n★ 完成!")