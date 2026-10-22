#!/usr/bin/env python3
"""
O11 Maser H₀ — 統計顯著性分析
==============================
問題: 73.9 ± 3.0 (MCP XIII) 嘅 +1.80% 偏移, 喺 1σ = ±4.13% 誤差內
      → 偏移本身可能只係統計漲落, 唔係結構效應

要回答:
1. 73.9 vs 72.59 差異顯著嗎? (z-score)
2. 如果 MCP 2025 profile likelihood 73.5 係「最新」, 偏移得 1.25%
3. 結構公式鎖定需要幾大統計量?
4. 決定: 鎖定公式 vs 🟡 記錄為統計上未分辨

鐵律: 誠實 — 如果 1.80% 冇結構組合 → 🟡 記錄
      禁止數字遊戲 — 唔好為咗 fit 1.80% 而作公式
"""
import math

phi = (1 + 5**0.5) / 2
phi_inv = 1 / phi
kappa = 1 / 16

H0_idcm = 72.59
H0_maser = 73.9
err_maser = 3.0
H0_maser_pl = 73.5  # profile likelihood 2025

print("=" * 70)
print("O11 Maser H₀ — 統計顯著性")
print("=" * 70)

# ---- 1. z-score ----
print("\n[1] 偏移顯著性")
for name, h, err in [("MCP XIII (Bayesian)", H0_maser, err_maser),
                     ("MCP 2025 (Profile)", H0_maser_pl, err_maser)]:
    z = (h - H0_idcm) / err
    print(f"  {name}: {h} ± {err} vs {H0_idcm}")
    print(f"    z = ({h}-{H0_idcm})/{err} = {z:.2f}σ  "
          f"{'✅ 唔顯著 (<2σ)' if abs(z)<2 else '🟡 邊緣' if abs(z)<3 else '🔴 顯著'}")
    print(f"    offset = {(h/H0_idcm-1)*100:.3f}% (誤差 {err/H0_idcm*100:.2f}%)")

# ---- 2. 誤差來源: 系統誤差主導? ----
print("\n[2] MCP 誤差結構")
print("  MCP XIII 73.9 ± 3.0: 統計 (maser 幾何) + 系統 (peculiar velocity)")
print("  250 km/s peculiar velocity 不確定度 → ΔH₀ ~ 250/7000 ~ 3.6%")
print("  → 主導誤差係 peculiar velocity, 唔係 maser 幾何本身")
print(f"  幾何距離誤差 (NGC 4258): ~3% → 對 H₀ 影響 ~{3.0/73.9*100:.1f}%")

# ---- 3. 用 6 個星系獨立測量 ----
print("\n[3] 每個星系嘅 H₀ 貢獻")
# MCP XIII: 6 個星系 (UGC3789, NGC6264, NGC6323, NGC5765b, CGCG074-064, NGC4258)
# 各有幾何距離誤差: 3-5% 不等, 加埋 peculiar velocity 250 km/s
print("  6 星系: UGC3789, NGC6264, NGC6323, NGC5765b, CGCG074-064, NGC4258")
print("  每個距離誤差 3-5% → H₀ 組合誤差 ±3.0")
print("  任何單一星系嘅偏移都有 ±8-12% 誤差 → 無法分辨 1.8% 結構偏移")

# ---- 4. 結構預測 vs 統計分辨力 ----
print("\n[4] 結構預測嘅可分辨性")
preds = {
    "H₀_idcm (結構)": 72.59,
    "Maser 幾何全深度?": 72.59 * (1 + kappa * phi_inv / 2),  # κφ⁻¹/2 候選
    "MCP XIII 觀測": 73.9,
}
for name, h in preds.items():
    print(f"  {name}: {h:.2f} (offset {(h/H0_idcm-1)*100:+.3f}%)")

print(f"\n  結構候選 κφ⁻¹/2 = {kappa*phi_inv/2*100:.4f}% → H₀ = {72.59*(1+kappa*phi_inv/2):.2f}")
print(f"  vs 觀測 73.9 ± 3.0 → z = {(73.9-72.59*(1+kappa*phi_inv/2))/3.0:.2f}σ")
print(f"  → 喺誤差內, 無法分辨 κφ⁻¹/2 (1.93%) vs 純幾何 (0%) vs 觀測 1.80%")

# ---- 5. 決定 ----
print("\n[5] 判定")
print("  Maser offset +1.80% 嘅 1σ 誤差 = ±4.13%")
print("  → 偏移本身 z ≈ 0.44σ (73.9 vs 72.59)")
print("  → 統計上唔顯著!")
print("  → 唔應該鎖定任何公式 (會係數字遊戲)")

# ---- 6. 但係: 如果偏移係真, 邊個結構最合理? ----
print("\n[6] 如果偏移係真 (假設性結構分析)")
print("  Maser 方法 = 純幾何 (angular diameter distance, 冇距離階梯)")
print("  → 唔似 TRGB/Miras 嘅恆星投影層")
print("  → IDCM 結構: 幾何距離 = D_app(ℓ) 直接量度?")
print("  D_app(ℓ=0) = (44-44/4^0)(R_H/44)(1+0) = 0 (近距離)")
print("  H_eff(z→0) = c / dD_app/dz |_{z=0}")
print("  → H_eff(0) 應該 = H₀_idcm = 72.59 如果 D_app 正確")
print("  → 但 MCP 量度嘅係 H₀ 喺 z~0.01-0.04 (6 個星系)")
print("  → 如果 D_app 有非線性, H_eff 喺 z~0.02 可能偏移")

# D_app derivative at low z
import numpy as np

def D_app(z):
    ell = math.log(1 + z, 4)
    return (44 - 44 / 4**ell) * (4129.94 / 44) * (1 + 2 * phi_inv * ell)

def H_eff(z, dz=1e-5):
    return 299792.458 / ((D_app(z + dz) - D_app(z - dz)) / (2 * dz))

print("\n  IDCM H_eff(z) 低紅移:")
for z in [0.0, 0.005, 0.01, 0.02, 0.03, 0.04]:
    print(f"    z={z:.3f}: H_eff = {H_eff(z):.2f} (offset {(H_eff(z)/72.59-1)*100:+.3f}%)")

# 搵 z 令 H_eff(z) = 73.9
target = 73.9
z_lo, z_hi = 0.0, 0.05
for _ in range(60):
    zm = (z_lo + z_hi) / 2
    if H_eff(zm) > target:
        z_hi = zm
    else:
        z_lo = zm
print(f"\n  H_eff(z) = 73.9 喺 z ≈ {(z_lo+z_hi)/2:.4f}")
print(f"  MCP 星系 z 範圍: NGC4258 z=0.0015, UGC3789 z=0.0116, NGC6264 z=0.0300")
print(f"  → 唔同星系唔同 z → H_eff(z) 唔同 → 組合平均")

print("\n" + "=" * 70)
print("初步結論: 統計上未分辨 → 需要更深入分析")
print("=" * 70)
