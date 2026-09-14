#!/usr/bin/env python3
# O200 scripts/05 — T4b: c 值精確鎖定 (Fraction) + T5: j₁ 統一精確定理
# T4 發現: a_n·Rⁿ·n = c·sin(nδ), c ≈ 2 (dev 3e-6) — 候選 c = μ² = 2
# 本 script: 用 O196 Fraction k_n 精確算 a_n·Rⁿ·n, 對每個 n 解 c_n = a_n·Rⁿ·n/sin(nδ)
#            c_n → 常數? c = 2 = μ²?
# T5: j₁ 統一 — R = 1.202532 vs j₁/2 = 1.2024128 (dev 0.0099%)
#     機制: δ=1 根被 I₀ 首零點極點吸引 (O195); 量化吸引距離 + ε 結構
from fractions import Fraction as F
import math
import mpmath as mp

mp.mp.dps = 60
PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

# ===== T4b: c 精確鎖定 =====
# 用 O196 方法: k_n = n!·a_n (Fraction 精確)
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

# a_n = k_n/n! (奇 n 先有值 — k_odd 即係全鏈奇累積量)
# O196: D_n = round(k_odd); a_n = [tⁿ]artanh(δ)
# 根參數 (dps=60)
r1 = mp.findroot(lambda t: 88*mp.besseli(0, 2*t) - mp.sinh(2*t), mp.mpc('0.0074','1.2024'), tol=1e-50, maxsteps=100)
R = abs(r1); theta1 = mp.arg(r1); delta = mp.pi/2 - theta1

print("== T4b: c_n = a_n·Rⁿ·n / sin(nδ) — 收斂到 c = ? ==")
print(f"  R = {mp.nstr(R, 20)}, δ = {mp.nstr(delta, 20)}")
cs = []
for n in range(5, 80, 2):
    a_n = float(k_n[n-1].numerator)/float(k_n[n-1].denominator)/math.factorial(n)
    c_n = abs(a_n) * R**n * n / mp.sin(n*delta)
    cs.append(float(c_n))
    if n % 10 == 5 or n > 69:
        print(f"  n={n:>2}: c_n = {mp.nstr(mp.mpf(c_n), 12)}")
tail = cs[-8:]
print(f"  尾端 c_n (n=63..79): {[f'{c:.6f}' for c in tail]}")
print(f"  c 尾端均值 = {sum(tail)/len(tail):.8f}, spread = {max(tail)-min(tail):.2e}")
check("T4b c_n 收斂 (尾端 spread < 1e-3)", max(tail)-min(tail) < 1e-3, f"spread={max(tail)-min(tail):.2e}")
check("T4b c = 2 = μ² (尾端均值 dev < 1e-3)", abs(sum(tail)/len(tail) - 2.0) < 1e-3,
      f"c̄ = {sum(tail)/len(tail):.6f}")
# c = 2 嘅結構身份: μ² = E−O = BC-cost (O192 預算量子) — log 分支留數 = 譜隙!
print(f"  ⟹ log 分支留數 c = μ² = 2 — 分支強度 = 扇區隙 (O192 預算量子)")

