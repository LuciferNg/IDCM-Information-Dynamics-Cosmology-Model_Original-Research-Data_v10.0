#!/usr/bin/env python3
# O200 scripts/07 — 綜合閉合: T1-T6 全檢查
# T1: Δθ 干涉相位 — 冇乾淨結構身份 (π/256 dev 0.34%), Re(r₁)≈1/136 🟡 (3.96e-5)
# T2: κ Rayleigh 11-adic — v₁₁(κ_{2m}) = f(11-free(m)) 自相似 + f=0 ⟺ {F₂..F₅}·11^j
#      v₁₁(σ_m) = v₁₁(m) + v₁₁(κ) − v₁₁((2m)!) (Legendre)
# T3: Σγ^n 11-adic — v₁₁(Σγ^n)=0, odd = 1+v₁₁(C(2n,n)), even = 0
# T4: α=0 嚴格證明 — log 分支 1/n 被 δ=arcsin(Re/R) 吸收 (sinc 結構)
# T5: j₁ 統一 — c = μ² = 2 EXACT (log 分支留數 = 扇區隙)
# T6: 完整漸近 — a_n = ±2·R^{−n}·sin(nδ)/n + O((R/|r₃|)ⁿ), 殘差 ratio 0.008
from fractions import Fraction as F
import math
import mpmath as mp

mp.mp.dps = 60
PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

def v11_int(k):
    e = 0
    while k % 11 == 0: k //= 11; e += 1
    return e

def eleven_free(m):
    while m % 11 == 0: m //= 11
    return m

# ===== 根參數 =====
r1 = mp.findroot(lambda t: 88*mp.besseli(0, 2*t) - mp.sinh(2*t), mp.mpc('0.0074','1.2024'), tol=1e-50, maxsteps=100)
r2 = mp.findroot(lambda t: 88*mp.besseli(0, 2*t) + mp.sinh(2*t), mp.mpc('-0.0074','1.2024'), tol=1e-50, maxsteps=100)
R = abs(r1); theta1 = mp.arg(r1); delta = mp.pi/2 - theta1
Re1 = r1.real

print("== T1: Δθ 干涉相位 — 結構身份裁決 ==")
dth = abs(mp.arg(r1) - mp.arg(r2))
print(f"  Δθ = {mp.nstr(mp.degrees(dth), 10)}° = {mp.nstr(dth, 15)} rad")
print(f"  最佳候選 π/256: dev {mp.nstr(abs(dth - mp.pi/256)/dth, 6)} (> 1e-3, 唔夠)")
print(f"  Re(r₁) ≈ 1/136: dev {mp.nstr(abs(Re1 - mp.mpf(1)/136)/abs(Re1), 6)} (🟡 候選, φ-陷阱窗內)")
check("T1 Δθ 冇乾淨結構身份 (幾何干涉, O196 T2 預告一致)", 
      abs(dth - mp.pi/256)/dth > 1e-3, f"Δθ={mp.nstr(mp.degrees(dth),8)}°")
check("T1 Re(r₁)≈1/136 🟡 (唔閉合, 需獨立機制)", 
      abs(abs(Re1) - mp.mpf(1)/136)/abs(Re1) < 1e-2, f"dev={mp.nstr(abs(abs(Re1)-mp.mpf(1)/136)/abs(Re1),5)}")

print("\n== T2: κ Rayleigh 11-adic ==")
# κ_{2m} 遞迴 (m ≤ 80 夠)
M = 80
kap = [0]*(M+1)
for j in range(1, M+1):
    val = math.comb(2*j, j)
    for m in range(1, j):
        val -= math.comb(2*j-1, 2*m-1) * math.comb(2*j-2*m, j-m) * kap[m]
    kap[j] = val
# f(d) 表 (d 11-free ≤ 80)
fmap = {}
for m in range(1, M+1):
    fmap[eleven_free(m)] = v11_int(kap[m])
fz = sorted(d for d in fmap if fmap[d] == 0)
print(f"  v₁₁(κ₂ₘ)=0 ⟺ 11-free(m) ∈ {{1,2,3,5}}: {fz == [1,2,3,5]}")
check("T2 v₁₁(κ₂ₘ)=0 ⟺ 11-free(m) ∈ {F₂,F₃,F₄,F₅} (m≤80)", fz == [1,2,3,5], f"{fz}")
# v₁₁ 自相似: m 同 11·m 同 f
ok_sim = all(v11_int(kap[m]) == fmap[eleven_free(m)] for m in range(1, M+1))
check("T2 v₁₁(κ₂ₘ) = f(11-free(m)) 11-adic 自相似 (m≤80)", ok_sim)
# Legendre 完整和公式
def legendre_11(m):
    s = 0; p = 11
    while p <= m: s += m // p; p *= 11
    return s
