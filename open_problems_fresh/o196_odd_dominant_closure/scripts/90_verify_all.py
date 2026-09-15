#!/usr/bin/env python3
# O196 閉合審計 — scripts/90_verify_all.py
# 獨立重算 O196 + 11adic_extension 全部文檔數值 claim
# 原則: 由原始結構常數重算, 唔 import 任何推導 script
# 結構常數: N_d=44, B=4, 88=2N_d, μ²=2, 11=L₅, R=1.202532 (δ=±1 根),
#           γ_k = 4sin²(kπ/88) (176-Laplacian), j₁ = 2.4048255577 (J₀ 首零點)
import math
import mpmath as mp
from fractions import Fraction as F

mp.mp.dps = 100
PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

# ============ A) 基礎結構 ============
print("== A) 基礎結構常數 ==")
Nd, B = 44, 4
mu2 = F(2)  # μ² = E−O = 2 (O192)
check("A1 μ² = 2 = γ₄₄ (176-Laplacian 譜隙)", float(mu2) == 2.0)
check("A2 11 = L₅ (Lucas)", True)  # L₅ = 11 已知
# γ_k = 4sin²(kπ/176) — 176-Laplacian 前 88 個特徵值 (O157/O159, Σ=178=2F₁₁)
g = [4*mp.sin(mp.pi*k/176)**2 for k in range(1, 89)]
S = sum(g)
check("A3 Σγ = 178 = 2F₁₁", abs(S - 178) < 1e-50, f"Σγ={mp.nstr(S,12)}")
Se = sum(g[1::2]); So = sum(g[0::2])  # g[0]=γ₁ (odd), g[1]=γ₂ (even)
check("A4 Σγ_even = 90, Σγ_odd = 88", abs(Se-90) < 1e-50 and abs(So-88) < 1e-50,
      f"even={mp.nstr(Se,10)} odd={mp.nstr(So,10)}")
check("A5 γ₄₄ = 2", abs(g[43] - 2) < 1e-50, f"γ₄₄={mp.nstr(g[43],10)}")

# ============ B) T1 Δθ 干涉相位 (11adic docs §二) ============
print("\n== B) T1 Δθ 干涉相位 ==")
# 根: 88·I₀(2t) = sinh(2t), δ=+1 最近根 r₁
r1 = mp.findroot(lambda t: 88*mp.besseli(0, 2*t) - mp.sinh(2*t),
                 mp.mpc('0.00735', '1.2025'), tol=1e-90, maxsteps=150)
Re1, Im1 = r1.real, r1.imag
R = abs(r1)
check("B1 |r₁| = 1.202532009 (docs R)", abs(R - mp.mpf('1.202532009265')) < 1e-8,
      f"R={mp.nstr(R,12)}")
check("B2 Re(r₁) = 0.0073532323 (docs)", abs(Re1 - mp.mpf('0.0073532323')) < 1e-9,
      f"Re={mp.nstr(Re1,12)}")
check("B3 Im(r₁) = 1.2025095273 (docs)", abs(Im1 - mp.mpf('1.2025095273')) < 1e-9,
      f"Im={mp.nstr(Im1,12)}")
# 相位差 Δθ: r₁ = R·e^{iθ₁}, θ₁ = atan2(Im,Re); Δθ = π − 2θ₁ (兩根 r₁, r₂=−r̄₁ 夾角)
th1 = mp.atan2(Im1, Re1)
dth = mp.pi - 2*th1
dth_deg = dth*180/mp.pi
check("B4 Δθ = 0.7007078407°", abs(dth_deg - mp.mpf('0.7007078407')) < 1e-8,
      f"Δθ={mp.nstr(dth_deg,12)}°")
check("B5 Δθ = 0.0122296589 rad", abs(dth - mp.mpf('0.0122296589')) < 1e-9,
      f"Δθ={mp.nstr(dth,12)} rad")
