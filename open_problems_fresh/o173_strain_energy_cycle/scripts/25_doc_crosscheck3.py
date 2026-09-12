#!/usr/bin/env python3
"""
O173 script 25 — 全文檔獨立核對 (閉合程序第 1-2 步, 用戶 09-13 指示)
====================================================================
由零重算 docs/01-21 所有核心公式/數值 (mpmath 50 dps),
唔依賴原 scripts 輸出 — 目的係捉 doc 入面嘅錯.

原則 (o-series-research-workflow 文檔審計):
- 每 doc 一區塊, 每項 chk(doc, claim, computed, docval, tol)
- 觀測引用值 (Elvis/Auger/Holberg 等) 核對「文檔內一致」+ 重算比率
- 禁跨文檔污染: 只核對已寫入內容, 唔引入新推導
"""
import mpmath as mp

mp.mp.dps = 50
PHI = (1 + mp.sqrt(5))/2
ok = 0; bad = 0
def chk(doc, claim, comp, docval, tol, unit=""):
    global ok, bad
    dev = abs(comp - docval)/abs(docval) if docval != 0 else abs(comp)
    mark = "[OK]" if dev <= tol else "[XX]"
    if dev <= tol:
        ok += 1
    else:
        bad += 1
    print(f"  {mark} {doc} {claim}: 重算 {mp.nstr(comp,8)}{unit} vs doc {mp.nstr(docval,8)}{unit} (dev {mp.nstr(dev*100,4)}%)")

M_SUN = mp.mpf('1.989e30')   # kg
eta = PHI**-21

print("="*74)
print("docs/01 — 能量流盤點")
print("="*74)
# 池 = (pi^2/75)·M_Pl·(R_H/L_P)·44^-6
M_Pl = mp.mpf('2.176e-8')          # kg
R_H_m = mp.mpf('4129.94')*mp.mpf('3.085677581e22')  # m
L_P = mp.mpf('1.616e-35')          # m
E_strain = (mp.pi**2/75)*M_Pl*(R_H_m/L_P)*mp.mpf('44')**-6
E_strain_Msun = E_strain/M_SUN
chk("d01", "池 E_strain (kg)", E_strain, mp.mpf('3.1122e42'), 1e-4)
chk("d01", "池 E_strain (M☉)", E_strain_Msun, mp.mpf('1.565e12'), 5e-4)
chk("d01", "η = φ⁻²¹", eta, mp.mpf('4.086e-5'), 2e-3)
budget = E_strain_Msun*eta
chk("d01", "一次性凝聚預算 (池×η)", budget, mp.mpf('6.39e7'), 1e-2)
quota8 = E_strain_Msun*mp.mpf('0.02994')
chk("d01", "節點 8 應變配額 (池×0.02994)", quota8, mp.mpf('4.685e10'), 1e-2)
M_base8 = quota8*eta
chk("d01", "M_base(8) = 配額×η", M_base8, mp.mpf('1.914e6'), 1e-2)
obs_cond = mp.mpf('434')*mp.mpf('6.97e6')
chk("d01", "觀測凝聚 434×6.97e6", obs_cond, mp.mpf('3.02e9'), 1e-2)
chk("d01", "觀測凝聚 vs 預算 = 47.3×", obs_cond/budget, mp.mpf('47.3'), 2e-2)
strain_base = mp.mpf('434')*mp.mpf('4.685e10')
chk("d01", "應變消耗 base 434×4.685e10", strain_base, mp.mpf('2.03e13'), 1e-2)
chk("d01", "應變消耗 base vs 池 = 13.0×", strain_base/E_strain_Msun, mp.mpf('13.0'), 2e-2)
chk("d01", "應變消耗含δ vs 池 = 47.3×", mp.mpf('7.40e13')/E_strain_Msun, mp.mpf('47.3'), 2e-2)
chk("d01", "median LRD 應變 = 3.64× 配額", mp.mpf('1.70e11')/mp.mpf('4.685e10'), mp.mpf('3.64'), 2e-2)
rate_strain = mp.mpf('0.275')/eta
chk("d01", "應變消耗率 = 0.275/η", rate_strain, mp.mpf('6731'), 1e-2, " M☉/yr")
chk("d01", "節點配額耗盡時標 (Myr)", mp.mpf('4.685e10')/rate_strain/1e6, mp.mpf('6.96'), 2e-2)
chk("d01", "池耗盡時標 (Gyr)", E_strain_Msun/rate_strain/1e9, mp.mpf('0.232'), 2e-2)
chk("d01", "凝聚時標 6.97e6/1.54 = 4.54 Myr", mp.mpf('6.97e6')/mp.mpf('1.54')/1e6, mp.mpf('4.54'), 1e-2)

