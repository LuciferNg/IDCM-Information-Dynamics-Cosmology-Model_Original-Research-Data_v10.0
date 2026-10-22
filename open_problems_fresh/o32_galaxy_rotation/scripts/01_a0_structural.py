#!/usr/bin/env python3
"""
O32-01: IDCM 星系旋轉曲線 — 結構常數推導
============================================
目標: 推導 IDCM 的 a₀ (MOND 臨界加速度) 零自由參數表達式

IDCM 結構:
  R_H = c/H₀ = 4129.94 Mpc  (K_Chain 環周長, H₀_idcm = 72.59 km/s/Mpc)
  λ_sync = 294.88 Mpc        (宇宙同步波長)
  K_Tree: 33 levels, B=4

關鍵洞察:
  MOND 的 a₀ ≈ 1.2e-10 m/s² ≈ cH₀/2π
  IDCM: a₀_idcm = c²/(2π R_H) = cH₀/2π  ← 零自由參數, 因為 R_H = c/H₀ 係結構定義!

物理意義:
  喺 IDCM 無膨脹宇宙, R_H 唔係粒子視界, 而係 K_Chain 環周長。
  星系旋轉曲線嘅平坦部分 = W-field 共振效應, 加速度低於 a₀ 時
  引力被 K_Chain 諧波結構放大。
"""
import numpy as np

# ============ IDCM 結構常數 ============
c = 299792.458          # km/s
R_H = 4129.94           # Mpc
H0_idcm = c / R_H       # 72.59 km/s/Mpc
Mpc_to_m = 3.085677581e22  # m
c_ms = c * 1e3          # m/s

# 單位轉換
# H0 in s^-1: H0_km/s/Mpc -> s^-1
# 1 Mpc = 3.085677581e22 m = 3.085677581e19 km
Mpc_to_km = 3.085677581e19
H0_s = H0_idcm / Mpc_to_km  # s^-1

print("=" * 60)
print("O32-01: IDCM a₀ 結構常數推導")
print("=" * 60)
print(f"H₀_idcm = c/R_H = {H0_idcm:.4f} km/s/Mpc")
print(f"R_H = {R_H} Mpc")

# ============ a₀ 推導 ============
# MOND: a₀ ≈ 1.2e-10 m/s²
# IDCM 候選: a₀ = cH₀/2π (物理: R_H 環上嘅向心加速度標度)
a0_idcm = c_ms * H0_s / (2 * np.pi)
print(f"\na₀_idcm = cH₀/2π = {a0_idcm:.4e} m/s²")

# 另一種表達: a₀ = c²/(2πR_H)
a0_idcm2 = c_ms**2 / (2 * np.pi * R_H * Mpc_to_m)
print(f"a₀_idcm = c²/(2πR_H) = {a0_idcm2:.4e} m/s² (相同: {abs(a0_idcm-a0_idcm2)/a0_idcm:.2e})")

# MOND 觀測值 (McGaugh 2016 RAR, Lelli+2017):
a0_obs = 1.2e-10
print(f"\nMOND 觀測 a₀ = {a0_obs:.2e} m/s²")
print(f"IDCM/MOND = {a0_idcm/a0_obs:.4f}")
print(f"偏差 = {(a0_idcm-a0_obs)/a0_obs*100:.2f}%")

# ============ 更精確的 MOND a₀ (RAR 擬合) ============
# Lelli+2017 (RAR): a₀ = 1.2e-10 m/s², 但 McGaugh+2016: 1.2e-10
# 精確值: a₀ = 1.2e-10 ± 0.026e-10 (MOND 標準)
# 另一個常用: a₀ ≈ 1.2e-10 = cH₀/(2π) 用 H₀ = 72.59
print(f"\n[註] 用 H₀ = 72.59: cH₀/2π = {a0_idcm:.4e}")
print(f"[註] 用 H₀ = 67.4 (Planck): cH₀/2π = {c_ms*(67.4/Mpc_to_km)/(2*np.pi):.4e}")

# ============ 關鍵: a₀ 的 φ 結構 ============
# IDCM: Ω_Λ = 4/(φ⁴-1) = 0.68328, Ω_m = 3ε/(1+3ε)
# a₀ = c²/(2πR_H) 係純幾何, 無 φ 依賴!
# 但 MOND 的 a₀ 有已知關係: a₀ ≈ cH₀/2π ≈ 1.2e-10
phi = (1 + np.sqrt(5)) / 2
print(f"\nφ = {phi:.6f}")
print(f"φ⁻¹ = {1/phi:.6f}")

# 檢查: a₀ 用 λ_sync 表達?
# λ_sync = 2πR_H/88 = πR_H/44 (因為 ℓ_sync = 44 = 2N_d)
lambda_sync = 2 * np.pi * R_H / 88
print(f"\nλ_sync = 2πR_H/88 = {lambda_sync:.2f} Mpc (檢查: {294.88})")
print(f"→ a₀ = c²/(2πR_H) = c²/(88·λ_sync/2·...)  [無需]")

# ============ 深層結構: a₀ = cH₀/2π 的 K_Chain 意義 ============
# R_H = 44·dx, dx = 93.86 Mpc (site spacing)
# a₀ = c²/(2π·44·dx) = c²/(88π·dx)
dx = R_H / 44
print(f"\nsite 間距 dx = R_H/44 = {dx:.4f} Mpc")
print(f"a₀ = c²/(88π·dx) = {c_ms**2/(88*np.pi*dx*Mpc_to_m):.4e} m/s²")
print(f"→ a₀ 對應 K_Chain 一個 site 嘅「環向心加速度」: c²/(44·dx·2π)")

# ============ v(r) 預測 ============
# MOND 深 MOND 極限: v⁴ = G·M·a₀
# 平坦速度: V_f = (G·M·a₀)^(1/4)
G = 6.674e-11  # m³/(kg·s²)
Msun = 1.989e30  # kg
kpc_to_m = 3.085677581e19  # m

# 測試一個典型星系: NGC 2403, M_bary ~ 8e9 Msun, V_f ~ 130 km/s
M_bary = 8e9 * Msun
V_f_pred = (G * M_bary * a0_idcm) ** 0.25
print(f"\n典型星系 M_bary = 8e9 Msun:")
print(f"V_f = (G·M·a₀)^(1/4) = {V_f_pred/1e3:.1f} km/s (NGC 2403: ~130)")

# ============ 總結 ============
print("\n" + "=" * 60)
print("結論:")
print(f"  a₀_idcm = cH₀/2π = {a0_idcm:.4e} m/s²")
print(f"  MOND a₀   = {a0_obs:.2e} m/s²")
print(f"  偏差 = {(a0_idcm-a0_obs)/a0_obs*100:.2f}%")
print(f"  → 零自由參數! R_H 由 H₀ 結構定義, a₀ 係純幾何")
print("=" * 60)
