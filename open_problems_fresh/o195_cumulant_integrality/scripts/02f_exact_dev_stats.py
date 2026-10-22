#!/usr/bin/env python3
# O195 scripts/02f — dev_abs 精確 (Fraction) 統計 + 奇異點分析修正
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
    # round 到最近整數 (Fraction 精確): floor(x + 1/2)
    return (2*x.numerator + x.denominator) // (2*x.denominator)

print("== dev_abs 精確 (Fraction→float) n=5..59 ==")
devs, Ds = {}, {}
for n in range(5, 61, 2):
    kn = k_n[n-1]
    D = round_frac(kn)
    dev = abs(kn - D)
    devs[n] = float(dev); Ds[n] = int(D)
    print(f"  n={n:>2}: D={D:>28,d}  dev={float(dev):.6e}")

vals = [devs[n] for n in range(5, 61, 2)]
print(f"\n== dev_abs 統計 (n=5..59, {len(vals)} 點, Fraction 精確) ==")
print(f"  min={min(vals):.6f} max={max(vals):.6f} mean={sum(vals)/len(vals):.6f}")
print(f"  Uniform[0,0.5] 期望 mean=0.25: {'接近' if abs(sum(vals)/len(vals)-0.25)<0.08 else '偏離'}")
print(f"  >0.25 比例: {sum(1 for v in vals if v>0.25)}/{len(vals)}")

# 奇異點: 88·I₀(2t) − sinh(2t) = 0 最近根 (複平面)
print("\n== 奇異點: 88·I₀(2t) − sinh(2t) = 0 最近根 ==")
import mpmath as mp
mp.mp.dps = 40
def F(t):
    return 88*mp.besseli(0, 2*t) - mp.sinh(2*t)
# 沿實軸 + 虛軸 + 45° 掃描初始點, findroot
cands = []
for re_ in mp.linspace(0, 6, 61):
    for im_ in mp.linspace(0, 6, 61):
        t0 = mp.mpc(re_, im_)
        r = abs(t0)
        if r < 0.5 or r > 6: continue
        try:
            root = mp.findroot(F, t0, tol=1e-25, maxsteps=60)
        except Exception:
            continue
        if abs(root) < 1e-8: continue
        cands.append(root)
# 去重 (距離 < 1e-6 視為同一根) 同取共軛
uniq = []
for r in cands:
    if not any(abs(r-u) < 1e-6 for u in uniq):
        uniq.append(r)
uniq.sort(key=abs)
print(f"  搵到 {len(uniq)} 個唯一根, 最近 8 個:")
for r in uniq[:8]:
    print(f"    |t| = {float(abs(r)):.10f}   t = {mp.nstr(r, 12)}")
R = abs(uniq[0]) if uniq else None
if R:
    print(f"\n  R = {mp.nstr(R, 12)}")
    print(f"  R⁻² = {mp.nstr(1/R**2, 10)}  (D ratio 漸進係數預言)")
    j1 = mp.besseljzero(0, 1)
    print(f"  j₁/2 = {mp.nstr(j1/2, 10)}  (I₀ 首零點, 即 δ 極點位置)")
    print(f"  (j₁/2)⁻² = {mp.nstr((2/j1)**2, 10)}")

# D ratio vs n²·R⁻²
if R:
    print("\n== D_{n+2}/D_n vs (n+1)n·R⁻² ==")
    R2 = float(1/R**2)
    for n in range(7, 45, 2):
        pred = (n+1)*n*R2
        obs = Ds[n+2]/Ds[n] if Ds[n] else 0
        print(f"  n={n}: pred={pred:.2f} obs={obs:.2f} obs/pred={obs/pred:.4f}")
