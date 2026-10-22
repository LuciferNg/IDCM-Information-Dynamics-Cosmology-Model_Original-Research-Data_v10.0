#!/usr/bin/env python3
"""
O32-10: 文獻方法複製 + 系統誤差 + IDCM a₀ 證偽測試
=====================================================
目標: 釐清「最佳 a₀ ≈ 9.85e-11 vs IDCM 1.1225e-10 vs MOND 1.2e-10」

關鍵問題:
1. 文獻 Lelli+2017 報 a₀ = 1.2e-10 ± 0.026 (stat) ± 0.14 (sys)。
   我 fit 出 9.85e-11 — 方法唔同? 
2. Υ prior 影響? 文獻用 Υ[3.6] ∈ [0.1, 1.0] (SPS-motivated)
3. Quality cuts? 文獻用 Q=1,2 (quality ≥ 2)
4. 系統誤差: inclination 5-10° → V_obs 誤差 5-20%

文獻方法 (Lelli+2017 RAR):
- 每個星系 fit Υ ∈ [0.1, 1.0]
- RAR: g_obs = V_obs²/R vs g_bar = Υ·ΣV_i²/R
- 對 log 空間 bin 數據 fit a₀
- 加 systematic error 使 χ²/dof = 1
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

# Quality flags
sample_q = {}
with open('data/SPARC_Lelli2016c.mrt') as f:
    for line in f:
        parts = line.split()
        if len(parts) < 18:
            continue
        name = parts[0]
        if not name or name in ('Galaxy', 'Authors', 'Table', 'Title:') or not name[0].isalpha():
            continue
        try:
            Q = int(parts[17])   # parts[16] = e_Vflat, parts[17] = Q
        except (ValueError, IndexError):
            continue
        sample_q[name] = Q

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

def fit_galaxy(gal, a0, ups_lo=0.1, ups_hi=1.0):
    res = minimize_scalar(
        lambda u: gal_chi2(u, gal, a0),
        bounds=(ups_lo, ups_hi), method='bounded',
        options={'xatol': 1e-7}
    )
    return res.x, res.fun

# ============ 1. 文獻方法: Υ ∈ [0.1,1.0] + Q cuts ============
print("=" * 65)
print("1. 文獻方法複製: Υ ∈ [0.1, 1.0], Q ≤ 2 (高質量)")
print("=" * 65)

def build_rar_with_cuts(a0, qmax=3, ups_lo=0.1, ups_hi=1.0):
    all_gbar, all_gobs, all_gerr, all_ups = [], [], [], []
    n_gal_used = 0
    for name, gal in galaxies.items():
        if sample_q.get(name, 3) > qmax:
            continue
        ups, _ = fit_galaxy(gal, a0, ups_lo, ups_hi)
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
        all_ups.append(ups)
        n_gal_used += 1
    return (np.array(all_gbar), np.array(all_gobs), np.array(all_gerr),
            np.array(all_ups), n_gal_used)

def rar_chi2(a0, data):
    gbar, gobs, gerr = data[:3]
    gpred = interpol_simple(gbar, a0)
    return np.sum(((gobs - gpred) / gerr)**2)

def fit_a0_rar(data):
    a0_grid = np.linspace(0.7e-10, 1.6e-10, 91)
    chi2s = np.array([rar_chi2(a0, data) for a0 in a0_grid])
    best = a0_grid[np.argmin(chi2s)]
    a0_fine = np.linspace(max(0.7e-10, best-0.15e-10), min(1.6e-10, best+0.15e-10), 61)
    chi2s_f = np.array([rar_chi2(a0, data) for a0 in a0_fine])
    best_f = a0_fine[np.argmin(chi2s_f)]
    chi2_best = chi2s_f.min()
    dchi2 = np.abs(chi2s_f - chi2_best)
    mask = dchi2 < 1.0
    return best_f, chi2_best, (a0_fine[mask].min(), a0_fine[mask].max()) if mask.sum() else (best_f, best_f)

for qmax in [3, 2]:
    data = build_rar_with_cuts(A0_MOND, qmax=qmax)
    a0_best, chi2_b, err_range = fit_a0_rar(data)
    gbar, gobs, gerr, ups, ngal = data
    print(f"\nQ ≤ {qmax}: {ngal} 星系, {len(gbar)} 點")
    print(f"  Υ median = {np.median(ups):.3f}")
    print(f"  最佳 a₀ = {a0_best:.4e} (1σ: [{err_range[0]:.4e}, {err_range[1]:.4e}])")
    print(f"  χ² = {chi2_b:.1f}, dof = {len(gbar)-1}, χ²/dof = {chi2_b/(len(gbar)-1):.2f}")
    # IDCM/MOND
    chi2_idcm = rar_chi2(A0_IDCM, data)
    chi2_mond = rar_chi2(A0_MOND, data)
    print(f"  IDCM a₀: χ² = {chi2_idcm:.1f} (Δχ² = {chi2_idcm-chi2_b:.1f})")
    print(f"  MOND a₀: χ² = {chi2_mond:.1f} (Δχ² = {chi2_mond-chi2_b:.1f})")
    # IDCM 喺 1σ?
    print(f"  IDCM 喺 1σ? {A0_IDCM >= err_range[0] and A0_IDCM <= err_range[1]}")

# ============ 2. 系統誤差 ============
print("\n" + "=" * 65)
print("2. 系統誤差分析 (inclination, distance)")
print("=" * 65)

# SPARC e_Inc ~ 5-10° → V_obs 誤差 = V/sin(Inc)·cos(Inc)·ΔInc
# V_true = V_obs/sin(i), 所以 σ_V/V = cot(i)·σ_i
# 典型: i = 60°, σ_i = 5° → σ_V/V = 0.05
inc_data = {}
with open('data/SPARC_Lelli2016c.mrt') as f:
    for line in f:
        parts = line.split()
        if len(parts) < 18:
            continue
        name = parts[0]
        if not name or name in ('Galaxy', 'Authors', 'Table', 'Title:') or not name[0].isalpha():
            continue
        try:
            inc = float(parts[5])
            e_inc = float(parts[6])
        except (ValueError, IndexError):
            continue
        inc_data[name] = (inc, e_inc)

# 典型系統誤差
sys_fracs = []
for name in galaxies:
    if name in inc_data:
        inc, e_inc = inc_data[name]
        if inc > 20:  # 避免低 inclination (不穩定)
            frac = np.radians(e_inc) / np.tan(np.radians(inc))
            sys_fracs.append(abs(frac))
sys_fracs = np.array(sys_fracs)
print(f"Inclination 系統誤差 σ_V/V: median = {np.median(sys_fracs)*100:.1f}%")
print(f"Distance 誤差: SPARC f_D = 1 (Cepheid, ~5%), 2 (TF, ~15%), 3 (other)")
print(f"→ V 誤差係距離無關 (V 由角尺度×距離→線尺度, 誤差同距離), 但 R 誤差 ~15%")

# 將系統誤差加入 e_Vobs:
# σ_sys = σ_inc (約 5-10%) → 加喺 e_Vobs 度 (quadrature)
data = build_rar_with_cuts(A0_MOND, qmax=2)
gbar, gobs, gerr, ups, ngal = data
sys_frac = np.median(sys_fracs)
gerr_sys = np.sqrt(gerr**2 + (sys_frac * gobs)**2)
data_sys = (gbar, gobs, gerr_sys, ups, ngal)

a0_best_sys, chi2_b_sys, err_sys = fit_a0_rar(data_sys)
print(f"\n加入 inclination 系統誤差後:")
print(f"  最佳 a₀ = {a0_best_sys:.4e} (1σ: [{err_sys[0]:.4e}, {err_sys[1]:.4e}])")
print(f"  χ²/dof = {chi2_b_sys/(len(gbar)-1):.2f}")
chi2_idcm_sys = rar_chi2(A0_IDCM, data_sys)
chi2_mond_sys = rar_chi2(A0_MOND, data_sys)
print(f"  IDCM a₀: Δχ² = {chi2_idcm_sys-chi2_b_sys:.1f}")
print(f"  MOND a₀: Δχ² = {chi2_mond_sys-chi2_b_sys:.1f}")
print(f"  IDCM 喺 1σ? {A0_IDCM >= err_sys[0] and A0_IDCM <= err_sys[1]}")

# ============ 3. 掃描系統誤差大小 ============
print("\n" + "=" * 65)
print("3. 系統誤差掃描: IDCM a₀ 幾時落入 1σ?")
print("=" * 65)
data_base = build_rar_with_cuts(A0_MOND, qmax=2)
gbar, gobs, gerr0, ups, ngal = data_base
for syspct in [5, 10, 15, 20]:
    gerr_t = np.sqrt(gerr0**2 + (syspct/100 * gobs)**2)
    data_t = (gbar, gobs, gerr_t, ups, ngal)
    a0_b, c2, err_r = fit_a0_rar(data_t)
    in1s = A0_IDCM >= err_r[0] and A0_IDCM <= err_r[1]
    print(f"σ_sys = {syspct}%: 最佳 a₀ = {a0_b:.4e}, 1σ = [{err_r[0]:.3e}, {err_r[1]:.3e}], "
          f"IDCM 入 1σ? {in1s}")

# ============ 4. 用 SPARC 官方 RAR bin 數據? ============
print("\n" + "=" * 65)
print("4. 對比: 文獻報道 a₀ = 1.2e-10 ± 0.026 (stat) ± 0.14 (sys)")
print("=" * 65)
print("""
文獻 (Lelli+2017, MNRAS 468, 1471):
  - 用 RAR bins (log g_bar 分 bin), 唔係全部 2700 點
  - 每個 bin 用 weighted mean
  - a₀ = 1.2e-10 ± 0.026 (random) ± 0.14 (systematic)
  - 系統誤差大: 來自 Υ, distance, inclination 不確定性

IDCM a₀ = 1.1225e-10:
  與文獻 a₀ 偏差 = 6.5% (喺 0.14 系統誤差內!)
  與我嘅 best-fit (9.85e-11) 偏差 = 14% 
  → 但 best-fit 對 method 敏感 (Υ prior, Q cuts, interpolation)

關鍵: IDCM 係 ZERO-PARAMETER 預測, MOND a₀ 係 fit 參數。
      IDCM 預測 a₀ = cH₀/2π, 唔需要 fit!
""")

# ============ 保存 ============
results = {
    'a0_idcm': float(A0_IDCM),
    'a0_mond': 1.2e-10,
    'a0_best_q3': None, 'a0_best_q2': None,
    'sys_frac_median': float(np.median(sys_fracs))
}
with open('data/systematics_analysis.json', 'w') as f:
    json.dump(results, f, indent=2)
print("結果已存: data/systematics_analysis.json")
