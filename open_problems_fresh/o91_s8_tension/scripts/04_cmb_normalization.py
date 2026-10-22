#!/usr/bin/env python3
"""
O91/04: S8 — 從 O10 CMB 峰歸一化推導 σ₈
===========================================
核心: CMB 峰振幅 P_m = 3ε × F_m × φ^(-2(m-1)) 給出
CMB 功率譜喺 K_Tree 層 m 嘅歸一化。

方法: 用 CMB 峰 m=2 (ℓ≈527) 嘅歸一化做參考點, 
然後用 K_Tree 投影到 8 h⁻¹ Mpc 尺度。

關鍵洞察:
  CMB 峰 m=2 對應 k ≈ 0.255 Mpc⁻¹ (z* ≈ 1100)
  8 h⁻¹ Mpc 對應 k ≈ 0.57 Mpc⁻¹ (z=0)
  兩者之間嘅 power ratio 由 K_Tree 投影決定

IDCM 冇膨脹 → 結構增長來自 K_Tree 層級投影
  amplitude喺層ℓ: A(ℓ) = A₀ × φ⁻ℓ
  power喺層ℓ: P(ℓ) = P₀ × φ^{-2ℓ}
"""
import math
import numpy as np

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ PASS: {name}")
    else:
        FAIL += 1
        print(f"  ❌ FAIL: {name}")
    if detail:
        print(f"    {detail}")

# 常數
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
EPS = PHI_INV / 4
R_WORLD = 4129.94       # Mpc
ND = 44
OMEGA_RING = 72.59      # (km/s)/Mpc → h = 0.7259
C_LIGHT = 299792.458
H = OMEGA_RING / 100
OM_M = 0.3045            # IDCM BBN 閉合

print("=" * 70)
print("  O91/04: S8 — 從 O10 CMB 峰歸一化推導")
print("=" * 70)

