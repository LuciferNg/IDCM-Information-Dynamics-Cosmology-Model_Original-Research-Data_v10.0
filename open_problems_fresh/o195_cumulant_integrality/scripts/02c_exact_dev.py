#!/usr/bin/env python3
# O195 scripts/02c — 精確 dev 分析: k_odd 幾乎整數嘅 dev 衰減率閉式追擊
# 用 Fraction 精確計算 dev_abs = |k_n − round(k_n)| (無 float 誤差),
# 計 dev 衰減率序列, 對比閉式候選: (j1/j2)^2, 1/44, 4/j1^2, (2/j1)^2·(j1/j2)^2, phi^-2 ...
# 同時測試: k_odd 主導整數 D_n 增長率 vs (2m)^2 級 + 差 5/3 觀察
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
    return (x.numerator + x.denominator//2) // x.denominator

# 精確 dev
print("== k_odd 精確 dev (Fraction) ==")
data = {}
for n in range(5, 61, 2):
    kn = k_n[n-1]
    D = round_frac(kn) * (1 if kn.numerator >= 0 else 1)  # round 已經帶符號
    # round_frac 對負數: numerator//denominator 係 floor; 用 round 語義
    q = kn.numerator / kn.denominator
    D = round(q)
    dev = abs(kn - D)  # Fraction 精確
    data[n] = (D, dev)
    print(f"  n={n:>2}: D={D:>24,d}  dev={dev}")

print("\n== dev_abs 衰減率 r(n) = dev(n+2)/dev(n) ==")
ns = sorted(data)
for i in range(len(ns)-1):
    n1, n2 = ns[i], ns[i+1]
    r = data[n2][1] / data[n1][1]
    rf = float(r)
    print(f"  r({n1}→{n2}) = {rf:.8f}   |k| ratio = {float(abs(data[n2][0]))/float(abs(data[n1][0])):.4f}")

# 候選閉式
print("\n== 候選閉式對比 ==")
j1 = 2.404825557695773
j2 = 5.520078110286311
cand = {
    "(j1/j2)^2": (j1/j2)**2,
    "1/44": 1/44,
    "(2/j1)^2=4/j1^2": 4/j1**2,
    "(j1/j2)^4": (j1/j2)**4,
    "1/44^2": 1/44**2,
    "phi^-2": ((5**0.5-1)/2)**2,
    "(2/j1)^2·(j1/j2)^2": (2/j1)**2*(j1/j2)**2,
}
for name, v in cand.items():
    print(f"  {name:<26} = {v:.8f}")

print("\n== D_n 增長率 vs (2m)^2 級觀察 ==")
ns = sorted(data)
for i in range(len(ns)-1):
    n1, n2 = ns[i], ns[i+1]
    D1, D2 = abs(data[n1][0]), abs(data[n2][0])
    if D1 == 0: continue
    ratio = D2/D1
    sq = ratio**0.5
    print(f"  n={n1:>2}→{n2:>2}: D ratio = {ratio:>10.3f}  sqrt = {sq:.5f}  (n≈{n2})")
