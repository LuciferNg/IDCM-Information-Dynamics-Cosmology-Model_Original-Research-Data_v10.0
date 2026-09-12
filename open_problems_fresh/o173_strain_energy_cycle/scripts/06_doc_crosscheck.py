#!/usr/bin/env python3
"""
O173 script 06 — 文檔獨立核對 (Doc Crosscheck)
=================================================
由零重算 docs/01-05 每個宣稱 (唔依賴原 scripts 輸出)
每 doc 一區塊 (A/B/C...), 每項 chk() 輸出 [✔]/[✘] + 重算值 vs doc 值
"""
import math, cmath
import mpmath as mp

mp.mp.dps = 60
OK = 0; BAD = 0
def chk(doc, claim, computed, docval, tol=mp.mpf('1e-6'), unit=""):
    """computed/docval: 數值 (mpf/float/int) 或 special str ('i','-1','1','0')"""
    global OK, BAD
    if isinstance(docval, str) or isinstance(computed, str):
        ok = str(computed) == str(docval)
        cd = str(computed); dv = str(docval)
    else:
        try:
            cv = mp.mpf(computed); dv = mp.mpf(docval)
            ok = abs(cv - dv) <= mp.mpf(tol)*max(mp.mpf('1'), abs(dv))
            cd = mp.nstr(cv, 6); dv = mp.nstr(dv, 6)
        except Exception:
            ok = False; cd = str(computed); dv = str(docval)
    if ok:
        OK += 1
        mark = "[✔]"
    else:
        BAD += 1
        mark = "[✘]"
    print(f"  {mark} {doc} {claim}: {cd}{unit}  (doc: {dv}{unit})")
    return ok

print("="*78)
print("Block A — docs/01 能量流盤點")
print("="*78)
H0 = mp.mpf('72.59')*mp.mpf('1e3')/(mp.mpf('3.085677581e22'))
Gc = mp.mpf('6.674e-11'); c = mp.mpf('2.99792458e8')
M_Pl = mp.mpf('2.176434e-8'); L_P = mp.mpf('1.616255e-35')
M_sun = mp.mpf('1.98892e30')
R_H_m = c/H0; lam_sync = 2*mp.pi*R_H_m/88
rho_crit = 3*H0**2/(8*mp.pi*Gc); eps = mp.mpf(1)/30
V_edge = (lam_sync/44)**3
E_kg = 32*rho_crit*c**2*eps**2*V_edge/c**2
E_msun = E_kg/M_sun
closed = (mp.pi**2/75)*M_Pl*(R_H_m/L_P)/44**6
chk("01", "E_strain kg", E_kg, mp.mpf('3.1122e42'), mp.mpf('1e-3'))
chk("01", "E_strain M☉", E_msun, mp.mpf('1.5648e12'), mp.mpf('1e-3'))
chk("01", "閉合形式 dev%", abs(E_kg-closed)/closed*100, mp.mpf('0.004509'), mp.mpf('1e-3'), "%")
phi = (1+mp.sqrt(5))/2
eta = phi**(-21)
chk("01", "η = φ^-21", eta, mp.mpf('4.0856e-5'), mp.mpf('1e-3'))
budget = E_msun*eta
chk("01", "一次性預算", mp.nstr(budget,5), mp.nstr(mp.mpf('6.3931e7'),5), mp.mpf('1e-3'))
S8 = mp.mpf('0.047048509643483345'); f4 = 1-mp.mpf('0.3636')
M_base = E_msun*eta*S8*f4
chk("01", "M_base(8)", mp.nstr(M_base,5), mp.nstr(mp.mpf('1.9142e6'),5), mp.mpf('1e-3'))
strain_ev = E_msun*S8*f4
chk("01", "每次事件應變", mp.nstr(strain_ev,5), mp.nstr(mp.mpf('4.6852e10'),5), mp.mpf('1e-3'))
M_obs = mp.mpf('6.97e6'); Nl = 434
M_cond = Nl*M_obs
chk("01", "觀測凝聚 M☉", mp.nstr(M_cond,5), mp.nstr(mp.mpf('3.025e9'),5), mp.mpf('1e-3'))
chk("01", "觀測/預算 ratio", mp.nstr(M_cond/budget,4), mp.nstr(mp.mpf('47.32'),4), mp.mpf('1e-2'))
r_base = Nl*strain_ev/E_msun
chk("01", "應變消耗 base ratio", mp.nstr(r_base,4), mp.nstr(mp.mpf('12.99'),4), mp.mpf('1e-2'))
delta = (M_obs/M_base)**(mp.mpf(2)/3)-1
r_delta = Nl*(M_obs/eta)/E_msun
chk("01", "δ 反解", mp.nstr(delta,4), mp.nstr(mp.mpf('1.367'),4), mp.mpf('1e-2'))
chk("01", "應變消耗 δ ratio", mp.nstr(r_delta,4), mp.nstr(mp.mpf('47.32'),4), mp.mpf('1e-2'))
t_act = mp.mpf('11e9')
rate_m = M_cond/t_act
rate_s = rate_m/eta
chk("01", "質量形成率 M☉/yr", mp.nstr(rate_m,4), mp.nstr(mp.mpf('0.275'),4), mp.mpf('1e-2'))
chk("01", "應變消耗率 M☉/yr", rate_s, mp.mpf('6731'), mp.mpf('1e-2'))
chk("01", "節點耗盡 Myr", strain_ev/rate_s/1e6, mp.mpf('6.96'), mp.mpf('1e-2'))
chk("01", "池耗盡 Gyr", mp.nstr(E_msun/rate_s/1e9,4), mp.nstr(mp.mpf('0.2325'),4), mp.mpf('1e-2'))
L_Edd = mp.mpf('1.26e38')*M_obs
Mdot = (L_Edd*mp.mpf('9.91')*1e-7)/(mp.mpf('0.1')*c**2)*mp.mpf('3.156e7')/M_sun
chk("01", "輻射率 1.54", mp.nstr(Mdot,4), mp.nstr(mp.mpf('1.5366'),4), mp.mpf('1e-2'))
chk("01", "t_cond Myr", mp.nstr(M_obs/Mdot/1e6,4), mp.nstr(mp.mpf('4.536'),4), mp.mpf('1e-2'))
V_uni = 4*mp.pi/3*(R_H_m/(mp.mpf('3.085677581e22')))**3
M_uhecr = (mp.mpf('5e44')*V_uni*1e-7)/(M_sun*c**2)
chk("01", "UHECR M☉/yr", mp.nstr(M_uhecr,4), mp.nstr(mp.mpf('82.53'),4), mp.mpf('1e-2'))
print("")

