#!/usr/bin/env python3
# O195 scripts/02e — 奇異點分析 + dev_abs 統計裁決 (開放項 1 核心)
# ① artanh(δ) 最近奇異點: δ=±1 根 (88I₀=±sinh) — 決定 a_n 衰減率 → D_n 增長率
# ② D_n 增長率 vs n!·R^{-n} 預言對比
# ③ dev_abs 序列統計: 有界? random-like? 有閉式?
# 用 mpmath 高精度 (如果可用), 否則 numpy/scipy root-finding
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
    return round(float(x))

print("== dev_abs 精確序列 (float) ==")
devs, Ds = {}, {}
for n in range(5, 61, 2):
    kn = k_n[n-1]
    fv = float(kn)
    D = round(fv)
    dev = abs(fv - D)
    devs[n] = dev; Ds[n] = D
print(f"  dev_abs: {[f'{devs[n]:.6f}' for n in range(5, 61, 2)]}")

# dev_abs 統計
vals = [devs[n] for n in range(5, 61, 2)]
print(f"\n== dev_abs 統計 (n=5..59, {len(vals)} 點) ==")
print(f"  min={min(vals):.4f} max={max(vals):.4f} mean={sum(vals)/len(vals):.4f}")
print(f"  Uniform[0,0.5] 期望 mean=0.25: {'接近' if abs(sum(vals)/len(vals)-0.25)<0.1 else '偏離'}")
# 過半數喺 [0.25,0.5)?
print(f"  >0.25 比例: {sum(1 for v in vals if v>0.25)}/{len(vals)}")

# 奇異點分析: 88I₀(2t) = sinh(2t) 複根 (最近 |t|)
# I₀(2t) = Σ t^{2m}/(m!)²  (z=2t: I₀(z) = Σ (z/2)^{2m}/(m!)² = Σ t^{2m}/(m!)²)
# 求 F(t) = 88·I₀(2t) − sinh(2t) = 0 最近根
print("\n== 奇異點: 88·I₀(2t) − sinh(2t) = 0 最近根 ==")
try:
    import mpmath as mp
    mp.mp.dps = 30
    def I0z(z):
        return mp.besselj(0, mp.mpc(0,1)*z) if False else mp.besseli(0, z)
    def F(t):
        return 88*mp.besseli(0, 2*t) - mp.sinh(2*t)
    # 網格掃描複平面 |t| < 5, 搵最近根
    best = None
    for re_ in [i*0.1 for i in range(-50, 51)]:
        for im_ in [i*0.1 for i in range(-50, 51)]:
            if re_ == 0 and im_ == 0: continue
            t0 = mp.mpc(re_, im_)
            r = abs(t0)
            if r > 5: continue
            try:
                root = mp.findroot(F, t0, tol=1e-20, maxsteps=50)
            except Exception:
                continue
            rr = abs(root)
            if rr < 1e-9: continue
            if best is None or rr < abs(best):
                # 去重: 同已有根太近就跳過
                best = root
    print(f"  最近根 |t| = {abs(best):.10f}, t = {best}")
    R = abs(best)
    print(f"  R⁻² = {1/R**2:.6f}  (D ratio 漸進係數預言)")
    print(f"  j₁/2 = {mp.besseljzero(0,1)/2:.6f}  (I₀ 首零點)")
    print(f"  (j₁/2)⁻² = {(2/mp.besseljzero(0,1))**2:.6f}")
except ImportError:
    print("  mpmath 唔可用 — 用 scipy?")
    try:
        import scipy.optimize as so
        import numpy as np
        from scipy.special import iv
        def Fre(t):
            return 88*iv(0, 2*t) - np.sinh(2*t)
        # 實根掃描
        xs = np.linspace(0, 200, 4000)
        ys = Fre(xs)
        signs = np.sign(ys)
        roots = []
        for i in range(len(xs)-1):
            if signs[i]*signs[i+1] < 0:
                r = so.brentq(Fre, xs[i], xs[i+1])
                roots.append(r)
        print(f"  實根: {roots[:5]}")
    except ImportError:
        print("  冇 mpmath/scipy — 跳過")

# D_n 增長率理論對比: 若 a_n ~ R^{-n}·c, k_n = n!·a_n ~ n!·R^{-n}
# D_{n+2}/D_n ≈ (n+2)(n+1)·R^{-2} = (n²+3n+2)·R^{-2}
print("\n== D ratio vs n²·R⁻² 預言 ==")
if 'R' in dir():
    for n in range(7, 30, 2):
        pred = (n+1)*(n)*R**-2  # D_n 到 D_{n+2}: 用 n
        obs = Ds[n+2]/Ds[n] if Ds[n] else 0
        print(f"  n={n}: pred={pred:.1f} obs={obs:.1f} ratio={obs/pred if pred else 0:.4f}")
