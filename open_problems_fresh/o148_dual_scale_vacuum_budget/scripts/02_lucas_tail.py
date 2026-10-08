#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O148 scripts/02_lucas_tail.py
=============================
δ 族結構定理: 41/60 vs 4/(phi^4-1) 嘅「觀察者稅」唔係物理效應,
而係 Lucas 遞迴嘅有限尾:  L_n*phi - L_{n+1} = (-1)^n * sqrt(5) * phi^-n

sympy 精確推導, 每個 δ 成員:
  delta1 = 41/60  - 4/(phi^4-1)  =  sqrt(5)*phi^-10 / (60*(3*phi+1))     (o33「觀察者稅」)
  delta2 = 19/41  - 3/(4*phi)    = -sqrt(5)*phi^-9  / (164*phi)          (Ω_m/Ω_L 整數 vs phi 形式)
  delta3 = 19/123 - phi^-1/4     = -sqrt(5)*phi^-10 / 492                (ε_exact vs ε_phi)
  delta4 = 41/19 - 4*phi/3       = +sqrt(5)*phi^-9  / 57                 (O39「精確 4φ/3」審計, 有理-phi 約定)
  M*     = 33 - 180*delta1       = 33 - 3*sqrt(5)*phi^-10/(3*phi+1)      (Q1 M* 拆穿)

定理背景: L_n = phi^n + (-phi)^-n, 所以
  L_n*phi - L_{n+1} = (-phi)^-n * (phi - (-phi)^-1)
                    = (-1)^n * phi^-n * (phi + phi^-1)
                    = (-1)^n * sqrt(5) * phi^-n        [因 phi + phi^-1 = sqrt(5)]
呢個係 Lucas 恆等式嘅精確代數形式 — δ 嘅量級就係 phi^-n 指數衰減尾。
"""
import sympy as sp

# ---------- 符號 ----------
phi = sp.symbols('phi', positive=True)
sqrt5 = sp.sqrt(5)

def lucas_sym(n):
    return sp.simplify(phi**n + (-phi)**(-n))

PHI_VAL = (1 + sp.sqrt(5)) / 2

def check(name, lhs, rhs):
    diff = sp.simplify(lhs - rhs)
    if diff == 0:
        print(f"  [PASS] {name}")
        return True
    # 代換 phi = (1+sqrt5)/2 後再驗 (符號化簡可能唔完全)
    d_sub = sp.simplify(diff.subs(phi, PHI_VAL))
    if d_sub == 0:
        print(f"  [PASS] {name} (phi 代換後為 0)")
        return True
    num = sp.N(d_sub, 40)          # 而家係純數值 (Float)
    if abs(num) < 1e-35:
        print(f"  [PASS] {name} (數值 0: {num})")
        return True
    print(f"  [FAIL] {name}  差 = {diff} = {num}")
    return False

print("=" * 72)
print("O148 02: δ 族 = Lucas 尾 (sympy 精確)")
print("=" * 72)

print("\n[1] 定理: L_n*phi - L_{n+1} = (-1)^n*sqrt(5)*phi^-n")
ok = True
for n in range(1, 14):
    Ln, Ln1 = lucas_sym(n), lucas_sym(n + 1)
    lhs = sp.simplify(Ln * phi - Ln1)
    rhs = sp.simplify((-1)**n * sqrt5 * phi**(-n))
    ok &= check(f"n={n}: L{n}*phi - L{n+1} == (-1)^{n}*sqrt5*phi^-{n}", lhs, rhs)

# 整數驗證: L_9=76, L_10=123, L_11=199
print("\n[2] Lucas 整數 (由 phi 表達式還原)")
for n, v in [(9, 76), (10, 123), (11, 199)]:
    Ln = sp.simplify(phi**n + (-phi)**(-n))
    # 用 sqrt5 代換: phi = (1+sqrt5)/2
    Ln_sub = Ln.subs(phi, (1 + sqrt5) / 2).simplify()
    ok &= check(f"L_{n} == {v}", Ln_sub, sp.Integer(v))

print("\n[3] delta1 = 41/60 - 4/(phi^4-1) == sqrt5*phi^-10/(60*(3phi+1))")
phi4m1 = (phi**4 - 1)
d1 = sp.simplify(sp.Rational(41, 60) - 4 / phi4m1)
tail1 = sp.simplify(sqrt5 * phi**(-10) / (60 * (3 * phi + 1)))
ok &= check("delta1 尾部形式", d1 - tail1, 0)
ok &= check("41/60 - 4/(phi^4-1) == (L10*phi - L11)/(60*(3phi+1)) [o34 恆等式 = 同一尾]",
            d1, sp.simplify((lucas_sym(10) * phi - lucas_sym(11)) / (60 * (3 * phi + 1))))
print(f"    delta1 = {sp.N(d1.subs(phi, (1 + sqrt5) / 2), 15)}")

print("\n[4] delta2 = 19/41 - 3/(4phi) == -sqrt5*phi^-9/(164*phi)")
d2 = sp.simplify(sp.Rational(19, 41) - sp.Rational(3, 4) / phi)
tail2 = sp.simplify(-sqrt5 * phi**(-9) / (164 * phi))
ok &= check("delta2 尾部形式", d2 - tail2, 0)
ok &= check("delta2 == (L9*phi - L10)/(164*phi) [Lucas 對偶]",
            d2, sp.simplify((lucas_sym(9) * phi - lucas_sym(10)) / (164 * phi)))
print(f"    delta2 = {sp.N(d2.subs(phi, (1 + sqrt5) / 2), 15)}")

print("\n[5] delta3 = 19/123 - phi^-1/4 == -sqrt5*phi^-10/492")
d3 = sp.simplify(sp.Rational(19, 123) - sp.Rational(1, 4) / phi)
tail3 = sp.simplify(-sqrt5 * phi**(-10) / 492)
ok &= check("delta3 尾部形式", d3 - tail3, 0)
print(f"    delta3 = {sp.N(d3.subs(phi, (1 + sqrt5) / 2), 15)}")

print("\n[6] delta4 = 41/19 - 4phi/3 == +sqrt5*phi^-9/57  (有理-phi 約定)")
d4 = sp.simplify(sp.Rational(41, 19) - 4 * phi / 3)
tail4 = sp.simplify(+sqrt5 * phi**(-9) / 57)
ok &= check("delta4 尾部形式", d4 - tail4, 0)
print(f"    delta4 = {sp.N(d4.subs(phi, (1 + sqrt5) / 2), 15)}")

print("\n[7] M* = 33 - 180*delta1 (Q1 拆穿) == 33 - 3*sqrt5*phi^-10/(3phi+1)")
Mstar = sp.simplify(33 - 180 * d1)
Mstar2 = sp.simplify(33 - 3 * sqrt5 * phi**(-10) / (3 * phi + 1))
ok &= check("M* 尾部形式", Mstar - Mstar2, 0)
print(f"    M* = {sp.N(Mstar.subs(phi, (1 + sqrt5) / 2), 15)}  (≠ 33, 偏差 = 180*delta1 = {sp.N(180 * d1.subs(phi, (1 + sqrt5) / 2), 10)})")

print("\n[8] 指數衰減: phi^-n 量級表 (δ 族點解細)")
phi_num = PHI_VAL
for n in [8, 9, 10, 11]:
    print(f"    phi^-{n} = {sp.N(phi_num**(-n), 12)}  (Lucas 尾特徵尺度)")

print("\n" + "=" * 72)
print(f"RESULT: {'ALL PASS' if ok else 'HAS FAILURES'}")
raise SystemExit(0 if ok else 1)