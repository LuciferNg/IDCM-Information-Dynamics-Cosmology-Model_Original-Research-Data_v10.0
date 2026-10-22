#!/usr/bin/env python3
"""
O91/01: S8 張力 — 核心結構推導
================================
從 K_Chain + K_Tree 推導 σ₈ 歸一化，比較 Planck CMB vs 弱透鏡 S8。

IDCM 框架:
  - 冇膨脹 (PARADIGM BREAK) → 結構增長唔係 ΛCDM 嘅 D(z)
  - K_Chain 44 模式: γₙ = 4sin²(nπ/88), Aₙ = 2sin(nπ/88)
  - K_Tree B=4: 每層投影效率 φ⁻¹ (O76)
  - CMB 峰振幅: P_m = 3ε × F_m × φ^(-2(m-1)) (O10 閉合)
  - z 紅移 = 投影效應, ℓ = log₄(1+z) (O76 閉合)
  - 世界環: R_world = 4129.94 Mpc

S8 = σ₈ √(Ωₘ/0.3)
  σ₈² = ∫ dk/k · Δ²(k) · |W₈(k)|², W₈(k) = 3j₁(kR)/(kR)
  R = 8 h⁻¹ Mpc

問題:
  1. Planck 2018 σ₈ = 0.811 ± 0.006 → S8 = 0.834 ± 0.016
  2. KiDS-1000 S8 = 0.759 ± 0.017 (2.9σ)
  3. DES Y3 S8 = 0.776 ± 0.017 (2.3σ)
  4. ACT DR6 S8 = 0.788 ± 0.010 (2.0σ)
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

# ============ 結構常數 ============
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
EPS = PHI_INV / 4      # ε = φ⁻¹/4
R_WORLD = 4129.94       # Mpc
ND = 44                 # 44-site K_Chain
B = 4                   # K_Tree branching
OMEGA_RING = 72.59      # (km/s)/Mpc (O73)
C_LIGHT = 299792.458    # km/s
H = OMEGA_RING / 100    # h = 0.7259 (for 8 h⁻¹ Mpc)

# 導出量
SITE_SPACING = R_WORLD / ND  # 46.93 Mpc
R_8 = 8.0 / H                 # 8 h⁻¹ Mpc in Mpc
LN4 = math.log(4)

print("=" * 70)
print("  O91/01: S8 張力 — 核心結構推導")
print("=" * 70)

# ============ 1. 基本常數驗證 ============
print("\n--- 1. 基本常數 ---")
print(f"  φ = {PHI:.10f}")
print(f"  ε = φ⁻¹/4 = {EPS:.10f}")
print(f"  R_world = {R_WORLD:.2f} Mpc")
print(f"  ω_ring = {OMEGA_RING:.4f} (km/s)/Mpc  →  h = {H:.4f}")
print(f"  Δs (site spacing) = {SITE_SPACING:.4f} Mpc")
print(f"  8 h⁻¹ Mpc = {R_8:.4f} Mpc")
check("R_world/c = ω_ring", abs(C_LIGHT / R_WORLD - OMEGA_RING) < 0.01,
      f"{C_LIGHT/R_WORLD:.4f} vs {OMEGA_RING:.4f}")

# ============ 2. K_Chain 模式振幅 ============
print("\n--- 2. K_Chain 模式振幅 ---")
modes = []
for n in range(1, ND + 1):
    gamma = 4 * math.sin(math.pi * n / 88) ** 2
    amp = 2 * abs(math.sin(math.pi * n / 88))
    modes.append({"n": n, "gamma": gamma, "amp": amp})

sum_gamma = sum(m["gamma"] for m in modes)
sum_amp2 = sum(m["amp"]**2 for m in modes)
print(f"  Σγₙ (n=1..44) = {sum_gamma:.10f}  (應 = 90)")
check("Σγ = 90", abs(sum_gamma - 90) < 1e-9)
check("ΣA² = 90", abs(sum_amp2 - 90) < 1e-9)

# ============ 3. CMB 峰振幅對照 (O10) ============
print("\n--- 3. CMB 峰振幅結構 (O10) ---")
# P_m = 3ε × F_m × φ^(-2(m-1))
F = [1, 1, 2, 3, 5, 8, 13, 21, 34]  # Fibonacci
for m in range(1, 6):
    P_m = 3 * EPS * F[m] * PHI_INV ** (2 * (m - 1))
    print(f"  m={m}: P_m = 3ε·F_{m}·φ⁻²⁽ᵐ⁻¹⁾ = {P_m:.6f}")

# 3ε 係 CMB 第一峰歸一化
P1 = 3 * EPS * F[1] * PHI_INV ** 0  # = 3ε
print(f"\n  P₁ = 3ε = {P1:.6f}  (CMB fundamental normalization)")
print(f"  Planck 2018 TT peak 1 (binned, 10⁻⁶): D₁ ≈ 5816")
print(f"  → 3ε = {P1:.6f} 對應 CMB 功率譜歸一化水平")

# ============ 4. Scale Mapping: 8 h⁻¹ Mpc → K_Tree layer ============
print("\n--- 4. 尺度映射: 8 h⁻¹ Mpc → K_Tree layer ℓ ---")
# 8 h⁻¹ Mpc = 11.02 Mpc
# K_Tree: 每層 ℓ 對應尺度 R_world/4^ℓ
# ℓ = log₄(R_world / s)

ell_8 = math.log(R_WORLD / R_8, 4)
print(f"  R_world = {R_WORLD:.2f} Mpc")
print(f"  8 h⁻¹ Mpc = {R_8:.4f} Mpc")
print(f"  ℓ₈ = log₄(R_world / (8/h)) = {ell_8:.4f}")

# 最近整數層
ell_floor = int(math.floor(ell_8))
ell_ceil = ell_floor + 1
print(f"  最近 K_Tree 層: ℓ={ell_floor} (scale={R_WORLD/4**ell_floor:.1f} Mpc)")
print(f"                ℓ={ell_ceil} (scale={R_WORLD/4**ell_ceil:.1f} Mpc)")

# ============ 5. K_Chain 模式在 8 h⁻¹ Mpc 嘅貢獻 ============
print("\n--- 5. K_Chain 模式對 8 h⁻¹ Mpc 嘅貢獻 ---")
# 每個 K_Chain 模式 n 有波長 λₙ = R_world/n
# 喺尺度 s = 8 h⁻¹ Mpc 嘅貢獻係: γₙ · j₀(πns/R_world) · (φ⁻¹)^{ℓ(s)}
# 其中 j₀(x) = sin(x)/x 係球 Bessel 零階

# 但 j₀ 嘅零點會導致干涉相消。
# 關鍵: 8 h⁻¹ Mpc 遠細過 K_Chain 最小波長 (93.86 Mpc)
# 所以 j₀(πns/R_world) ≈ j₀(0) = 1 對於所有 n
# 振幅主要來自 K_Tree 投影

print(f"  最小 K_Chain 波長 (Nyquist): λ₄₄ = {R_WORLD/44:.2f} Mpc")
print(f"  8 h⁻¹ Mpc = {R_8:.2f} Mpc < λ_min/2 = {R_WORLD/88:.2f} Mpc")
print(f"  → 8 h⁻¹ Mpc 在 K_Chain 次格點尺度 (sub-grid)")
print(f"  → 振幅由 K_Tree 投影決定, 非直接 K_Chain 模式")

# ============ 6. σ₈ 從 K_Chain + K_Tree 投影 ============
print("\n--- 6. σ₈ 從 K_Chain + K_Tree 投影 ---")
# IDCM 框架: 結構增長由 K_Chain 模式振幅通過 K_Tree 投影到不同尺度
# CMB 峰振幅 P_m = 3ε × F_m × φ^(-2(m-1)) 給出喺 K_Tree 層 m 嘅功率
# 同樣邏輯, 喺尺度 s 嘅功率 = 3ε × (φ⁻¹)^{2ℓ(s)} × 尺度權重

# 方法 A: 從 3ε 歸一化直接投影
# 3ε 係 CMB 基礎歸一化, 對應 Σγ = 90 嘅總功率
# 喺 8 h⁻¹ Mpc 嘅功率係 3ε 乘 K_Tree 投影因子

# K_Tree 投影因子: (φ⁻¹)^{2ℓ} 因為每層投影效率 φ⁻¹
# 注意: CMB 峰係 P_m ∝ φ^(-2(m-1)), 即每層 φ⁻²
# 對於 8 h⁻¹ Mpc: ℓ ≈ 4.28 → 投影因子 = φ^(-2ℓ)

proj_factor = PHI_INV ** (2 * ell_8)
print(f"  K_Tree 投影因子 φ^(-2ℓ₈) = {proj_factor:.6f}")

# 尺度權重: 8 h⁻¹ Mpc 對應嘅 K_Chain 模式密度
# 每個模式 n 貢獻 γₙ · j₀²(πn·R_8/R_world)
# 對於小尺度: j₀²(x) ≈ 1 - x²/3 + ...
# 總和 Σ γₙ · j₀²(πn·R_8/R_world) 近似 = Σ γₙ · (1 - (πn·R_8/R_world)²/3)
# = 90 - (π²·R_8²)/(3·R_world²) · Σ γₙ n²

# 計算 Σ γₙ n²
sum_gamma_n2 = sum(m["gamma"] * m["n"]**2 for m in modes)
correction = (math.pi**2 * R_8**2) / (3 * R_WORLD**2) * sum_gamma_n2
print(f"  Σγₙ = {sum_gamma:.6f}")
print(f"  Σγₙ·n² = {sum_gamma_n2:.6f}")
print(f"  j₀² 修正項 = {correction:.6f}")

# 有效功率
eff_power = sum_gamma - correction
print(f"  有效功率 P_eff = Σγₙ·j₀²(πn·R₈/R_world) ≈ {eff_power:.6f}")
print(f"  相對總功率: {eff_power/sum_gamma:.4f}")

# σ₈² = 3ε × (φ⁻¹)^{2ℓ₈} × (P_eff/90)
# 3ε 係 CMB 歸一化 (對應 Σγ=90 總功率)
# (φ⁻¹)^{2ℓ₈} 係 K_Tree 投影到 8 h⁻¹ Mpc 尺度
# P_eff/90 係模式採樣修正

sigma8_sq = P1 * proj_factor * (eff_power / sum_gamma)
sigma8 = math.sqrt(sigma8_sq)
print(f"\n  σ₈² = 3ε × φ^(-2ℓ₈) × (P_eff/90)")
print(f"      = {P1:.6f} × {proj_factor:.6f} × {eff_power/sum_gamma:.6f}")
print(f"      = {sigma8_sq:.6f}")
print(f"  σ₈ = {sigma8:.4f}")

# ============ 7. 與觀測比較 ============
print("\n--- 7. 與觀測比較 ---")
# S8 = σ₈ √(Ωₘ/0.3)
OM_M = 0.3045  # IDCM BBN 閉合 (Ω_b/Ω_m = 2/15)
S8_pred = sigma8 * math.sqrt(OM_M / 0.3)
print(f"  Ωₘ (IDCM) = {OM_M:.4f}")
print(f"  S8 預測 = σ₈ × √(Ωₘ/0.3) = {sigma8:.4f} × {math.sqrt(OM_M/0.3):.4f} = {S8_pred:.4f}")

# 觀測值
obs = [
    ("Planck 2018", 0.834, 0.016),
    ("KiDS-1000", 0.759, 0.017),
    ("DES Y3", 0.776, 0.017),
    ("ACT DR6", 0.788, 0.010),
    ("IDCM (this work)", S8_pred, 0),
]
print(f"\n  {'Survey':<20} {'S8':>8} {'σ':>6} {'dev':>8} {'status':>8}")
for name, s8, err in obs:
    if name == "IDCM (this work)":
        continue
    dev = (s8 - S8_pred) / err
    status = "✅" if abs(dev) < 1 else "🟡" if abs(dev) < 2 else "❌" if abs(dev) < 3 else "🔴"
    print(f"  {name:<20} {s8:8.4f} ±{err:.3f}  {dev:+6.2f}σ  {status:>8}")

print(f"  {'IDCM (this work)':<20} {S8_pred:8.4f}")

# ============ 8. 張力分析 ============
print("\n--- 8. S8 張力分析 ---")
print(f"  IDCM S8 預測 = {S8_pred:.4f}")
print(f"  Planck S8 = 0.834 ± 0.016 → Δ = {(S8_pred - 0.834)/0.016:.2f}σ")
print(f"  KiDS-1000 S8 = 0.759 ± 0.017 → Δ = {(S8_pred - 0.759)/0.017:.2f}σ")
print(f"  DES Y3 S8 = 0.776 ± 0.017 → Δ = {(S8_pred - 0.776)/0.017:.2f}σ")
print(f"  ACT DR6 S8 = 0.788 ± 0.010 → Δ = {(S8_pred - 0.788)/0.010:.2f}σ")

# S8 張力 = Planck vs 弱透鏡平均
wl_avg = (0.759 + 0.776 + 0.788) / 3
wl_err = 0.017  # 保守
print(f"  弱透鏡平均 S8 = {wl_avg:.3f} ± {wl_err:.3f}")
print(f"  Planck vs WL: Δ = {(0.834 - wl_avg)/0.016:.2f}σ (ΛCDM 張力)")
print(f"  IDCM vs WL:  Δ = {(S8_pred - wl_avg)/wl_err:.2f}σ")

# ============ 9. 開放問題 ============
print("\n--- 9. 開放問題 ---")
print("""
  🔴 K_Tree 投影因子 φ^(-2ℓ) 嘅嚴格推導 — 假設咗每層 φ⁻¹ 效率
  🔴 j₀² 修正嘅高階項 — 近似到 O(1/R_world²)
  🔴 K_Chain 模式同 K_Tree 層之間嘅干涉項
  🔴 3ε 歸一化嘅嚴格證明 (對應 Σγ=90)
  🟡 尺度權重: Σγₙ·j₀² 嘅 j₀ 近似
""")

# Summary
print(f"\n{'='*70}")
print(f"  PASS: {PASS}/{PASS+FAIL}")
print(f"  FAIL: {FAIL}/{PASS+FAIL}")
print(f"{'='*70}")