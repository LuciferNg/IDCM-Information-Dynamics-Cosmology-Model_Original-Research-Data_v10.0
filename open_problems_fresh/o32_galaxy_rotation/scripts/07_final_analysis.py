#!/usr/bin/env python3
"""
O32-07: RAR 完整分析 — 修正 Υ + BTFR + 多星系展示
===================================================
問題: 上一個 script 嘅 Υ fit 出 49 (median) — 有 bug:
fit_galaxy 回傳 (res.x, res.fun), 但 zip(*[fit_galaxy(...)]) 解包錯位。
修正: 直接收集 fit 結果。

同時:
1. RAR direct fit 最佳 a₀ vs IDCM vs MOND (確立 1.115e-10 ≈ 1.1225e-10 結果)
2. BTFR: log M_bary vs log V_f, 斜率 = 4 (MOND 預測)
3. 選 3 個代表星系出旋轉曲線圖
"""
import numpy as np
from scipy.optimize import minimize_scalar
import json

c = 299792.458
R_H = 4129.94
H0_idcm = c / R_H
Mpc_to_km = 3.085677581e19
c_ms = c * 1e3
H0_s = H0_idcm / Mpc_to_km
kpc_to_m = 3.085677581e19
G = 6.674e-11
Msun = 1.989e30
Lsun = 3.828e26  # W
lsun_36_to_Msun = 0.47  # M/L[3.6] ~ 0.47 (IRAC 3.6μm)

A0_IDCM = c_ms * H0_s / (2 * np.pi)   # 1.1225e-10
A0_MOND = 1.2e-10

def parse_mass_models(path):
    galaxies = {}
    with open(path) as f:
        for line in f:
            if line.startswith(('Title', 'Authors', 'Table', 'Byte', '---', 'Note',
                                '       Spitzer', '======')):
                continue
            line = line.rstrip('\n').rstrip('\r')
            if len(line.strip()) < 40:
                continue
            try:
                name = line[0:11].strip()
                R = float(line[19:25])
                Vobs = float(line[26:32])
                eVobs = float(line[33:38])
                Vgas = float(line[39:45])
                Vdisk = float(line[46:52])
                Vbul = float(line[53:59])
            except ValueError:
                continue
            if name not in galaxies:
                galaxies[name] = []
            galaxies[name].append({
                'R': R, 'Vobs': Vobs, 'eVobs': eVobs,
                'Vgas': Vgas, 'Vdisk': Vdisk, 'Vbul': Vbul
            })
    return galaxies

galaxies = parse_mass_models('data/MassModels_Lelli2016c.mrt')

def interpol_simple(gbar, a0):
    y = a0 / np.maximum(gbar, 1e-30)
    return gbar * (1 + np.sqrt(1 + 4 * y)) / 2

def gal_chi2(ups, gal, a0):
    R = np.array([p['R'] for p in gal]) * kpc_to_m
    Vobs = np.array([p['Vobs'] for p in gal])
    eVobs = np.array([p['eVobs'] for p in gal])
    Vgas_ms = np.array([p['Vgas'] for p in gal]) * 1e3
    Vdisk_ms = np.array([p['Vdisk'] for p in gal]) * 1e3
    Vbul_ms = np.array([p['Vbul'] for p in gal]) * 1e3
    Vbar2 = ups * (Vdisk_ms**2 + Vbul_ms**2) + Vgas_ms**2
    gbar = Vbar2 / R
    gobs_pred = interpol_simple(gbar, a0)
    Vpred = np.sqrt(np.maximum(R * gobs_pred, 0)) / 1e3
    return np.sum(((Vobs - Vpred) / eVobs)**2)

def fit_galaxy(gal, a0, ups_lo=0.05, ups_hi=2.0):
    res = minimize_scalar(
        lambda u: gal_chi2(u, gal, a0),
        bounds=(ups_lo, ups_hi), method='bounded',
        options={'xatol': 1e-6}
    )
    return res.x, res.fun

# ============ 1. RAR direct fit (修正) ============
print("=== 1. RAR direct fit (修正版) ===")