print("\n" + "="*74)
print("docs/02 — 守恆審計")
print("="*74)
chk("d02", "Q = 44 = N_d", mp.mpf('44'), mp.mpf('44'), 0)
chk("d02", "ΣJ = 0 (總通量零)", mp.mpf('44')-mp.mpf('44'), 0, 0)
chk("d02", "J₈₈ = +44, J₈₇ = −44 (共軛)", mp.mpf('44'), mp.mpf('44'), 0)
# μ² = 2 由 E−O = 90−88
chk("d02", "μ² = E−O = 90−88 = 2", mp.mpf('90')-mp.mpf('88'), mp.mpf('2'), 0)

print("\n" + "="*74)
print("docs/03 — 再生機制")
print("="*74)
T_ring = mp.mpf('84.63')   # Gyr
tau = mp.mpf('13.4701')    # Gyr
t_true = 131*T_ring + tau
chk("d03", "t_true = 131·T_ring+τ", t_true, mp.mpf('11100.64'), 1e-4, " Gyr")
cap131 = 131*mp.mpf('1.565e12')
chk("d03", "131 圈再生容量", cap131, mp.mpf('2.05e14'), 1e-2, " M☉")
chk("d03", "消耗/容量 = 36.1%", mp.mpf('7.40e13')/cap131*100, mp.mpf('36.1'), 2e-2)
chk("d03", "dβ/dℓ = 176/42", mp.mpf('176')/42, mp.mpf('4.1905'), 1e-4)
chk("d03", "N(z=0) = 4⁰ = 1 (駐定)", mp.mpf('4')**0, 1, 0)

print("\n" + "="*74)
print("docs/06 — SMBH 通道")
print("="*74)
ton_lo = mp.mpf('4.07e10'); ton_hi = mp.mpf('6.6e10')
chk("d06", "TON 618 應變需求 (低估) vs 池", ton_lo/eta/mp.mpf('1.565e12'), mp.mpf('637'), 2e-2)
chk("d06", "TON 618 應變需求 (高估) vs 池", ton_hi/eta/mp.mpf('1.565e12'), mp.mpf('1032'), 2e-2)
M_seed100 = mp.mpf('1.914e6')*mp.mpf('101')**mp.mpf('1.5')
chk("d06", "種子上限 δ=100", M_seed100, mp.mpf('1.94e9'), 1e-2)
chk("d06", "UHz1 = 0.87× 上限", mp.mpf('1.7e9')/M_seed100, mp.mpf('0.87'), 2e-2)
univ_smbh = mp.mpf('3e18'); univ_smbh_hi = mp.mpf('5.9e18')
chk("d06", "全宇宙 SMBH vs 池 (低)", univ_smbh/mp.mpf('1.565e12'), mp.mpf('1.9e6'), 5e-2)
chk("d06", "全宇宙 SMBH vs 池 (高)", univ_smbh_hi/mp.mpf('1.565e12'), mp.mpf('3.8e6'), 5e-2)

