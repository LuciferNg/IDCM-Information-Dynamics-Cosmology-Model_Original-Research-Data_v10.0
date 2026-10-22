#!/usr/bin/env python3
"""
O32-11: 官方 RAR bins + BTFR 驗證 — IDCM a₀ 零參數測試
=========================================================
用 Lelli+2017 官方發布嘅 RAR bins (14 bins) 直接測試:
- IDCM a₀ = cH₀/2π = 1.1225e-10 (零自由參數)
- vs MOND 最佳 a₀ = 1.2e-10 (fit)

BTFR 官方數據 (Lelli+2016):
- log(Mb) vs log(Vf), 驗證斜率 4
- IDCM 預測: M = V⁴/(G·a₀), 零參數
"""
import numpy as np
import json

c = 299792.458
R_H = 4129.94
H0_idcm = c / R_H
Mpc_to_km = 3.085677581e19
c_ms = c * 1e3
H0_s = H0_idcm / Mpc_to_km
G = 6.674e-11
Msun = 1.989e30

A0_IDCM = c_ms * H0_s / (2 * np.pi)   # 1.1225e-10
A0_MOND = 1.2e-10

# ============ 1. RAR bins ============
print("=" * 60)
print("1. 官方 RAR bins (Lelli+2017, 14 bins)")
print("=" * 60)

# 解析 RARbins
rar_bins = []
with open('data/RARbins.mrt') as f:
    for line in f:
        line = line.strip()
        parts = line.split()
        if len(parts) == 4:
            try:
                gbar_l = float(parts[0])
                gobs_l = float(parts[1])
                sd = float(parts[2])
                n = int(parts[3])
                rar_bins.append((gbar_l, gobs_l, sd, n))
            except ValueError:
                continue

rar_bins = np.array(rar_bins)
print(f"RAR bins: {len(rar_bins)}")
print(f"{'log gbar':>8} {'log gobs':>8} {'IDCM pred':>9} {'MOND pred':>9} {'obs-pred_IDCM':>12}")

def interp_log(gbar_log, a0):
    """RAR 插值函數 (log 空間)"""
    gbar = 10**gbar_log
    y = a0 / np.maximum(gbar, 1e-30)
    gobs = gbar * (1 + np.sqrt(1 + 4 * y)) / 2
    return np.log10(gobs)

chi2_idcm = 0
chi2_mond = 0
for gbar_l, gobs_l, sd, n in rar_bins:
    pred_idcm = interp_log(gbar_l, A0_IDCM)
    pred_mond = interp_log(gbar_l, A0_MOND)
    chi2_idcm += ((gobs_l - pred_idcm) / sd)**2
    chi2_mond += ((gobs_l - pred_mond) / sd)**2
    print(f"{gbar_l:>8.2f} {gobs_l:>8.2f} {pred_idcm:>9.3f} {pred_mond:>9.3f} "
          f"{(gobs_l-pred_idcm):>+12.3f}")

dof = len(rar_bins) - 1
print(f"\nχ² (IDCM, 零參數): {chi2_idcm:.2f}, dof = {dof}, χ²/dof = {chi2_idcm/dof:.3f}")
print(f"χ² (MOND, 1 fit 參數): {chi2_mond:.2f}, dof = {dof}, χ²/dof = {chi2_mond/dof:.3f}")
print(f"Δχ² = {chi2_idcm - chi2_mond:.2f} (IDCM - MOND)")
print(f"→ IDCM 用 0 參數, MOND 用 1 參數")

# a₀ 掃描 (官方 bins)
a0_grid = np.linspace(0.8e-10, 1.5e-10, 71)
chi2s = []
for a0 in a0_grid:
    c2 = sum(((gobs_l - interp_log(gbar_l, a0)) / sd)**2
             for gbar_l, gobs_l, sd, n in rar_bins)
    chi2s.append(c2)
chi2s = np.array(chi2s)
best = a0_grid[np.argmin(chi2s)]
print(f"\n官方 bins 最佳 a₀ = {best:.4e} (χ² = {chi2s.min():.2f})")
print(f"IDCM a₀ = {A0_IDCM:.4e}")
print(f"最佳/IDCM = {best/A0_IDCM:.4f}")
# 1σ
dchi2 = np.abs(chi2s - chi2s.min())
mask = dchi2 < 1.0
print(f"1σ 範圍: [{a0_grid[mask].min():.4e}, {a0_grid[mask].max():.4e}]")
print(f"IDCM 喺 1σ? {A0_IDCM >= a0_grid[mask].min() and A0_IDCM <= a0_grid[mask].max()}")

# ============ 2. BTFR ============
print("\n" + "=" * 60)
print("2. 官方 BTFR (Lelli+2016)")
print("=" * 60)

