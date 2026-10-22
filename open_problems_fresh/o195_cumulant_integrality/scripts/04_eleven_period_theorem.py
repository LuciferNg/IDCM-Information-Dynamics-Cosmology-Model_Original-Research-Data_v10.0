#!/usr/bin/env python3
# O195 scripts/04 — 開放項 2 閉合: k_n 分母 11 指數 11-週期定理驗證 (n≤80)
# 觀察: v₁₁(den k_n) = n−1 一般; n ≡ 1 (mod 11) 時 = n−2 (anomaly 位 12,23,34,45,56,...)
# 定理候選: v₁₁(k_n) = −(n−1) + [n≡1 mod 11]  — 週期 11 = L₅
# 機制: cumulant Bell 係數 (k−1)! 喺 k=12,23,... (=n≡1 mod 11 時可達) 帶 11 因子
#       + 矩 m_j = C(2j,j) + 2^{2j−4}/11 嘅 11-adic 估值 −1 (Lucas: 11|C(2j,j) 時保持)
# 另: 43 出現規律 (m=6 零星, m≥22 穩定) — κ prime 家族裁決
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

def v11(x):
    """11-adic 估值 (負 = 分母)"""
    n = abs(x.numerator); d = x.denominator
    e = 0
    while n % 11 == 0: n //= 11; e += 1
    while d % 11 == 0: d //= 11; e -= 1
    return e

print("== ① v₁₁(k_n) vs −(n−1)+[n≡1 mod 11] (n=1..80) ==")
fails = []
for n in range(1, 81):
    v = v11(k_n[n-1])
    expect = -(n-1) + (1 if n % 11 == 1 else 0)
    mark = "OK" if v == expect else "FAIL"
    if v != expect: fails.append((n, v, expect))
    if n in (11,12,13,22,23,24,33,34,35,44,45,56,67,78) or n <= 6:
        print(f"  n={n:>2}: v₁₁ = {v:>3}  expect {expect:>3}  {mark}")
print(f"\n  驗證 n=1..80: {'ALL PASS' if not fails else str(fails)}")

print("\n== ② 11-週期 anomaly 位置: n ≡ 1 mod 11 (n≥12) ==")
anom = [n for n in range(12, 81) if n % 11 == 1]
print(f"  anomaly 位: {anom}  (等差 11 = L₅)")

print("\n== ③ 43 (N_d−1) 出現規律 (κ_{2m}) ==")
# 由 03 輸出: m=6 (零星), m=22..30 (穩定) — 檢查 m=16..21
def moments_to_cumulants(m):
    res = []
    for n in range(1, len(m)+1):
        kappa = m[n-1]
        for j in range(1, n):
            kappa -= math.comb(n-1, j-1)*res[j-1]*m[n-1-j]
        res.append(kappa)
    return res
NMOM = 60
mom = [math.comb(2*n, n) for n in range(1, NMOM+1)]
kap = moments_to_cumulants(mom)
for m in range(1, 31):
    v = kap[2*m-1]
    has43 = v % 43 == 0
    has11 = v % 11 == 0
    print(f"  m={m:>2} (κ_{2*m:>2}): 43={'Y' if has43 else '.'}  11={'Y' if has11 else '.'}")

print("\n== ④ σ_m 分母 = 2^a·3^b·... (Rayleigh) vs κ prime — 來源分解 ==")
print("  κ_{2m} = (2m)!·2^{2m}·σ_m/m ⟹ prime 集 = (2m)! 嘅 prime ∪ σ_m 分子 prime")
print("  (2m)! prime ≤ 2m; σ_m 分子可帶 >2m 大質數 (229, 1607, 101369, ...)")
print("  ⟹ 冇乾淨家族: 新大質數隨 m 出現, 11/43 係低階命中 (O194 R3 同判決)")