# ===== T5: j₁ 統一精確定理 =====
print("\n== T5: j₁ 統一 — R vs j₁/2 精確關係 ==")
j1 = mp.besseljzero(0, 1)   # J₀ 首零點
print(f"  j₁ = {mp.nstr(j1, 25)}")
print(f"  j₁/2 = {mp.nstr(j1/2, 25)}")
print(f"  R = {mp.nstr(R, 25)}")
dR = R - j1/2
print(f"  R − j₁/2 = {mp.nstr(dR, 25)}")
print(f"  dev = {mp.nstr(abs(dR)/(j1/2), 10)}")
# 吸引機制: δ=1 根 = 88I₀(2t) = sinh(2t); I₀ 首零點喺 2t = ij₁ (純虛) ⟹ t = ij₁/2
# 但 δ=1 根唔喺虛軸 (Re = +0.00735) — sinh 嘅相位推走咗
# 量化: δ=1 根 r₁ 同 I₀ 極點 ij₁/2 嘅距離
pole = mp.mpc(0, j1/2)
dist = abs(r1 - pole)
print(f"  I₀ 首零點極點 ij₁/2 = {mp.nstr(pole, 20)}")
print(f"  |r₁ − ij₁/2| = {mp.nstr(dist, 20)}")
print(f"  Re(r₁) = {mp.nstr(r1.real, 20)} — 吸引嘅「實部推離」")
# 假說: Re(r₁) 由 sinh 喺 ij₁/2 嘅相位差決定?
# 88·I₀(2t) = sinh(2t) — 喺 t = ij₁/2: sinh(ij₁) = i·sin(j₁) ≈ i·sin(2.4048) ≈ i·0.6755
# I₀(ij₁) = J₀(j₁) = 0 (零點!) — 所以 88I₀ = 0 ≠ sinh — 根要偏離極點令兩邊平衡
# 一階: 88·I₀(2t) ≈ 88·I₀'(ij₁)·(2t−ij₁)·... vs sinh(2t) ≈ sinh(ij₁)
# ⟹ 2t − ij₁ ≈ sinh(ij₁)/(88·I₀'(ij₁)·2)... 
print("\n  ★機制: 根被極點吸引但 sinh 嘅非零值推離實軸")
print("  I₀(2t) 零點 (極點) 本身唔係奇異點 (artanh→iπ/2 常數, O195)")
print("  δ=1 根係 88I₀ 同 sinh 嘅平衡點 — 喺極點附近但被 sinh 相位推離")
# j₁/2 距離 vs 結構常數
print(f"  R vs 4/j₁²: 4/j₁² = {mp.nstr(4/j1**2, 15)} (O195 arcsine 尺度)")
print(f"  R⁻² = {mp.nstr(1/R**2, 15)}")
print(f"  dev = {mp.nstr(abs(1/R**2 - 4/j1**2)/(4/j1**2), 8)} (0.02% 內, O195 已記)")
check("T5 4/j₁² 同時控制 arcsine κ 同 D 增長 (dev < 1e-3)",
      abs(1/R**2 - 4/j1**2)/(4/j1**2) < 1e-3,
      f"dev={mp.nstr(abs(1/R**2-4/j1**2)/(4/j1**2),6)}")

# T5b: Re(r₁) 吸引距離嘅結構掃描
print("\n== T5b: Re(r₁) = 極點推離量 — 結構掃描 ==")
Re1 = r1.real
# sinh(ij₁) = i·sin(j₁) 嘅大小
sinj1 = mp.sin(j1)
print(f"  sinh(ij₁) = i·sin(j₁) = i·{mp.nstr(sinj1, 10)}")
print(f"  Re(r₁) = {mp.nstr(Re1, 15)}")
# 一階近似: 2·Re ≈ sin(j₁)/(88·I₀'(ij₁)·2)? I₀'(ij₁) = I₁(ij₁) = i·J₁(j₁)?? I₁(z) = −i·J₁(iz)
# I₁(ij₁): I₁(ix) = i·J₁(x)? 唔啱 — I₁(ix) = i^{1}·J₁(x)? 用 mpmath 直接算
I1 = mp.besseli(1, 2*pole)  # I₁(2·ij₁/2) = I₁(ij₁)
print(f"  I₁(ij₁) = {mp.nstr(I1, 10)}")
# 一階平衡: 88·I₀(2t) ≈ 88·I₀(ij₁ + 2·(t−ij₁/2))... 用泰勒: I₀(z+ε) ≈ I₀(z) + I₁(z)ε
# 88·I₀(2t) = sinh(2t); 2t = ij₁ + 2Δ (Δ = t − ij₁/2)
# 88·[I₀(ij₁) + I₁(ij₁)·2Δ] ≈ 88·I₁(ij₁)·2Δ = sinh(ij₁ + 2Δ) ≈ sinh(ij₁) + cosh(ij₁)·2Δ
# I₀(ij₁) = J₀(j₁) = 0; sinh(ij₁) = i·sin(j₁); cosh(ij₁) = cos(j₁)
# ⟹ 2Δ(88·I₁(ij₁) − cos(j₁)) ≈ i·sin(j₁)
d2 = mp.mpc(0, sinj1) / (2*(88*I1 - mp.cos(j1)))
print(f"  一階 Δ 預言 = {mp.nstr(d2, 10)} (實部 = {mp.nstr(d2.real, 10)}, 虛部 = {mp.nstr(d2.imag, 10)})")
print(f"  實際 r₁ − ij₁/2 = {mp.nstr(r1 - pole, 10)}")
check("T5b 一階極點推離模型 (實部量級一致)", 
      abs(d2.real - (r1-pole).real) < abs((r1-pole).real),
      f"模型 Re={mp.nstr(d2.real,8)} vs 實際 Re={mp.nstr((r1-pole).real,8)}")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
