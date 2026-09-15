#!/usr/bin/env python3
# O196 scripts/05 — T2 閉式定案: α 指數 + 兩根干涉
# 由精確 Fraction k_n 直接計: k_n·Rⁿ/n! ~ n^{−α} ⟹ log-log 斜率 = −α
# 殘差來源: δ=±1 兩根等距 |r₁|=|r₂|=R, 干涉項 ~ cos 振盪
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

# R = δ=±1 根 (O195 已驗證 |t|=1.202532009265)
R = 1.202532009265

print("== T2b': α 指數 (log-log 斜率) ==")
# s_n = ln|k_n·Rⁿ/n!| ~ −α·ln n + c   (k_n 奇 n 先有值; k_odd 全體)
print("  n    ln|k_n Rⁿ/n!|    Δ/Δln n (局部 α)")
alphas = []
ns = list(range(9, 70, 2))
lnn = [math.log(n) for n in ns]
lns = [math.log(abs(float(k_n[n-1])) * R**n / math.factorial(n)) for n in ns]
for i in range(2, len(ns)-1):
    # 三點斜率
    a = (lns[i+1]-lns[i-1])/(lnn[i+1]-lnn[i-1])
    alphas.append(-a)
    if ns[i] % 8 == 1 or ns[i] > 61:
        print(f"  {ns[i]:>2}  {lns[i]:>14.5f}  {a:>8.3f}")
alpha_tail = alphas[-5:]
check("T2b α → 0 (log-log 斜率尾端 < 0.05)", max(abs(x) for x in alpha_tail) < 0.05,
      f"尾端 α = {[round(x,3) for x in alpha_tail]}")

print("\n== T2c: 殘差結構 — dev vs n (兩根干涉?) ==")
print("  n    dev=(k_{n+2}/k_n)/((n+1)(n+2)R⁻²)−1   dev·n")
devs = []
for n in range(7, 60, 2):
    fr = abs(k_n[n+1]/k_n[n-1])
    r = float(fr.numerator)/float(fr.denominator)
    pred = (n+1)*(n+2)/R**2
    dev = r/pred - 1
    devs.append(dev)
    if n % 8 == 1 or n > 53:
        print(f"  {n:>2}  {dev:>+14.6e}  {dev*n:>+10.3f}")
# 振盪檢查: dev 符號變化次數 (兩根干涉 ⟹ 振盪, 唔係單調 1/n)
signs = [1 if d > 0 else -1 for d in devs]
flips = sum(1 for i in range(1, len(signs)) if signs[i] != signs[i-1])
check("T2c dev 符號振盪 ≥ 2 次 (兩根干涉, 唔係單調 1/n)", flips >= 2, f"符號翻轉 {flips} 次 (n=7..59, {len(devs)} 點)")
# 唔係 1/n 單調: 尾端 |dev·n| 唔收斂去常數
dnt = [abs(d*n) for d, n in zip(devs[-4:], range(53, 60, 2))]
check("T2c' |dev·n| 尾端唔收斂 (排除純 1/n 修正)", max(dnt) > 2*min(dnt), f"尾端 dev·n = {[round(x,2) for x in dnt]}")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
