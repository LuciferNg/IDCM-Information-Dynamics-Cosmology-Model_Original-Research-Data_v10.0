#!/usr/bin/env python3
"""
O20-B: 極化譜深入分析 — raw EE 譜 + 結構公式推導
==================================================
問題: 
1. CAMB raw EE 峰檢測失敗 (振幅太低) → 改用 log 標度 / 更靈敏方法
2. 中點假設部分匹配但需要更精確嘅結構公式
3. 探索 K_Chain 模式投影到極化嘅結構
"""
import numpy as np
import math as _m
import os
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

O9_DATA = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o9_high_ell_peaks/data"
O20_DIR = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o20_eb_polarization"
OUT_DIR = os.path.join(O20_DIR, "data")

phi = (1 + 5**0.5)/2
F = [0, 1]
for i in range(2, 15): F.append(F[-1]+F[-2])
L = [2, 1, 3, 4, 7, 11, 18, 29]

def idcm_tt(m):
    if m == 5: return 44*(33 - F[6]) + F[8]
    C = _m.comb(9-m, 2) if 9-m >= 2 else 0
    return 44*(33 - C) + (((m-1)*9) % 25)

# ══════════════════════════════════════════════
# 1. CAMB raw EE 深入分析
# ══════════════════════════════════════════════
print("=" * 80)
print("O20-B: 極化譜深入分析")
print("=" * 80)

import camb
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, tau=0.0544)
pars.InitPower.set_params(ns=0.9649, As=2.1e-9)
pars.set_for_lmax(2500)
results = camb.get_results(pars)
raw = results.get_cmb_power_spectra(raw_cl=True)
lmax = 2500
ell = np.arange(lmax+1)

raw_tt = raw['unlensed_scalar'][:lmax+1, 0]
raw_ee = raw['unlensed_scalar'][:lmax+1, 1]
raw_te = raw['unlensed_scalar'][:lmax+1, 3]
raw_bb = raw['unlensed_scalar'][:lmax+1, 2]

# Raw C_ℓ 轉 D_ℓ μK²
raw_tt_dl = raw_tt * ell * (ell+1) / (2*np.pi) * 1e12
raw_ee_dl = raw_ee * ell * (ell+1) / (2*np.pi) * 1e12
raw_te_dl = raw_te * ell * (ell+1) / (2*np.pi) * 1e12

print("\n1. Raw EE 譜分析:")
print(f"   Raw EE D_ℓ 範圍: [{raw_ee_dl[50:2000].min():.4f}, {raw_ee_dl[50:2000].max():.4f}] μK²")
print(f"   Raw TT D_ℓ 範圍: [{raw_tt_dl[50:2000].min():.1f}, {raw_tt_dl[50:2000].max():.1f}] μK²")
print(f"   EE/TT 振幅比: ~{raw_ee_dl[100:2000].max()/raw_tt_dl[100:2000].max()*100:.2f}%")

# 用多個 sigma 掃描 raw EE 峰
print("\n2. Raw EE 峰掃描 (多個平滑尺度):")
for sigma in [1, 2, 3, 5, 8]:
    smooth = gaussian_filter1d(raw_ee_dl, sigma=sigma)
    # 只取 ℓ>50 嘅正區段
    peaks, props = find_peaks(smooth[50:], distance=20, height=0.01)
    peaks = peaks + 50
    if len(peaks) > 0:
        heights = smooth[peaks]
        print(f"   sigma={sigma}: {[f'{p:.0f}({h:.3f})' for p, h in zip(peaks, heights)]}")
    else:
        print(f"   sigma={sigma}: 無峰檢測")

# 正規化後嘅 raw EE 譜 (除以 TT 包絡)
print("\n3. Raw EE / Raw TT 比率 (正規化):")
ratio = np.zeros_like(raw_ee_dl)
mask = raw_tt_dl > 1
ratio[mask] = raw_ee_dl[mask] / raw_tt_dl[mask]
smooth_ratio = gaussian_filter1d(ratio, sigma=3)
peaks_r, _ = find_peaks(smooth_ratio[50:], distance=30, height=0.01)
peaks_r = peaks_r + 50
print(f"   正規化 EE 峰: {[f'{p:.0f}' for p in peaks_r]}")