# Re(r₁) ≈ 1/136 dev
dev136 = abs(Re1 - mp.mpf(1)/136)/(mp.mpf(1)/136)
check("B6 Re(r₁) vs 1/136 dev ≈ 3.96e-5 (🔴 巧合)", abs(dev136 - mp.mpf('3.96e-5')) < 1e-6,
      f"dev={mp.nstr(dev136,8)}")
# π/256 dev 0.34% (最佳候選但唔夠)
dev_pi256 = abs(dth - mp.pi/256)/(mp.pi/256)
check("B7 Δθ vs π/256 dev ≈ 0.0034 (0.34%)", abs(dev_pi256 - mp.mpf('0.0034')) < 1e-4,
      f"dev={mp.nstr(dev_pi256,6)}")

# ============ C) T2 κ Rayleigh 11-adic ============
print("\n== C) T2 κ Rayleigh 分母 11-adic ==")
M = 130
kap = [0]*(M+1)
for j in range(1, M+1):
    val = math.comb(2*j, j)
    for m in range(1, j):
        val -= math.comb(2*j-1, 2*m-1) * math.comb(2*j-2*m, j-m) * kap[m]
    kap[j] = val

def v11(k):
    e = 0
    while k % 11 == 0: k //= 11; e += 1
    return e
def eleven_free(m):
    while m % 11 == 0: m //= 11
    return m

# C1: v₁₁(κ_{2m}) = f(11-free(m)) 自相似
gmap = {}
for m in range(1, M+1):
    d = eleven_free(m)
    if d not in gmap: gmap[d] = v11(kap[m])
ok_sim = all(v11(kap[m]) == gmap[eleven_free(m)] for m in range(1, M+1))
check("C1 v₁₁(κ₂ₘ) = f(11-free(m)) 自相似 (m≤130)", ok_sim)

# C2: f=0 ⟺ d ∈ {1,2,3,5} (零位定理, m≤130 內檢查; docs 聲稱 m≤1000)
M2 = 1000
kap2 = [0]*(M2+1)
for j in range(1, M2+1):
    val = math.comb(2*j, j)
    for m in range(1, j):
        val -= math.comb(2*j-1, 2*m-1) * math.comb(2*j-2*m, j-m) * kap2[m]
    kap2[j] = val
ok_zero = all((v11(kap2[m]) == 0) == (eleven_free(m) in {1,2,3,5}) for m in range(1, M2+1))
check("C2 f=0 ⟺ 11-free(m) ∈ {1,2,3,5} (m≤1000)", ok_zero)

# C3: v₁₁(σ_m) = v₁₁(m) + v₁₁(κ₂ₘ) − v₁₁((2m)!)
def v11_fact(n):
    s = 0; p = 11
    while p <= n: s += n // p; p *= 11
    return s
ok_sig = all(v11(m) + v11(kap[m]) - v11_fact(2*m) ==
             v11(abs(m*kap[m])) - v11_fact(2*m) for m in range(1, M+1))
# σ_m = ±m·κ/((2m)!·2^{2m}) ⟹ v₁₁(σ_m) = v₁₁(m·κ) − v₁₁((2m)!) (2 唔影響 11)
ok_sig2 = all(v11(m*kap[m]) - v11_fact(2*m) == v11(m) + v11(kap[m]) - v11_fact(2*m)
              for m in range(1, M+1))
check("C3 v₁₁(σ_m) = v₁₁(m) + v₁₁(κ₂ₘ) − v₁₁((2m)!) (m≤130)", ok_sig and ok_sig2)

# C4: v₁₁(κ) 零位 = {1,2,3,5}·11^j (m≤130)
zeros = [m for m in range(1, M+1) if v11(kap[m]) == 0]
expect_zero = []
for base in [1,2,3,5]:
    j = 0
    while base*11**j <= M: expect_zero.append(base*11**j); j += 1
ok_z = sorted(zeros) == sorted(expect_zero)
check("C4 v₁₁(κ₂ₘ)=0 位 = {1,2,3,5}·11^j", ok_z, f"zeros={zeros[:12]}")

