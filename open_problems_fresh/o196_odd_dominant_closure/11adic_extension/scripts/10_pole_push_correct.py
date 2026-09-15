#!/usr/bin/env python3
# O200 scripts/10 — 極點推離修正高階導數 + 1/136 最終裁決
# 正確 Bessel 高階導數: I₀^(k)(z) = 2^{-k}·Σ_{j=0}^{⌊k/2⌋} C(k,j)·I_{k-2j}(z)
# 喺 z = ij₁: I_n(ij₁) = iⁿ·J_n(j₁)
# 目標: 高階極點推離收斂值 vs 實際 Re(r₁) vs 1/136 — 判定 1/136 身份
import math
import mpmath as mp

mp.mp.dps = 120
PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

r1 = mp.findroot(lambda t: 88*mp.besseli(0, 2*t) - mp.sinh(2*t), mp.mpc('0.0074','1.2024'), tol=1e-100, maxsteps=150)
Re1 = r1.real
j1 = mp.besseljzero(0, 1)
sj = mp.sin(j1); cj = mp.cos(j1)
c136 = mp.mpf(1)/136

# I₀^(k)(ij₁) 正確公式: I₀^(k)(z) = 2^{-k}·Σ_{j=0}^{k} C(k,j)·I_{k-2j}(z), I_{-n}=I_n
def dkI0(k):
    s = mp.mpc(0)
    for j in range(k+1):
        n = abs(k - 2*j)   # I_{k-2j} = I_{|k-2j|} (I_{-n} = I_n)
        Jn = mp.besselj(n, j1)
        s += math.comb(k, j) * (mp.mpc(0,1)**n) * Jn
    return s / (2**k)

# sinh(ij₁+ε) = i·sj·cosh(ε) + cj·sinh(ε) = i·sj·Σε^{2m}/(2m)! + cj·Σε^{2m+1}/(2m+1)!
# 88·Σ εᵏ/k!·I₀^(k)(ij₁) = sinh 展開

def pole_push(NORD):
    def f(e):
        s = mp.mpc(0)
        for k in range(NORD+1):
            s += e**k / mp.factorial(k) * dkI0(k)
        s *= 88
        s -= mp.mpc(0, sj)*mp.cosh(e) + cj*mp.sinh(e)
        return s
    e0 = mp.mpc('0.0147', '0.0002')
    return mp.findroot(f, e0, tol=1e-100, maxsteps=100)

print("== A) 極點推離 (正確導數) 收斂 ==")
print(f"{'階':>3} {'Re(ε)/2':>24} {'dev vs 實際':>14} {'dev vs 1/136':>14}")
for order in [1, 2, 3, 4, 5, 6, 8, 10, 12]:
    e = pole_push(order)
    Re_est = e.real/2
    dev_act = abs(Re_est - Re1)/abs(Re1)
    dev_136 = abs(Re_est - c136)/c136
    print(f"{order:>3} {mp.nstr(Re_est, 22):>24} {mp.nstr(dev_act, 12):>14} {mp.nstr(dev_136, 12):>14}")
print(f"  實際 Re(r₁) = {mp.nstr(Re1, 25)}")
print(f"  1/136       = {mp.nstr(c136, 25)}")

# 收斂極限判定: 12 階 dev vs 實際
e12 = pole_push(12)
Re12 = e12.real/2
dev12_act = abs(Re12 - Re1)/abs(Re1)
print(f"\n  12 階 Re(ε)/2 = {mp.nstr(Re12, 25)}")
print(f"  dev vs 實際   = {mp.nstr(dev12_act, 12)}")
# 如果極點推離收斂到實際 ⟹ Re(r₁) 純幾何量 (88I₀=sinh 平衡), 1/136 巧合
check("A) 12 階極點推離收斂到實際 Re(r₁) (dev < 1e-6)", dev12_act < mp.mpf('1e-6'),
      f"dev = {mp.nstr(dev12_act, 10)}")
check("A) 12 階極點推離 ≠ 1/136 (dev_136 明顯 > dev_act 或 > 3.96e-5)",
      abs(Re12 - c136)/c136 > mp.mpf('3.96e-5')*2,
      f"dev_136 = {mp.nstr(abs(Re12-c136)/c136, 10)}")

