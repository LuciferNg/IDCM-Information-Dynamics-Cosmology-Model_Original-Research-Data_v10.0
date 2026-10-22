#!/usr/bin/env python3
# O193 scripts/03 — 鏈熱力學: U(beta), C_v(beta), S(beta) + O40 virial T = 123/4 接合
# 前置: scripts/02 (E-M 修正 Z = e^{-2b}[N*I0(2b) - sinh(2b)] + aliasing 階梯)
# 本 script (mpmath 60 digits):
#   I.  內能 U(b) = <gamma>(b) = 2 - 2[N*I1(2b)-cosh(2b)]/[N*I0(2b)-sinh(2b)]  (b << N^2)
#       b->0: U = 89/44 = mu^2 + 1/N_d;  b->inf: U -> gamma_1 (基態, 用精確和驗證)
#   II. 比熱 C_v(b) = b^2 * Var;  高溫 C_v ~ b^2 k2;  低溫指數衰減 (gap)
#   III. 熵 S(b) = ln Z + b*U;  S(0) = ln 88, S(inf) -> 0
#   IV. ★ 累積量精確結構 (mpmath + Fraction):
#       k1 = 2 + 1/44            (arcsine k1 = 2)
#       k2 = 2 - 1/44^2          (arcsine k2 = 2)
#       k3 = -2/44 + 2/44^3      (arcsine k3 = 0)
#       k4 = -6 + 8/44^2 - 6/44^4 (arcsine k4 = -6)
#       ★ 生成函數: K_disc(t) = ln[e^{2t}I0(2t) + (e^{4t}-1)/176] = K_arc(t) + ln[1 + sinh(2t)/(N*I0(2t))]
#        (176 = 2N 已經內含 /N; K_disc = ln(Z(-t)/N) = ln E[e^{tX}], 唔再額外 -ln N)
#       修正 = Nyquist 原子熱修飾 ln(1 + delta), delta = sinh(2t)/(N*I0(2t)) ~ t/44 - t^3/132 + ...
#   V.  O40 virial T = 123/4 = 3(N_d - N_gen)/4 -> b* = 4/123:
#       U(b*)=1.957714, C_v(b*)=0.0021128, S(b*)=4.47628 (高溫區, S ~ ln 88)
#       E-M 修正 Bessel 喺 b* 嘅 dev = 2.4e-61
#   VI. 低溫 gap = gamma_2 - gamma_1 = 4 sin(pi/176) sin(3pi/176)
# 規則: stdlib + mpmath only

import mpmath as mp
mp.mp.dps = 60

N = 88
g = [mp.mpf(4)*mp.sin(mp.pi*k/(2*N))**2 for k in range(1, N+1)]

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

def Z(b): return sum(mp.exp(-b*x) for x in g)
def U_num(b): return sum(x*mp.exp(-b*x) for x in g)/Z(b)
def U2_num(b): return sum(x*x*mp.exp(-b*x) for x in g)/Z(b)
def U_f(b):
    return 2 - 2*(N*mp.besseli(1, 2*b) - mp.cosh(2*b))/(N*mp.besseli(0, 2*b) - mp.sinh(2*b))
def Cv_num(b): return b*b*(U2_num(b) - U_num(b)**2)

# ================= Part I: U(beta) =================
print("== Part I: U(b) 內能 ==")
for b in (0.00001, 0.05, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 100.0):
    bm = mp.mpf(b)
    u1 = U_num(bm); u2 = U_f(bm)
    print(f"  beta={b:8.2f}  U_num={mp.nstr(u1, 10)}  U_formula={mp.nstr(u2, 10)}  match={abs(u1-u2)<mp.mpf('1e-20')}")
check("T01 U(b) 公式 = 數值 (beta=0.00001..100, 公式域 b << N^2=7744)", 
      all(abs(U_num(mp.mpf(b))-U_f(mp.mpf(b))) < mp.mpf('1e-20') for b in (0.00001, 0.05, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 100.0)))
b0 = mp.mpf('1e-25')
u_b0 = U_f(b0)
check("T02 U(0) = 89/44 = mu^2 + 1/N_d (equipartition 預算 178 = 88*U(0))",
      abs(u_b0 - mp.mpf(89)/44) < mp.mpf('1e-12') and abs(88*u_b0 - 178) < mp.mpf('1e-9'), f"U(0)={mp.nstr(u_b0, 14)}")
# 基態: 用精確和 (公式喺 b >> N^2 失效 — aliasing 主導)
g1 = g[0]
u_inf = U_num(mp.mpf(1e6))
check("T03 U(inf) -> gamma_1 (基態 k=1; 精確和驗證; 公式域限 b << N^2)", abs(u_inf - g1) < mp.mpf('1e-10'),
      f"U(1e6)={mp.nstr(u_inf, 10)} vs gamma_1={mp.nstr(g1, 10)}")

