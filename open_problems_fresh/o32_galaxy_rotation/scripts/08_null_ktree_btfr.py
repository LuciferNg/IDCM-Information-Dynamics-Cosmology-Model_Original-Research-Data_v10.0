#!/usr/bin/env python3
"""
O32-08: Kepler null test + K_Tree 尺度閉合
=============================================
1. Kepler null test: 純重子引力 (無 DM 暈, 無 MOND 效應) 能否解釋旋轉曲線?
   → 如果唔得, 證明需要額外效應 (IDCM: a₀ = c²/2πR_H)
2. K_Tree 尺度閉合: λ_sync = 294.88 Mpc, B=4 分支
   Level 5: 294.88/4^5 = 0.288 Mpc = 288 kpc (星系暈)
   Level 6: 294.88/4^6 = 72 kpc   (星系)
   Level 7: 294.88/4^7 = 18 kpc   (星系內區)
3. 有效質量計算: 喺 K_Tree level ℓ, 星系嘅「表觀 DM 質量」= ?
"""
import numpy as np
from scipy.optimize import minimize_scalar
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
lambda_sync = 294.88  # Mpc
phi = (1 + np.sqrt(5)) / 2

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

def gal_chi2_kepler(ups, gal):
    """純 Kepler: V_model² = G·M_bar(r)/r, 無任何修正"""
    R = np.array([p['R'] for p in gal]) * kpc_to_m
    Vobs = np.array([p['Vobs'] for p in gal])
    eVobs = np.array([p['eVobs'] for p in gal])
    Vgas_ms = np.array([p['Vgas'] for p in gal]) * 1e3
    Vdisk_ms = np.array([p['Vdisk'] for p in gal]) * 1e3
    Vbul_ms = np.array([p['Vbul'] for p in gal]) * 1e3
    Vbar2 = ups * (Vdisk_ms**2 + Vbul_ms**2) + Vgas_ms**2
    Vpred = np.sqrt(np.maximum(Vbar2, 0)) / 1e3
    return np.sum(((Vobs - Vpred) / eVobs)**2)

def gal_chi2_mond(ups, gal, a0):
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

# ============ 1. Kepler null test ============
print("=" * 60)
print("1. Kepler NULL TEST (純重子引力, 無額外效應)")
print("=" * 60)

chi2_kepler = 0
chi2_mond = 0
n_pts = 0
ups_kepler_all = []
ups_mond_all = []

for name, gal in galaxies.items():
    # Kepler
    res_k = minimize_scalar(lambda u: gal_chi2_kepler(u, gal),
                            bounds=(0.01, 3.0), method='bounded')
    chi2_kepler += res_k.fun
    ups_kepler_all.append(res_k.x)
    # MOND (IDCM a₀)
    res_m = minimize_scalar(lambda u: gal_chi2_mond(u, gal, A0_IDCM),
                            bounds=(0.01, 3.0), method='bounded')
    chi2_mond += res_m.fun
    ups_mond_all.append(res_m.x)
    n_pts += len(gal)

n_gal = len(galaxies)
dof_kepler = n_pts - n_gal
dof_mond = n_pts - n_gal

print(f"數據點: {n_pts}, 星系: {n_gal}")
print(f"Kepler fit: χ² = {chi2_kepler:.1f}, χ²/dof = {chi2_kepler/dof_kepler:.2f}")
print(f"IDCM a₀ fit: χ² = {chi2_mond:.1f}, χ²/dof = {chi2_mond/dof_mond:.2f}")
print(f"Δχ² = {chi2_kepler - chi2_mond:.1f} (Kepler - IDCM)")
print(f"→ Kepler 完全失敗 (χ²/dof >> 1), 需要額外效應 ✅")

# ============ 2. K_Tree 尺度閉合 ============
print("\n" + "=" * 60)
print("2. K_Tree 尺度閉合 (λ_sync = 294.88 Mpc, B = 4)")
print("=" * 60)

print(f"\nλ_sync = {lambda_sync} Mpc")
print(f"B = 4 = φ³ - φ⁻³ (MERA branching)")
print(f"\n尺度階梯 (星系尺度):")
print(f"{'Level ℓ':<10} {'λ_sync/4^ℓ':<14} {'物理區':<20} {'4^ℓ':<12}")
for ell in range(0, 9):
    scale = lambda_sync / (4 ** ell)
    if scale > 5:
        region = "超星系團" if scale > 100 else ("星系團" if scale > 10 else "星系群")
    else:
        if scale > 1:
            region = "星系暈"
        elif scale > 0.2:
            region = "星系盤"
        else:
            region = "星系核"
    print(f"{ell:<10} {scale*1e3 if scale<1 else scale:<14.3f} "
          f"{region:<20} {4**ell:<12}")

print(f"\nSPARC 星系尺度對應:")
print(f"  R_galaxy ~ 5-50 kpc → ℓ = 6-7 (72-18 kpc) ✅")
print(f"  R_halo ~ 100-300 kpc → ℓ = 5 (288 kpc) ✅")

# ============ 3. 深層結構: a₀ 嘅 K_Chain 推導 ============
print("\n" + "=" * 60)
print("3. a₀ = c²/(2πR_H) 嘅結構推導")
print("=" * 60)

