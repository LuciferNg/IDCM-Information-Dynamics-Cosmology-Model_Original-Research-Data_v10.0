#!/usr/bin/env python3
"""
O51/70: BOSS DR12 post-recon ξ(s) — 標準 BAO 峰谷檢驗 (ξ×s²)
===============================================================
用宇宙學標準做法 (唔用 EMD — 數據 extrema 太少 EMD 收斂唔到):
  1. ξ(s)×s² 放大 BAO 訊號
  2. BAO 峰位置 (預期 ~105 h⁻¹Mpc) vs IDCM λ_sync/2 = 99.18
  3. 峰谷結構: 第一個峰 (BAO) + 第二個峰 (~2×) 位置
  4. 諧波序列: ξ×s² 嘅局部峰 vs λ_sync/n
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
print("BOSS DR12 post-recon ξ(s) — BAO 峰谷檢驗")
print("=" * 62)
print(f"數據: {len(s)} bins, s = {s.min():.1f}-{s.max():.1f} h⁻¹Mpc")

# ============ 2. IDCM 預言 ============
R_H = 4129.94
h = 0.6727
lambda_sync = 2 * math.pi * R_H / 88
lambda_h = lambda_sync * h
bao_idcm = lambda_h / 2
print(f"\nIDCM λ_sync = {lambda_h:.2f} h⁻¹Mpc")
print(f"IDCM BAO = λ_sync/2 = {bao_idcm:.2f} h⁻¹Mpc")

# ============ 3. BAO 峰檢驗 (ξ×s²) ============
print("\n--- BAO 峰檢驗 (ξ×s², 標準做法) ---")
xs2 = xi * s**2
err_xs2 = err * s**2

# BAO 峰: 喺 s=80-130 範圍搵最大 (避開 s<80 嘅線性區)
mask_bao = (s >= 80) & (s <= 130)
i_bao = np.argmax(xs2[mask_bao]) + np.where(mask_bao)[0][0]
s_bao_obs = s[i_bao]
snr_bao = xs2[i_bao] / err_xs2[i_bao]
print(f"觀測 BAO 峰: s = {s_bao_obs:.1f} h⁻¹Mpc, ξs² = {xs2[i_bao]:.2f}, S/N = {snr_bao:.1f}")
print(f"IDCM 預言:   s = {bao_idcm:.2f} h⁻¹Mpc")
dev_bao = abs(s_bao_obs - bao_idcm) / bao_idcm * 100
print(f"偏差: {dev_bao:.2f}%")
check("BAO 峰 ≈ λ_sync/2 (5%)", dev_bao < 5, f"obs={s_bao_obs:.1f}, IDCM={bao_idcm:.2f}, dev={dev_bao:.2f}%")

# 標準 BAO 峰 (Planck+CMASS 文獻值 ~105)
print(f"文獻 BAO 峰: ~105 h⁻¹Mpc (Ross+2016)")
dev_std = abs(s_bao_obs - 105) / 105 * 100
check("BAO 峰 ≈ 文獻 105 (5%)", dev_std < 5, f"obs={s_bao_obs:.1f}, 文獻=105, dev={dev_std:.2f}%")

# ============ 4. 第二峰檢驗 (2×BAO) ============
print("\n--- 第二峰檢驗 (s ≈ 2×BAO) ---")
s2_pred = 2 * bao_idcm
mask2 = (s >= 150) & (s <= 200)
if mask2.sum() > 0:
    i2 = np.argmax(xs2[mask2]) + np.where(mask2)[0][0]
    s2_obs = s[i2]
    print(f"IDCM 預言: s = {s2_pred:.2f} h⁻¹Mpc")
    print(f"觀測第二峰: s = {s2_obs:.1f} h⁻¹Mpc, ξs² = {xs2[i2]:.2f}")
    dev2 = abs(s2_obs - s2_pred) / s2_pred * 100
    print(f"偏差: {dev2:.2f}%")
    check("第二峰 ≈ 2×λ_sync/2 (10%)", dev2 < 10, f"obs={s2_obs:.1f}, IDCM={s2_pred:.2f}, dev={dev2:.2f}%")

# ============ 5. 諧波序列檢驗 ============
print("\n--- 諧波序列 (λ_sync/n 位置嘅 ξs² S/N) ---")
harm_results = []
for n in range(2, 13):
    s_n = lambda_h / n
    if s.min() <= s_n <= s.max():
        idx = np.argmin(np.abs(s - s_n))
        snr = xs2[idx] / err_xs2[idx]
        harm_results.append((n, s_n, s[idx], xs2[idx], snr))
        marker = " ✅" if snr > 3 else ""
        print(f"  n={n:2d}: s_pred={s_n:6.2f} → bin {s[idx]:6.1f}, ξs²={xs2[idx]:7.2f}, S/N={snr:+7.1f}{marker}")

n_harm = len(harm_results)
n_detect = sum(1 for _,_,_,_,snr in harm_results if snr > 3)
print(f"\n檢測率: {n_detect}/{n_harm} (S/N > 3)")
check("諧波檢測 ≥ 8/11", n_detect >= 8, f"{n_detect}/{n_harm}")

# ============ 6. Null: 諧波之間 (λ_sync/(n+0.5)) ============
print("\n--- Null: 諧波之間 (λ_sync/(n+0.5) 嘅 ξs² 應該細) ---")
null_vals = []
for n in range(2, 12):
    s_n = lambda_h / (n + 0.5)
    if s.min() <= s_n <= s.max():
        idx = np.argmin(np.abs(s - s_n))
        null_vals.append((n, s_n, s[idx], xs2[idx]))
        print(f"  n={n:2d}: s_pred={s_n:6.2f} → bin {s[idx]:6.1f}, ξs²={xs2[idx]:7.2f}")

# 對比: 峰 vs 谷
print("\n峰谷對比:")
contrast = 0
total = 0
for n in range(2, 12):
    s_p = lambda_h / n
    s_nl = lambda_h / (n + 0.5)
    if s.min() <= s_nl <= s.max() and s.min() <= s_p <= s.max():
        idx_p = np.argmin(np.abs(s - s_p))
        idx_nl = np.argmin(np.abs(s - s_nl))
        if xs2[idx_p] > xs2[idx_nl]:
            contrast += 1
        total += 1
print(f"峰 > 谷: {contrast}/{total}")
check("峰 > 谷 (多數)", contrast >= total * 0.6, f"{contrast}/{total}")

# ============ 7. 總結 ============
print(f"\n{'=' * 62}")
print(f"BOSS post-recon BAO 檢驗: ✅ {PASS} / {PASS+FAIL}")
print(f"{'=' * 62}")

result = {
    'lambda_sync_h': round(lambda_h, 3),
    'bao_idcm': round(bao_idcm, 2),
    'bao_obs': round(float(s_bao_obs), 2),
    'bao_dev_pct': round(float(dev_bao), 2),
    'harm_detected': n_detect,
    'harm_total': n_harm,
    'contrast': f'{contrast}/{total}',
    'harm_list': [{'n': n, 's_pred': round(sp,2), 's_bin': float(sb), 'xs2': round(x,2), 'snr': round(snr,1)} for n,sp,sb,x,snr in harm_results],
    'pass': PASS,
    'fail': FAIL
}

with open('data/70_boss_bao_peaks.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"\n✅ 結果 -> data/70_boss_bao_peaks.json")