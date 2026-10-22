#!/usr/bin/env python3
"""
O200 script 04 — ② 幀候選唯一性裁決
======================================
候選: t_Pl / τ_ring=1/ω_ring / T_ring / a/c / T_sync / T_age

判準:
  (i)  幀之間嘅關係係唔係【精確結構因子】(2π, 88, ...) → 內部幀
  (ii) t_Pl 同 IDCM 幀嘅關係係唔係結構數 → 決定 t_Pl 係唔係 IDCM 幀

Run: /usr/bin/python3 scripts/04_frame_adjudication.py
"""
import mpmath as mp, math, random
from bisect import bisect_left
mp.mp.dps = 30
random.seed(20260919)

c_si = mp.mpf('299792458'); hbar = mp.mpf('1.054571817e-34')
G = mp.mpf('6.67430e-11'); eV = mp.mpf('1.602176634e-19')
Mpc = mp.mpf('3.0856775814913673e22'); Gyr = mp.mpf('3.1556952e16')
t_Pl = mp.sqrt(hbar*G/c_si**5)

R_world = mp.mpf('4129.94')*Mpc
omega_ring = mp.mpf('72.73e3')/Mpc
H0 = mp.mpf('71.157e3')/Mpc
T_ring = 2*mp.pi/omega_ring
tau = 1/omega_ring
T_sync = 2*mp.pi/H0

CAND = [
    ("t_Pl (普朗克)",        t_Pl),
    ("τ = 1/ω_ring",        tau),
    ("T_ring = 2π/ω_ring",  T_ring),
    ("a/c = R_world/(88c)", R_world/(88*c_si)),
    ("T_sync = 2π/H₀",      T_sync),
    ("T_age",               mp.mpf('11100.64')*Gyr),
]

print("="*80)
print("O200 ② 幀候選唯一性裁決")
print("="*80)

print(f"\n[候選幀]")
for n, v in CAND:
    print(f"  {n:<24} = {mp.nstr(v, 10)} s")

print(f"\n[幀間關係 — 精確結構因子?]")
print(f"\n{'幀 A':<22} {'÷ 幀 B':<22} {'比值':>18} {'最近結構候選':<16} {'偏差%':>9} {'判定'}")
print("-"*100)
STRUCT = [2*mp.pi, mp.pi, mp.mpf(88), mp.mpf(44), mp.mpf(2), mp.mpf(1), mp.mpf(1)/(2*mp.pi),
          mp.mpf(88)/(2*mp.pi), mp.mpf(2)/mp.pi, mp.mpf(123), mp.mpf(176), mp.mpf(45)]
for i, (na, va) in enumerate(CAND):
    for j, (nb, vb) in enumerate(CAND):
        if i >= j:
            continue
        r = va/vb
        best, bd = None, 1e9
        for s in STRUCT:
            d = abs(r/s - 1)
            if d < bd: bd, best = d, s
        verdict = "🟢 精確結構" if bd < 1e-10 else ("🟡 近似" if bd < 0.01 else "🔴 非結構")
        print(f"{na:<22} {'÷ '+nb:<22} {mp.nstr(r, 10):>18} {mp.nstr(best, 8):<16} {float(bd)*100:>8.4f}% {verdict}")

print(f"\n" + "="*80)
print("[裁決]")
print("="*80)
print(f"""
  ① IDCM 內部幀全部由【精確結構因子】互相鎖定:
     T_ring = 2π × τ          (2π — 環幾何, EXACT)
     a/c    = τ × (c_W/c)/88  (88 — 站點數, dev 0.19%)
     ⟹ τ、T_ring、a/c 係同一個幾何幀嘅三個刻度

  ② t_Pl 同 IDCM 幀嘅關係:
     τ/t_Pl = {mp.nstr(tau/t_Pl, 10)}
     ⟹ 唔係結構數 (script 01/02 已證 φ-冪 P = 0.70)

  ★ 結論:
     幀 = IDCM 內部幾何幀 τ = 1/ω_ring (= R_world/c)
     t_Pl 唔係 IDCM 幀 — 佢係【外部單位約定】(含 ħ, G)
     兩者之比 = 階層數 N = τ/t_Pl ≈ 7.87e60 (觀測鎖定, 非結構)
""")

# ---- 階層數結構性再檢 (擴大池: 2^k, 10^k, φ^k × p/q) ----
print("="*80)
print("[階層數 N = τ/t_Pl 結構性再檢 (擴大池)]")
print("="*80)
N = tau/t_Pl
pool = []
for k in range(-400, 401):
    pool.append(float(phi**k) if False else float((1+mp.sqrt(5))/2)**k)
for k in range(0, 300):
    pool.append(float(mp.mpf(2)**k)); pool.append(float(mp.mpf(10)**k))
for p in range(1, 301):
    for q in range(1, 301):
        pool.append(float(mp.mpf(p)/q))
pool = sorted(set(v for v in pool if v > 0))

def best(x):
    xf = float(x); lo = bisect_left(pool, xf); bd = 1e9
    for i in (lo-1, lo):
        if 0 <= i < len(pool):
            bd = min(bd, abs(pool[i]/xf - 1))
    return bd

bd_actual = best(N)
cnt = 0; M = 20000
lo_, hi_ = math.log(float(N))-3, math.log(float(N))+3
for _ in range(M):
    if best(math.exp(random.uniform(lo_, hi_))) <= bd_actual: cnt += 1
print(f"  N = {mp.nstr(N, 10)}")
print(f"  最佳池偏差 = {bd_actual*100:.4f}%")
print(f"  P(null, M={M}, 池 {len(pool)}) = {cnt/M:.4f}")
print(f"  ⟹ {'🟢 超越隨機' if cnt/M < 0.01 else '🔴 ≈ 隨機 — 階層數唔係結構數'}")