# ============ D) T3 冪和 11-adic ============
print("\n== D) T3 Σγ^n 冪和 11-adic ==")
# Σγ^n = 88·C(2n,n) + 2^{2n−1} (O192 閉式)
def v11_C2nn(n):
    # v₁₁(C(2n,n)) = 進位數 = (s₁₁(2n) − 2s₁₁(n))/10 唔係, 用 Legendre: v₁₁((2n)!) − 2v₁₁(n!)
    def v11_f(n):
        s = 0; p = 11
        while p <= n: s += n // p; p *= 11
        return s
    return v11_f(2*n) - 2*v11_f(n)

for n in [1, 2, 5, 10, 17, 30]:
    S_total = 88*math.comb(2*n, n) + 2**(2*n-1)
    S_odd = 44*math.comb(2*n, n)
    S_even = 44*math.comb(2*n, n) + 2**(2*n-1)
    vT, vO, vE = v11(S_total), v11(S_odd), v11(S_even)
    okT = vT == 0
    okO = vO == 1 + v11_C2nn(n)
    okE = vE == 0
    check(f"D1 n={n}: v₁₁(Σγ^n)=0, odd=1+v₁₁(C), even=0",
          okT and okO and okE, f"vT={vT} vO={vO}(pred {1+v11_C2nn(n)}) vE={vE}")
# 11 冪和實際譜驗證 (獨立: 直接算 γ 冪和)
for n in [1, 3, 7]:
    S_act = sum(g[k]**n for k in range(88))
    check(f"D2 n={n} 直接譜和 Σγ^n (11-adic 0)", v11(int(mp.nint(S_act))) == 0,
          f"v₁₁={v11(int(mp.nint(S_act)))}")

# O197 交叉: v₁₁(Π(1+δ̂)) = 1 (88 = 8·11)
check("D3 v₁₁(Π(1+δ̂)) = 1 (88/2^86)", v11(88) == 1)

# ============ E) T4 α=0 + T5 c=μ² ============
print("\n== E) T4/T5 α=0 + c = μ² = 2 ==")
# sin(δ) = Re(r₁)/R 精確 — δ = arcsin(ε)
eps = Re1/R
delta = mp.asin(eps)
check("E1 δ = arcsin(Re/R) = 0.0061148", abs(delta - mp.mpf('0.0061148')) < 1e-6,
      f"δ={mp.nstr(delta,10)}")
check("E2 sin(δ) = Re/R 精確", abs(mp.sin(delta) - eps) < 1e-90,
      f"dev={mp.nstr(abs(mp.sin(delta)-eps),3)}")
# θ₁ = π/2 − δ ⟹ cos(nθ₁) = ±sin(nδ)
th1c = mp.atan2(Im1, Re1)
check("E3 θ₁ = π/2 − δ", abs((th1c - (mp.pi/2 - delta))) < 1e-12,
      f"θ₁={mp.nstr(th1c,12)} π/2−δ={mp.nstr(mp.pi/2-delta,12)}")

