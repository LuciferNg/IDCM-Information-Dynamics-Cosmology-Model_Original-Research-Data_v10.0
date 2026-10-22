#!/usr/bin/env python3
"""
O32-02: SPARC RAR 分析 — IDCM a₀ 零參數測試
==============================================
測試 IDCM 的結構預測 a₀ = cH₀/2π = 1.1225e-10 m/s²
vs MOND 擬合值 a₀ = 1.2e-10 m/s²

方法 (Lelli+2017):
1. 每個星系 fit 單一 M/L (Υ) 使模型匹配旋轉曲線
2. 對所有點計算:
   g_obs = V_obs²/R
   g_bar = (Υ·V_disk² + Υ·V_bul² + V_gas²)/R  (gas 用 Υ=1.33 已含 He)
3. MOND 插值: g_obs = g_bar·ν(g_bar/a₀)
   標準 ν(x): g_obs = g_bar/2 + √(g_bar²/4 + g_bar·a₀)
4. 比較 IDCM a₀ vs MOND a₀ 嘅 χ²
"""
import numpy as np
import json

# ============ 常數 ============
c = 299792.458            # km/s
R_H = 4129.94             # Mpc
H0_idcm = c / R_H         # 72.59 km/s/Mpc
Mpc_to_km = 3.085677581e19
c_ms = c * 1e3            # m/s
H0_s = H0_idcm / Mpc_to_km
kpc_to_m = 3.085677581e19

# IDCM 結構 a₀ (零自由參數)
A0_IDCM = c_ms * H0_s / (2 * np.pi)   # 1.1225e-10 m/s²
A0_MOND = 1.2e-10                     # MOND 標準值

# ============ 解析 SPARC MassModels ============
def parse_mass_models(path):
    """解析 fixed-width MassModels 文件"""
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
print(f"解析星系數: {len(galaxies)}")
print(f"總數據點: {sum(len(v) for v in galaxies.values())}")

# ============ MOND 插值 ============
def mond_interp(gbar, a0):
    """標準 MOND 插值: g_obs = g_bar/2 + sqrt(g_bar²/4 + g_bar·a₀)
    對應 μ(x) = x/sqrt(1+x²), x = g_bar/a₀"""
    return gbar / 2 + np.sqrt(gbar**2 / 4 + gbar * a0)

# ============ 每個星系 fit Υ (M/L at 3.6μm) ============
def fit_upsilon(gal, a0):
    """Fit 單一 Υ 使模型匹配觀測曲線
    模型: V_model² = Υ·(V_disk² + V_bul²) + V_gas²
    然後 MOND 修正: V_pred² = R·g_obs(R), g_obs = mond_interp(V_bar²/R, a0)
    """
    R = np.array([p['R'] for p in gal])
    Vobs = np.array([p['Vobs'] for p in gal])
    eVobs = np.array([p['eVobs'] for p in gal])
    Vgas = np.array([p['Vgas'] for p in gal])
    Vdisk = np.array([p['Vdisk'] for p in gal])
    Vbul = np.array([p['Vbul'] for p in gal])

    # 質量模型速度 (R 單位 kpc -> m)
    R_m = R * kpc_to_m

    # 單位: V 係 km/s → 轉 m/s (×1e3); R 係 kpc → m (×3.086e19)
    Vobs_ms = Vobs * 1e3
    eVobs_ms = eVobs * 1e3
    Vgas_ms = Vgas * 1e3
    Vdisk_ms = Vdisk * 1e3
    Vbul_ms = Vbul * 1e3

    def chi2_for(ups):
        Vbar2 = (ups * (Vdisk_ms**2 + Vbul_ms**2) + Vgas_ms**2)  # m²/s²
        gbar = Vbar2 / R_m                                       # m/s²
        gobs_pred = mond_interp(gbar, a0)                        # m/s²
        Vpred2 = R_m * gobs_pred                                 # m²/s²
        # 避免負值
        Vpred = np.sqrt(np.maximum(Vpred2, 0)) / 1e3             # km/s
        return np.sum(((Vobs - Vpred) / eVobs)**2)

    # 網格搜索 Υ ∈ [0.1, 1.0]
    ups_grid = np.linspace(0.1, 1.0, 91)
    chi2s = np.array([chi2_for(u) for u in ups_grid])
    best = ups_grid[np.argmin(chi2s)]

    # 精細搜索
    ups_grid2 = np.linspace(max(0.05, best-0.05), min(1.2, best+0.05), 101)
    chi2s2 = np.array([chi2_for(u) for u in ups_grid2])
    best2 = ups_grid2[np.argmin(chi2s2)]
    return best2, chi2_for(best2)

