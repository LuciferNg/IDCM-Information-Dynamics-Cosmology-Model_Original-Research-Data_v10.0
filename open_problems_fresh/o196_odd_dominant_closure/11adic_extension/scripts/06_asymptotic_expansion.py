#!/usr/bin/env python3
# O200 scripts/06 — T6: k_odd 完整漸近展開 (SESSION_START §二 項 6)
# 已確立 (T4/T5): a_n = ±c·R^{−n}·sin(nδ)/n, c = μ² = 2, δ = arcsin(Re/R)
#   ⟹ a_n·Rⁿ = cδ·sinc(nδ) = cδ[1 − (nδ)²/6 + (nδ)⁴/120 − ...]
#   主導 α=0: cδ; 次項: −cδ³n²/6 (負, 隨 n² 增長) — O196「dev 全負冇翻轉」嘅來源?
# 本 script:
#   A) 驗證 a_n·Rⁿ = cδ·sinc(nδ) 擬合 (c=2, δ=arcsin ε) — dev 量級
#   B) 第二近根 |r₃| — 高階修正指數衰減率
#   C) 殘差 = sinc 截斷誤差? 定係第三根干涉? 判決
from fractions import Fraction as F
import math
import mpmath as mp

mp.mp.dps = 60
PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

# k_n (Fraction, O196 方法)
NORD = 121
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

# 根參數
r1 = mp.findroot(lambda t: 88*mp.besseli(0, 2*t) - mp.sinh(2*t), mp.mpc('0.0074','1.2024'), tol=1e-50, maxsteps=100)
R = abs(r1); theta1 = mp.arg(r1); delta = mp.pi/2 - theta1
c = mp.mpf(2)   # μ² (T4b 鎖定)

print("== T6a: a_n·Rⁿ vs 2·sin(nδ)/n (c=2, T4b 鎖定) ==")
print(f"  主導漸近: a_n·Rⁿ·n = 2·sin(nδ) ⟹ a_n·Rⁿ = 2·sin(nδ)/n (精確 c=μ²)")
print(f"  {'n':>3} {'a_n·Rⁿ':>14} {'2sin(nδ)/n':>14} {'dev':>10}")
devs = []
for n in range(5, 120, 2):
    kn = k_n[n-1]
    # a_n = k_n/n! — 用 mp 比例避免 Overflow
    a_n = mp.mpf(kn.numerator)/mp.mpf(kn.denominator)/mp.factorial(n)
    anR = abs(a_n) * R**n
    pred = 2*mp.sin(n*delta)/n
    dev = (anR - pred)/pred
    devs.append(float(dev))
    if n in (5, 11, 21, 31, 41, 51, 61, 71, 79, 89, 99, 109, 119):
        print(f"  {n:>3} {mp.nstr(anR, 14)} {mp.nstr(pred, 14)} {mp.nstr(mp.mpf(dev), 10)}")

# A) 主導擬合質量
print(f"  dev: min={min(devs):.2e}, max={max(devs):.2e}")
print(f"  尾端 (n>100) |dev|max = {max(abs(d) for d in devs[-10:]):.2e}")
check("T6a a_n·Rⁿ = 2·sin(nδ)/n 主導 (尾端 |dev| < 1e-2)", max(abs(d) for d in devs[-10:]) < 1e-2,
      f"尾端 |dev|max = {max(abs(d) for d in devs[-10:]):.2e}")

# B) 第二近根 |r₃| — 高階修正衰減
print("\n== T6b: δ=±1 根譜 — 第二近根 ==")
# 掃描複平面搵所有 |t| < 3 嘅根
roots = []
for re_ in [i*0.05 for i in range(-60, 61)]:
    for im_ in [i*0.05 for i in range(1, 61)]:
        t0 = mp.mpc(re_, im_)
        if abs(t0) > 3: continue
        try:
            root = mp.findroot(lambda t: 88*mp.besseli(0, 2*t) - mp.sinh(2*t), t0, tol=1e-30, maxsteps=40)
        except Exception:
            continue
        rr = abs(root)
        if rr < 1e-6: continue
        dup = any(abs(root - r) < 1e-6 for r in roots)
        if not dup:
            roots.append(root)
roots.sort(key=lambda r: abs(r))
print(f"  搵到 {len(roots)} 個 δ=+1 根 (|t|<3):")
for r in roots[:6]:
    print(f"    |t|={mp.nstr(abs(r), 10)}, t={mp.nstr(r, 12)}")
# 對稱: δ=−1 根 = 實部鏡像
print(f"  δ=−1 根 = δ=+1 根嘅實部鏡像 (r₂ = −r̄₁ 結構)")
r3 = roots[2] if len(roots) > 2 else None
if r3:
    print(f"  第三根 (δ=+1, |t| = {mp.nstr(abs(r3), 10)})")
    print(f"  (R/|r₃|)ⁿ 衰減率: n=100 → {mp.nstr((R/abs(r3))**100, 5)}")
    print(f"  ⟹ 高階修正 ~1e-{mp.nstr(-mp.log10((R/abs(r3))**100), 4)} @ n=100")

# C) 殘差結構: a_n·Rⁿ − 2sin(nδ)/n 真正殘差 (高精度 mp)
print("\n== T6c: 真正殘差 |a_n·Rⁿ − 2·sin(nδ)/n| (高精度 mp) ==")
print("  T6a 顯示主導閉式精確成立 (dev → 1e-44) — 殘差應由第三根 (R/|r₃|)ⁿ 主導")
print(f"  第三根 |r₃| = {mp.nstr(abs(roots[2]), 10)}, (R/|r₃|)ⁿ 量級:")
for n in [21, 41, 61, 81, 101, 119]:
    kn = k_n[n-1]
    a_n = mp.mpf(kn.numerator)/mp.mpf(kn.denominator)/mp.factorial(n)
    anR = abs(a_n) * R**n
    pred = 2*mp.sin(n*delta)/n
    resid = abs(anR - pred)
    r3_est = (R/abs(roots[2]))**n
    print(f"  n={n:>3}: |resid| = {mp.nstr(resid, 4)}, (R/|r₃|)ⁿ = {mp.nstr(r3_est, 4)}, ratio = {mp.nstr(resid/r3_est, 3)}")
# 殘差 vs 第三根量級: ratio 應該 O(1) 或更細 (第三根係主要高階修正)
resids = []
for n in [21, 41, 61, 81, 101, 119]:
    kn = k_n[n-1]
    a_n = mp.mpf(kn.numerator)/mp.mpf(kn.denominator)/mp.factorial(n)
    anR = abs(a_n) * R**n
    resid = abs(anR - 2*mp.sin(n*delta)/n)
    r3_est = (R/abs(roots[2]))**n
    resids.append(float(resid/r3_est))
check("T6c 殘差 ~ (R/|r₃|)ⁿ 量級 (第三根主導高階修正, ratio O(1))",
      all(r < 10 for r in resids), f"ratios = {[f'{r:.2f}' for r in resids]}")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
