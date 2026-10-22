#!/usr/bin/env python3
"""
O51/69: BOSS DR12 post-recon ξ(s) — EMD 諧波 Peak/Null 檢驗
===============================================================
數據: Ross+2016 BOSS DR12 zbin1 monopole post-recon
     (ross_dr12_corrfunc.zip, bincent0 = 主 bin)
IDCM 預言:
  Peak:  s_n = λ_sync/n  (n=2..20)
  Null:  s_n = λ_sync/(n+0.5)
skill §9: BOSS post-recon EMD → 17/19 harmonics, 0 false positives, p<10⁻⁵⁰
"""
import json, math, sys, zipfile
import numpy as np

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

# ============ 1. 讀數據 ============
z = zipfile.ZipFile('/home/wsl/Projects/IDCM-Original/IDCM-v9.0--W-Field-Lattice/sync_bump_analysis/ross_dr12_corrfunc.zip')
data_path = 'Ross_2016_COMBINEDDR12/Ross_2016_COMBINEDDR12_zbin1_correlation_function_monopole_post_recon_bincent0.dat'
s_vals, xi_vals, err_vals = [], [], []
with z.open(data_path) as f:
    for line in f.read().decode().strip().split('\n'):
        if line.startswith('#') or not line.strip():
            continue
        parts = line.split()
        s_vals.append(float(parts[0]))
        xi_vals.append(float(parts[1]))
        err_vals.append(float(parts[2]))

s = np.array(s_vals)
xi = np.array(xi_vals)
err = np.array(err_vals)
print("=" * 62)
print("BOSS DR12 post-recon ξ(s) — EMD 諧波檢驗")
print("=" * 62)
print(f"數據: {len(s)} bins, s = {s.min():.1f}-{s.max():.1f} h⁻¹Mpc")

# ============ 2. EMD 分解 ============
def emd_decompose(x, max_imfs=5, sd_threshold=0.01, max_iterations=40):
    """EMD sifting (skill §9.2, np.interp 版)"""
    imfs, residual = [], x.copy()
    for imf_idx in range(max_imfs):
        h = residual.copy()
        for iteration in range(max_iterations):
            maxima = [i for i in range(1, len(h)-1) if h[i] > h[i-1] and h[i] > h[i+1]]
            minima = [i for i in range(1, len(h)-1) if h[i] < h[i-1] and h[i] < h[i+1]]
            if len(maxima) < 2 or len(minima) < 2: break
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

print("\n--- EMD 分解 ---")
imfs, residual = emd_decompose(xi, max_imfs=5, sd_threshold=0.01)
print(f"IMFs: {len(imfs)}")
for i, imf in enumerate(imfs):
    print(f"  IMF{i+1}: range [{imf.min():+.4f}, {imf.max():+.4f}], std={imf.std():.4f}")

n_high = min(3, len(imfs))
emd_signal = sum(imfs[:n_high])
print(f"\n高頻訊號 (IMF1-{n_high}): std={emd_signal.std():.4f}")
print(f"Broadband: std={(xi-emd_signal).std():.4f}")

# ============ 3. IDCM 預言 ============
R_H = 4129.94
h = 0.6727
lambda_sync = 2 * math.pi * R_H / 88
lambda_h = lambda_sync * h
print(f"\nλ_sync = {lambda_h:.2f} h⁻¹Mpc")
print(f"BAO (λ_sync/2) = {lambda_h/2:.2f} h⁻¹Mpc")

# ============ 4. Peak 檢驗 ============
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
check("Peak 檢測 ≥ 15/18 (BOSS post-recon 目標 17/19)", n_detect >= 15,
      f"{n_detect}/{n_peaks}")

# ============ 5. Null 檢驗 ============
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
check("Null 假陽性 ≤ 2", n_false <= 2, f"{n_false}/{n_nulls}")

# ============ 6. 峰谷對比 (同 n) ============
print("\n--- 峰谷對比 (同一 n 區域) ---")
contrast = 0
total = 0
for n in range(2, 19):
    s_p = lambda_h / n
    s_nl = lambda_h / (n + 0.5)
    if s.min() <= s_nl <= s.max():
        idx_p = np.argmin(np.abs(s - s_p))
        idx_nl = np.argmin(np.abs(s - s_nl))
        if abs(emd_signal[idx_p]) > abs(emd_signal[idx_nl]):
            contrast += 1
        total += 1
print(f"峰強於谷: {contrast}/{total}")
check("峰強於谷 (多數)", contrast >= total * 0.6, f"{contrast}/{total}")

# ============ 7. 總結 ============
print(f"\n{'=' * 62}")
print(f"BOSS post-recon EMD 檢驗: ✅ {PASS} / {PASS+FAIL}")
print(f"{'=' * 62}")

result = {
    'lambda_sync_h': round(lambda_h, 3),
    'n_imfs': len(imfs),
    'peak_detected': n_detect,
    'peak_total': n_peaks,
    'null_false_positive': n_false,
    'null_total': n_nulls,
    'contrast': f'{contrast}/{total}',
    'peak_list': [{'n': n, 's_pred': round(sp,2), 's_bin': float(sb), 'emd': round(e,4), 'snr': round(snr,2)} for n,sp,sb,e,snr in peak_results],
    'pass': PASS,
    'fail': FAIL
}

with open('data/69_boss_postrecon_emd.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"\n✅ 結果 -> data/69_boss_postrecon_emd.json")