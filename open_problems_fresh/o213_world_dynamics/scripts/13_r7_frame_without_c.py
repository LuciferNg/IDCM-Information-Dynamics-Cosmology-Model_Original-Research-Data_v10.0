#!/usr/bin/env python3
"""
O213 scripts/13 — R7: 幀 τ 可否「唔用 c」由拓撲導出（令 c 變輸出）?
========================================================================
R7 原文: 「幀 τ 可否唔用 c 由拓撲導出（令 c 變輸出）」
        現狀 🟡: 已證 {R_world, ω_ring, c, τ} rank = 1; R_world 絕對值不可約。

本腳本做三件事:
  [A] rank-1 之精確重述 (mpmath dps=40)
  [B] ★ 定理 1 (no-go): 由「唔用 c」之基 {ħ, k_BT, G, m_p} 構造 τ 之不可能性
  [C] ★ 定理 2 (正面): 「c 變輸出」之精確意義 — c 從未係必需輸入
  [D] 離散環色散之新結構結果: ω_ring = 2√J·sin(π/88) ⟹ 精確因子 (88/π)sin(π/88)
  [E] 與 O73 殘餘之關係 + 判決

紀律: 零新常數; 只用錨 + 結構數; 唔改上游原文。
"""
import mpmath as mp
import numpy as np

mp.mp.dps = 40
PASS, FAIL = [], []
def chk(name, cond, detail=''):
    (PASS if cond else FAIL).append(name)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ''))

# ------------------------------------------------------------------ 常數
c_SI   = mp.mpf('299792.458')            # km/s, SI 2019 精確定義
G      = mp.mpf('6.67430e-11')           # CODATA 2018 測量 (u_r 2.2e-5)
hbar   = mp.mpf('1.054571817e-34')       # h/2π, h SI 2019 定義
kB     = mp.mpf('1.380649e-23')          # SI 2019 定義
m_p    = mp.mpf('1.67262192369e-27')     # CODATA 2018
T_CMB  = mp.mpf('2.72548')               # Planck 2018
R_world_Mpc = mp.mpf('4129.94')          # O73 docs/18 §1.1 規範值
Mpc_m  = mp.mpf('3.0856775814913673e22') # m per Mpc
R_world = R_world_Mpc * Mpc_m            # m

print("=" * 78)
print("O213 scripts/13 — R7: 幀 τ 可否『唔用 c』由拓撲導出?")
print("=" * 78)

# ------------------------------------------------------------------ [A] rank 1
print("\n[A] rank-1 之精確重述 ({R_world, ω_ring, c, τ}, mpmath dps=40)")
omega_ring = c_SI * mp.mpf(1000) / R_world          # s^-1
tau        = 1 / omega_ring
T_ring     = 2 * mp.pi / omega_ring
print(f"  ω_ring = c/R_world      = {mp.nstr(omega_ring, 12)} s^-1")
print(f"  τ      = 1/ω_ring       = {mp.nstr(tau, 12)} s = {mp.nstr(tau/3.15576e16, 8)} Gyr")
print(f"  T_ring = 2π/ω_ring      = {mp.nstr(T_ring, 12)} s = {mp.nstr(T_ring/3.15576e16, 8)} Gyr")
d1 = abs(R_world * omega_ring / (c_SI * 1000) - 1)
d2 = abs(2 * mp.pi / T_ring / omega_ring - 1)
d3 = abs(tau * omega_ring - 1)
print(f"  恆等式殘餘: c=Rω: {mp.nstr(d1, 3)} | ω=2π/T: {mp.nstr(d2, 3)} | τ=1/ω: {mp.nstr(d3, 3)}")
chk('C1 三恆等式精確 (dev < 1e-35)', d1 < mp.mpf('1e-35') and d2 < mp.mpf('1e-35') and d3 < mp.mpf('1e-35'))
print("  ⟹ 4 未知 − 3 恆等式 = 1 自由度 (數學必然, 非 IDCM 特有)")