def build_rar_err(a0, ups_lo=0.05, ups_hi=2.0):
    all_gbar, all_gobs, all_gerr = [], [], []
    ups_all = {}
    for name, gal in galaxies.items():
        ups, _ = fit_galaxy(gal, a0, ups_lo, ups_hi)
        ups_all[name] = ups
        R = np.array([p['R'] for p in gal]) * kpc_to_m
        Vobs_ms = np.array([p['Vobs'] for p in gal]) * 1e3
        eVobs_ms = np.array([p['eVobs'] for p in gal]) * 1e3
        Vgas_ms = np.array([p['Vgas'] for p in gal]) * 1e3
        Vdisk_ms = np.array([p['Vdisk'] for p in gal]) * 1e3
        Vbul_ms = np.array([p['Vbul'] for p in gal]) * 1e3
        Vbar2 = ups * (Vdisk_ms**2 + Vbul_ms**2) + Vgas_ms**2
        gbar = Vbar2 / R
        gobs = Vobs_ms**2 / R
        gerr = 2 * Vobs_ms * eVobs_ms / R
        all_gbar.extend(gbar)
        all_gobs.extend(gobs)
        all_gerr.extend(gerr)
    return (np.array(all_gbar), np.array(all_gobs), np.array(all_gerr)), ups_all

def rar_chi2(a0, data):
    gbar, gobs, gerr = data
    gpred = interpol_simple(gbar, a0)
    return np.sum(((gobs - gpred) / gerr)**2)

# 用 IDCM a₀ fit Υ
data, ups_all = build_rar_err(A0_IDCM)
ups_arr = np.array(list(ups_all.values()))
print(f"Υ (IDCM a₀ fit): median={np.median(ups_arr):.3f}, "
      f"16-84%=[{np.percentile(ups_arr,16):.3f},{np.percentile(ups_arr,84):.3f}]")

# a₀ 掃描
a0_grid = np.linspace(0.8e-10, 1.4e-10, 61)
chi2s = np.array([rar_chi2(a0, data) for a0 in a0_grid])
best = a0_grid[np.argmin(chi2s)]
a0_fine = np.linspace(best-0.1e-10, best+0.1e-10, 61)
chi2s_f = np.array([rar_chi2(a0, data) for a0 in a0_fine])
best_f = a0_fine[np.argmin(chi2s_f)]
chi2_best = chi2s_f.min()

print(f"RAR direct 最佳 a₀ = {best_f:.4e} (χ² = {chi2_best:.1f}, N = {len(data[0])})")

# 1σ
dchi2 = np.abs(chi2s_f - chi2_best)
mask = dchi2 < 1.0
a0_lo, a0_hi = a0_fine[mask].min(), a0_fine[mask].max()
print(f"1σ 範圍: [{a0_lo:.4e}, {a0_hi:.4e}]")

chi2_idcm = rar_chi2(A0_IDCM, data)
chi2_mond = rar_chi2(A0_MOND, data)
print(f"\nIDCM a₀ = {A0_IDCM:.4e}: χ² = {chi2_idcm:.1f}, Δχ² = {chi2_idcm-chi2_best:.1f}")
print(f"MOND a₀ = {A0_MOND:.4e}: χ² = {chi2_mond:.1f}, Δχ² = {chi2_mond-chi2_best:.1f}")
print(f"IDCM 喺 1σ? {A0_IDCM >= a0_lo and A0_IDCM <= a0_hi}")
print(f"MOND 喺 1σ? {A0_MOND >= a0_lo and A0_MOND <= a0_hi}")
print(f"最佳/IDCM = {best_f/A0_IDCM:.4f}")

# RAR scatter
gpred_idcm = interpol_simple(data[0], A0_IDCM)
resid = np.log10(data[1]) - np.log10(gpred_idcm)
print(f"RAR scatter (IDCM a₀): {np.sqrt(np.mean(resid**2)):.4f} dex")

