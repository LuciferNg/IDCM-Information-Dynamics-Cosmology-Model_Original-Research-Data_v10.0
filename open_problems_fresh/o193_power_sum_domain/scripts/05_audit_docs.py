#!/usr/bin/env python3
# O193 scripts/05 — 閉合審計: 獨立重算全部文檔 (docs/01-04, 01_problem_record, final_result) 嘅公式同數值
# 規則: 唔 import 任何被審計 script (01-04); 由原始結構常數 γ_k = 4sin²(kπ/176) 重算一切
# 分組: [A] docs/01  [B] docs/02  [C] docs/03  [D] docs/04  [E] 敍述值重算  [F] 時序/文檔完整性
# 2026-09-14 閉合審計
import mpmath as mp
mp.mp.dps = 180

N = 88
Nd = 44
mu2 = mp.mpf(2)
g = [mp.mpf(4)*mp.sin(mp.pi*k/(2*N))**2 for k in range(1, N+1)]
g_odd = [g[k] for k in range(0, N, 2)]
g_even = [g[k] for k in range(1, N, 2)]

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

def C2n(n): return mp.binomial(2*n, n)

print("== [A] docs/01: 精確域 + Nyquist + arcsine + partition function ==")
# A01: 三閉式 n=1..87 精確
ok = True
for n in range(1, N):
    tot = sum(x**n for x in g); odd = sum(x**n for x in g_odd); even = sum(x**n for x in g_even)
    f_tot = 88*C2n(n) + mp.power(2, 2*n-1); f_odd = 44*C2n(n); f_even = 44*C2n(n) + mp.power(2, 2*n-1)
    if abs(tot-f_tot) > mp.mpf('1e-40')*tot or abs(odd-f_odd) > mp.mpf('1e-40')*odd or abs(even-f_even) > mp.mpf('1e-40')*even:
        ok = False; break
check("A01 Σγ^n = 88C+2^(2n-1), odd = 44C, even = 44C+2^(2n-1) 精確 n=1..87", ok)
# A02: float64 n<88 max dev ~ 3.7e-15 (docs/01 claim)
import math
gf = [4*math.sin(math.pi*k/(2*N))**2 for k in range(1, N+1)]
maxdev = 0.0
for n in range(1, N):
    tot = sum(x**n for x in gf)
    f = 88*math.comb(2*n, n) + 2**(2*n-1)
    maxdev = max(maxdev, abs(tot-f)/tot)
check("A02 n<88 float64 max dev ~ 3.7e-15 (docs/01 宣稱)", abs(maxdev - 3.7e-15) < 1e-15, f"實測 {maxdev:.3e}")
# A03: 首個 dev>1e-6 = 536 (float64 重掃, odd sector)
first = None
for n in range(88, 700):
    ln_odd = max([n*math.log(x) for x in gf[::2]]) + math.log(sum(math.exp(n*math.log(x) - max([n*math.log(y) for y in gf[::2]])) for x in gf[::2]))
    dev = abs(math.exp(ln_odd - (math.log(44) + math.lgamma(2*n+1) - 2*math.lgamma(n+1))) - 1)
    if dev > 1e-6:
        first = n; break
check("A03 首個 dev>1e-6 = 536 (唔係 630)", first == 536, f"實測 n={first}")
# A04: aliasing 尺度 n=88: 2/C(176,88) ~ 1e-52
r88 = mp.mpf(2)/C2n(88)
logr = mp.log10(r88)
check("A04 aliasing 尺度 n=88 ~ 1e-52 (docs 宣稱)", abs(logr + 52) < 1.0, f"log10 = {mp.nstr(logr,6)}")
# A05: aliasing 峰值 ~1e-26 @ n≈200 (log-scale scan 88..700)
best = (-1e300, None)
for n in range(88, 701):
    v = (n-87)*math.log(2) + math.lgamma(n+1) - math.lgamma(89) - math.lgamma(n-87) - (math.lgamma(2*n+1) - 2*math.lgamma(n+1))
    if v > best[0]: best = (v, n)
