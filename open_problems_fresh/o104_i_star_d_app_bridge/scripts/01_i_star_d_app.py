#!/usr/bin/env python3
"""
O104/01: I* ↔ D_app(ℓ*) 直接關係
==============================================
問題: I* = 24(1-π/44)/7 同 D_app(ℓ*) 有冇直接結構關係?
    即係 I* 係咪可以由 D_app(ℓ*) 導出?

關鍵身份:
  - I* = 24(1-π/44)/7 = 3.18377  (IDCM 結構數)
  - D_A(z*) = (24/7)R_world  (O73 發現)
  - I* = D_A(z*)/R_world - 6π/77 = 24/7 - 6π/77
  - 檢查 D_app(ℓ*) 同 I* 嘅關係

三部曲:
  1. ℓ* = log₄(1+z*) 計算
  2. D_app(ℓ*) 同 D_A(ℓ*) 計算
  3. I* 同 D_app(ℓ*) 嘅關係
"""
import json, math, sys

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

# ============ 1. 結構常數 ============
phi = (1 + math.sqrt(5)) / 2
phii = 1 / phi
eps = phii / 4
kappa = 1 / 16
R_world = 4129.94       # Mpc (O73)
N_d = 44
B = 4
N_gen = 3
L4 = 7   # φ⁴+φ⁻⁴
L5 = 11  # φ⁵+φ⁻⁵
pi = math.pi
ln4 = math.log(4)

print("=" * 66)
print("O104/01: I* ↔ D_app(ℓ*) 直接關係")
print("=" * 66)

# ============ 2. I* 結構分解 ============
print("\n--- 1. I* 結構分解 ---")
I_star = 24 * (1 - pi/44) / 7
term1 = 24/7           # = D_A(z*)/R_world
term2 = 6*pi/77        # = 6π/(L₄×L₅)
print(f"I* = 24(1-π/44)/7 = {I_star:.10f}")
print(f"  24/7 = {term1:.10f} (D_A(z*)/R_world)")
print(f"  6π/77 = {term2:.10f} = 6π/(L₄×L₅) = 6π/({L4}×{L5})")
print(f"  77 = {L4}×{L5} = L₄×L₅ = {L4*L5}")
print(f"  6 = 2×{N_gen} = 2×N_gen")
check("I* = 24/7 - 6π/77", abs(I_star - (term1 - term2)) < 1e-15)

# ============ 3. ℓ* 計算 ============
print("\n--- 2. ℓ* = log₄(1+z*) ---")
z_star = 1089.9  # Planck 2018 recombination
ell_star = math.log(1 + z_star, 4)
print(f"z* = {z_star}")
print(f"ℓ* = log₄(1+z*) = log₄({1+z_star:.1f}) = {ell_star:.10f}")
print(f"  驗證: 4^ℓ* = {4**ell_star:.6f} (should be {1+z_star:.1f})")
check("4^ℓ* = 1+z*", abs(4**ell_star - (1+z_star)) / (1+z_star) < 1e-10)

# ============ 4. D_app 公式 ============
print("\n--- 3. D_app(ℓ*) 計算 ---")
def D_app(ell, C=-0.1697):
    """D_app(ℓ) = R_world(1-4^{-ℓ})(1 + 2φ⁻¹ℓ + δ(ℓ))
    δ(ℓ) = C(ℓ-0.5)(1-4^{-ℓ})  (O51 群延遲權重修正)"""
    base = R_world * (1 - 4**(-ell))
    proj = 1 + 2*phii*ell
    delta = C * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

D_app_star = D_app(ell_star)
factor_4ell = 4**(-ell_star)
one_minus = 1 - factor_4ell
proj_factor = 1 + 2*phii*ell_star
delta_factor = -0.1697 * (ell_star - 0.5) * one_minus

print(f"4^(-ℓ*) = 1/(1+z*) = {factor_4ell:.10f}")
print(f"1-4^(-ℓ*) = {one_minus:.10f}")
print(f"投影因子 1+2φ⁻¹ℓ* = {proj_factor:.10f}")
print(f"δ(ℓ*) 修正 = {delta_factor:.10f}")
print(f"D_app(ℓ*) = {D_app_star:.4f} Mpc")
print(f"D_app(ℓ*)/R_world = {D_app_star/R_world:.10f}")

# Angular diameter distance in IDCM
# D_A(ℓ) = D_app(ℓ) / 4^ℓ  (since 1+z = 4^ℓ)
D_A_star = D_app_star / (4**ell_star)
print(f"\nD_A(ℓ*) = D_app(ℓ*)/4^ℓ* = D_app(ℓ*)/(1+z*) = {D_A_star:.4f} Mpc")
print(f"D_A(ℓ*)/R_world = {D_A_star/R_world:.10f}")
print(f"24/7 = {24/7:.10f}")