# ══════════════════════════════════════════════
# 2. K_Chain 模式投影到極化
# ══════════════════════════════════════════════
print("\n" + "-" * 80)
print("4. K_Chain 44-site 模式投影到極化")
print("-" * 80)

# γ_n = 4 sin²(πn/88), n=1..44
gamma = np.array([4 * np.sin(np.pi*n/88)**2 for n in range(1, 45)])
print(f"\n   K_Chain 44-site 譜:")
print(f"   Σγ = {gamma.sum():.0f} (should be 90)")

# 溫度峰對應嘅 n 值
# TT ℓ_m = 44 × N_int + phase → 對應 K_Chain 模式 n = ?
# 如果 ℓ = 44 × k, 對應 n = k 或 n = 88-k
# TT1=220=44×5 → n=5 或 n=83
# TT2=537=44×12+9 → n=12 或 n=76
# 但 537 唔係 44 嘅整數倍
print(f"\n   TT 峰對應 K_Chain 模式:")
tt_pred = {m: idcm_tt(m) for m in range(1, 8)}
for m, l in tt_pred.items():
    n_int = l // 44
    n_frac = l % 44
    print(f"   m={m}: ℓ={l} = 44×{n_int} + {n_frac} → n={n_int} 或 n={88-n_int}")

# 極化峰: 如果係 π/2 相移, 對應 half-integer n
# n_E = n_T + 0.5 (半整數偏移)
print(f"\n   極化峰 (n = n_T + 0.5):")
for m in range(1, 7):
    n_int = tt_pred[m] // 44
    n_E = n_int + 0.5
    # ℓ_E = 44 × n_E? 但相位項要考慮
    l_E_simple = 44 * n_E
    mid = (tt_pred[m] + tt_pred[m+1]) / 2.0
    print(f"   m={m}: n_T={n_int} + 0.5 → n_E={n_E} → ℓ_E≈{l_E_simple:.0f} vs 中點={mid:.1f}")

# ══════════════════════════════════════════════
# 3. 觀測極化峰 vs 結構公式候選
# ══════════════════════════════════════════════
print("\n" + "-" * 80)
print("5. 極化峰結構公式候選")
print("-" * 80)

# 從檔案讀取各數據源
from astropy.io import fits

# Planck binned
planck_ee = np.loadtxt(os.path.join(O9_DATA, 'planck_ee.txt'))
planck_te = np.loadtxt(os.path.join(O9_DATA, 'planck_te.txt'))
planck_tt = np.loadtxt(os.path.join(O9_DATA, 'planck_tt.txt'))

# ACT DR6
hdul = fits.open(os.path.join(O9_DATA, 'act_dr6_cmb_sacc.fits'))
act_te = hdul['data:cl_0e'].data
act_ee = hdul['data:cl_ee'].data

# SPT window
win = np.loadtxt(os.path.join(O9_DATA, 'spt_tt150_windows.txt'))
ell_w = win[:, 0]
W = win[:, 1:]
bin_centers = np.array([(ell_w * W[:, b]).sum() / W[:, b].sum() for b in range(W.shape[1])])

# SPT bdp
bdp = np.loadtxt(os.path.join(O9_DATA, 'spt3g_tne_bdp.txt'))
specs = [('TT90x90',52), ('TE90x90',72), ('EE90x90',72), ('TT90x150',52),
         ('TE90x150',72), ('TE150x90',72), ('EE90x150',72), ('TT90x220',52),
         ('TE90x220',72), ('TE220x90',72), ('EE90x220',72), ('TT150x150',52),
         ('TE150x150',72), ('EE150x150',72), ('TT150x220',52), ('TE150x220',72),
         ('TE220x150',72), ('EE150x220',72), ('TT220x220',52), ('TE220x220',72),
         ('EE220x220',72)]
spt = {}
idx = 0
for name, n in specs:
    spt[name] = bdp[idx:idx+n]
    idx += n

# ═══ 候選公式測試 ═══
# 候選 A: 簡單中點 ℓ_E(m) = (ℓ_T(m) + ℓ_T(m+1))/2
# 候選 B: 44 × 整數偏移 + phase/2 
# 候選 C: 44 × (M - C(9-m,2)) + 偏移 (獨立公式)

