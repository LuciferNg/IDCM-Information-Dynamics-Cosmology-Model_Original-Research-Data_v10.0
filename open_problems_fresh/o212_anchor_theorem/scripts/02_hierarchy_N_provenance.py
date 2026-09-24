#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O212 script 02 — 階層數 N 嘅來源 (Hierarchy N Provenance)
==========================================================
SESSION_START 唯一剩餘真問題:
  「階層數 N = tau/t_Pl = 7.8695e60 為何係呢個值?」

方法:
  C1  BBN 鎖定重現 (O73 docs/04): eta_B(obs)+T_CMB+Omega_b -> omega_ring
  C2  Omega_b 版本敏感度 (O73 O5-1): 19/450 -> 72.73 ; 3/60 -> 66.834
  C3  N = tau/t_Pl 兩個約定 (omega_ring=72.59 錨 / 72.73 BBN); 差 = c_W/c
  C4  ★ 精確無量綱恆等式:
        N^2 = [3pi/(16 zeta(3))] * (Omega_b/eta_B) * (m_Pl/m_p)^4 * (m_p c^2/(k_B T))^3
  C5  N <-> G 一一對應 (G_implied = c^5/(hbar*omega_ring^2*N^2))
  C6  null test: N = f(結構數)? (O200 同款池 + 密度基準)
  C7  剛性: 由恆等式解析 log-導數 vs 數值擾動
  C8  可證偽清單