# ================= Part II: C_v(beta) =================
print("\n== Part II: C_v(b) = b^2 dU/db = b^2 * Var ==")
for b in (0.05, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0):
    bm = mp.mpf(b)
    cv = Cv_num(bm)
    print(f"  beta={b:5.2f}  C_v={mp.nstr(cv, 10)}")
k2 = mp.mpf(2) - mp.mpf(1)/1936
cv_small = Cv_num(mp.mpf('1e-12'))/(mp.mpf('1e-24'))
check("T04 高溫極限: C_v/b^2 -> k2 = mu^2 - 1/N_d^2", abs(cv_small - k2) < mp.mpf('1e-6'),
      f"C_v/b^2 @1e-12 = {mp.nstr(cv_small, 10)} vs k2={mp.nstr(k2, 10)}")
gap = g[1] - g[0]
cv_cold = Cv_num(mp.mpf(2000.0))
approx = mp.mpf(2000.0)**2 * gap**2 * mp.exp(-2000.0*gap)
check("T05 低溫: C_v 指數衰減 (gapped spectrum), 兩能級近似同尺度", abs(cv_cold/approx - 1) < 0.05,
      f"ratio={mp.nstr(cv_cold/approx, 6)}")
check("T06 gap = gamma_2 - gamma_1 = 4 sin(pi/176) sin(3pi/176)", abs(gap - 4*mp.sin(mp.pi/176)*mp.sin(3*mp.pi/176)) < mp.mpf('1e-30'),
      f"gap={mp.nstr(gap, 12)}")

# ================= Part III: S(beta) =================
print("\n== Part III: S(b) = ln Z + b*U ==")
S0 = mp.log(88)
S_inf = mp.log(Z(mp.mpf(1e6))) + mp.mpf(1e6)*U_num(mp.mpf(1e6))
check("T07 S(0) = ln 88 (最大熵)", abs(mp.log(Z(mp.mpf('1e-25'))) - S0) < mp.mpf('1e-12'), f"ln 88 = {mp.nstr(S0, 10)}")
check("T08 S(inf) -> 0 (基態佔據)", abs(S_inf) < mp.mpf('1e-6'), f"S(1e6) = {mp.nstr(S_inf, 8)}")

# ================= Part IV: 累積量精確結構 =================
print("\n== Part IV: ★ 累積量精確結構 (arcsine + Nyquist 修飾) ==")
S1 = sum(x for x in g); S2 = sum(x*x for x in g); S3 = sum(x**3 for x in g); S4 = sum(x**4 for x in g)
S5 = sum(x**5 for x in g); S6 = sum(x**6 for x in g)
m1 = S1/N; m2 = S2/N; m3 = S3/N; m4 = S4/N; m5 = S5/N; m6 = S6/N
k1 = m1; k2 = m2 - m1**2
k3 = m3 - 3*m1*m2 + 2*m1**3
k4 = m4 - 4*m1*m3 - 3*m2**2 + 12*m1**2*m2 - 6*m1**4
k5 = m5 - 5*m1*m4 - 10*m2*m3 + 20*m1**2*m3 + 30*m1*m2**2 - 60*m1**3*m2 + 24*m1**5
k6 = (m6 - 6*m1*m5 - 15*m2*m4 - 10*m3**2 + 30*m1**2*m4 + 120*m1*m2*m3 + 30*m2**3
      - 120*m1**3*m3 - 270*m1**2*m2**2 + 360*m1**4*m2 - 120*m1**6)
Nd = mp.mpf(44)
print(f"  k1 = {mp.nstr(k1, 15)}   pred 2 + 1/44 = {mp.nstr(2 + 1/Nd, 15)}")
print(f"  k2 = {mp.nstr(k2, 15)}   pred 2 - 1/44^2 = {mp.nstr(2 - 1/Nd**2, 15)}")
print(f"  k3 = {mp.nstr(k3, 15)}   pred -2/44 + 2/44^3 = {mp.nstr(-2/Nd + 2/Nd**3, 15)}")
print(f"  k4 = {mp.nstr(k4, 15)}   pred -6 + 8/44^2 - 6/44^4 = {mp.nstr(-6 + 8/Nd**2 - 6/Nd**4, 15)}")
print(f"  k5 = {mp.nstr(k5, 12)}   (arcsine k5 = 0)")
print(f"  k6 = {mp.nstr(k6, 12)}   (arcsine k6 = 80)")
check("T09 k1 = 2 + 1/N_d (mu^2 + 1/N_d)", abs(k1 - (2 + 1/Nd)) < mp.mpf('1e-30'))
check("T10 k2 = 2 - 1/N_d^2", abs(k2 - (2 - 1/Nd**2)) < mp.mpf('1e-30'))
check("T11 k3 = -2/N_d + 2/N_d^3", abs(k3 - (-2/Nd + 2/Nd**3)) < mp.mpf('1e-30'))
check("T12 k4 = -6 + 8/N_d^2 - 6/N_d^4", abs(k4 - (-6 + 8/Nd**2 - 6/Nd**4)) < mp.mpf('1e-30'))

