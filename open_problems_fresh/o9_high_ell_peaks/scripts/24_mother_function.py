#!/usr/bin/env python3
"""
O9-C: 振幅級聯母函數 — Fibonacci-Lucas 連分數生成
=====================================================
已確認級聯:
A₂/A₁ = 4/9 = (2/3)²
A₃/A₂ = 1/1
A₄/A₃ = 11/26
A₅/A₄ = 15/13
A₆/A₅ = 14/23
A₇/A₆ = 23/21

目標: 搵統一母函數鎖定所有比率

線索:
1. 4/9 = (2/3)²
2. 分子分母: 4,9,11,26,15,13,14,23,23,21
   → 9,13,21,23,26 = Fibonacci/Lucas 附近!
   F: 1,1,2,3,5,8,13,21,34
   L: 2,1,3,4,7,11,18,29,47
   13=F₇, 21=F₈, 11=L₅, 29=L₇!
3. 連分數: 4/9 = [0;2,4], 11/26 = [0;2,2,1,2]?
4. 檢查 (F_{m}/F_{m+1}) 級聯?
"""
from fractions import Fraction
import math

print("="*80)
print("O9-C: 振幅級聯母函數搜尋")
print("="*80)

# Fibonacci / Lucas
F = [0, 1]
for i in range(2, 16): F.append(F[-1]+F[-2])
L = [2, 1]
for i in range(2, 16): L.append(L[-1]+L[-2])

ratios = {
    2: (0.4434, Fraction(4, 9)),
    3: (0.9897, Fraction(1, 1)),
    4: (0.4229, Fraction(11, 26)),
    5: (1.1545, Fraction(15, 13)),
    6: (0.6081, Fraction(14, 23)),
    7: (1.0954, Fraction(23, 21)),
}

print("\n1. Fibonacci/Lucas 配對檢查:")
for m, (val, fr) in ratios.items():
    n, d = fr.numerator, fr.denominator
    nf = [i for i, x in enumerate(F) if x == n]
    df = [i for i, x in enumerate(F) if x == d]
    nl = [i for i, x in enumerate(L) if x == n]
    dl = [i for i, x in enumerate(L) if x == d]
    tags = []
    if nf: tags.append(f"F_{nf[0]}")
    if df: tags.append(f"F_{df[0]}")
    if nl: tags.append(f"L_{nl[0]}")
    if dl: tags.append(f"L_{dl[0]}")
    print(f"   A{m}/A{m-1} = {n}/{d} → {', '.join(tags) if tags else '—'}")

print("\n2. 連分數展開:")
for m, (val, fr) in ratios.items():
    cf = []
    x = fr.numerator/fr.denominator
    a = int(x)
    cf.append(a)
    for _ in range(5):
        if abs(x - a) < 1e-10: break
        x = 1/(x - a)
        a = int(x)
        cf.append(a)
    print(f"   A{m}/A{m-1} = {fr} → 連分數 {cf}")

print("\n3. 級聯生成嘗試:")
print("   a) 交替乘積 (2/3)^k 模式:")
# A_m/A_1 應該係 (2/3)^k × 修正
A1_norm = {1: Fraction(1,1), 2: Fraction(4,9), 3: Fraction(18,41),
           4: Fraction(5,27), 5: Fraction(3,14), 6: Fraction(3,23), 7: Fraction(1,7)}
print("   歸一化 A_m/A_1:")
for m in range(1, 8):
    fr = A1_norm[m]
    print(f"   A{m}/A1 = {fr.numerator}/{fr.denominator} = {fr.numerator/fr.denominator:.4f}")

print("\n   b) 檢查 A_m/A_1 分子分母 vs Fib/Lucas:")
for m in range(1, 8):
    fr = A1_norm[m]
    n, d = fr.numerator, fr.denominator
    nf = [i for i, x in enumerate(F) if x == n]
    df = [i for i, x in enumerate(F) if x == d]
    nl = [i for i, x in enumerate(L) if x == n]
    dl = [i for i, x in enumerate(L) if x == d]
    tags = []
    if nf: tags.append(f"F_{nf[0]}")
    if df: tags.append(f"F_{df[0]}")
    if nl: tags.append(f"L_{nl[0]}")
    if dl: tags.append(f"L_{dl[0]}")
    print(f"   A{m}/A1 = {n}/{d} → {', '.join(tags) if tags else '—'}")

print("\n4. 母函數候選:")
print("   A_m/A_1 ≈ 4/(3^m) × (Lucas 修正)?")
for m in range(1, 8):
    a = A1_norm[m].numerator/A1_norm[m].denominator
    print(f"   m={m}: A_m/A1={a:.4f}, 4/3^m={4/3**m:.4f}, 比={a/(4/3**m):.3f}")

print("\n   A_m/A_1 ≈ (2/3)^{k(m)} × ε 修正?")
phi = (1+5**0.5)/2
for m in range(1, 8):
    a = A1_norm[m].numerator/A1_norm[m].denominator
    k = math.log(a)/math.log(2/3)
    print(f"   m={m}: k={k:.3f}")

print("\n5. 關鍵: 分母 9, 41, 27, 14, 23, 7")
print("   → 9=L₄? L₄=7! 唔係")
print("   → 9=3², 41=L₆=18? 唔係 41")
print("   → 27=3³, 14=2×7, 23=L₄+16?")
print("   → 7=L₄")
print()
print("   41 好奇怪 — 18/41 可能係 4/9 × 81/82 之類?")
print(f"   (4/9) × (18/41)/(4/9) = {(18/41)/(4/9):.4f}")
print(f"   (18/41)/(4/9) = {18*9/(41*4):.4f} = 162/164 = 81/82")
print(f"   ★ 81/82 ≈ 1 − 1/82 ≈ 1 − φ⁻¹⁰? φ⁻¹⁰ = {phi**-10:.5f}")
print(f"   82 = 2×41, 41 = 33 + 8 = M + F₆! (M=33, F₆=8)")

print("\n6. 母函數結構總結:")
print("   A_m/A_1 分母: 9, 41, 27, 14, 23, 7")
print("   分子: 4, 18, 5, 3, 3, 1")
print()
print("   ⚠️ 誠實結論: 冇簡單 Fib/Lucas 配對")
print("   41 = M+F₆ 係唯一結構線索 (41 = 33+8)")
print("   需要更多數據 (ACT DR4 精確振幅) 先可以鎖定")