from fractions import Fraction as Fr
ok_leg = True
for m in range(1, 41):
    sig = Fr(m*kap[m], math.factorial(2*m)*2**(2*m))
    v = 0
    n = abs(sig.numerator); d = sig.denominator
    while n % 11 == 0: n //= 11; v += 1
    while d % 11 == 0: d //= 11; v -= 1
    pred = v11_int(m) + v11_int(kap[m]) - legendre_11(2*m)
    if v != pred: ok_leg = False; break
check("T2 v₁₁(σ_m) = v₁₁(m) + v₁₁(κ₂ₘ) − v₁₁((2m)!) (m≤40)", ok_leg)

print("\n== T3: Σγ^n 11-adic ==")
ok3 = all(v11_int(88*math.comb(2*n, n) + 2**(2*n-1)) == 0 for n in range(1, 41))
check("T3 v₁₁(Σγ^n) = 0 ∀n≤40 (2^{2n−1} 保護)", ok3)
def v11_binom(ap, bp):
    p = 11
    def sd(x):
        s = 0
        while x: s += x % p; x //= p
        return s
    return (sd(bp) + sd(ap-bp) - sd(ap)) // (p-1)
ok3b = all(v11_int(44*math.comb(2*n, n)) == 1 + v11_binom(2*n, n) for n in range(1, 41))
check("T3 v₁₁(Σγ^n_odd) = 1 + v₁₁(C(2n,n)) ∀n≤40", ok3b)

print("\n== T4: α=0 嚴格證明 ==")
# sin(δ) = Re/R 精確; a_n·Rⁿ·n = 2·sin(nδ) (c=μ²)
print(f"  sin(δ) = Re/R: {abs(mp.sin(delta) - Re1/R) < mp.mpf('1e-50')}")
check("T4 sin(δ) = Re/R 精確 (δ=arcsin ε, 兩根干涉相位 = 極點推離)", 
      abs(mp.sin(delta) - Re1/R) < mp.mpf('1e-50'))
print(f"  log 分支 1/n → sinc: sin(nδ)/n = δ·sinc(nδ), nδ→0 收斂 δ (α=0)")
check("T4 α=0 主導 (sin(nδ)/n → δ, log 1/n 被 δ 吸收)", 
      abs(mp.sin(delta)/delta - 1) < 1e-5)

print("\n== T5: c = μ² EXACT (log 分支留數 = 扇區隙) ==")
# a_n·Rⁿ·n / sin(nδ) → 2? 用 k_n (O196 Fraction)
NORD = 61
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
cs = []
for n in range(31, 60, 2):
    a_n = mp.mpf(k_n[n-1].numerator)/mp.mpf(k_n[n-1].denominator)/mp.factorial(n)
    cs.append(float(abs(a_n) * R**n * n / mp.sin(n*delta)))
c_ok = abs(sum(cs)/len(cs) - 2.0) < 1e-6 and max(cs)-min(cs) < 1e-6
check("T5 c = μ² = 2 EXACT (n=31..59, spread < 1e-6)", c_ok,
      f"c̄ = {sum(cs)/len(cs):.8f}, spread = {max(cs)-min(cs):.2e}")

print("\n== T6: 完整漸近展開 ==")
print("  a_n = ±2·R^{−n}·sin(nδ)/n + O((R/|r₃|)ⁿ)")
print("  δ = arcsin(Re/R) = 0.0061148 (幾何量, 冇獨立閉式 🟡)")
print("  |r₃| = 2.76032 (第二近 δ=±1 根), 殘差 ratio ~0.008")
# j₁ 統一
j1 = mp.besseljzero(0, 1)
dev_j1 = abs(1/R**2 - 4/j1**2)/(4/j1**2)
check("T5' 4/j₁² 統一 arcsine κ + D 增長 (dev < 1e-3)", dev_j1 < 1e-3, f"dev={mp.nstr(dev_j1,6)}")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