print(f"\n   候選 A: 中點 (已測試)")
print(f"   候選 B: ℓ_E(m) = 44 × (M - C(9-m,2)) + 整數部分 + 相移/2")

# 分析: 邊 d 極化峰匹配得好, 邊 d 唔匹配?
# 用 CAMB raw TE 峰 (最可靠嘅極化峰檢測)
camb_te = np.array([310, 468, 749, 914, 1072, 1370])  # raw TE 峰 (排除 152 重離子峰)
print(f"\n   CAMB raw TE 峰 (排除重離子): {[f'{l:.0f}' for l in camb_te]}")
print(f"   CAMB raw TE 間距: {np.diff(camb_te)}")

# 將 CAMB raw TE 峰映射到 IDCM 極化峰
# 需要決定邊個 TE 峰對應邊個 m
# TE_3=749 可能對應 m=2 (中點 673.5)
# TE_4=914 可能對應 m=3 (中點 912.0) ✅
# TE_5=1072 可能對應 m=4 (中點 1067.5) ✅
# TE_6=1370 可能對應 m=6 (中點 1376.0) ✅

# 嘗試映射
print(f"\n   CAMB raw TE → IDCM 極化峰映射:")
te_mapping = {3: 749, 4: 914, 5: 1072, 6: 1370}  # TE peak → m
for m, l_te in te_mapping.items():
    mid = (tt_pred[m] + tt_pred[m+1]) / 2.0
    dev = (l_te - mid) / mid * 100
    print(f"   m={m}: IDCM 中點={mid:.1f} vs CAMB raw TE={l_te} (dev={dev:+.2f}%)")

# 睇下 TE 峰嘅偏移量有冇規律
print(f"\n   TE 峰偏移量分析:")
for m, l_te in te_mapping.items():
    t1 = tt_pred[m]
    t2 = tt_pred[m+1]
    mid = (t1 + t2) / 2.0
    offset = l_te - mid
    offset_norm = offset / (t2 - t1) * 100  # 佔峰間距百分比
    print(f"   m={m}: offset={offset:+.1f} = {offset_norm:+.1f}% 嘅 Δℓ")

# ═══ 新候選: 極化峰可能係獨立嘅 K_Chain 模式 ═══
# 如果 TT 峰係 K_Chain 嘅「位移」模式
# 極化峰可能係 K_Chain 嘅「速度」模式
# 速度模式 = 位移模式嘅相鄰點 (half-integer n)
print(f"\n\n   候選 D: 獨立 K_Chain 模式 (n = 半整數):")
for m in range(1, 7):
    n_int = tt_pred[m] // 44
    # 半整數 n 對應嘅 ℓ
    n_half = n_int + 0.5
    # 但 ℓ 嘅相位部分點處理? 
    # 對 TT, ℓ = 44×n_int + phase, phase = ((m-1)×9) mod 25
    # 對 EE, ℓ = 44×n_half + phase_EE? 
    # 如果 phase_EE = phase + Δphase/2
    phase_t1 = ((m-1) * 9) % 25
    phase_t2 = (m * 9) % 25
    # phase 差嘅一半
    phase_mid = (phase_t1 + phase_t2) / 2.0
    if phase_mid >= 25: phase_mid -= 25
    l_E = 44 * n_half + phase_mid
    dev = (l_E - (tt_pred[m]+tt_pred[m+1])/2)
    print(f"   m={m}: ℓ_E = 44×({n_int}+0.5) + {phase_mid:.1f} = {l_E:.1f} (vs 中點={(tt_pred[m]+tt_pred[m+1])/2:.1f}, Δ={dev:+.1f})")

# ══════════════════════════════════════════════
# 6. 極化峰間距模式
# ══════════════════════════════════════════════
print("\n" + "-" * 80)
print("6. 極化峰間距模式")
print("-" * 80)

# SPT EE 峰間距
spt_ee_peaks = np.array([674, 974, 1324, 1624, 1924, 2224])
spt_ee_spacing = np.diff(spt_ee_peaks)
print(f"\n   SPT EE150 峰間距: {spt_ee_spacing}")
print(f"   平均: {spt_ee_spacing.mean():.1f}, 44 倍數: {[f'{s/44:.2f}' for s in spt_ee_spacing]}")

