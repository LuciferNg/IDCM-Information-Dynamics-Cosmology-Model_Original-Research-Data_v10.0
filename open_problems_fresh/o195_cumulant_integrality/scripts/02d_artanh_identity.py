#!/usr/bin/env python3
# O195 scripts/02d — 結構身份驗證: k_odd = artanh(δ) 累積量 + dev 真正行為
# ① ΔK(t) = ln(1+δ), δ = sinh(2t)/(88·I₀(2t)): 奇部 artanh(δ) = ½ln((1+δ)/(1−δ))
#    ⟹ k_odd (n≥3, arcsine 奇累積量=0) = (n)!·[tⁿ] artanh(δ) — 直接驗證
# ② dev_abs float 值 + dev_rel + |k| 增長, 睇「幾乎整數」喺 n≥21 嘅真實行為
# ③ D_n 二階差 5.5 = L₅/2 驗證
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

# arcsine 累積量 κ (偶序列已知整數, 奇 n≥3 全部 0)
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
kap = moments_to_cumulants(mom)  # κ_1..κ_60

# 驗證: 奇數 n≥3, k_n == Δk_n (κ_n = 0)
print("== ① arcsine 奇累積量 κ_odd (n=1..30) ==")
odd_zero = all(kap[n-1] == 0 for n in range(3, 31, 2))
print(f"  κ_3,κ_5,...,κ_29 全零: {odd_zero}")
print(f"  κ_1 = {kap[0]}")

# ② 獨立路徑: artanh(δ) = ½ln((1+δ)/(1−δ)) 累積量
# δ(t) = sinh(2t)/(88·I₀(2t)) — sinh 係數 2^{2m+1}/(2m+1)!
sinh = [F(0)]*NORD
for m in range(NORD//2):
    k = 2*m+1
    if k < NORD: sinh[k] = F(2)**k / math.factorial(k)
# δ = sinh / (88·I₀): 用級數除法
def sdiv(num, den):
    n = len(num)
    res = [F(0)]*n
    for k in range(n):
        s = num[k] - sum(res[j]*den[k-j] for j in range(k))
        res[k] = s / den[0]
    return res
inv88i0 = sdiv([F(1)] + [F(0)]*(NORD-1), [88*x for x in i0])
delta = smul(sinh, inv88i0)  # δ(t) Taylor
# artanh(δ) = δ + δ³/3 + δ⁵/5 + ...
art = [F(0)]*NORD
p = [F(1)] + [F(0)]*(NORD-1)
for k in range(1, NORD, 2):   # 只奇次冪
    p = smul(p, delta) if k > 1 else delta[:]
    # p = δ^k (要用冪, 唔係乘 delta 一次)
    for i in range(NORD):
        art[i] += p[i] / k
    # 下一冪
    if k < NORD-2:
        p = smul(p, delta)
print("\n== ② artanh(δ) 奇部累積量 vs 全鏈 k_odd ==")
kap_art = [art[n]*math.factorial(n) for n in range(1, NORD)]
# 注意 art 係 ΔK_odd 嘅 Taylor 係數 (未乘 n!), art[n] = [tⁿ]ΔK_odd
match = True
for n in range(1, 41):
    if n % 2 == 0: continue
    # k_n (全鏈) = κ_n + Δk_n; κ_odd(n≥3)=0 ⟹ k_n = Δk_n = n!·[tⁿ]art
    if n == 1:
        # k_1 = κ_1 + Δk_1 = 2 + Δk_1
        expected = kap[0] + kap_art[0]
        if k_n[0] != expected: match = False; print(f"  MISMATCH n=1: {k_n[0]} vs {expected}")
    else:
        if k_n[n-1] != kap_art[n-1]:
            match = False
            print(f"  MISMATCH n={n}: k_n={k_n[n-1]} vs art={kap_art[n-1]}")
print(f"  artanh(δ) 身份: k_odd = n![tⁿ]artanh(δ) {'PASS (n=3..39 全中)' if match else 'FAIL'}")

# ③ dev 真正行為 (float)
print("\n== ③ dev_abs / dev_rel / |k| 真實行為 ==")
print(f"{'n':>3} {'dev_abs':>12} {'dev_rel':>12} {'|k| float':>14}")
devs = {}
Ds = {}
for n in range(5, 51, 2):
    kn = k_n[n-1]
    q = float(kn)
    D = round(q)
    dev = abs(q - D)
    devs[n] = dev; Ds[n] = D
    print(f"{n:>3} {dev:>12.6e} {dev/abs(D) if D else 0:>12.6e} {abs(q):>14.6e}")

print("\n== ④ D_n 增長率二階差 (收斂 5.5 = L₅/2?) ==")
ratios = []
for n in range(5, 49, 2):
    ratios.append(Ds[n+2]/Ds[n])
diffs = [ratios[i+1]-ratios[i] for i in range(len(ratios)-1)]
diffs2 = [diffs[i+1]-diffs[i] for i in range(len(diffs)-1)]
for i, d in enumerate(diffs2[2:], start=2):
    print(f"  n={5+2*i}: Δ²(D-ratio) = {d:.4f}")
print(f"  L₅/2 = {11/2}, B+1.5 = {5.5}")

# ⑤ 對比: δ 極點位置 = I₀ 零點 i·j_k/2 — artanh 奇異點衰減率
print("\n== ⑤ artanh(δ) 最近奇異點: 88I₀ = ±sinh 根 + I₀ 零點 ==")
# I₀(2t)=0 ⟺ 2t = i j_k ⟺ t = i j_k/2, j₁ = 2.4048
j1 = 2.404825557695773
print(f"  I₀ 首零點極點: |t| = j₁/2 = {j1/2:.6f}  ⟹ 係數衰減 ~ (j₁/2)^n = {j1/2:.6f}^n")
# artanh 喺 δ=1: 88I₀(2x) = sinh(2x) 實根 (大 x)
from math import *
def I0(x):
    s = 0.0
    for k in range(60):
        s += (x/2)**(2*k)/math.factorial(k)**2
    return s
x = 100.0
while 88*I0(x) > math.sinh(x): x += 1
print(f"  88I₀=sinh 首實根 (δ=1): x ≈ {x} (artanh 對數奇異點)")