# ★ 生成函數: K_disc(t) = K_arc(t) + ln[1 + sinh(2t)/(N*I0(2t))] - ln N
# 驗證: 用 t 展開兩邊一致 (t 細)
print("\n  ★ 生成函數: K_disc(t) = ln[e^{2t}I0(2t) + sinh(2t)/N] - ln N   (= K_arc + ln[1 + sinh/(N*I0)] - ln N)")
t = mp.mpf('0.05')
# Z(-t)/88 = e^{2t}I0(2t) - (1-e^{4t})/176   (E-M 修正式, t = -beta)
K_disc = mp.log(mp.exp(2*t)*mp.besseli(0, 2*t) + (mp.exp(4*t) - 1)/176)
K_mom = mp.log(sum(mp.exp(t*x) for x in g)/N)
check("T13 生成函數: K_disc(t) = ln[e^{2t}I0(2t) + (e^{4t}-1)/176] = ln E[e^{tX}]",
      abs(K_disc - K_mom) < mp.mpf('1e-40'),
      f"{mp.nstr(K_disc, 12)} vs {mp.nstr(K_mom, 12)}")
# 修正項分解: delta = sinh(2t)/(N*I0(2t)) ~ t/44 + t^3/132 + ...
delta = mp.sinh(2*t)/(N*mp.besseli(0, 2*t))
K_arc = mp.log(mp.exp(2*t)*mp.besseli(0, 2*t))
corr = mp.log(1 + delta)
K_check = K_arc + corr
check("T14 K_disc = K_arc + ln(1+delta) (Nyquist 熱修飾分解)", abs(K_disc - K_check) < mp.mpf('1e-50'),
      f"{mp.nstr(K_disc, 12)} vs {mp.nstr(K_check, 12)}")

# ================= Part V: O40 virial T = 123/4 接合 =================
print("\n== Part V: O40 virial T = 123/4 -> b* = 4/123 ==")
T_v = mp.mpf(123)/4
b_star = mp.mpf(4)/123
U_star = U_num(b_star); Cv_star = Cv_num(b_star); S_star = mp.log(Z(b_star)) + b_star*U_star
Z_star = Z(b_star)
print(f"  T_virial = 123/4 = {mp.nstr(T_v, 8)}  (= 3(N_d-N_gen)/4 = {mp.nstr(3*mp.mpf(44-3)/4, 8)})")
print(f"  b* = 4/123 = {mp.nstr(b_star, 10)}")
print(f"  Z(b*) = {mp.nstr(Z_star, 10)}")
print(f"  U(b*) = {mp.nstr(U_star, 12)}   (<gamma>(0) = {mp.nstr(mp.mpf(89)/44, 12)})")
print(f"  C_v(b*) = {mp.nstr(Cv_star, 12)}")
print(f"  S(b*) = {mp.nstr(S_star, 12)}   (ln 88 = {mp.nstr(S0, 12)}, 差 {mp.nstr(S0-S_star, 6)})")
print(f"  88*U(b*) = {mp.nstr(88*U_star, 10)}  (178 = equipartition)")
print(f"  熱赤字 88*(U(0)-U(b*)) = {mp.nstr(88*(mp.mpf(89)/44 - U_star), 10)}")
# b* 喺 E-M 修正 Bessel 嘅精確度
dev_bstar = abs(Z_star - (N*mp.exp(-2*b_star)*mp.besseli(0, 2*b_star) - mp.mpf(0.5)*(1-mp.exp(-4*b_star))))/Z_star
check("T15 Z(b*) 用 E-M 修正 Bessel dev < 1e-50 (高溫區, b* << N^2)", dev_bstar < mp.mpf('1e-50'), f"dev={mp.nstr(dev_bstar, 3)}")
# 累積量展開交叉驗證
U_exp = k1 - b_star*k2 + b_star**2*k3/2 - b_star**3*k4/6 + b_star**4*k5/24 - b_star**5*k6/120
check("T16 U(b*) = 累積量展開 (6 階)", abs(U_exp - U_star) < mp.mpf('1e-8'), f"dev={mp.nstr(abs(U_exp-U_star), 4)}")
lnZ_exp = S0 + sum(kk*mp.power(-b_star, n)/mp.factorial(n) for n, kk in ((1,k1),(2,k2),(3,k3),(4,k4),(5,k5)))
S_exp = lnZ_exp + b_star*U_exp
check("T17 S(b*) = 累積量展開 (5 階)", abs(S_exp - S_star) < mp.mpf('1e-6'), f"dev={mp.nstr(abs(S_exp-S_star), 4)}")
check("T18 S(b*) < ln 88 (熱激活降低熵, 高溫區差 0.00106)", S_star < S0, f"delta S = {mp.nstr(S0-S_star, 6)}")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL:
    print("FAIL:", FAIL)
    exit(1)
