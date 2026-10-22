#!/usr/bin/env python3
"""
IDCM ⁷Li 抑制機制 — 結構推導 (O73 O5-3 判定後重寫)
==============================================
ΛCDM BBN 預測 ⁷Li/H = 4.9×10⁻¹⁰ (η_B=6.1e-10)
觀測 (Spite plateau) = 1.58×10⁻¹⁰
張力 = 3.1×

IDCM 結構思路:
- η_B 已閉合 (O5-3 判定): η_B = 6.2116×10⁻¹⁰ (+1.56% = 2.32σ 預言)
- ⁷Li 產生 = 兩步合成 (³He+⁴He→⁷Be→⁷Li), 係唯一兩步輕元素
- 結構抑制因子: 2ε×(1-ε) = φ⁻¹/2 × (1-φ⁻¹/4)
  - 2ε: 管道比例 (ε = φ⁻¹/4, 兩步各一步)
  - (1-ε): 非耗散存活比例 (同 τ 公式共享)

推導:
⁷Li/H = η_B × 2ε × (1-ε)

★ 2026-10-09: η_B 由 6.0622e-10 → 6.2116e-10 (O5-3 判定)。
  ⁷Li/H = 1.6229e-10 (+2.72% = 0.14σ) — 仍閉合 (觀測誤差 ±0.31e-10 大)。
"""
import math

phi = (1 + 5**0.5) / 2
phi_inv = 1 / phi
eps = phi_inv / 4
kappa = 1 / 16

# 已閉合值 (O73 O5-3 判定 2026-09-23)
eta_B = 6.2116e-10

# 觀測
Li7_obs = 1.58e-10          # Spite plateau (Sbordone+2010)
Li7_lcdm = 4.9e-10          # ΛCDM BBN 預測 (η_B=6.1e-10)
D_H_obs = 2.527e-5

print("=" * 72)
print("IDCM ⁷Li 抑制機制 — 結構推導 (O5-3 判定後)")
print("=" * 72)

print("\n[1] 問題重述")
print("-" * 72)
print(f"ΛCDM BBN 預測: ⁷Li/H = {Li7_lcdm:.2e}")
print(f"觀測 (Spite):  ⁷Li/H = {Li7_obs:.2e}")
print(f"ΛCDM 張力 = {Li7_lcdm/Li7_obs:.1f}×")
print()

print("[2] IDCM 結構推導")
print("-" * 72)
# ⁷Li/H = η_B × 2ε × (1-ε)
# 結構元素:
#   η_B   = 重子-光子比 (O5-3: 6.2116e-10, +1.56% 預言)
#   2ε    = φ⁻¹/2 (管道比例, ⁷Li 兩步合成)
#   (1-ε) = 非耗散存活 (同 τ = κ(1-ε)(1+ε²) 共享)
factor = 2 * eps * (1 - eps)
Li7_pred = eta_B * factor

print(f"η_B     = {eta_B:.4e}  (O5-3 判定, +1.56% = 2.32σ)")
print(f"ε       = φ⁻¹/4 = {eps:.6f}")
print(f"2ε      = φ⁻¹/2 = {2*eps:.6f}")
print(f"1-ε     = {1-eps:.6f}")
print(f"2ε×(1-ε) = {factor:.6f}")
print()
print(f"⁷Li/H_pred = η_B × 2ε × (1-ε)")
print(f"           = {eta_B:.4e} × {factor:.6f}")
print(f"           = {Li7_pred:.4e}")
print(f"⁷Li/H_obs  = {Li7_obs:.4e}  (±{0.31e-10:.2e})")
print(f"偏差 = {abs(Li7_pred-Li7_obs)/Li7_obs*100:.2f}% = {abs(Li7_pred-Li7_obs)/0.31e-10:.2f}σ")
print(f"對比 ΛCDM: 3.1× 張力 → IDCM 閉合 (0.14σ)")
print()

print("[3] 抑制因子交叉驗證")
print("-" * 72)
supp = Li7_obs / Li7_lcdm
print(f"觀測抑制比 = {Li7_obs:.2e}/{Li7_lcdm:.2e} = {supp:.4f}")
print(f"結構因子 2ε(1-ε) = {factor:.4f}")
print(f"偏差 = {abs(supp-factor)/supp*100:.2f}%")
print()

print("[4] 結構一致性 (同已閉合公式)")
print("-" * 72)
# τ = κ(1-ε)(1+ε²) — 共用 (1-ε)
tau = kappa * (1-eps) * (1+eps**2)
print(f"τ 公式共用 (1-ε): τ = κ(1-ε)(1+ε²) = {tau:.6f} (已閉合 0.19%)")
print(f"⁷Li 公式共用 (1-ε): ⁷Li/H = η_B×2ε×(1-ε)")
print()
print(f"結構元素譜系:")
print(f"  0,1 → x²+x-1=0 → φ = {phi:.6f}")
print(f"  φ → ε = φ⁻¹/4 = {eps:.6f} (管道比例)")
print(f"  φ → κ = 1/16 = {kappa:.6f} (四階耦合)")
print(f"  ε → 2ε = φ⁻¹/2 (⁷Li 兩步管道)")
print(f"  ε → 1-ε = {1-eps:.6f} (非耗散存活)")
print()

print("[5] 可證偽預言")
print("-" * 72)
print(f"P1: ⁷Li/H(primordial) = {Li7_pred:.3e} ± 結構誤差")
print("    (如果未來量度偏離 > 3% → 結構因子失敗)")
print("P2: ⁷Li 產量同 η_B 線性 (唔係 ΛCDM η_B²)")
print("P3: ⁷Li 冇「恆星耗盡」需求 — Spite plateau 就係 primordial")
print()

print("=" * 72)
print(f"總結: ⁷Li/H = η_B×2ε×(1-ε) = {Li7_pred:.4e}")
print(f"      vs 觀測 {Li7_obs:.4e} → 偏差 {abs(Li7_pred-Li7_obs)/Li7_obs*100:.2f}% = {abs(Li7_pred-Li7_obs)/0.31e-10:.2f}σ ✅")
print(f"      ΛCDM 3.1× 張力 → 零自由參數閉合")
print("=" * 72)