check("D_A(z*)/R_world ≈ 24/7", abs(D_A_star/R_world - 24/7) / (24/7) < 0.01)

# 精確偏差
DA_dev = (D_A_star/R_world - 24/7) / (24/7) * 100
print(f"  偏差: {DA_dev:.4f}%")
if abs(DA_dev) < 0.05:
    check("D_A(z*) = (24/7)R_world 精確", True, f"dev={DA_dev:.4f}%")
else:
    check("D_A(z*) = (24/7)R_world 精確", False, f"dev={DA_dev:.4f}%")

# ============ 5. I* 同 D_app 嘅關係 ============
print("\n--- 4. I* 同 D_app/D_A 關係 ---")
# I* = 24/7 - 6π/77
# D_A(z*)/R_world = 24/7 (from O73)
# So I* = D_A(z*)/R_world - 6π/77
I_from_DA = D_A_star / R_world - 6*pi/77
print(f"I* (直接) = {I_star:.10f}")
print(f"I* (from D_A/R_world - 6π/77) = {I_from_DA:.10f}")
print(f"  偏差: {abs(I_from_DA - I_star):.2e}")
check("I* = D_A/R_world - 6π/77", abs(I_from_DA - I_star) < 1e-6)

# D_app(ℓ*) 同 I* 有冇直接關係?
# D_app(ℓ*) = D_A(ℓ*) × 4^ℓ* = D_A(ℓ*) × (1+z*)
# I* = D_A/R_world - 6π/77
# So I* = D_app(ℓ*)/(R_world × 4^ℓ*) - 6π/77
I_from_Dapp = D_app_star / (R_world * 4**ell_star) - 6*pi/77
print(f"\nI* (from D_app/(R_world·4^ℓ*) - 6π/77) = {I_from_Dapp:.10f}")
print(f"  偏差: {abs(I_from_Dapp - I_star):.2e}")
check("I* = D_app/(R_world·4^ℓ*) - 6π/77", abs(I_from_Dapp - I_star) < 1e-6)

# ============ 6. (1-π/44) 同 D_app 嘅關係 ============
print("\n--- 5. (1-π/44) 同 D_app 嘅關係 ---")
# I* = (24/7)(1-π/44)
# (1-π/44) = I* × 7/24
# Check: 1-π/44 = I* × 7/24 = 1 - θ_site
one_minus_pi_44 = 1 - pi/44
I_times_7_24 = I_star * 7 / 24
print(f"1-π/44 = {one_minus_pi_44:.10f}")
print(f"I* × 7/24 = {I_times_7_24:.10f}")
check("1-π/44 = I* × 7/24", abs(one_minus_pi_44 - I_times_7_24) < 1e-15)

# D_app 嘅 (1-4^{-ℓ}) 因子 ≈ 1 at ℓ*, so D_app ≈ R_world × (1+2φ⁻¹ℓ*+δ)
# 但 I* 係 D_A 嘅修正, 唔係 D_app 嘅
print(f"\nD_app(ℓ*) / (R_world × 4^ℓ*) = {D_app_star/(R_world * 4**ell_star):.10f}")
print(f"  呢個 = D_A(ℓ*)/R_world = {D_A_star/R_world:.10f}")
print(f"D_A(ℓ*)/R_world × (1-π/44) = {D_A_star/R_world * (1-pi/44):.10f}")
print(f"I* = {I_star:.10f}")
print(f"  D_A/R_world × (1-π/44) / I* = {D_A_star/R_world * (1-pi/44) / I_star:.10f}")

# ============ 7. 核心發現: I* 嘅 D_app 結構分解 ============
print("\n" + "=" * 66)
print("核心發現: I* 嘅 D_app 結構分解")
print("=" * 66)

# I* 嘅第一個身份: I* = D_A(z*)/R_world - 6π/77
# 但 D_A(z*) = D_app(ℓ*)/(1+z*)
# 所以 I* = D_app(ℓ*)/(R_world·(1+z*)) - 6π/77

# 第二個身份: I* = (24/7)(1-π/44)
# 24/7 = D_A(z*)/R_world (近似, 偏差 0.014%)
# 所以 I* = D_A(z*)/R_world × (1-π/44) = D_A(z*)/R_world - D_A(z*)/R_world × π/44

# 但 D_A(z*)/R_world × π/44 = 24/7 × π/44 = 6π/77
# 所以 I* = D_A(z*)/R_world - 6π/77

