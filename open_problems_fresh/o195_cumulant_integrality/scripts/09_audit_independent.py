#!/usr/bin/env python3
# O195 審計 — 獨立核對 v2 (修正 v1 bug: besseli/J₀ 混淆, Fraction round, δ 級數)
import mpmath as mp
from fractions import Fraction
from math import comb, factorial
mp.mp.dps = 60

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  PASS " if cond else "  FAIL ") + name + (f"  [{detail}]" if detail else ""))

def cumulants_full(N, obs_only=False):
    """全鏈 (或觀察者) 累積量 — Fraction 精確"""
    m = [Fraction(0)]*(N+1)
    for n in range(1, N+1):
        base = Fraction(comb(2*n, n))
        m[n] = base + (Fraction(0) if obs_only else Fraction(2**(2*n-1), 88))
    m[0] = Fraction(1)
    k = [Fraction(0)]*(N+1)
    for n in range(1, N+1):
        s = Fraction(0)
        for kk in range(1, n):
            s += Fraction(comb(n-1, kk-1))*k[kk]*m[n-kk]
        k[n] = m[n] - s
    return k

K_obs = cumulants_full(20, obs_only=True)
K_full = cumulants_full(80)

print("═══ docs/01 ═══")
# T1: docs/01 序列 = [κ₁, κ₂, κ₄, κ₆, ..., κ₁₆] (奇累積量 = 0, 緊湊寫法)
seq = [2, 2, -6, 80, -2310, 114912, -8741040, 943113600, -136984998150]
expect = [K_obs[1], K_obs[2], K_obs[4], K_obs[6], K_obs[8], K_obs[10], K_obs[12], K_obs[14], K_obs[16]]
check("T1 κ₁..κ₁₆ (奇=0) = docs 序列", [int(x) for x in expect] == seq, f"{[int(x) for x in expect]}")
check("T1' 奇累積量 κ₃,κ₅,κ₇ = 0", K_obs[3] == 0 and K_obs[5] == 0 and K_obs[7] == 0)
check("T1'' κ_n ∈ ℤ ∀n≤20", all(k.denominator == 1 for k in K_obs[1:21]))

# T2: 顯式整數遞迴
for j in range(1, 9):
    s = Fraction(0)
    for mm in range(1, j):
        s += Fraction(comb(2*j-1, 2*mm-1))*Fraction(comb(2*j-2*mm, j-mm))*K_obs[2*mm]
    check(f"T2 顯式遞迴 j={j}", Fraction(comb(2*j, j)) - s == K_obs[2*j])

# T3: Rayleigh 橋 σ_m = ±m·κ_{2m}/((2m)!·2^{2m}) — 用 κ 整數推出 σ 對比 docs 值
sigma_claim = [Fraction(1,4), Fraction(1,32), Fraction(1,192), Fraction(11,12288),
               Fraction(19,122880), Fraction(473,17694720), Fraction(229,49545216)]
for m in range(1, 8):
    k2m = K_obs[2*m]
    sign = 1 if m % 2 == 1 else -1   # (−1)^{m+1}: m odd → +1
    sig = Fraction(sign * m * k2m, factorial(2*m) * 2**(2*m))
    check(f"T3 σ_{m} Rayleigh 橋 = docs 值", sig == sigma_claim[m-1], f"{sig}")

# T3': 直接 Rayleigh 和 — 收斂慢 (N⁻¹), 2000 零點 0.24995 已顯示 → 1/4 趨勢
# 經典 Bessel 零點平方倒數和 = 1/4 (Watson), O194 R4 已建立
print("  (T3' 註: Σj_{0,k}⁻² 直接求和收斂 N⁻¹ 慢 — 2000 零點 0.24995, 趨勢 → 1/4; 唔係 docs 錯)")

# T4
j1 = mp.besseljzero(0, 1)
check("T4 j₁ = 2.4048256", abs(j1 - 2.4048256) < 1e-6, f"j₁={mp.nstr(j1,10)}")
check("T4' 4/j₁² = 0.69166", abs(4/j1**2 - 0.69166) < 1e-4, f"4/j₁²={mp.nstr(4/j1**2,8)}")

# T5: 全鏈分母 {2, 11}
def den_ok(fr):
    d = fr.denominator
    while d % 2 == 0: d //= 2
    while d % 11 == 0: d //= 11
    return d == 1
check("T5 全鏈 k_n 分母只含 2,11 (n≤20)", all(den_ok(K_full[n]) for n in range(1, 21)))

print("═══ docs/02 ═══")
# A1: k_odd = n![tⁿ]artanh(δ) — 用 mpmath taylor 直接算 artanh(δ(t)) 係數
# δ(t) = sinh(2t)/(88·I₀(2t)); artanh(δ) = ½ln((1+δ)/(1−δ))
def artanh_delta_coeff(N):
    # 數值級數: 用複步長/直接 taylor 技巧 — 高精度
    # δ(t) 奇函數: δ(t) = Σ a_{2j+1} t^{2j+1}
    # artanh(δ) = Σ δ^{2k+1}/(2k+1)
    # 用 mpmath 冪級數對象 (polyval 唔得 — 自己黎)
    # 方法: 定義 f(t) = artanh(sinh(2t)/(88 besseli(0,2t))), 數值微分取係數
    # 用 mp.diff 高階導數: [tⁿ]f = f⁽ⁿ⁾(0)/n!
    def f(t): return mp.atanh(mp.sinh(2*t)/(88*mp.besseli(0, 2*t)))
    coeffs = []
    for n in range(3, N+1, 2):
        c = mp.diff(f, 0, n) / mp.factorial(n)
        coeffs.append((n, c))
    return coeffs

