#!/usr/bin/env python3
# O200 scripts/09 — 攻堅: 高階極點推離收斂 + v₂(κ₂ₘ) 2-adic 閉式
# A) 極點推離到 6 階 — 睇 Re(r₁) 收斂極限, 判定 1/136 係咪級數極限/巧合
# B) v₂(κ₂ₘ) 結構: 自相似已確立 (2-free 決定), 搵閉式 g(d)
#    v₂(C(2m,m)) = s₂(m) (binary digit sum, Legendre) — κ 嘅 v₂ 有冇同款?
import math
import mpmath as mp
from fractions import Fraction as Fr

mp.mp.dps = 120
PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

def v2_int(k):
    e = 0
    while k % 2 == 0: k //= 2; e += 1
    return e

def two_free(m):
    while m % 2 == 0: m //= 2
    return m

# ===== A) 高階極點推離 =====
print("== A) 極點推離 6 階 (ε 展開) ==")
r1 = mp.findroot(lambda t: 88*mp.besseli(0, 2*t) - mp.sinh(2*t), mp.mpc('0.0074','1.2024'), tol=1e-100, maxsteps=150)
Re1 = r1.real
j1 = mp.besseljzero(0, 1)
J1j = mp.besselj(1, j1); J2j = mp.besselj(2, j1); J3j = mp.besselj(3, j1)
sj = mp.sin(j1); cj = mp.cos(j1)

# I₀(ij₁+ε) = Σ εᵏ/k! · I_k(ij₁) = Σ εᵏ/k! · iᵏ·J_k(j₁)
# sinh(ij₁+ε) = i·sj·cosh(ε)... 用 sinh(ij₁+ε) = sinh(ij₁)cosh(ε) + cosh(ij₁)sinh(ε)
#   = i·sj·Σε^{2k}/(2k)! + cj·Σε^{2k+1}/(2k+1)!
# 方程: 88·Σ εᵏ·iᵏ·J_k(j₁)/k! = i·sj·cosh(ε) + cj·sinh(ε)
# 用牛頓直接解截斷多項式 — 高階

def pole_push(NORD):
    """NORD 階截斷 ε 解"""
    def f(e):
        s = mp.mpc(0)
        for k in range(NORD+1):
            Jk = mp.besselj(k, j1)
            s += e**k * (mp.mpc(0,1)**k) * Jk / mp.factorial(k)
        s *= 88
        s -= mp.mpc(0, sj)*mp.cosh(e) + cj*mp.sinh(e)
        return s
    e0 = mp.mpc('0.0147', '0.0002')
    return mp.findroot(f, e0, tol=1e-100, maxsteps=100)

print(f"{'階':>3} {'Re(ε)/2':>22} {'dev vs 實際':>14} {'dev vs 1/136':>14}")
c136 = mp.mpf(1)/136
prev = None
for order in [1, 2, 3, 4, 5, 6]:
    e = pole_push(order)
    Re_est = e.real/2
    dev_act = abs(Re_est - Re1)/abs(Re1)
    dev_136 = abs(Re_est - c136)/c136
    print(f"{order:>3} {mp.nstr(Re_est, 18):>22} {mp.nstr(dev_act, 12):>14} {mp.nstr(dev_136, 12):>14}")
    if order == 6:
        print(f"  實際 Re(r₁) = {mp.nstr(Re1, 22)}")
        print(f"  1/136       = {mp.nstr(c136, 22)}")
        # 收斂判定: 6 階 dev vs 1/136 有冇改善?
        check("A) 6 階極點推離 dev vs 1/136 < 3.96e-5 (1/136 = 級數極限?)",
              dev_136 < mp.mpf('3.96e-5'), f"6 階 dev_136 = {mp.nstr(dev_136, 10)}")
        check("A) 6 階極點推離 dev vs 實際 < 1e-4 (收斂中)", dev_act < mp.mpf('1e-4'),
              f"6 階 dev_act = {mp.nstr(dev_act, 10)}")

# ===== B) v₂(κ₂ₘ) 閉式 =====
print("\n== B) v₂(κ₂ₘ) = g(2-free(m)) — 閉式搜索 ==")
M = 80
kap = [0]*(M+1)
for j in range(1, M+1):
    val = math.comb(2*j, j)
    for m in range(1, j):
        val -= math.comb(2*j-1, 2*m-1) * math.comb(2*j-2*m, j-m) * kap[m]
    kap[j] = val
