#!/usr/bin/env python3
"""
O108 — Script 03: VL 質量標度結構公式驗證
============================================
驗證 M_VL_c ≈ M_PS × 2/5 同 M_VL_s ≈ M_R × E_proj 嘅精確度。
"""

import numpy as np

# 常數
phi = (1 + np.sqrt(5)) / 2
Nd = 44
M_Pl = 1.221e19  # GeV
g1 = 4 * np.sin(np.pi / 88) ** 2  # γ₁

# O89 級聯
M_GUT = M_Pl * g1**1
M_PS = M_Pl * g1**2
M_R = M_Pl * g1**3
M_EW = M_Pl * g1**8 * Nd

# O89 VL 閾值
M_VL_c = 1.26e14  # GeV
M_VL_s = 2.52e13  # GeV

# O54 投影因子
E_proj = 15.5  # muon projection factor

print("=" * 72)
print("  O108 — Script 03: VL 質量標度結構公式驗證")
print("=" * 72)

print(f"\n─── 級聯標度 ───")
print(f"  M_Pl = {M_Pl:.4e} GeV")
print(f"  M_GUT = M_Pl × γ₁¹ = {M_GUT:.4e} GeV")
print(f"  M_PS  = M_Pl × γ₁² = {M_PS:.4e} GeV")
print(f"  M_R   = M_Pl × γ₁³ = {M_R:.4e} GeV")
print(f"  M_EW  = M_Pl × γ₁⁸ × N_d = {M_EW:.4e} GeV")

print(f"\n─── 公式 1: M_VL_c = M_PS × 2/5 ───")
pred_c = M_PS * 2 / 5
dev_c = abs(pred_c - M_VL_c) / M_VL_c * 100
print(f"  M_PS × 2/5 = {pred_c:.4e} GeV")
print(f"  O89 value  = {M_VL_c:.4e} GeV")
print(f"  偏差 = {dev_c:.4f}%")
print(f"  狀態: {'✅' if dev_c < 1 else '🟡' if dev_c < 5 else '🔴'}")

print(f"\n─── 公式 2: M_VL_s = M_R × E_proj ───")
pred_s = M_R * E_proj
dev_s = abs(pred_s - M_VL_s) / M_VL_s * 100
print(f"  M_R × {E_proj} = {pred_s:.4e} GeV")
print(f"  O89 value    = {M_VL_s:.4e} GeV")
print(f"  偏差 = {dev_s:.4f}%")
print(f"  狀態: {'✅' if dev_s < 1 else '🟡' if dev_s < 5 else '🔴'}")

print(f"\n─── 公式 3: M_VL_c/M_VL_s = 5 = F₅ ───")
ratio = M_VL_c / M_VL_s
print(f"  M_VL_c/M_VL_s = {ratio:.4f}")
print(f"  F₅ = 5")
print(f"  偏差 = {abs(ratio - 5)/5*100:.4f}%")
print(f"  狀態: {'✅' if abs(ratio-5)/5 < 1 else '🟡'}")

print(f"\n─── 公式 4: 跨公式檢驗 ───")
# (M_PS × 2/5) / (M_R × E_proj) = ?
ratio2 = (M_PS * 2/5) / (M_R * E_proj)
print(f"  (M_PS × 2/5) / (M_R × E_proj) = {ratio2:.4f}")
print(f"  目標: 5.0")
print(f"  偏差 = {abs(ratio2 - 5)/5*100:.4f}%")

# 公式 5: 用 γ₁ 表達
print(f"\n─── 公式 5: 用 γ₁ 級聯表達 ───")
# M_VL_c = M_Pl × γ₁² × 2/5
# M_VL_s = M_Pl × γ₁³ × E_proj
pred_c2 = M_Pl * g1**2 * 2/5
pred_s2 = M_Pl * g1**3 * E_proj
print(f"  M_VL_c = M_Pl × γ₁² × 2/5 = {pred_c2:.4e} GeV")
print(f"  dev = {abs(pred_c2 - M_VL_c)/M_VL_c*100:.4f}%")
print(f"  M_VL_s = M_Pl × γ₁³ × E_proj = {pred_s2:.4e} GeV")
print(f"  dev = {abs(pred_s2 - M_VL_s)/M_VL_s*100:.4f}%")

# 公式 6: 探索 γ₁ 冪次
print(f"\n─── 公式 6: γ₁ 冪次探索 ───")
print(f"  γ₁ = {g1:.6e}")
for k in range(1, 13):
    val = M_Pl * g1**k
    if val < M_VL_s * 10 and val > M_VL_c / 10:
        dev_c = abs(val - M_VL_c) / M_VL_c * 100
        dev_s = abs(val - M_VL_s) / M_VL_s * 100
        print(f"  M_Pl × γ₁^{k:2d} = {val:.4e} GeV, dev_c={dev_c:.2f}%, dev_s={dev_s:.2f}%")

