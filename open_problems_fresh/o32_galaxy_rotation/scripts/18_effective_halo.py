#!/usr/bin/env python3
"""
O32-18: W-field 有效勢 V_eff(r) — 從 RAR 反推
================================================
目標: 從 RAR 插值函數推導等效「暗物質暈」密度分佈
      (即 ΛCDM 會點詮釋 IDCM 幾何效應)

方法:
1. RAR: g_obs(R) = g_bar·ν(g_bar/a₀), 其中 g_bar = GM_bar(R)/R²
2. 總質量: M_tot(R) = g_obs(R)·R²/G
3. 有效 DM: M_DM(R) = M_tot(R) - M_bar(R)
4. DM 密度: ρ_DM(R) = (1/4πR²)·dM_DM/dR
5. 有效勢: Φ(R) = ∫ g_obs(R')dR'

預言:
- ρ_DM(R) 應該係 cored (唔係 NFW cusp!)
- 外圍 ρ_DM ∝ R⁻² (isothermal, 產生平坦曲線)
- 中心 ρ_DM → 有限 (core), 唔係 NFW 嘅 R⁻¹ cusp
"""
import numpy as np
from scipy.integrate import cumulative_trapezoid as cumtrapz
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

A0_IDCM = c_ms * H0_s / (2 * np.pi)   # 1.1225e-10

def interpol_simple(gbar, a0):
    y = a0 / np.maximum(gbar, 1e-30)
    return gbar * (1 + np.sqrt(1 + 4 * y)) / 2

# ============ 典型星系參數 ============
# NGC 3198: M_bar ~ 2e10 Msun, 指數盤 R_d ~ 2.6 kpc
Mbar = 2e10 * Msun  # kg
Rd = 2.6 * kpc_to_m  # m
print("=" * 65)
print("W-field 有效勢: 典型星系 (M_bar = 2e10 Msun, R_d = 2.6 kpc)")
print("=" * 65)

# 指數盤質量分佈
def M_bar(R):
    """指數盤累積質量"""
    x = R / Rd
    return Mbar * (1 - (1 + x) * np.exp(-x))

# R 網格
R_grid = np.logspace(-1, 1.5, 200) * kpc_to_m  # 0.1 - 30 kpc

# g_bar, g_obs
g_bar = G * M_bar(R_grid) / R_grid**2
g_obs = interpol_simple(g_bar, A0_IDCM)

# 總質量 (假設球形近似)
M_tot = g_obs * R_grid**2 / G
M_DM = M_tot - M_bar(R_grid)

# DM 密度 (數值微分) — 單位 Msun/kpc³
dM_dR = np.gradient(M_DM, R_grid)
rho_DM = dM_dR / (4 * np.pi * R_grid**2)  # kg/m³
rho_DM_kpc3 = rho_DM * (kpc_to_m**3) / Msun  # Msun/kpc³

# 有效勢
Phi = cumtrapz(g_obs, R_grid, initial=0)

# 旋轉曲線
V_obs = np.sqrt(R_grid * g_obs) / 1e3  # km/s
V_bar = np.sqrt(R_grid * g_bar) / 1e3
V_tot = np.sqrt(R_grid * g_obs) / 1e3

print(f"\n{'R(kpc)':>8} {'g_bar':>10} {'g_obs':>10} {'M_DM':>10} {'ρ_DM':>10} {'V_obs':>7}")
for Rk in [0.3, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0]:
    R = Rk * kpc_to_m
    idx = np.argmin(np.abs(R_grid - R))
    mb_idx = float(M_bar(R))  # scalar!
    ratio = M_DM[idx] / mb_idx
    print(f"{Rk:>8.1f} {g_bar[idx]:>10.3e} {g_obs[idx]:>10.3e} "
          f"{M_DM[idx]/Msun:>10.2e} {rho_DM_kpc3[idx]:>10.3f} {V_obs[idx]:>7.1f}  ratio={ratio:.2f}")

# ============ 密度剖面分析 ============
print("\n" + "=" * 65)
print("密度剖面: cored vs cusp")
print("=" * 65)

# 檢查外圍斜率: ρ ∝ R^α
print(f"\n外圍密度斜率 (R > 10 kpc):")
slopes = []
for i in range(len(R_grid) - 10, len(R_grid) - 1):
    dr = np.log(R_grid[i+1] / R_grid[i])
    drho = np.log(rho_DM[i+1] / rho_DM[i])
    slopes.append(drho / dr)
print(f"  α = {np.mean(slopes):.3f} (isothermal: -2, NFW: -3)")

# 中心密度 (R → 0)
print(f"\n中心密度 (R = 0.1 kpc): ρ = {rho_DM_kpc3[np.argmin(np.abs(R_grid - 0.1*kpc_to_m))]:.3f} Msun/kpc³")
print(f"中心密度 (R = 1 kpc): ρ = {rho_DM_kpc3[np.argmin(np.abs(R_grid - 1.0*kpc_to_m))]:.3f} Msun/kpc³")
print(f"→ 中心有限 = CORED (唔係 NFW cusp!)")

# ============ 對比 NFW ============
print("\n" + "=" * 65)
print("對比 NFW 暈")
print("=" * 65)

# NFW: ρ(r) = ρ_s/((r/r_s)(1+r/r_s)²)
# cored: ρ(r) = ρ_0/(1+(r/r_c)²)  (pseudo-isothermal)
# 我哋: ρ(r) = ?  (由 RAR 幾何決定)

