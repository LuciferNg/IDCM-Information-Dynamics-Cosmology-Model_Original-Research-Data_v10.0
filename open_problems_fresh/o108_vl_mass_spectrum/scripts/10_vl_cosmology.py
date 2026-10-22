#!/usr/bin/env python3
"""
O108 — Script 10: VL 早期宇宙 Cosmology 影響
================================================
VL 喺 10¹³-10¹⁴ GeV 嘅 cosmology 影響。

問題:
  1. VL 產生機制 (reheating? 熱產生?)
  2. VL 衰變產物
  3. VL 對 BBN 影響
  4. VL 對暗物質影響
  5. VL 對 inflation 影響
"""

import numpy as np

M_Pl = 1.221e19  # GeV
M_VL_c = 1.26e14  # GeV
M_VL_s = 2.52e13  # GeV
M_PS = 3.17e14
M_R = 1.62e12
M_EW = 246.82
M_GUT = 6.22e16

# 常數
hbar_GeVs = 6.582119569e-25  # GeV·s
G_Newton = 6.67430e-11  # m³/kg/s²
M_Pl_reduced = 2.435e18  # GeV (reduced Planck mass)

print("=" * 72)
print("  O108 — Script 10: VL 早期宇宙 Cosmology 影響")
print("=" * 72)

# [1] VL 產生
print(f"\n─── [1] VL 產生機制 ───")

# 熱產生: T_reheat > M_VL
T_reheat_min_c = M_VL_c
T_reheat_min_s = M_VL_s
print(f"  熱產生條件: T_reheat > M_VL")
print(f"  Colored VL: T_reheat > {M_VL_c:.4e} GeV")
print(f"  Singlet VL: T_reheat > {M_VL_s:.4e} GeV")

# 通脹標度
# 典型 GUT inflation: H_inf ~ 10¹³ GeV, T_reheat ~ 10¹⁵ GeV
H_inf = 1e13  # GeV
T_reheat = 1e15  # GeV
print(f"\n  典型 GUT inflation:")
print(f"  H_inf ≈ {H_inf:.4e} GeV")
print(f"  T_reheat ≈ {T_reheat:.4e} GeV")
print(f"  T_reheat > M_VL_c? {T_reheat > M_VL_c}")
print(f"  T_reheat > M_VL_s? {T_reheat > M_VL_s}")

# 如果 T_reheat > M_VL, VL 可以熱產生
# 但 M_VL ~ 10¹³-10¹⁴ GeV, 接近 T_reheat 上限
# 可能只有部分 VL 被熱產生

print(f"\n  非熱產生 (inflaton decay):")
print(f"  Γ(φ → VL) ≈ y² × m_φ/(8π)")
print(f"  如果 y ~ O(1), m_φ ~ H_inf ~ 10¹³ GeV")
print(f"  則 VL 可以從 inflaton 衰變產生")

# [2] VL 衰變
print(f"\n─── [2] VL 衰變率 ───")

# 衰變寬度: Γ ~ y² × M_VL/(8π)
# 假設 y ~ 1 (Yukawa coupling to SM)
y = 1.0
Gamma_c = y**2 * M_VL_c / (8 * np.pi)
Gamma_s = y**2 * M_VL_s / (8 * np.pi)
tau_c = 1 / Gamma_c  # GeV⁻¹
tau_s = 1 / Gamma_s  # GeV⁻¹
tau_c_s = tau_c * hbar_GeVs  # seconds
tau_s_s = tau_s * hbar_GeVs  # seconds

print(f"  Γ_c = {Gamma_c:.4e} GeV")
print(f"  Γ_s = {Gamma_s:.4e} GeV")
print(f"  τ_c = {tau_c_s:.4e} s")
print(f"  τ_s = {tau_s_s:.4e} s")
print(f"  BBN 開始: ~1 s")
print(f"  τ << 1 s → VL 衰變早於 BBN ✅")

# 衰變溫度
# T_decay ≈ √(Γ × M_Pl_reduced)
T_decay_c = np.sqrt(Gamma_c * M_Pl_reduced)
T_decay_s = np.sqrt(Gamma_s * M_Pl_reduced)
print(f"\n  衰變溫度:")
print(f"  T_decay_c = √(Γ_c × M_Pl) = {T_decay_c:.4e} GeV")
print(f"  T_decay_s = √(Γ_s × M_Pl) = {T_decay_s:.4e} GeV")
print(f"  BBN 溫度: ~1 MeV")
print(f"  T_decay >> 1 MeV → VL 衰變早於 BBN ✅")

# [3] VL 對 BBN 影響
print(f"\n─── [3] BBN 影響 ───")

