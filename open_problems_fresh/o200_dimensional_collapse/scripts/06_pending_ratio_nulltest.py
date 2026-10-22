#!/usr/bin/env python3
"""
O200 script 06 — 待檢比例 null test
=====================================
清單標記為「待檢」嘅三個比例:
  T_age/T_ring   = 131.4093423  (近整數 131)
  R_world/λ_sync = 14.00563625  (近 14)
  v_SM/M₀        = 8824.80019

Run: /usr/bin/python3 scripts/06_pending_ratio_nulltest.py
"""
import math, random
import mpmath as mp
from bisect import bisect_left
mp.mp.dps = 30
random.seed(20260919)

phi = (1+mp.sqrt(5))/2
Mpc = mp.mpf('3.0856775814913673e22'); Gyr = mp.mpf('3.1556952e16')

R_world = mp.mpf('4129.94')*Mpc
omega_ring = mp.mpf('72.73e3')/Mpc
T_ring = 2*mp.pi/omega_ring
lam_sync = mp.mpf('294.8770')*Mpc
T_age = mp.mpf('11100.64')*Gyr
M0 = mp.mpf('27.900915'); v_SM = mp.mpf('246.22e3')

# 池: 整數 1..400 + φ^k + Lucas/Fib + p/q(p,q<=200)
LUCAS = [2,1,3,4,7,11,18,29,47,76,123,199,322,521,843]
FIB = [1,1,2,3,5,8,13,21,34,55,89,144,233,377,610]
pool = set()
for k in range(-400, 401): pool.add(float(phi**k))
for v in LUCAS+FIB: pool.add(float(v))
for v in range(1, 401): pool.add(float(v))
for p in range(1, 201):
    for q in range(1, 201): pool.add(float(mp.mpf(p)/q))
pool = sorted(v for v in pool if v > 0)
print(f"池大小: {len(pool)}")

def best(x):
    xf = float(x); lo = bisect_left(pool, xf); bd = 1e9; bv = None
    for i in (lo-1, lo):
        if 0 <= i < len(pool):
            d = abs(pool[i]/xf - 1)
            if d < bd: bd, bv = d, pool[i]
    return bv, bd

def null(x, M=40000):
    xf = float(x)
    bv, bd = best(xf)
    lo_, hi_ = math.log(xf)-2.5, math.log(xf)+2.5
    c = 0
    for _ in range(M):
        if best(math.exp(random.uniform(lo_, hi_)))[1] <= bd: c += 1
    return bv, bd, c/M

RATIOS = [
    ("T_age/T_ring", T_age/T_ring, "O51 N=131"),
    ("R_world/λ_sync", R_world/lam_sync, "O73"),
    ("v_SM/M₀", v_SM/M0, "O40"),
    ("T_age/T_sync", T_age/(2*mp.pi/(mp.mpf('71.157e3')/Mpc)), "O40/O51"),
    ("M₀/m₇", M0/mp.mpf('13.800155'), "對照 (已知 FAIL)"),
]

print("\n" + "="*76)
print("[待檢比例 — 隨機控制組 null test]")
print("="*76)
print(f"\n{'比例':<18} {'值':>18} {'最佳候選':>12} {'偏差%':>9} {'P(null)':>9} {'判定'}")
print("-"*76)
for n, x, src in RATIOS:
    bv, bd, P = null(x)
    v = "🟢 超越隨機" if P < 0.01 else ("🟡 邊緣" if P < 0.10 else "🔴 ≈ 隨機")
    print(f"{n:<18} {mp.nstr(x, 12):>18} {mp.nstr(bv, 8):>12} {float(bd)*100:>8.4f}% {P:>9.4f} {v}")

print(f"\n★ 全部需 P < 0.01 才算超越隨機。")
