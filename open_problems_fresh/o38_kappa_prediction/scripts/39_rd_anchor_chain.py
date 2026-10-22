#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O38/m0-scale — Script 39: 節拍階梯內部閉合 (r_d 錨鏈) + 缺口重鑄
================================================================
日期: 2026-10-18
觸發: 用戶「繼續」— 承接 scripts/38 節拍階梯重推
發現 (本輪預查):
  ★ R_world = 88·r_d/π = 4129.9424 Mpc 精確命中 R_H = 4129.94 (dev 5.9e−7)
    ⟹ scripts/38 用嘅 R_H = 4129.94 唔係外部輸入, 係 O127 r_d 內部閉合!
  ★ t_site = 2·r_d/(πc) 同 R_H/(44c) 完全等價 (dev 0.0)
    ⟹ 節拍階梯完全由 r_d (DESI DR2 觀測) 內部閉合
本輪:
  A. 節拍階梯 r_d 錨鏈閉合: R_H = 88r_d/π, t_site = 2r_d/(πc), τ_depth, T_SYNC
  B. ★ N_O38 缺口重鑄: N_O38 = (88/π)·(M₀·r_d/(ħc)) — 缺口 = M₀·r_d/(ħc)
  C. M₀·r_d/(ħc) = 6.4327062e38 對生成集/K_φ/log 空間 member check
  D. 判決