v2s = [v2_int(kap[m]) for m in range(1, M+1)]
gmap = {}
for m in range(1, M+1):
    gmap[two_free(m)] = v2s[m-1]

# 先睇 2-free d 嘅 g(d)
ds = sorted(d for d in gmap if d == two_free(d))
print("  d (2-free):", " ".join(f"{d:>2}" for d in ds[:40]))
print("  g(d):      ", " ".join(f"{gmap[d]:>2}" for d in ds[:40]))

# 假說: g(d) = s₂(d) + 修正? s₂ = binary digit sum
def s2(n):
    return bin(n).count('1')
print("\n  d:      ", " ".join(f"{d:>2}" for d in ds[:25]))
print("  g(d):   ", " ".join(f"{gmap[d]:>2}" for d in ds[:25]))
print("  s₂(d):  ", " ".join(f"{s2(d):>2}" for d in ds[:25]))
print("  g−s₂:   ", " ".join(f"{gmap[d]-s2(d):>2}" for d in ds[:25]))

# 觀察: g−s₂ 似乎 = ?
gdiffs = [gmap[d]-s2(d) for d in ds[:40]]
print(f"  g−s₂ 值集: {sorted(set(gdiffs))}")
# 睇 d 奇: s₂(d) = popcount
d_odd = [d for d in ds if d % 2 == 1][:30]
print("  d odd:  ", " ".join(f"{d:>2}" for d in d_odd))
print("  g(d):   ", " ".join(f"{gmap[d]:>2}" for d in d_odd))
print("  s₂(d):  ", " ".join(f"{s2(d):>2}" for d in d_odd))
print("  g−s₂:   ", " ".join(f"{gmap[d]-s2(d):>2}" for d in d_odd))

# 假說 2: g(d) = v₂((d−1)!)? 定 d 嘅某種階乘估值?
def v2_fact(n):
    s = 0; p = 2
    while p <= n: s += n // p; p *= 2
    return s
print("\n  d:     ", " ".join(f"{d:>2}" for d in d_odd[:25]))
print("  g(d):  ", " ".join(f"{gmap[d]:>2}" for d in d_odd[:25]))
print("  v₂(d!):", " ".join(f"{v2_fact(d):>2}" for d in d_odd[:25]))
print("  g−v₂(d!):", " ".join(f"{gmap[d]-v2_fact(d):>2}" for d in d_odd[:25]))

# 假說 3: g(d) = (d−1) + v₂(σ 分母部分)?
# 觀察: d=1: g=1, d=3: g=4, d=5: g=5, d=7: g=7, d=9: g=6, d=11: g=8, d=13: 8, d=15: 10
# v₂(C(2d,d)) = s₂(d): d=1:1, 3:2, 5:2, 7:3, 9:2, 11:3, 13:3, 15:4
# g − s₂:     d=1:0, 3:2, 5:3, 7:4, 9:4, 11:5, 13:5, 15:6
# g − s₂ = ? d=3:2 = d−1? no (d−1=2 ✓); d=5:3 = d−2? no...
# (d−1)/2: d=3:1, 5:2, 7:3, 9:4, 11:5, 13:6, 15:7
# g−s₂ vs (d−1)/2: 3:2 vs 1; 5:3 vs 2; 7:4 vs 3; 9:4 vs 4 ✓; 11:5 vs 5 ✓; 13:5 vs 6; 15:6 vs 7
# 唔係 (d−1)/2

# 假說 4: g(d) = v₂(κ_{2d}) — κ 係矩 m_j = C(2j,j) 嘅 Bell 轉換
# v₂(C(2j,j)) = s₂(j); Bell 遞迴 v₂ 傳播...
# 直接查: g(d) 有冇 = v₂(Bell(d))? Bell 數 v₂?
# 試: g(d) − v₂(C(2d,d)) = g − s₂(d) 嘅模式
# 睇 d 由細到大: g−s₂: 0, 2, 3, 4, 4, 5, 5, 6, 5, 6, 6, 7, 7, 8, 6, 7, ...
# 呢個好似 = v₂(d!·某嘢)?
print("\n  額外: v₂(κ₂ₘ) 0 位 = 空 (κ 永遠偶) — 同 11-adic (有 0 位) 對比")
print("  v₂ 自相似: True (scripts/08) — 2 都係結構素數 (μ² = 2 譜隙!)")
# 2 = μ²: v₂ 自相似可能反映「2-adic 係觀察者側」結構

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