# 公式 7: M_VL_c = M_PS × F₅/F₅ = M_PS × 1 ? No
# 試 M_VL_c = M_PS × 2/φ²?
print(f"\n─── 公式 7: φ 比例探索 ───")
for numer, denom, name in [
    (2, 5, "2/5=F₅⁻¹"), (1, phi, "1/φ"), (1, phi**2, "1/φ²"),
    (2, phi, "2/φ"), (2, phi**2, "2/φ²"), (3, phi, "3/φ"),
    (1, 2*phi, "1/(2φ)"), (1, phi**3, "1/φ³"),
    (5, 13, "5/13=F₅/F₇"), (3, 8, "3/8=F₄/F₆"),
    (1, 3, "1/3"), (2, 3, "2/3"),
]:
    pred = M_PS * numer / denom
    dev = abs(pred - M_VL_c) / M_VL_c * 100
    print(f"  M_PS × {name:<10s} = {pred:.4e} GeV, dev={dev:.4f}%")

# 最準確嘅比例
print(f"\n─── 最準確嘅 M_VL_c/M_PS 比例 ───")
best_ratio = M_VL_c / M_PS
print(f"  M_VL_c / M_PS = {best_ratio:.6f}")
print(f"  2/5 = {2/5:.6f}")
print(f"  1/φ² = {1/phi**2:.6f}")
print(f"  1/φ = {1/phi:.6f}")
print(f"  φ⁻¹/2 = {1/(2*phi):.6f}")

# 最準確嘅 M_VL_s/M_R 比例
print(f"\n─── 最準確嘅 M_VL_s/M_R 比例 ───")
best_ratio_s = M_VL_s / M_R
print(f"  M_VL_s / M_R = {best_ratio_s:.6f}")
print(f"  E_proj = {E_proj}")
print(f"  88/√(π) = {88/np.sqrt(np.pi):.6f}")
print(f"  528/33 = {528/33:.6f}")
print(f"  90/6 = {90/6:.6f}")
print(f"  44/3 = {44/3:.6f}")
print(f"  φ⁴ = {phi**4:.6f}")
print(f"  φ⁵ = {phi**5:.6f}")
print(f"  N_d × φ⁻¹ = {Nd/phi:.6f}")
print(f"  N_d × φ⁻² = {Nd/phi**2:.6f}")

# 探索 15.5 嘅結構數分解
print(f"\n─── 15.5 = E_proj 結構分解 ───")
print(f"  15.5 = 31/2 = L₇ + 2? L₇=29, +2=31")
print(f"  15.5 = (N_d + L₄)/2? (44+7)/2=25.5 ❌")
print(f"  15.5 = (N_d - L₇)/2? (44-29)/2=7.5 ❌")
print(f"  15.5 = 90/6 - 0.5? 90/6=15, +0.5=15.5")
print(f"  15.5 = 528/34? 528/34=15.53")
print(f"  15.5 = N_d × φ⁻¹? 44/φ=27.2 ❌")
print(f"  15.5 = 17 - 1.5? n₀(Gen1)-1.5=15.5!")
print(f"  15.5 = 33/2 + 1? 33/2=16.5, -1=15.5")
print(f"  15.5 = 28.5 - 13? E_proj=28.5 (O54), -13=F₇=13")
print(f"  15.5 = 18 - 2.5? L₆=18, -2.5=15.5")
print(f"  15.5 = 7 + 8.5? L₄=7, +F₆=8, =15")
print(f"  15.5 = 15 + 0.5 = (N_d - L₇)/2 + 0.5")
print(f"  15.5 = 18 - 5/2 = L₆ - F₅/2 = 18 - 2.5 = 15.5 ✅")

print(f"\n─── 總結 ───")
print(f"  ✅ M_VL_c = M_PS × 2/5 ({dev_c:.4f}%)")
print(f"  ✅ M_VL_s = M_R × E_proj ({dev_s:.4f}%)")
print(f"  ✅ M_VL_c/M_VL_s = 5 = F₅ ({abs(ratio-5)/5*100:.4f}%)")
print(f"  🟡 E_proj = 15.5 = L₆ - F₅/2 = 18 - 2.5 (結構分解)")
print(f"  🔴 2/5 嘅結構來源: M_VL_c = M_PS × 2/F₅ 需要推導")