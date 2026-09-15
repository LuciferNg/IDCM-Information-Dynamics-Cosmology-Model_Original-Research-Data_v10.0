#!/usr/bin/env python3
# O196 scripts/06 — T2 奇異點指數定案 (精確 a_n = k_n/n! = [tⁿ]artanh(δ))
# a_n = k_n/n! (Fraction 精確), 檢驗:
#   log 奇異點: a_n ~ c·R^{−n}/n        ⟹ a_n·Rⁿ·n → const
#   α=0:        a_n ~ c·R^{−n}          ⟹ a_n·Rⁿ → const
#   α>0:        a_n ~ c·R^{−n}·n^{−α}   ⟹ 兩者都發散/收斂慢
from fractions import Fraction as F
import math

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
a_n = [float(k_n[n-1].numerator)/float(k_n[n-1].denominator)/math.factorial(n) for n in range(1, NORD)]

R = 1.202532009265
print("== a_n·Rⁿ·n (log 奇異點應收斂) vs a_n·Rⁿ (α=0 應收斂) ==")
print("  n    a_n·Rⁿ·n      a_n·Rⁿ")
vals_n, vals_0 = [], []
for n in range(5, 80, 2):
    an = abs(a_n[n-1])
    v_n = an * R**n * n
    v_0 = an * R**n
    vals_n.append(v_n); vals_0.append(v_0)
    if n % 10 == 1 or n > 69:
        print(f"  {n:>2}  {v_n:>12.6f}  {v_0:>10.6f}")

# 相對變化 (尾端 10 點)
def relvar(v):
    t = v[-10:]
    return max(abs(t[i+1]-t[i])/t[i] for i in range(len(t)-1))
rv_n = relvar(vals_n); rv_0 = relvar(vals_0)
check("T2 log 奇異點 (a_n·Rⁿ·n 收斂, 尾端變化 < 2%)", rv_n < 0.02, f"relvar={rv_n:.4f}")
check("T2' α=0 (a_n·Rⁿ) 唔收斂 (變化 ≫ log 模型)", rv_0 > 5*rv_n, f"relvar0={rv_0:.4f} vs relvar_n={rv_n:.4f}")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
