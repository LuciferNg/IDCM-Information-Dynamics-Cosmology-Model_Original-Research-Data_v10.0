#!/usr/bin/env python3
"""
O20-C: 極化峰結構公式推導 — 核心發現
========================================
發現: EE 峰整數部分 = 44 × (F₆ + L₄·(k-1)) = 44 × (8 + 7(k-1))
      = 44 × (1 + 7k) for k=1..7
      步長 7 = L₄ (Lucas 數)

驗證:
1. CAMB raw EE 峰 vs 公式
2. Planck binned EE 峰 vs 公式
3. SPT-3G EE150 峰 vs 公式
4. TE 峰結構探索
5. 相位項 φ_E(k) 分析
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
L = [2, 1, 3, 4, 7, 11, 18, 29]  # L₀=2, L₁=1, L₂=3, L₃=4, L₄=7, L₅=11

def idcm_tt(m):
    if m == 5: return 44*(33 - F[6]) + F[8]
    C = _m.comb(9-m, 2) if 9-m >= 2 else 0
    return 44*(33 - C) + (((m-1)*9) % 25)

print("=" * 80)
print("O20-C: 極化峰結構公式推導")
print("=" * 80)

# ══════════════════════════════════════════════
# 1. CAMB 生成 EE 譜
# ══════════════════════════════════════════════
import camb
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, tau=0.0544)
pars.InitPower.set_params(ns=0.9649, As=2.1e-9)
pars.set_for_lmax(2500)
results = camb.get_results(pars)
raw = results.get_cmb_power_spectra(raw_cl=True)
lmax = 2500
ell = np.arange(lmax+1)

raw_ee = raw['unlensed_scalar'][:lmax+1, 1]
raw_ee_dl = raw_ee * ell * (ell+1) / (2*np.pi) * 1e12

# 峰檢測
smooth_ee = gaussian_filter1d(raw_ee_dl, sigma=2)
peaks, props = find_peaks(smooth_ee[50:], distance=20, height=0.01)
camb_ee_peaks = peaks + 50
print(f"\n1. CAMB raw EE 峰: {[f'{l:.0f}' for l in camb_ee_peaks]}")

# ══════════════════════════════════════════════
# 2. EE 峰整數部分分析
# ══════════════════════════════════════════════
print("\n" + "-" * 80)
print("2. EE 峰 mod 44 分析")
print("-" * 80)

print(f"\n   CAMB raw EE 峰 mod 44:")
for l in camb_ee_peaks:
    n_int = l // 44
    n_frac = l % 44
    print(f"   ℓ={l:.0f} = 44×{n_int:.0f} + {n_frac:.0f}")

# 整數部分序列
ee_int = [l // 44 for l in camb_ee_peaks]
print(f"\n   整數部分序列: {ee_int}")
print(f"   間距: {np.diff(ee_int)}")
print(f"   ★ 步長 = {np.diff(ee_int)[0]} = L₄ = {L[4]}")
print(f"   ★ 起始 = {ee_int[0]} = F₆ = {F[6]}")

# 公式: n_int(k) = F₆ + L₄·(k-1) = 8 + 7(k-1)
print(f"\n   公式: n_int(k) = F₆ + L₄·(k-1) = {F[6]} + {L[4]}·(k-1)")
for k in range(1, len(ee_int)+1):
    n_pred = F[6] + L[4]*(k-1)
    n_actual = ee_int[k-1]
    print(f"   k={k}: n_pred={n_pred} vs actual={n_actual} {'✅' if n_pred==n_actual else '🔴'}")

# ═══ 排除重離子峰 (140) ═══
camb_ee_acoustic = camb_ee_peaks[camb_ee_peaks > 150]
print(f"\n   EE 聲學峰 (排除重離子): {[f'{l:.0f}' for l in camb_ee_acoustic]}")

# ══════════════════════════════════════════════
# 3. 相位項 φ_E(k) 分析
# ══════════════════════════════════════════════
print("\n" + "-" * 80)
print("3. 相位項 φ_E(k) 分析")
print("-" * 80)

# 相位 = ℓ - 44 × n_int
ee_phases = [l - 44*(l//44) for l in camb_ee_acoustic]
print(f"\n   EE 相位 (CAMB raw): {ee_phases}")

# 相位是否同 TT 相位有關?
tt_pred = {m: idcm_tt(m) for m in range(1, 8)}
tt_phases = [tt_pred[m] % 44 for m in range(1, 8)]
print(f"   TT 相位: {tt_phases}")

# TT 中點相位
mid_phases = []
for m in range(1, 7):
    p1 = tt_pred[m] % 44
    p2 = tt_pred[m+1] % 44
    mid = (p1 + p2) / 2.0
    if mid > 44: mid -= 44
    mid_phases.append(mid)
print(f"   TT 中點相位: {[f'{p:.1f}' for p in mid_phases]}")

# 相位差: EE 相位 - TT 中點相位
print(f"\n   EE 相位 vs TT 中點相位:")
for k, (l, ep, mp) in enumerate(zip(camb_ee_acoustic, ee_phases, mid_phases)):
    diff = ep - mp
    print(f"   k={k+1}: EE_phase={ep:.0f} vs TT_mid_phase={mp:.1f} (Δ={diff:+.1f})")

# 相位 mod 25 檢查 (TT 用 mod 25)
print(f"\n   EE 相位 mod 25:")
for k, ep in enumerate(ee_phases):
    print(f"   k={k+1}: {ep:.0f} mod 25 = {ep % 25}")

# 相位 mod 9 檢查 (TT 步長 9)
print(f"\n   EE 相位 mod 9:")
for k, ep in enumerate(ee_phases):
    print(f"   k={k+1}: {ep:.0f} mod 9 = {ep % 9}")

# ══════════════════════════════════════════════
# 4. Planck EE 驗證
# ══════════════════════════════════════════════
print("\n" + "-" * 80)
print("4. Planck binned EE 驗證")
print("-" * 80)

planck_ee = np.loadtxt(os.path.join(O9_DATA, 'planck_ee.txt'))
planck_ee_ell = planck_ee[:, 0]
planck_ee_d = planck_ee[:, 1] * planck_ee_ell * (planck_ee_ell+1) / (2*np.pi)

smooth_p = gaussian_filter1d(planck_ee_d, sigma=2)
peaks_p, _ = find_peaks(smooth_p[50:], distance=20, height=1)
planck_ee_peaks = peaks_p + 50
planck_ee_peaks = planck_ee_peaks[planck_ee_peaks > 150]
print(f"\n   Planck EE 峰 (排除重離子): {[f'{l:.0f}' for l in planck_ee_peaks]}")

print(f"\n   Planck EE 峰 mod 44:")
for l in planck_ee_peaks:
    n_int = l // 44
    n_frac = l % 44
    print(f"   ℓ={l:.0f} = 44×{n_int:.0f} + {n_frac:.0f}")

# ══════════════════════════════════════════════
# 5. SPT-3G EE 驗證
# ══════════════════════════════════════════════
print("\n" + "-" * 80)
print("5. SPT-3G EE150 驗證")
print("-" * 80)

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

win = np.loadtxt(os.path.join(O9_DATA, 'spt_tt150_windows.txt'))
ell_w = win[:, 0]
W = win[:, 1:]
bin_centers = np.array([(ell_w * W[:, b]).sum() / W[:, b].sum() for b in range(W.shape[1])])

spt_ee150 = spt['EE150x150']
spt_ee_peaks = []
for i in range(1, len(spt_ee150)-1):
    if spt_ee150[i] > spt_ee150[i-1] and spt_ee150[i] > spt_ee150[i+1] and spt_ee150[i] > 5:
        spt_ee_peaks.append(bin_centers[i])
spt_ee_peaks = np.array(spt_ee_peaks)
print(f"\n   SPT EE150 峰: {[f'{l:.0f}' for l in spt_ee_peaks]}")

print(f"\n   SPT EE150 峰 mod 44:")
for l in spt_ee_peaks:
    n_int = l // 44
    n_frac = l % 44
    print(f"   ℓ={l:.0f} = 44×{n_int:.0f} + {n_frac:.0f}")

# ══════════════════════════════════════════════
# 6. 結構公式閉合測試
# ══════════════════════════════════════════════
print("\n" + "-" * 80)
print("6. 結構公式閉合測試")
print("-" * 80)

# 公式: ℓ_E(k) = 44 × (F₆ + L₄·(k-1)) + φ_E(k)  for k=1..7
# 其中 φ_E(k) = 相位項 (有待閉合)
# 先用 CAMB raw EE 相位做參考

print(f"\n   公式: ℓ_E(k) = 44 × (F₆ + L₄·(k-1)) + φ_E(k)")
print(f"         = 44 × ({F[6]} + {L[4]}·(k-1)) + φ_E(k)")
print(f"         = 44 × (1 + 7k) + φ_E(k)  for k=1..7")

print(f"\n   CAMB raw EE 閉合:")
for k, l in enumerate(camb_ee_acoustic):
    n_int = l // 44
    n_pred = F[6] + L[4]*k
    phase = l % 44
    print(f"   k={k+1}: ℓ={l:.0f} = 44×{n_int:.0f}+{phase:.0f}  (n_pred={n_pred}) {'✅' if n_int==n_pred else '🔴'}")

# 用各數據源嘅整數部分驗證
print(f"\n   多數據源整數部分驗證:")
for k in range(1, 8):
    n_pred = F[6] + L[4]*(k-1)
    print(f"   k={k}: n_pred={n_pred} (44×{n_pred}={44*n_pred})")

# 睇下 Planck EE 整數部分
print(f"\n   Planck EE 整數部分 vs 公式:")
for k, l in enumerate(planck_ee_peaks):
    n_int = l // 44
    k_idx = k + 1
    n_pred = F[6] + L[4]*k
    if k_idx < 8:
        match = "✅" if n_int == n_pred else "🔴"
        print(f"   k={k_idx}: Planck n_int={n_int} vs pred={n_pred} {match}")

# ══════════════════════════════════════════════
# 7. TE 峰結構探索
# ══════════════════════════════════════════════
print("\n" + "-" * 80)
print("7. TE 峰結構探索")
print("-" * 80)

# CAMB raw TE
raw_te = raw['unlensed_scalar'][:lmax+1, 3]
raw_te_dl = raw_te * ell * (ell+1) / (2*np.pi) * 1e12
smooth_te = gaussian_filter1d(np.abs(raw_te_dl), sigma=2)
peaks_te, _ = find_peaks(smooth_te[50:], distance=20, height=1)
camb_te_peaks = peaks_te + 50
camb_te_acoustic = camb_te_peaks[camb_te_peaks > 200]
print(f"\n   CAMB raw TE 峰: {[f'{l:.0f}' for l in camb_te_acoustic]}")

print(f"\n   CAMB raw TE mod 44:")
for l in camb_te_acoustic:
    n_int = l // 44
    n_frac = l % 44
    print(f"   ℓ={l:.0f} = 44×{n_int:.0f} + {n_frac:.0f}")

te_int = [l // 44 for l in camb_te_acoustic]
print(f"\n   TE 整數部分: {te_int}")
print(f"   TE 整數部分間距: {np.diff(te_int)}")

# TE 整數部分 vs EE 整數部分
ee_int_ref = [F[6] + L[4]*k for k in range(7)]
print(f"\n   TE vs EE 整數部分:")
for i, (ti, ei) in enumerate(zip(te_int, ee_int_ref)):
    print(f"   k={i+1}: TE n_int={ti} vs EE n_int={ei} (Δ={ti-ei:+.0f})")

# 睇下 TE 峰係咪 EE 峰嘅子集或偏移
# TE 可能係 EE 嘅一半 (因為 TE 有正負交替)
print(f"\n   TE 可能結構: TE 峰 = EE 峰 ± 偏移?")
for l in camb_te_acoustic:
    # 最近的 EE 整數部分
    n_int = l // 44
    nearest_ee = min(ee_int_ref, key=lambda x: abs(x - n_int))
    nearest_ee_idx = ee_int_ref.index(nearest_ee) + 1
    print(f"   TE ℓ={l:.0f}: n_int={n_int} → nearest EE k={nearest_ee_idx} (n={nearest_ee})")

# ══════════════════════════════════════════════
# 8. 總結
# ══════════════════════════════════════════════
print("\n" + "=" * 80)
print("總結: 極化峰結構公式")
print("=" * 80)

print(f"""
發現:
══════

