#!/usr/bin/env python3
# O196 scripts/01 — T1: v₁₁(k_n) Bell 組合層證明 + T2: D_n 增長閉式檢查
# ① 11^n·k_n ∈ ℤ 且 v₁₁(11^n·k_n) = ⌊(n−1)/11⌋ (O195 D1 等價形式)
# ② Bell 項估值: 每項 v₁₁ = −n + ⌊(k−1)/11⌋ − Σp_j⌊j/11⌋ − Σ⌊p_j/11⌋, k=|π|
#    證明「所有項 ≥ −n + ⌊(n−1)/11⌋」+ 至少一項相等 + 相消結構
# ③ D_{n+2}/D_n vs (n+1)(n+2)·R⁻² (R = δ=1 根 1.202532) — 1/n 修正係咪假象
from fractions import Fraction as F
import math

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
A = smul(e2, i0)
B = [e4m1[k]/176 for k in range(NORD)]
AB = [A[k]+B[k] for k in range(NORD)]
u = [F(0)] + AB[1:]
K = sln1p(u)
k_n = [K[n]*math.factorial(n) for n in range(1, NORD)]

def v11_int(x):
    e = 0
    while x % 11 == 0: x //= 11; e += 1
    return e

print("== T1a: 11^n·k_n ∈ ℤ, v₁₁(11^n·k_n) = ⌊(n−1)/11⌋ ==")
fails = []
for n in range(1, 81):
    kn = k_n[n-1]
    scaled = kn * (11**n)
    if scaled.denominator != 1:
        fails.append((n, "not int"))
        continue
    v = v11_int(scaled.numerator)
    expect = (n-1)//11
    if v != expect:
        fails.append((n, v, expect))
print(f"  n=1..80: {'ALL PASS' if not fails else fails}")

print("\n== T1b: Bell 項估值分析 ==")
print("  每 partition π (k=|π| 部分, p_j 係 j 出現次數, Σp_j·j=n):")
print("  v₁₁(項) = −n + ⌊(k−1)/11⌋ − Σ_j p_j⌊j/11⌋ − Σ_j ⌊p_j/11⌋")
print("  目標: v₁₁(k_n) = −n + ⌊(n−1)/11⌋ (即 11^n·k_n v₁₁ = ⌊(n−1)/11⌋)")
# 對細 n 枚舉 partition, 睇項估值分佈 + 相消
def partitions(n, max_part=None):
    if n == 0: yield []; return
    if max_part is None: max_part = n
    for first in range(min(n, max_part), 0, -1):
        for rest in partitions(n - first, first):
            yield [first] + rest

print("\n  各項 v₁₁ (n=5..14, 對比淨值):")
for n in range(5, 15):
    kn = k_n[n-1]
    net = -n + (n-1)//11
    terms = []
    for pi in partitions(n):
        k = len(pi)
        from collections import Counter
        cnt = Counter(pi)
        # 項估值 (未計 m_j 內部 — m_j = C(2j,j) + 2^{2j−4}/11, v₁₁(m_j) = −1 ∀j)
        v = -n + (k-1)//11 - sum(p*(j//11) for j, p in cnt.items()) - sum((p//11) for p in cnt.values())
        terms.append((v, tuple(pi)))
    vmin = min(t[0] for t in terms)
    print(f"  n={n:>2}: 淨 v₁₁(k_n) = {net}, 項估值 min = {vmin}, "
          f"min 項數 = {sum(1 for t in terms if t[0]==vmin)}, "
          f"min 項 = {[t[1] for t in terms if t[0]==vmin][:3]}")