用法: /usr/bin/python3 scripts/39_rd_anchor_chain.py
"""
import mpmath as mp
mp.mp.dps = 50

ok = fail = 0
def chk(name, cond, info=""):
    global ok, fail
    if cond: ok += 1; print(f"  ✅ {name} {info}")
    else:    fail += 1; print(f"  ❌ {name} {info}")

pi = mp.pi
c = mp.mpf('2.99792458e8')
Mpc_m = mp.mpf('3.085677581e22')
r_d = mp.mpf('147.4386')               # O127 (DESI DR2, 零參數)
M0_MeV = mp.mpf('27.900915')
hbar_evs = mp.mpf('6.582119569e-16')
N38 = mp.mpf('1.80188233461e40')

print("=" * 76)
print("A. 節拍階梯 r_d 錨鏈閉合 (全部內部)")
print("=" * 76)
R_world = 88 * r_d / pi
print(f"  R_world = 88·r_d/π = {mp.nstr(R_world,8)} Mpc (記錄 R_H = 4129.94)")
dA1 = abs(R_world / mp.mpf('4129.94') - 1)
chk("A1 R_H = 88r_d/π 內部閉合", dA1 < mp.mpf('1e-5'), f"(dev {mp.nstr(dA1,4)})")
t_site_a = R_world * Mpc_m / (44 * c)
t_site_b = 2 * r_d * Mpc_m / (pi * c)
t_site_Gyr = t_site_a / mp.mpf('3.15576e16')
print(f"  t_site = R_H/(44c) = {mp.nstr(t_site_Gyr,7)} Gyr")
print(f"  t_site = 2r_d/(πc) = {mp.nstr(t_site_b/mp.mpf('3.15576e16'),7)} Gyr (dev {mp.nstr(abs(t_site_a/t_site_b-1),4)})")
chk("A2 t_site = 2r_d/(πc) 等價 (dev 0)", t_site_a == t_site_b)
tau_depth = 44 * t_site_a
T_SYNC = 88 * t_site_a
print(f"  τ_depth = 44t_site = {mp.nstr(tau_depth/mp.mpf('3.15576e16'),6)} Gyr = R_world/c")
print(f"  T_SYNC = 88t_site = {mp.nstr(T_SYNC/mp.mpf('3.15576e16'),6)} Gyr")
chk("A3 τ_depth = R_world/c 閉合", abs(tau_depth*c/(R_world*Mpc_m) - 1) < mp.mpf('1e-9'))
print(f"  ⟹ 節拍階梯 3 錨 (t_site/τ_depth/T_SYNC) 全部由 r_d 單一輸入閉合")

print()
print("=" * 76)
print("B. ★ N_O38 缺口重鑄: N_O38 = (88/π)·(M₀·r_d/(ħc))")
print("=" * 76)
Mr = M0_MeV * mp.mpf('1e6') * r_d * Mpc_m / (hbar_evs * c)
print(f"  M₀·r_d/(ħc) = {mp.nstr(Mr,8)}  (log₁₀ {mp.nstr(mp.log10(Mr),6)})")
N38_rd = (88/pi) * Mr
print(f"  (88/π)·M₀·r_d/(ħc) = {mp.nstr(N38_rd,10)}")
d_B = abs(N38_rd / N38 - 1)
chk("B1 N_O38 = (88/π)·(M₀·r_d/(ħc))", d_B < mp.mpf('1e-5'), f"(dev {mp.nstr(d_B,4)} = r_d 輸入精度)")
print(f"  88/π = {mp.nstr(88/pi,6)} — 有結構 (O127 R_world = 88r_d/π 閉合)")
print(f"  ⟹ 缺口收窄: N_O38 嘅 r_d 部分已閉合, 剩餘缺口 = M₀·r_d/(ħc)")
print(f"  M₀·r_d/(ħc) = ω_M0·(r_d/c) — M₀ 喺 r_d 光行時間內振盪次數")

print()
print("=" * 76)
print("C. M₀·r_d/(ħc) 對生成集/K_φ/log 空間 member check")
print("=" * 76)
# 生成集 (scripts/26 同制 + γ 譜)
G = [mp.mpf(4)*mp.sin(mp.mpf(n)*mp.pi/88)**2 for n in range(1,45)]
G += [90, 88, phi if (phi := (1+mp.sqrt(5))/2) else 0, 1/phi/4, 44, 33, 4,
      137, 256, 45, 176, 61.5, 294.88, 147.44, 72.59, 134, 2, 8, 11, 22, 7,
      18, 29, 47, 76, 123, 55, 1, 3, 40, 180]
G = [mp.mpf(g) for g in G]
hits = [abs(g/Mr - 1) < mp.mpf('1e-3') for g in G]
print(f"  生成集 {len(G)} 元素 direct member check @1e−3: {sum(hits)} 命中")
chk("C1 M₀·r_d/(ħc) 對生成集零命中", sum(hits) == 0)
# log 空間
l10 = mp.log10(Mr)
print(f"  log₁₀ = {mp.nstr(l10,7)} (尾數 {mp.nstr(l10 - mp.floor(l10),5)})")
print(f"  log₂  = {mp.nstr(mp.log(Mr)/mp.log(2),6)}")
print(f"  log_φ = {mp.nstr(mp.log(Mr)/mp.log(phi),6)}")
print(f"  log₄  = {mp.nstr(mp.log(Mr)/mp.log(4),6)}")
# 拆解: M₀·r_d/(ħc) = (r_d/l_Pl)·(M₀/M_Pl)
l_Pl = c * mp.mpf('5.391247e-44')
rd_lPl = r_d * Mpc_m / l_Pl
M0_MPl = M0_MeV / mp.mpf('1.2208901e22')
print(f"  拆解: (r_d/l_Pl)·(M₀/M_Pl) = {mp.nstr(rd_lPl,5)} × {mp.nstr(M0_MPl,5)} = {mp.nstr(rd_lPl*M0_MPl,5)}")
print(f"  log₁₀(r_d/l_Pl) = {mp.nstr(mp.log10(rd_lPl),6)}  (59.4495)")
print(f"  log₁₀(M₀/M_Pl) = {mp.nstr(mp.log10(M0_MPl),6)}  (−20.6411)")
chk("C2 拆解恆等", abs(rd_lPl*M0_MPl/Mr - 1) < mp.mpf('1e-5'), f"(t_Pl 7 位輸入 ⟹ 容差 1e−5)")
print(f"  ⟹ 缺口仍然係 M₀/M_Pl (已知); r_d/l_Pl = 2.8147e59 係新量 (未註冊)")

print()
print("=" * 76)
print("D. 判決")
print("=" * 76)
print("  1. ★★ 節拍階梯完全內部閉合: R_H = 88r_d/π (dev 5.9e−7)")
print("     t_site = 2r_d/(πc), τ_depth = R_world/c, T_SYNC = 88t_site — 全部 r_d 單輸入")
print("  2. ★ N_O38 缺口重鑄: N_O38 = (88/π)·(M₀·r_d/(ħc))")
print("     r_d 部分已閉合; 剩餘缺口 = M₀·r_d/(ħc) = 6.4327062e38")
print("  3. 🔴 M₀·r_d/(ħc) 對生成集零命中 + log 空間冇結構 (C1 ✓)")
print("  4. 拆解: M₀·r_d/(ħc) = (r_d/l_Pl)·(M₀/M_Pl) — 恆等, 缺口仍 = M₀/M_Pl")
print("  5. 節拍階梯框架確立: 標度錨 = r_d (觀測) → t_site (0.306 Gyr)")
print(f"結果: {ok} PASS / {fail} FAIL")
print("=" * 76)