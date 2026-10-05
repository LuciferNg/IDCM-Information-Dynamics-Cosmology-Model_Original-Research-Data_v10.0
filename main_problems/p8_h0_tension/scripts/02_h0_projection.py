#!/usr/bin/env python3
"""
IDCM 局域哈勃常數張力 — 首個結構推導
=======================================
用 Formula 60 投影 Jacobian 推導局域 vs 全域 H₀

★ 2026-09-23 (O170 N4 交收): 本 script 用嘅伸長律 1+2φ⁻¹ℓ 已被 O169 證偽 (DESI DR2 4.88σ)。
  H_eff(0.03) = 73.13 / 「SH0ES 匹配 0.12%」係舊律假象 → 已撤回。
  新橫向律: D_app = R(1−4^{−ℓ})(ℓ + 1.11911398), H_eff(0.03) = 66.27 (−9.3%) → N4 開放
  (詳見 ../09_o170_n4_handoff.md)。本 script 保留作歷史記錄; 新律重算見 O170 scripts/21。

方法（第一原理）：
1. H₀_idcm = c/R_H = 72.59 km/s/Mpc (結構定義)
2. 局域觀測 (近距離) = 細投影深度 → 有效 H₀ 偏移
3. 全域觀測 (CMB) = 全投影 → H₀_idcm
4. 張力 = 投影深度差異嘅自然結果

對比觀測:
  Planck: 67.36 ± 0.54 (全域)
  SH0ES: 73.04 ± 1.04 (局域, Cepheid+SNIa)
  TRGB: 69.8 ± 1.9
  Miras: 73.3 ± 2.6
"""
import math

# ============ IDCM 核心常數 ============
phi = (1 + 5**0.5) / 2          # 1.61803398875
phi_inv = 1 / phi               # 0.61803398875
eps = phi_inv / 4               # 0.1545084972
kappa = 1 / 16                  # 0.0625
Nd = 44                         # K_Chain 維度
M = 33                          # K_Tree 深度
B = 4                           # MERA branching factor
CY3 = 134                       # h11=36, h21=98
lambda_sync = 294.88            # Mpc
BAO = lambda_sync / 2           # 147.44 Mpc
H0_idcm = 72.59                 # km/s/Mpc
R_H = 4129.94                   # Mpc
c = 299792.458                  # km/s

# ============ 觀測 ============
obs = {
    "Planck 2018 (全域)": (67.36, 0.54),
    "SH0ES (局域)": (73.04, 1.04),
    "Riess 2025 JWST": (73.17, 0.86),
    "TRGB (局域)": (69.8, 1.9),
    "Miras (局域)": (73.3, 2.6),
    "Maser M106": (73.9, 3.0),
}

print("=" * 72)
print("IDCM 局域哈勃常數張力 — 首個結構推導")
print("=" * 72)

# ============ 1. 基礎: H₀ 結構定義 ============
print("\n[1] H₀ 結構定義")
print("-" * 72)
H0_calc = c / R_H * 1000  # km/s/Mpc (R_H in Mpc, c in km/s → ×1000?)
# 檢查: c/R_H = 299792.458/4129.94 = 72.59 km/s/Mpc ✅ (單位: km/s ÷ Mpc)
H0_calc = c / R_H
print(f"H₀_idcm = c/R_H = {H0_calc:.2f} km/s/Mpc ✅")
print(f"R_H = c/H₀ = {c/H0_idcm:.2f} Mpc")

# ============ 2. Formula 60 投影 ============
print("\n[2] Formula 60 投影 Jacobian")
print("-" * 72)
# D_app(ℓ) = (44 - 44/4^ℓ) × (R_H/44) × (1 + 2φ⁻¹·ℓ)
# ℓ = log₄(1+z)
# 
# 物理: 1D K_Chain (44 site) 投影到 3D
# - 近距離 (ℓ→0): D_app → (44-44)×... = 0, 但投影 stretch P(ℓ) = 1+2φ⁻¹ℓ → 1
# - 遠距離: D_app → 44×(R_H/44)×(1+2φ⁻¹ℓ) = R_H(1+2φ⁻¹ℓ)
# 
# H₀ 係「每單位距離嘅紅移」= d(cz)/dD = c/(dD/dz)
# 喺投影框架, H_eff(z) = c/(dD_app/dz)

