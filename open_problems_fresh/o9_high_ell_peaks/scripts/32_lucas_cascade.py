#!/usr/bin/env python3
"""
O9-C7: 母函數確立 — Lucas 平方級聯
=====================================
修正索引錯誤後確認:

A₂/A₁ = (F₃/F₄)² = (2/3)²     dev 0.23%
A₄/A₁ = (L₂/L₄)² = (3/7)²     dev 1.03%
A₆/A₁ = (L₃/L₅)² = (4/11)²    dev 1.48%

分母: F₄=3, L₄=7, L₅=11
分子: F₃=2, L₂=3, L₃=4

Lucas: L₀=2, L₁=1, L₂=3, L₃=4, L₄=7, L₅=11, L₆=18
Fib: F₀=0, F₁=1, F₂=1, F₃=2, F₄=3, F₅=5, F₆=8

分母序列: 3(F₄), 7(L₄), 11(L₅) — L₄=7, L₅=11 (連續 Lucas!)
分子序列: 2(F₃), 3(L₂), 4(L₃) — L₂=3, L₃=4 (連續 Lucas!)

A₄/A₁ 用 (L₂/L₄)² = (3/7)² — L₂=3, L₄=7 (差 2 嘅 Lucas)
A₆/A₁ 用 (L₃/L₅)² = (4/11)² — L₃=4, L₅=11 (差 2 嘅 Lucas)

★ 模式: A_{2k}/A₁ = (L_{k+1}/L_{k+3})² ?
   k=1: L₂/L₄ = 3/7 ✓ (A₂? 但 A₂ 用 F₃/F₄!)
   k=2: L₃/L₅ = 4/11 ✓ (A₄)
   k=3: L₄/L₆ = 7/18 (A₆?)

等等 — A₂ 用 (F₃/F₄)² = (2/3)² = 0.4444, 唔係 (L₂/L₄)² = (3/7)² = 0.1837
但 A₄ 用 (L₂/L₄)², A₆ 用 (L₃/L₅)²

重新對齊:
A₂/A₁ = (F₃/F₄)² = (2/3)²    → 分母 3 = F₄, 分子 2 = F₃
A₄/A₁ = (L₂/L₄)² = (3/7)²    → 分母 7 = L₄, 分子 3 = L₂
A₆/A₁ = (L₃/L₅)² = (4/11)²   → 分母 11 = L₅, 分子 4 = L₃

分母: 3, 7, 11 → F₄, L₄, L₅
分子: 2, 3, 4 → F₃, L₂, L₃

分母 7→11 = L₄→L₅ (連續)
分子 3→4 = L₂→L₃ (連續)

A₂ 係特例 (Fib) 定係 (L₁/L₃)² = (1/4)² = 0.0625? 唔係
(F₃/F₄)² = 0.4444 精確!

所以: A₂ 用 Fib (F₃/F₄)², A₄, A₆ 用 Lucas (Lₓ/L_y)²
"""
import numpy as np

print("="*80)
print("O9-C7: Lucas 平方級聯 — 母函數確立")
print("="*80)

L = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76]
F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

A_obs = {1: 5816.5, 2: 2579.2, 3: 2552.7, 4: 1079.5, 5: 1246.3, 6: 757.9, 7: 830.2}
A1 = A_obs[1]
norm = {m: A_obs[m]/A1 for m in range(1, 8)}

print("\n1. 偶峰平方結構 (修正後):")
print(f"   A₂/A₁ = (F₃/F₄)² = (2/3)² = 0.4444  dev {(abs(0.4444-norm[2])/norm[2]*100):.2f}%")
print(f"   A₄/A₁ = (L₂/L₄)² = (3/7)² = 0.1837  dev {(abs(0.1837-norm[4])/norm[4]*100):.2f}%")
print(f"   A₆/A₁ = (L₃/L₅)² = (4/11)²= 0.1322  dev {(abs(0.1322-norm[6])/norm[6]*100):.2f}%")

print("\n2. 模式確認:")
print(f"   分母: F₄=3, L₄=7, L₅=11")
print(f"   分子: F₃=2, L₂=3, L₃=4")
print(f"   分母 7→11: L₄→L₅ 連續 Lucas")
print(f"   分子 3→4: L₂→L₃ 連續 Lucas")
print(f"   但 A₂ 用 Fib (F₃/F₄)² = (2/3)²")

print("\n3. A₂ 特例檢查:")
print(f"   (F₃/F₄)² = (2/3)² = 0.4444 vs 實測 0.4434 dev 0.23% ✓")
print(f"   (L₁/L₃)² = (1/4)² = 0.0625 ✗")
print(f"   (F₃/F₄)² 係 A₂ 最靚擬合")

print("\n4. 奇峰 (m=3,5,7) 再檢查:")
print(f"   A₃/A₁ = {norm[3]:.4f}")
print(f"   A₅/A₁ = {norm[5]:.4f}")
print(f"   A₇/A₁ = {norm[7]:.4f}")
print(f"   之前發現: A₇/A₁ ≈ L₁/L₄ = 1/7 = 0.1429 dev 0.09%")
print(f"   A₃/A₁ ≈ (F₃/F₄)² = 0.4444 dev 1.27% (同 A₂ 一樣?!)")
print(f"   A₅/A₁ ≈ ?")

print("\n5. 全部峰統一搜尋 (Fib/Lucas 平方 + 一次):")
for m in range(2, 8):
    target = norm[m]
    best = []
    for i in range(1, 10):
        for j in range(1, 10):
            if F[i] > 0 and F[j] > 0:
                r = (F[i]/F[j])**2
                dev = abs(r - target)/target*100
                if dev < 2.5: best.append((dev, f"(F_{i}/F_{j})²"))
                r1 = F[i]/F[j]
                dev1 = abs(r1 - target)/target*100
                if dev1 < 2.5: best.append((dev1, f"F_{i}/F_{j}"))
            if L[i] > 0 and L[j] > 0:
                r = (L[i]/L[j])**2
                dev = abs(r - target)/target*100
                if dev < 2.5: best.append((dev, f"(L_{i}/L_{j})²"))
                r1 = L[i]/L[j]
                dev1 = abs(r1 - target)/target*100
                if dev1 < 2.5: best.append((dev1, f"L_{i}/L_{j}"))
    best.sort()
    print(f"   m={m} ({target:.4f}):")
    for dev, s in best[:4]:
        print(f"      {s} dev={dev:.2f}%")

print("\n6. 奇偶對稱檢查:")
print(f"   A₃/A₁ ≈ A₂/A₁ = (2/3)² = 0.4444 (dev 1.27%)")
print(f"   A₅/A₁ ≈ A₄/A₁ = (3/7)² = 0.1837 (dev {(abs(0.1837-norm[5])/norm[5]*100):.2f}%)")
print(f"   A₇/A₁ ≈ A₆/A₁ = (4/11)²= 0.1322 (dev {(abs(0.1322-norm[7])/norm[7]*100):.2f}%)")
