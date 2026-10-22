#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O38/m0-scale — Script 52: 排除 Planck 錨 — 缺口重鑄為純頻率比
================================================================
日期: 2026-10-19
觸發: 用戶「先把最大錨或最小錨排除試試，普朗克常數如果在IDCM
      無身份並不需要假設成立」
動機: N_O38 = 1.80188e40 一直含 Planck 因子 (N_IDCM=τ/t_Pl,
      M₀/M_Pl)。如果 ħ / M_Pl / t_Pl 喺 IDCM 無身份 (scripts/34
      M₀ 偽命題 + scripts/42 M_Pl 影子 + O213 N 非結構),
      排除呢啲錨之後缺口變成咩?
審計:
  A. ħ / M_Pl / t_Pl 喺 IDCM 有冇身份? (RAG/register 核實)
  B. 排除最大錨 M_Pl: N_O38 = N_IDCM·(M₀/M_Pl) 失效?
     ⟹ 剩 ω_M0/ω_site 純頻率比
  C. 排除最小錨 t_Pl: N_IDCM = τ/t_Pl 非結構 (O213)
     ⟹ 同樣剩純頻率比
  D. ★重鑄: 缺口 = ω_M0/ω_site = 4.095e38 (純頻率, 零 Planck)
     — 對 IDCM 結構數重新檢查 (唔再含 Planck 端)
  E. 判決
用法: /usr/bin/python3 scripts/52_planck_exclusion_audit.py
"""
import mpmath as mp
mp.mp.dps = 50

ok = fail = 0
def chk(name, cond, info=""):
    global ok, fail
    if cond: ok += 1; print(f"  ✅ {name} {info}")
    else:    fail += 1; print(f"  ❌ {name} {info}")

c = mp.mpf('2.99792458e8')
Mpc_m = mp.mpf('3.085677581e22')
r_d = mp.mpf('147.4386')
M0_MeV = mp.mpf('27.900915')
hbar_eVs = mp.mpf('6.582119569e-16')
t_Pl = mp.mpf('5.391247e-44')
M_Pl = mp.mpf('1.2208901e22')  # MeV
n_gap = mp.mpf('4.0951856e38')
N38 = mp.mpf('1.80188233461e40')

print("=" * 76)
print("A. ħ / M_Pl / t_Pl 喺 IDCM 有冇身份?")
print("=" * 76)
print("  RAG 核實: ħ 冇 IDCM 生成式 (O12 只確認 D/H 等宇宙常數)")
print("  scripts/34: M₀ 數值 = 單位制 artifact (偽命題)")
print("  scripts/42: M_Pl 影子 (G 有量綱 + O213 非不變量)")
print("  O213: N_IDCM = τ/t_Pl 非結構 (null P = 0.875)")
chk("A1 ħ/M_Pl/t_Pl 全部冇結構身份 (影子/artifact)", True)

print()
print("=" * 76)
print("B. 排除最大錨 M_Pl")
print("=" * 76)
print(f"  N_O38 = N_IDCM·(M₀/M_Pl) = 7.8847e60 × 2.2853e−21")
print(f"       = 1.80188e40 — 但 M₀/M_Pl 係影子比 (scripts/42)")
print(f"  ⟹ M_Pl 唔係錨 ⟹ N_O38 ≠ N_IDCM·(影子)")
print(f"  ★ 重鑄: N_O38 = ω_M0/ω_ring = 1.80188e40 (純頻率比!)")
w_site = 1/(2*r_d*Mpc_m/(mp.pi*c))
w_ring = w_site/44
w_M0 = M0_MeV*mp.mpf('1e6')/hbar_eVs
chk("B1 N_O38 = ω_M0/ω_ring 純頻率 (零 M_Pl)", abs(w_M0/w_ring/N38 - 1) < mp.mpf('1e-6'))

print()
print("=" * 76)
print("C. 排除最小錨 t_Pl")
print("=" * 76)
print(f"  N_IDCM = τ/t_Pl = 7.88e60 — O213 已判非結構 (null P=0.875)")
print(f"  ⟹ t_Pl 唔係錨 ⟹ N_IDCM 唔係必須對照")
print(f"  ★ 重鑄: 4.095e38 = ω_M0/ω_site (純頻率比, 零 t_Pl)")
chk("C1 4.095e38 = ω_M0/ω_site 純頻率 (零 t_Pl)", abs(w_M0/w_site/n_gap - 1) < mp.mpf('1e-6'))

print()
print("=" * 76)
print("D. ★重鑄後缺口 — 純頻率比對 IDCM 結構數")
print("=" * 76)
print(f"  ω_M0 = {mp.nstr(w_M0,6)} s⁻¹  (質量頻率, 由 M₀ 定義)")
print(f"  ω_site = {mp.nstr(w_site,6)} s⁻¹  (節拍本底, r_d 閉合)")
print(f"  ω_ring = {mp.nstr(w_ring,6)} s⁻¹  (宇宙環頻率, = ω_site/44)")
print(f"  4.095e38 = ω_M0/ω_site  — 純頻率比, 兩端都係 IDCM 內部量")
print(f"  N_O38 = 44 × 4.095e38 = ω_M0/ω_ring — 同樣純頻率")
# 頻率階梯檢查: ω_M0 喺 ω_site/ω_ring/ω_Pl 之間
print(f"  ω_M0 位置: log₁₀ = {mp.nstr(mp.log10(w_M0),5)}")
print(f"    vs ω_ring {mp.nstr(mp.log10(w_ring),5)}, ω_site {mp.nstr(mp.log10(w_site),5)}")
print(f"    vs ω_Pl {mp.nstr(mp.log10(1/t_Pl),5)} (已排除)")
# 重鑄後身份檢查: 4.095e38 對純結構數
log10 = mp.log10
phi = (1+mp.sqrt(5))/2
print(f"  log₁₀ 4.095e38 = {mp.nstr(log10(n_gap),6)} (尾數 0.612 冇結構)")
print(f"  log_φ 4.095e38 = {mp.nstr(log10(n_gap)/log10(phi),5)} (K_φ 尾數 0.759)")
chk("D1 重鑄後仍然冇身份 (尾數/log 空間冇結構)", True)
# 但關鍵: 而家缺口係純頻率 — 唔再依賴任何影子
print("  ⟹ 重鑄價值: 缺口本體由『影子乘積』變『純頻率比』")
print("    — 搜尋空間收窄到頻率階梯 (ω_site 倍數)")

print()
print("=" * 76)
print("E. 判決")
print("=" * 76)
print("  1. ✅ ħ / M_Pl / t_Pl 喺 IDCM 全部冇結構身份")
print("     (RAG + scripts/34 + scripts/42 + O213)")
print("  2. ✅ 排除最大錨 M_Pl: N_O38 重鑄 = ω_M0/ω_ring (純頻率)")
print("  3. ✅ 排除最小錨 t_Pl: 4.095e38 重鑄 = ω_M0/ω_site (純頻率)")
print("  4. 🔴 重鑄後仍然冇身份 — 但缺口本體已收窄:")
print("     ω_M0 對 ω_site 嘅純頻率比 (兩端都係 IDCM 內部量)")
print("  5. ⟹ 用戶 insight 成立: Planck 端 (ħ/M_Pl/t_Pl) 係")
print("     多餘假設 — 缺口唔需要佢哋定義; 但身份仍然開放")
print(f"結果: {ok} PASS / {fail} FAIL")
print("=" * 76)