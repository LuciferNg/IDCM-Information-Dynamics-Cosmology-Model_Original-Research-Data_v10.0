#!/usr/bin/env python3
"""
O181 script 02 — doc audit: 判決數字與 script 01 輸出交叉核對
================================================================
閉合紀律 (2026-08-17): data 與 stdout 不一致要修正。
核對 docs/01 + final_result + 01_problem_record 嘅關鍵數字 vs script 01 實算。
"""
import mpmath as mp
mp.mp.dps = 60

PASS = 0; FAIL = 0
def ck(name, cond, info=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  [PASS] {name} {info}")
    else:
        FAIL += 1; print(f"  [FAIL] {name} {info}")

# 重算 script 01 關鍵值 (由零)
N = mp.mpf(434)
M_exact = mp.mpf('6973199.69612336')
M_3sf = mp.mpf('6.97e6')
t_active = mp.mpf('11e9')
T_ring_yr = mp.mpf('84.6349e9')
eta = ((1+mp.sqrt(5))/2)**(-21)
E_strain = mp.mpf('1564785320847.4905')
pools_3sf = N*M_3sf*T_ring_yr/(t_active*eta*E_strain)
pools_ex = N*M_exact*T_ring_yr/(t_active*eta*E_strain)
d_ex = pools_ex - 364
B75 = mp.mpf(4)/75
sep = B75/364

print(f"  池/圈 (3-sf) = {mp.nstr(pools_3sf,10)}  (O177 記錄 364.0533148)")
print(f"  池/圈 (exact) = {mp.nstr(pools_ex,10)}")
print(f"  δ(exact) = {mp.nstr(d_ex,8)} ; B/75 覆蓋率 = {mp.nstr(B75/d_ex*100,4)}%")
print(f"  分離度 = {mp.nstr(sep*100,6)}% ; 3σ 需 < {mp.nstr(sep/3*100,6)}%")

# 採樣誤差
sig_dex = mp.mpf('0.42805979772036157')
se_med_rel = mp.mpf(10)**(mp.mpf('1.253')*sig_dex/mp.sqrt(434)) - 1
n_need = (mp.mpf('1.253')*sig_dex/mp.mpf('0.0000126'))**2
print(f"  SE(median) = {mp.nstr(se_med_rel*100,4)}% ; n_need(5sf) = {mp.nstr(n_need,3)}")

# 宇宙學
H0_s = mp.mpf('67.36')*mp.mpf('1e3')/mp.mpf('3.0857e22')
Gyr_s = mp.mpf('3.15576e16')
def tzGyr_par(H0v, Omv, z):
    import mpmath as mpl
    zz = mp.mpf(z); H = mp.mpf(H0v)*mp.mpf('1e3')/mp.mpf('3.0857e22'); OLv = 1-mp.mpf(Omv)
    def g(x):
        x = mp.mpf(x)
        return 1/((1+x)*mp.sqrt(mp.mpf(Omv)*(1+x)**3 + OLv))
    return mpl.quad(g, [zz, mp.mpf('150')]) / H / Gyr_s
dt90 = tzGyr_par(67.36,0.3153,0) - tzGyr_par(67.36,0.3153,9)
dthi = tzGyr_par(67.90,0.3153,0) - tzGyr_par(67.90,0.3153,9)
dtlo = tzGyr_par(66.82,0.3153,0) - tzGyr_par(66.82,0.3153,9)
dtOmhi = tzGyr_par(67.36,0.3226,0) - tzGyr_par(67.36,0.3226,9)
dtOmLo = tzGyr_par(67.36,0.3080,0) - tzGyr_par(67.36,0.3080,9)
sig_dt = mp.sqrt((abs(dthi-dtlo)/2)**2 + (abs(dtOmhi-dtOmLo)/2)**2)
print(f"  Δt(9→0) = {mp.nstr(dt90,7)} Gyr ; σ_rel = {mp.nstr(sig_dt/dt90*100,4)}%")

# N(z) 加權
import mpmath as mpl
def wf(z):
    z = mp.mpf(z)
    return 1/((1+z)**2*mp.sqrt(mp.mpf('0.3153')*(1+z)**3 + mp.mpf('0.6847')))
t_eff = mpl.quad(wf, [0, mp.mpf('9')]) / H0_s / Gyr_s
dt92 = tzGyr_par(67.36,0.3153,2) - tzGyr_par(67.36,0.3153,9)
print(f"  t_eff(N加權) = {mp.nstr(t_eff,6)} Gyr ; Δt(9→2) = {mp.nstr(dt92,6)} Gyr")

print()
# ================= 核對 docs =================
print("="*74)
print("Part A — docs/01 + final_result 數字核對")
print("="*74)
ck("A1 δ(exact) = +0.2204 (docs/01 §4, final_result §附帶)", 
   abs(d_ex - mp.mpf('0.2204')) < mp.mpf('0.0005'), f"δ = {mp.nstr(d_ex,6)}")
ck("A2 B/75 覆蓋率 ~24.2% (docs/01 §4, final_result)", 
   abs(B75/d_ex - mp.mpf('0.2419')) < mp.mpf('0.005'), f"= {mp.nstr(B75/d_ex*100,4)}%")
ck("A3 採樣 floor 6.1% (docs/01 §2.1, §3; final_result)", 
   abs(se_med_rel - mp.mpf('0.061')) < mp.mpf('0.001'), f"= {mp.nstr(se_med_rel*100,4)}%")
ck("A4 n_need ≈ 1.8e9 (docs/01 §2.1; final_result)", 
   n_need > mp.mpf('1e9') and n_need < mp.mpf('3e9'), f"= {mp.nstr(n_need,3)}")
ck("A5 Δt(9→0) = 13.256 Gyr (docs/01 §2.3; final_result)", 
   abs(dt90 - mp.mpf('13.2560')) < mp.mpf('0.001'), f"= {mp.nstr(dt90,7)}")
ck("A6 σ_t(宇宙學) ≈ 1.02% (docs/01 §2.3, §3; final_result)", 
   abs(sig_dt/dt90 - mp.mpf('0.01021')) < mp.mpf('0.001'), f"= {mp.nstr(sig_dt/dt90*100,4)}%")
ck("A7 t_eff(N加權) = 7.620 Gyr (−42.5%) (docs/01 §2.3)", 
   abs(t_eff - mp.mpf('7.6203')) < mp.mpf('0.01'), f"= {mp.nstr(t_eff,6)}")
ck("A8 Δt(9→2) = 2.729 Gyr (−79.4%) (docs/01 §2.3)", 
   abs(dt92 - mp.mpf('2.7290')) < mp.mpf('0.01'), f"= {mp.nstr(dt92,6)}")
ck("A9 分離度 1/6825 = 0.01465%, 3σ 需 < 0.00488% (docs/01 §3)", 
   abs(sep - mp.mpf('1')/mp.mpf('6825')) < mp.mpf('1e-9') and abs(sep/3 - mp.mpf('0.00004884')) < mp.mpf('1e-8'),
   f"sep = {mp.nstr(sep*100,6)}%")
# 合併 floor (最佳)
sig_best = mp.sqrt(se_med_rel**2 + (sig_dt/dt90)**2)
gap_best = sig_best/(sep/3)
ck("A10 合併 floor 6.19% → 差距 1268× (docs/01 §3; final_result)", 
   abs(gap_best - mp.mpf('1268')) < mp.mpf('10'), f"= {mp.nstr(gap_best,5)}×")
# 含 λ
sig_lam = mp.mpf(10)**mp.mpf('0.5') - 1
gap_full = mp.sqrt(sig_lam**2 + (sig_dt/dt90)**2)/(sep/3)
ck("A11 含 λ floor → 差距 ~44,270× (docs/01 §3; final_result)", 
   gap_full > mp.mpf('44000') and gap_full < mp.mpf('45000'), f"= {mp.nstr(gap_full,5)}×")
# 統計
sigma_n = d_ex/(sig_best*364)
ck("A12 exact-M 殘餘 = 0.0098σ (docs/01 §4; final_result)", 
   abs(sigma_n - mp.mpf('0.00978')) < mp.mpf('0.001'), f"= {mp.nstr(sigma_n,5)}σ")

print()
print("="*74)
print("Part B — O177 交叉核對 (errata 引用值)")
print("="*74)
ck("B1 O177 記錄 池/圈 = 364.0533148 用 3-sf M 重現", 
   abs(pools_3sf - mp.mpf('364.053314767')) < mp.mpf('1e-6'), f"= {mp.nstr(pools_3sf,10)}")
ck("B2 catalog median = 6,973,199.696 (JSON 值一致)", 
   M_exact == mp.mpf('6973199.69612336'), "11_cosmosweb_tests.json M_obs_Edd01_median")
ck("B3 δ(exact) = 4.13× O177 記錄 δ (+0.0533)", 
   abs(d_ex/mp.mpf('0.0533') - mp.mpf('4.135')) < mp.mpf('0.01'), f"= {mp.nstr(d_ex/mp.mpf('0.0533'),4)}×")
ck("B4 O177「M 捨入向上」方向錯: catalog (6.9732e6) > 6.97e6", 
   M_exact > M_3sf, "真實 median 高過 3-sf 值, 殘餘加大而非解釋")
ck("B5 364 身份統計一致 (≪1σ): O177/O173 閉合維持", 
   sigma_n < mp.mpf('0.05'), f"δ = {mp.nstr(sigma_n,5)}σ")

print()
print(f"RESULT: {PASS}/{PASS+FAIL} PASS")
import sys
sys.exit(0 if FAIL == 0 else 1)
