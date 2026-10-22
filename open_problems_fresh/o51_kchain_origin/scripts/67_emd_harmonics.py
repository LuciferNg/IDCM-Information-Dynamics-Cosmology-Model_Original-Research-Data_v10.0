#!/usr/bin/env python3
"""
O51/67: EMD 諧波檢測 — eBOSS DR16 raw ξ(s) (skill §9 pipeline)
===============================================================
skill §9.2: EMD 自適應分解 broadband vs 諧波
eBOSS raw 參數: max_imfs=8, sd_threshold=0.005, aggressive → 預期 11/19 harmonics

檢驗:
  1. EMD 分解 ξ(s) → IMFs + residual
  2. Peak: s_n = λ_sync/n (n=2..20) 喺 EMD residual 嘅 S/N
  3. Null: s_n = λ_sync/(n+0.5) 應該冇訊號
  4. 對比 raw vs EMD 檢測率
"""
import json, math, sys
import numpy as np
from scipy.interpolate import interp1d

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ PASS: {name}")
    else:
        FAIL += 1
        print(f"  ❌ FAIL: {name}")
    if detail:
        print(f"    {detail}")

# ============ 1. EMD 分解 (skill §9.2) ============
def emd_decompose(x, max_imfs=8, sd_threshold=0.005, max_iterations=40):
    """EMD sifting: decompose signal into IMFs + residual (skill 參數)"""
    imfs, residual = [], x.copy()
    for imf_idx in range(max_imfs):
        h = residual.copy()
        for iteration in range(max_iterations):
            maxima = [i for i in range(1, len(h)-1) if h[i] > h[i-1] and h[i] > h[i+1]]
            minima = [i for i in range(1, len(h)-1) if h[i] < h[i-1] and h[i] < h[i+1]]
            if len(maxima) < 2 or len(minima) < 2: break
            # np.interp: 穩陣線性插值, 零 boundary 問題 (scipy 1.18 interp1d 有坑)
            x_full = np.arange(len(h))
            upper = np.interp(x_full, maxima, h[maxima])
            lower = np.interp(x_full, minima, h[minima])
            h_new = h - (upper + lower) / 2
            if np.sum(h_new**2) > 1e-30:
                if np.sum((h_new - h)**2) / np.sum(h_new**2) < sd_threshold: break
            h = h_new
        imfs.append(h)
        residual -= h
        n_extrema = sum(1 for i in range(1, len(residual)-1)
                       if (residual[i] > residual[i-1] and residual[i] > residual[i+1]) or
                          (residual[i] < residual[i-1] and residual[i] < residual[i+1]))
        if n_extrema < 4: break
    return imfs, residual

# ============ 2. 讀數據 ============
s_vals, xi_vals, err_vals = [], [], []
with open('/home/wsl/Projects/IDCM-Original/IDCM-v9.0--W-Field-Lattice/sync_bump_analysis/eboss_dr16_lrg_xi.txt') as f:
    for line in f:
        if line.startswith('#') or not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 3:
            s_vals.append(float(parts[0]))
            xi_vals.append(float(parts[1]))
            err_vals.append(float(parts[2]))

s = np.array(s_vals)
xi = np.array(xi_vals)
err = np.array(err_vals)

print("=" * 62)
print("EMD 諧波檢測 — eBOSS DR16 raw ξ(s)")
print("=" * 62)
print(f"數據: {len(s)} bins, s = {s.min():.1f}-{s.max():.1f} h⁻¹Mpc")

# ============ 3. EMD 分解 ============
print("\n--- EMD 分解 ---")
imfs, residual = emd_decompose(xi, max_imfs=8, sd_threshold=0.005)
print(f"IMFs: {len(imfs)}, residual extrema < 4")
for i, imf in enumerate(imfs):
    print(f"  IMF{i+1}: range [{imf.min():+.4f}, {imf.max():+.4f}], std={imf.std():.4f}")

# EMD 諧波訊號 = 高頻 IMFs 之和 (IMF1-3 通常係諧波)
# 低頻 IMFs + residual = broadband
n_high = min(3, len(imfs))
emd_signal = sum(imfs[:n_high])
emd_bg = xi - emd_signal
print(f"\n高頻訊號 (IMF1-{n_high}): std={emd_signal.std():.4f}")
print(f"Broadband (其餘): std={emd_bg.std():.4f}")

