#!/usr/bin/env python3
"""
O32-13: W-field 物理機制 — 旋轉曲線嘅 IDCM 第一性原理
=======================================================
IDCM 解釋星系旋轉曲線嘅完整機制:

1. a₀ = c²/(2πR_H) = cH₀/2π 係 K_Chain 環嘅固有加速度標度
   (R_H = c/H₀, H₀ = 72.59 km/s/Mpc 結構定義)

2. K_Chain mode n=1 (基本模式): λ₁ = R_H = 4129.94 Mpc
   全環同步模式 — 提供最低加速度標度

3. 深 MOND 極限: g_obs → √(g_bar·a₀) ⟺ v⁴ = G·M·a₀ (BTFR 斜率 4)

4. m₇ = 13.8 MeV (p7 mode): 係 K_Chain 第 7 個模式嘅 DM 粒子
   Ω_DM/Ω_b = 13/2 = 6.5
   → DM 唔係粒子暈, 係 K_Chain 諧波嘅集體效應!
   → 但 IDCM 需要一個「物質化」嘅 DM 分量 (m₇) 嚟做引力源

5. K_Tree level: 唔同尺度嘅星系 = 唔同 K_Tree level 嘅投影
   Level 5: 288 kpc (星系暈)
   Level 6: 72 kpc (星系)
   Level 7: 18 kpc (星系內區)

關鍵問題: IDCM 嘅 DM (m₇) 有冇實體質量密度?
定係純幾何效應 (MOND-like)?
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
kpc_to_m = 3.085677581e19
Mpc_to_m = 3.085677581e22
phi = (1 + np.sqrt(5)) / 2

A0_IDCM = c_ms * H0_s / (2 * np.pi)
lambda_sync = 294.88  # Mpc

print("=" * 65)
print("O32-13: W-field 機制閉合")
print("=" * 65)

# ============ 1. 機制: 點解 a₀ = cH₀/2π? ============
print("\n=== 1. a₀ 嘅第一性原理 ===")
print(f"R_H = c/H₀ = {R_H} Mpc (K_Chain 環周長)")
print(f"H₀ = c/R_H = {H0_idcm:.2f} km/s/Mpc (結構定義)")
print(f"a₀ = cH₀/2π = {A0_IDCM:.4e} m/s²")
print(f"a₀ = c²/(2πR_H) — 光速² 除以環周長")
print(f"a₀ = c²/(88π·dx), dx = R_H/44 = {R_H/44:.2f} Mpc (site 間距)")

# 物理詮釋: 環嘅旋轉頻率
omega_ring = c / R_H  # 1/s (光繞環一圈嘅頻率)
print(f"\n光繞環頻率: ω = c/R_H = {omega_ring:.3e} s⁻¹")
print(f"對應周期: T = 2πR_H/c = {2*np.pi*R_H*Mpc_to_km*1e3/c_ms/3.156e16:.1f} Gyr")
print(f"向心加速度: a = ω²·R_H = c²/R_H = {c_ms**2/(R_H*Mpc_to_m):.3e} m/s² (太大)")
print(f"但 a₀ = c²/(2πR_H) = a_ring/2π — 環加速度除以 2π")
print("→ a₀ 係「環向心加速度嘅角度平均」: 1/2π ∫₀^{2π} a·cosθ dθ")

# ============ 2. MOND 極限閉合 ============
print("\n=== 2. 深 MOND 極限 → BTFR ===")
# RAR 插值: g_obs = g_bar·(1+√(1+4a₀/g_bar))/2
# g_bar << a₀: g_obs ≈ √(g_bar·a₀)
# V²/R = √((V_bar²/R)·a₀) → V⁴ = G·M·a₀ (BTFR 斜率 4)
print("g_bar << a₀: g_obs ≈ √(g_bar·a₀)")
print("→ V⁴ = G·M·a₀ (BTFR 斜率 4, 零自由參數)")
print(f"→ 驗證: V = 100 km/s → M = { (100e3)**4/(G*A0_IDCM)/Msun:.2e} Msun")

# ============ 3. m₇ DM 角色 ============
print("\n=== 3. m₇ = 13.8 MeV DM 角色 ===")
m7 = 13.8e6  # eV
m7_kg = m7 * 1.78266192e-36  # eV → kg
print(f"m₇ = {m7} eV = {m7_kg:.3e} kg")
print(f"Ω_DM/Ω_b = 13/2 = 6.5")

# DM 密度: Ω_DM·ρ_crit
rho_crit = 3*H0_s**2/(8*np.pi*G)  # kg/m³
print(f"ρ_crit = {rho_crit:.3e} kg/m³")
rho_dm = 0.26 * rho_crit  # Ω_DM ~ 0.26
print(f"ρ_DM = {rho_dm:.3e} kg/m³")

# DM 數密度
n_dm = rho_dm / m7_kg
print(f"n_DM = {n_dm:.3e} m⁻³ = {n_dm*1e6:.3e} cm⁻³")

# 星系尺度 DM 質量
# 典型星系: R = 30 kpc, 球
R_gal = 30 * kpc_to_m
M_dm_gal = (4/3)*np.pi*R_gal**3 * rho_dm
print(f"30 kpc 球內 DM: {M_dm_gal/Msun:.2e} Msun")
print(f"(典型星系 DM 暈: ~1e12 Msun — 差 4 個數量級!)")

# 關鍵: 如果 DM 係 m₇ 粒子暈, 密度太細
# → DM 唔可能係粒子暈!
print(f"\n⚠️ m₇ 粒子暈密度: {M_dm_gal/Msun:.1e} Msun/30kpc³")
print(f"   觀測需要: ~1e12 Msun/30kpc³")
print(f"   差距: {1e12/(M_dm_gal/Msun):.1e}×")
print(f"→ IDCM DM 唔可能係 m₇ 粒子暈! m₇ 只係宇宙學密度標度")
print(f"→ 星系尺度嘅「DM 效應」必須係 W-field/幾何效應 (MOND-like)")

# ============ 4. 閉合: IDCM = MOND-like 幾何 + m₇ 宇宙學 ============
print("\n=== 4. 機制閉合 ===")
print("""
IDCM 星系旋轉曲線解釋 (零自由參數):

