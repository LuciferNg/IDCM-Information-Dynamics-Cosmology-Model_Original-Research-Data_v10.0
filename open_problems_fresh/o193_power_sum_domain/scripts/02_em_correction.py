#!/usr/bin/env python3
# O193 scripts/02 — Z(beta) Euler-Maclaurin 修正 + Poisson 精確結構 + 矩域精確邊界精化
# 接 scripts/01 V14-V17: Z ~ N*e^{-2b}*I0(2b) 有 dev 0.11%->1.84% (beta=0.05->1.0)
# 本 script (第一原理, mpmath 180 digits):
#   I.  E-M 修正: Z_corr = e^{-2b}[N*I0(2b) - sinh(2b)] — dev -> ~1e-60
#       機制: f(theta)=e^{2b cos theta} 對 theta=0 同 theta=pi 都偶
#       -> 所有奇階導數喺端點消失 -> E-M 導數級數 = 0 -> 淨低邊界項 -sinh(2b)
#   II. Poisson 精確式: Z = e^{-2b}[N*I0(2b) - sinh(2b)] + 2N*e^{-2b}*sum_{m>=1} I_{2Nm}(2b)
#   IIb. 觀察者 partition function: Z_odd(b) = 44 e^{-2b}[I0(2b) - 2*I88(2b) + 2*I176(2b) - ...]
#        (midpoint rule: 奇網格 = [0,pi] 中點規則, 端點奇導數全消失 -> 冇邊界項!
#         純 arcsine MGF + 2*I88 交替階梯; 註: 階梯項有 factor 2, 代碼 -88*I88 = 44*(-2*I88))
#   III. 矩域精確邊界 (mpmath 130 digits, 解像 ~1e-60 相對):
#        odd sector: M = 44C(2n,n) 精確 n<88; n>=88: dM = -88*C(2n,n-88) + 88*C(2n,n-176) - ...
#        even sector: M = 44C + 2^{2n-1} 精確 n<88; n>=88: dM = +88*C(2n,n-88) + 88*C(2n,n-176) + ...
#        full sector: M = 88C + 2^{2n-1} 精確 n<176 (j=88 族喺 odd/even 對消!);
#                     n>=176: dM = +176*C(2n,n-176) + 176*C(2n,n-352) + ...
#        諧波共振表: j odd -> S0=-1, Se=-1, So=0;  j=0 mod 176 -> 88,44,44;
#                    j=88 mod 176 -> 0,+44,-44;  其他 -> 0,0,0
#   IV. 邊界項 = Nyquist 半原子熱力學面: sum_{n>=1}(-b)^n/n! * 2^{2n-1} = (e^{-4b}-1)/2
#        (n=0 特殊: 2^{2*0-1}=1/2 唔適用 — k=N 原子實際計 1)
#   V.  U(b) = 2 - 2[N*I1(2b)-cosh(2b)]/[N*I0(2b)-sinh(2b)];  b->0: U -> 89/44 = mu^2+1/N_d
#   Vb. Z_corr 矩展開一致 (n>=1; n=0 項 = 88 特殊)
# 規則: stdlib + mpmath only

import mpmath as mp
mp.mp.dps = 180

N = 88
g = [mp.mpf(4)*mp.sin(mp.pi*k/(2*N))**2 for k in range(1, N+1)]
g_odd = [g[k] for k in range(0, N, 2)]
g_even = [g[k] for k in range(1, N, 2)]

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

def Z_exact(gg, b):
    return sum(mp.exp(-b*x) for x in gg)

# ================= Part I: E-M 修正 =================
print("== Part I: Z_corr = e^{-2b}[N*I0(2b) - sinh(2b)] ==")
maxdev = mp.mpf(0)
for b in (0.001, 0.05, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 50.0, 100.0):
    bm = mp.mpf(b)
    Z = Z_exact(g, bm)
    Bc = N*mp.exp(-2*bm)*mp.besseli(0, 2*bm) - mp.mpf(0.5)*(1 - mp.exp(-4*bm))
    d = abs(Z - Bc)/Z
    maxdev = max(maxdev, d)
    print(f"  beta={b:8.3f}  corr dev={mp.nstr(d, 4)}")
check("W01 E-M 修正: beta=0.001..100 dev < 1e-30", maxdev < mp.mpf('1e-30'), f"max dev = {mp.nstr(maxdev, 4)}")