# ============ 4. IDCM 預言 ============
R_H = 4129.94
h = 0.6727
lambda_sync = 2 * math.pi * R_H / 88
lambda_h = lambda_sync * h
print(f"\nλ_sync = {lambda_h:.2f} h⁻¹Mpc")

# ============ 5. Peak 檢驗 (EMD 訊號) ============
print("\n--- Peak 檢驗: s_n = λ_sync/n (EMD 訊號) ---")
peak_results = []
for n in range(2, 20):
    s_n = lambda_h / n
    if s.min() <= s_n <= s.max():
        idx = np.argmin(np.abs(s - s_n))
        snr = emd_signal[idx] / err[idx]
        peak_results.append((n, s_n, s[idx], emd_signal[idx], snr))
        marker = " ✅" if abs(snr) > 2 else ""
        print(f"  n={n:2d}: s_pred={s_n:6.2f} → bin {s[idx]:6.1f}, EMD={emd_signal[idx]:+.4f}, S/N={snr:+.2f}{marker}")

n_peaks = len(peak_results)
n_detect = sum(1 for _,_,_,_,snr in peak_results if abs(snr) > 2)
print(f"\n檢測率: {n_detect}/{n_peaks} (|S/N| > 2)")
check("EMD Peak 檢測 ≥ 8/17 (eBOSS raw 預期 11/19)", n_detect >= 8,
      f"{n_detect}/{n_peaks}")

# ============ 6. Null 檢驗 (EMD 訊號) ============
print("\n--- Null 檢驗: s_n = λ_sync/(n+0.5) (EMD 訊號) ---")
null_results = []
for n in range(2, 20):
    s_n = lambda_h / (n + 0.5)
    if s.min() <= s_n <= s.max():
        idx = np.argmin(np.abs(s - s_n))
        snr = emd_signal[idx] / err[idx]
        null_results.append((n, s_n, s[idx], emd_signal[idx], snr))
        marker = " ⚠️" if abs(snr) > 2 else ""
        print(f"  n={n:2d}: s_pred={s_n:6.2f} → bin {s[idx]:6.1f}, EMD={emd_signal[idx]:+.4f}, S/N={snr:+.2f}{marker}")

n_nulls = len(null_results)
n_false = sum(1 for _,_,_,_,snr in null_results if abs(snr) > 2)
print(f"\n假陽性: {n_false}/{n_nulls}")
check("EMD Null 假陽性 ≤ 2", n_false <= 2, f"{n_false}/{n_nulls}")

# ============ 7. 對比 raw vs EMD ============
print("\n--- Raw vs EMD 對比 ---")
raw_peaks = 0
for n in range(2, 20):
    s_n = lambda_h / n
    if s.min() <= s_n <= s.max():
        idx = np.argmin(np.abs(s - s_n))
        if abs(xi[idx] / err[idx]) > 2:
            raw_peaks += 1

print(f"Raw 數據檢測: {raw_peaks}/{n_peaks}")
print(f"EMD 數據檢測: {n_detect}/{n_peaks}")
check("EMD 提升檢測率 (vs raw)", n_detect > raw_peaks, f"{n_detect} vs {raw_peaks}")

# ============ 8. 總結 ============
print(f"\n{'=' * 62}")
print(f"EMD 諧波檢測總結: ✅ {PASS} / {PASS+FAIL}")
print(f"{'=' * 62}")

result = {
    'lambda_sync_h': round(lambda_h, 3),
    'n_imfs': len(imfs),
    'peak_detected': n_detect,
    'peak_total': n_peaks,
    'null_false_positive': n_false,
    'null_total': n_nulls,
    'raw_detected': raw_peaks,
    'peak_list': [{'n': n, 's_pred': round(sp,2), 's_bin': float(sb), 'emd': round(e,4), 'snr': round(snr,2)} for n,sp,sb,e,snr in peak_results],
    'pass': PASS,
    'fail': FAIL
}

with open('data/67_emd_harmonics.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"\n✅ 結果 -> data/67_emd_harmonics.json")