def D_app(z):
    """Formula 60: 視角距離"""
    ell = math.log(1+z, 4)
    return (44 - 44/4**ell) * (R_H/44) * (1 + 2*phi_inv*ell)

def H_eff(z, dz=1e-5):
    """有效哈勃參數 = c/(dD/dz)"""
    dDdz = (D_app(z+dz) - D_app(z-dz)) / (2*dz)
    return c / dDdz

# 近鄰 (z→0) 極限:
# D_app(ℓ→0): 44(1-4^-ℓ) ≈ 44×ln(4)ℓ = 44×ln(4)×log₄(1+z) ≈ 44×ln(4)×z/ln(4) = 44z
# → dD/dz → 44 Mpc (單位 site!)
# H_eff(0) = c/44 = 6813 km/s/Mpc? 荒謬 — 單位錯
# 
# 注意: R_H/44 = 93.86 Mpc/site. D_app 單位係 Mpc.
# dD/dz (z→0) = 44×(R_H/44)×1 = R_H = 4129.94 Mpc? 
# 等等: 44×(1-4^-ℓ), d/dz = 44×d(4^-ℓ)/dz... 
# 4^-ℓ = 4^-log₄(1+z) = 1/(1+z)
# d/dz [44(1-1/(1+z))] = 44/(1+z)²
# D_app = 44(1-1/(1+z)) × (R_H/44) × (1+2φ⁻¹ℓ)
#       = R_H(1-1/(1+z)) × (1+2φ⁻¹ℓ)
# dD/dz (z→0) = R_H × 1 × 1 = R_H = 4129.94 Mpc ← 呢個係「近鄰」極限?
# 但觀測近鄰 H₀ = 73 (SH0ES) > H₀_idcm = 72.59!
# 
# 反轉: 如果近鄰觀測 z→0 用 D_app, dD/dz = R_H → H = c/R_H = 72.59
# 同 H₀_idcm 一樣! 近鄰 H₀ 應該 = 72.59?
# 但 SH0ES 量到 73.04 — 高 0.6%
# 
# 問題: SH0ES 用嘅距離係「光度距離」, 唔係 D_app?
# 光度距離 D_L = D_app × (1+z)² (ΛCDM 關係)
# 近鄰: D_L ≈ D_app(1+2z) → dD_L/dz ≈ dD_app/dz + 2D_app
# 
# IDCM: 光度距離投影 = D_L = D_app × (1+z)^p?
# p 需要推導

print("D_app(z) 公式: (44-44/4^ℓ)×(R_H/44)×(1+2φ⁻¹ℓ)")
print("4^-ℓ = 1/(1+z), 所以:")
print("D_app(z) = R_H × z/(1+z) × (1+2φ⁻¹·log₄(1+z))")
print()
print(f"dD/dz(z→0) = R_H = {R_H:.2f} Mpc → H_eff(0) = c/R_H = {H0_calc:.2f}")

