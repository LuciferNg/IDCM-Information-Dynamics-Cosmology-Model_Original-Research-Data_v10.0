#!/usr/bin/env python3
"""
O9: 統一驗證 — 用 script 16 正確峰表重算全部振幅級聯
=====================================================
峰表 (script 15/16 驗證):
m=1: ℓ=221  D=5816.5
m=2: ℓ=527  D=2579.2
m=3: ℓ=815  D=2552.7
m=4: ℓ=1013 D=1079.5
m=5: ℓ=1121 D=1246.3
m=6: ℓ=1337 D=757.9
m=7: ℓ=1400 D=830.2

重算: 相鄰比率 + 歸一化振幅 + 有理數擬合 + (2/3)^k
"""
import numpy as np
from fractions import Fraction

A = {1: 5816.5, 2: 2579.2, 3: 2552.7, 4: 1079.5, 5: 1246.3, 6: 757.9, 7: 830.2}
A1 = A[1]
phi = (1 + 5**0.5)/2

print("="*70)
print("O9: 統一振幅級聯 (script 16 峰表)")
print("="*70)

print("\n1. 歸一化振幅 A_m/A_1:")
for m in range(1, 8):
    a = A[m]/A1
    fr = Fraction(a).limit_denominator(50)
    dev = abs(a - fr.numerator/fr.denominator)/a*100
    print(f"   A_{m}/A_1 = {a:.4f} ≈ {fr.numerator}/{fr.denominator} ({fr.numerator/fr.denominator:.4f}) dev={dev:.2f}%")

print("\n2. 相鄰比率 A_{m+1}/A_m:")
ratios = {}
for m in range(1, 7):
    r = A[m+1]/A[m]
    ratios[m] = r
    fr = Fraction(r).limit_denominator(30)
    dev = abs(r - fr.numerator/fr.denominator)/r*100
    print(f"   A_{m+1}/A_{m} = {r:.4f} ≈ {fr.numerator}/{fr.denominator} ({fr.numerator/fr.denominator:.4f}) dev={dev:.2f}%")

print("\n3. (2/3)^k 指數:")
for m in range(1, 8):
    a = A[m]/A1
    k = np.log(a)/np.log(2/3)
    half = abs(k - round(2*k)/2)
    tag = "★半整數" if half < 0.15 else ""
    print(f"   A_{m}/A_1 = (2/3)^{k:.3f} {tag}")

print("\n4. ε=φ⁻¹/4 結構:")
eps = phi**-1/4
for m in range(1, 8):
    a = A[m]/A1
    print(f"   A_{m}/A_1 = {a:.4f} = {a/eps:.3f} × ε")

print("\n5. 5/8≈φ⁻¹ 檢查 (舊聲稱):")
print(f"   A_6/A_5 (統一) = {A[6]/A[5]:.4f} vs 5/8 = 0.6250 (dev {(A[6]/A[5]-5/8)/(5/8)*100:+.1f}%)")
print(f"   舊聲稱用錯 A6: 1373 峰 777.4 → 777.4/1246.3 = {777.4/1246.3:.4f} (但 1373 唔係 m=6 配對)")

print("\n6. 有理數級聯統一表:")
fracs = {}
for m in range(1, 7):
    r = ratios[m]
    fr = Fraction(r).limit_denominator(30)
    fracs[m] = fr
print("   A2/A1 = 4/9, A3/A2 = 1/1, A4/A3 = 11/26, A5/A4 = ?, A6/A5 = ?, A7/A6 = 23/21")
for m in range(1, 7):
    print(f"   A_{m+1}/A_{m} ≈ {fracs[m].numerator}/{fracs[m].denominator}")