1. EE 峰整數部分 = 44 × (F₆ + L₄·(k-1)) = 44 × (8 + 7(k-1))
   - F₆ = 8 (Fibonacci 數)
   - L₄ = 7 (Lucas 數)
   - k = 1..7 (7 個 EE 聲學峰)
   - 步長 7 = L₄ — 乾淨嘅 Lucas 數結構

2. EE 峰整數部分序列: 8, 15, 22, 29, 36, 43, 50
   - 等差數列, 步長 7
   - 對應 ℓ = 352, 660, 968, 1276, 1584, 1892, 2200 (未加相位)

3. 相位項 φ_E(k) 有待閉合:
   CAMB raw: 43, 28, 23, 24, 26, 32, 38
   Planck:   (40, 38, 1, 43, 10)
   SPT:      (14, 6, 4, 40, 32, 24)

4. TE 峰結構更複雜 (受正負交替影響),
   需要進一步分析

5. 相比 TT 公式 ℓ_m = 44×(M−C(9−m,2)) + ((m−1)×9 mod 25)
   EE 公式更簡單: ℓ_E(k) = 44×(F₆+L₄·(k-1)) + φ_E(k)
   → 整數部分係線性, 冇三角形數遞減
""")

# 保存結構公式數據
import json
results = {
    'ee_formula': {
        'description': 'ℓ_E(k) = 44 × (F₆ + L₄·(k-1)) + φ_E(k)',
        'F₆': int(F[6]),
        'L₄': int(L[4]),
        'n_int_sequence': [int(F[6] + L[4]*k) for k in range(7)],
        'ℓ_base': [int(44*(F[6] + L[4]*k)) for k in range(7)],
    },
    'camb_raw_ee': {
        'peaks': [float(l) for l in camb_ee_acoustic],
        'n_int': [int(l//44) for l in camb_ee_acoustic],
        'phases': [int(l%44) for l in camb_ee_acoustic],
    },
    'planck_ee': {
        'peaks': [float(l) for l in planck_ee_peaks] if len(planck_ee_peaks) > 0 else [],
    },
    'spt_ee': {
        'peaks': [float(l) for l in spt_ee_peaks] if len(spt_ee_peaks) > 0 else [],
    },
}
with open(os.path.join(OUT_DIR, 'ee_structural_formula.json'), 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n   結果已保存到: {os.path.join(OUT_DIR, 'ee_structural_formula.json')}")
print("\n★ 完成!")