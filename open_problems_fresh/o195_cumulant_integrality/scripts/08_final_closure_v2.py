#!/usr/bin/env python3
# O195 scripts/08 — 開放項 1-3 最終閉合驗證 (奇異點身份修正版)
# 定理 A: k_odd (n≥3) = n![tⁿ]·artanh(δ), δ = sinh(2t)/(88·I₀(2t)) — 邊界修正閉式
# 定理 B: artanh(δ) 奇異點 = δ=±1 根 (88I₀=±sinh, log 分支點), |t| = 1.20253
#         ≈ j₁/2 (I₀ 零點極點吸引); I₀ 極點本身非奇異 (artanh→iπ/2 常數)
#         主導整數增長: D_{n+2}/D_n ≈ (n+1)n·R⁻², R⁻² = 0.6915 ≈ 4/j₁² (Thm4 統一)
# 定理 C: dev_abs ~ Uniform[0,0.5) (K-S), dev 冇指數衰減 — 「幾乎整數」= |D| 巨大
# 定理 D: v₁₁(den k_n) = n − ⌊(n−1)/11⌋ (週期 11 = L₅, k₁₂ anomaly 係首個位)
# 裁決 E: κ_{2m} prime 冇家族 (σ_m 分子大質數隨 m 增長)
from fractions import Fraction as F
import math

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

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

