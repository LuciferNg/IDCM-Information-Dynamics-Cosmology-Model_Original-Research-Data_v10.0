#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/19 — R8-算子 獨立核對 (sympy sqrt_mod + 高斯歐幾里得演算法)

唔 import scripts/18。路線完全唔同:
  18: 由錨對 (14,15) **正算** ⇒ z², 再用 isqrt 窮舉確認兩平方和表示唯一。
  19: 由質數 421 **反解** —— sqrt_mod(−1, 421) 取 √−1, 再走 Z[i] 嘅
      **歐幾里得演算法** gcd(421, x+i) ⇒ 高斯素因子 ⇒ 讀出 (a, b)。
      Lucas 用 sympy.fibonacci 恆等式 L_n = F_{n−1} + F_{n+1} 獨立取得。
"""
from fractions import Fraction as F

from sympy import fibonacci, isprime
from sympy.ntheory.residue_ntheory import sqrt_mod

NP = NF = 0


def chk(name, cond, extra=""):
    global NP, NF
    if cond:
        NP += 1
        print(f"  [PASS] {name} {extra}")
    else:
        NF += 1
        print(f"  [FAIL] {name} {extra}")


# ---- 高斯整數基本運算 (本檔自建, 唔共用 18) ----
def gm(z, w):
    return (z[0] * w[0] - z[1] * w[1], z[0] * w[1] + z[1] * w[0])


def gconj(z):
    return (z[0], -z[1])


def gn(z):
    return z[0] * z[0] + z[1] * z[1]


def gdiv(a, b):
    """高斯整數除法 (最近點取整)"""
    num = gm(a, gconj(b))
    den = gn(b)
    return (round(F(num[0], den)), round(F(num[1], den)))


def gsub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def ggcd(a, b):
    """Z[i] 歐幾里得演算法"""
    while b != (0, 0):
        q = gdiv(a, b)
        r = gsub(a, gm(q, b))
        a, b = b, r
    return a


print("=" * 80)
print("O171 scripts/19 — R8-算子 獨立核對 (sqrt_mod + 高斯歐幾里得)")
print("=" * 80)

p = 421
print("\n=== A: 由質數 421 反解 (唔用錨對做輸入) ===")
chk("A1 421 係質數 (sympy.isprime)", isprime(421))
chk("A2 421 ≡ 1 (mod 4)", p % 4 == 1)
x = sqrt_mod(-1, p)
print(f"  sqrt_mod(−1, 421) = {x}   (驗: {x}² mod 421 = {(x*x) % p})")
chk("A3 x² ≡ −1 (mod 421)", (x * x) % p == p - 1)
g = ggcd((p, 0), (x, 1))
print(f"  gcd(421, {x}+i) 高斯歐幾里得 ⇒ g = {g[0]} + {g[1]}i")
chk("A4 gcd 範數 = 421", gn(g) == 421, f"(N(g) = {gn(g)})")
a19, b19 = abs(g[0]), abs(g[1])
chk("A5 ★ 由 gcd 讀出 (|a|, |b|) = (14, 15) 或 (15, 14)",
    sorted([a19, b19]) == [14, 15], f"(實際 {sorted([a19, b19])})")
a, b = 14, 15
chk("A6 ★ 反解路線命中錨對 (14, 15) — 與 18 嘅正算一致", sorted([a19, b19]) == [a, b])
chk("A7 421 分裂為 z·z̄ (唯一高斯素因子對)", gn(g) == p and gm(g, gconj(g)) == (p, 0),
    f"(g·ḡ = {gm(g, gconj(g))})")

print("\n=== B: Lucas 由 sympy Fibonacci 恆等式 (獨立於 18 嘅遞歸) ===")
L = {n: int(fibonacci(n - 1) + fibonacci(n + 1)) for n in range(1, 12)}
print(f"  L₁..L₁₁ = {[L[n] for n in range(1, 12)]}")
chk("B1 L₅ = 11, L₄ = 7, L₇ = 29", (L[5], L[4], L[7]) == (11, 7, 29))
chk("B2 恆等式 L_n = F_{n−1} + F_{n+1} (n = 1..11) 全中",
    all(L[n] == int(fibonacci(n - 1) + fibonacci(n + 1)) for n in range(1, 12)))
chk("B3 L₇ = a + b", L[7] == a + b)
chk("B4 L₄ = (L₇ − 15)/2 = 7", F(L[7] - 15, 2) == L[4])

print("\n=== C: z² 由反解得到嘅 z 重算 ===")
z = (a, b)
z2 = gm(z, z)
print(f"  z = {z[0]}+{z[1]}i  ⇒  z² = {z2[0]}+{z2[1]}i")
chk("C1 z² = −29 + 420i", z2 == (-29, 420))
chk("C2 N(z²) = 421² (範數乘法性)", gn(z2) == p * p)
chk("C3 Re² + Im² = 29² + 420² = 421²", 29**2 + 420**2 == p * p,
    f"({29**2+420**2} = {p*p})")
chk("C4 ★ 畢氏三元組 (29, 420, 421) — 421 係斜邊", 29**2 + 420**2 == 421**2)
chk("C5 |Re(z²)| = 29 = L₇", abs(z2[0]) == L[7])
chk("C6 Im(z²) = 420 = 2ab", z2[1] == 2 * a * b)
chk("C7 420 = (L₇²−1)/2 同 Im(z²) 一致", F(L[7]**2 - 1, 2) == z2[1])
chk("C8 421 = (L₇²+1)/2 同 N(z) 一致", F(L[7]**2 + 1, 2) == p)

print("\n=== D: sin(2θ) 算子佔比 (Fraction 精確) ===")
s2 = F(z2[1], gn(z))
print(f"  Im(z²)/N(z) = {s2} = {float(s2):.15f}")
chk("D1 Im(z²)/N(z) = 420/421", s2 == F(420, 421))
chk("D2 = 2ab/(a²+b²) (sin 2θ 形式)", s2 == F(2 * a * b, a * a + b * b))
chk("D3 Re²/N² + Im²/N² = 1", F(z2[0]**2, gn(z)**2) + F(z2[1]**2, gn(z)**2) == 1)
chk("D4 420/421 + 1/421 = 1 (真空佔比 1/d)", s2 + F(1, 421) == 1)

print("\n=== E: 唯一性 (由高斯素分解) ===")
# 421 質數 ⇒ Z[i] 中分裂成唯一 (至單位) 素因子對
cands = []
for u in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
    for zz in [g, gconj(g)]:
        w = gm(u, zz)
        cands.append((abs(w[0]), abs(w[1])))
uniq = sorted(set(tuple(sorted(t)) for t in cands))
print(f"  由 gcd 及其單位/共軛變體得到嘅 (|a|,|b|) 集合 = {uniq}")
chk("E1 至單位/共軛唯一 ⇒ 表示 = {14,15}", uniq == [(14, 15)])
chk("E2 421 質數 ⇒ Z[i] 分裂唯一 (Fermat 定理)", isprime(421) and 421 % 4 == 1)
# 交叉: 唔存在其他 (a,b) 令 a²+b² = 421 且 a+b = 29
alt = [(u, v) for u in range(1, 30) for v in range(u, 30)
       if u * u + v * v == 421 and u + v == 29]
print(f"  同時滿足 a²+b² = 421 且 a+b = 29 嘅 (a,b) = {alt}")
chk("E3 ★ 雙約束 (範數 + 和) 下解唯一 = (14, 15)", alt == [(14, 15)])

print("\n=== G: ★ 模算子讀法 (L₇ 係 √−1 mod 421) ===")
chk("G1 29² ≡ −1 (mod 421)", (29 * 29) % 421 == 420)
chk("G2 421 = (29²+1)/2 ⟺ 29² ≡ −1 (mod 421)  (同一條)", (29 * 29 + 1) // 2 == 421 == (29 * 29 + 1) / 2)
# ord_{421}(29)
o, v = 1, 29
while v != 1:
    v = (v * 29) % 421
    o += 1
print(f"  ord_{{421}}(29) = {o};  ⟨29⟩ = {{1, 29, 420, 392}}")
chk("G3 ord_{421}(29) = 4 (Z₄ 子群)", o == 4)
sub = sorted({pow(29, k, 421) for k in range(4)})
print(f"  ⟨29⟩ = {sub}")
chk("G4 ⟨29⟩ = {{1, 29, 420, 392}} = {{1, L₇, 420, −L₇}}", sub == [1, 29, 392, 420])
chk("G5 ★★ 420 = 29² mod 421 — sector **分子** = L₇² 嘅模值 (平方算子)",
    pow(29, 2, 421) == 420)
chk("G6 ★★ 421 = N(14+15i) — sector **分母** = 高斯範數", gn(g) == 421)
chk("G7 ★ 兩個算子讀法一致: 420/421 = (L₇² mod 421)/421 = Im(z²)/N(z)",
    F(pow(29, 2, 421), 421) == F(z2[1], gn(z)) == F(420, 421))
chk("G8 −1 ∈ ⟨29⟩ (即 420 係 Z₄ 中嘅 −1)", pow(29, 2, 421) == 420)

print("\n=== H: 總結 ===")
print("  反解路線 (sqrt_mod + 高斯歐幾里得) ⇒ z = 14+15i ⇒ z² = −29+420i")
print("  正算路線 (scripts/18) ⇒ 同一結果 ⇒ 兩條獨立路徑一致")
print("  ★ 額外: sqrt_mod(−1, 421) = 29 = L₇ ⇒ 420 = L₇² mod 421 (平方算子)")
print(f"\nRESULT: {NP}/{NP+NF} PASS")
print("=" * 80)