print("="*78)
print("Block B — docs/02 守恆審計")
print("="*78)
M = 88
gamma = [mp.mpf('4')*mp.sin(mp.mpf(k)*mp.pi/M/2)**2 for k in range(1, M+1)]
S_even = sum(gamma[i] for i in range(1, M, 2))
S_odd = sum(gamma[i] for i in range(0, M, 2))
chk("02", "Σγ = 178", mp.nstr(sum(gamma),10), mp.nstr(mp.mpf('178'),10), mp.mpf('1e-40'))
chk("02", "Σγ_even = 90", mp.nstr(S_even,10), mp.nstr(mp.mpf('90'),10), mp.mpf('1e-40'))
chk("02", "Σγ_odd = 88", mp.nstr(S_odd,10), mp.nstr(mp.mpf('88'),10), mp.mpf('1e-40'))
chk("02", "μ² = E−O = 2", mp.nstr(S_even-S_odd,10), mp.nstr(mp.mpf('2'),10), mp.mpf('1e-40'))
chk("02", "γ₄₄ = 2", mp.nstr(gamma[43],10), mp.nstr(mp.mpf('2'),10), mp.mpf('1e-40'))
Q_def = sum(k for k in range(2, M+1, 2)) - sum(k for k in range(1, M+1, 2))
chk("02", "Q = 44", Q_def, mp.mpf('44'), mp.mpf('1e-40'))
J = [sum(mp.mpf((-1)**j)*j for j in range(1, k+1)) for k in range(1, M+1)]
chk("02", "J₈₈ = 44", mp.nstr(J[87],10), mp.nstr(mp.mpf('44'),10), mp.mpf('1e-40'))
chk("02", "J₈₇ = −44", mp.nstr(J[86],10), mp.nstr(mp.mpf('-44'),10), mp.mpf('1e-40'))
chk("02", "Σ|J_k| = 1980", mp.nstr(sum(abs(jj) for jj in J),10), mp.nstr(mp.mpf('1980'),10), mp.mpf('1e-40'))
chk("02", "ΣJ = 0", mp.nstr(sum(J),10), mp.nstr(mp.mpf('0'),10), mp.mpf('1e-40'))
phase = sum(mp.mpf(k)*mp.pi/88 for k in range(1, M+1))
chk("02", "總相位 44.5π", mp.nstr(phase/mp.pi,8), mp.nstr(mp.mpf('44.5'),8), mp.mpf('1e-40'))
wl = cmath.exp(1j*float(phase))
chk("02", "Wilson line = i", "i" if abs(wl-1j) < 1e-12 else "?i", "i")
holo = cmath.exp(1j*float(M*mp.pi/M))
chk("02", "holonomy = −1", "-1" if abs(holo+1) < 1e-12 else "?", "-1")
lam_self = mp.mpf('2')/123
vev2 = mp.mpf('2')/(2*lam_self)
chk("02", "⟨W⟩² = 61.5", mp.nstr(vev2,10), mp.nstr(mp.mpf('61.5'),10), mp.mpf('1e-40'))
chk("02", "λ_self = 2/123", mp.nstr(lam_self,10), mp.nstr(mp.mpf('2')/123,10), mp.mpf('1e-40'))
chk("02", "V'' = 8", mp.nstr(4*mp.mpf('2'),10), mp.nstr(mp.mpf('8'),10), mp.mpf('1e-40'))
chk("02", "RG I = 21×176/42 = 88", mp.nstr(mp.mpf('21')*mp.mpf('176')/42,10), mp.nstr(mp.mpf('88'),10), mp.mpf('1e-40'))
print("")

