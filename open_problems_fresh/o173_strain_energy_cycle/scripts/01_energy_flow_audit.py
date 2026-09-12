#!/usr/bin/env python3
"""
O173 script 01 — 能量流盤點 (Energy Flow Audit)
================================================
全鏈審計: E_strain 池 → 凝聚 (η=φ^-21) → LRD 輻射 (λ=10%) → 末端去向

錨點 (crystal_stress records 04/07/12/13):
  E_strain = 32·μ·ε²·V_edge = (π²/75)·M_Pl·(R_H/L_P)·44^-6  (dev 0.0045%)
  η = φ^-21 = φ^{-(N_d−μ²)/2}
  COSMOS-Web: 434 LRDs @ 0.54 deg², median M = 6.97e6 M☉ (λ=10% 假設)
  M(8) = E_strain·η·S(8)·f(4) = 1.914e6 M☉ (hop=4 零環境)

問題: 池有限 (開放耗散) 定係再生 (閉合循環)?
"""
import math, json
import mpmath as mp

mp.mp.dps = 50
PASS = 0; FAIL = 0
def ck(name, cond, info=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {info}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {info}")

print("="*74)
print("Part A — 池與凝聚預算 (池 = 即時應變庫存, 唔係一次性燃料)")
print("="*74)

# --- 常數 (script 13 同源) ---
H0 = mp.mpf('72.59')*mp.mpf('1e3')/(mp.mpf('3.085677581e22'))  # s^-1  (ω_ring)
G  = mp.mpf('6.674e-11')
c  = mp.mpf('2.99792458e8')
M_Pl = mp.mpf('2.176434e-8')   # kg
L_P  = mp.mpf('1.616255e-35')  # m
M_sun = mp.mpf('1.98892e30')   # kg
R_H_m = c/H0                    # 世界環半徑 (m)
lam_sync = 2*mp.pi*R_H_m/88     # λ_sync (m)
rho_crit = 3*H0**2/(8*mp.pi*G)
eps = mp.mpf(1)/30
V_edge = (lam_sync/44)**3

# E_strain 數值式 (record 07): 32·μ·ε²·V_edge, μ=ρ_crit c²
E_strain_kg = 32 * rho_crit*c**2 * eps**2 * V_edge / c**2   # kg
# 閉合形式: (π²/75)·M_Pl·(R_H/L_P)·44^-6
closed = (mp.pi**2/75)*M_Pl*(R_H_m/L_P)/44**6
dev = abs(E_strain_kg - closed)/closed
print(f"  E_strain = {mp.nstr(E_strain_kg, 8)} kg = {mp.nstr(E_strain_kg/M_sun, 8)} M☉")
print(f"  閉合形式   = {mp.nstr(closed, 8)} kg  dev = {mp.nstr(dev*100, 5)}%")
ck("A1 E_strain 閉合形式 (dev < 0.01%)", dev < mp.mpf('1e-4'), f"({mp.nstr(dev*100,4)}%)")

E_pool = E_strain_kg/M_sun   # M☉
ck("A2 池 = 1.565e12 M☉ (record 04)", abs(E_pool - mp.mpf('1.565e12'))/mp.mpf('1.565e12') < mp.mpf('0.01'), f"= {mp.nstr(E_pool,6)}")

# --- 凝聚效率 η = φ^-21 ---
phi = (1+mp.sqrt(5))/2
eta = phi**(-21)
ck("A3 η = φ^-21 = 4.0909e-5", abs(eta - mp.mpf('4.0909e-5'))/mp.mpf('4.0909e-5') < mp.mpf('0.01'), f"= {mp.nstr(eta,7)}")
ck("A4 21 = (N_d−μ²)/2 譜身份", 21 == (44-2)//2, "(44-2)/2 = 21 ✓")

# --- 一次性凝聚預算 (無再生) ---
budget_total = E_pool*eta
print(f"\n  一次性凝聚預算 (池×η) = {mp.nstr(budget_total,6)} M☉  — 整個晶格, 全部節點, 一次過")
ck("A5 一次性預算 = 6.4e7 M☉", abs(budget_total - mp.mpf('6.4e7'))/mp.mpf('6.4e7') < mp.mpf('0.02'), f"= {mp.nstr(budget_total,5)}")

# --- 節點 8 (COSMOS) 配額 ---
S8 = mp.mpf('0.047048509643483345')
f4 = 1 - mp.mpf('0.3636')          # f(hop=4) 干涉核
M_base8 = E_pool*eta*S8*f4
strain_per_event = E_pool*S8*f4    # = M_base/η: 每次凝聚事件消耗嘅應變
print(f"\n  節點 8 (COSMOS, hop=4): S(8)={mp.nstr(S8,5)}, f(4)={mp.nstr(f4,5)}")
print(f"  M_base(8) = {mp.nstr(M_base8,6)} M☉  (record 07: 1.914e6 ✓)")
print(f"  每次事件消耗應變 = M_base/η = {mp.nstr(strain_per_event,6)} M☉")
ck("A6 M_base(8) = 1.914e6 M☉", abs(M_base8 - mp.mpf('1.914e6'))/mp.mpf('1.914e6') < mp.mpf('0.01'), f"= {mp.nstr(M_base8,6)}")
ck("A7 節點 8 嘅應變配額 = 4.69e10 M☉ (成個池 × S·f)", abs(strain_per_event - mp.mpf('4.69e10'))/mp.mpf('4.69e10') < mp.mpf('0.01'), f"= {mp.nstr(strain_per_event,5)}")

print("\n" + "="*74)
print("Part B — 觀測凝聚量 vs 預算 (證偽測試)")
print("="*74)
N_lrd = 434
M_obs_med = mp.mpf('6.97e6')     # M☉ median (λ=10% 假設, record 12 ratio 0.9994)
M_cond_obs = N_lrd*M_obs_med
frac_pool = M_cond_obs/E_pool
print(f"  觀測 (COSMOS-Web 0.54 deg²): {N_lrd} LRD × median {mp.nstr(M_obs_med,5)} M☉")
print(f"  = {mp.nstr(M_cond_obs,6)} M☉ = {mp.nstr(frac_pool*100,4)}% 池 (record: 0.193%)")
ck("B1 記錄 0.193% 一致", abs(frac_pool*100 - mp.mpf('0.193'))/mp.mpf('0.193') < mp.mpf('0.02'), f"= {mp.nstr(frac_pool*100,5)}%")
ck("B2 觀測凝聚 (3.0e9) > 一次性預算 (6.4e7) — 47×", M_cond_obs/budget_total > 40, f"ratio = {mp.nstr(M_cond_obs/budget_total,4)}×")

# 應變消耗 (每次事件 ≥ M_base/η; median 事件含 δ 放大)
strain_obs_base = N_lrd*strain_per_event
ratio_pool_base = strain_obs_base/E_pool
delta_cosmos = (M_obs_med/M_base8)**(mp.mpf(2)/3) - 1
strain_obs_delta = N_lrd*(M_obs_med/eta)
ratio_pool_delta = strain_obs_delta/E_pool
print(f"\n  δ 反解 (record 07): (1+δ)^1.5 = {mp.nstr(M_obs_med/M_base8,5)} → δ = {mp.nstr(delta_cosmos,4)}")
print(f"  應變消耗 (base, 434×4.69e10) = {mp.nstr(strain_obs_base,5)} M☉ = {mp.nstr(ratio_pool_base,4)}× 池")
print(f"  應變消耗 (含 δ median, 434×M/η) = {mp.nstr(strain_obs_delta,5)} M☉ = {mp.nstr(ratio_pool_delta,4)}× 池")
ck("B3 有限池被證偽 (base): 已消耗 13× 成個池", ratio_pool_base > 10, f"ratio = {mp.nstr(ratio_pool_base,4)}")
ck("B4 有限池被證偽 (含 δ): 已消耗 47× 成個池", ratio_pool_delta > 40, f"ratio = {mp.nstr(ratio_pool_delta,4)}")
ck("B5 第一個 median LRD 已用 3.6× 節點配額", M_obs_med/M_base8 > 3, f"= {mp.nstr(M_obs_med/M_base8,4)}× (δ 環境放大)")

print("\n" + "="*74)
print("Part C — 釋放率與耗盡時標")
print("="*74)
# 觀測平均形成率 (節點 8): 434 events / 活動窗口
t_active = mp.mpf('11e9')          # yr (z~9→0 渲染窗口, 保守)
rate_mass_node = M_cond_obs/t_active
rate_strain_node = rate_mass_node/eta
print(f"  節點 8 質量形成率 = {mp.nstr(rate_mass_node,5)} M☉/yr  (= 434×6.97e6 / 11 Gyr)")
print(f"  節點 8 應變消耗率 = {mp.nstr(rate_strain_node,5)} M☉/yr  (= 質量率/η)")
t_exh_node = strain_per_event/rate_strain_node
t_exh_pool = E_pool/rate_strain_node
print(f"  節點配額耗盡時標 = {mp.nstr(t_exh_node/1e6,5)} Myr  (配額 / 消耗率)")
print(f"  成個池耗盡時標   = {mp.nstr(t_exh_pool/1e9,5)} Gyr  (池 / 消耗率)")
ck("C1 節點配額耗盡 ~8.8 Myr ≪ 活動窗口 11 Gyr", t_exh_node < mp.mpf('1e8'), f"= {mp.nstr(t_exh_node/1e6,4)} Myr")
ck("C2 池耗盡 ~0.29 Gyr ≪ 11 Gyr (有限池矛盾)", t_exh_pool < mp.mpf('1e9'), f"= {mp.nstr(t_exh_pool/1e9,4)} Gyr")

# LRD 輻射率 (record: 1.54 M☉/yr/核 — 09-11 討論值, = Lbol/(0.1·c²))
L_Edd = mp.mpf('1.26e38')*M_obs_med          # erg/s (Eddington)
Lbol = mp.mpf('9.91')*L_Edd                    # λ_Edd = 9.91 ≈ 10
Mdot_rad_kg_s = (Lbol*1e-7)/(mp.mpf('0.1')*c**2)   # kg/s (Lbol erg→J ×1e-7)
Mdot_rad = Mdot_rad_kg_s*mp.mpf('3.156e7')/M_sun   # M☉/yr
print(f"\n  L_Edd(6.97e6) = {mp.nstr(L_Edd,5)} erg/s; Lbol = 9.91×L_Edd")
print(f"  M_dot(輻射) = Lbol/(0.1c²) = {mp.nstr(Mdot_rad,5)} M☉/yr/核  (record: 1.54)")
ck("C3 輻射率 1.54 M☉/yr/核 重現", abs(Mdot_rad - mp.mpf('1.54'))/mp.mpf('1.54') < mp.mpf('0.02'), f"= {mp.nstr(Mdot_rad,5)}")
t_cond_arith = M_obs_med/Mdot_rad
print(f"  ⚠️ 交接文檔「凝聚時標 3.2e7 yr = 6.97e6/1.54」算術檢查: 6.97e6/1.54 = {mp.nstr(t_cond_arith/1e6,4)} Myr ≠ 32 Myr")
ck("C4 交接算術修正: 6.97e6/1.54 = 4.5 Myr (32 Myr 對應率 0.218)", abs(t_cond_arith - mp.mpf('4.53e6'))/mp.mpf('4.53e6') < mp.mpf('0.02'), f"= {mp.nstr(t_cond_arith/1e6,4)} Myr")

# UHECR 釋放率 (標準 emissivity ~5e44 erg/Mpc³/yr ≥ 1e18.5 eV)
V_uni = 4*mp.pi/3*R_H_m**3/(mp.mpf('3.085677581e22'))**3   # Mpc³
P_uhecr = mp.mpf('5e44')*V_uni                              # erg/yr
M_uhecr = (P_uhecr*1e-7)/(M_sun*c**2)                       # M☉/yr (1 M☉c² = 1.79e47 J)
print(f"  宇宙體積 = {mp.nstr(V_uni,5)} Mpc³; UHECR 功率 ≈ {mp.nstr(P_uhecr,3)} erg/yr = {mp.nstr(M_uhecr,4)} M☉/yr")
ck("C5 UHECR 釋放 (~80 M☉/yr) ≪ 節點應變消耗率 6731 M☉/yr — 次要通道", M_uhecr < rate_strain_node/mp.mpf('10'), f"= {mp.nstr(M_uhecr,4)} M☉/yr vs {mp.nstr(rate_strain_node,5)}")

print("\n" + "="*74)
print("Part D — 時標層級 (hierarchy)")
print("="*74)
T_ring = mp.mpf('84.6349')       # Gyr (SYNC)
T_beat = mp.mpf('45963')         # Gyr (拓撲拍頻, record 04: 3330× 宇宙年齡)
tau     = mp.mpf('13.4701')      # Gyr 渲染深度
t_true  = mp.mpf('11100.64')     # Gyr (O51)
print(f"  t_cond ~ {mp.nstr(t_cond_arith/1e6,4)} Myr (4.5-32)  ≪  T_ring = {mp.nstr(T_ring,6)} Gyr  ≪  T_beat = {mp.nstr(T_beat,6)} Gyr")
print(f"  τ = {mp.nstr(tau,6)} Gyr;  t_true = {mp.nstr(t_true,6)} Gyr (O51)")
ck("D1 層級: t_cond ≪ T_ring ≪ T_beat", t_cond_arith < mp.mpf('1e9') and T_ring < T_beat, "")
ck("D2 活動窗口 11 Gyr = 0.13×T_ring — 池冇老化嘅觀測窗", mp.mpf('11e9')/(T_ring*1e9) < mp.mpf('1'), f"= {mp.nstr(mp.mpf('11e9')/(T_ring*1e9),4)} 週期")

# 保存
out = {
  "E_strain_kg": float(E_strain_kg), "E_strain_Msun": float(E_pool),
  "closed_dev_pct": float(dev*100), "eta": float(eta),
  "budget_total_Msun": float(budget_total),
  "M_base8_Msun": float(M_base8), "strain_per_event_Msun": float(strain_per_event),
  "N_lrd": N_lrd, "M_obs_median_Msun": float(M_obs_med),
  "M_cond_obs_Msun": float(M_cond_obs), "frac_pool_pct": float(frac_pool*100),
  "ratio_pool_base": float(ratio_pool_base), "ratio_pool_delta": float(ratio_pool_delta),
  "delta_cosmos": float(delta_cosmos),
  "rate_mass_node_Msun_yr": float(rate_mass_node), "rate_strain_node_Msun_yr": float(rate_strain_node),
  "t_exhaust_node_Myr": float(t_exh_node/1e6), "t_exhaust_pool_Gyr": float(t_exh_pool/1e9),
  "Mdot_rad_Msun_yr": float(Mdot_rad), "t_cond_Myr": float(t_cond_arith/1e6),
  "M_uhecr_Msun_yr": float(M_uhecr),
  "T_ring_Gyr": float(T_ring), "T_beat_Gyr": float(T_beat), "tau_Gyr": float(tau),
  "t_true_Gyr": float(t_true),
}
with open("data/01_energy_flow.json", "w") as f:
    json.dump(out, f, indent=2)
print(f"\nSaved data/01_energy_flow.json")
print(f"\nRESULT: {PASS}/{PASS+FAIL} PASS")