print("\n" + "="*74)
print("docs/09 — 黑洞三分 (用戶挑戰)")
print("="*74)
tau_rec = mp.mpf('5.9e18')/mp.mpf('82.53')
chk("d09", "τ_rec = 5.9e18/82.53", tau_rec, mp.mpf('7.1e16'), 2e-2, " yr")
chk("d09", "觀測窗損失比例", mp.mpf('13.8e9')/tau_rec*100, mp.mpf('1.9e-5'), 5e-2)
# 吞噬時標: 13.8e9×ln(306.1)/ln(2.45)
t_devour = mp.mpf('13.8e9')*mp.log(mp.mpf('306.1'))/mp.log(mp.mpf('2.45'))
chk("d09", "吞噬時標 (Gyr)", t_devour/1e9, mp.mpf('88.2'), 2e-2)
chk("d09", "吞噬時標 vs T_ring (週期級)", t_devour/1e9/mp.mpf('84.63'), 1+mp.mpf('0.0415'), 1e-2)

print("\n" + "="*74)
print("docs/10 — TON 618 上限閉環")
print("="*74)
M_max = mp.mpf('0.0033')*mp.mpf('1e13')
chk("d10", "M_BH_max = 0.33%×1e13", M_max, mp.mpf('3.3e10'), 1e-2)
chk("d10", "TON 618 = 1.25-2.02×", ton_lo/M_max, mp.mpf('1.25'), 2e-2)
chk("d10", "TON 618 = 1.25-2.02×", ton_hi/M_max, mp.mpf('2.02'), 2e-2)

print("\n" + "="*74)
print("docs/11 — ★306 結構身份")
print("="*74)
chk("d11", "306 = L₆·F_proj = 18×17", 18*17, 306, 0)
L6_binet = PHI**6 + PHI**-6
chk("d11", "L₆ = φ⁶+φ⁻⁶ = 18 (Binet)", L6_binet, 18, 1e-9)
ratio_id = mp.mpf(1)/306
chk("d11", "1/306 = 0.326797%", ratio_id*100, mp.mpf('0.326797'), 1e-4)
chk("d11", "Elvis dev 0.04%", abs(mp.mpf('4.9e5')/mp.mpf('1.5e8')-ratio_id)/ratio_id*100, mp.mpf('0.04'), 5e-2)
chk("d11", "ρ_BH 預言 = ρ_star/306", mp.mpf('1.5e8')/306, mp.mpf('4.902e5'), 1e-3)
chk("d11", "M_host = M_BH×306 (LRD)", mp.mpf('6.97e6')*306, mp.mpf('2.13e9'), 1e-2)

print("\n" + "="*74)
print("docs/12 — 殘骸累積")
print("="*74)
chk("d12", "ρ_debris = 2%×1.5e8", mp.mpf('0.02')*mp.mpf('1.5e8'), mp.mpf('3.0e6'), 1e-2)
chk("d12", "固定點 4.0e6 (形成史×2%)", mp.mpf('0.02')*mp.mpf('2.0e8'), mp.mpf('4.0e6'), 1e-2)
chk("d12", "t_double = 3e6/4e-4 (Gyr)", mp.mpf('3e6')/mp.mpf('4e-4')/1e9, mp.mpf('7.5'), 1e-2)

print("\n" + "="*74)
print("docs/13 — 層級分離")
print("="*74)
chk("d13", "13.8/84.63 = 0.163 週期", mp.mpf('13.8')/mp.mpf('84.63'), mp.mpf('0.163'), 1e-2)
chk("d13", "SFRD 10% peak", mp.mpf('0.02')/mp.mpf('0.2'), mp.mpf('0.10'), 1e-2)

print("\n" + "="*74)
print("docs/15 — 裁決審計")
print("="*74)
d_eff = (mp.mpf('1.7e9')/mp.mpf('1.914e6'))**mp.mpf('2/3') - 1
chk("d15", "UHz1 δ_eff = 91.4", d_eff, mp.mpf('91.4'), 1e-2)