Run: /usr/bin/python3 scripts/02_hierarchy_N_provenance.py
"""
import mpmath as mp
import random, math
from fractions import Fraction as F
from bisect import bisect_left

mp.mp.dps = 40
random.seed(20260924)

# ---- 單位常數 ----
c     = mp.mpf('299792458')
hbar  = mp.mpf('6.62607015e-34')/(2*mp.pi)
kB    = mp.mpf('1.380649e-23')
echg  = mp.mpf('1.602176634e-19')
G     = mp.mpf('6.67430e-11')
Mpc   = mp.mpf('3.0856775814913673e22')
m_p   = mp.mpf('1.67262192369e-27')
zeta3 = mp.zeta(3)
T_CMB = mp.mpf('2.72548')
eta_B = mp.mpf('6.104e-10')          # O73 方向 B: D/H 核網絡 (無 H0)
omega_anchor = mp.mpf('72.59e3')/Mpc # O11 距離階梯錨 (結構值)
Om_b_old = F(19,450); Om_b_new = F(3,60)

m_Pl = mp.sqrt(hbar*c/G); t_Pl = mp.sqrt(hbar*G/c**5)

print("="*94)
print("O212 ② 階層數 N 嘅來源")
print("="*94)

# ---- n_gamma 同 BBN 鏈 ----
def _frac(x):
    return mp.mpf(x.numerator)/mp.mpf(x.denominator) if hasattr(x,'numerator') else mp.mpf(x)

def omega_from_chain(Om_b, T=T_CMB, eta=eta_B):
    """Om_b 為 Fraction 或 mpf; 回傳 omega_ring (rad/s)"""
    n_gamma = 2*zeta3/mp.pi**2 * (kB*T/(hbar*c))**3
    rho_c   = eta*m_p*n_gamma/_frac(Om_b)
    return mp.sqrt(8*mp.pi*G*rho_c/3)

def to_km_s_Mpc(w): return w*Mpc/mp.mpf('1e3')

# ================= C1 =================
print("\n[C1] BBN 鎖定重現 (O73 docs/04 方向 B: 觀測 -> omega_ring)")
w_old = omega_from_chain(Om_b_old)
print(f"    Omega_b = 19/450 = {float(Om_b_old):.6f}")
print(f"    n_gamma = {mp.nstr(2*zeta3/mp.pi**2*(kB*T_CMB/(hbar*c))**3, 8)} m^-3  (實測 4.107e8)")
print(f"    omega_ring = {mp.nstr(to_km_s_Mpc(w_old), 8)} (km/s)/Mpc   vs 72.59 -> dev {float(abs(to_km_s_Mpc(w_old)/72.59-1))*100:.4f}%")
c1 = abs(to_km_s_Mpc(w_old)/72.59-1) < mp.mpf('0.005')
print(f"    {'PASS' if c1 else 'FAIL'} (O73 註冊 72.73, dev 0.19%)")

# ================= C2 =================
print("\n[C2] Omega_b 版本敏感度 (O73 已註冊 O5-1, 未裁定)")
w_new = omega_from_chain(Om_b_new)
print(f"    Omega_b = 3/60 = {float(Om_b_new):.6f}  -> omega_ring = {mp.nstr(to_km_s_Mpc(w_new), 8)}")
print(f"      vs 結構 72.59 : {float((to_km_s_Mpc(w_new)/72.59-1))*100:+.2f}%")
print(f"      vs Planck 67.36: {float((to_km_s_Mpc(w_new)/67.36-1))*100:+.2f}%")
print(f"      vs CMB 投影 67.407: {float((to_km_s_Mpc(w_new)/67.407-1))*100:+.2f}%")
c2 = abs(to_km_s_Mpc(w_new)/mp.mpf('66.834')-1) < mp.mpf('0.002')
print(f"    {'PASS' if c2 else 'FAIL'} (O73 快照註冊 66.834, -8.11%)")
print("    ==> BBN 鎖定係【Omega_b 版本敏感】; 現行 Omega_b 未裁定 (O5-1)")
print("    ==> 現階段 omega_ring = 72.59 仍係【觀測錨】(O11 距離階梯), 唔係 BBN 預言")

# ================= C3 =================
print("\n[C3] N = tau/t_Pl 兩個約定")
N_anchor = (1/omega_anchor)/t_Pl
N_bbn    = (1/w_old)/t_Pl
print(f"    N(omega_ring = 72.59 錨)   = {mp.nstr(N_anchor,10)}")
print(f"    N(omega_ring = 72.73 BBN)  = {mp.nstr(N_bbn,10)}   (O200 註冊 7.869511471e60)")
dev_bbn = abs(N_bbn/mp.mpf('7.869511471e60')-1)
cw_c = mp.mpf('1.001928261')
print(f"    vs O200 註冊值 dev = {float(dev_bbn)*100:.4f}%  (< 0.05% = 同一量, 差異來自 omega_ring 0.02% 級捨入)")
c3a = dev_bbn < mp.mpf('5e-4')
print(f"    比值 N_anchor/N_bbn = {mp.nstr(N_anchor/N_bbn,10)}  vs c_W/c = 1.001928261 -> dev "
      f"{float(abs(N_anchor/N_bbn/cw_c-1))*100:.4f}%")
c3 = c3a and abs(N_anchor/N_bbn/cw_c-1) < mp.mpf('1e-3')
print(f"    {'PASS' if c3 else 'FAIL'} — 兩個約定差 ≈ c_W/c (0.19% 級 🟡), 同一量兩個輸入")
print(f"    備註: c_W/c = R_world*omega_ring/c 用註冊 R_world = 4129.94 Mpc;")
print(f"          若用 R_world = c/omega_ring (72.59) 則比值恆等 1 (定義)")

# ================= C4 核心恆等式 =================
print("\n[C4] ★ 精確無量綱恆等式")
print("    推導: N^2 = c^5/(hbar G) / omega_ring^2 ;  omega_ring^2 = (8piG/3) rho_c")
print("          rho_c = eta_B m_p n_gamma / Omega_b ;  n_gamma = 2z3/pi^2 (k_BT/(hbar c))^3")
print("       => N^2 = 3pi Omega_b hbar^2 c^8 / (16 z3 eta_B m_p G^2 (k_BT)^3)")
print("       代入 (m_Pl/m_p)^4 = hbar^2 c^2/(G^2 m_p^4):")
print("       => N^2 = [3pi/(16 z3)] (Omega_b/eta_B) (m_Pl/m_p)^4 (m_p c^2/(k_BT))^3")
def N_closed(Om_b, T=T_CMB, eta=eta_B, Gv=G, mp_=m_p):
    mPl = mp.sqrt(hbar*c/Gv)
    pref = 3*mp.pi/(16*zeta3)
    return mp.sqrt(pref*(_frac(Om_b)/eta)*(mPl/mp_)**4*(mp_*c**2/(kB*T))**3)
for tag, Om in (("19/450", Om_b_old), ("3/60", Om_b_new)):
    Nc = N_closed(Om); Nd = (1/omega_from_chain(Om))/t_Pl
    dev = abs(Nc/Nd - 1)
    print(f"    Omega_b={tag:<7}: N_closed = {mp.nstr(Nc,10)}  N_direct = {mp.nstr(Nd,10)}  dev = {mp.nstr(dev,3)}")
c4 = abs(N_closed(Om_b_old)/((1/omega_from_chain(Om_b_old))/t_Pl)-1) < mp.mpf('1e-35')
print(f"    {'PASS' if c4 else 'FAIL'} — 恆等式 EXACT (dps=40, dev < 1e-35)")
print("    ==> N 係【純無量綱量嘅函數】: Omega_b, eta_B, m_Pl/m_p, k_BT/(m_p c^2)")

# ================= C5 N <-> G =================
print("\n[C5] N <-> G 一一對應")
def G_from_N(N, w=omega_anchor):
    return c**5/(hbar*w**2*N**2)
G_imp = G_from_N(N_anchor)
print(f"    G_implied(N = {mp.nstr(N_anchor,8)}, omega_ring = 72.59) = {mp.nstr(G_imp,8)}")
print(f"    CODATA G = {mp.nstr(G,8)}  -> dev {float(abs(G_imp/G-1))*100:.5f}%")
c5 = abs(G_imp/G-1) < mp.mpf('1e-4')
print(f"    {'PASS' if c5 else 'FAIL'}")
# N <-> m_p/m_Pl (given eta_B, T)
def mratio_from_N(N, Om_b=Om_b_old, T=T_CMB, eta=eta_B):
    pref = 3*mp.pi/(16*zeta3)
    return (N**2/(pref*(_frac(Om_b)/eta)*(m_p*c**2/(kB*T))**3))**(mp.mpf(1)/4)
r_imp = mratio_from_N(N_bbn)
print(f"    m_Pl/m_p 由 N 反解 = {mp.nstr(r_imp,8)}  vs 實測 {mp.nstr(m_Pl/m_p,8)}  -> dev "
      f"{float(abs(r_imp/(m_Pl/m_p)-1))*100:.5f}%")
c5b = abs(r_imp/(m_Pl/m_p)-1) < mp.mpf('1e-4')
print(f"    {'PASS' if c5b else 'FAIL'}")
print("    ==> N 同 G (即 m_p/m_Pl) 攜帶完全相同嘅資訊")

# ================= C6 null test =================
print("\n[C6] null test: N = f(結構數)? (密度基準)")
pool = []
for k in range(-400, 401): pool.append(float((1+mp.sqrt(5))/2)**k)
for k in range(0, 300): pool.append(float(mp.mpf(2)**k)); pool.append(float(mp.mpf(10)**k))
for p_ in range(1, 301):
    for q_ in range(1, 301): pool.append(p_/q_)
pool = sorted(set(v for v in pool if v > 0))
def best(x):
    xf = float(x); lo = bisect_left(pool, xf); bd = 1e99
    for i in (lo-1, lo):
        if 0 <= i < len(pool): bd = min(bd, abs(pool[i]/xf - 1))
    return bd
d_obs = best(N_bbn)
lo_, hi_ = math.log(float(N_bbn))-3, math.log(float(N_bbn))+3
M = 20000
stats = sorted(best(math.exp(random.uniform(lo_, hi_))) for _ in range(M))
d_med = stats[M//2]; q_obs = sum(1 for s in stats if s <= d_obs)/M
print(f"    N = {mp.nstr(N_bbn,10)}")
print(f"    N_search = {len(pool)}  d_obs = {float(d_obs)*100:.4f}%  d_med = {float(d_med)*100:.4f}%  q_obs = {q_obs:.4f}")
c6 = q_obs > 0.05
print(f"    {'PASS (🔴 確認 ≈ 隨機)' if c6 else 'FAIL'} — N 唔係結構數 (O200 P=0.8735 重現)")

# ================= C7 剛性 =================
print("\n[C7] 剛性: 解析 log-導數 vs 數值擾動")
base = N_closed(Om_b_old)
def num_dlnN(f):
    h = mp.mpf('1e-8'); return (mp.log(f(1+h))-mp.log(f(1-h)))/(2*h)
tests = [
    ("Omega_b", lambda s: N_closed(Om_b_old*s), mp.mpf(1)/2),
    ("eta_B",   lambda s: N_closed(Om_b_old, eta=eta_B*s), -mp.mpf(1)/2),
    ("k_BT",    lambda s: N_closed(Om_b_old, T=T_CMB*s), -mp.mpf(3)/2),
    ("G",       lambda s: N_closed(Om_b_old, Gv=G*s), -mp.mpf(1)),
    ("m_p",     lambda s: N_closed(Om_b_old, mp_=m_p*s), -mp.mpf(1)/2),
]
c7 = 0
for name, f, expect in tests:
    d = num_dlnN(f)
    ok = abs(d-expect) < mp.mpf('1e-4'); c7 += ok
    print(f"    d lnN / d ln{name:<8} = {mp.nstr(d,8):>12}   解析 {mp.nstr(expect,6):>8}   {'PASS' if ok else 'FAIL'}")
print(f"    {'PASS' if c7==len(tests) else 'FAIL'} ({c7}/{len(tests)})")
print("    ==> N ∝ 1/G EXACT: 任何 G 嘅變動 1:1 反映喺 N (反向)")

# ================= C8 可證偽 =================
print("\n[C8] 可證偽清單")
print("""    F1  N 唔可以由結構數導出 (null q_obs > 0.05) — 若將來聲稱導出 N, 必須先過同池 null
    F2  N ∝ 1/G: 用任何獨立 G 值重算 N, 必得同 CODATA 一致嘅階層數
    F3  恆等式 N^2 = [3pi/(16z3)](Om_b/eta_B)(m_Pl/m_p)^4 (m_p c^2/k_BT)^3 — 任一輸入更新即全鏈更新
    F4  若要「導出 N」, 等價於由 W-field 晶格導出 m_p/m_Pl (重力扇區 O86) — 目前 🔴""")

tot = c1+c2+c3+c4+c5+c5b+c6+c7
print("\n" + "="*94)
print(f"RESULT: {tot}/12 PASS  (C1 {int(c1)} + C2 {int(c2)} + C3 {int(c3)} + C4 {int(c4)} "
      f"+ C5 {int(c5)}+{int(c5b)} + C6 {int(c6)} + C7 {c7})")
print("""
  ★ 核心結論:
    N 唔係 IDCM 嘅自由參數 — 佢係【無量綱量嘅複合】:
        N^2 = [3pi/(16 zeta(3))] (Omega_b/eta_B) (m_Pl/m_p)^4 (m_p c^2/(k_BT))^3
    其中 Omega_b 係結構 (3/60), eta_B/T_CMB 係無量綱觀測, m_Pl/m_p 係【重力階層】。
    ==> 「N 為何係 7.87e60」 等價於 「m_p/m_Pl 為何係 7.69e-20」(重力階層問題),
        唔係錨定理嘅缺口 — 亦唔可以喺無量綱結構內導出 (維度定理)。
""")
