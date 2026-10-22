#!/usr/bin/env python3
"""
O32-04: RAR 聯合擬合 (Simple Interpolation) — IDCM vs MOND a₀
===============================================================
Lelli+2017 (RAR) 用 simple interpolation:
  g_obs = g_bar·(1 + √(1 + 4a₀/g_bar))/2
  (μ(x) = x/(1+x))

而 standard form:
  g_obs = g_bar/2 + √(g_bar²/4 + g_bar·a₀)
  (μ(x) = x/√(1+x²))

兩個形式喺深 MOND 極限同樣收斂到 √(g_bar·a₀), 但喺中間區唔同。
文獻 RAR a₀ = 1.2e-10 用 simple form → 必須用同一形式比較。
"""
import numpy as np
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
                D = float(line[12:18])
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
    """Simple form: μ(x) = x/(1+x) → g_obs = g_bar·(1+√(1+4a₀/g_bar))/2"""
    y = a0 / np.maximum(gbar, 1e-30)
    return gbar * (1 + np.sqrt(1 + 4 * y)) / 2

def interpol_standard(gbar, a0):
    """Standard form: μ(x) = x/√(1+x²)"""
    return gbar / 2 + np.sqrt(gbar**2 / 4 + gbar * a0)

def gal_chi2_min(gal, a0, interp_fn, ups_grid=None):
    R = np.array([p['R'] for p in gal]) * kpc_to_m
    Vobs = np.array([p['Vobs'] for p in gal])
    eVobs = np.array([p['eVobs'] for p in gal])
    Vgas_ms = np.array([p['Vgas'] for p in gal]) * 1e3
    Vdisk_ms = np.array([p['Vdisk'] for p in gal]) * 1e3
    Vbul_ms = np.array([p['Vbul'] for p in gal]) * 1e3

    if ups_grid is None:
        ups_grid = np.linspace(0.05, 1.5, 291)

    best_chi2 = np.inf
    best_ups = 0.5
    for ups in ups_grid:
        Vbar2 = ups * (Vdisk_ms**2 + Vbul_ms**2) + Vgas_ms**2
        gbar = Vbar2 / R
        gobs_pred = interp_fn(gbar, a0)
        Vpred = np.sqrt(np.maximum(R * gobs_pred, 0)) / 1e3
        chi2 = np.sum(((Vobs - Vpred) / eVobs)**2)
        if chi2 < best_chi2:
            best_chi2 = chi2
            best_ups = ups
    return best_ups, best_chi2

def total_chi2(a0, interp_fn):
    tot = 0
    for name, gal in galaxies.items():
        _, chi2 = gal_chi2_min(gal, a0, interp_fn)
        tot += chi2
    return tot

n_pts = sum(len(v) for v in galaxies.values())
n_gal = len(galaxies)
dof = n_pts - n_gal - 1

# ============ 掃描 (兩種 interpolation) ============
print("=== a₀ 掃描: Simple vs Standard Interpolation ===")
for label, interp_fn in [("SIMPLE (μ=x/(1+x))", interpol_simple),
                          ("STANDARD (μ=x/√(1+x²))", interpol_standard)]:
    a0_grid = np.linspace(0.8e-10, 1.6e-10, 81)
    results = []
    for a0 in a0_grid:
        results.append((a0, total_chi2(a0, interp_fn)))
    results = np.array(results)
    best_idx = np.argmin(results[:, 1])
    a0_best = results[best_idx, 0]

    # 精細
    a0_fine = np.linspace(a0_best - 0.05e-10, a0_best + 0.05e-10, 41)
    for a0 in a0_fine:
        results = np.vstack([results, [a0, total_chi2(a0, interp_fn)]])
    best_idx = np.argmin(results[:, 1])
    a0_best = results[best_idx, 0]
    chi2_best = results[best_idx, 1]

    chi2_idcm = total_chi2(A0_IDCM, interp_fn)
    chi2_mond = total_chi2(A0_MOND, interp_fn)

    # 1σ 誤差
    dchi2 = results[:, 1] - chi2_best
    mask = dchi2 < 1.0
    a0_lo = results[mask, 0].min() if mask.sum() > 0 else a0_best
    a0_hi = results[mask, 0].max() if mask.sum() > 0 else a0_best

    print(f"\n--- {label} ---")
    print(f"最佳 a₀ = {a0_best:.4e} (χ²/dof = {chi2_best/dof:.3f})")
    print(f"1σ 範圍: [{a0_lo:.4e}, {a0_hi:.4e}]")
    print(f"MOND  a₀ = {A0_MOND:.4e}: χ²/dof = {chi2_mond/dof:.3f}, Δχ² = {chi2_mond-chi2_best:.1f}")
    print(f"IDCM  a₀ = {A0_IDCM:.4e}: χ²/dof = {chi2_idcm/dof:.3f}, Δχ² = {chi2_idcm-chi2_best:.1f}")
    print(f"MOND  喺 1σ? {A0_MOND >= a0_lo and A0_MOND <= a0_hi}")
    print(f"IDCM  喺 1σ? {A0_IDCM >= a0_lo and A0_IDCM <= a0_hi}")

    # 保存
    with open(f'data/scan_{label.split()[0].lower()}.json', 'w') as f:
        json.dump({'a0_grid': results[:, 0].tolist(), 'chi2': results[:, 1].tolist(),
                   'a0_best': float(a0_best), 'chi2_best': float(chi2_best),
                   'a0_idcm': float(A0_IDCM), 'chi2_idcm': float(chi2_idcm),
                   'a0_mond': float(A0_MOND), 'chi2_mond': float(chi2_mond)}, f, indent=2)