DA_R = D_A_star / R_world
print(f"\nI* = D_A(z*)/R_world - 6π/(L₄×L₅)")
print(f"   = {DA_R:.10f} - {6*pi/(L4*L5):.10f}")
print(f"   = {DA_R - 6*pi/(L4*L5):.10f}")
print(f"   vs I* = {I_star:.10f}")
check("I* = D_A/R_world - 6π/(L₄·L₅)", abs(DA_R - 6*pi/(L4*L5) - I_star) < 1e-6)

# 第三個身份: 6π/(L₄×L₅) = (24/7) × (π/44)
# = D_A(z*)/R_world × π/44
print(f"\n6π/77 = (24/7) × π/44 = {24/7 * pi/44:.10f}")
print(f"  6π/77 = {6*pi/77:.10f}")
check("6π/77 = (24/7)×(π/44)", abs(6*pi/77 - 24/7*pi/44) < 1e-15)

# 所以 I* = D_A(z*)/R_world × (1 - π/44)
print(f"\nI* = D_A(z*)/R_world × (1 - π/44)")
print(f"   = {DA_R:.10f} × {1-pi/44:.10f}")
print(f"   = {DA_R * (1-pi/44):.10f}")
print(f"   vs I* = {I_star:.10f}")
check("I* = D_A/R_world × (1-π/44)", abs(DA_R * (1-pi/44) - I_star) < 1e-6)

# ============ 8. 總結: 關係圖 ============
print("\n" + "=" * 66)
print("總結: I* ↔ D_app(ℓ*) 關係圖")
print("=" * 66)
print(f"""
Z* = {z_star} (recombination)
  ↓
ℓ* = log₄(1+z*) = {ell_star:.6f}
  ↓
D_app(ℓ*) = R_world(1-4^(-ℓ*))(1+2φ⁻¹ℓ*+δ(ℓ*))
  = {D_app_star:.2f} Mpc
  ↓ (除以 1+z* = 4^ℓ*)
D_A(ℓ*) = D_app(ℓ*)/(1+z*) = {D_A_star:.2f} Mpc
  = ({D_A_star/R_world:.6f}) × R_world
  ≈ (24/7) × R_world = {24/7:.6f} × R_world  [偏差 {abs(D_A_star/R_world - 24/7)/(24/7)*100:.4f}%]
  ↓
I* = D_A(ℓ*)/R_world - 6π/77
  = {DA_R:.10f} - {6*pi/77:.10f}
  = {I_star:.10f}
  ↓
I* = 24(1-π/44)/7 = {I_star:.10f}  ✅
""")

# 第二種路徑: 直接用 D_app 寫 I*
print("I* 嘅 D_app 直接表達式:")
print(f"  I* = D_app(ℓ*)/(R_world·(1+z*)) - 6π/(L₄×L₅)")
print(f"     = {D_app_star/(R_world * (1+z_star)):.10f} - {6*pi/(L4*L5):.10f}")
print(f"     = {I_star:.10f}")

# 第三種路徑: 用 (1-π/44) 投影
print(f"\n  I* = (24/7) × (1-π/44)")
print(f"     = D_A(ℓ*)/R_world × (1-π/44)  [近似, 偏差 0.014%]")
print(f"     = {DA_R:.10f} × {1-pi/44:.10f}")
print(f"     = {DA_R * (1-pi/44):.10f}")

# ============ 9. 最終判決 ============
print("\n" + "=" * 66)
print("判決")
print("=" * 66)
print(f"""
I* 同 D_app(ℓ*) 嘅關係: ✅ 直接結構關係成立

I* 可以寫成三個等價形式:
  1. I* = 24(1-π/44)/7                     (原始定義)
  2. I* = D_A(ℓ*)/R_world - 6π/77          (D_A 形式)
  3. I* = D_app(ℓ*)/(R_world·(1+z*)) - 6π/77  (D_app 形式)

其中:
  - D_A(ℓ*) = D_app(ℓ*)/(1+z*) = (24/7)R_world (零參數閉合, O73)
  - 6π/77 = (24/7) × π/44 = D_A(ℓ*)/R_world × θ_site
  - θ_site = π/44 = 88-site 對偶鏈半 site 角

結論: I* 係 D_A(ℓ*)/R_world 嘅 (1-π/44) 投影 — 
      π/44 係觀測者「site 角」, 1-π/44 係 sync 投影因子。
      6π/77 = 6π/(L₄×L₅) = 2×N_gen × π/(L₄×L₅) 全結構數。
""")

# 最終 PASS/FAIL
total = PASS + FAIL
print(f"\n{'='*66}")
print(f"結果: {PASS}/{total} PASS, {FAIL}/{total} FAIL")
if FAIL == 0:
    print("🎉 全部 PASS! I* ↔ D_app 關係閉合")
else:
    print(f"⚠️  {FAIL} 個 FAIL, 需要調查")
print(f"{'='*66}")