#!/usr/bin/env python3
"""
O9-C6: 偶峰級聯真結構 — 相鄰偶峰比
=====================================
發現: A₂/A₁, A₄/A₁, A₆/A₁ 各自接近 (2/3)², (3/7)², (3/11)²
但 A₆/A₄ = 0.7021 ≠ (7/11)² = 0.4049

原因: 如果 A₂/A₁=(2/3)², A₄/A₁=(3/7)², A₆/A₁=(3/11)²
      A₄/A₂ = (3/7)²/(2/3)² = (9/14)² = 0.4133
      但實測 A₄/A₂ = 1079.5/2579.2 = 0.4185
      → 差 1.2% — 可能係誤差內!

      A₆/A₄ = (3/11)²/(3/7)² = (7/11)² = 0.4049
      但實測 A₆/A₄ = 757.9/1079.5 = 0.7021 ✗✗✗
      差 42%! 唔可以!

結論: (3/11)² 擬合 A₆/A₁ 係巧合? 或者 A₆ 用錯峰?

重算: m=6 obs=1337 D=757.9 (統一峰表)
      但之前 script 17 用 757.9, 對!
      A₆/A₁ = 757.9/5816.5 = 0.1303
      (3/11)² = 0.0744 ✗ 差 43%!
      但 script 28 話 (L₃/L₅)² dev=1.48%?
      L₃=3, L₅=11 → (3/11)² = 0.0744
      0.0744 vs 0.1303 = 43% 差!

      script 28 有 bug? 等我重睇...
"""
import numpy as np

print("="*80)
print("O9-C6: 偶峰級聯 — bug 排查")
print("="*80)

A_obs = {1: 5816.5, 2: 2579.2, 3: 2552.7, 4: 1079.5, 5: 1246.3, 6: 757.9, 7: 830.2}
A1 = A_obs[1]
norm = {m: A_obs[m]/A1 for m in range(1, 8)}

F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
L = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76]

print("\n1. 重算所有候選:")
cands = {
    2: [(F[3]/F[4])**2, (L[3]/L[4])**2],
    4: [(L[2]/L[4])**2, (F[4]/L[4])**2, (L[3]/L[5])**2],
    6: [(L[3]/L[5])**2, (F[6]/F[7])**2, (F[4]/F[5])**2],
}
for m, cs in cands.items():
    print(f"   m={m} 實測 {norm[m]:.4f}:")
    for c in cs:
        dev = abs(c - norm[m])/norm[m]*100
        print(f"      {c:.4f} dev={dev:.2f}%")

print("\n2. 之前 script 28 話 (L₃/L₅)² dev=1.48% 係錯?")
print(f"   (L₃/L₅)² = (3/11)² = {(L[3]/L[5])**2:.4f}")
print(f"   A₆/A₁ = {norm[6]:.4f}")
print(f"   差 = {(L[3]/L[5])**2 - norm[6]:.4f} = {(L[3]/L[5])**2/norm[6]*100:.1f}%")
print(f"   → (3/11)² = 0.0744 vs 0.1303 = 43% 差, 唔係 1.48%!")
print(f"   script 28 bug: L 陣列索引錯? L[3]=3, L[5]=11 — 冇錯")
print(f"   但 (3/11)² = 0.0744, dev = |0.0744−0.1303|/0.1303 = 42.9%")
print(f"   → script 28 有 bug! (L₃/L₅)² 唔係 0.1322!")

print("\n3. 重新檢查 script 28 輸出:")
print(f"   '(L_3/L_5)²=0.1322' — 0.1322 = (0.3636)²?")
print(f"   sqrt(0.1322) = {np.sqrt(0.1322):.4f}")
print(f"   3/11 = {3/11:.4f}")
print(f"   (3/11)² = {(3/11)**2:.4f}")
print(f"   → 0.1322 ≠ (3/11)² = 0.0744")
print(f"   script 28 嘅 (L_3/L_5)² 計算有 bug!")
print(f"   可能 L[3]/L[5] 係 11/3? (反轉)")

# 正確檢查
print("\n4. 正確搜尋 m=6 (0.1303):")
best = []
for i in range(1, 10):
    for j in range(1, 10):
        if F[i] > 0 and F[j] > 0:
            r = (F[i]/F[j])**2
            dev = abs(r - norm[6])/norm[6]*100
            if dev < 3: best.append((dev, f"(F_{i}/F_{j})²={r:.4f}"))
        if L[i] > 0 and L[j] > 0:
            r = (L[i]/L[j])**2
            dev = abs(r - norm[6])/norm[6]*100
            if dev < 3: best.append((dev, f"(L_{i}/L_{j})²={r:.4f}"))
best.sort()
for dev, s in best[:8]:
    print(f"   {s} dev={dev:.2f}%")

print("\n5. 正確搜尋 m=4 (0.1856):")
best = []
for i in range(1, 10):
    for j in range(1, 10):
        if F[i] > 0 and F[j] > 0:
            r = (F[i]/F[j])**2
            dev = abs(r - norm[4])/norm[4]*100
            if dev < 3: best.append((dev, f"(F_{i}/F_{j})²={r:.4f}"))
        if L[i] > 0 and L[j] > 0:
            r = (L[i]/L[j])**2
            dev = abs(r - norm[4])/norm[4]*100
            if dev < 3: best.append((dev, f"(L_{i}/L_{j})²={r:.4f}"))
best.sort()
for dev, s in best[:8]:
    print(f"   {s} dev={dev:.2f}%")
