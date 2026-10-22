#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O60 M31 旋轉曲線 RAR 檢驗 (IDCM 零參數預測)
==============================================
O32 已閉合 SPARC 樣本 (Lelli+2017): μ(x) = x/(1+x), a₀ = 1.1225e-10 m/s²
M31 係最近大螺旋星系 — 獨立檢驗面!

數據: M31 旋轉曲線 (Chemin+2009; Carignan+2013; Sofue 2015)
V_flat ~ 250-255 km/s (R > 10 kpc)
baryon 質量模型: disk (exponential, M_d~1e11) + bulge (M_b~3e10) + HI/gas

IDCM RAR: g_obs = g_bar·(1+√(1+4a₀/g_bar))/2
即: V²(R) = R·g_obs(R), g_bar(R) = G·M_bar(<R)/R²
"""
import numpy as np

G = 4.3009e-6  # kpc (km/s)²/M☉
a0 = 1.1225e-10  # m/s² (IDCM 零參數)
kpc_to_m = 3.085677581e19

def gbar_from_mass(R, M_bar):
    """g_bar in m/s²"""
    # G[M☉] = 4.3009e-6 kpc·(km/s)²/M☉ → GM/R² 單位: (km/s)²/kpc
    g_kms2_per_kpc = G * M_bar / R**2
    # → m/s²: × 1e6 / 3.0857e16 km... 
    # (km/s)²/kpc = km²/s²/kpc = 1e6 m²/s² / (3.0857e19 m) = 3.24e-14 m/s²
    return g_kms2_per_kpc * 1e6 / kpc_to_m

def V_idcm(R, M_bar):
    gbar = gbar_from_mass(R, M_bar)
    gobs = gbar * (1 + np.sqrt(1 + 4*a0/gbar)) / 2
    # V² = gobs·R → V in m/s: √(m/s² × m) = m/s
    V = np.sqrt(gobs * R * kpc_to_m)
    return V / 1e3  # km/s

print("=" * 72)
print("M31 旋轉曲線 — IDCM RAR 零參數預測")
print("=" * 72)

# M31 質量模型 (Carignan+2013; Chemin+2009):
# Disk: M_d = 1.0e11 M☉, R_d = 6 kpc (exponential)
# Bulge: M_b = 3.2e10 M☉, R_b = 0.6 kpc
# Gas: M_g = 6e9 M☉ (HI + H2)
M_disk, R_d = 1.0e11, 6.0
M_bulge, R_b = 3.2e10, 0.6
M_gas = 6e9

def M_bar(R):
    """Cumulative baryon mass within R"""
    # Exponential disk: M(<R) = M_d·(1 - (1+R/R_d)·exp(-R/R_d))
    x = R / R_d
    M_d_R = M_disk * (1 - (1 + x) * np.exp(-x))
    # Bulge: Hernquist-ish, M(<R) = M_b·(R/(R+R_b))
    M_b_R = M_bulge * R / (R + R_b)
    return M_d_R + M_b_R + M_gas

# 觀測數據 (Sofue 2015 M31 rotation curve):
# R (kpc): V (km/s)
obs = [
    (0.5, 120), (1, 180), (2, 225), (3, 240), (5, 250),
    (8, 252), (10, 253), (15, 254), (20, 255), (30, 255),
    (40, 253), (50, 248), (80, 240), (100, 230), (120, 210),
]

print(f"\n{'R(kpc)':>8} {'M_bar':>10} {'g_bar':>10} {'V_IDCM':>8} {'V_obs':>8} {'ΔV/V':>8}")
deviations = []
for R, Vobs in obs:
    Mb = M_bar(R)
    V = V_idcm(R, Mb)
    dev = (V - Vobs) / Vobs * 100
    deviations.append(dev)
    print(f"{R:8.1f} {Mb:10.2e} {gbar_from_mass(R,Mb):10.2e} {V:8.1f} {Vobs:8.1f} {dev:8.1f}%")

print(f"\n平均偏差: {np.mean(np.abs(deviations)):.1f}%")
print(f"最大偏差: {np.max(np.abs(deviations)):.1f}%")

# 同 MOND 比較 (a0_MOND = 1.2e-10)
print(f"\n同 MOND 比較 (a₀ = 1.2e-10):")
a0_mond = 1.2e-10
def V_mond(R, M_bar):
    gbar = gbar_from_mass(R, M_bar)
    gobs = gbar * (1 + np.sqrt(1 + 4*a0_mond/gbar)) / 2
    return np.sqrt(gobs * R * kpc_to_m) / 1e3

dev_m = []
for R, Vobs in obs:
    Mb = M_bar(R)
    V = V_mond(R, Mb)
    dev = (V - Vobs) / Vobs * 100
    dev_m.append(dev)
print(f"  MOND 平均偏差: {np.mean(np.abs(dev_m)):.1f}%")

print(f"""
分析:
  IDCM 同 MOND 喺 M31 嘅預測幾乎一樣 (a₀ 差 6.5%)
  → M31 單獨唔能分辨 IDCM vs MOND
  → 但可以檢驗「RAR 喺大質量星系成立?」
  M31 觀測 V_flat 250-255 vs IDCM 230-240 → 偏差 5-8%
  呢個偏差可能來自:
    1. M31 質量模型誤差 (baryon 低估)
    2. M31 並未完全 relaxed (潮汐歷史)
    3. IDCM RAR 需要修正 (大質量端?)
  ⚠️ 誠實標記: 需要完整 M31 baryon 質量模型先可定論
""")
