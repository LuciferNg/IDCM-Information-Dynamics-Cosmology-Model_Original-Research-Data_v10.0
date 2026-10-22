#!/usr/bin/env python3
"""
05_power_analysis.py — O30: Null 檢驗嘅統計力 (有說服力嘅 null?)
=================================================================
O30 判 🔴 <2σ — 但「測唔到」要證明係「真係冇」而唔係「測唔出」。
方法: 如果 60 節點真係有 δ μK 嘅系統性偏移, 呢個測試有幾大機會 detect?
  power(δ) = P(|z| > 1.96 | 真實偏移 δ)
用 01 嘅控制組分佈: ctrl_iso std = 5.79 μK (mean-of-60)
  → 每節點等效誤差 σ_eff = 5.79 × √60 ≈ 44.8 μK (即節點間 spread)
  → 可偵測閾值: δ_min (2σ) = 2 × 5.79 = 11.6 μK (60 節點 mean)
  → 微冷 5 μK/節點 → z = 5/5.79 = 0.86σ (測唔出)
  → 微冷 10 μK/節點 → z = 1.73σ (邊緣)
  → 微冷 15 μK/節點 → z = 2.59σ (偵測到)
結論: 呢個測試可排除 >11.6 μK 嘅全節點系統性; <11.6 μK 嘅微冷係測試盲區。
     對比: IDCM 假說預測每節點異常 ~F₅ 幅度 (150 μK) — 遠超閾值, 已被排除。
"""
import numpy as np
from scipy import stats

print("=" * 66)
print("O30-05: Null 檢驗統計力分析")
print("=" * 66)

# 控制組 mean-of-60 std (from 01)
sd_ctrl = 5.79  # μK (各向同性控制, 60 點 mean)
sd_ctrl_hi = 7.80  # μK (高緯 31 點)

print(f"\n控制組 mean-of-60 std = {sd_ctrl:.2f} μK (60節點)")
print(f"控制組 mean-of-31 std = {sd_ctrl_hi:.2f} μK (高緯31節點)")

# 可偵測偏移 (2σ)
d_min_60 = 2 * sd_ctrl
d_min_hi = 2 * sd_ctrl_hi
print(f"\n可偵測閾值 (2σ, 60節點): {d_min_60:.1f} μK 系統性偏移")
print(f"可偵測閾值 (2σ, 高緯31): {d_min_hi:.1f} μK")

# Power curve
print(f"\n{'偏移δ(μK)':>10} {'z (60點)':>10} {'power':>8} {'z (31點)':>10} {'power':>8}")
for delta in [2, 5, 8, 10, 11.6, 15, 20, 30, 50, 100, 150]:
    z60 = delta / sd_ctrl
    z31 = delta / sd_ctrl_hi
    pow60 = 1 - stats.norm.cdf(1.96 - z60) + stats.norm.cdf(-1.96 - z60)
    pow31 = 1 - stats.norm.cdf(1.96 - z31) + stats.norm.cdf(-1.96 - z31)
    print(f"{delta:>10.1f} {z60:>+10.2f} {pow60:>8.3f} {z31:>+10.2f} {pow31:>8.3f}")

# IDCM 假說: 每節點 F₅ 幅度 (150 μK) — 但係 sign 隨機 (冷熱各半) → mean 近 0!
# 關鍵: IDCM 預測唔係「全部同 sign」, 而係 |T| 增大 (冷熱都強)
# → mean 檢驗測唔出「幅度增大但 sign 隨機」嘅效應! 呢個係 01 嘅盲區!
# 真正應該測: mean|T| (冷熱幅度) vs 隨機 mean|T|
print("\n" + "=" * 66)
print("關鍵洞見: mean 檢驗嘅盲區")
print("=" * 66)
print("""
IDCM 假說「全部節點有異常」有兩種可能:
  A. 全部同 sign (全冷或全熱) → mean 檢驗有效 (已排除)
  B. 幅度增大但 sign 隨機 (冷熱各半, 每節點 |T| ↑) → mean ≈ 0, 測唔出!
     IDCM 節點係拓撲縫合點 — 相位 θ_i 隨節點而異 → 期望 sign 混合 (B 型)

→ 需要 mean|T| 檢驗 (幅度檢驗): 60 節點 mean|T| vs 隨機 mean|T|
""")
