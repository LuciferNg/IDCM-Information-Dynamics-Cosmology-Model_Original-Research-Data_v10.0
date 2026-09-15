#!/usr/bin/env python3
# O196 scripts/04 — T2 閉式判定: (n+1)(n+2)·R⁻² vs (n+1)n·R⁻²
# 精確 Fraction ratio (唔 round) + 奇異點指數 α 檢驗
# [tⁿ]artanh(δ) ~ c·R^{−n}·n^{−α} ⟹ k_n ~ n!·R^{−n}·n^{−α}
#   α=0 ⟹ k_{n+2}/k_n ~ (n+1)(n+2)·R⁻²  (數值支持)
#   α=1 ⟹ k_{n+2}/k_n ~ (n+1)n·R⁻²      (O195 B3 舊假設)
import mpmath as mp
from fractions import Fraction as F
import math

mp.mp.dps = 50
PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

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
k_n = [K[n]*math.factorial(n) for n in range(1, NORD)]

R = mp.mpf("1.202532009265")
R2 = 1/R**2

print("== T2a: 精確 ratio k_{n+2}/k_n (冇 round) ==")
print("  n    k_{n+2}/k_n        (n+1)(n+2)R⁻²   dev    (n+1)n·R⁻²    dev")
devs_new, devs_old = [], []
for n in range(7, 60, 2):
    fr = abs(k_n[n+1]/k_n[n-1])
    r = mp.mpf(fr.numerator)/mp.mpf(fr.denominator)
    pn = (n+1)*(n+2)*R2
    po = (n+1)*n*R2
    dn = float(abs(r - pn)/pn); do = float(abs(r - po)/po)
    devs_new.append(dn); devs_old.append(do)
    if n % 6 == 1 or n > 55:
        print(f"  {n:>2}  {mp.nstr(r, 12):>16}  {mp.nstr(pn, 10):>12}  {dn:>7.2e}  {mp.nstr(po,10):>10}  {do:>7.2e}")
mn = max(devs_new); mo = min(devs_old)
check("T2a (n+1)(n+2)R⁻² 最大 dev < 0.1%", mn < 1e-3, f"max_dev_new={mn:.2e}")
check("T2a' (n+1)(n+2) 遠勝 (n+1)n (新 min dev 比舊 max 細)", mn < mo/10, f"new_max={mn:.2e} vs old_min={mo:.2e}")

print("\n== T2b: 奇異點指數 α (mpmath, artanh(δ) 係數) ==")
# δ(t) = sinh(2t)/(88·I₀(2t)), a_n = [tⁿ]artanh(δ)
# 高精度 Taylor 係數
def taylor_artanh_delta(N):
    """返回 a_n = [tⁿ]artanh(δ(t)), n=1..N, mpmath"""
    # δ 嘅 Taylor 係數 d_n: δ(t) = Σ d_n tⁿ
    # sinh(2t) = Σ 2^{2m+1} t^{2m+1}/(2m+1)!
    # I₀(2t) = Σ t^{2m}/(m!)²
    # 88·I₀(2t)·δ(t) = sinh(2t) ⟹ 卷積求 d_n
    d = [mp.mpf(0)]*(N+1)
    I0 = [mp.mpf(0)]*(N+1); S = [mp.mpf(0)]*(N+1)
    for m in range(N//2+2):
        if 2*m <= N: I0[2*m] = mp.mpf(1)/mp.factorial(m)**2
    for m in range(N//2+2):
        if 2*m+1 <= N: S[2*m+1] = mp.mpf(2)**(2*m+1)/mp.factorial(2*m+1)
    # 88·(I0*d) = S ⟹ d = S/(88·I0) 卷積除法 (I0[0]=1)
    # d_n = (S_n − 88·Σ_{k<n} I0_{n−k}·d_k)/88
    for n in range(1, N+1):
        acc = S[n] - 88*sum(I0[n-k]*d[k] for k in range(1, n))
        d[n] = acc/88
    # artanh(δ) = δ + δ³/3 + δ⁵/5 + ... (δ 奇函數 ⟹ 只奇次)
    # a_n = Σ_{k odd} δ^k 嘅係數 /k
    a = [mp.mpf(0)]*(N+1)
    dpow = [mp.mpf(0)]*(N+1)
    dpow[0] = 1
    # 迭代: 手動冪
    def conv(x, y):
        out = [mp.mpf(0)]*(N+1)
        for kk in range(N+1):
            out[kk] = sum(x[i]*y[j] for i in range(N+1) for j in range(N+1) if i+j == kk)
        return out
    p = [mp.mpf(0)]*(N+1); p[0] = 1
    for k in range(1, N+1, 2):
        p = conv(p, d)
        p = conv(p, d)  # p = δ^k
        for n in range(1, N+1):
            a[n] += p[n]/k
    return a

a = taylor_artanh_delta(79)
# α 檢驗: n·(a_n/a_{n+2})·R² → ?
print("  n    a_{n+2}/a_n·(n+2)(n+1)... 直接比 a_n vs R^{−n}·n^{−α}")
print("  n    a_n·Rⁿ·n     a_n·Rⁿ       (α=1 應收斂, α=0 應發散)")
rat1, rat0 = [], []
for n in range(7, 60, 2):
    a_n = a[n]
    v1 = abs(a_n * R**n * n)    # α=1 檢驗: a_n·Rⁿ·n → const?
    v0 = abs(a_n * R**n)        # α=0: a_n·Rⁿ → const?
    rat1.append(v1); rat0.append(v0)
    if n % 6 == 1 or n > 55:
        print(f"  {n:>2}  {mp.nstr(v1, 9):>14}  {mp.nstr(v0, 9):>12}")
s1 = [abs(rat1[i+1]-rat1[i])/rat1[i] for i in range(len(rat1)-1)]
s0 = [abs(rat0[i+1]-rat0[i])/rat0[i] for i in range(len(rat0)-1)]
check("T2b α=1 (a_n·Rⁿ·n 收斂, 尾端相對變化 < 1%)", max(s1[-8:]) < 0.01,
      f"尾端變化 max={max(s1[-8:]):.4f}")
check("T2b' α=0 (a_n·Rⁿ) 唔收斂 (變化 ≫ α=1)", max(s0[-8:]) > 5*max(s1[-8:]),
      f"α0變化={max(s0[-8:]):.4f} vs α1={max(s1[-8:]):.4f}")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