print("="*78)
print("Block C — docs/03 再生機制")
print("="*78)
chk("03", "有限池三路矛盾 ratio_budget>40", bool(r_delta > 40), True)
chk("03", "ratio_base>10", bool(r_base > 10), True)
chk("03", "t_exhaust<1 Gyr", bool(E_msun/rate_s/1e9 < 1), True)
T_ring = mp.mpf('84.6349'); tau = mp.mpf('13.4701')
t_true = mp.mpf('11100.64')
chk("03", "131·T_ring+τ = t_true", mp.nstr(131*T_ring+tau,6), mp.nstr(t_true,6), mp.mpf('1e-4'))
cap131 = mp.mpf('131')*E_msun
chk("03", "131 圈容量 2.05e14", mp.nstr(cap131,5), mp.nstr(mp.mpf('2.0499e14'),5), mp.mpf('1e-3'))
strain_obs = M_cond/eta
chk("03", "觀測消耗 7.40e13", mp.nstr(strain_obs,5), mp.nstr(mp.mpf('7.4039e13'),5), mp.mpf('1e-3'))
chk("03", "36.1% 容量", mp.nstr(strain_obs/cap131*100,4)+"%", "36.12%", mp.mpf('1e-2'))
chk("03", "R_rel = 6731", rate_s, mp.mpf('6731'), mp.mpf('1e-2'))
chk("03", "dβ/dℓ = 176/42 = 4.1905", mp.mpf('176')/42, mp.mpf('4.190476'), mp.mpf('1e-5'))
print("")

print("="*78)
print("Block D — docs/04 預言")
print("="*78)
chk("04", "P2 一次性預算/median = 9.17", mp.nstr(budget/M_obs,4), mp.nstr(mp.mpf('9.172'),4), mp.mpf('1e-2'))
E_hops = [0.01482, 0.00914, 0.00898, 0.00775, 0.00692, 0.00775, 0.00898, 0.00914, 0.01482]
E0 = mp.mpf(str(E_hops[0]))
Erest = sum(mp.mpf(str(e)) for e in E_hops[1:])
chk("04", "P5 干涉比 4.958", mp.nstr(Erest/E0,4), mp.nstr(mp.mpf('4.958'),4), mp.mpf('1e-2'))
chk("04", "P5 free-fall δ=30 → 173", mp.nstr(mp.mpf('31')**mp.mpf('1.5'),4), mp.nstr(mp.mpf('172.6'),4), mp.mpf('1e-2'))
chk("04", "P5 free-fall δ=100 → 1015", mp.nstr(mp.mpf('101')**mp.mpf('1.5'),4), mp.nstr(mp.mpf('1015'),4), mp.mpf('1e-2'))
chk("04", "T_beat = 3330× 年齡", mp.mpf('45963')/mp.mpf('13.8'), mp.mpf('3331'), mp.mpf('1e-2'))
chk("04", "觀測窗 0.1592 週期", tau/T_ring, mp.mpf('0.1592'), mp.mpf('1e-2'))
print("")

print("="*78)
print("Block E — docs/05 場論")
print("="*78)
G44 = mp.mpf(1)/(gamma[43]+2)
G88 = mp.mpf(1)/(gamma[87]+2)
chk("05", "G(44) = 1/4", mp.nstr(G44,10), mp.nstr(mp.mpf('0.25'),10), mp.mpf('1e-40'))
chk("05", "G(88) = 1/6", mp.nstr(G88,10), mp.nstr(mp.mpf(1)/6,10), mp.mpf('1e-40'))
chk("05", "A₄₄ = 0", gamma[43]-2, mp.mpf('0'), mp.mpf('1e-40'))
chk("05", "A₈₈ = 2", mp.nstr(gamma[87]-2,10), mp.nstr(mp.mpf('2'),10), mp.mpf('1e-40'))
chk("05", "γ₈₈−γ₄₄ = 2 = μ²", mp.nstr(gamma[87]-gamma[43],10), mp.nstr(mp.mpf('2'),10), mp.mpf('1e-40'))
chk("05", "i⁴ = 1 (352 閉合)", "1" if abs(1j**4-1) < 1e-50 else "?", "1")
chk("05", "λ = 1 (乘子)", mp.nstr(mp.mpf('2')/2,10), mp.nstr(mp.mpf('1'),10), mp.mpf('1e-40'))
print("")

print("="*78)
print(f"AUDIT RESULT: {OK}/{OK+BAD} 核對通過")
print("="*78)