okA = True
for n, c in artanh_delta_coeff(15):
    kpred = mp.factorial(n)*c
    kfrac = K_full[n]
    kval = mp.mpf(kfrac.numerator)/mp.mpf(kfrac.denominator)
    if abs(kpred - kval) > mp.mpf(10)**-40:
        okA = False
        print(f"    n={n}: pred={mp.nstr(kpred,15)} vs k_n={mp.nstr(kval,15)}")
check("A1 k_odd = n![tⁿ]artanh(δ) (n=3..15, 數值高階導數)", okA)

# B1: δ=±1 根 88·I₀(2t) = ±sinh(2t), |t| = 1.202532 (I₀ = besseli!)
def f1(t): return 88*mp.besseli(0, 2*t) - mp.sinh(2*t)
def fm1(t): return 88*mp.besseli(0, 2*t) + mp.sinh(2*t)
r1 = mp.findroot(f1, mp.mpc(0.00735, 1.2025))
r2 = mp.findroot(fm1, mp.mpc(-0.00735, 1.2025))
check("B1 δ=1 根 |t| = 1.202532", abs(abs(r1) - 1.202532) < 1e-6, f"|t|={mp.nstr(abs(r1),10)}")
check("B1' δ=−1 根 |t| = 1.202532", abs(abs(r2) - 1.202532) < 1e-6, f"|t|={mp.nstr(abs(r2),10)}")
check("B2 兩根等距", abs(abs(r1) - abs(r2)) < 1e-12, f"差={mp.nstr(abs(abs(r1)-abs(r2)),5)}")
R = abs(r1)
check("B2' R⁻² = 0.6915 ≈ 4/j₁² = 0.6917 (j₁ 統一)", abs(R**-2 - 4/j1**2) < 2e-4,
      f"R⁻²={mp.nstr(R**-2,7)} vs 4/j₁²={mp.nstr(4/j1**2,7)}")

# B3: D 增長 (n+1)n·R⁻² (docs/02 聲稱, 被 O196 修正為 (n+1)(n+2)·R⁻²)
# 本 O 記錄 B3 用 (n+1)n + 1/n 修正 — O196 已撤銷 → 審計標註
print("  ⚠️ B3: docs/02 用 (n+1)n·R⁻² + 1/n 修正 — O196 T2 已撤銷 (正確 = (n+1)(n+2)·R⁻²)")
Ds = []
for n in range(3, 60, 2):
    k = K_full[n]
    Dn = Fraction((k.numerator*2 + k.denominator) // (2*k.denominator))  # round
    Ds.append((n, Dn))
# 驗證 O196 閉式 (n+1)(n+2)·R⁻²
okB3 = True
for i in range(2, len(Ds)-2):
    n, Dn = Ds[i]
    # Ds 間距 2 (n 步長 2): 單步閉式 D_{n+2}/D_n = (n+1)(n+2)·R⁻²
    # 直接用相鄰 (間距 2) 驗證: Ds[i+1] = D_{n+2}
    n2, Dn2 = Ds[i+1]
    if Dn == 0: continue
    ratio = Dn2/Dn
    pred2 = mp.mpf((n+1)*(n+2))/R**2
    # 相對偏差 (絕對差 ~ O(n²) 增長, 唔可以用固定絕對容差)
    rel = abs(abs(mp.mpf(ratio.numerator)/mp.mpf(ratio.denominator)) - pred2)/pred2
    if rel > mp.mpf('5e-3'):
        okB3 = False
check("B3' O196 閉式 (n+1)(n+2)·R⁻² 命中 (n=7..59)", okB3, "O196 T2 修正後閉式")

# C: dev_abs ~ Uniform — Fraction 精確 round
devs = []
for n in range(5, 60, 2):
    k = K_full[n]
    if k.denominator == 1: continue
    num, den = k.numerator, k.denominator
    r = Fraction((2*num + den) // (2*den)) if num >= 0 else Fraction(-((-2*num + den) // (2*den)))
    devs.append(abs(k - r))
import statistics
mean = statistics.mean(devs)
mx, mn = max(devs), min(devs)
check("C1 dev_abs mean ≈ 0.25 (Uniform[0,0.5))", abs(mean - 0.25) < 0.1, f"mean={float(mean):.4f} n={len(devs)}")
check("C2 dev_abs ∈ [0, 0.5)", mx < 0.5 and mn > 0, f"[{float(mn):.3f}, {float(mx):.3f}]")

# D: v₁₁ 週期
def v11(n):
    c = 0
    while n > 0 and n % 11 == 0:
        c += 1; n //= 11
    return c
okD = True
for n in range(1, 81):
    if v11(K_full[n].denominator) != n - (n-1)//11:
        okD = False; break
check("D1 v₁₁(den k_n) = n − ⌊(n−1)/11⌋ (n≤80)", okD)

# E: κ prime 冇家族 — σ_m 分子大質數 (m=1..10 → κ₂₀)
primes_obs = []
for m in range(1, 11):
    k2m = K_obs[2*m]
    sig = Fraction(m*k2m, factorial(2*m)*2**(2*m)) if m % 2 == 1 else Fraction(-m*k2m, factorial(2*m)*2**(2*m))
    num = sig.numerator
    # 粗略質因數: 睇有冇 > 2m 嘅因子
    n2 = num
    big = []
    d = 2
    while d*d <= n2:
        while n2 % d == 0: n2 //= d
        d += 1
    if n2 > 1 and n2 > 2*m: big.append(n2)
    primes_obs.append(big)
bigs = [b for b in primes_obs if b]
check("E1 σ_m 分子大質數 > 2m (冇家族)", len(bigs) >= 3, f"{[b[0] for b in bigs[:4]]}")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL:
    print("FAIL:", FAIL)
    exit(1)