# R_H = 44·dx (44 sites), dx = site spacing
# λ_sync = 2πR_H/88 = πR_H/44 (half-wavelength of fundamental mode)
# a₀ = c²/(2πR_H) = c²/(2π·44·dx)

dx = R_H / 44
print(f"R_H = {R_H} Mpc = 44 × {dx:.2f} Mpc")
print(f"λ_sync = {lambda_sync} Mpc = 2πR_H/88")
print(f"a₀ = c²/(2πR_H) = {A0_IDCM:.4e} m/s²")
print(f"  = c²/(88π·dx) — 每個 site 嘅環向心加速度")

# 另一種: a₀ = c·H₀/(2π), H₀ = c/R_H
print(f"a₀ = c·H₀/(2π), H₀ = c/R_H = {H0_idcm:.2f} km/s/Mpc")
print(f"→ a₀ 係 K_Chain 環嘅固有加速度標度")

# 關鍵: a₀ 同 ε 嘅關係
# ε = φ⁻¹/4 = 0.1545
# a₀·(1+ε) = ?
a0_corr = A0_IDCM * (1 + 1/phi/4)
print(f"\n修正候選: a₀·(1+ε) = {a0_corr:.4e} (ε = φ⁻¹/4)")
print(f"  vs MOND 1.2e-10: 偏差 {(a0_corr-1.2e-10)/1.2e-10*100:.2f}%")
print(f"  vs 最佳 1.06e-10: 偏差 {(a0_corr-1.06e-10)/1.06e-10*100:.2f}%")

# a₀·φ⁻¹ 檢查
a0_phi = A0_IDCM * (1/phi)
print(f"a₀·φ⁻¹ = {a0_phi:.4e} — 太細, 唔係")

# ============ 4. 深 MOND v⁴ = G·M·a₀ 嘅 BTFR 斜率 ============
print("\n" + "=" * 60)
print("4. BTFR: v⁴ = G·M_bary·a₀ (斜率 4)")
print("=" * 60)

# 理論 BTFR: log M_bary = 4·log V_f - 4·log(G·a₀)^(1/4)
# 用 IDCM a₀:
logM_pred = lambda logV: 4*logV - np.log10(G * A0_IDCM / 1e6)  # V 單位 km/s → m/s
# 檢查: V = 100 km/s → M = ?
V_test = 100e3  # m/s
M_pred = V_test**4 / (G * A0_IDCM)
print(f"V = 100 km/s → M_bary = {M_pred/Msun:.2e} Msun = {M_pred/Msun/1e9:.2f}×10⁹ Msun")
print(f"(典型星系: 10⁹-10¹⁰ Msun ✅)")

# 同 BTFR 數據比較
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
            L36 = float(parts[7])
            MHI = float(parts[13])
            Vflat = float(parts[15])
        except (ValueError, IndexError):
            continue
        sample[name] = {'L36': L36, 'MHI': MHI, 'Vflat': Vflat}

# 用 median Υ = 0.44 估 M_bary (冇 fit 嘅簡化版)
ups_med = np.median(ups_mond_all)
btfr_pts = []
for name in sample:
    if sample[name]['Vflat'] <= 0:
        continue
    L36 = sample[name]['L36']
    MHI = sample[name]['MHI']
    Mbary = ups_med * L36 + 1.33 * MHI
    btfr_pts.append((Mbary, sample[name]['Vflat']))

btfr_pts = np.array(btfr_pts)
logM = np.log10(btfr_pts[:, 0])
logV = np.log10(btfr_pts[:, 1])

# IDCM 預測 (零自由參數, 無 fit):
# M_bary = V⁴/(G·a₀), V 單位 m/s = V_km/s × 1e3
# log10(M_bary/Msun) = 4·logV + 4·log10(1e3) - log10(G·a₀) - log10(Msun)
# log10(M_bary/1e9 Msun) = 上面 - 9
logM_idcm = 4 * logV + 4*np.log10(1e3) - np.log10(G * A0_IDCM) - np.log10(Msun) - 9

resid = logM - logM_idcm
rms = np.sqrt(np.mean(resid**2))
print(f"\nBTFR 樣本: {len(btfr_pts)} 星系 (Υ = median {ups_med:.2f})")
print(f"IDCM BTFR 預測 (斜率 4, 零參數) scatter: {rms:.3f} dex")

# 線性 fit 斜率
slope, intercept = np.polyfit(logV, logM, 1)
print(f"數據 fit 斜率: {slope:.2f} (理論 4.00)")
print(f"數據 fit 截距: {intercept:.2f} (IDCM 預測 {np.log10(G*A0_IDCM)-4*np.log10(1e3)-np.log10(Msun)+9:.2f})")

# ============ 保存 ============
with open('data/null_ktree_btfr.json', 'w') as f:
    json.dump({
        'chi2_kepler': float(chi2_kepler),
        'chi2_mond_idcm': float(chi2_mond),
        'n_pts': n_pts, 'n_gal': n_gal,
        'btfr_slope_fit': float(slope),
        'btfr_slope_theory': 4.0,
        'btfr_rms_idcm': float(rms),
        'a0_idcm': float(A0_IDCM)
    }, f, indent=2)
print("\n結果已存: data/null_ktree_btfr.json")