# ============ 2. BTFR ============
print("\n=== 2. BTFR (Baryonic Tully-Fisher) ===")
# 質量: M_bary = Υ·L[3.6] + 1.33·MHI (L 單位 1e9 Lsun, MHI 單位 1e9 Msun)
sample = {}
with open('data/SPARC_Lelli2016c.mrt') as f:
    for line in f:
        parts = line.split()
        if len(parts) < 17:
            continue
        name = parts[0]
        if not name or name in ('Galaxy', 'Authors', 'Table', 'Title:') or not name[0].isalpha():
            continue
        try:
            L36 = float(parts[7])    # 1e9 Lsun
            MHI = float(parts[13])   # 1e9 Msun
            Vflat = float(parts[15]) # km/s
        except (ValueError, IndexError):
            continue
        sample[name] = {'L36': L36, 'MHI': MHI, 'Vflat': Vflat}

btfr = []
for name in sample:
    if name not in ups_all:
        continue
    L36 = sample[name]['L36']
    MHI = sample[name]['MHI']
    ups = ups_all[name]
    Mbary = (ups * L36 + 1.33 * MHI)  # 1e9 Msun
    Vflat = sample[name]['Vflat']
    if Vflat > 0 and Mbary > 0:
        btfr.append({'name': name, 'Mbary': Mbary, 'Vflat': Vflat})

btfr = np.array([(b['Mbary'], b['Vflat']) for b in btfr])
print(f"BTFR 星系數: {len(btfr)}")

# 線性回歸 log M_bary vs log V_f (斜率 = 4 預測)
logM = np.log10(btfr[:, 0])  # 1e9 Msun 單位
logV = np.log10(btfr[:, 1])
slope, intercept = np.polyfit(logV, logM, 1)
print(f"BTFR 斜率: {slope:.2f} (MOND 預測 4.0)")
print(f"BTFR 截距: {intercept:.2f} (M_bary = 10^{intercept} × V^{slope})")
print(f"M_bary(1e9 Msun) vs V_fit: logM = {slope:.2f}·logV + {intercept:.2f}")

# 殘差 scatter
pred = slope * logV + intercept
print(f"BTFR scatter: {np.sqrt(np.mean((logM - pred)**2)):.3f} dex")

# ============ 3. 代表星系 ============
print("\n=== 3. 代表星系 (IDCM a₀ 預測) ===")
for gname in ['NGC2403', 'NGC3198', 'NGC6503']:
    if gname in galaxies:
        gal = galaxies[gname]
        ups, chi2 = fit_galaxy(gal, A0_IDCM)
        R = np.array([p['R'] for p in gal])
        Vobs = np.array([p['Vobs'] for p in gal])
        eVobs = np.array([p['eVobs'] for p in gal])
        Vgas = np.array([p['Vgas'] for p in gal])
        Vdisk = np.array([p['Vdisk'] for p in gal])
        Vbul = np.array([p['Vbul'] for p in gal])

        R_m = R * kpc_to_m
        Vbar2 = ups * ((Vdisk*1e3)**2 + (Vbul*1e3)**2) + (Vgas*1e3)**2
        gbar = Vbar2 / R_m
        gpred = interpol_simple(gbar, A0_IDCM)
        Vpred = np.sqrt(R_m * gpred) / 1e3

        # 外半徑
        outer_mask = R > 0.5 * R.max()
        print(f"\n{gname}: Υ = {ups:.3f}, χ² = {chi2:.1f}")
        print(f"  R 範圍: {R.min():.2f}-{R.max():.2f} kpc")
        print(f"  外半徑 V_obs = {Vobs[outer_mask].mean():.1f} ± {eVobs[outer_mask].mean():.1f}")
        print(f"  外半徑 V_pred = {Vpred[outer_mask].mean():.1f}")

# ============ 保存 ============
with open('data/rar_final.json', 'w') as f:
    json.dump({
        'a0_best': float(best_f), 'chi2_best': float(chi2_best),
        'a0_idcm': float(A0_IDCM), 'chi2_idcm': float(chi2_idcm),
        'a0_mond': float(A0_MOND), 'chi2_mond': float(chi2_mond),
        'a0_lo': float(a0_lo), 'a0_hi': float(a0_hi),
        'idcm_in_1sigma': bool(A0_IDCM >= a0_lo and A0_IDCM <= a0_hi),
        'rar_scatter': float(np.sqrt(np.mean(resid**2))),
        'btfr_slope': float(slope), 'btfr_intercept': float(intercept),
        'btfr_n': len(btfr)
    }, f, indent=2)
print("\n結果已存: data/rar_final.json")
