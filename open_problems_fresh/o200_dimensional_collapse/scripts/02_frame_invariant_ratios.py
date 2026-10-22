#!/usr/bin/env python3
"""
O200 script 02 (v2) — 幀無關比例結構性檢定
=============================================
正確 null test: 隨機控制組（O136 範式）
  - 對每個比例, 抽 M 個隨機目標（同對數範圍）
  - 搵最佳池候選偏差
  - P = 隨機目標最佳偏差 ≤ 實際最佳偏差 嘅比例
  P 細 ⟹ 實際匹配超越隨機 ⟹ 有結構性訊號

Run: /usr/bin/python3 scripts/02_frame_invariant_ratios.py
"""
import math, random
import mpmath as mp
from bisect import bisect_left

mp.mp.dps = 30
phi = (1+mp.sqrt(5))/2
random.seed(20260919)

# ---------- 常數 ----------
c_si = mp.mpf('299792458'); hbar = mp.mpf('1.054571817e-34')
G = mp.mpf('6.67430e-11'); kB = mp.mpf('1.380649e-23')
eV = mp.mpf('1.602176634e-19'); Mpc = mp.mpf('3.0856775814913673e22')
t_Pl = mp.sqrt(hbar*G/c_si**5); l_Pl = c_si*t_Pl
m_Pl_MeV = mp.sqrt(hbar*c_si/G)*c_si**2/eV*mp.mpf('1e-6')

R_world = mp.mpf('4129.94')*Mpc
omega_ring = mp.mpf('72.73e3')/Mpc
T_ring = 2*mp.pi/omega_ring
r_d = mp.mpf('147.088')*Mpc
M0 = mp.mpf('27.900915'); E_kchain = mp.mpf('4.019988e-3'); m7 = mp.mpf('13.800155')
T_CMB = mp.mpf('2.72548'); A_cs = mp.mpf('134.2e-6')
c_W = R_world*omega_ring; a0 = c_si**2/(2*mp.pi*R_world)

# ---------- 候選池 (只放有結構意義嘅) ----------
LUCAS = [2,1,3,4,7,11,18,29,47,76,123,199,322,521,843]
FIB = [1,1,2,3,5,8,13,21,34,55,89,144,233,377,610]
IDCM = [4,7,11,12,15,17,18,22,29,30,32,33,36,44,45,46,55,61,62,66,88,90,98,105,120,123,134,143,176,248,264,421,496,528,946,1891,2025]
pool = []
for k in range(-400, 401):
    pool.append((float(phi**k), f"phi^{k}"))
for v in LUCAS: pool.append((float(v), f"Lucas{v}"))
for v in FIB: pool.append((float(v), f"Fib{v}"))
for v in IDCM: pool.append((float(v), f"IDCM{v}"))
for p in range(1, 201):
    for q in range(1, 201):
        pool.append((float(mp.mpf(p)/q), f"{p}/{q}"))
for k in range(-6, 7):
    pool.append((float(mp.pi**k), f"pi^{k}"))
pool.append((float(2*mp.pi), "2pi")); pool.append((float(mp.e), "e"))
pool = sorted(set(pool))
pool_vals = [v for v, _ in pool if v > 0]
pool_map = {v: n for v, n in pool if v > 0}
print(f"候選池大小: {len(pool_vals)}")

def best_match(x):
    xf = float(x)
    if xf <= 0: return None, None
    lo = bisect_left(pool_vals, xf)
    best, bd = None, 1e9
    for i in (lo-1, lo):
        if 0 <= i < len(pool_vals):
            d = abs(pool_vals[i]/xf - 1)
            if d < bd: bd, best = d, pool_vals[i]
    return best, bd

def null_test(x, M=40000):
    """隨機控制組: 同對數範圍抽 M 個隨機目標"""
    xf = float(x)
    if xf <= 0: return None
    lo, hi = math.log(xf) - 3, math.log(xf) + 3   # ±3 e-folds 範圍
    _, bd_actual = best_match(xf)
    count = 0
    for _ in range(M):
        r = math.exp(random.uniform(lo, hi))
        _, bd = best_match(r)
        if bd <= bd_actual: count += 1
    return bd_actual, count/M

ratios = [
    ("N_ring/N_world", (T_ring/t_Pl)/(R_world/l_Pl), "結構恆等 2πc/c_W"),
    ("R_world/(c·T_ring)", R_world/(c_si*T_ring), "光穿越/環週期"),
    ("c_W/c", c_W/c_si, "O73"),
    ("a₀/(c²/R_world)", a0/(c_si**2/R_world), "O32 (定義式)"),
    ("R_world/r_d", R_world/r_d, "O170/O73"),
    ("M₀/m₇", M0/m7, "O38/O204"),
    ("M₀/E_kchain", M0/E_kchain, "O38"),
    ("m₇/E_kchain", m7/E_kchain, "O204/O38"),
    ("T_CMB/A", T_CMB/A_cs, "Planck/O41"),
    ("T_CMB/(ħ/(kB·T_ring))", T_CMB/(hbar/(kB*T_ring)), "熱力學"),
    ("(T_ring/t_Pl)/2π", (T_ring/t_Pl)/(2*mp.pi), "幀數/2π"),
    ("M₀/m_Pl", M0/m_Pl_MeV, "質量收束"),
    ("T_CMB/T_Pl", T_CMB/(mp.sqrt(hbar*c_si/G)*c_si**2/kB), "溫度收束"),
]

print("\n" + "="*82)
print("[幀無關比例 — 結構性檢定 (隨機控制組 null test, M=40000)]")
print("="*82)
print(f"\n{'比例':<24} {'值':>14} {'最佳候選':<12} {'偏差%':>9} {'P(null)':>9} {'判定'}")
print("-"*82)
for name, x, src in ratios:
    r = null_test(x)
    if r is None: continue
    bd, P = r
    best, _ = best_match(x)
    bname = pool_map.get(best, "?")
    verdict = "🟢 超越隨機" if P < 0.01 else ("🟡 邊緣" if P < 0.10 else "🔴 ≈ 隨機")
    print(f"{name:<24} {mp.nstr(x, 8):>14} {bname:<12} {bd*100:>8.4f}% {P:>9.4f} {verdict}")

print(f"\n★ P = 隨機目標最佳偏差 ≤ 實際偏差 嘅比例。P < 0.01 = 超越隨機。")
print(f"★ 池子含 φ^k (k=-400..400) + Lucas + Fib + IDCM整數 + p/q (p,q≤200) + π冪。")
