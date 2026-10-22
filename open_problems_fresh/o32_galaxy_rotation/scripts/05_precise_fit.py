#!/usr/bin/env python3
"""
O32-05: RAR 精確擬合 — scipy optimize + 文獻方法
=================================================
改進:
1. 用 scipy.optimize.minimize_scalar fit 每個星系 Υ (連續優化)
2. 檢查 Υ 分佈合理性
3. 掃描 a₀ 用更精細 grid
4. 對比 IDCM a₀ vs MOND a₀ vs 數據最佳

關鍵: 文獻 (Lelli+2017) 報道 RAR scatter = 0.13 dex, χ²/dof 高係因為
e_Vobs 只係隨機誤差 (non-circular motion), 唔包含系統誤差。
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

def gal_chi2(ups, gal, a0, interp_fn=interpol_simple):
    R = np.array([p['R'] for p in gal]) * kpc_to_m
    Vobs = np.array([p['Vobs'] for p in gal])
    eVobs = np.array([p['eVobs'] for p in gal])
    Vgas_ms = np.array([p['Vgas'] for p in gal]) * 1e3
    Vdisk_ms = np.array([p['Vdisk'] for p in gal]) * 1e3
    Vbul_ms = np.array([p['Vbul'] for p in gal]) * 1e3
    Vbar2 = ups * (Vdisk_ms**2 + Vbul_ms**2) + Vgas_ms**2
    gbar = Vbar2 / R
    gobs_pred = interp_fn(gbar, a0)
    Vpred = np.sqrt(np.maximum(R * gobs_pred, 0)) / 1e3
    return np.sum(((Vobs - Vpred) / eVobs)**2)

def fit_galaxy(gal, a0):
    """連續優化 Υ ∈ [0.01, 3.0]"""
    res = minimize_scalar(
        lambda u: gal_chi2(u, gal, a0),
        bounds=(0.01, 3.0), method='bounded',
        options={'xatol': 1e-6}
    )
    return res.x, res.fun

def total_chi2_opt(a0):
    tot = 0
    ups_list = []
    for name, gal in galaxies.items():
        ups, chi2 = fit_galaxy(gal, a0)
        tot += chi2
        ups_list.append(ups)
    return tot, ups_list

# ============ 驗證: 用文獻 a₀ = 1.2e-10 檢查 Υ 分佈 ============
print("=== Υ 分佈檢查 (a₀ = 1.2e-10, MOND 文獻值) ===")
_, ups_ref = total_chi2_opt(A0_MOND)
ups_arr = np.array(ups_ref)
print(f"Υ: min={ups_arr.min():.3f}, median={np.median(ups_arr):.3f}, max={ups_arr.max():.3f}")
print(f"Υ > 1.0 嘅星系數: {(ups_arr > 1.0).sum()} / {len(ups_arr)}")
print(f"Υ < 0.1 嘅星系數: {(ups_arr < 0.1).sum()} / {len(ups_arr)}")
# 文獻: Υ[3.6] 中位數 ~0.5, 範圍 0.1-1.0 (Lelli+2016)
# 如果太多 Υ > 1.0 或 < 0.1 → 質量模型有問題

# ============ a₀ 掃描 (精確) ============
print("\n=== a₀ 掃描 (scipy optimize Υ) ===")
a0_grid = np.linspace(0.7e-10, 1.5e-10, 49)
results = []
for a0 in a0_grid:
    tot, _ = total_chi2_opt(a0)
    results.append((a0, tot))
    print(f"  a₀ = {a0:.3e}: χ² = {tot:.1f}")

results = np.array(results)
best_idx = np.argmin(results[:, 1])
a0_best = results[best_idx, 0]
chi2_best = results[best_idx, 1]

# 精細掃描
a0_fine = np.linspace(max(0.7e-10, a0_best-0.08e-10), min(1.5e-10, a0_best+0.08e-10), 33)
for a0 in a0_fine:
    tot, _ = total_chi2_opt(a0)
    results = np.vstack([results, [a0, tot]])
best_idx = np.argmin(results[:, 1])
a0_best = results[best_idx, 0]
chi2_best = results[best_idx, 1]

n_pts = sum(len(v) for v in galaxies.values())
n_gal = len(galaxies)
dof = n_pts - n_gal - 1

print(f"\n最佳 a₀ = {a0_best:.4e} (χ²/dof = {chi2_best/dof:.3f})")

# 1σ 誤差
dchi2 = results[:, 1] - chi2_best
mask = dchi2 < 1.0
a0_lo = results[mask, 0].min()
a0_hi = results[mask, 0].max()
print(f"1σ 範圍: [{a0_lo:.4e}, {a0_hi:.4e}]")

# 對比
chi2_idcm, _ = total_chi2_opt(A0_IDCM)
chi2_mond, _ = total_chi2_opt(A0_MOND)
print(f"\nMOND  a₀ = {A0_MOND:.4e}: χ² = {chi2_mond:.1f}, Δχ² = {chi2_mond-chi2_best:.1f}")
print(f"IDCM  a₀ = {A0_IDCM:.4e}: χ² = {chi2_idcm:.1f}, Δχ² = {chi2_idcm-chi2_best:.1f}")
print(f"MOND 喺 1σ? {A0_MOND >= a0_lo and A0_MOND <= a0_hi}")
print(f"IDCM 喺 1σ? {A0_IDCM >= a0_lo and A0_IDCM <= a0_hi}")

# ============ 重要: IDCM 修正? ============
print("\n=== IDCM 結構修正分析 ===")
print(f"最佳/IDCM = {a0_best/A0_IDCM:.4f}")
phi = (1 + np.sqrt(5)) / 2
print(f"φ⁻¹/2 = {1/phi/2:.4f}")
print(f"ε = φ⁻¹/4 = {1/phi/4:.4f}")
print(f"φ⁻² = {1/phi**2:.4f}")
# a₀_best/a₀_idcm = 0.8886 → 接近 φ⁻¹·φ⁻¹? = 0.382, 唔啱
# 或者 = 1 - ε = 0.8455? 差 5%
# 或者 = 1/(1+ε) = 0.8662? 差 2.6%
print(f"1/(1+ε) = {1/(1+1/phi/4):.4f} (差 {abs(1/(1+1/phi/4)-a0_best/A0_IDCM)/(a0_best/A0_IDCM)*100:.1f}%)")
print(f"1-ε = {1-1/phi/4:.4f} (差 {abs(1-1/phi/4-a0_best/A0_IDCM)/(a0_best/A0_IDCM)*100:.1f}%)")

with open('data/rar_precise_fit.json', 'w') as f:
    json.dump({
        'a0_best': float(a0_best), 'chi2_best': float(chi2_best),
        'a0_idcm': float(A0_IDCM), 'chi2_idcm': float(chi2_idcm),
        'a0_mond': float(A0_MOND), 'chi2_mond': float(chi2_mond),
        'a0_lo': float(a0_lo), 'a0_hi': float(a0_hi),
        'n_gal': n_gal, 'n_pts': n_pts,
        'ups_median_mond': float(np.median(ups_arr))
    }, f, indent=2)
print("\n結果已存: data/rar_precise_fit.json")
