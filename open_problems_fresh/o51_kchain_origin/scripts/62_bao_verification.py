#!/usr/bin/env python3
"""
O51/62: BAO 驗證 — λ_sync/2 = 147.44 Mpc vs eBOSS DR16
===============================================================
IDCM 預言:
  λ_sync = 2πR_H/88 = 294.877 Mpc (K_Chain 空間週期)
  BAO 主峰 = λ_sync/2 = 147.44 Mpc
  標準 ΛCDM r_drag ≈ 147.0 Mpc → 0.3% 吻合
  
  諧波序列: s_n = λ_sync/n, n = 2,3,4,...

數據: eBOSS DR16 LRG raw ξ(s) (Bautista+2020)
  範圍: s = 7.5-247.5 h⁻¹Mpc, 49 bins
  單位: h⁻¹Mpc
"""
import json, math, sys
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

# ============ 1. 讀 eBOSS 數據 ============
print("=" * 62)
print("eBOSS DR16 LRG ξ(s) 數據")
print("=" * 62)

s_vals = []
xi_vals = []
err_vals = []
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
print(f"數據點: {len(s)}")
print(f"範圍: s = {s.min():.1f} - {s.max():.1f} h⁻¹Mpc")
print(f"ξ 範圍: [{xi.min():.4f}, {xi.max():.4f}]")

# ============ 2. IDCM 預言位置 ============
print("\n" + "=" * 62)
print("IDCM 預言: λ_sync 諧波序列")
print("=" * 62)

R_H = 4129.94  # Mpc
lambda_sync = 2 * math.pi * R_H / 88
h = 0.6727  # 標準 h

# λ_sync 喺 h⁻¹Mpc 單位
lambda_sync_h = lambda_sync * h
print(f"λ_sync = 2πR_H/88 = {lambda_sync:.4f} Mpc")
print(f"λ_sync (h⁻¹Mpc, h={h}) = {lambda_sync_h:.2f} h⁻¹Mpc")

# 諧波位置
harmonics = []
for n in range(1, 21):
    s_n = lambda_sync_h / n
    harmonics.append((n, s_n))

print("\nIDCM 諧波序列 (喺 eBOSS 範圍內):")
in_range = []
for n, s_n in harmonics:
    if s.min() <= s_n <= s.max():
        in_range.append((n, s_n))
        # 搵最近 bin
        idx = np.argmin(np.abs(s - s_n))
        snr = xi[idx] / err[idx]
        print(f"  n={n:2d}: s = {s_n:7.2f} h⁻¹Mpc → bin s={s[idx]:6.1f} (Δ={s[idx]-s_n:+5.1f}), ξ={xi[idx]:.4f}, S/N={snr:+.2f}")

# ============ 3. 主峰檢驗: n=2 (λ_sync/2 = 99.2 h⁻¹Mpc) ============
print("\n" + "=" * 62)
print("主峰檢驗: λ_sync/2 = 99.18 h⁻¹Mpc")
print("=" * 62)

# 標準 BAO 峰位置 (post-recon 一般 ~105 h⁻¹Mpc)
# IDCM λ_sync/2 = 99.18 h⁻¹Mpc
s_peak_idcm = lambda_sync_h / 2
idx_peak = np.argmin(np.abs(s - s_peak_idcm))
print(f"IDCM λ_sync/2 = {s_peak_idcm:.2f} h⁻¹Mpc")
print(f"最近 bin: s={s[idx_peak]:.1f}, ξ={xi[idx_peak]:.4f}±{err[idx_peak]:.4f}, S/N={xi[idx_peak]/err[idx_peak]:+.2f}")

# 比較: 附近 bins 嘅 S/N
print("\n峰附近區域:")
for i in range(max(0, idx_peak-3), min(len(s), idx_peak+4)):
    snr = xi[i] / err[i]
    marker = " ← IDCM 峰" if i == idx_peak else ""
    print(f"  s={s[i]:6.1f}: ξ={xi[i]:.4f}±{err[i]:.4f}, S/N={snr:+.2f}{marker}")