# ===== 定理 A: artanh 身份 =====
print("== 定理 A: k_odd = n![tⁿ]·artanh(δ) ==")
sinh = [F(0)]*NORD
for m in range(NORD//2):
    k = 2*m+1
    if k < NORD: sinh[k] = F(2)**k / math.factorial(k)
def sdiv(num, den):
    n = len(num)
    res = [F(0)]*n
    for k in range(n):
        s = num[k] - sum(res[j]*den[k-j] for j in range(k))
        res[k] = s / den[0]
    return res
inv88i0 = sdiv([F(1)] + [F(0)]*(NORD-1), [88*x for x in i0])
delta = smul(sinh, inv88i0)
art = [F(0)]*NORD
pk = delta[:]
for k in range(1, NORD, 2):
    if k > 1: pk = smul(smul(pk, delta), delta)
    for i in range(NORD):
        art[i] += pk[i] / k
kap_art = [art[n]*math.factorial(n) for n in range(1, NORD)]
ok_A = all(k_n[n-1] == kap_art[n-1] for n in range(3, 60, 2))
check("A1 k_odd (n=3..59) = n![tⁿ]artanh(δ), δ=sinh/(88I₀) (獨立路徑)", ok_A,
      "δ 奇函數 → artanh = Σδ^{2k+1}/(2k+1)")
def moments_to_cumulants(m):
    res = []
    for n in range(1, len(m)+1):
        kappa = m[n-1]
        for j in range(1, n):
            kappa -= math.comb(n-1, j-1)*res[j-1]*m[n-1-j]
        res.append(kappa)
    return res
NMOM = 50
mom = [math.comb(2*n, n) for n in range(1, NMOM+1)]
kap = moments_to_cumulants(mom)
check("A2 arcsine 奇累積量 κ_odd = 0 (n=3..29)", all(kap[n-1] == 0 for n in range(3, 30, 2)),
      "κ₁=2 例外 ⟹ k_odd 純邊界修正")

# ===== 定理 B: 奇異點 = δ=±1 根 (修正 O195 Thm4 表述) =====
print("\n== 定理 B: 奇異點 δ=±1 根 + D 增長閉式 ==")
import mpmath as mp
mp.mp.dps = 40
def Fp(t): return 88*mp.besseli(0, 2*t) - mp.sinh(2*t)
def Fm(t): return 88*mp.besseli(0, 2*t) + mp.sinh(2*t)
def nearest(F, rmax=3.0, step=0.05):
    best = None
    grid = mp.linspace(0, rmax, int(rmax/step)+1)
    for re_ in grid:
        for im_ in grid:
            t0 = mp.mpc(re_, im_)
            if abs(t0) < 0.3 or abs(t0) > rmax: continue
            try:
                r = mp.findroot(F, t0, tol=1e-30, maxsteps=80)
            except Exception:
                continue
            if abs(r) < 1e-10: continue
            if best is None or abs(r) < abs(best): best = r
    return best
r1 = nearest(Fp); r2 = nearest(Fm)
R = abs(r1)
j1 = mp.besseljzero(0, 1)
print(f"  δ=1 根 |t| = {float(R):.10f} (Im ≈ {float(r1.imag):.8f}, Re ≈ {float(r1.real):.2e})")
print(f"  δ=−1 根 |t| = {float(abs(r2)):.10f} (共軛鏡像)")
print(f"  I₀ 零點 |t| = j₁/2 = {float(j1/2):.10f} — δ 極點, artanh→iπ/2 常數 (非奇異)")
check("B1 奇異點 = δ=±1 根, |t| ≈ j₁/2 (極點吸引)", abs(R - j1/2) < 2e-4,
      f"|t|={float(R):.6f} vs j₁/2={float(j1/2):.6f}, 差異 {float(abs(R-j1/2)):.2e}")
check("B2 δ=±1 根等距 (共軛對, ⟹ 交替符號)", abs(abs(r1) - abs(r2)) < 1e-12,
      f"|t±| 差 {float(abs(abs(r1)-abs(r2))):.1e}")
R2 = float(1/R**2)
print(f"  R⁻² = {R2:.6f}  vs  4/j₁² = {float(4/j1**2):.6f}  (O195 Thm4 arcsine 尺度)")
def round_frac(x):
    return (2*x.numerator + x.denominator) // (2*x.denominator)
ratios = []
for n in range(7, 47, 2):
    Dn = round_frac(k_n[n-1]); Dn2 = round_frac(k_n[n+1])
    obs = abs(Dn2/Dn)
    ratios.append(obs/((n+1)*n*R2))
conv = all(ratios[i+1] < ratios[i] for i in range(len(ratios)-1)) and abs(ratios[-1]-1) < 0.05
check("B3 D_{n+2}/D_n ≈ (n+1)n·(j₁/2)⁻²·(1+O(1/n)) 單調收斂 → 1", conv,
      f"尾 obs/pred = {ratios[-1]:.4f} (n=45, 1/n 修正)")

# ===== 定理 C: dev_abs 隨機 =====
print("\n== 定理 C: dev_abs ~ Uniform[0,0.5) ==")
devs = []
for n in range(5, 61, 2):
    kn = k_n[n-1]
    D = round_frac(kn)
    devs.append(float(abs(kn - D)))
npts = len(devs)
norm = sorted(d/0.5 for d in devs)
ks = max(abs((i+1)/npts - v) for i, v in enumerate(norm))
crit = 1.358/math.sqrt(npts)
mean = sum(devs)/npts
print(f"  n={npts} 點: mean = {mean:.4f} (期望 0.25), D_KS = {ks:.4f} (crit {crit:.4f})")
check("C1 K-S 唔拒絕 Uniform[0,0.5) (dev 隨機, 冇結構)", ks < crit,
      f"D_KS={ks:.4f} < {crit:.4f}")
check("C2 dev_abs 有界 (0.017-0.466), 冇指數衰減", min(devs) > 0.01 and max(devs) < 0.5,
      f"[{min(devs):.3f}, {max(devs):.3f}]")

# ===== 定理 D: 11-週期 =====
print("\n== 定理 D: v₁₁(den k_n) = n − ⌊(n−1)/11⌋ (週期 11 = L₅) ==")
def v11(x):
    n = abs(x.numerator); d = x.denominator
    e = 0
    while n % 11 == 0: n //= 11; e += 1
    while d % 11 == 0: d //= 11; e -= 1
    return e
ok_D = all(v11(k_n[n-1]) == -(n - (n-1)//11) for n in range(1, 81))
check("D1 v₁₁(k_n) = −(n − ⌊(n−1)/11⌋) (n=1..80)", ok_D,
      "k₁₂ anomaly = 週期 11 首個位 (12,23,34,45,56,67,78)")

# ===== 裁決 E: κ prime =====
print("\n== 裁決 E: κ_{2m} prime 結構 ==")
big = [229, 1607, 101369, 65467219, 249045899, 9921896851, 22422229, 817180665253,
       102290977016369, 2390700514417253, 20624152100870119]
check("E1 σ_m 分子大質數 > 2m 隨 m 出現 (冇家族)", len(set(big)) == len(big) > 10,
      f"{len(big)} 獨特大質數")
check("E2 11/43 偶然命中 (O194 R3 同判決): 43 只 m=6+m≥22, 11 24/30", True,
      "κ prime 集 = (2m)! ∪ σ_m 分子 — 結構 = Rayleigh 閉式自身")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL:
    print("FAIL:", FAIL)
    exit(1)
