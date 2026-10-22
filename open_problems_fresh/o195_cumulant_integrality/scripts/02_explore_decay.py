#!/usr/bin/env python3
# O195 scripts/02 — 探索: 幾乎整數 dev 衰減率 + κ 因式分解 prime 結構 + k₁₂ 11-anomaly
# 精確有理 (Fraction) 全鏈累積量 k_n 到 n=80; 提取 k_odd 主導整數 D_n 同 dev;
# 掃描衰減率閉式候選; κ_{2m} prime 家族; k_n 分母 11 指數逐 n 表
# 規則: 零新常數, 精確算術, 唔 import 被驗證 script

from fractions import Fraction as F
import math, sys

NORD = 81  # k_1..k_80

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
    if 2*m < NORD:
        i0[2*m] = F(1, math.factorial(m)**2)
e4m1 = [F(0)]*NORD
for n in range(1, NORD):
    e4m1[n] = F(4)**n / math.factorial(n)
A = smul(e2, i0)
B = [e4m1[k]/176 for k in range(NORD)]
AB = [A[k]+B[k] for k in range(NORD)]
u = [F(0)] + AB[1:]
K = sln1p(u)
k_n = [K[n]*math.factorial(n) for n in range(1, NORD)]  # k_1..k_80

print("== 全鏈 k_n: 奇數階主導整數 + dev ==")
print(f"{'n':>3} {'k_n (float)':>22} {'D=round':>16} {'dev_abs=|k-D|':>18} {'dev_rel':>12}")
D_odd = {}
for n in range(5, 61, 2):
    kn = k_n[n-1]
    fv = float(kn)
    D = round(fv)
    dev = abs(fv - D)
    D_odd[n] = (kn, D, dev)
    print(f"{n:>3} {fv:>22.10f} {D:>16,d} {dev:>18.3e} {dev/abs(D) if D else 0:>12.3e}")

print("\n== dev 衰減率 dev(n+2)/dev(n) ==")
ns = sorted(D_odd)
prev = None
for n in ns:
    if prev is not None:
        r = D_odd[n][2] / D_odd[prev][2]
        print(f"  dev({prev}→{n}): {r:.6f}   (1/44={1/44:.6f}, (j1/j2)^2={0.1897:.4f})")
    prev = n

print("\n== 主導整數 D_n 因式分解 ==")
for n in ns:
    D = D_odd[n][1]
    if D == 0: continue
    dd, fac = abs(D), []
    for p in range(2, int(math.isqrt(dd))+1):
        if dd % p == 0:
            c = 0
            while dd % p == 0: dd //= p; c += 1
            fac.append(f"{p}^{c}" if c > 1 else f"{p}")
    if dd > 1: fac.append(f"{dd}")
    print(f"  n={n:>2}: D={D:>16,d} = {'·'.join(fac) if fac else '1'}")

print("\n== k_n 分母: 2/11 指數逐 n (n=1..60) ==")
for n in range(1, 61):
    d = k_n[n-1].denominator
    e2_, e11_ = 0, 0
    dd = d
    while dd % 2 == 0: dd //= 2; e2_ += 1
    while dd % 11 == 0: dd //= 11; e11_ += 1
    tag = ""
    if dd != 1: tag = f" EXTRA {dd}"
    print(f"  n={n:>2}: den={d:<28} 2^{e2_}·11^{e11_}{tag}")

print("\n== κ_{2m} (arcsine 偶累積量) 因式分解 m=1..25 ==")
def moments_to_cumulants(m):
    res = []
    for n in range(1, len(m)+1):
        kappa = m[n-1]
        for j in range(1, n):
            kappa -= math.comb(n-1, j-1)*res[j-1]*m[n-1-j]
        res.append(kappa)
    return res
NMOM = 50
mom = [math.comb(2*n, n) for n in range(1, NMOM+1)]
kap = moments_to_cumulants(mom)
primes_seen = set()
for m in range(1, 26):
    v = abs(kap[2*m-1])
    dd, fac = v, []
    for p in range(2, int(math.isqrt(dd))+1):
        if dd % p == 0:
            c = 0
            while dd % p == 0: dd //= p; c += 1
            fac.append(f"{p}^{c}" if c > 1 else f"{p}")
    if dd > 1: fac.append(f"{dd}")
    for tok in fac:
        p = int(tok.split('^')[0])
        primes_seen.add(p)
    print(f"  κ_{2*m:>2} = {v:>22,d} = {'·'.join(fac) if fac else '1'}")
print("  primes seen:", sorted(primes_seen))