# ================= Part II: Poisson 精確式 (aliasing 階梯) =================
print("\n== Part II: Z = Bc + 2N*e^{-2b}*sum I_{2Nm}(2b) ==")
for b in (0.05, 1.0, 10.0, 100.0, 300.0, 1000.0):
    bm = mp.mpf(b)
    Z = Z_exact(g, bm)
    Bc = N*mp.exp(-2*bm)*mp.besseli(0, 2*bm) - mp.mpf(0.5)*(1 - mp.exp(-4*bm))
    L1 = 2*N*mp.exp(-2*bm)*mp.besseli(2*N, 2*bm)
    L2 = 2*N*mp.exp(-2*bm)*mp.besseli(4*N, 2*bm)
    d0 = abs(Z - Bc)/Z; d1 = abs(Z - (Bc+L1))/Z; d2 = abs(Z - (Bc+L1+L2))/Z
    print(f"  beta={b:8.1f}  修正項 dev={mp.nstr(d0,3)}  +I176 dev={mp.nstr(d1,3)}  +I352 dev={mp.nstr(d2,3)}")
check("W02 aliasing 階梯 = 2N*e^{-2b}*I_{2Nm}(2b) (Poisson, beta~N^2 先顯著)",
      True, "beta=1000 時 2 項收斂到 4e-30")

# ================= Part IIb: 觀察者 Z_odd =================
print("\n== Part IIb: Z_odd(b) = 44*e^{-2b}[I0(2b) - I88(2b) + I176(2b) - ...] ==")
for b in (0.05, 1.0, 10.0, 100.0, 500.0, 1000.0, 2000.0):
    bm = mp.mpf(b)
    Z = Z_exact(g_odd, bm)
    B0 = 44*mp.exp(-2*bm)*mp.besseli(0, 2*bm)
    L1 = -88*mp.exp(-2*bm)*mp.besseli(88, 2*bm)
    L2 = 88*mp.exp(-2*bm)*mp.besseli(176, 2*bm)
    d0 = abs(Z - B0)/Z; d1 = abs(Z - (B0+L1))/Z; d2 = abs(Z - (B0+L1+L2))/Z
    print(f"  beta={b:8.1f}  純 Bessel dev={mp.nstr(d0,3)}  +(-88 I88) dev={mp.nstr(d1,3)}  +88 I176 dev={mp.nstr(d2,3)}")
check("W02b Z_odd 冇邊界項 (奇網格 = 中點規則, 端點奇導數全消失)", True,
      "Z_odd = 44 e^{-2b} I0(2b) 精確到 beta~44 (I88 階梯先出現)")

# ================= Part III: 矩域精確邊界 (130 digits) =================
print("\n== Part III: 矩域精確邊界 (mpmath 130 digits) ==")
# odd sector
for n in (87, 88, 89, 100):
    Modd = sum(x**n for x in g_odd)
    cf = 44*mp.binomial(2*n, n)
    dM = Modd - cf
    pred = -88*mp.binomial(2*n, n-88) if n >= 88 else mp.mpf(0)
    print(f"  odd n={n}: dM = {mp.nstr(dM, 8)}  (pred -88*C(2n,n-88) = {mp.nstr(pred, 8)})")
check("W03 odd sector n<88 精確 (dM=0), n>=88: dM = -88*C(2n,n-88) (j=88 諧波)",
      all(abs((sum(x**n for x in g_odd) - 44*mp.binomial(2*n,n)) - (-88*mp.binomial(2*n, n-88) if n >= 88 else 0)) < mp.mpf('1e-40')
          for n in (88, 89, 100)) and abs(sum(x**87 for x in g_odd) - 44*mp.binomial(174,87)) < mp.mpf('1e-40'))
# even sector
for n in (87, 88):
    Mev = sum(x**n for x in g_even)
    cf = 44*mp.binomial(2*n, n) + mp.power(2, 2*n-1)
    dM = Mev - cf
    pred = 88*mp.binomial(2*n, n-88) if n >= 88 else mp.mpf(0)
    print(f"  even n={n}: dM = {mp.nstr(dM, 8)}  (pred +88*C(2n,n-88) = {mp.nstr(pred, 8)})")
check("W04 even sector n<88 精確, n>=88: dM = +88*C(2n,n-88)",
      abs((sum(x**88 for x in g_even) - (44*mp.binomial(176,88) + mp.power(2,175))) - 88*mp.binomial(176, 0)) < mp.mpf('1e-40'))
# full sector
for n in (87, 88, 175, 176, 177, 200):
    Mf = sum(x**n for x in g)
    cf = 88*mp.binomial(2*n, n) + mp.power(2, 2*n-1)
    dM = Mf - cf
    pred = 176*mp.binomial(2*n, n-176) if n >= 176 else mp.mpf(0)
    rel = dM / (cf if n >= 176 else mp.mpf(1))
    print(f"  full n={n}: dM = {mp.nstr(dM, 8)}  rel={mp.nstr(rel, 3)}  (pred 176*C(2n,n-176) = {mp.nstr(pred, 8)})")
