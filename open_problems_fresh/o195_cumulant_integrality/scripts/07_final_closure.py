#!/usr/bin/env python3
# O195 scripts/07 — 最終閉合: dev_abs 隨機性檢定 (K-S) + D 增長收斂精度 + 全驗證
# ① dev_abs K-S test vs Uniform[0,0.5) — 隨機性裁決 (唔靠 mean 猜)
# ② D_{n+2}/D_n obs/pred 收斂尾端 (R = δ=1 根 vs j₁/2 兩個候選邊個收斂好)
# ③ artanh(δ) 身份延到 n=59 + 奇異點修正後嘅 B1/B2 重驗
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

def round_frac(x):
    return (2*x.numerator + x.denominator) // (2*x.denominator)

# dev_abs
devs = []
for n in range(5, 61, 2):
    kn = k_n[n-1]
    D = round_frac(kn)
    devs.append(float(abs(kn - D)))

# K-S test vs Uniform[0,0.5): 歸一化到 [0,1]
import statistics
norm = sorted(d / 0.5 for d in devs)
n = len(norm)
ks = max(abs((i+1)/n - v) for i, v in enumerate(norm))
# K-S critical value 0.05: 1.358/sqrt(n) (single-sample, two-sided)
crit = 1.358/math.sqrt(n)
print(f"== K-S test (n={n} 樣本, Uniform[0,1) 對照) ==")
print(f"  D_KS = {ks:.4f}  critical(α=0.05) = {crit:.4f}")
print(f"  判決: {'FAIL to reject Uniform (隨機)' if ks < crit else 'REJECT (有結構)'}")
print(f"  mean = {statistics.mean(devs):.4f} (期望 0.25),  median = {statistics.median(devs):.4f} (期望 0.25)")

# D 增長收斂: R = δ=1 根 |t|=1.202532009265, R⁻² = 0.6915231274
R2a = 0.6915231274    # δ=1 根
R2b = 4/2.404825557695773**2  # 4/j1² = 0.6916602761
print("\n== D_{n+2}/D_n obs/pred 收斂對比 (兩個 R⁻² 候選) ==")
for n in range(7, 47, 2):
    Dn = abs(round_frac(k_n[n-1])); Dn2 = abs(round_frac(k_n[n+1]))
    obs = Dn2/Dn
    pa, pb = (n+1)*n*R2a, (n+1)*n*R2b
    print(f"  n={n:>2}: obs={obs:>10.3f}  obs/pred(δ1根)={obs/pa:>8.4f}  obs/pred(4/j1²)={obs/pb:>8.4f}")

# artanh 身份延到 n=59
print("\n== artanh(δ) 身份 n=3..59 (延長驗證) ==")
sinh = [F(0)]*NORD
for m in range(NORD//2):
    k = 2*m+1
    if k < NORD: sinh[k] = F(2)**k / math.factorial(k)
def sdiv(num, den):
    n = len(num)
    res = [F(0)]*n
    for k in range(n):
        s = num[k] - sum(res[j]*den[k-j] for j in range(k))
        res[k] = s / den[0]
    return res
inv88i0 = sdiv([F(1)] + [F(0)]*(NORD-1), [88*x for x in i0])
delta = smul(sinh, inv88i0)
art = [F(0)]*NORD
pk = delta[:]
for k in range(1, NORD, 2):
    if k > 1: pk = smul(smul(pk, delta), delta)
    for i in range(NORD):
        art[i] += pk[i] / k
kap_art = [art[n]*math.factorial(n) for n in range(1, NORD)]
bad = [n for n in range(3, 60, 2) if k_n[n-1] != kap_art[n-1]]
print(f"  {'ALL PASS n=3..59' if not bad else f'FAIL: {bad}'}")