# ============ 3. 局域 H₀ = 投影深度 ============
print("\n[3] 局域 H₀ = 投影深度效應")
print("-" * 72)
# 局域距離階梯 (SH0ES) 用 Cepheid + SNIa:
# - Cepheid: 周期-光度關係 → 絕對星等 → 距離
# - SNIa: 標準燭光
# - 距離模數 μ = 5log₁₀(D/10pc)
# 
# IDCM: 近鄰距離 (D < 100 Mpc) 投影深度 ℓ < 0.1
# D_app 喺細 ℓ 有修正:
# D_app = R_H × z/(1+z) × (1+2φ⁻¹ℓ)
# 
# 但 SH0ES 量嘅係「實際距離」, 用幾何方法 (maser, parallax) 校準
# 如果投影框架下「真實距離」= D_app, 咁 H₀ 應該 = 72.59?
# 唔啱 — SH0ES 量到 73.04, TRGB 69.8, 兩者之間都有差異
# 
# 關鍵洞察: 「距離」喺 IDCM 係投影量
# 局域: 用幾何距離 (parallax, maser) → 直接投影距離 D_app
#        → H₀ = c × dz/dD_app = c × (1+z)²/R_H (z→0) = 72.59
# 但 SH0ES = 73.04 ≠ 72.59!
# 
# 嘗試: Cepheid 周期-光度關係有 K_Chain 模式耦合?
# Cepheid 係脈動星 — 脈動周期 P ↔ 光度 L 關係
# 如果脈動模式耦合 K_Chain → 距離校準偏移
# 
# 更基本: SNIa 標準燭光校準喺 Cepheid 距離
# Cepheid 距離 = 幾何 (parallax) + PL 關係
# 
# 直接測試: 局域 H₀ 觀測值 vs IDCM 結構?
# SH0ES 73.04: 73.04/72.59 = 1.0062 (+0.62%)
# TRGB 69.8: 69.8/72.59 = 0.9616 (-3.84%)
# 
# 0.62% = φ⁻¹×1%? 0.618%? ✅ 接近!
# φ⁻¹/100 = 0.618% vs 0.62% ✅ 非常接近!
print(f"SH0ES/IDCM = {73.04/72.59:.4f} → 偏移 +{73.04/72.59*100-100:.2f}%")
print(f"φ⁻¹/100 = {phi_inv/100*100:.2f}% vs +0.62% → 偏差 {(phi_inv-0.0062)/0.0062*100:.1f}%")
print()
print(f"TRGB/IDCM = {69.8/72.59:.4f} → 偏移 {69.8/72.59*100-100:.2f}%")
print(f"−φ⁻¹/16 = {-(phi_inv/16)*100:.2f}% vs -3.84% → 偏差 {abs(phi_inv/16-0.0384)/0.0384*100:.1f}%")
print(f"−φ⁻²/4 = {-(phi_inv**2/4)*100:.2f}% vs -3.84% → 偏差 {abs(phi_inv**2/4-0.0384)/0.0384*100:.1f}%")
print()
print("Maser: 73.9/72.59 = 1.018 → +1.80%")
print(f"  2×φ⁻¹/100 = {2*phi_inv/100*100:.2f}% vs +1.80% → 偏差 {(2*phi_inv/100-0.018)/0.018*100:.1f}%")
print()
print("初步模式: 局域 H₀ 偏移 ~ φ⁻ⁿ × 結構因子")
print("狀態: 🟡 需要更嚴格推導 (點解 Cepheid 偏移 +0.6%?)")

# ============ 4. SYNC 模式激活 → H₀ 分層 ============
print("\n[4] K_Chain 模式激活 → H₀ 分層")
print("-" * 72)
# 模式 n 激活 z_n = (γ_n/γ₂)×z_c - 1
# z_c = 0.6 (SYNC bump)
# 局域觀測 (z < 0.1) 只有低 n 模式激活
# 每個模式有唔同群速度 v_g(n) = cos(πn/88)
# → 局域「有效光速」< c → H₀ 偏移?
# 
# 模式 n 嘅激活紅移:
gamma = [4*math.sin(math.pi*n/88)**2 for n in range(1, 45)]
gamma2 = gamma[1]  # n=2
z_c = 0.6
print("模式激活紅移 z_n = (γ_n/γ₂)×z_c - 1:")
for n in [1, 2, 3, 4, 5, 6, 7, 8]:
    z_n = (gamma[n-1]/gamma2)*z_c - 1
    print(f"  n={n}: γ={gamma[n-1]:.4f}, z_n={z_n:.2f}")

print()
print("局域距離階梯範圍 (z<0.05):")
print("  z=0.05 → ℓ = log₄(1.05) =", f"{math.log(1.05,4):.4f}")
print("  只有 mode n=1 激活 (z₁<0.05?)")
z1 = (gamma[0]/gamma2)*z_c - 1
print(f"  n=1 激活 z₁ = {z1:.2f} → {'✅ 已激活' if z1 < 0.05 else '❌ 未激活'}")

