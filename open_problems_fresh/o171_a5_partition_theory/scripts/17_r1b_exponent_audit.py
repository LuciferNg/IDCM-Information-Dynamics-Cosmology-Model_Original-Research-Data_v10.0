#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/17 — R1b-指數 獨立核對 (mpmath Binet 純路徑)

唔 import scripts/16; Lucas 用 **Binet 閉式** L_n = φⁿ + ψⁿ (ψ = −1/φ) 由 mpmath 算,
唔用遞歸。rung 唯一性用「d 嘅因數 ∩ 不變量集」獨立枚舉, 唔用 16 嘅雙迴圈。

核對目標:
  (1) R = N_d/B = 11 = L₅ (Binet 精確整數)
  (2) 表層 m = 5 唯一; 深層 m = 4 唯一
  (3) 交叉排除
"""
import mpmath as mpm
from fractions import Fraction as F

mp = mpm.mp
mp.dps = 50

B, NG, ND = 4, 3, 44
NP = NF = 0


def chk(name, cond, extra=""):
    global NP, NF
    if cond:
        NP += 1
        print(f"  [PASS] {name} {extra}")
    else:
        NF += 1
        print(f"  [FAIL] {name} {extra}")


# --- Binet: L_n = φⁿ + ψⁿ,  ψ = −1/φ ---
phi = (1 + mp.sqrt(5)) / 2
psi = -1 / phi


def lucas_binet(n):
    v = phi**n + psi**n
    return int(mp.nint(v)), abs(v - mp.nint(v))


print("=" * 80)
print("O171 scripts/17 — R1b-指數 獨立核對 (Binet 純路徑)")
print("=" * 80)

print("\n=== A: Lucas 由 Binet 閉式 (獨立於 16 嘅遞歸) ===")
LB = {}
for n in range(16):
    val, err = lucas_binet(n)
    LB[n] = val
    if n <= 8:
        print(f"  L_{n} = {val}  (|誤差| = {float(err):.2e})")
chk("A1 Binet 前 9 項 = 2,1,3,4,7,11,18,29,47",
    [LB[n] for n in range(9)] == [2, 1, 3, 4, 7, 11, 18, 29, 47])
chk("A2 Binet 全部 16 項誤差 < 1e-40 (dps=50)",
    all(lucas_binet(n)[1] < mp.mpf('1e-40') for n in range(16)))
chk("A3 L₅ = 11", LB[5] == 11)
chk("A4 L₄ = 7, L₇ = 29", LB[4] == 7 and LB[7] == 29)
# 恆等式 L_n² − 5F_n² = 4(−1)^n 交叉確認 Binet
fib = lambda n: int(mp.nint((phi**n - psi**n) / mp.sqrt(5)))
chk("A5 恆等式 L_n² − 5F_n² = 4(−1)^n (n=0..15) 交叉確認 Binet",
    all(LB[n]**2 - 5 * fib(n)**2 == 4 * ((-1)**n) for n in range(16)))

print("\n=== B: 鏈週期 R (獨立算式) ===")
R = F(2 * ND, 2 * B)
print(f"  R = 2N_d/(2B) = {R}  (Fraction, 約簡後分母 = {R.denominator})")
chk("B1 R 係整數", R.denominator == 1)
chk("B2 R = N_d/B = 11", F(ND, B) == R == 11)
chk("B3 R = L₅ (Binet 值) — 鏈週期 = Lucas 第 5 項", int(R) == LB[5])
chk("B4 2B·R = 2N_d = 88 (帶均分閉合)", 2 * B * int(R) == 2 * ND == 88)
# 88 嘅因數 ∩ Binet-Lucas
div88 = sorted(d for d in range(1, 89) if 88 % d == 0)
inter = [d for d in div88 if d in set(LB.values())]
print(f"  88 因數 ∩ Lucas = {inter}")
chk("B5 88 因數 ∩ Lucas = {1,2,4,11} ⇒ Lucas 路線唔唯一 (需帶數約束)", inter == [1, 2, 4, 11])
chk("B6 加帶數約束 (帶數 = 2B) ⇒ R = 11 唯一",
    88 // (2 * B) == 11 and 88 % (2 * B) == 0)

print("\n=== C: rung 分解唯一性 (因數 ∩ 不變量 路線) ===")
irr = [1, 3, 3, 4, 5]
A5 = sum(d * d for d in irr)
inv = sorted(set(irr + [sum(sorted(set(d for d in irr if d > 1))),
                        sum(d for d in irr if d > 1), sum(irr), A5]))
print(f"  不變量集 = {inv}")
Lset = set(LB.values())
for d in (33, 44, 55, 420):
    gs = [g for g in div88 if False]  # placeholder 避免誤用
    gdiv = sorted(g for g in range(1, d + 1) if d % g == 0 and g in inv)
    sols = [(g, d // g) for g in gdiv if d // g in Lset]
    print(f"  d = {d:>3}: 因數 ∩ 不變量 = {gdiv} ⇒ (g, L_m) = {sols}")
    chk(f"C d = {d} 唯一解 (因數路線獨立確認)", len(sols) == 1)
    chk(f"Cb d = {d} 嘅 L_m ∈ {sorted(set(LB.values()))}", sols[0][1] in Lset)
chk("C3 ★ 表層三成員 L_m = 11 = R (同一個 rung)",
    all(F(d, g) == R for d, g in ((33, 3), (44, 4), (55, 5))))
chk("C4 ★ 深層 420/|A₅| = 7 = L₄", F(420, A5) == 7 == LB[4])
chk("C5 ★ 420 = (L₇²−1)/2 (Binet L₇)", F(LB[7]**2 - 1, 2) == 420)

print("\n=== D: 交叉排除 (獨立重算) ===")
cross1 = [F(d, A5) for d in (33, 44, 55)]
print(f"  表層 /60 = {cross1}")
chk("D1 表層用 g = 60 ⇒ 全部 ∉ Lucas", all(q.denominator != 1 or q.numerator not in Lset for q in cross1))
cross2 = [F(420, g) for g in (3, 4, 5)]
print(f"  深層 /3,/4,/5 = {cross2}")
chk("D2 深層用 g ∈ {3,4,5} ⇒ 全部 ∉ Lucas",
    all(q.denominator != 1 or q.numerator not in Lset for q in cross2))
# 只有 g = 60 令 420/g ∈ Lucas
ok = [g for g in inv if F(420, g).denominator == 1 and int(F(420, g)) in Lset]
chk("D3 ★ 唯一性: g ∈ 不變量集中只有 g = 60 令 420/g ∈ Lucas", ok == [60])
ok2 = [g for g in inv if F(33, g).denominator == 1 and int(F(33, g)) in Lset]
chk("D4 ★ d = 33 只有 g = 3 令 33/g ∈ Lucas", ok2 == [3], f"(實際 {ok2})")

print("\n=== E: 總結 ===")
print("  R = N_d/B = 11 = L₅ (Binet) ⇒ 表層 m = 5 係導出量")
print("  420/|A₅| = 7 = L₄ (Binet) ⇒ 深層 m = 4 係導出量")
print("  ⚠️ 剩餘輸入: 階層律分派 (表層單因子 / 深層全積) — 本節唔重推")
print(f"\nRESULT: {NP}/{NP+NF} PASS")
print("=" * 80)