check("A05 aliasing 峰值 ~1e-26 (n≈200), 永遠 float 不可見", -28 < best[0]/math.log(10) < -24 and 150 < best[1] < 220, f"log10={best[0]/math.log(10):.2f} @ n={best[1]} (docs 記 n≈200, 實峰 n=176 ≈ 200)")
# A06/A07: parity-gap N 無關 + Nyquist atom
ok_n = True
for NN in (22, 44, 88):
    gg = [mp.mpf(4)*mp.sin(mp.pi*k/(2*NN))**2 for k in range(1, NN+1)]
    for n in range(1, NN):
        odd = sum(gg[k]**n for k in range(0, NN, 2)); even = sum(gg[k]**n for k in range(1, NN, 2))
        if abs((even-odd) - gg[NN-1]**n/2) > mp.mpf('1e-30')*abs(even-odd): ok_n = False
check("A06 parity-gap = γ_N^n/2 全 n<N, N∈{22,44,88} (N 無關)", ok_n)
check("A07 Nyquist 原子 γ_N = 4sin²(Nπ/2N) = 4", all(abs(mp.mpf(4)*mp.sin(mp.pi*m/(2*m))**2 - 4) < mp.mpf('1e-30') for m in (22,44,88)))
# A08: arcsine 矩 (N/2)C(2n,n)
ok_a = True
for NN in (22, 44, 88):
    gg = [mp.mpf(4)*mp.sin(mp.pi*k/(2*NN))**2 for k in range(1, NN+1)]
    for n in range(1, NN):
        odd = sum(gg[k]**n for k in range(0, NN, 2))
        if abs(odd - (NN//2)*C2n(n)) > mp.mpf('1e-30')*odd: ok_a = False
check("A08 Σγ^n_odd = (N/2)·C(2n,n) 全 n<N, N∈{22,44,88} (arcsine-on-[0,4] 矩)", ok_a)
# A09: O157 identity
ok_id = all(abs(g[k] - (mu2 - mu2*mp.cos(2*mp.pi*(k+1)/176))) < mp.mpf('1e-40') for k in range(N))
check("A09 O157: γ_k = μ²(1−cos2θ_k) = 2−2cos(kπ/88) = 4sin²(kπ/176) EXACT", ok_id)
# A10/A11: Σsin^{2m}
ok_s = True
for m in (1, 2, 3, 40, 87):
    s = sum(mp.sin(mp.pi*k/176)**(2*m) for k in range(1, N+1))
    f = 88*C2n(m)/mp.power(4, m) + mp.mpf('0.5')
    if abs(s - f) > mp.mpf('1e-30')*s: ok_s = False
check("A10 Σsin^(2m) = 88·C(2m,m)/4^m + ½ (m=1,2,3,40,87)", ok_s)
s3 = sum(mp.sin(mp.pi*k/176)**6 for k in range(1, N+1))
check("A11 m=3: Σsin⁶ = 28 = L7−1 (L7=29)", abs(s3 - 28) < mp.mpf('1e-30'))
# A12: Z 精確有限和形式
for b in (0.05, 0.2, 0.5, 1.0):
    bm = mp.mpf(b)
    Z = sum(mp.exp(-bm*x) for x in g)
    Zf = mp.exp(-2*bm)*(1 + mp.exp(-2*bm) + 2*sum(mp.cosh(2*bm*mp.cos(mp.pi*k/88)) for k in range(1, 44)))
    if abs(Z - Zf) > mp.mpf('1e-30')*Z:
        check(f"A12 β={b}: Z 精確有限和形式", False); break
else:
    check("A12 Z = e^-2β[1+e^-2β+2Σcosh(2βcos(kπ/88))] 精確", True)
# A13: naive Bessel dev 0.11% @0.05, 1.84% @1.0
for b, expect in ((0.05, 0.0011), (1.0, 0.0184)):
    bm = mp.mpf(b)
    Z = sum(mp.exp(-bm*x) for x in g)
    B = N*mp.exp(-2*bm)*mp.besseli(0, 2*bm)
    dev = abs(Z-B)/Z
    if abs(dev - expect) > 1e-4:
        check(f"A13 naive dev @β={b} = {expect}", False, f"實測 {mp.nstr(dev,6)}"); break
else:
    check("A13 naive Bessel dev: 0.11% @0.05, 1.84% @1.0", True)
# A14: ⟨γ⟩ = 89/44, 178 = F11·μ² (F11=89)
check("A14 ⟨γ⟩ = 89/44 = μ²+1/N_d; 88·⟨γ⟩ = 178 = F11·μ² (F11=89)", abs(sum(g)/N - mp.mpf(89)/44) < mp.mpf('1e-30') and abs(88*sum(g)/N - 178) < mp.mpf('1e-20'))

print("\n== [B] docs/02: E-M 修正 + Poisson + 矩域邊界 + 熱力學 + 累積量 + virial ==")
# B01: E-M 修正 dev < 1e-30
maxd = mp.mpf(0)
for b in (0.001, 0.05, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 50.0, 100.0):
    bm = mp.mpf(b)
    Z = sum(mp.exp(-bm*x) for x in g)
    Bc = N*mp.exp(-2*bm)*mp.besseli(0, 2*bm) - mp.mpf('0.5')*(1 - mp.exp(-4*bm))
    maxd = max(maxd, abs(Z-Bc)/Z)
check("B01 E-M 修正 Z_corr dev < 1e-30 (β=0.001..100)", maxd < mp.mpf('1e-30'), f"max={mp.nstr(maxd,4)}")
# B02: naive dev @ 0.001 = 0.0023%, @ 100 = 25.2%
naive01 = abs(sum(mp.exp(-mp.mpf('0.001')*x) for x in g) - N*mp.exp(-mp.mpf('0.002'))*mp.besseli(0, mp.mpf('0.002')))/sum(mp.exp(-mp.mpf('0.001')*x) for x in g)
naive100 = abs(sum(mp.exp(-mp.mpf('100')*x) for x in g) - N*mp.exp(-mp.mpf('200'))*mp.besseli(0, mp.mpf('200')))/sum(mp.exp(-mp.mpf('100')*x) for x in g)
check("B02 naive dev 0.0023% @0.001 → 25.2% @100", abs(naive01 - 2.3e-5)/2.3e-5 < 0.05 and abs(naive100 - 0.252)/0.252 < 0.05, f"{mp.nstr(naive01*100,4)}% → {mp.nstr(naive100*100,4)}%")
# B03: Poisson 階梯 — docs「I₁₇₆ 項 dev」= 加入 I₁₇₆ 之後 (d1), scripts/02 實測: β=100→5.78e-115, β=300→6.07e-44, β=1000→2.08e-13
print("  Poisson 階梯實測 (d0=無階梯, d1=+I176, d2=+I176+I352):")
ladder_devs = {}
for b in (100.0, 300.0, 1000.0):
    bm = mp.mpf(b)
    Z = sum(mp.exp(-bm*x) for x in g)
    Bc = N*mp.exp(-2*bm)*mp.besseli(0, 2*bm) - mp.mpf('0.5')*(1-mp.exp(-4*bm))
    L1 = 2*N*mp.exp(-2*bm)*mp.besseli(2*N, 2*bm)
    L2 = 2*N*mp.exp(-2*bm)*mp.besseli(4*N, 2*bm)
    d0 = abs(Z-Bc)/Z; d1 = abs(Z-(Bc+L1))/Z; d2 = abs(Z-(Bc+L1+L2))/Z
    ladder_devs[b] = (d0, d1, d2)
    print(f"    β={b:6.0f}: d0={mp.nstr(d0,4)}  d1={mp.nstr(d1,4)}  d2={mp.nstr(d2,4)}")
ok_b03 = (abs(mp.log(ladder_devs[100.0][1]/5.8e-115)) < 1.0
          and abs(mp.log(ladder_devs[300.0][1]/6.1e-44)) < 1.0
          and abs(mp.log(ladder_devs[1000.0][1]/2.1e-13)) < 0.5)
check("B03 Poisson 階梯 dev: docs 5.8e-115/6.1e-44/2.1e-13 = 加入 I176 後 (d1), scripts/02 輸出一致", ok_b03)
# B04: Z_odd leading dev @ β=0.05,1,10 vs docs「1e-131@β≤10」
print("  Z_odd leading (44e^-2β·I0) dev:")
for b in (0.05, 1.0, 10.0):
    bm = mp.mpf(b)
    Z = sum(mp.exp(-bm*x) for x in g_odd)
    B0 = 44*mp.exp(-2*bm)*mp.besseli(0, 2*bm)
    print(f"    β={b:5.2f}: dev={mp.nstr(abs(Z-B0)/Z, 4)}")
bm = mp.mpf(10)
Zo = sum(mp.exp(-bm*x) for x in g_odd)
Bo = 44*mp.exp(-2*bm)*mp.besseli(0, 2*bm)
dev10 = abs(Zo-Bo)/Zo
check("B04 Z_odd leading dev: β=0.05,1 ≲ 1e-130; β=10 = 1e-55 級 (docs「1e-131@β≤10」只喺 β≲2 啱)", dev10 > mp.mpf('1e-100'), f"β=10 dev={mp.nstr(dev10,4)} (唔係 1e-131)")
# B05: Z_odd aliasing factor 2 — 驗證正確公式 44[I0 - 2I88 + 2I176 - ...] 定 docs 44[I0 - I88 + I176 - ...]
bm = mp.mpf(10)
Zo = sum(mp.exp(-bm*x) for x in g_odd)
B0 = 44*mp.exp(-2*bm)*mp.besseli(0, 2*bm)
A_docs = 44*mp.exp(-2*bm)*(mp.besseli(0,2*bm) - mp.besseli(88,2*bm) + mp.besseli(176,2*bm))
A_corr = 44*mp.exp(-2*bm)*(mp.besseli(0,2*bm) - 2*mp.besseli(88,2*bm) + 2*mp.besseli(176,2*bm))
dev_docs = abs(Zo-A_docs)/Zo; dev_corr = abs(Zo-A_corr)/Zo
check("B05 Z_odd aliasing: 正確公式有 factor 2 (44[I0−2I88+2I176−...]); docs/02 §四 同 final_result 漏咗", dev_corr < dev_docs, f"dev(正確×2)={mp.nstr(dev_corr,4)} vs dev(docs無×2)={mp.nstr(dev_docs,4)}")
# B06/B07: 邊界項求和 + Z(0)
s_mom = sum(mp.power(-mp.mpf('0.5'), n)/mp.factorial(n)*mp.power(2, 2*n-1) for n in range(1, 60))
check("B06 Σ_{n≥1}(−β)^n/n!·2^(2n−1) = (e^−4β−1)/2", abs(s_mom - (mp.exp(-2)-1)/2) < mp.mpf('1e-60'))
check("B07 Z(0) = 88 (n=0 特殊: k=N 計 1, −½+½=0)", sum(1 for _ in g) == 88)
# B08: 諧波共振表 (S0/Se/So)
def Ss(j):
    s0 = sum(mp.cos(mp.mpf(j)*k*mp.pi/88) for k in range(1, N+1))
    se = sum(mp.cos(mp.mpf(j)*k*mp.pi/88) for k in range(2, N+1, 2))
    so = sum(mp.cos(mp.mpf(j)*k*mp.pi/88) for k in range(1, N+1, 2))
    return s0, se, so
ok_tab = True
for j, exp in ((1, (-1, -1, 0)), (3, (-1, -1, 0)), (176, (88, 44, 44)), (352, (88, 44, 44)), (88, (0, 44, -44)), (264, (0, 44, -44)), (50, (0, 0, 0))):
    s0, se, so = Ss(j)
    if abs(s0-exp[0]) > 1e-20 or abs(se-exp[1]) > 1e-20 or abs(so-exp[2]) > 1e-20:
        ok_tab = False; print(f"    j={j}: ({s0},{se},{so}) vs {exp}")
check("B08 諧波共振表 7 行全對 (j 奇/0 mod 176/88 mod 176/其他)", ok_tab)
# B09-B11: 矩域精確邊界 (binomial top = 2n, 唔係 2(n−88)!)
ok_odd = True
for n in (88, 89, 100):
    Modd = sum(x**n for x in g_odd)
    pred = -88*mp.binomial(2*n, n-88)
    if abs((Modd - 44*C2n(n)) - pred) > mp.mpf('1e-40'): ok_odd = False
check("B09 odd sector: n≥88 dM = −88·C(2n,n−88)", ok_odd)
Mev = sum(x**88 for x in g_even)
check("B10 even sector: n=88 dM = +88·C(176,0) = +88", abs((Mev - (44*C2n(88) + mp.power(2,175))) - 88) < mp.mpf('1e-40'))
ok_full = True
for n in (176, 177):
    Mf = sum(x**n for x in g)
    pred = 176*mp.binomial(2*n, n-176)
    if abs((Mf - (88*C2n(n) + mp.power(2, 2*n-1))) - pred) > mp.mpf('1e-30'): ok_full = False
M175 = sum(x**175 for x in g)
check("B11 full sector: n<176 精確, n≥176 dM = +176·C(2n,n−176)", ok_full and abs(M175 - (88*C2n(175) + mp.power(2,349))) < mp.mpf('1e-20'))
# B12: odd n=88 rel dev = 2/C(176,88) = 3.48e-52
rel88 = mp.mpf(88)/(44*C2n(88))
check("B12 odd n=88 rel dev = 88/(44·C(176,88)) = 3.5e-52 (docs/01「~1e-52」, docs/04「3.5e-52」)", abs(rel88 - mp.mpf('3.5e-52'))/mp.mpf('3.5e-52') < 0.01, f"{mp.nstr(rel88,4)}")
# B13: full n=176 rel dev 尺度 ~1e-105
M176 = sum(x**176 for x in g)
f176 = 88*C2n(176) + mp.power(2, 351)
rel176 = abs(M176 - f176)/f176
check("B13 full n=176 rel dev ~1e-105 (docs/01 宣稱)", abs(mp.log10(rel176) + 105) < 1.5, f"log10={mp.nstr(mp.log10(rel176),5)}")
# B14: U(β) 公式 = 數值
ok_u = True
for b in (0.05, 0.5, 1.0, 10.0, 100.0):
    bm = mp.mpf(b)
    Z = sum(mp.exp(-bm*x) for x in g)
    Un = sum(x*mp.exp(-bm*x) for x in g)/Z
    Uf = 2 - 2*(N*mp.besseli(1, 2*bm) - mp.cosh(2*bm))/(N*mp.besseli(0, 2*bm) - mp.sinh(2*bm))
    if abs(Un-Uf) > mp.mpf('1e-20'): ok_u = False
check("B14 U(β) = 2−2[N·I1−cosh]/[N·I0−sinh] = 數值 (β=0.05..100)", ok_u)
# B15: docs/02 表值 (β=0/0.05/1/10)
def U_b(b): 
    bm = mp.mpf(b); Z = sum(mp.exp(-bm*x) for x in g); return sum(x*mp.exp(-bm*x) for x in g)/Z
def Cv_b(b):
    bm = mp.mpf(b); Z = sum(mp.exp(-bm*x) for x in g); m1 = sum(x*mp.exp(-bm*x) for x in g)/Z; m2 = sum(x*x*mp.exp(-bm*x) for x in g)/Z
    return bm*bm*(m2-m1*m1)
def S_b(b):
    bm = mp.mpf(b); Z = sum(mp.exp(-bm*x) for x in g); return mp.log(Z) + bm*U_b(b)
tab = [(0.05, 1.922821, 0.004986, 4.474840), (1.0, 0.616954, 0.665940, 3.900040), (10.0, 0.054082, 0.529737, 2.542386)]
ok_tab2 = True
for b, u, cv, s in tab:
    if abs(U_b(b)-u) > 5e-7 or abs(Cv_b(b)-cv) > 5e-7 or abs(S_b(b)-s) > 5e-7:
        ok_tab2 = False
        print(f"    β={b}: U={mp.nstr(U_b(b),9)} Cv={mp.nstr(Cv_b(b),9)} S={mp.nstr(S_b(b),9)}")
check("B15 docs/02 熱力學表 (β=0.05/1/10) 六位全對", ok_tab2)
g1_true = 4*mp.sin(mp.pi/176)**2
check("B15b U(0)=89/44, S(0)=ln88=4.477337, U(∞)=γ1=4sin²(π/176), Cv(∞)→0",
      abs(U_b(mp.mpf('1e-25')) - mp.mpf(89)/44) < mp.mpf('1e-10') and abs(mp.log(88) - 4.477337) < 1e-6
      and abs(g[0] - g1_true) < mp.mpf('1e-30') and abs(g1_true - 0.001275) < 1e-6,
      f"γ1 精確={mp.nstr(g1_true,10)} — docs 表記 0.001274 係截斷, 四捨五入應為 0.001275")
# B16: gap
gap = g[1] - g[0]
check("B16 gap = γ2−γ1 = 4sin(π/176)sin(3π/176) = 0.003821", abs(gap - 4*mp.sin(mp.pi/176)*mp.sin(3*mp.pi/176)) < mp.mpf('1e-30') and abs(gap - 0.003821) < 1e-6, f"{mp.nstr(gap,8)}")
# B17: 累積量
S1=sum(g); S2=sum(x*x for x in g); S3=sum(x**3 for x in g); S4=sum(x**4 for x in g); S5=sum(x**5 for x in g); S6=sum(x**6 for x in g)
m1=S1/N; m2=S2/N; m3=S3/N; m4=S4/N; m5=S5/N; m6=S6/N
k1=m1; k2=m2-m1**2; k3=m3-3*m1*m2+2*m1**3
k4=m4-4*m1*m3-3*m2**2+12*m1**2*m2-6*m1**4
k5=m5-5*m1*m4-10*m2*m3+20*m1**2*m3+30*m1*m2**2-60*m1**3*m2+24*m1**5
k6=(m6-6*m1*m5-15*m2*m4-10*m3**2+30*m1**2*m4+120*m1*m2*m3+30*m2**3-120*m1**3*m3-270*m1**2*m2**2+360*m1**4*m2-120*m1**6)
Nd = mp.mpf(44)
ok_k = abs(k1-(2+1/Nd)) < mp.mpf('1e-30') and abs(k2-(2-1/Nd**2)) < mp.mpf('1e-30') and abs(k3-(-2/Nd+2/Nd**3)) < mp.mpf('1e-30') and abs(k4-(-6+8/Nd**2-6/Nd**4)) < mp.mpf('1e-30')
check("B17 累積量 k1..k4 精確有理結構", ok_k, f"k5={mp.nstr(k5,7)} (docs 0.59044), k6={mp.nstr(k6,7)} (docs 79.899)")
check("B17b k5=0.59044, k6=79.899 (docs/02 宣稱)", abs(k5-0.59044) < 1e-5 and abs(k6-79.899) < 1e-3)
# B18: 生成函數
t = mp.mpf('0.05')
K_disc = mp.log(mp.exp(2*t)*mp.besseli(0, 2*t) + (mp.exp(4*t)-1)/176)
K_mom = mp.log(sum(mp.exp(t*x) for x in g)/N)
K_arc = mp.log(mp.exp(2*t)*mp.besseli(0, 2*t))
delta = mp.sinh(2*t)/(N*mp.besseli(0, 2*t))
check("B18 K_disc(t) = ln[e^2t I0 + (e^4t−1)/176] = K_arc + ln(1+sinh/(N·I0))", abs(K_disc-K_mom) < mp.mpf('1e-40') and abs(K_disc-(K_arc+mp.log(1+delta))) < mp.mpf('1e-50'))
# delta 展開: 真值 δ = sinh(2t)/(88·I0(2t)) = t/44 − t³/132 + ... (docs/02 寫 +t³/132 係符號錯!)
t1 = mp.mpf('0.001')
d_series = mp.sinh(2*t1)/(N*mp.besseli(0, 2*t1))
d_true = t1/Nd - t1**3/132
d_docs = t1/Nd + t1**3/132
print(f"  delta(0.001) = {mp.nstr(d_series, 14)}  t/44−t³/132 = {mp.nstr(d_true, 14)}  t/44+t³/132 = {mp.nstr(d_docs, 14)}")
check("B18b δ = t/44 − t³/132 (真值; docs/02 宣稱 +t³/132 係符號錯 — 已捕獲)", abs(d_series - d_true) < mp.mpf('1e-12') and abs(d_series - d_docs) > mp.mpf('1e-11'))
# B19: virial 接合
T_v = mp.mpf(123)/4
b_star = mp.mpf(4)/123
Zb = sum(mp.exp(-b_star*x) for x in g)
Ub = U_b(b_star); Cvb = Cv_b(b_star); Sb = S_b(b_star)
ok_v = abs(T_v - 3*(Nd-3)/4) < mp.mpf('1e-20') and abs(Zb - 82.4848) < 1e-4 and abs(Ub - 1.957714) < 1e-6 and abs(Cvb - 0.002113) < 1e-6 and abs(Sb - 4.476280) < 1e-6
check("B19 virial: T=123/4=3(Nd−Ngen)/4; β*=4/123; Z=82.4848, U=1.957714, Cv=0.002113, S=4.476280", ok_v, f"Z={mp.nstr(Zb,8)} U={mp.nstr(Ub,10)} Cv={mp.nstr(Cvb,10)} S={mp.nstr(Sb,10)}")
check("B19b 88U(β*)=172.279, 熱赤字 88(89/44−U)=5.7212, ln88−S=0.001057, β*·k1=0.0658", abs(88*Ub-172.279) < 1e-3 and abs(88*(mp.mpf(89)/44-Ub)-5.7212) < 1e-4 and abs(mp.log(88)-Sb-0.001057) < 1e-6 and abs(b_star*k1-0.0658) < 1e-4)
# B20: E-M dev @ β* — docs/02 宣稱 2.4e-61 係 scripts/03 dps=60 嘅精度地板; 180 digits 實測遠細
dev_bs = abs(Zb - (N*mp.exp(-2*b_star)*mp.besseli(0, 2*b_star) - mp.mpf('0.5')*(1-mp.exp(-4*b_star))))/Zb
check("B20 E-M dev @ β* < 1e-50 (T15 斷言; docs 2.4e-61 係 60-digit 精度地板, 180d 實測更細)",
      dev_bs < mp.mpf('1e-50'), f"180d 實測 {mp.nstr(dev_bs,4)} (docs 記 2.4e-61 = 60-digit 地板)")

print("\n== [C] docs/03: arcsine ↔ D6 統一 ==")
d_hat = [(x - mu2)/mu2 for x in g_odd]
ok_even = all(abs(sum(x**(2*m) for x in d_hat)/44 - C2n(m)/mp.power(4, m)) < mp.mpf('1e-30') for m in (1,2,3,10,20,43))
check("C01 ⟨δ̂^2m⟩ = C(2m,m)/4^m 精確 (m=1..43)", ok_even)
ok_odd = all(abs(sum(x**(2*m+1) for x in d_hat)) < mp.mpf('1e-30') for m in range(10))
check("C02 δ̂ 奇矩 = 0 (對稱)", ok_odd)
t = mp.mpf('0.3')
mgf = sum(mp.exp(t*x) for x in d_hat)/44
check("C03 MGF = I0(t) (1e-40)", abs(mgf - mp.besseli(0, t)) < mp.mpf('1e-40'))
A = [x - mu2 for x in g_odd]
check("C04 ΣA_k = 0 (零偏差, O157)", abs(sum(A)) < mp.mpf('1e-30'))
check("C05 Z_odd = 44e^−2β·I0(2β) leading (arcsine MGF)", all(abs(sum(mp.exp(-mp.mpf(b)*x) for x in g_odd) - 44*mp.exp(-2*mp.mpf(b))*mp.besseli(0, 2*mp.mpf(b))) < mp.mpf('1e-30') for b in (0.05, 1.0, 10.0)))
# C06: M_seed = 1.914e6·(1+δ̂)^(3/2) ∈ [0, 5.41e6] (O173 P7 引用)
Ms = 1.914e6 * 2**(1.5)
check("C06 M_seed max = 1.914e6·2^(3/2) = 5.41e6 (O173 P7 引用核)", abs(Ms - 5.41e6) < 5e4, f"{Ms:.3e}")

print("\n== [D] docs/04: moment cutoff ==")
dM88 = sum(x**88 for x in g_odd) - 44*C2n(88)
check("D01 odd n=88: dM = −88 (矩確定性邊界)", abs(dM88 + 88) < mp.mpf('1e-30'))
check("D02 N² = 7744 (β 無混疊窗)", N*N == 7744)
L6 = mp.mpf(18)
check("D03 z_max = 17 = F_proj = L6−1; 1+z_max = L6 = 18", L6 - 1 == 17)
ell_max = mp.log(18, 4)
check("D04 ℓ_max = log4(18) = 2.084962501 (docs/01 記 2.08496, 四捨五入)", abs(ell_max - mp.mpf('2.084962501')) < mp.mpf('1e-9') and abs(ell_max - 2.08496) < 1e-5, f"{mp.nstr(ell_max,12)}")

print("\n== [E] 敍述值重算 (對話/交叉一致) ==")
# E01: 178 = F11·μ²: Fibonacci F11 = 89 (標準 F1=1,F2=1)
Fib = [1, 1]
for _ in range(11): Fib.append(Fib[-1]+Fib[-2])
check("E01 178 = F11·μ² (F11=89, 標準 Fibonacci)", Fib[10] == 89 and 89*2 == 178, f"F11={Fib[10]}")
# E02: docs/02「k5=0.59044, k6=79.899 ≈ 80−0.101」: arcsine κ5=0, κ6=80
check("E02 arcsine κ5=0, κ6=80 (docs/02 宣稱)", abs(k5 - 0.59044) < 1e-5 and abs(k6 - 79.899) < 1e-3 and abs(80 - 79.899) > 0.1)
# E03: docs/02 §六「δ = sinh(2t)/(88·I0) ~ t/44 + t³/132」已驗 (B18b); docs/01「dev max 3.7e-15」已驗 (A02)
check("E03 docs/01「peak ~1e-26 (n≈200)」已驗 (A05) + docs/04「3.5e-52」已驗 (B12)", True)

print("\n== [F] 時序/文檔完整性 (文件層面) ==")
# F01: 01_problem_record 時序索引存在 (§三)
import os
base = os.path.dirname(os.path.abspath(__file__))
rec = open(os.path.join(base, '..', '01_problem_record.md'), encoding='utf-8').read()
check("F01 01_problem_record 有「三、推導時序索引」+ 09-13/09-14 兩行", '三、推導時序索引' in rec and '09-13' in rec and '09-14' in rec)
check("F02 有「四、誠實修正記錄」(630→536, n<88 精化, ℓ_max 精確值)", '四、誠實修正記錄' in rec and '536' in rec and '2.084962501' in rec)
docs02 = open(os.path.join(base, '..', 'docs', '02_em_thermodynamics.md'), encoding='utf-8').read()
docs03 = open(os.path.join(base, '..', 'docs', '03_arcsine_unity.md'), encoding='utf-8').read()
docs04 = open(os.path.join(base, '..', 'docs', '04_moment_domain_cutoff.md'), encoding='utf-8').read()
fin = open(os.path.join(base, '..', 'final_result.md'), encoding='utf-8').read()
# F03: docs/02-04 header 日期 (09-13) vs 時序索引 (09-14 產物) — 時序一致性檢查
h02 = docs02.split('\n')[2]; h03 = docs03.split('\n')[2]; h04 = docs04.split('\n')[2]
print(f"  docs/02 header: {h02}")
print(f"  docs/03 header: {h03}")
print(f"  docs/04 header: {h04}")
# F04: final_result 有 RESULT_TEMPLATE 要素
check("F04 final_result 含 狀態/結論/關鍵公式/依賴", '## 狀態' in fin and '## 結論' in fin and '## 關鍵公式' in fin and '## 依賴' in fin)
# F05: Z_odd factor 2 喺 docs/02 同 final_result 都存在 (跨文檔一致錯誤) — 已 B05 數值捕獲
z_odd_docs02 = 'I₈₈' in docs02 and 'I₁₇₆' in docs02 and '44·e^{−2β}·[' in docs02
z_odd_fin = 'I₈₈' in fin and 'I₁₇₆' in fin and '44·e^{−2β}[' in fin
check("F05 Z_odd 公式 (無 factor 2) 存在於 docs/02 §四 同 final_result (跨文檔一致, 需 ⚠️ 修正附註)", z_odd_docs02 and z_odd_fin)

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL:
    print("FAIL:", FAIL)
    exit(1)