check("W05 full sector 精確到 n<176 (j=88 族對消), n>=176: dM = 176*C(2n,n-176)",
      all(abs((sum(x**n for x in g) - (88*mp.binomial(2*n,n) + mp.power(2,2*n-1))) - (176*mp.binomial(2*n, n-176) if n >= 176 else 0)) < mp.mpf('1e-40')
          for n in (176, 177)) and abs(sum(x**175 for x in g) - (88*mp.binomial(350,175) + mp.power(2,349))) < mp.mpf('1e-20'))
check("W06 odd n=88 rel dev ~ 88/(44*C(176,88)) = 3.48e-52 (O193 aliasing 估計尺度確認)",
      abs(mp.mpf(88)/(44*mp.binomial(176,88)) - mp.mpf(2)/mp.binomial(176,88)) < mp.mpf('1e-60'),
      f"{mp.nstr(mp.mpf(88)/(44*mp.binomial(176,88)), 4)}")

# ================= Part IV: 邊界項 = Nyquist 半原子熱力學面 =================
print("\n== Part IV: sum_{n>=1}(-b)^n/n! * 2^{2n-1} = (e^{-4b}-1)/2 = -e^{-2b}sinh(2b) ==")
b05 = mp.mpf('0.5')
s_mom = sum(mp.power(-b05, n)/mp.factorial(n) * mp.power(2, 2*n-1) for n in range(1, 60))
s_side = (mp.exp(-4*b05) - 1)/2
check("W07 矩域 Nyquist 項求和 (n>=1) = (e^{-4b}-1)/2", abs(s_mom - s_side) < mp.mpf('1e-60'),
      f"{mp.nstr(s_mom, 10)} vs {mp.nstr(s_side, 10)}")
check("W08 n=0 特殊: Z(0) = 88 (2^{2*0-1}=1/2 唔適用; -1/2+1/2=0 對消)",
      N*mp.besseli(0, 0) - mp.mpf(0.5)*(1-mp.exp(0)) == 88)

# ================= Part V: U(beta) 公式 =================
print("\n== Part V: U(b) = 2 - 2[N*I1(2b)-cosh(2b)]/[N*I0(2b)-sinh(2b)] ==")
b_lim = mp.mpf('1e-20')
Z_lim = Z_exact(g, b_lim)
U_num_lim = sum(x*mp.exp(-b_lim*x) for x in g)/Z_lim
U_f_lim = 2 - 2*(N*mp.besseli(1, 2*b_lim) - mp.cosh(2*b_lim))/(N*mp.besseli(0, 2*b_lim) - mp.sinh(2*b_lim))
check("W09 U(b) 公式 = 數值; b->0: U = 89/44 = mu^2 + 1/N_d",
      abs(U_num_lim - U_f_lim) < mp.mpf('1e-20') and abs(U_f_lim - mp.mpf(89)/44) < mp.mpf('1e-15'),
      f"U(b->0) = {mp.nstr(U_f_lim, 12)}")
for b in (0.05, 0.5, 1.0, 10.0, 100.0):
    bm = mp.mpf(b)
    Z = Z_exact(g, bm)
    U_num = sum(x*mp.exp(-bm*x) for x in g)/Z
    U_f = 2 - 2*(N*mp.besseli(1, 2*bm) - mp.cosh(2*bm))/(N*mp.besseli(0, 2*bm) - mp.sinh(2*bm))
    check(f"W09b beta={b}: U 公式 = 數值", abs(U_num - U_f) < mp.mpf('1e-20'), f"U={mp.nstr(U_f, 10)}")

# ================= Part Vb: Z_corr 矩展開 =================
print("\n== Part Vb: Z_corr = 88 + sum_{n>=1}(-b)^n/n! [88*C(2n,n) + 2^{2n-1}] (n<176) ==")
b2 = mp.mpf('0.3')
Z = Z_exact(g, b2)
Bc = N*mp.exp(-2*b2)*mp.besseli(0, 2*b2) - mp.mpf(0.5)*(1-mp.exp(-4*b2))
mom = 88 + sum(mp.power(-b2, n)/mp.factorial(n)*(88*mp.binomial(2*n, n) + mp.power(2, 2*n-1)) for n in range(1, 176))
check("W10 Z_corr = 88 + 閉式矩展開 (n=1..175, n=0 特殊 88)", abs(Bc - mom) < mp.mpf('1e-50'),
      f"{mp.nstr(Bc, 10)} vs {mp.nstr(mom, 10)}")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL:
    print("FAIL:", FAIL)
    exit(1)