# ============ 全樣本分析 ============
def full_analysis(a0, label):
    print(f"\n{'='*60}")
    print(f"分析: {label} (a₀ = {a0:.4e})")
    print(f"{'='*60}")

    all_gobs = []
    all_gbar = []
    all_chi2 = []
    all_ups = []
    n_pts = 0
    n_gal = 0

    for name, gal in galaxies.items():
        R = np.array([p['R'] for p in gal])
        Vobs = np.array([p['Vobs'] for p in gal])
        eVobs = np.array([p['eVobs'] for p in gal])
        R_m = R * kpc_to_m

        ups, chi2 = fit_upsilon(gal, a0)
        all_ups.append(ups)
        all_chi2.append(chi2)

        Vgas_ms = np.array([p['Vgas'] for p in gal]) * 1e3
        Vdisk_ms = np.array([p['Vdisk'] for p in gal]) * 1e3
        Vbul_ms = np.array([p['Vbul'] for p in gal]) * 1e3
        Vbar2 = ups * (Vdisk_ms**2 + Vbul_ms**2) + Vgas_ms**2
        gbar = Vbar2 / R_m
        gobs = (Vobs * 1e3)**2 / R_m

        all_gobs.extend(gobs)
        all_gbar.extend(gbar)
        n_pts += len(gal)
        n_gal += 1

    all_gobs = np.array(all_gobs)
    all_gbar = np.array(all_gbar)

    # 總 χ²
    total_chi2 = sum(all_chi2)
    dof = n_pts - n_gal  # 每個星系一個 Υ
    print(f"星系數: {n_gal}, 數據點: {n_pts}")
    print(f"Υ 中位數: {np.median(all_ups):.3f}")
    print(f"總 χ² = {total_chi2:.1f}, dof = {dof}")
    print(f"χ²/dof = {total_chi2/dof:.3f}")

    # RAR scatter (log 空間, 殘差標準差)
    gobs_pred = mond_interp(all_gbar, a0)
    resid = np.log10(all_gobs) - np.log10(gobs_pred)
    rms = np.sqrt(np.mean(resid**2))
    print(f"RAR scatter (log₁₀): {rms:.4f} dex")

    return {
        'label': label, 'a0': a0,
        'chi2': total_chi2, 'dof': dof,
        'chi2_dof': total_chi2/dof,
        'scatter': rms,
        'n_gal': n_gal, 'n_pts': n_pts,
        'median_ups': float(np.median(all_ups))
    }

r_mond = full_analysis(A0_MOND, "MOND a₀ = 1.2e-10")
r_idcm = full_analysis(A0_IDCM, "IDCM a₀ = cH₀/2π")

# ============ 對比 ============
print(f"\n{'='*60}")
print("對比總結")
print(f"{'='*60}")
print(f"{'模型':<24} {'χ²/dof':>8} {'RAR scatter':>12} {'Δχ²':>8}")
print(f"{'MOND a₀=1.2e-10':<24} {r_mond['chi2_dof']:>8.3f} {r_mond['scatter']:>12.4f} {'—':>8}")
print(f"{'IDCM a₀=1.1225e-10':<24} {r_idcm['chi2_dof']:>8.3f} {r_idcm['scatter']:>12.4f} {r_idcm['chi2']-r_mond['chi2']:>8.1f}")

# 保存
with open('data/rar_results.json', 'w') as f:
    json.dump({'mond': r_mond, 'idcm': r_idcm}, f, indent=2)
print("\n結果已存: data/rar_results.json")

# ============ 關鍵: 如果 IDCM a₀ 略低, 有無 φ 修正? ============
phi = (1 + np.sqrt(5)) / 2
print(f"\n=== IDCM 結構修正候選 ===")
print(f"a₀_idcm = {A0_IDCM:.4e}")
print(f"a₀_idcm × φ⁻¹/2 修正? = {A0_IDCM*(1/phi)/2:.4e}")
print(f"a₀_MOND/a₀_idcm = {A0_MOND/A0_IDCM:.4f}")
print(f"φ⁻¹/2 = {1/phi/2:.4f}")
print(f"(a₀_MOND/a₀_idcm - 1) = {(A0_MOND/A0_IDCM-1)*100:.2f}%")
print(f"φ⁻²/4 = {(1/phi)**2/4:.4f}")
print(f"ε = φ⁻¹/4 = {1/phi/4:.4f}")