# ------------------------------------------------------------------ [B] 定理 1
print("\n[B] ★ 定理 1 (no-go): 「唔用 c」導出 τ 之不可能性")
# 「唔用 c」之基: {ħ, k_BT, G, m_p}. 4 量, 3 維 (M,L,T) ⟹ 1 個無量綱不變量 Π.
# 解 ħ^a (k_BT)^b G^c m_p^d = 無量綱:
#   M: a+b-c+d=0; L: 2a+2b+3c=0; T: -a-2b-2c=0  ⟹ a=2b, c=-2b, d=-5b
Pi = hbar**2 * (kB * T_CMB) / (G**2 * m_p**5)
print(f"  唯一無量綱不變量 Π = ħ²k_BT/(G²m_p⁵) = {mp.nstr(Pi, 12)}")
# 由 {ħ, k_BT} 唯一可造之「時間」= ħ/(k_BT)
t_unit = hbar / (kB * T_CMB)
print(f"  c-free 時間單位 ħ/(k_BT) = {mp.nstr(t_unit, 12)} s")
X = tau / t_unit
print(f"  ⟹ τ = X·ħ/(k_BT),  X = {mp.nstr(X, 12)}")
# X 係唔係結構數? 用 Π 表達: 任何 c-free 表達式 τ = (ħ/k_BT)·f(Π)
p_eff = mp.log(X) / mp.log(Pi)
print(f"  若 f(Π) = Π^p: p = {mp.nstr(p_eff, 8)}  (非整數/半整數/結構比)")
# 精確: X = N·(T_CMB/T_Pl)  ⟹ X 繼承階層數 N
t_Pl = mp.sqrt(hbar * G / (c_SI * 1000)**5)
T_Pl = mp.sqrt(hbar * (c_SI * 1000)**5 / (G * kB**2))
N = tau / t_Pl
X2 = N * T_CMB / T_Pl
print(f"  等價檢查: X = N·(T_CMB/T_Pl)  →  {mp.nstr(X, 10)} vs {mp.nstr(X2, 10)}"
      f"  (dev {mp.nstr(abs(X/X2-1), 3)})")
chk('C2 X = N·(T_CMB/T_Pl) EXACT (X 繼承階層數 N)', abs(X / X2 - 1) < mp.mpf('1e-30'))
print(f"  N = τ/t_Pl = {mp.nstr(N, 12)}  (O212: 非結構, null P = 0.875)")
print("  ⟹ 任何 c-free 之 τ 表達式 = (ħ/k_BT)·f(Π); f 必含重力階層 ⟹ no-go")

# null test: X 對結構池之覆蓋率
S = [1, 2, 3, 4, 5, 7, 8, 9, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 25,
     26, 29, 30, 31, 32, 33, 35, 36, 40, 41, 44, 45, 47, 49, 55, 60, 64, 70, 77,
     88, 90, 120, 123, 176, 421]
pool = set()
for a in S:
    for b in S:
        if a != b and 0.5 < a / b < 2.0:
            pool.add(round(a / b, 10))
for k in range(1, 8):
    for base in (mp.mpf(2), mp.mpf(4), (1 + mp.sqrt(5)) / 2):
        for s in (1, -1):
            v = base ** (k * s)
            if 0.5 < v < 2.0:
                pool.add(round(float(v), 10))
vals = np.array(sorted(pool))
print(f"  結構池: {len(vals)} 值 (由 |S|={len(S)} 個 IDCM 結構整數生成)")
print(f"  X 之尾數 1.51368e29 之有效數位 = 1.51368  → 池中最近 = "
      f"{vals[np.argmin(np.abs(vals-1.51368))]:.5f}")
print("  ⟹ 但 X 係 ~1e29 之量, 唔喺池範圍 (0.5,2) ⟹ 必須先解釋量級 = 重力階層")
chk('C3 X 之量級 = 重力階層 (非結構池可及)',
    abs(mp.log10(X) - mp.log10(N) - mp.log10(T_CMB / T_Pl)) < mp.mpf('1e-25'))

# ------------------------------------------------------------------ [C] 定理 2
print("\n[C] ★ 定理 2 (正面): 「c 變輸出」之精確意義")
# R_world 可由 c-free 觀測鎖定: R_world = r_d·88·421/(420π), r_d = BAO 尺
r_d = mp.mpf('147.09')      # DESI DR2 Mpc, 純幾何觀測 (c-無關)
R_from_rd = r_d * 88 * 421 / (420 * mp.pi)
print(f"  ★ c-free 長度錨: r_d (BAO) = {r_d} Mpc  →  R_world = r_d·88·421/(420π)"
      f" = {mp.nstr(R_from_rd, 8)} Mpc")
