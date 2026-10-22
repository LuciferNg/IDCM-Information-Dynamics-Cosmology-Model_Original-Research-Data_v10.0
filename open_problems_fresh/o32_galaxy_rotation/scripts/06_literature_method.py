#!/usr/bin/env python3
"""
O32-06: 文獻方法 RAR 擬合 — Υ prior [0.1, 1.0] + RAR direct fit
================================================================
Lelli+2017 RAR 方法:
1. 每個星系 fit Υ ∈ [0.1, 1.0] (物理 prior)
2. 用 fit 出嚟嘅 Υ 計 g_bar 同 g_obs
3. RAR 數據直接 fit a₀ (g_obs vs g_bar)

問題: 點解我 fit 出嚟嘅 a₀ = 9.8e-11 而文獻 = 1.2e-10?
可能: (a) Υ prior 唔同, (b) fit 方法唔同, (c) quality cuts
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
        options={'xatol': 1e-6}
    )
    return res.x, res.fun

def build_rar(a0):
    """Fit Υ per galaxy, 收集 RAR 數據點"""
    all_gbar = []
    all_gobs = []
    for name, gal in galaxies.items():
        ups, _ = fit_galaxy(gal, a0)
        R = np.array([p['R'] for p in gal]) * kpc_to_m
        Vobs_ms = np.array([p['Vobs'] for p in gal]) * 1e3
        Vgas_ms = np.array([p['Vgas'] for p in gal]) * 1e3
        Vdisk_ms = np.array([p['Vdisk'] for p in gal]) * 1e3
        Vbul_ms = np.array([p['Vbul'] for p in gal]) * 1e3
        Vbar2 = ups * (Vdisk_ms**2 + Vbul_ms**2) + Vgas_ms**2
        gbar = Vbar2 / R
        gobs = Vobs_ms**2 / R
        all_gbar.extend(gbar)
        all_gobs.extend(gobs)
    return np.array(all_gbar), np.array(all_gobs)

def rar_chi2(a0, gbar, gobs, gerr):
    """RAR direct fit: χ² = Σ (g_obs - g_pred)²/σ²"""
    gpred = interpol_simple(gbar, a0)
    return np.sum(((gobs - gpred) / gerr)**2)

# ============ Step 1: 用 Υ prior [0.1, 1.0] fit Υ ============
print("=== Υ prior [0.1, 1.0] fit (a₀ = 1.2e-10) ===")
_, ups_ref = zip(*[fit_galaxy(g, A0_MOND) for g in galaxies.values()])
ups_arr = np.array(ups_ref)
print(f"Υ: min={ups_arr.min():.3f}, median={np.median(ups_arr):.3f}, max={ups_arr.max():.3f}")
print(f"Υ = 0.1 (lower bound) 嘅星系數: {(ups_arr <= 0.11).sum()}")
print(f"Υ = 1.0 (upper bound) 嘅星系數: {(ups_arr >= 0.99).sum()}")

# ============ Step 2: RAR direct fit ============
print("\n=== RAR direct fit a₀ (Υ prior [0.1,1.0]) ===")
# 用誤差傳播: σ_g_obs = 2·V·σ_V/R
def build_rar_err(a0):
    all_gbar, all_gobs, all_gerr = [], [], []
    for name, gal in galaxies.items():
        ups, _ = fit_galaxy(gal, a0)
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
    return np.array(all_gbar), np.array(all_gobs), np.array(all_gerr)

# 用 fixed a₀ = 1.2e-10 fit Υ, 然後 RAR direct fit
gbar, gobs, gerr = build_rar_err(A0_MOND)
print(f"RAR 數據點: {len(gbar)}")

# 掃描 a₀
a0_grid = np.linspace(0.7e-10, 1.5e-10, 41)
chi2s = [rar_chi2(a0, gbar, gobs, gerr) for a0 in a0_grid]
chi2s = np.array(chi2s)
best = a0_grid[np.argmin(chi2s)]
print(f"RAR direct 最佳 a₀ = {best:.4e} (χ² = {chi2s.min():.1f})")

# 精細
a0_fine = np.linspace(best-0.1e-10, best+0.1e-10, 41)
chi2s_f = np.array([rar_chi2(a0, gbar, gobs, gerr) for a0 in a0_fine])
best_f = a0_fine[np.argmin(chi2s_f)]
print(f"精細: 最佳 a₀ = {best_f:.4e} (χ² = {chi2s_f.min():.1f})")

# 1σ
dchi2 = np.abs(chi2s_f - chi2s_f.min())
mask = dchi2 < 1.0
print(f"1σ: [{a0_fine[mask].min():.4e}, {a0_fine[mask].max():.4e}]")

chi2_idcm = rar_chi2(A0_IDCM, gbar, gobs, gerr)
chi2_mond = rar_chi2(A0_MOND, gbar, gobs, gerr)
print(f"\nIDCM a₀ = {A0_IDCM:.4e}: χ² = {chi2_idcm:.1f}, Δχ² = {chi2_idcm-chi2s_f.min():.1f}")
print(f"MOND a₀ = {A0_MOND:.4e}: χ² = {chi2_mond:.1f}, Δχ² = {chi2_mond-chi2s_f.min():.1f}")
print(f"最佳/IDCM = {best_f/A0_IDCM:.4f}")

# ============ Step 3: Quality cuts (Q=1,2 高質量) ============
print("\n=== Quality cut: 只留高質量星系 ===")
# SPARC sample table Q flag: 1=高質量, 2=中, 3=低
sample_q = {}
with open('data/SPARC_Lelli2016c.mrt') as f:
    for line in f:
        parts = line.split()
        if len(parts) < 18:
            continue
        name = parts[0]
        if not name or not name[0].isalpha():
            continue
        try:
            Q = int(parts[16])
        except (ValueError, IndexError):
            continue
        sample_q[name] = Q

for qcut in [3, 2, 1]:
    gbar_q, gobs_q, gerr_q = [], [], []
    for name, gal in galaxies.items():
        if sample_q.get(name, 3) > qcut:
            continue
        ups, _ = fit_galaxy(gal, A0_MOND)
        R = np.array([p['R'] for p in gal]) * kpc_to_m
        Vobs_ms = np.array([p['Vobs'] for p in gal]) * 1e3
        eVobs_ms = np.array([p['eVobs'] for p in gal]) * 1e3
        Vgas_ms = np.array([p['Vgas'] for p in gal]) * 1e3
        Vdisk_ms = np.array([p['Vdisk'] for p in gal]) * 1e3
        Vbul_ms = np.array([p['Vbul'] for p in gal]) * 1e3
        Vbar2 = ups * (Vdisk_ms**2 + Vbul_ms**2) + Vgas_ms**2
        gbar_q.extend(Vbar2 / R)
        gobs_q.extend(Vobs_ms**2 / R)
        gerr_q.extend(2 * Vobs_ms * eVobs_ms / R)
    gbar_q, gobs_q, gerr_q = map(np.array, (gbar_q, gobs_q, gerr_q))
    chi2s_q = np.array([rar_chi2(a0, gbar_q, gobs_q, gerr_q) for a0 in a0_grid])
    best_q = a0_grid[np.argmin(chi2s_q)]
    print(f"Q ≤ {qcut}: {len(gbar_q)} 點, 最佳 a₀ = {best_q:.4e}")

with open('data/rar_literature_method.json', 'w') as f:
    json.dump({
        'a0_best_rar_direct': float(best_f),
        'a0_idcm': float(A0_IDCM),
        'a0_mond': float(A0_MOND),
        'ups_median': float(np.median(ups_arr))
    }, f, indent=2)
print("\n結果已存: data/rar_literature_method.json")