# SPT TE 峰間距
spt_te_peaks = np.array([474, 724, 924, 1074, 1374, 1674, 1974, 2324])
spt_te_spacing = np.diff(spt_te_peaks)
print(f"\n   SPT TE150 峰間距: {spt_te_spacing}")
print(f"   平均: {spt_te_spacing.mean():.1f}, 44 倍數: {[f'{s/44:.2f}' for s in spt_te_spacing]}")

# Planck EE 峰間距
planck_ee_peaks = np.array([392, 698, 1013, 1319, 1682])
planck_ee_spacing = np.diff(planck_ee_peaks)
print(f"\n   Planck EE 峰間距: {planck_ee_spacing}")
print(f"   平均: {planck_ee_spacing.mean():.1f}, 44 倍數: {[f'{s/44:.2f}' for s in planck_ee_spacing]}")

# CAMB raw TE 峰間距 (排除 152 重離子)
camb_te_acoustic = camb_te  # 310, 468, 749, 914, 1072, 1370
camb_te_spacing = np.diff(camb_te_acoustic)
print(f"\n   CAMB raw TE 聲學峰間距: {camb_te_spacing}")
print(f"   平均: {camb_te_spacing.mean():.1f}, 44 倍數: {[f'{s/44:.2f}' for s in camb_te_spacing]}")

# ═══ 關鍵觀察: 極化峰間距 vs TT 峰間距 ═══
print(f"\n\n   關鍵: 極化峰間距 vs TT 峰間距")
tt_spacing = np.diff(list(tt_pred.values()))
print(f"   TT 峰間距 (IDCM): {tt_spacing}")
print(f"   TT 峰間距平均: {tt_spacing.mean():.1f}")
print(f"   Planck EE 峰間距: {planck_ee_spacing}")
print(f"   SPT EE 峰間距: {spt_ee_spacing}")
print(f"   CAMB raw TE 峰間距: {camb_te_spacing}")

# 結論: 極化峰間距似乎係 TT 峰間距嘅約一半
# TT 間距: 317, 273, 204, 107, 219, 72
# 極化間距: ~300, ~250, ~200, ~150 (Planck EE)
# 呢個模式同 TT 類似但更平滑

# ══════════════════════════════════════════════
# 7. 探索: 極化峰 = 44 × (M - C(9-m,2)) + 結構相位
# ══════════════════════════════════════════════
print("\n" + "-" * 80)
print("7. 極化峰獨立公式探索")
print("-" * 80)

# 如果極化峰都係 44 基頻, 咁佢哋應該都可以寫成 44 × 整數 + 相位
# 用 Planck EE 峰測試
print(f"\n   Planck EE 峰 mod 44:")
for l in planck_ee_peaks:
    n_int = l // 44
    n_frac = l % 44
    print(f"   ℓ={l:.0f} = 44×{n_int:.0f} + {n_frac:.0f}")

# SPT EE 峰 mod 44
print(f"\n   SPT EE150 峰 mod 44:")
for l in spt_ee_peaks:
    n_int = l // 44
    n_frac = l % 44
    print(f"   ℓ={l:.0f} = 44×{n_int:.0f} + {n_frac:.0f}")

# CAMB raw TE 峰 mod 44
print(f"\n   CAMB raw TE 峰 mod 44:")
for l in camb_te_acoustic:
    n_int = l // 44
    n_frac = l % 44
    print(f"   ℓ={l:.0f} = 44×{n_int:.0f} + {n_frac:.0f}")

# TT 峰 mod 44
print(f"\n   TT 峰 mod 44 (IDCM):")
for m, l in tt_pred.items():
    n_int = l // 44
    n_frac = l % 44
    print(f"   m={m}: ℓ={l} = 44×{n_int} + {n_frac}")

# 睇下極化峰嘅整數部分同 TT 有咩關係
print(f"\n   極化峰整數部分 vs TT 整數部分:")
for m in range(1, 7):
    n_tt = tt_pred[m] // 44
    n_tt_next = tt_pred[m+1] // 44
    n_mid = (n_tt + n_tt_next) / 2.0
    print(f"   m={m}: TT n={n_tt},{n_tt_next} → 中點 n={n_mid:.1f}")

print("\n★ 完成!")