btfr = []
with open('data/BTFR_Lelli2016a.mrt') as f:
    for line in f:
        parts = line.split()
        if len(parts) < 9:
            continue
        name = parts[0]
        if not name or name in ('Galaxy', 'Authors', 'Table', 'Title:') or not name[0].isalpha():
            continue
        try:
            logMb = float(parts[4])   # log(Mb/Msun) — parts[3]=f_Dist
            elogMb = float(parts[5])
            logVf = float(parts[6])   # log(Vf/km/s) — parts[5]=e_logMb
            elogVf = float(parts[7])
            Fg = float(parts[8])
            btfr.append((name, logMb, elogMb, logVf, elogVf, Fg))
        except ValueError:
            continue

btfr = np.array(btfr, dtype=object)
print(f"BTFR 星系數: {len(btfr)}")

logMb = btfr[:, 1].astype(float)
logVf = btfr[:, 3].astype(float)
elogMb = btfr[:, 2].astype(float)
elogVf = btfr[:, 4].astype(float)

# 線性 fit (orthogonal 或 standard)
slope, intercept = np.polyfit(logVf, logMb, 1)
print(f"數據 fit: log(Mb) = {slope:.2f}·log(Vf) + {intercept:.2f}")
print(f"斜率: {slope:.2f} (理論 4.00)")
print(f"scatter: {np.sqrt(np.mean((logMb - (slope*logVf + intercept))**2)):.3f} dex")

# IDCM 預測 (零參數):
# M = V⁴/(G·a₀), V 單位 m/s = 10^logVf × 1e3
# log10(M/Msun) = 4·logVf + 4·log10(1e3) - log10(G·a₀) - log10(Msun)
logMb_idcm = 4*logVf + 4*np.log10(1e3) - np.log10(G*A0_IDCM) - np.log10(Msun)
resid_idcm = logMb - logMb_idcm
rms_idcm = np.sqrt(np.mean(resid_idcm**2))
print(f"\nIDCM 預測 (斜率 4, 零參數):")
print(f"  rms = {rms_idcm:.3f} dex")

# MOND 預測 (a₀ = 1.2e-10)
logMb_mond = 4*logVf + 4*np.log10(1e3) - np.log10(G*A0_MOND) - np.log10(Msun)
rms_mond = np.sqrt(np.mean((logMb - logMb_mond)**2))
print(f"MOND 預測 (a₀ = 1.2e-10):")
print(f"  rms = {rms_mond:.3f} dex")

# fit 斜率 4 固定嘅截距
logMb_fit4 = logMb - 4*logVf
intercept4 = np.mean(logMb_fit4)
print(f"\n固定斜率 4 嘅最佳截距: {intercept4:.3f}")
print(f"IDCM 預測截距: {4*np.log10(1e3) - np.log10(G*A0_IDCM) - np.log10(Msun):.3f}")
print(f"MOND 預測截距: {4*np.log10(1e3) - np.log10(G*A0_MOND) - np.log10(Msun):.3f}")
print(f"Δ(截距) IDCM vs 數據: {intercept4 - (4*np.log10(1e3) - np.log10(G*A0_IDCM) - np.log10(Msun)):.3f} dex")
print(f"Δ(截距) MOND vs 數據: {intercept4 - (4*np.log10(1e3) - np.log10(G*A0_MOND) - np.log10(Msun)):.3f} dex")

# χ² 比較 (BTFR)
chi2_btfr_idcm = np.sum((logMb - logMb_idcm)**2 / (elogMb**2 + (4*elogVf)**2))
chi2_btfr_mond = np.sum((logMb - logMb_mond)**2 / (elogMb**2 + (4*elogVf)**2))
print(f"\nBTFR χ² (IDCM 零參數): {chi2_btfr_idcm:.1f}")
print(f"BTFR χ² (MOND a₀=1.2e-10): {chi2_btfr_mond:.1f}")

# ============ 保存 ============
with open('data/official_verification.json', 'w') as f:
    json.dump({
        'rar': {
            'a0_idcm': float(A0_IDCM), 'chi2_idcm': float(chi2_idcm),
            'a0_mond': float(A0_MOND), 'chi2_mond': float(chi2_mond),
            'a0_best': float(best), 'chi2_best': float(chi2s.min()),
            'n_bins': len(rar_bins)
        },
        'btfr': {
            'slope_fit': float(slope),
            'rms_idcm': float(rms_idcm),
            'rms_mond': float(rms_mond),
            'intercept_fit4': float(intercept4),
            'intercept_idcm': float(4*np.log10(1e3) - np.log10(G*A0_IDCM) - np.log10(Msun)),
            'intercept_mond': float(4*np.log10(1e3) - np.log10(G*A0_MOND) - np.log10(Msun)),
            'n_gal': len(btfr)
        }
    }, f, indent=2)
print("\n結果已存: data/official_verification.json")
