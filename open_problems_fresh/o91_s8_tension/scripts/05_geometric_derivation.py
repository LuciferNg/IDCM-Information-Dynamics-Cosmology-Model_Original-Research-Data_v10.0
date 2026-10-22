#!/usr/bin/env python3
"""
O91/05: S8 — 幾何推導 (物質團積速度)
========================================
核心: 物質團積速度 = K_Chain 幾何投影問題
類似 ⁷Li 嘅 2ε synthesis step costing:
  - 每層 K_Tree 投影 = 一步「團積」
  - 每步嘅效率 = φ⁻¹ (K_Tree 投影效率)
  - 8 h⁻¹ Mpc 需要 ℓ = log₄(R_world/(8/h)) 步

σ₈² = (3/R³) ∫₀^R s² ξ(s) (1 - 3s/(2R) + s³/(2R³)) ds
其中 ξ(s) = Σγₙ × (φ⁻¹)^{2ℓ(s)} = 90 × φ^{-2ℓ(s)}
ℓ(s) = log₄(R_world/s)
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
R_WORLD = 4129.94       # Mpc
ND = 44
OMEGA_RING = 72.59      # (km/s)/Mpc → h = 0.7259
C_LIGHT = 299792.458
H = OMEGA_RING / 100
OM_M = 0.3045            # IDCM BBN 閉合

print("=" * 70)
print("  O91/05: S8 — 幾何推導 (物質團積速度)")
print("=" * 70)

# ============ 1. K_Chain 基本量 ============
print("\n--- 1. K_Chain 基本量 ---")
sum_gamma = 90  # Σγ = 90
A0 = math.sqrt(sum_gamma)  # fundamental amplitude
print(f"  Σγ = {sum_gamma}")
print(f"  A₀ = √Σγ = {A0:.4f}")

# ============ 2. 幾何投影 ============
print("\n--- 2. 幾何投影: 團積速度 ---")
# 8 h⁻¹ Mpc
R_8 = 8.0 / H  # Mpc
print(f"  8 h⁻¹ Mpc = {R_8:.4f} Mpc")
print(f"  R_world = {R_WORLD:.2f} Mpc")

# ℓ = log₄(R_world/R)
ell_8 = math.log(R_WORLD / R_8, 4)
print(f"\n  ℓ = log₄(R_world / (8/h)) = log₄({R_WORLD/R_8:.2f}) = {ell_8:.4f}")

# 每層投影效率 φ⁻¹
# 第 ℓ 層嘅 amplitude: A(ℓ) = A₀ × φ^{-ℓ}
# 第 ℓ 層嘅 power: P(ℓ) = A₀² × φ^{-2ℓ} = 90 × φ^{-2ℓ}
A_ell = A0 * PHI_INV ** ell_8
P_ell = A_ell ** 2
print(f"  Amplitude at ℓ = {ell_8:.4f}: A(ℓ) = A₀ × φ⁻^{ell_8:.2f} = {A0:.4f} × {PHI_INV**ell_8:.4f} = {A_ell:.4f}")
print(f"  Power at ℓ = {ell_8:.4f}: P(ℓ) = {P_ell:.4f}")

# 類似 ⁷Li: 每步 synthesis cost = ε
# 呢度: 每步團積 cost = φ⁻¹ (投影效率)
# 總 cost = φ^{-ℓ} (amplitude) 或 φ^{-2ℓ} (power)
print(f"\n  Analogous to ⁷Li 2ε costing:")
print(f"    ⁷Li: 2 steps × ε = 2ε")
print(f"    σ₈: {ell_8:.2f} steps × φ⁻¹ per step = φ⁻^{ell_8:.2f}")

# ============ 3. 相關函數 ξ(s) ============
print("\n--- 3. 相關函數 ξ(s) ---")
# ξ(s) = Σγₙ × (φ⁻¹)^{2ℓ(s)} = 90 × φ^{-2ℓ(s)}
# ℓ(s) = log₄(R_world/s)

def xi_idcm(s):
    """IDCM correlation function at separation s (Mpc)"""
    ell = math.log(R_WORLD / s, 4)
    return sum_gamma * PHI_INV ** (2 * ell)

# 驗證 ξ(s) 喺幾個尺度
for s_test in [0.1, 1, 10, 100, 1000, 4129.94]:
    if s_test > R_WORLD:
        continue
    xi = xi_idcm(s_test)
    print(f"  ξ({s_test:8.2f} Mpc) = {xi:.6f}")

# ============ 4. σ₈ 積分 ============
print("\n--- 4. σ₈ 積分 ---")
# σ₈² = (3/R³) ∫₀^R s² ξ(s) W_TH(s) ds
# W_TH(s) = 1 - 3s/(2R) + s³/(2R³)

def sigma8_sq_idcm(R):
    """Compute σ₈² for top-hat radius R"""
    n = 10000
    ds = R / n
    integral = 0.0
    for i in range(n):
        s = (i + 0.5) * ds  # midpoint
        xi = xi_idcm(s)
        W = 1 - 1.5 * s / R + 0.5 * (s / R) ** 3
        integral += s ** 2 * xi * W
    sigma2 = (3.0 / R ** 3) * integral * ds
    return sigma2

sigma2 = sigma8_sq_idcm(R_8)
sigma8 = math.sqrt(sigma2)
print(f"  R = {R_8:.4f} Mpc")
print(f"  σ₈² = {sigma2:.6f}")
print(f"  σ₈ = {sigma8:.4f}")

# S8
S8_pred = sigma8 * math.sqrt(OM_M / 0.3)
print(f"  S8 = σ₈ × √(Ωₘ/0.3) = {sigma8:.4f} × {math.sqrt(OM_M/0.3):.4f} = {S8_pred:.4f}")

# ============ 5. 與觀測比較 ============
print(f"\n--- 5. 與觀測比較 ---")
obs = [
    ("Planck 2018", 0.834, 0.016, "CMB"),
    ("KiDS-1000", 0.759, 0.017, "WL"),
    ("DES Y3", 0.776, 0.017, "WL"),
    ("ACT DR6", 0.788, 0.010, "WL"),
    ("IDCM 幾何", S8_pred, 0, "geom"),
]
print(f"  {'Survey':<20} {'S8':>8} {'σ':>6} {'dev(Planck)':>12} {'dev(WL avg)':>12} {'type':>6}")
wl_avg = (0.759 + 0.776 + 0.788) / 3
wl_err = 0.017
for name, s8, err, typ in obs:
    if typ == "geom":
        print(f"  {name:<20} {s8:8.4f}")
    else:
        dev_p = (s8 - 0.834) / 0.016
        dev_wl = (s8 - wl_avg) / wl_err
        print(f"  {name:<20} {s8:8.4f} ±{err:.3f}  {dev_p:+10.2f}σ  {dev_wl:+10.2f}σ  {typ:>6}")

# IDCM vs 觀測
dev_p = (S8_pred - 0.834) / 0.016
dev_wl = (S8_pred - wl_avg) / wl_err
print(f"  {'-'*40}")
print(f"  IDCM vs Planck:  {dev_p:+4.2f}σ")
print(f"  IDCM vs WL avg:  {dev_wl:+4.2f}σ")

# ============ 6. S8 張力分析 ============
print(f"\n--- 6. S8 張力分析 ---")
print(f"  ΛCDM 張力: Planck vs WL = {(0.834 - wl_avg)/0.016:.2f}σ")
if abs(dev_wl) < 1:
    print(f"  ✅ IDCM 自然解決 S8 張力: 預測同弱透鏡一致 (<1σ)")
elif abs(dev_wl) < 2:
    print(f"  🟡 IDCM 減弱 S8 張力: 預測同弱透鏡偏差 {abs(dev_wl):.1f}σ")
else:
    print(f"  ❌ IDCM 未解決 S8 張力: 預測同弱透鏡偏差 {abs(dev_wl):.1f}σ")

# ============ 7. 參數掃描 ============
print(f"\n--- 7. 幾何參數掃描 ---")
# 唔同 R 值嘅 σ₈
for h_test in [0.67, 0.70, 0.7259, 0.74]:
    R_test = 8.0 / h_test
    s2 = sigma8_sq_idcm(R_test)
    s8 = math.sqrt(s2)
    S8_t = s8 * math.sqrt(OM_M / 0.3)
    print(f"  h = {h_test:.4f}, R = {R_test:.2f} Mpc: σ₈ = {s8:.4f}, S8 = {S8_t:.4f}")

# ============ 8. 同 ΛCDM 相關函數比較 ============
print(f"\n--- 8. IDCM vs ΛCDM 相關函數比較 ---")
# ΛCDM 相關函數 (近似)
def xi_lcdm(s):
    """ΛCDM correlation function (approximate, from Eisenstein-Hu)"""
    # 簡單近似: ξ(s) ≈ σ₈² × (s/8h⁻¹Mpc)^{-γ} × (3/8)^{-1}
    # 其中 γ ≈ 1.8, σ₈ ≈ 0.81
    gamma = 1.8
    s0 = 8.0 / 0.7259  # 8 h⁻¹ Mpc in Mpc
    xi0 = 0.81**2 / (3/8)  # ξ(8 h⁻¹) that gives σ₈=0.81
    return xi0 * (s / s0) ** (-gamma)

for s_test in [0.1, 1, 10, 100]:
    xi_i = xi_idcm(s_test)
    xi_l = xi_lcdm(s_test)
    print(f"  s = {s_test:8.2f} Mpc: ξ_IDCM = {xi_i:.4f}, ξ_ΛCDM = {xi_l:.4f}, ratio = {xi_i/xi_l:.4f}")

print(f"\n{'='*70}")
print(f"  結果: IDCM 幾何推導 σ₈ = {sigma8:.4f}")
print(f"  S8 = {S8_pred:.4f}")
print(f"  弱透鏡平均 S8 = {wl_avg:.3f}")
print(f"  {'✅ 張力解決!' if abs(dev_wl) < 1.5 else '🟡 接近但未完全閉合'}")
print(f"{'='*70}")