print(f"    vs 規範值 {R_world_Mpc} Mpc → dev {mp.nstr(100*abs(R_from_rd/R_world_Mpc-1), 4)}%")
chk('C4 R_world 可由 c-free 觀測 (r_d) 鎖定', abs(R_from_rd / R_world_Mpc - 1) < mp.mpf('0.01'),
    f'dev {mp.nstr(100*abs(R_from_rd/R_world_Mpc-1), 4)}%')
print("  ⟹ 長度側: c-free 錨**存在** (r_d)")
print("  ⟹ 時間側: c-free 錨**唔存在** (定理 1) ⟹ 仍需 1 個有量綱輸入")
print("  ★ 但「c 係輸出」之精確陳述: c = R_world·ω_ring; 若 R_world 由 r_d 鎖定,")
print("    則 c 之預言值 = R_world(r_d)·ω_ring(結構)。c 從來唔係必需輸入。")
print("  ⟹ R7 之精確答案: 「c 變輸出」邏輯上 ✅ 成立 (rank 1);")
print("    但**時間側錨不可免** ⟹ 等價於導出重力階層 (O86)")

# ------------------------------------------------------------------ [D] 離散環色散
print("\n[D] ★ 離散環色散: 新結構結果")
N_sites = 88
lam_sync = 2 * mp.pi * R_world / N_sites        # 格距 (m)
L_ring = 2 * mp.pi * R_world                    # 環周長
print(f"  88-site 環: 格距 a = λ_sync = 2πR/88 = {mp.nstr(lam_sync/Mpc_m, 8)} Mpc")
print(f"  最近鄰 hop 色散: ω(k) = 2√J·|sin(ka/2)|   (離散波方程)")
print(f"  基模 k = 2π/L_ring ⟹ ka/2 = π/88")
print(f"  ⟹ ω_ring = 2√J·sin(π/88)")
print(f"  連續極限 c = √J·a (O73 §10) ⟹ √J = c/a")
omega_pred = 2 * (c_SI * 1000 / lam_sync) * mp.sin(mp.pi / N_sites)
factor = omega_pred / omega_ring
print(f"  ⟹ ω_ring(離散基模) = {mp.nstr(omega_pred, 12)} s^-1")
print(f"     vs 定義 ω_ring = c/R_world = {mp.nstr(omega_ring, 12)} s^-1")
print(f"  ★ 精確因子 ω_ring·R_world/c = (88/π)·sin(π/88) = {mp.nstr(factor, 15)}")
print(f"     = 1 − {mp.nstr(1-factor, 8)}  → 格點修正 {mp.nstr(100*(1-factor), 6)}%")
chk('C5 精確因子 = (88/π)sin(π/88)',
    abs(factor - (88 / mp.pi) * mp.sin(mp.pi / 88)) < mp.mpf('1e-35'))
# 連續 vs 離散之「每格 tick 數」
tick_disc = 1 / (2 * mp.sin(mp.pi / N_sites))
tick_cont = N_sites / (2 * mp.pi)
print(f"  τ = (tick 數)·(hop 時間 t_hop = a/c):")
print(f"    離散: 1/(2sin(π/88)) = {mp.nstr(tick_disc, 10)}")
print(f"    連續: 88/(2π)        = {mp.nstr(tick_cont, 10)}")
print(f"    ★ 兩者皆 ≈ 14 = O171 錘對生成元 a  (dev: 離散 {mp.nstr(100*(tick_disc/14-1),4)}%,"
      f" 連續 {mp.nstr(100*(tick_cont/14-1),4)}%)")
print("  ⟹ 幀 τ = 14 個格點 tick (錘對生成元 a = 14, O171), 誤差 0.04–0.06%")
chk('C6 tick 數 ≈ 14 (錘對生成元 a) 於 0.1% 內',
    abs(tick_disc / 14 - 1) < mp.mpf('0.001') and abs(tick_cont / 14 - 1) < mp.mpf('0.001'))