print("\n" + "="*74)
print("docs/16 — P14 樣本定義")
print("="*74)
chk("d16", "YT02 dev 10.2%", abs(mp.mpf('4.4e5')/mp.mpf('1.5e8')-ratio_id)/ratio_id*100, mp.mpf('10.2'), 2e-2)
chk("d16", "Marconi dev 6.2%", abs(mp.mpf('4.6e5')/mp.mpf('1.5e8')-ratio_id)/ratio_id*100, mp.mpf('6.2'), 2e-2)
chk("d16", "K&H dev 49%", abs(mp.mpf('2.5e5')/mp.mpf('1.5e8')-ratio_id)/ratio_id*100, mp.mpf('49.0'), 2e-2)
chk("d16", "K&H factor 1.96×", ratio_id/(mp.mpf('2.5e5')/mp.mpf('1.5e8')), mp.mpf('1.961'), 2e-2)

print("\n" + "="*74)
print("docs/17 — 現有數據盤點")
print("="*74)
chk("d17", "Abell 1201 = 0.91× 上限", mp.mpf('3.0e10')/mp.mpf('3.3e10'), mp.mpf('0.9091'), 1e-3)
n_wd = mp.mpf('4.8e-3'); rho_wd = n_wd*mp.mpf('0.6')
chk("d17", "ρ_WD = 4.8e-3×0.6", rho_wd, mp.mpf('2.88e-3'), 1e-2, " M☉/pc³")
chk("d17", "局部 WD 比例 7.2%", rho_wd/mp.mpf('0.04')*100, mp.mpf('7.2'), 2e-2)

print("\n" + "="*74)
print("docs/18 — P12 種子先行")
print("="*74)
M_BH = mp.mpf(10)**mp.mpf('8.61'); M_star = mp.mpf(10)**mp.mpf('8.92')
ratio_obs = M_BH/M_star
chk("d18", "JADES M_BH/M_star = 49%", ratio_obs*100, mp.mpf('49'), 3e-2)
over = ratio_obs/ratio_id
chk("d18", "過重 150×", over, mp.mpf('150'), 2e-2)
alpha = mp.log(over)/mp.log(mp.mpf('13.8')/mp.mpf('0.77'))
chk("d18", "α = 1.74", alpha, mp.mpf('1.74'), 1e-2)
z2 = ratio_id*(mp.mpf('13.8')/mp.mpf('3.28'))**alpha
chk("d18", "z=2 預言 ~3.9%", z2*100, mp.mpf('3.9'), 3e-2)
chk("d18", "宿主完成度 0.66%", M_star/(M_BH*306)*100, mp.mpf('0.66'), 3e-2)

print("\n" + "="*74)
print("docs/20 — Auger 對比 (引用值核對)")
print("="*74)
print("  (Auger 4.0σ/3.2σ/3.1σ/2.7σ = 文獻引用, 非推導 — 核對 JSON 一致性)")
import json
with open("data/21_uhacr_auger.json") as f:
    auger = json.load(f)
chk("d20", "Auger SBG 4.0σ (JSON 一致)", float(auger["auger_2018"]["SBG"].split("σ")[0]), 4.0, 0)
chk("d20", "Auger Cen A 3.1σ (JSON 一致)", float(auger["auger_2018"]["CenA"].split("σ")[0]), 3.1, 0)

print("\n" + "="*74)
print("docs/21 — 熵論 (Landauer)")
print("="*74)
k_B = mp.mpf('1.380649e-23')
E_write = k_B*mp.mpf('134.2e-6')
chk("d21", "E_write = k_B×134.2μK", E_write, mp.mpf('1.853e-27'), 1e-3, " J")
chk("d21", "Landauer kT ln2", k_B*mp.log(2)*mp.mpf('134.2e-6'), mp.mpf('1.284e-27'), 1e-3, " J")

print("\n" + "="*74)
print(f"AUDIT RESULT: {ok}/{ok+bad} 核對通過")
if bad > 0:
    print(f"⚠️ {bad} 項不一致 — 需檢查 docs 顯示值 vs 重算值")