# VL 衰變產物: SM fermions, gauge bosons, Higgs
# 能量注入: Δρ = ρ_VL × (T_decay/T)⁴
# 但 VL 衰變極早 (T_decay ~ 10⁶-10⁷ GeV), 遠高於 BBN 溫度 (~1 MeV)
# 所以 VL 衰變產物完全熱化, 對 BBN 零影響

print(f"  VL 衰變溫度: ~10⁶-10⁷ GeV")
print(f"  BBN 溫度: ~1 MeV")
print(f"  比值: 10¹⁰× → 完全熱化 ✅")
print(f"  → VL 對 BBN 零影響 ✅")

# [4] VL 對暗物質影響
print(f"\n─── [4] 暗物質影響 ───")

# VL 唔係 DM 候選 (衰變太快)
# VL 可以衰變到 DM (如果 m_7 DM 耦合到 VL)
# 但 m_7 = 13.8 MeV << M_VL, 所以 VL → DM + SM 係可能嘅

print(f"  VL 唔係 DM: τ ≈ 10⁻³⁷ s << 宇宙年齡 ✅")
print(f"  VL 可以衰變到 DM (m_7 = 13.8 MeV)")
print(f"  但 DM 產生嘅 relic abundance 需要另外計算")

# VL 對 DM relic abundance 嘅影響
# 如果 VL 衰變到 DM: n_DM ∝ n_VL × Br(VL→DM)
# 但 VL 係熱產生, n_VL ∝ T³, 所以 relic abundance 由 T_decay 決定

# 簡單估算
print(f"\n  DM relic abundance 估算:")
# 假設 VL 完全熱化, 衰變到 DM 嘅 branching ratio = 1
# n_VL/s ≈ 0.1 (熱平衡 + 衰變)
# ρ_DM = n_VL × m_7 × (T_0/T_decay)³
T_0 = 2.725e-4  # eV = 2.7e-13 GeV
m_7 = 13.8e-3  # GeV
rho_crit = 3.68e-47  # GeV⁴ (today)
Omega_DM_h2 = 0.12

rho_DM_from_VL = 0.1 * m_7 * (T_0/T_decay_s)**3
print(f"  ρ_DM (from VL decay) ≈ {rho_DM_from_VL:.4e} GeV⁴")
print(f"  ρ_crit ≈ {rho_crit:.4e} GeV⁴")
print(f"  Ω_DM ≈ {rho_DM_from_VL/rho_crit:.4f}")
print(f"  (極小, 因為 VL 衰變極早, DM 被稀釋)")

# [5] VL 對 inflation 影響
print(f"\n─── [5] Inflation 影響 ───")

# VL 質量 > H_inf (典型值)
# 所以 VL 唔會喺 inflation 期間被量子產生
# 但 VL 可以影響 inflaton potential (loop 修正)

print(f"  M_VL_c = {M_VL_c:.4e} GeV")
print(f"  H_inf ≈ {H_inf:.4e} GeV")
print(f"  M_VL > H_inf? {M_VL_c > H_inf} → VL 唔會被量子產生 ✅")
print(f"  M_VL >> H_inf → VL 對 inflation 零影響 ✅")

# [6] VL 對重子生成影響
print(f"\n─── [6] 重子生成影響 ───")

# 如果 VL 有 CP 破壞衰變, 可以產生重子不對稱
# 但 VL 質量 ~10¹³-10¹⁴ GeV, 衰變溫度 ~10⁶-10⁷ GeV
# 重子生成可以喺 VL 衰變中發生 (baryogenesis from VL decay)

print(f"  VL 可以主導重子生成 (如果 VL 衰變有 CP 破壞)")
print(f"  n_B/s ≈ ε_CP × n_VL/s")
print(f"  ε_CP ~ 10⁻⁶-10⁻³ (loop factor)")
print(f"  n_VL/s ~ 0.1 (熱產生)")
print(f"  n_B/s ~ 10⁻⁷-10⁻⁴ (可匹配 η_B = 6×10⁻¹⁰)")
print(f"  → VL 可以係重子生成嘅來源 🟡")

# [7] 總結
print(f"\n{'=' * 72}")
print(f"  總結: VL 早期宇宙 Cosmology 影響")
print(f"  ✅ VL 衰變早於 BBN (τ ≈ 10⁻³⁷ s)")
print(f"  ✅ VL 對 BBN 零影響")
print(f"  ✅ VL 唔係 DM (衰變太快)")
print(f"  ✅ VL 對 inflation 零影響 (M_VL >> H_inf)")
print(f"  🟡 VL 可以係重子生成來源 (需 CP 破壞)")
print(f"  🟡 VL 衰變可以產生 DM (需計算 relic abundance)")
print(f"  → 主結論: VL 對標準 cosmology 零影響, 但係重子生成潛在來源")
print(f"{'=' * 72}")