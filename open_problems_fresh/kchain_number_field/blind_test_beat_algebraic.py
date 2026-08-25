#!/usr/bin/env python3
"""盲測第三輪: beat(2,31) 精確代數驗證 (sympy)"""
from sympy import sin, pi, sqrt, nsimplify, minimal_polynomial, Poly, factor, nfloat, symbols
from sympy.ntheory import totient
from math import gcd
from fractions import Fraction

x = symbols('x')

# 精確代數數
w2  = 2*sin(2*pi/88)
w31 = 2*sin(31*pi/88)
B   = abs(w2 - w31)
print(f"精確: B = |2sin(2π/88) − 2sin(31π/88)|")

# 化簡 sin(2π/88) = sin(π/44) — 唔係標準角度, degree 20
# 化簡 sin(31π/88): 31 = 44-13, sin(31π/88)=cos(13π/88)
print(f"sin(2π/88) = sin(π/44) (degree 20)")
print(f"sin(31π/88) = cos(13π/88) (degree 40)")

# 數值
Bv = float(B.evalf(30))
print(f"\nB = {Bv:.15f}")

# minimal polynomial (可能要一陣)
from sympy import Poly as Poly_
try:
    mp_expr = minimal_polynomial(B, x=x)
except Exception:
    from sympy import QQ
    from sympy.polys.numberfields import minimal_polynomial as mp2
    mp_expr = mp2(B, x)
mp = Poly_(mp_expr, x)
print(f"\nminimal polynomial degree: {mp.degree()}")
print(f"minpoly: {mp}")
print(f"leading coeff: {mp.LC()}, constant: {mp.TC()}")

# 檢查係咪二次/四次根式組合
print(f"\n=== 根式試探 ===")
cands = {
    "√3": sqrt(3),
    "√2": sqrt(2),
    "√(2+√2)": sqrt(2+sqrt(2)),
    "√(2−√2)": sqrt(2-sqrt(2)),
    "√(2+√3)": sqrt(2+sqrt(3)),
    "√(2−√3)": sqrt(2-sqrt(3)),
    "√(3−√2)": sqrt(3-sqrt(2)),
    "√(2+√2)+√2": sqrt(2+sqrt(2))+sqrt(2),
    "√(2+√3)−√2": sqrt(2+sqrt(3))-sqrt(2),
    "√3−√(2−√2)": sqrt(3)-sqrt(2-sqrt(2)),
}
for name, c in cands.items():
    diff = abs(float((B - c).evalf(20)))
    if diff < 1e-10:
        print(f"  ✅ {name} EXACT!")
    elif diff < 1e-6:
        print(f"  🟡 {name} ≈ {diff:.2e}")

# nsimplify 試探
print(f"\n=== nsimplify ===")
for tol in [1e-8, 1e-10]:
    ns = nsimplify(B, tolerance=tol, full=True)
    print(f"  tol={tol}: {ns} = {float(ns.evalf(15)):.10f}")

# 檢查 B 同 catalog beats 嘅比值有冇特別數值
print(f"\n=== 與 catalog beats 嘅比值 ===")
omega = lambda n: float(2*sin(pi*n/88).evalf(20))
def beat(a,b): return abs(omega(a)-omega(b))
catalog = {"(5,6)":(5,6),"(19,25)":(19,25),"(33,35)":(33,35),"(3,22)":(3,22),
           "(42,43)":(42,43),"(10,31)":(10,31),"(25,35)":(25,35),"(6,37)":(6,37),
           "(13,14)":(13,14),"(41,42)":(41,42),"(3,37)":(3,37),"(16,35)":(16,35),
           "(10,28)":(10,28),"(4,13)":(4,13),"(9,25)":(9,25),"(11,23)":(11,23),
           "(12,26)":(12,26),"(25,29)":(25,29),"(3,20)":(3,20)}
interesting = {"φ": (1+5**0.5)/2, "√2": 2**0.5, "√3": 3**0.5, "√5": 5**0.5, "√6": 6**0.5,
               "√7": 7**0.5, "√8": 8**0.5, "2": 2, "3": 3, "1.5": 1.5, "2.5": 2.5,
               "φ²": ((1+5**0.5)/2)**2, "√2+√3": 2**0.5+3**0.5}
for cname, (a,b) in catalog.items():
    cb = beat(a,b)
    r = Bv/cb
    for iname, iv in interesting.items():
        if abs(r-iv)/iv < 1e-5:
            print(f"  B/beat{cname} = {r:.8f} ≈ {iname} ({abs(r-iv)/iv*100:.6f}%)")
print("  (掃描完成)")
