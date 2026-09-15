#!/usr/bin/env python3
# O196 scripts/02 — T1 v₁₁(k_n) 結構證明驗證 (公式修正版)
#
# 定理: n < 121 ⟹ v₁₁(k_n) = −n + ⌊(n−1)/11⌋  (k_n = n![tⁿ]ln M)
# 證明骨架 (cumulant-MGF 展開):
#   k_n = Σ_{partitions} n!·(−1)^{r+1}·((r−1)!/Πp_j!)·Π_j (m_j/j!)^{p_j},  r=Σp_j
#   關鍵: v₁₁(m_j) = −1 ∀j  (m_j = C(2j,j) + 2^{2j−4}/11, 11∤2^{2j−4})
#   項估值: v(π) = ⌊n/11⌋ + ⌊(r−1)/11⌋ − Σ⌊p_j/11⌋ − r − Σp_j⌊j/11⌋
#   (a) all-1 分拆 (p₁=n, r=n): v = ⌊(n−1)/11⌋ − n = 目標  ✓ 唯一最低
#   (b) 其他分拆: v ≥ 目標+1 (證明: r+Σp_j⌊j/11⌋ ≤ n−1 且 ⌊(r−1)/11⌋−Σ⌊p_j/11⌋ ≥ −1,
#       等號同時達成需要 r≡0 mod 11 + 唯一 2-part + Σ(p_j mod 11) = 11 → 矛盾)
#   ⟹ 唯一最低項 = all-1 ⟹ 冇相消 ⟹ v₁₁(k_n) = 目標
# 週期 11 來源: v₁₁((n−1)!) = ⌊(n−1)/11⌋ 跳躍 ⟹ anomaly 位 n ≡ 1 mod 11
from fractions import Fraction as F
import math

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

def v11_int(x):
    e = 0
    while x % 11 == 0: x //= 11; e += 1
    return e

def part_val(n, pi):
    """項估值公式 (pi = partition parts list)
    v(π) = ⌊n/11⌋ + ⌊(k−1)/11⌋ − Σ⌊p_j/11⌋ − k − Σp_j⌊j/11⌋
    注意 Σ⌊p_j/11⌋ 用 p//11 (=v₁₁(p!) 對 p<121), 唔係 v11(p)"""
    from collections import Counter
    cnt = Counter(pi)
    k = len(pi)
    v = (n//11) + ((k-1)//11) - sum(p//11 for p in cnt.values()) - k \
        - sum(p*(j//11) for j, p in cnt.items())
    return v

def partitions(n):
    res = []
    def rec(rem, maxp, cur):
        if rem == 0: res.append(cur[:]); return
        for first in range(min(rem, maxp), 0, -1):
            cur.append(first); rec(rem-first, first, cur); cur.pop()
    rec(n, n, [])
    return res

print("== T1a: all-1 分拆估值 = 目標 (公式, n=1..120) ==")
ok = True
for n in range(1, 121):
    target = -n + (n-1)//11
    v_all1 = part_val(n, [1]*n)
    if v_all1 != target:
        ok = False; print(f"  n={n}: v_all1={v_all1} target={target}")
check("T1a all-1 v = −n + ⌊(n−1)/11⌋ (n=1..120)", ok)

print("\n== T1b: 窮舉驗證 all-1 係唯一最低項 (n=1..30) ==")
ok = True; bad = []
for n in range(1, 31):
    target = -n + (n-1)//11
    minv = None; nmin = 0; minpis = []
    for pi in partitions(n):
        v = part_val(n, pi)
        if minv is None or v < minv: minv = v; nmin = 1; minpis = [pi]
        elif v == minv: nmin += 1; minpis.append(pi)
    if minv != target or nmin != 1 or minpis[0] != [1]*n:
        ok = False; bad.append((n, minv, nmin, minpis[0]))
check("T1b 唯一最低項 = all-1, v = 目標 (n=1..30)", ok, str(bad[:2]) if bad else "")

print("\n== T1c: v₁₁(k_n) 直接 Fraction 驗證 (n=1..80) ==")
NORD = 81
def smul(a, b):
    n = len(a)
    return [sum(a[i]*b[j] for i in range(n) for j in range(n) if i+j == k) for k in range(n)]
def sln1p(a):
    n = len(a)
    res = [F(0)]*n; p = [F(1)] + [F(0)]*(n-1)
    for k in range(1, n):
        p = smul(p, a)
        sgn = F(1) if k % 2 == 1 else F(-1)
        for i in range(n):
            res[i] += sgn * p[i] / k
    return res
e2 = [F(2)**n / math.factorial(n) for n in range(NORD)]
i0 = [F(0)]*NORD
for m in range(NORD//2 + 2):
    if 2*m < NORD: i0[2*m] = F(1, math.factorial(m)**2)
e4m1 = [F(0)]*NORD
for n in range(1, NORD): e4m1[n] = F(4)**n / math.factorial(n)
AB = [smul(e2, i0)[k] + e4m1[k]/176 for k in range(NORD)]
u = [F(0)] + AB[1:]
K = sln1p(u)
def v11f(x):
    n = abs(x.numerator); d = x.denominator
    e = 0
    while n % 11 == 0: n //= 11; e += 1
    while d % 11 == 0: d //= 11; e -= 1
    return e
ok = all(v11f(K[n]*math.factorial(n)) == -n + (n-1)//11 for n in range(1, NORD))
check("T1c v₁₁(k_n) = −n + ⌊(n−1)/11⌋ (Fraction, n=1..80)", ok)

print("\n== T1d: m_j 結構 — v₁₁(m_j) = −1 ∀j = 證明關鍵 ==")
ok = True
for j in range(1, 30):
    mj = F(math.comb(2*j, j)) + F(2)**(2*j-4) / 11 if j >= 2 else F(2) + F(1, 44)
    if v11f(mj) != -1: ok = False; print(f"  j={j}: v₁₁(m_j)={v11f(mj)}")
check("T1d v₁₁(C(2j,j) + 2^{2j−4}/11) = −1 ∀j≥1 (11∤2^{2j−4})", ok)

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