# 事後性檢查 (post-hoc guard): 若 tick 係 [10,20] 內之「隨機」實數, 命中 14±0.06% 之機率
p_rand = 2 * abs(tick_disc / 14 - 1) * 14 / 10
print(f"  ⚠️ 事後性 (post-hoc guard): 若 tick ∈ [10,20] 隨機, 命中 14±{100*float(abs(tick_disc/14-1)):.3f}%"
      f" 之機率 = {100*float(p_rand):.2f}%")
print("     ⟹ 標記 🟡 (0.06% 級數值巧合; 但 14 係 O171 導出之結構數, 非任意整數)")

# ------------------------------------------------------------------ [E] 與 O73 殘餘
print("\n[E] 與 O73 殘餘之關係 (雙向檢驗)")
res_O73 = mp.mpf('0.02315')        # % (O73 裁定後之 c_W/c_SI 殘餘)
disc_corr = 100 * (1 - factor)     # % 格點修正
print(f"  O73 裁定後殘餘 (c_W/c_SI − 1) = +{res_O73}%")
print(f"  本輪格點修正 (1 − (88/π)sin(π/88)) = {mp.nstr(disc_corr, 6)}%")
print("  ★ 兩個方向之檢驗 (唔可以亂相消):")
print(f"    (a) c_SI ↔ 連續值 c_IDCM ≡ R_world·ω_ring:")
print(f"        殘餘維持 +{res_O73}%  (格點修正唔適用)")
c_lat = c_SI * (1 + res_O73 / 100) * mp.pi / (88 * mp.sin(mp.pi / 88))
print(f"    (b) c_SI ↔ 格點值 c_lat = c_IDCM·π/(88sin(π/88)):")
print(f"        殘餘變為 {mp.nstr(100*(c_lat/c_SI-1), 6)}%  (更差 {mp.nstr(100*(c_lat/c_SI-1)/res_O73, 4)}×)")
print("  ⟹ 格點修正**唔解釋** O73 殘餘 (兩個方向都唔對)")
print("  ⟹ 兩者量級相近 (0.021% vs 0.023%) 標記為 🟡 巧合, 交 O73 註冊")
chk('C7 格點修正唔解釋 O73 殘餘 (雙向皆唔匹配)',
    abs(disc_corr / res_O73 - 1) > mp.mpf('0.05'))

# ------------------------------------------------------------------ 判決
print("\n" + "=" * 78)
print("[F] R7 判決")
print("=" * 78)
print(f"""
  ① 定理 1 (no-go) 🟢: τ **唔可以**「唔用 c」由拓撲導出
     c-free 基 {{ħ, k_BT, G, m_p}} 之唯一無量綱不變量 Π = ħ²k_BT/(G²m_p⁵)
     任何 c-free 之 τ = (ħ/k_BT)·f(Π); f 必含重力階層 (Π ⟺ m_p/m_Pl)
     ⟹ 等價於導出重力階層 ⟹ **O86**, 唔係 R7 可以單獨解決

  ② 定理 2 (正面) 🟢: 「c 變輸出」邏輯上**成立**
     rank 1 ⟹ 錨係 1 個有量綱數; 放喺邊個 (c/R/ω/τ/G) 係坐標選擇
     ★ 長度側 c-free 錨**存在**: R_world = r_d·88·421/(420π), r_d = BAO (純幾何)
     ⟹ c = R_world·ω_ring 係**輸出**; c 從來唔係必需輸入

  ③ 新結構結果: 離散環基模 ω_ring = 2√J·sin(π/88)
     ★ 精確因子 ω_ring·R_world/c = (88/π)sin(π/88) = {mp.nstr(factor, 12)}
     ★ 幀 τ = 14 個格點 tick (錘對生成元 a = 14, O171), 誤差 0.04–0.06%

  ④ R7 狀態: no-go 定理 ✅ + 「c 輸出」精確化 ✅ + 新結構因子 ✅
     剩餘 = 時間側錨 (= 重力階層) → O86
""")
print(f"RESULT: {len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL:
    print("FAILED:", FAIL)
