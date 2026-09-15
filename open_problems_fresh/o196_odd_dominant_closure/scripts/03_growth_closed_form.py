#!/usr/bin/env python3
# O196 scripts/03 — T2: D_n 增長閉式
# O195 B3: D_{n+2}/D_n vs (n+1)n·R⁻² obs/pred = 1.043 @ n=45 (🟡 冇閉式)
# 候選修正: k_odd = n![tⁿ]artanh(δ), δ = sinh/(88I₀), 奇異點 δ=±1 |t|=R=1.202532
#   奇異點係 log 分支 (artanh) ⟹ a_n ~ R^{-n}·n^{-1} (Darboux, log 奇異點 n^{-1} 因子)
#   k_n ~ n!·R^{-n}·n^{-1} ⟹ D_{n+2}/D_n ~ (n+2)!·R^{-(n+2)}·(n+2)^{-1} / [n!·R^{-n}·n^{-1}]
#     = (n+1)(n+2)·R^{-2}·n/(n+2) = (n+1)n·R^{-2}  ... 等等, log 奇異點係 -1/2 ln(1-z/R)?
#   重新推: artanh(δ(t)) 喺 δ=1 根 r₁: δ(t)-1 ≈ c(t-r₁) ⟹ artanh ~ -(1/2)ln(1-δ) ~ -(1/2)ln(t-r₁)
#   [tⁿ]ln(t-r₁) = -1/(n·r₁ⁿ) ⟹ a_n ~ (1/2)·1/(n·r₁ⁿ) ⟹ k_n ~ (1/2)·(n-1)!·r₁^{-n}
#   D_{n+2}/D_n ~ (n+1)!·r₁^{-(n+2)} / [(n-1)!·r₁^{-n}] = n(n+1)·R^{-2}
#   但 O195 B3 實測 1.043 @ n=45 (用 (n+1)n·R⁻²)。要 check 係咪 (n+1)(n+2)
#   直接數值: D_n = round(k_odd), 對比兩種 pred
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
K = sln1p(u)  # ln M 係數 (cumulant/n!)
k_n = [K[n]*math.factorial(n) for n in range(1, NORD)]  # κ_n
k_odd = [k_n[n-1] for n in range(1, NORD) if n % 2 == 1]

def rnd(x):
    return (2*x.numerator + x.denominator) // (2*x.denominator)

R = 1.202532009265
R2 = 1/R**2
print(f"R = {R}, R⁻² = {R2:.8f}")
print("\n  n    D_{n+2}/D_n obs   (n+1)n·R⁻²  obs/pred_old  (n+1)(n+2)·R⁻²  obs/pred_new")
old_dev, new_dev = [], []
for n in range(7, 30, 2):  # n=7..29: D_{n+2}/D_n, D_m = round(κ_m)
    Dn = rnd(k_odd[(n-1)//2]); Dn2 = rnd(k_odd[(n+1)//2])
    obs = abs(Dn2/Dn)
    po = (n+1)*n*R2
    pn = (n+1)*(n+2)*R2
    old_dev.append(obs/po); new_dev.append(obs/pn)
    print(f"  {n:>2}  {obs:>14.6f}  {po:>10.4f}  {obs/po:>10.4f}  {pn:>12.4f}  {obs/pn:>10.4f}")

print("\n  n    obs/pred_new  (1 − pred_new/obs)  n·(obs/pred_new − 1)")
for i, n in enumerate(range(7, 30, 2)):
    d = new_dev[i]
    print(f"  {n:>2}  {d:>10.5f}  {1-1/d:>12.5f}  {n*(d-1):>10.4f}")

# 尾端收斂檢查
tail = new_dev[-5:]
conv = all(abs(t-1) < 0.02 for t in tail) and abs(tail[-1]-1) < abs(tail[0]-1)
check("T2a (n+1)(n+2)·R⁻² pred 收斂 → 1 (尾端 |dev| < 2%)", conv, f"尾={tail}")
# 舊 pred 殘差係咪 1/n 形式? 1 − obs/pred_old vs 2/n
print("\n  1 − obs/pred_old vs 2/n:")
for i, n in enumerate(range(7, 30, 2)):
    d = old_dev[i]
    print(f"  n={n:>2}: 1−obs/pred_old = {1-d:>8.4f}, 2/n = {2/n:>8.4f}, ratio = {(1-d)/(2/n):>6.3f}")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
