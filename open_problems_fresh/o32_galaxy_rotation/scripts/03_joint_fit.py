#!/usr/bin/env python3
"""
O32-03: SPARC RAR 聯合擬合 — 最佳 a₀ vs IDCM 結構 a₀
======================================================
方法 (Lelli+2017 風格):
1. 每個星系獨立 fit Υ (1D 最小化), 給定 global a₀
2. 掃描 a₀ ∈ [0.8, 1.6]e-10, 搵 global 最佳
3. 比較: IDCM 結構值 a₀ = cH₀/2π = 1.1225e-10 vs 數據最佳值

同時輸出每星系最佳 Υ 同 V_f, 供 BTFR 使用。
"""
import numpy as np
import json

# ============ 常數 ============
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

def mond_interp(gbar, a0):
    return gbar / 2 + np.sqrt(gbar**2 / 4 + gbar * a0)

def gal_chi2_min(gal, a0, ups_grid=None):
    """對給定 a₀, 搵單一星系最佳 Υ 及對應 χ²"""
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
        gobs_pred = mond_interp(gbar, a0)
        Vpred = np.sqrt(np.maximum(R * gobs_pred, 0)) / 1e3
        chi2 = np.sum(((Vobs - Vpred) / eVobs)**2)
        if chi2 < best_chi2:
            best_chi2 = chi2
            best_ups = ups
    return best_ups, best_chi2

def total_chi2(a0):
    """所有星系總 χ²"""
    tot = 0
    ups_list = []
    for name, gal in galaxies.items():
        ups, chi2 = gal_chi2_min(gal, a0)
        tot += chi2
        ups_list.append(ups)
    return tot, ups_list

# ============ a₀ 掃描 ============
print("=== a₀ 掃描 (聯合 fit: global a₀ + per-galaxy Υ) ===")
a0_grid = np.linspace(0.8e-10, 1.6e-10, 81)
results = []
for a0 in a0_grid:
    tot, _ = total_chi2(a0)
    results.append((a0, tot))

results = np.array(results)
best_idx = np.argmin(results[:, 1])
a0_best = results[best_idx, 0]
chi2_best = results[best_idx, 1]

print(f"最佳 a₀ = {a0_best:.4e} m/s² (χ² = {chi2_best:.1f})")
print(f"IDCM a₀ = {A0_IDCM:.4e} m/s²")

# 精度改進: 喺最佳附近精細掃描
a0_fine = np.linspace(a0_best - 0.05e-10, a0_best + 0.05e-10, 41)
for a0 in a0_fine:
    tot, _ = total_chi2(a0)
    results = np.vstack([results, [a0, tot]])
best_idx = np.argmin(results[:, 1])
a0_best = results[best_idx, 0]
chi2_best = results[best_idx, 1]
print(f"精細: 最佳 a₀ = {a0_best:.4e} (χ² = {chi2_best:.1f})")

# ============ 對比 ============
n_pts = sum(len(v) for v in galaxies.values())
n_gal = len(galaxies)
dof = n_pts - n_gal - 1  # a₀ + 175 Υ

print(f"\n數據點: {n_pts}, 星系: {n_gal}, dof = {dof}")
print(f"最佳 a₀ fit: χ²/dof = {chi2_best/dof:.3f}")

# IDCM a₀ 嘅 χ²
chi2_idcm, ups_idcm = total_chi2(A0_IDCM)
print(f"IDCM a₀ fit: χ²/dof = {chi2_idcm/dof:.3f}")
print(f"Δχ² = {chi2_idcm - chi2_best:.1f}")

# a₀ 誤差 (Δχ² = 1)
dchi2 = results[:, 1] - chi2_best
mask = dchi2 < 1.0
if mask.sum() > 0:
    a0_lo = results[mask, 0].min()
    a0_hi = results[mask, 0].max()
    print(f"a₀ 誤差 (Δχ²=1): [{a0_lo:.4e}, {a0_hi:.4e}]")
    print(f"IDCM a₀ 喺 1σ 內? {A0_IDCM >= a0_lo and A0_IDCM <= a0_hi}")

# ============ 保存結果 ============
# 用 IDCM a₀ 嘅 Υ fit 結果
ups_final = {}
vflat_final = {}
for name, gal in galaxies.items():
    ups, _ = gal_chi2_min(gal, A0_IDCM)
    ups_final[name] = float(ups)
    # V_f: 用最外點估算
    outer = max(gal, key=lambda p: p['R'])
    vflat_final[name] = float(outer['Vobs'])

# 質量: M_bary = Υ·(L_disk + L_bul) + M_gas
# 用 SPARC sample table 嘅 L[3.6] 同 MHI (whitespace split, 更穩陣)
# 格式: name T D eD fD Inc eInc L36 eL36 Reff SBeff Rdisk SBdisk MHI RHI Vflat eVflat Q Ref
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
            L36 = float(parts[7])    # 10^9 Lsun
            MHI = float(parts[13])   # 10^9 Msun
            Vflat = float(parts[15]) # km/s
        except (ValueError, IndexError):
            continue
        sample[name] = {'L36': L36, 'MHI': MHI, 'Vflat': Vflat}

print(f"\nSample table 星系數: {len(sample)}")

# M_bary = Υ·L[3.6] + 1.33·MHI (Υ 用 fit 值, L 單位 1e9 Lsun)
# M/L_3.6 = 1 → M/L 由 Υ 給出
btfr_data = []
for name in sample:
    if name not in ups_final:
        continue
    L36 = sample[name]['L36']  # 1e9 Lsun
    MHI = sample[name]['MHI']  # 1e9 Msun
    ups = ups_final[name]
    Mbary = ups * L36 + 1.33 * MHI  # 1e9 Msun
    Vflat = sample[name]['Vflat']
    if Vflat > 0 and Mbary > 0:
        btfr_data.append({'name': name, 'Mbary': Mbary, 'Vflat': Vflat})

print(f"BTFR 星系數: {len(btfr_data)}")

with open('data/rar_joint_fit.json', 'w') as f:
    json.dump({
        'a0_best': float(a0_best), 'chi2_best': float(chi2_best),
        'a0_idcm': float(A0_IDCM), 'chi2_idcm': float(chi2_idcm),
        'n_gal': n_gal, 'n_pts': n_pts,
        'ups_final': ups_final,
        'btfr': btfr_data
    }, f, indent=2, default=str)

print("\n結果已存: data/rar_joint_fit.json")