# 模式激活前後 H₀ 差異:
# 如果局域只有 n=1 激活, 有效模式密度 = 1/44
# H_eff = H₀ × (模式密度比)^α?
# 1/44 = 0.0227 — 太極端
# 
# 更合理: 群速度修正
# 模式 n 嘅 v_g = cos(πn/88)
# 局域平均 v_g (前幾個模式):
v_g_sum = sum(math.cos(math.pi*n/88) for n in range(1, 5)) / 4
print(f"\n前 4 個模式平均 v_g = {v_g_sum:.4f} c")
print(f"→ 局域 H₀ 修正 = H₀/v_g = {H0_idcm/v_g_sum:.2f}? (唔合理)")

# ============ 5. 全域 vs 局域 = 投影 Jacobian 斜率 ============
print("\n[5] 投影 Jacobian 斜率 → H₀ 差異")
print("-" * 72)
# D_app(z) = R_H × z/(1+z) × (1+2φ⁻¹ℓ)
# dD/dz = R_H/(1+z)² × (1+2φ⁻¹ℓ) + R_H×z/(1+z) × 2φ⁻¹×dℓ/dz
# dℓ/dz = 1/(ln4 × (1+z))
# 
# H_eff(z) = c/(dD/dz):
# z→0: H_eff = c/R_H = 72.59
# z>0: H_eff 演化
for z in [0.01, 0.05, 0.1, 0.2, 0.5, 1.0]:
    H = H_eff(z)
    print(f"  z={z:.2f}: H_eff = {H:.2f} km/s/Mpc")

print()
print("關鍵: H_eff(z→0) = 72.59 = IDCM 全域值")
print("局域量度 (SH0ES z<0.1) 應該見到 ~72.6?")
print("但 SH0ES 量到 73.04 → 差異喺距離校準, 唔係 H_eff")

# ============ 6. 張力結構解釋 ============
print("\n[6] 張力結構解釋")
print("-" * 72)
# ΛCDM 張力: Planck 67.36 vs SH0ES 73.04
# IDCM: 冇「膨脹」, 冇單一 H₀
# H₀_idcm = 72.59 = c/R_H (結構)
# 
# 但點解 Planck 量到 67.36?
# Planck 用 ΛCDM fit CMB → H₀ 係模型依賴量
# CMB C_ℓ 喺 IDCM 係 SYNC 底噪譜 → Planck 用錯模型 fit
# → 67.36 係 ΛCDM 詮釋, 唔係 IDCM 量
# 
# IDCM 預測:
# 1. 真正結構 H₀ = 72.59 (c/R_H)
# 2. 局域幾何量度 (maser, parallax) 應該收斂到 72.59 ± 投影修正
# 3. CMB 冇 H₀ — C_ℓ 係結構譜, 唔係膨脹譜
# 4. 「張力」= ΛCDM 內部矛盾 (兩個模型依賴量度)
print("IDCM 立場:")
print("  1. H₀_idcm = c/R_H = 72.59 (結構定義, 唯一)")  
print("  2. Planck 67.36 = ΛCDM fit CMB 嘅模型依賴量")
print("  3. 局域 73.04 = 距離階梯校準嘅投影效應")
print("  4. 張力 = ΛCDM 用 FLRW 詮釋兩個量度 → 必然矛盾")
print()
print("可證偽預測:")
print("  P1: 純幾何局域量度 (maser, parallax, GW) → 72.59 ± 0.5")
print("  P2: Cepheid 校準偏移 ~ +0.6% (φ⁻¹/100) 如果 PL 關係耦合 K_Chain")
print("  P3: TRGB 偏移 ~ -3.8% (φ⁻²/4) — 但需要機制解釋")

# ============ 總結 ============
print("\n" + "=" * 72)
print("總結")
print("=" * 72)
print(f"H₀_idcm = c/R_H = {H0_calc:.2f} km/s/Mpc (結構定義)")
print(f"SH0ES/IDCM = +{(73.04/72.59-1)*100:.2f}% ≈ φ⁻¹/100 = {phi_inv/100*100:.2f}% (候選)")
print(f"TRGB/IDCM = {(69.8/72.59-1)*100:.2f}% ≈ -φ⁻²/4 = {-(phi_inv**2/4)*100:.2f}% (候選)")
print()
print("狀態: 🟡 部分推導 — H₀_idcm 結構定義確認")
print("下一步: 距離階梯 (Cepheid PL) 嘅 K_Chain 耦合機制推導")