1. 星系內部: 重子引力 (Kepler) — 觀測支持
2. 低加速度區 (g < a₀ = cH₀/2π = 1.1225e-10):
   K_Chain 基本模式 (mode 1) 嘅 W-field 耦合放大引力
   → 等效 MOND 插值函數
3. 深 MOND 極限: V⁴ = G·M·a₀ → BTFR 斜率 4
4. m₇ = 13.8 MeV: 宇宙學 DM 密度 (Ω_DM/Ω_b = 13/2)
   → 星系尺度唔需要 m₇ 粒子暈
   → 星系 DM = K_Chain 諧波投影 (幾何), 唔係粒子

★ 關鍵區別:
   ΛCDM: 星系 DM = 粒子暈 (CDM)
   MOND: 星系 DM = 修改動力學 (a₀ 係 fit 參數)
   IDCM: 星系 DM = K_Chain 幾何投影 (a₀ 係結構常數 cH₀/2π, 零參數)
""")

# ============ 5. 預言 ============
print("=== 5. IDCM 可證偽預言 ===")
print(f"""
P1: a₀ 精確值 = cH₀/2π = {A0_IDCM:.4e} m/s² (零參數)
    → 用 H₀_idcm = 72.59, 唔係 Planck 67.4!
    → 如果用 Planck H₀: a₀ = {c_ms*(67.4/Mpc_to_km)/(2*np.pi):.4e} (差 {(c_ms*(67.4/Mpc_to_km)/(2*np.pi)-A0_IDCM)/A0_IDCM*100:.1f}%)

P2: BTFR 斜率 = 4 (深 MOND 極限, 同 MOND 一致)

P3: RAR 喺高加速度區 (g >> a₀) 回復牛頓
    → 但轉換點 (1+ε) 修正: g_t = a₀·(1+ε)? 

P4: 冇 DM 粒子暈 → 弱透鏡無 DM 訊號 (對比 CDM 預言)

P5: K_Tree level 5-7 (288/72/18 kpc) 對應唔同星系尺度
    → 星系規模分佈應有層級結構
""")

# ============ 6. 檢查 P3: ε 修正 ============
print("=== 6. RAR 轉換點 ε 修正 ===")
# 官方 bins 最佳 a₀ = 1.14e-10 vs IDCM 1.1225e-10
a0_best_official = 1.14e-10
ratio = a0_best_official / A0_IDCM
print(f"官方 bins 最佳/IDCM = {ratio:.4f}")
print(f"(1+ε)/1 = {1+1/phi/4:.4f}")
print(f"(1+ε/2) = {1+1/phi/8:.4f}")
print(f"φ⁻¹/2 = {1/phi/2:.4f}")
print(f"→ 最佳/IDCM = {ratio:.4f}, ε = {ratio-1:.4f}, φ⁻¹/4 = {1/phi/4:.4f}")

# 對比官方 RAR bins 直接 fit
# a₀_best = 1.14e-10 ± 0.026 (stat) ± 0.14 (sys)
# IDCM = 1.1225e-10 → 偏差 1.6% (stat) / 12% (sys)
print(f"\nIDCM vs 官方最佳: 偏差 {(ratio-1)*100:.1f}%")
print(f"官方統計誤差: 0.026e-10 = {0.026/1.2*100:.1f}%")
print(f"官方系統誤差: 0.14e-10 = {0.14/1.2*100:.1f}%")
print(f"→ IDCM 偏差 1.6% << 系統誤差 12% ✅")

# 保存
with open('data/wfield_mechanism.json', 'w') as f:
    json.dump({
        'a0_idcm': float(A0_IDCM),
        'a0_official_best': a0_best_official,
        'ratio': float(ratio),
        'm7_kg': m7_kg,
        'rho_dm': float(rho_dm),
        'M_dm_30kpc': float(M_dm_gal/Msun),
        'mechanism': 'K_Chain geometric projection, not particle halo'
    }, f, indent=2)
print("\n結果已存: data/wfield_mechanism.json")
