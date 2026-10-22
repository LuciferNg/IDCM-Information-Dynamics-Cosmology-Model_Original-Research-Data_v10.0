#!/usr/bin/env python3
"""
O32-09: GLOBAL JOINT FIT — a₀ + 所有 Υ 同時優化
==================================================
方法: 
- 參數: log10(a₀) + 175 個 Υ
- 對每個候選 a₀, 每個星系獨立 fit Υ (inner loop)
- outer loop: 掃描 a₀ → 全局最優

呢個等同於「同時 fit」因為 Υ 之間互相獨立 (只通過 a₀ 耦合)。
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
        options={'xatol': 1e-7}
    )
    return res.x, res.fun

def total_chi2(a0):
    tot = 0.0
    ups = {}
    for name, gal in galaxies.items():
        u, c2 = fit_galaxy(gal, a0)
        tot += c2
        ups[name] = u
    return tot, ups

# ============ 全局掃描 (密集) ============
print("=== GLOBAL JOINT FIT: a₀ + Υ 同時優化 ===")
print(f"IDCM 結構 a₀ = {A0_IDCM:.6e}")

# 粗掃
a0_grid = np.linspace(0.9e-10, 1.3e-10, 41)
results = []
for a0 in a0_grid:
    tot, _ = total_chi2(a0)
    results.append((a0, tot))

results = np.array(results)
best = results[np.argmin(results[:, 1])]

# 精細掃
a0_fine = np.linspace(best[0]-0.15e-10, best[0]+0.15e-10, 61)
for a0 in a0_fine:
    tot, _ = total_chi2(a0)
    results = np.vstack([results, [a0, tot]])

best_idx = np.argmin(results[:, 1])
a0_best = results[best_idx, 0]
chi2_best = results[best_idx, 1]

n_pts = sum(len(v) for v in galaxies.values())
n_gal = len(galaxies)
dof = n_pts - n_gal - 1

print(f"\n全局最佳 a₀ = {a0_best:.6e} m/s²")
print(f"χ²_best = {chi2_best:.1f}, dof = {dof}, χ²/dof = {chi2_best/dof:.3f}")

# 1σ (Δχ² = 1)
dchi2 = np.abs(results[:, 1] - chi2_best)
mask = dchi2 < 1.0
a0_lo, a0_hi = results[mask, 0].min(), results[mask, 0].max()
print(f"1σ 範圍: [{a0_lo:.6e}, {a0_hi:.6e}]")

# 對比
chi2_idcm, ups_idcm = total_chi2(A0_IDCM)
chi2_mond, _ = total_chi2(1.2e-10)
print(f"\nIDCM a₀ = {A0_IDCM:.6e}: χ² = {chi2_idcm:.1f}, Δχ² = {chi2_idcm-chi2_best:.1f}")
print(f"MOND a₀ = 1.200e-10: χ² = {chi2_mond:.1f}, Δχ² = {chi2_mond-chi2_best:.1f}")
print(f"IDCM 喺 1σ? {A0_IDCM >= a0_lo and A0_IDCM <= a0_hi}")
print(f"MOND 喺 1σ? {1.2e-10 >= a0_lo and 1.2e-10 <= a0_hi}")
print(f"最佳/IDCM = {a0_best/A0_IDCM:.4f}")

# ============ 深層分析: 點解最佳 < IDCM? ============
print("\n=== 殘差分析: 邊啲星系貢獻最多 χ²? ===")
ups_final, chi2_final = {}, {}
for name, gal in galaxies.items():
    u, c2 = fit_galaxy(gal, A0_IDCM)
    ups_final[name] = u
    chi2_final[name] = c2

# Top 10 差星系
worst = sorted(chi2_final.items(), key=lambda x: -x[1])[:10]
print(f"{'星系':<12} {'χ²':>8} {'Υ':>6} {'N':>4}")
for name, c2 in worst:
    n = len(galaxies[name])
    print(f"{name:<12} {c2:>8.1f} {ups_final[name]:>6.3f} {n:>4}")

# 分析: 高 χ² 星系嘅共同特徵
# 如果係低質量 (gas-rich) 星系 → Υ 細, χ² 高 → 可能係 gas 主導
gas_dom = []
for name, gal in galaxies.items():
    Vgas_max = max(p['Vgas'] for p in gal)
    Vdisk_max = max(p['Vdisk'] for p in gal)
    if Vgas_max > Vdisk_max:
        gas_dom.append(name)
print(f"\nGas-dominated 星系數: {len(gas_dom)} / {n_gal}")

# 高 χ² 星系有幾多係 gas-dominated?
worst_names = [w[0] for w in worst]
gas_worst = [n for n in worst_names if n in gas_dom]
print(f"Top-10 χ² 星系中 gas-dominated: {len(gas_worst)} / 10")

# ============ 保存 ============
with open('data/global_joint_fit.json', 'w') as f:
    json.dump({
        'a0_best': float(a0_best), 'chi2_best': float(chi2_best),
        'a0_idcm': float(A0_IDCM), 'chi2_idcm': float(chi2_idcm),
        'a0_mond': 1.2e-10, 'chi2_mond': float(chi2_mond),
        'a0_lo': float(a0_lo), 'a0_hi': float(a0_hi),
        'n_gal': n_gal, 'n_pts': n_pts,
        'ups_idcm': ups_idcm,
        'ratio_best_idcm': float(a0_best/A0_IDCM)
    }, f, indent=2, default=str)
print("\n結果已存: data/global_joint_fit.json")