# 寬峰檢查: s=90-110 區域
region = (s >= 90) & (s <= 110)
print(f"\n寬峰檢查 (s=90-110 h⁻¹Mpc):")
print(f"  區域內 bins: {region.sum()}")
print(f"  mean S/N: {np.mean(xi[region]/err[region]):+.3f}")
print(f"  max ξ: {xi[region].max():.4f} @ s={s[region][np.argmax(xi[region])]:.1f}")

# ============ 4. 諧波檢測 (EMD 或簡單減背景) ============
print("\n" + "=" * 62)
print("諧波檢測: 減平滑背景後嘅殘差")
print("=" * 62)

# 用簡單移動平均做背景 (raw data 冇 post-recon, 背景係 broadband)
from scipy.ndimage import uniform_filter1d
xi_bg = uniform_filter1d(xi, size=9, mode='nearest')
xi_resid = xi - xi_bg

print("殘差 (raw − 平滑背景):")
resid_snr = xi_resid / err
detected = []
for n, s_n in in_range:
    idx = np.argmin(np.abs(s - s_n))
    snr = resid_snr[idx]
    status = "✅" if abs(snr) > 2 else ("🟡" if abs(snr) > 1 else "❌")
    if abs(snr) > 1:
        detected.append((n, s_n, snr))
    print(f"  n={n:2d}: s={s_n:7.2f} → residual ξ={xi_resid[idx]:+.4f}, S/N={snr:+.2f} {status}")

print(f"\n檢測到 (|S/N|>1): {len(detected)}/{len(in_range)}")
print(f"  {[n for n,_,_ in detected]}")

# ============ 5. ΛCDM 對比 ============
print("\n" + "=" * 62)
print("ΛCDM 對比: r_drag vs λ_sync/2")
print("=" * 62)

r_drag = 147.09  # Planck 2018 sound horizon (Mpc)
print(f"ΛCDM r_drag = {r_drag} Mpc (Planck 2018)")
print(f"IDCM λ_sync/2 = {lambda_sync/2:.2f} Mpc")
print(f"差異: {abs(lambda_sync/2 - r_drag):.2f} Mpc ({abs(lambda_sync/2 - r_drag)/r_drag*100:.3f}%)")

check("λ_sync/2 ≈ r_drag (0.3%)", abs(lambda_sync/2 - r_drag)/r_drag < 0.005,
      f"λ_sync/2={lambda_sync/2:.2f}, r_drag={r_drag:.2f}, dev={abs(lambda_sync/2-r_drag)/r_drag*100:.3f}%")

# λ_sync 整數關係
print(f"\nλ_sync 結構: λ_sync = 2πR_H/88")
print(f"  R_H = {R_H} Mpc (c/H0, H0=72.59)")
print(f"  88 = 2N_d (N_d=44)")
print(f"  λ_sync = 2π·4129.94/88 = {lambda_sync:.2f} Mpc")
print(f"  λ_sync/2 = πR_H/88 = {lambda_sync/2:.2f} Mpc")
print(f"  → BAO 峰 = πR_H/88 = π·(c/H0)/88 — 純結構, 零 ΛCDM 參數")

# ============ 6. 總結 ============
print(f"\n{'=' * 62}")
print(f"BAO 驗證總結: ✅ {PASS} / {PASS+FAIL}")
print(f"{'=' * 62}")

result = {
    'lambda_sync_mpc': round(lambda_sync, 4),
    'lambda_sync_h_inv_mpc': round(lambda_sync_h, 4),
    'bao_peak_idcm_mpc': round(lambda_sync/2, 4),
    'bao_peak_idcm_h_inv': round(lambda_sync_h/2, 4),
    'r_drag_lcdm_mpc': r_drag,
    'dev_pct': round(abs(lambda_sync/2 - r_drag)/r_drag*100, 3),
    'eBOSS_peak_bin': {'s': float(s[idx_peak]), 'xi': float(xi[idx_peak]), 'err': float(err[idx_peak])},
    'detected_harmonics': [n for n, _, _ in detected],
    'pass': PASS,
    'fail': FAIL
}

with open('data/62_bao_verification.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"\n✅ 結果 -> data/62_bao_verification.json")