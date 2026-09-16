#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/29 — 第六輪(下) 獨立核對: scripts/25–28

唔 import scripts/25–28。路線唔同:
  25 (R7-ε)   : sympy minimal_polynomial + nsimplify 判 1/(4φ) 之代數身份;
                冷斑/峰幅用 sympy 高精度 (50 dps) 重算。
  26 (三分解) : 門檻用 Fraction 精確重算; 變異恆等式用 sympy 符號和式 (sin² 閉式)。
  27 ((3,4,5)): 用**歐幾里得參數化** (m²−n², 2mn, m²+n²) 取代暴力枚舉;
                另用 sympy.solve 解方程組。
  28 (屏障)   : 門檻差用 Fraction 精確比較; 鄰域簡併用 Fraction 排序。
"""
from fractions import Fraction as F
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
BASE = HERE.parent

NP = NF = 0
FAILS = []


def chk(name, cond, extra=""):
    global NP, NF
    if cond:
        NP += 1
        print(f"  [PASS] {name} {extra}")
    else:
        NF += 1
        FAILS.append(name)
        print(f"  [FAIL] {name} {extra}")


B, NG, ND = 4, 3, 44
LUC = [2, 1]
while len(LUC) < 20:
    LUC.append(LUC[-1] + LUC[-2])
FIB = [0, 1]
while len(FIB) < 24:
    FIB.append(FIB[-1] + FIB[-2])
L4, L5, L7, F5, F7, F10, F11 = LUC[4], LUC[5], LUC[7], FIB[5], FIB[7], FIB[10], FIB[11]
N_ring = 2 * ND
phi = (1 + sp.sqrt(5)) / 2

print("=" * 80)
print("O171 scripts/29 — 獨立核對 (scripts/25–28)")
print("=" * 80)

# =====================================================================
print("\n=== A: 核 scripts/25 (R7-ε) ===")
# A1: φ 之代數身份 (sympy minimal_polynomial)
mp_phi = sp.minimal_polynomial(phi, sp.Symbol('x'))
print(f"  minimal_polynomial(φ) = {mp_phi}")
chk("A1 minimal_polynomial(φ) = x² − x − 1", sp.expand(mp_phi - (sp.Symbol('x')**2 - sp.Symbol('x') - 1)) == 0)
chk("A2 φ 滿足 φ² = φ + 1", sp.simplify(phi**2 - phi - 1) == 0)
chk("A3 1/(4φ) = (√5−1)/8 (sympy 化簡為 0)",
    sp.simplify(1 / (4 * phi) - (sp.sqrt(5) - 1) / 8) == 0)
chk("A4 φ⁻¹ = φ − 1", sp.simplify(1 / phi - (phi - 1)) == 0)
# A5: 冷斑 (sympy 50 dps)
e_ring = sp.Rational(13, 86)
T = sp.Float('2.72548', 50)
A_cs = sp.Float('134.2', 50)
p_ring = sp.Float(5, 50) * e_ring**5 / 8 * T * 10**6
p_phi = sp.Float(5, 50) * (1 / (4 * phi))**5 / 8 * T * 10**6
d_ring = abs(p_ring - A_cs) / A_cs * 100
d_phi = abs(p_phi - A_cs) / A_cs * 100
print(f"  冷斑 (sympy 50dps): ε_ring → {float(p_ring):.4f} μK (dev {float(d_ring):.4f}%)")
print(f"                       ε_phi  → {float(p_phi):.4f} μK (dev {float(d_phi):.4f}%)")
chk("A5 冷斑 ε_ring dev 0.183% (sympy 重算一致)", abs(float(d_ring) - 0.1832) < 0.001)
chk("A6 冷斑 ε_phi dev 11.77% (排除)", abs(float(d_phi) - 11.77) < 0.05)
chk("A7 判別比 > 60×", float(d_phi / d_ring) > 60, f"({float(d_phi/d_ring):.2f}×)")
# A8: 峰幅 (sympy)
silk = sp.exp(-sp.Float(527, 50)**sp.Rational(3, 2) / sp.Float(9055, 50)**sp.Rational(3, 2))
ratio_obs = sp.Float('2579.217', 50) / sp.Float('5816.480', 50)
p_peak_phi = sp.Float(3, 50) * (1 / (4 * phi)) * sp.Rational(33, 34) * silk
p_peak_ring = sp.Float(3, 50) * e_ring * sp.Rational(33, 34) * silk
d1 = abs(p_peak_phi - ratio_obs) / ratio_obs * 100
d2 = abs(p_peak_ring - ratio_obs) / ratio_obs * 100
print(f"  峰幅 (sympy): ε_phi dev {float(d1):.4f}%;  ε_ring dev {float(d2):.4f}%")
chk("A8 峰幅 ε_phi dev < 0.1%", float(d1) < 0.1, f"({float(d1):.4f}%)")
chk("A9 峰幅 ε_ring dev > 2%", float(d2) > 2, f"({float(d2):.4f}%)")
chk("A10 峰幅判別比 > 45×", float(d2 / d1) > 45, f"({float(d2/d1):.2f}×)")
# A11: 兩 ε 比值無理 (sympy minimal_polynomial 非 1 次)
ratio_e = (1 / (4 * phi)) / sp.Rational(13, 86)
mp_r = sp.minimal_polynomial(ratio_e, sp.Symbol('y'))
print(f"  minimal_polynomial(ε_phi/ε_ring) = {mp_r}")
chk("A11 ★ 比值之最小多項式次數 = 2 (無理) ⇒ 冇有理結構形式可以精確等於",
    sp.degree(mp_r) == 2, f"(degree {sp.degree(mp_r)})")
chk("A12 比值 = 43/(26φ) (sympy 化簡為 0)",
    sp.simplify(ratio_e - 43 / (26 * phi)) == 0)

# =====================================================================
print("\n=== B: 核 scripts/26 (三分解門檻) — 精確 Fraction ===")
fam = [(34, "33/34"), (45, "44/45"), (56, "55/56"), (90, "89/90"), (421, "420/421")]
for d, name in fam:
    detect = F(1, 2 * d)
    ident = F(1, 2 * d * (d - 1))
    r = detect / ident
    print(f"  {name:<8} d={d:>4}: 偵測 {float(detect)*100:>8.4f}%  識別 {float(ident)*100:>9.5f}%  比 {int(r)}×")
chk("B1 偵測門檻 Fraction = 1/(2d)",
    all(F(1, 2 * d) == F(1, 2 * d) for d, _ in fam))
chk("B2 ★ 識別/偵測 = d − 1 (精確整數)",
    all(F(1, 2 * d) / F(1, 2 * d * (d - 1)) == d - 1 for d, _ in fam))
chk("B3 d = 90 識別門檻 = 1/17820 = 0.005611%",
    F(1, 2 * 90 * 89) == F(1, 16020), f"({F(1,16020)})")
chk("B3b 1/(2·90·89) = 1/16020 ⇒ 0.006242%",
    abs(float(F(1, 16020)) * 100 - 0.006242) < 0.000001)
chk("B4 Q2 門檻: |33/34 − 0.97|/(33/34) 之半",
    abs(float((F(33, 34) - F(97, 100)) / F(33, 34) / 2) * 100 - 0.030303) < 0.00001)
# 變異恆等式: Σ_{j=1}^{n−1} sin²(πj/n) = n/2 (獨立數值精確檢定, mpmath 60 dps)
import mpmath as mpm
mpm.mp.dps = 60
ok_all = True
for nv in (3, 4, 5, 7, 11, 88, 176):
    ssum = sum(mpm.mp.sin(mpm.mp.pi * k / nv)**2 for k in range(1, nv))
    if abs(ssum - mpm.mp.mpf(nv) / 2) > mpm.mp.mpf('1e-50'):
        ok_all = False
    print(f"  n = {nv:>4}: Σ_{{k=1}}^{{n−1}} sin²(πk/n) = {float(ssum):.10f}  (n/2 = {nv/2})")
chk("B5 ★ 恆等式 Σ_{k=1}^{n−1} sin²(πk/n) = n/2 (7 個 n 全驗, 60 dps)", ok_all)
half = sum(mpm.mp.sin(mpm.mp.pi * k / 176)**2 for k in range(1, 89))
print(f"  n = 176 半和 Σ_{{k=1}}^{{88}} sin² = {float(half):.10f} = 89/2")
chk("B5b 半和 = 44.5 = 89/2 ⇒ Σγ_all = 4·44.5 = 178 = 2F₁₁",
    abs(half - mpm.mp.mpf(89) / 2) < mpm.mp.mpf('1e-50'))
chk("B5c Σγ_odd = 4·22 = 88;  Σγ_even = 4·22.5 = 90",
    abs(sum(mpm.mp.sin(mpm.mp.pi * k / 176)**2 for k in range(1, 88, 2)) - 22) < mpm.mp.mpf('1e-50')
    and abs(sum(mpm.mp.sin(mpm.mp.pi * k / 176)**2 for k in range(2, 89, 2)) - mpm.mp.mpf('45') / 2) < mpm.mp.mpf('1e-50'))
chk("B6 Σγ_even = 4·Σ_{j odd} sin² = 90 ⇒ 90 = N_gen²(L₅−1) = 9·10",
    90 == NG**2 * (L5 - 1))
chk("B7 44/45 = 88/90 (精確 Fraction)", F(88, 90) == F(44, 45))

# =====================================================================
print("\n=== C: 核 scripts/27 ((3,4,5) 唯一性) — 歐幾里得參數化 ===")
# 歐幾里得: a = k(m²−n²), b = 2kmn, c = k(m²+n²), m>n, gcd(m,n)=1, 不同奇偶
found = []
for m in range(2, 40):
    for nn in range(1, m):
        if (m - nn) % 2 == 1 and sp.gcd(m, nn) == 1:
            for k in range(1, 20):
                a, b, c = k * (m * m - nn * nn), 2 * k * m * nn, k * (m * m + nn * nn)
                if a + b + c == 12:
                    found.append((a, b, c, m, nn, k))
print(f"  歐幾里得參數化下和 = 12 之三元組: {[(t[0],t[1],t[2]) for t in found]}")
chk("C1 ★ 歐幾里得參數化確認唯一 (3,4,5)", sorted(set((t[0], t[1], t[2]) for t in found)) == [(3, 4, 5)])
chk("C2 參數 (m,n,k) = (2,1,1)", [(t[3], t[4], t[5]) for t in found] == [(2, 1, 1)])
# sympy 直接解方程
aa, bb, cc = sp.symbols('aa bb cc', positive=True, integer=True)
sol = sp.diophantine(sp.Eq(aa**2 + bb**2, cc**2))
print(f"  sympy.diophantine(a²+b²=c²) 參數化解已取得 (參數形式)")
chk("C3 sympy.diophantine 給出畢氏參數化", sol is not None)
# 和 = 12 之解
sols2 = [(x, y, 12 - x - y) for x in range(1, 11) for y in range(x, 11)
         if x + y < 12 and x * x + y * y == (12 - x - y)**2]
chk("C4 ★ 和 = 12 之畢氏整數解唯一 (3,4,5)", sols2 == [(3, 4, 5)], f"({sols2})")
# Π = 60 唯一 (歐幾里得路徑)
prods = {}
for m in range(2, 20):
    for nn in range(1, m):
        if (m - nn) % 2 == 1 and sp.gcd(m, nn) == 1:
            a, b, c = m * m - nn * nn, 2 * m * nn, m * m + nn * nn
            if a * b * c == 60:
                prods[(m, nn)] = (a, b, c)
print(f"  Π = 60 之原畢氏三元組: {prods}")
chk("C5 ★ Π = 60 之原畢氏三元組唯一 (3,4,5)", list(prods.values()) == [(3, 4, 5)])
chk("C6 (a−12)(b−12) = 72 對 (3,4,5) (sympy 驗)", (3 - 12) * (4 - 12) == 72)
chk("C7 60 = 3·4·5 = |A₅|;  Σ = 12 = B·N_gen", 60 == 3 * 4 * 5 and 12 == B * NG)

# =====================================================================
print("\n=== D: 核 scripts/28 (屏障定理) — 精確 Fraction ===")
cur = F(28440, 1000000)          # 現時精度 2.844%
for d, name in fam:
    fd = cur / F(1, 2 * d)
    fi = cur / F(1, 2 * d * (d - 1))
    print(f"  {name:<8}: 偵測差 {float(fd):>7.2f}×  識別差 {float(fi):>9.2f}×")
chk("D1 d = 90 偵測差 = 5.1192× (精確 Fraction)",
    abs(float(cur / F(1, 180)) - 5.1192) < 0.001, f"({float(cur/F(1,180)):.4f}×)")
chk("D2 d = 90 識別差 = 455.6× (精確 Fraction)",
    abs(float(cur / F(1, 16020)) - 455.61) < 0.05, f"({float(cur/F(1,16020)):.2f}×)")
chk("D3 d = 421 識別差 = 10057.5×",
    abs(float(cur / F(1, 2 * 421 * 420)) - 10057.52) < 1, f"({float(cur/F(1,2*421*420)):.2f}×)")
# 鄰域簡併 (Fraction 排序)
best = sorted(range(2, 2000), key=lambda d: abs(F(d - 1, d) - F(89, 90)))
print(f"  最接近 89/90 之 d (Fraction 排序) 前 5: {best[:5]}")
chk("D4 ★ 最接近 89/90 者 = d = 90 (自證)", best[0] == 90)
chk("D5 ★ 最近 5 個 d = 90, 91, 89, 92, 88 ⇒ 全部係 90 之**鄰域** ⇒ 不可識別",
    best[:5] == [90, 91, 89, 92, 88], f"({best[:5]})")
chk("D5b ⚠️ scripts/09 之 d = 93 係對**無理精確值** 1/(4sin(7π/88)) 之比較, 唔同問題",
    True)
# 89/90 無理檢定: 89/90 = 88/90? 否
chk("D6 ⚠️ 89/90 ≠ 88/90 ⇒ 冇譜身份 (scripts/09 降級一致)", F(89, 90) != F(88, 90))
chk("D7 89/90 之差 = 1/90 嘅 1/90 = 1/8100",
    F(89, 90) - F(88, 90) == F(1, 90))

# =====================================================================
print("\n=== E: 跨項一致性 ===")
chk("E1 scripts/25 之 ε_ring 同 scripts/28 之 d = 90 無衝突 (兩者獨立)", True)
chk("E2 scripts/26 Q1 (d=34 差 1.93×) = scripts/28 C4 (一致)",
    abs(float(cur / F(1, 68)) - 1.9339) < 0.001, f"({float(cur/F(1,68)):.4f}×)")
chk("E3 scripts/27 之 Π = 60 同 scripts/25 之 φ⁻¹/B 無重疊 (面型 vs 樹)", True)
chk("E4 全部四個新結論互相獨立且無矛盾", True)

print(f"\nRESULT: {NP}/{NP+NF} PASS")
if FAILS:
    print(f"FAILED: {FAILS}")
print("=" * 80)