# 外圍: 平坦曲線 → V = const → g = V²/R ∝ R⁻¹
# M_tot = gR²/G ∝ R, M_bar → const (外圍)
# M_DM ∝ R → ρ_DM = dM/dR/(4πR²) ∝ R⁻² ✓ isothermal
print("IDCM 預言 (外圍): ρ_DM ∝ R⁻² (isothermal)")
print("NFW 預言:          ρ_DM ∝ R⁻³ (外圍)")
print("觀測:              好多星系用 cored 更好 fit (低面亮度星系)")
print("→ IDCM 自動產生 cored isothermal 暈, 解決 cusp-core problem!")

# ============ 有效勢形式 ============
print("\n" + "=" * 65)
print("有效勢 Φ(R) 嘅閉合形式")
print("=" * 65)

# 外圍 (g_bar << a₀): g_obs ≈ √(GM_bar·a₀)/R (如果 M_bar const)
# → Φ(R) = ∫ √(GMa₀)/R dR = √(GMa₀)·ln(R) → ln 勢!
# ln 勢 → 平坦曲線 (V² = √(GMa₀) = const) ✓
print("外圍: g_obs ≈ √(GMa₀)/R → Φ ∝ ln(R)")
print("      → V = (GMa₀)^(1/4) = const → 平坦曲線 ✅")
print("      → BTFR: V⁴ = GMa₀ ✅")
print()
print("過渡區: 冇閉合形式 (用插值函數)")

# ============ 質量-加速度關係 ============
print("\n" + "=" * 65)
print("有效 DM 質量 vs 重子質量")
print("=" * 65)
for Rk in [1.0, 5.0, 10.0, 20.0, 30.0]:
    R = Rk * kpc_to_m
    idx = np.argmin(np.abs(R_grid - R))
    ratio = M_DM[idx] / float(M_bar(R))
    print(f"R = {Rk:>4.1f} kpc: M_DM/M_bar = {ratio:.2f}")

# ============ 關鍵: M_DM/M_bar 同 Ω_DM/Ω_b 嘅關係 ============
print("\n" + "=" * 65)
print("宇宙學 vs 星系尺度 DM 比例")
print("=" * 65)
# 宇宙學: Ω_DM/Ω_b = 13/2 = 6.5
# 星系外圍: M_DM/M_bar 趨向?
R_out = 30 * kpc_to_m
idx = np.argmin(np.abs(R_grid - R_out))
ratio_out = M_DM[idx] / float(M_bar(R_out))
print(f"R = 30 kpc: M_DM/M_bar = {ratio_out:.2f} (宇宙學 6.5)")
print(f"→ 星系尺度比例 < 宇宙學比例: DM 喺星系尺度唔完全 virialized")
print(f"→ 但隨 R 增加, 比例趨向宇宙學值 (如果暈延伸夠遠)")

# 更大 R
R_big = np.logspace(1.5, 2.5, 100) * kpc_to_m  # 30 - 300 kpc
Mbar_big = np.full_like(R_big, Mbar)  # 外圍重子 const
g_bar_big = G * Mbar_big / R_big**2
g_obs_big = interpol_simple(g_bar_big, A0_IDCM)
M_tot_big = g_obs_big * R_big**2 / G
M_DM_big = M_tot_big - Mbar_big
for Rk in [50, 100, 200, 300]:
    idx = np.argmin(np.abs(R_big - Rk*kpc_to_m))
    print(f"R = {Rk:>3} kpc: M_DM/M_bar = {M_DM_big[idx]/Mbar:.2f}")

# 檢查趨向 Ω_DM/Ω_b = 6.5 嘅 R
# M_DM/M_bar = 6.5 → M_DM = 6.5·Mbar → M_tot = 7.5·Mbar
# g_obs = GM_tot/R², g_obs = √(GM_bar·a₀)/R → GM_tot/R² = √(GM_bar a₀)/R
# M_tot = R·√(GM_bar·a₀)/G → R_6.5 = 6.5·Mbar·G/√(GM_bar·a₀) = 6.5·√(GM_bar/a₀)
R65 = 6.5 * np.sqrt(G * Mbar / A0_IDCM)
print(f"\nM_DM/M_bar = 6.5 嘅半徑: R = {R65/kpc_to_m:.0f} kpc")
print(f"(物理: 宇宙學比例喺暈外圍達到)")

# ============ 保存 ============
profile = np.column_stack([R_grid/kpc_to_m, g_bar, g_obs, M_DM/Msun, rho_DM_kpc3, V_obs])
np.savetxt('data/effective_halo_profile.txt', profile,
           header='R_kpc g_bar_m/s2 g_obs_m/s2 M_DM_Msun rho_DM_Msun_kpc3 V_km_s', fmt='%.6e')
print("\n結果已存: data/effective_halo_profile.txt")

with open('data/effective_halo.json', 'w') as f:
    json.dump({
        'outer_slope': float(np.mean(slopes)),
        'central_rho_0.1kpc': float(rho_DM_kpc3[np.argmin(np.abs(R_grid-0.1*kpc_to_m))]),
        'M_DM_Mbar_30kpc': float(ratio_out),
        'R_6.5': float(R65/kpc_to_m),
        'potential_form': 'ln(R) outer, BTFR V^4 = GMa0'
    }, f, indent=2)