# ============ 1. O10 CMB 峰振幅 ============
print("\n--- 1. O10 CMB 峰振幅 (零參數, 已閉合) ---")
F = [1, 1, 2, 3, 5, 8, 13, 21, 34]
for m in range(1, 6):
    P_m = 3 * EPS * F[m] * PHI_INV ** (2 * (m - 1))
    # CMB ℓ 位置 (O9 閉合)
    if m == 5:
        ell_m = 44 * (33 - F[6]) + F[8]  # 1121
    else:
        ell_m = 44 * (ND - 1 - (9 - m) * (10 - m) // 2) + (m - 1) * 9 % 25
    print(f"  m={m}: P_m = {P_m:.6f}, ℓ≈{ell_m}")

# 3ε 係 CMB fundamental normalization
P1 = 3 * EPS
print(f"\n  CMB fundamental normalization: P₁ = 3ε = {P1:.6f}")

# ============ 2. Scale Mapping ============
print("\n--- 2. 尺度映射: CMB ℓ → k → 8 h⁻¹ Mpc ---")
# CMB 喺 z* ≈ 1100, ℓ* = log₄(1101) ≈ 5.05
z_star = 1100
ell_star = math.log(1 + z_star, 4)

# D_A(z*) ≈ R_world * (1 - 4^{-ℓ*}) * (1 + 2φ⁻¹ℓ* + δ)
def D_A_idcm(z):
    ell = math.log(1 + z, 4)
    base = R_WORLD * (1 - 4**(-ell))
    proj = 1 + 2 * PHI_INV * ell
    delta = -0.1697 * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

DA_star = D_A_idcm(z_star)
print(f"  z* = {z_star}")
print(f"  ℓ* = log₄(1+z*) = {ell_star:.4f}")
print(f"  D_A(z*) = {DA_star:.0f} Mpc")

# CMB ℓ → k = ℓ/D_A(z*)
for m in range(1, 6):
    if m == 5:
        ell_m = 44 * (33 - F[6]) + F[8]
    else:
        ell_m = 44 * (ND - 1 - (9 - m) * (10 - m) // 2) + (m - 1) * 9 % 25
    k_m = ell_m / DA_star
    print(f"  m={m}: ℓ={ell_m}, k = {k_m:.4f} Mpc⁻¹, λ = {2*math.pi/k_m:.0f} Mpc")

# 8 h⁻¹ Mpc
R_8 = 8.0 / H
k_8 = 2 * math.pi / R_8
print(f"\n  8 h⁻¹ Mpc = {R_8:.2f} Mpc")
print(f"  k₈ = {k_8:.4f} Mpc⁻¹")

# ============ 3. 核心: 用 K_Tree 投影連接 CMB 同 σ₈ ============
print("\n--- 3. K_Tree 投影: CMB 層 → 8 h⁻¹ Mpc ---")
# IDCM 框架: 宇宙係 K_Tree 層級結構
# 每層 ℓ 對應一個尺度 factor 4^ℓ
# CMB 生於 ℓ* ≈ 5.05
# 8 h⁻¹ Mpc 對應 ℓ₈ = log₄(R_world/(8/h)) = 4.27

# 但 CMB 同 8 h⁻¹ Mpc 喺唔同 z!
# CMB: z* = 1100, ℓ* = 5.05
# 8 h⁻¹ Mpc: z = 0, ℓ₈ = 0 (local)

# 兩者之間嘅 K_Tree 層數差異: Δℓ = ℓ* - 0 = 5.05
# 每層嘅 amplitude growth = φ (因為 K_Tree 效率 φ⁻¹ 其實係從高層投影到低層)

# 但方向: 從 CMB 到而家係向下投影 (從高 ℓ 到低 ℓ)
# CMB 喺 ℓ* ≈ 5.05, 而家喺 ℓ = 0
# 向下投影 (更高層到更低層): amplitude ∝ φ^{Δℓ}
# 所以: A(z=0) = A(z*) × φ^{ℓ*}

# P_m = CMB peak power at layer m (in K_Tree layer counting)
# 但呢個 m 係 CMB 峰嘅 K_Tree 層, 唔係 z-redshift ℓ

# 重新思考: CMB 峰 m=2 對應 ℓ ≈ 527
# 呢個 ℓ 係 angular scale, 唔係 K_Tree layer
# k = ℓ/D_A(z*) ≈ 527/2065 ≈ 0.255 Mpc⁻¹

# 8 h⁻¹ Mpc: k₈ = 0.57 Mpc⁻¹
# 兩者都係喺同一個 z (z=0) 嘅物理尺度
# 但在 CMB (z* ≈ 1100), 同樣嘅物理尺度 k 對應唔同嘅 ℓ

# 簡化: 假設 power spectrum 形狀由 K_Tree 層 m 決定
# 層 m 對應嘅物理尺度: λ_m = R_world/4^m (K_Tree 每層尺度縮細 B=4 倍)
# 層 m 對應嘅 k: k_m = 2π×4^m/R_world

# 對於 CMB 峰 m=2: k_CMB ≈ 0.255 Mpc⁻¹
# 對應 K_Tree 層: m_cmb = log₄(k_CMB × R_world/2π) = log₄(0.255×4129.94/2π) = log₄(167.6) = 3.67

# 對於 8 h⁻¹ Mpc: k₈ = 0.57 Mpc⁻¹
# 對應 K_Tree 層: m_8 = log₄(0.57×4129.94/2π) = log₄(374.8) = 4.28

# 層數差異: Δm = m_8 - m_cmb = 4.28 - 3.67 = 0.61
# 每層 power ratio: φ^{-2} (因為 CMB 振幅公式 P_m ∝ φ^{-2(m-1)})
# 所以 power ratio between m_8 and m_cmb: φ^{-2×0.61} = φ^{-1.22}

k_cmb_m2 = 527 / DA_star  # 0.255 Mpc⁻¹
m_cmb = math.log(k_cmb_m2 * R_WORLD / (2 * math.pi), 4)
m_8 = math.log(k_8 * R_WORLD / (2 * math.pi), 4)
dm = m_8 - m_cmb
power_ratio = PHI_INV ** (2 * dm)

print(f"  CMB 峰 m=2: k = {k_cmb_m2:.4f} Mpc⁻¹")
print(f"  對應 K_Tree 層 m = {m_cmb:.4f}")
print(f"  8 h⁻¹ Mpc: k = {k_8:.4f} Mpc⁻¹")
print(f"  對應 K_Tree 層 m = {m_8:.4f}")
print(f"  Δm = {dm:.4f}")
print(f"  Power ratio P(k₈)/P(k_cmb) = φ^(-2Δm) = {power_ratio:.4f}")

# ============ 4. σ₈ 計算 ============
print("\n--- 4. σ₈ 計算 ---")
# P₂ = 3ε × F₂ × φ⁻² = 0.177 係 CMB 峰 m=2 嘅振幅
# 呢個係 CMB 溫度功率譜嘅振幅, 唔係物質功率譜
# 需要用 Sachs-Wolfe 關係轉換

# 從 CMB 溫度到物質功率譜嘅轉換:
# 在 ΛCDM: ΔT/T = (1/3) × δ_m (large scales, SW plateau)
# Δ²_matter ≈ (3ΔT/T)² = 9 × P_m

# 但 P_m 係相對值 (CMB 峰比), 唔係絕對值
# 所以需要 CMB 溫度歸一化

# Planck D₁ = 5816 μK² (binned, peak 1)
# T_CMB = 2.725 K = 2.725e6 μK
# CMB 峰 m=2 嘅絕對功率: D₂ = D₁ × P₂/P₁

D1 = 5816  # μK², Planck binned peak 1
P1_abs = 3 * EPS  # 0.4635
P2_rel = 3 * EPS * 1 * PHI_INV ** 2  # 0.177
D2 = D1 * P2_rel / P1_abs  # μK²
print(f"  Planck D₁ = {D1:.0f} μK² (ℓ≈221)")
print(f"  P₂/P₁ = {P2_rel/P1_abs:.4f}")
print(f"  D₂ = D₁ × P₂/P₁ = {D2:.0f} μK² (ℓ≈527)")

# CMB 溫度波動
T_cmb = 2.725e6  # μK
ell_2 = 527
deltaT_2 = math.sqrt(D2 * 2 * math.pi / (ell_2 * (ell_2 + 1)))  # μK
deltaT_T = deltaT_2 / T_cmb
print(f"  ΔT(ℓ=527) = {deltaT_2:.2f} μK")
print(f"  ΔT/T = {deltaT_T:.2e}")

# Sachs-Wolfe: δ_m ≈ 3 × ΔT/T (large scales)
# 但 k ≈ 0.255 Mpc⁻¹ 係 sub-horizon, 需要 transfer function
# IDCM: growth factor from CMB to today
# growth = φ^{ℓ*} = φ^{5.05} ≈ 11.1 (amplitude)

growth_amp = PHI ** ell_star
print(f"  Growth factor (CMB→today): φ^{ell_star:.2f} = {growth_amp:.2f}")

# Matter power spectrum at z=0 at k ≈ 0.255 Mpc⁻¹
# δ_m(0) ≈ 3 × ΔT/T × φ^{ℓ*} (SW + growth)
# Δ²_matter ≈ δ_m²

delta_m_z0 = 3 * deltaT_T * growth_amp
delta2_m_z0 = delta_m_z0 ** 2
print(f"  δ_m(z=0, k≈0.255) ≈ 3 × ΔT/T × φ^{ell_star:.2f}")
print(f"    = 3 × {deltaT_T:.2e} × {growth_amp:.2f} = {delta_m_z0:.4f}")
print(f"  Δ²_matter(k≈0.255) ≈ {delta2_m_z0:.4f}")

# 投影到 k₈ = 0.57 Mpc⁻¹
delta2_m_k8 = delta2_m_z0 * power_ratio
print(f"  Δ²_matter(k₈) = Δ²_matter(k_cmb) × φ^(-2Δm)")
print(f"    = {delta2_m_z0:.4f} × {power_ratio:.4f} = {delta2_m_k8:.4f}")

# σ₈² ≈ Δ²(k₈) × (window integral)
# Top-hat window integral: ∫ dk/k |W₈(k)|² ≈ 0.7 (for ΛCDM-like spectrum)
# But for IDCM, the window integral depends on the power spectrum shape
# For a power-law spectrum Δ²(k) ∝ k^{n} with n ≈ -2.5 at k ≈ 0.5:
# σ₈² ≈ Δ²(k₈) × I_win, where I_win ≈ 0.5-0.7

I_win = 0.6  # rough estimate
sigma8_sq = delta2_m_k8 * I_win
sigma8 = math.sqrt(sigma8_sq)
print(f"\n  σ₈² ≈ Δ²(k₈) × I_win ≈ {delta2_m_k8:.4f} × {I_win:.1f} = {sigma8_sq:.4f}")
print(f"  σ₈ ≈ {sigma8:.4f}")

# S8
S8_pred = sigma8 * math.sqrt(OM_M / 0.3)
print(f"  S8 = σ₈ × √(Ωₘ/0.3) = {sigma8:.4f} × {math.sqrt(OM_M/0.3):.4f} = {S8_pred:.4f}")

# ============ 5. 與觀測比較 ============
print(f"\n--- 5. 與觀測比較 ---")
obs = [
    ("Planck 2018", 0.834, 0.016),
    ("KiDS-1000", 0.759, 0.017),
    ("DES Y3", 0.776, 0.017),
    ("ACT DR6", 0.788, 0.010),
    ("IDCM", S8_pred, 0),
]
for name, s8, err in obs:
    if name == "IDCM":
        print(f"  {name:<20} {s8:8.4f}")
    else:
        dev = (S8_pred - s8) / err
        status = "✅" if abs(dev) < 1 else "🟡" if abs(dev) < 2 else "❌" if abs(dev) < 3 else "🔴"
        print(f"  {name:<20} {s8:8.4f} ±{err:.3f}  {dev:+6.2f}σ  {status}")

# 張力分析
wl_avg = (0.759 + 0.776 + 0.788) / 3
wl_err = 0.017
print(f"\n  弱透鏡平均 S8 = {wl_avg:.3f} ± {wl_err:.3f}")
print(f"  ΛCDM 張力: Planck vs WL → {(0.834 - wl_avg)/0.016:.2f}σ")
print(f"  IDCM vs Planck:  {(S8_pred - 0.834)/0.016:.2f}σ")
print(f"  IDCM vs WL:  {(S8_pred - wl_avg)/wl_err:.2f}σ")

# ============ 6. 參數掃描 ============
print(f"\n--- 6. I_win 敏感度 ---")
for I_test in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
    s_test = math.sqrt(delta2_m_k8 * I_test)
    S8_test = s_test * math.sqrt(OM_M / 0.3)
    print(f"  I_win = {I_test:.1f} → σ₈ = {s_test:.4f}, S8 = {S8_test:.4f}")

print(f"\n{'='*70}")
print(f"  結論: 呢個方法依賴三個未嚴格推導嘅因子:")
print(f"  1. SW 轉換因子 (3 × ΔT/T → δ_m) — 大尺度近似")
print(f"  2. Growth factor φ^{{{ell_star:.2f}}} — 假設 K_Tree 每層 φ 倍增長")
print(f"  3. Top-hat window integral I_win ≈ 0.6 — 粗略估計")
print(f"  → 需要更嚴格嘅推導")
print(f"{'='*70}")