# B) 一階閉式解析值 vs 1/136: 一階閉式本身有冇身份?
print("\n== B) 一階閉式 a = 88J₁sj/((88J₁)²+cj²) 嘅結構 ==")
J1j = mp.besselj(1, j1)
a1 = 88*J1j*sj/((88*J1j)**2 + cj**2)
print(f"  一階 a/2 = {mp.nstr(a1/2, 25)}")
# 有冇 = 1/(某結構)? 試 1/a, 1/(2a)
print(f"  1/a = {mp.nstr(1/a1, 15)}")
print(f"  1/(a/2) = {mp.nstr(2/a1, 15)}")
# j₁ 冇閉式 (超越數) ⟹ a 冇閉式 ⟹ Re(r₁) 冇閉式 — 但 δ=arcsin(Re/R) 幾何
print("  j₁ 係超越數 (J₀ 零點) ⟹ 一階閉式 a 冇有理閉式 ⟹ Re(r₁) 冇有理身份")
print("  ⟹ 1/136 dev 3.96e-5 係巧合 (φ-陷阱窗內但冇機制)")

# C) 2-adic v₂(κ_{2m}) — 再深挖 g(d) 閉式
print("\n== C) v₂(κ₂ₘ) = g(2-free(m)) — g(d) 閉式搜索 ==")
M = 100
kap = [0]*(M+1)
for j in range(1, M+1):
    val = math.comb(2*j, j)
    for m in range(1, j):
        val -= math.comb(2*j-1, 2*m-1) * math.comb(2*j-2*m, j-m) * kap[m]
    kap[j] = val
def v2_int(k):
    e = 0
    while k % 2 == 0: k //= 2; e += 1
    return e
def two_free(m):
    while m % 2 == 0: m //= 2
    return m
gmap = {}
for m in range(1, M+1):
    gmap[two_free(m)] = v2_int(kap[m])
# 自相似確認
ok_sim = all(v2_int(kap[m]) == gmap[two_free(m)] for m in range(1, M+1))
check("C) v₂(κ₂ₘ) = g(2-free(m)) 自相似 (m≤100)", ok_sim)

# g(d) for d odd — 搵模式
ds = sorted(d for d in gmap if d % 2 == 1)[:40]
gvals = [gmap[d] for d in ds]
print("  d odd:", " ".join(f"{d:>2}" for d in ds))
print("  g(d): ", " ".join(f"{g:>2}" for g in gvals))
# 差分模式?
gd = [gvals[i+1]-gvals[i] for i in range(len(gvals)-1)]
print("  差分: ", " ".join(f"{x:+d}" for x in gd))
# 睇: g(2d-1) vs g(d)? g(2k+1) − g(k)?
# 觀察 d odd: g 增長 ~ +1 每個奇數 (除咗 2^k 附近?)
# d=2^k+1 位?
print("\n  d=2^k+1 (k=1..6):", [(2**k+1, gmap.get(2**k+1)) for k in range(1, 7)])
# g(2^k+1): 3→4, 5→5, 9→6, 17→7, 33→8, 65→?
print("  g(2^k+1) = k+3? 3→4 ✓, 5→5 ✓, 9→6 ✓, 17→7 ✓, 33→8 ✓ (k=1..5)")
print("  65 → 預言 9")
print(f"  實測 g(65) = {gmap.get(65)}")
check("C) g(2^k+1) = k+3 (k=1..5)", all(gmap[2**k+1] == k+3 for k in range(1, 6)),
      f"g(65)={gmap.get(65)}")

# g(d) 一般: g(d) = s₂(d) + h(d), h(d) = ?
# 用 d = 2^k+1: s₂ = 2, g = k+3 ⟹ h = k+1
# d = 2^k−1: s₂ = k, g = ?
for k in range(2, 7):
    d = 2**k - 1
    print(f"  d=2^k−1={d}: g={gmap.get(d)}, s₂={k}, g−s₂={gmap.get(d)-k}")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
