#!/usr/bin/env python3
# O195 scripts/03 — 開放項 2+3: k₁₂ 分母 11 指數 anomaly + κ_{2m} 因式分解 prime 結構
# ① k_n 分母 11 指數逐 n (n=1..60): 搵 anomaly 位 + gcd 約簡機制
#    (O194 R1: 分母只含 2,11; n=12 得 11^11 而唔係 11^12)
# ② κ_{2m} 因式分解 (m=1..30): prime 結構, 睇有冇家族
#    (11 = L₅, 43 = N_d−1 零星命中 → 家族掃描)
# ③ σ_m 分母定理延伸: (2m)!·2^{2m}/m 嘅 prime 結構 vs κ_{2m}
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

def factor_small(n, plist=(2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53)):
    """只分解 plist 內嘅 prime; 餘下大質數照列 (唔 trial 到 sqrt — 大數太快)"""
    n = abs(n)
    fac = {}
    for p in plist:
        while n % p == 0:
            fac[p] = fac.get(p, 0) + 1
            n //= p
    if n > 1: fac[n] = 1
    return fac

print("== ① k_n 分母 11 指數 (n=1..60) + 分子 11 指數 (anomaly 追蹤) ==")
print(f"{'n':>3} {'den 2^':>4} {'den 11^':>6} {'num 11^':>7}  anomaly?")
prev = None
for n in range(1, 61):
    kn = k_n[n-1]
    df = factor_small(kn.denominator)
    nf = factor_small(kn.numerator)
    e2d, e11d = df.get(2, 0), df.get(11, 0)
    e11n = nf.get(11, 0)
    # 期望: den 11 指數 = 累計最大? (O194: n=12 得 11^11 vs 11^12)
    tag = ""
    if n == 12: tag = " ← O194 anomaly 位"
    if n in (11, 13, 14): tag += " (鄰近對照)"
    print(f"{n:>3} {e2d:>4} {e11d:>6} {e11n:>7}{tag}")

print("\n== ② κ_{2m} 因式分解 (m=1..30) ==")
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
primes_seen = {}
for m in range(1, 31):
    v = kap[2*m-1]
    fac = factor_small(v)
    for p in fac:
        primes_seen.setdefault(p, []).append(m)
    facs = "·".join(f"{p}^{e}" if e > 1 else f"{p}" for p, e in sorted(fac.items()))
    print(f"  κ_{2*m:>2} = {v:>26,d} = {facs if facs else '1'}")

print("\n== ③ prime 出現表 (prime → 邊個 m 出現) ==")
for p in sorted(primes_seen):
    print(f"  {p:>4}: m = {primes_seen[p]}")

# 11 同 43 嘅出現
print("\n== ④ 結構命中檢查 ==")
print("  11 = L₅, 43 = N_d−1, 19 = ? 17 = F_proj, 7 = L₄, 5 = F₅, 3 = N_gen")
print("  κ 序列: 2, −6, 80, −2310, 114912, −8741040, 943113600, −136984998150")
print("  因式分解:")
for m in range(1, 9):
    v = kap[2*m-1]
    print(f"    κ_{2*m} = {v} = {'·'.join(f'{p}^{e}' if e>1 else str(p) for p,e in sorted(factor_small(v).items()))}")

# ⑤ σ_m = ±m·κ_{2m}/((2m)!·2^{2m}) — 分母 prime 結構 (Rayleigh)
print("\n== ⑤ Rayleigh σ_m 分母結構 m=1..12 ==")
for m in range(1, 13):
    num = m * kap[2*m-1]
    den = math.factorial(2*m) * (2**(2*m))
    s = F(num, den)
    df = factor_small(s.denominator)
    nf = factor_small(s.numerator)
    dstr = "·".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(df.items())) or "1"
    nstr = "·".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(nf.items())) or "1"
    print(f"  σ_{m:>2} = {s}  den={dstr}  num={nstr}")
