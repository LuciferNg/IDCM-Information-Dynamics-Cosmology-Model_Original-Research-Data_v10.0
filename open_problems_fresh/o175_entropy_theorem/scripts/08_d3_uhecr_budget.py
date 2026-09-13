#!/usr/bin/env python3
"""
O175 遺留攻堅 D3: 耗散熵流 vs UHECR 預算 — 定量閉合嘗試 (用戶指示: 在 O175 內推)
=====================================================================
Observed anchor (Auger-constrained, independent 2024/2025 papers):
  L_UHECR ~ 10^45 erg Mpc^-3 yr^-1 (production rate density, above 0.6-5 EeV)
  => rho_UHECR ~ L x t_H ~ 4.7e-19 erg/cm^3 (consistent w/ Auger energy density)

IDCM channels:
  (a) write channel: 44 x B(n) x gamma per cycle = control parameter (O175 定理1)
  (b) strain pool release: R_rel = 6,730.86 M_sun/yr (O173 steady state)
  (c) pool turnover: 364 池/圈, t_turn = T_ring/364 (O177)

判決: naive「池支付 UHECR」讀法 fail (factor ~2.5e5) → 正確通道 = 黑洞轉化 (O121/O173)
"""
import mpmath as mp
mp.mp.dps = 40

PASS = 0; FAIL = 0
def ck(claim, cond, info=""):
    global PASS, FAIL
    if cond: PASS += 1; print(f"  [✔] {claim} {info}")
    else:    FAIL += 1; print(f"  [✘] {claim} {info}")

# ── 常數 ──
T_ring = mp.mpf('84.6349')          # Gyr
R_rel = mp.mpf('6730.85550941724')  # M_sun/yr (O173 穩態釋放率)
E_strain = mp.mpf('1564785320847.4905')  # M_sun (池)
M_sun = mp.mpf('1.989e30')          # kg
c2 = mp.mpf('8.98755e16')           # m^2/s^2
Mpc_m = mp.mpf('3.085677581e22')    # m
R_world_Mpc = mp.mpf('4129.94')     # Mpc
V_univ_Mpc3 = mp.mpf(4)/3*mp.pi*R_world_Mpc**3
L_UHECR = mp.mpf('1e45')            # erg Mpc^-3 yr^-1 (Auger-constrained)

# ── (a) 寫入通道能量率 (相位級控制, O175) ──
# 每圈寫入能量 (μK·k_B 單位): 44 × B(n) × γ = 61.5 × 192
E_write_cycle = mp.mpf('61.5')*mp.mpf('192')          # μK·k_B
# 轉 erg: 1 μK·k_B = 1e-6 K × 1.380649e-16 erg/K = 1.380649e-22 erg
E_write_erg_yr = E_write_cycle*mp.mpf('1.380649e-22')/(T_ring*mp.mpf('1e9'))
L_write = E_write_erg_yr/V_univ_Mpc3                  # erg Mpc^-3 yr^-1
print(f"(a) 寫入通道: {mp.nstr(E_write_erg_yr,4)} erg/yr global = {mp.nstr(L_write,4)} erg Mpc^-3 yr^-1")
ck("D3-1: 寫入通道 << UHECR (11 數量級) — 寫入係控制參數, 唔係能量對等 (O175 定理1 重現)",
   L_write < L_UHECR/mp.mpf('1e8'))

# ── (b) 池釋放通道 ──
L_pool = R_rel*M_sun*c2/V_univ_Mpc3                  # erg Mpc^-3 yr^-1
print(f"(b) 池釋放: {mp.nstr(R_rel*M_sun*c2,4)} erg/yr = {mp.nstr(L_pool,4)} erg Mpc^-3 yr^-1")
ck("D3-2: 池平均釋放率對比 UHECR 生產率密度",
   L_pool < L_UHECR, f"ratio L_UHECR/L_pool = {mp.nstr(L_UHECR/L_pool,5)}")
factor = L_UHECR/L_pool
print(f"    ★ naive「池支付 UHECR」讀法 deficit = {mp.nstr(factor,5)}")

# ── (c) 池週轉後總處理能量 ──
t_univ = mp.mpf('13.8')                               # Gyr
turnovers = t_univ*mp.mpf('1e9')/(T_ring*mp.mpf('1e9')/364)
E_total_pool = E_strain*M_sun*c2*turnovers            # erg (週轉後總能量)
E_UHECR_total = L_UHECR*V_univ_Mpc3*t_univ*mp.mpf('1e9')
print(f"(c) 池週轉 {mp.nstr(turnovers,5)} 次 → 總處理 {mp.nstr(E_total_pool,4)} erg")
print(f"    UHECR 宇宙總預算 {mp.nstr(E_UHECR_total,4)} erg → deficit {mp.nstr(E_UHECR_total/E_total_pool,5)}")
ck("D3-3: 全週轉池能量仍 < UHECR 總預算 (deficit > 100)",
   E_UHECR_total > 100*E_total_pool)

# ── 結論通道重定向 ──
print()
print("判決: naive「池支付 UHECR 能量」讀法 **fail** (deficit ~2.5e5)")
print("→ 正確通道: UHECR 能量 = 黑洞轉化 (O121/O173: SMBH=轉化器, P14 M_BH/M* = 1/306),")
print("  唔係池平均釋放 — 同主流物理 (AGN/GRB 為 UHECR 源) 一致")
print(f"D3 AUDIT: {PASS}/{PASS+FAIL}")
import sys; sys.exit(0 if FAIL == 0 else 1)