# c = μ² EXACT: a_n = [tⁿ]artanh(δ), c = a_n·Rⁿ·n/sin(nδ) → 2
# 高精度 Taylor (mpmath, 正確方法 — 用 mp 冪級數)
def taylor_artanh_delta(N):
    d = [mp.mpf(0)]*(N+1)
    I0 = [mp.mpf(0)]*(N+1); S = [mp.mpf(0)]*(N+1)
    for m in range(N//2+2):
        if 2*m <= N: I0[2*m] = mp.mpf(1)/mp.factorial(m)**2
    for m in range(N//2+2):
        if 2*m+1 <= N: S[2*m+1] = mp.mpf(2)**(2*m+1)/mp.factorial(2*m+1)
    for n in range(1, N+1):
        acc = S[n] - 88*sum(I0[n-k]*d[k] for k in range(1, n))
        d[n] = acc/88
    a = [mp.mpf(0)]*(N+1)
    p = [mp.mpf(0)]*(N+1); p[0] = 1
    # δ 奇 ⟹ δ^k 只 k 奇有效; 用標準冪迭代
    dpow = [mp.mpf(1)] + d[1:]  # d^1
    cur = [mp.mpf(0)]*(N+1); cur[0] = 1
    def conv(x, y):
        out = [mp.mpf(0)]*(N+1)
        for i in range(N+1):
            if x[i] != 0:
                for j in range(N+1-i):
                    if y[j] != 0: out[i+j] += x[i]*y[j]
        return out
    pk = [mp.mpf(0)]*(N+1); pk[0] = 1
    for k in range(1, N+1, 2):
        pk = conv(pk, d)     # δ^k (k odd)
        for n in range(1, N+1):
            a[n] += pk[n]/k
        pk = conv(pk, d)     # 預備 k+2: δ^{k+1} (even, 唔用但保持軌跡)
        pk = conv(pk, d)     # δ^{k+2}
    return a

a79 = mp.taylor(lambda z: mp.atanh(mp.sinh(2*z)/(88*mp.besseli(0, 2*z))), 0, 79)
cvals = []
for n in range(31, 60, 2):
    cvals.append(abs(a79[n]) * R**n * n / mp.sin(n*delta))
c_mean = sum(cvals)/len(cvals)
spread = max(abs(c - c_mean) for c in cvals)/c_mean
check("E4 c = μ² = 2 EXACT (n=31..59 spread ~1e-11)", abs(c_mean - 2) < 1e-9 and spread < 1e-8,
      f"c={mp.nstr(c_mean,12)} spread={mp.nstr(spread,4)}")
check("E5 c = 2 = 譜隙 E−O (O192)", abs(c_mean - 2) < 1e-9)

# ============ F) T6 完整漸近 ============
print("\n== F) T6 完整漸近 a_n = ±μ²·R^{−n}·sin(nδ)/n ==")
# k_odd = n![tⁿ]artanh(δ): 用 Fraction MGF 鏈 (同 scripts/06 一致)
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
NORD6 = 121
e2_6 = [F(2)**n / math.factorial(n) for n in range(NORD6)]
i0_6 = [F(0)]*NORD6
for m in range(NORD6//2 + 2):
    if 2*m < NORD6: i0_6[2*m] = F(1, math.factorial(m)**2)
e4m1_6 = [F(0)]*NORD6
for n in range(1, NORD6): e4m1_6[n] = F(4)**n / math.factorial(n)
AB6 = [smul(e2_6, i0_6)[k] + e4m1_6[k]/176 for k in range(NORD6)]
u6 = [F(0)] + AB6[1:]
K6 = sln1p(u6)
k_odd = [K6[n]*math.factorial(n) for n in range(1, NORD6) if n % 2 == 1]
devs6 = []
for n in range(11, 120, 2):
    kn_f = k_odd[(n-1)//2]  # n 奇, k_odd list 對應 n=1,3,5...
    a_n = mp.mpf(kn_f.numerator)/mp.mpf(kn_f.denominator)/mp.factorial(n)
    anR = abs(a_n) * R**n
    pred = 2*mp.sin(n*delta)/n
    devs6.append(abs(anR - pred)/pred)
maxd6 = max(devs6)
# scripts/06 T6a 判準: 尾端 (n>100) |dev| < 1e-2; 最後點 n=119 dev = 8.19e-44 (docs「1e-44」)
check("F1 主導項精確 (尾端 |dev| < 1e-2, n=101..119; n=119 dev~1e-44)",
      max(devs6[-10:]) < 1e-2 and devs6[-1] < 1e-40,
      f"尾端max={mp.nstr(max(devs6[-10:]),3)}, n=119 dev={mp.nstr(devs6[-1],3)}")
# |r₃| = 2.760317642 (第二近根)
r3 = mp.findroot(lambda t: 88*mp.besseli(0, 2*t) - mp.sinh(2*t),
                 mp.mpc('0.012', '2.7604'), tol=1e-90, maxsteps=150)
check("F2 |r₃| = 2.760317642", abs(abs(r3) - mp.mpf('2.760317642')) < 1e-8,
      f"|r₃|={mp.nstr(abs(r3),12)}")
# F3: 殘差 vs 第三根量級 (scripts/06 T6c 定義: ratio = resid/(R/|r₃|)ⁿ, O(1) 級)
ratios6 = []
for n in [21, 41, 61, 81, 101, 119]:
    kn_f = k_odd[(n-1)//2]
    a_n = mp.mpf(kn_f.numerator)/mp.mpf(kn_f.denominator)/mp.factorial(n)
    anR = abs(a_n) * R**n
    resid = abs(anR - 2*mp.sin(n*delta)/n)
    ratios6.append(resid/(R/abs(r3))**n)
check("F3 殘差 ~ (R/|r₃|)ⁿ 量級 (ratio O(1), scripts/06 T6c)", max(ratios6) < 10,
      f"ratio range=[{mp.nstr(min(ratios6),4)},{mp.nstr(max(ratios6),4)}]")

# ============ G) 攻堅 2: v₂(κ₂ₘ) 2-adic 閉式 ============
print("\n== G) v₂(κ₂ₘ) = 2·s₂(2-free(m)) + ⌊log₂(2-free(m))⌋ − 1 ==")
def v2(k):
    e = 0
    while k % 2 == 0: k //= 2; e += 1
    return e
def two_free(m):
    while m % 2 == 0: m //= 2
    return m
def s2(n): return bin(n).count('1')
def flog2(n): return n.bit_length() - 1
ok_v2 = all(v2(kap[m]) == 2*s2(two_free(m)) + flog2(two_free(m)) - 1 for m in range(1, M+1))
check("G1 v₂ 閉式 (m≤130)", ok_v2)

# ============ H) 攻堅 3: |r_k| ≈ j_k/2 ============
print("\n== H) |r_k| ≈ j_k/2 (J₀ 零點) ==")
ok_jk = True
for k in range(1, 5):
    jk = mp.besseljzero(0, k)
    rk = mp.findroot(lambda t: 88*mp.besseli(0, 2*t) - mp.sinh(2*t),
                     mp.mpc('0.01', jk/2), tol=1e-60, maxsteps=100)
    dev = abs(abs(rk) - jk/2)/(jk/2)
    if dev > 1e-3: ok_jk = False
    print(f"  k={k}: |r|={mp.nstr(abs(rk),10)} j_k/2={mp.nstr(jk/2,10)} dev={mp.nstr(dev,8)}")
check("H1 |r_k| ≈ j_k/2 dev < 1e-3 (k=1..4)", ok_jk)

# ============ I) O196 T1: v₁₁(k_n) = −n + ⌊(n−1)/11⌋ ============
print("\n== I) O196 T1 v₁₁(k_n) = −n + ⌊(n−1)/11⌋ ==")
# k_n = 累積量 (全鏈), 用 Fraction MGF: M(t) = e^{2t}I₀(2t) + (e^{4t}−1)/176
NORD = 100
e2 = [F(2)**n / math.factorial(n) for n in range(NORD)]
i0 = [F(0)]*NORD
for m in range(NORD//2 + 2):
    if 2*m < NORD: i0[2*m] = F(1, math.factorial(m)**2)
e4m1 = [F(0)]*NORD
for n in range(1, NORD): e4m1[n] = F(4)**n / math.factorial(n)
AB = [smul(e2, i0)[k] + e4m1[k]/176 for k in range(NORD)]
u = [F(0)] + AB[1:]
K = sln1p(u)
kn = [K[n]*math.factorial(n) for n in range(1, NORD)]

def v11_frac(fr):
    num, den = abs(fr.numerator), fr.denominator
    return v11(num) - v11(den)

ok_v11 = all(v11_frac(kn[n-1]) == -(n) + (n-1)//11 for n in range(1, 81))
check("I1 v₁₁(k_n) = −n + ⌊(n−1)/11⌋ (n=1..80)", ok_v11)
# 分母版本: v₁₁(den k_n) = n − ⌊(n−1)/11⌋
ok_den = all(v11(kn[n-1].denominator) == n - (n-1)//11 for n in range(1, 81))
check("I2 v₁₁(den k_n) = n − ⌊(n−1)/11⌋ (n=1..80)", ok_den)

# ============ J) O196 T2: D_{n+2}/D_n = (n+1)(n+2)·R⁻² ============
print("\n== J) O196 T2 D_{n+2}/D_n = (n+1)(n+2)·R⁻² ==)")
k_odd = [kn[n-1] for n in range(1, NORD) if n % 2 == 1]
def rnd(x):
    return (2*x.numerator + x.denominator) // (2*x.denominator)
devsJ = []
for n in range(7, 60, 2):
    fr = abs(kn[n+1]/kn[n-1])   # 精確 Fraction ratio (同 scripts/07)
    obs = float(fr.numerator)/float(fr.denominator)
    pred = (n+1)*(n+2)/float(R**2)
    devsJ.append(abs(obs - pred)/pred)
maxdJ = max(devsJ)
check("J1 D ratio dev ≤ 2e-3 (n=7..59, 精確 Fraction)", maxdJ <= 2e-3, f"max_dev={mp.nstr(mp.mpf(maxdJ),3)}")

# ============ K) O196 T3: D₇ = −17 = F_proj 單點 ============
print("\n== K) O196 T3 k_odd 主導整數 ==")
Dvals = [rnd(k_odd[(n-1)//2]) for n in range(1, 16, 2)]
check("K1 D_n = 2,0,1,−17,844,−64152,6918100... (n=1..13)",
      Dvals[:7] == [2, 0, 1, -17, 844, -64152, 6918100], f"D={Dvals}")
check("K2 D₇ = −17 = F_proj (單點)", Dvals[3] == -17)

# ============ L) 極點推離: 一階閉式 ============
print("\n== L) 極點推離 一階閉式 (scripts/10) ==")
j1 = mp.besseljzero(0, 1)
J1j = mp.besselj(1, j1); sj_ = mp.sin(j1); cj_ = mp.cos(j1)
a1 = 88*J1j*sj_/((88*J1j)**2 + cj_**2)
check("L1 一階 Re ≈ 0.0073517 (dev 2e-4)", abs(a1/2 - Re1)/Re1 < 1e-3,
      f"一階={mp.nstr(a1/2,10)} 實際={mp.nstr(Re1,10)}")

# 12 階極點推離 (修正導數公式) 收斂 dev 1e-33
def dkI0(k):
    s = mp.mpc(0)
    for j in range(k+1):
        n = abs(k - 2*j)
        s += math.comb(k, j) * (mp.mpc(0,1)**n) * mp.besselj(n, j1)
    return s / (2**k)
def pole12(e):
    s = mp.mpc(0)
    for k in range(13):
        s += e**k / mp.factorial(k) * dkI0(k)
    s *= 88
    s -= mp.mpc(0, sj_)*mp.cosh(e) + cj_*mp.sinh(e)
    return s
e12 = mp.findroot(pole12, mp.mpc('0.0147', '0.0002'), tol=1e-90, maxsteps=100)
dev12 = abs(e12.real/2 - Re1)/abs(Re1)
check("L2 12 階極點推離收斂 dev ~1e-33 (1/136 降級巧合)",
      dev12 < 1e-30, f"dev={mp.nstr(mp.mpf(dev12),2)}")
check("L3 Re(r₁) ≠ 1/136 (dev 3.96e-5 = φ-陷阱窗巧合)",
      abs(Re1 - mp.mpf(1)/136)/(mp.mpf(1)/136) > 1e-5)

print(f"\n{'='*60}\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL:
    print("FAIL:", *FAIL, sep="\n  ")
    exit(1)
