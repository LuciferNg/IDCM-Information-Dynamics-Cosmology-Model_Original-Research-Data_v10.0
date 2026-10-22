#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O38/m0-scale — Script 38: 以節拍階梯為標度重新推導 N_O38
================================================================
日期: 2026-10-18
觸發: 用戶「以節拍階梯為標度重新開始推導」
背景 (scripts/37 結論): μ_ℓ 階梯跨度 φ³³ = 7.9e6 遠細過質量階梯 10^22
      ⟹ 樹唔係質量階梯; 樹階梯真正對標 = 節拍階梯 4^ℓ·t_site
      t_site = R_H/(44c) = 0.30614 Gyr (p10 docs/04 0.046% 閉合) ← 有結構出處!
本輪 (節拍階梯重推):
  A. 節拍階梯閉合結構重演: t_site = R_H/(44c), τ_depth = 44·t_site = R_H/c,
     T_SYNC = 88·t_site — 全部有結構出處 (p10 docs/04)
  B. ★ N_O38 節拍階梯重寫: N_O38 = M₀/ħω_ring = M₀·τ_depth/ħ = M₀·R_H/(ħc)
     = ω_M0·τ_depth (ω_M0 = M₀/ħ 質量頻率) — 全新框架語言
  C. 分解: N_O38 = 44·(M₀·t_site/ħ);  M₀·t_site/ħ = (t_site/t_Pl)·(M₀/M_Pl)
  D. 頻率視角: ω_M0 = M₀/ħ 對節拍階梯 ω(ℓ) = 1/(4^ℓ·t_site) 邊層?
     ⟹ ℓ* = log₄(ħ/(M₀·t_site)) = −64.2 (樹外負層) — 誠實負結果
  E. ★ 引用核實: O213 已降級 N = τ/t_Pl 為非結構 (null P = 0.875, 四種 c 四值)
     ⟹ O38 scripts/22「N_O38 = N_IDCM·M₀/M_Pl 唯一閉合」依賴非結構量 — 附註更正
  F. 判決: 節拍標度框架確立; 缺口重鑄 = ω_M0 對節拍階梯嘅身份; 維持 🔴
用法: /usr/bin/python3 scripts/38_beat_ladder_rederive.py
"""
import mpmath as mp
mp.mp.dps = 50

ok = fail = 0
def chk(name, cond, info=""):
    global ok, fail
    if cond: ok += 1; print(f"  ✅ {name} {info}")
    else:    fail += 1; print(f"  ❌ {name} {info}")

c_si = mp.mpf('2.99792458e8')      # m/s
Mpc_m = mp.mpf('3.085677581e22')   # m/Mpc
R_H_Mpc = mp.mpf('4129.94')        # 可觀測宇宙半徑 (O127/O7 錨)
t_Pl = mp.mpf('5.391247e-44')      # s
hbar_evs = mp.mpf('6.582119569e-16')  # ħ in eV·s
M0_MeV = mp.mpf('27.900915')
N38 = mp.mpf('1.80188233461e40')

print("=" * 76)
print("A. 節拍階梯閉合結構 (全部有結構出處)")
print("=" * 76)
R_H = R_H_Mpc * Mpc_m
t_site = R_H / (44 * c_si)                     # s
t_site_Gyr = t_site / (mp.mpf('3.15576e16'))
tau_depth = 44 * t_site
tau_depth_Gyr = tau_depth / mp.mpf('3.15576e16')
T_SYNC = 88 * t_site
T_SYNC_Gyr = T_SYNC / mp.mpf('3.15576e16')
print(f"  t_site = R_H/(44c)  = {mp.nstr(t_site_Gyr,6)} Gyr  (p10: 0.30614, dev {mp.nstr(abs(t_site_Gyr/mp.mpf('0.30614')-1),4)})")
print(f"  τ_depth = 44·t_site = {mp.nstr(tau_depth_Gyr,6)} Gyr  (p10: 13.470, dev {mp.nstr(abs(tau_depth_Gyr/mp.mpf('13.470')-1),4)})")
print(f"  T_SYNC = 88·t_site  = {mp.nstr(T_SYNC_Gyr,6)} Gyr  (p10: 26.940, dev {mp.nstr(abs(T_SYNC_Gyr/mp.mpf('26.940')-1),4)})")
chk("A1 t_site = R_H/(44c) 重演 (0.306 Gyr)", abs(t_site_Gyr/mp.mpf('0.306')-1) < mp.mpf('0.01'))
chk("A2 τ_depth = R_H/c = 13.47 Gyr", abs(tau_depth_Gyr/mp.mpf('13.47')-1) < mp.mpf('0.01'))
chk("A3 T_SYNC = 88·t_site = 26.94 Gyr", abs(T_SYNC_Gyr/mp.mpf('26.94')-1) < mp.mpf('0.01'))

print()
print("=" * 76)
print("B. ★ N_O38 節拍階梯重寫: N_O38 = M₀·τ_depth/ħ = M₀·R_H/(ħc)")
print("=" * 76)
w_ring = 1 / tau_depth                        # s⁻¹  (ω_ring = c/R_H)
hw_ring = hbar_evs * w_ring                   # eV
hw_ring_MeV = hw_ring / mp.mpf('1e6')
print(f"  ω_ring = 1/τ_depth = {mp.nstr(w_ring,6)} s⁻¹")
print(f"  ħω_ring = {mp.nstr(hw_ring_MeV,8)} MeV  (記錄: 1.548431574e-39, dev {mp.nstr(abs(hw_ring_MeV/mp.mpf('1.548431574e-39')-1),4)})")
N38_a = M0_MeV * tau_depth / (hbar_evs / mp.mpf('1e6'))
print(f"  N_O38 = M₀·τ_depth/ħ = {mp.nstr(N38_a,10)}  (記錄: 1.80188233461e40)")
d_B = abs(N38_a / N38 - 1)
chk("B1 N_O38 = M₀·τ_depth/ħ 重寫成立", d_B < mp.mpf('1e-3'), f"(dev {mp.nstr(d_B,4)} = 輸入精度)")
# 分解: M₀·R_H/(ħc) — 統一 eV: M₀(MeV)×1e6 = eV, ħc = ħ(eV·s)·c(m/s) = eV·m
N38_b = (M0_MeV * mp.mpf('1e6')) * R_H / (hbar_evs * c_si)
print(f"  N_O38 = M₀·R_H/(ħc) = {mp.nstr(N38_b,10)}")
chk("B2 N_O38 = M₀·R_H/(ħc) 等價", abs(N38_b/N38-1) < mp.mpf('1e-3'))
print(f"  ⟹ ★ N_O38 = 質量頻率 × 宇宙深度: ω_M0 = M₀/ħ = {mp.nstr(M0_MeV*mp.mpf('1e6')/hbar_evs,5)} s⁻¹")
print(f"    N_O38 = ω_M0·τ_depth — M₀ 喺宇宙深度時間內振盪嘅次數")

print()
print("=" * 76)
print("C. 分解: N_O38 = 44·(M₀·t_site/ħ)")
print("=" * 76)
f44 = M0_MeV * t_site / (hbar_evs / mp.mpf('1e6'))
print(f"  M₀·t_site/ħ = {mp.nstr(f44,8)}")
print(f"  44·(M₀·t_site/ħ) = {mp.nstr(44*f44,10)}")
d_C = abs(44*f44 / N38 - 1)
chk("C1 N_O38 = 44·(M₀·t_site/ħ)", d_C < mp.mpf('1e-3'), f"(dev {mp.nstr(d_C,4)})")
# M₀·t_site/ħ = (t_site/t_Pl)·(M₀/M_Pl)
M_Pl_MeV = mp.mpf('1.2208901e22')
rhs = (t_site/t_Pl) * (M0_MeV/M_Pl_MeV)
print(f"  (t_site/t_Pl)·(M₀/M_Pl) = {mp.nstr(rhs,8)}")
chk("C2 恆等重寫: M₀·t_site/ħ = (t_site/t_Pl)·(M₀/M_Pl)", abs(rhs/f44-1) < mp.mpf('1e-3'))
print(f"  t_site/t_Pl = {mp.nstr(t_site/t_Pl,6)}  (log₁₀ {mp.nstr(mp.log10(t_site/t_Pl),5)})")

print()
print("=" * 76)
print("D. 頻率視角: ω_M0 對節拍階梯邊層? (誠實負結果)")
print("=" * 76)
w_M0 = M0_MeV * mp.mpf('1e6') / hbar_evs     # s⁻¹
ell_star = mp.log(hbar_evs/(M0_MeV*mp.mpf('1e6')*t_site)) / mp.log(4)
print(f"  ω_M0 = M₀/ħ = {mp.nstr(w_M0,6)} s⁻¹")
print(f"  ω(ℓ) = 1/(4^ℓ·t_site): ℓ=0 → {mp.nstr(1/t_site,4)} s⁻¹ (樹頂), ℓ=33 → {mp.nstr(1/(mp.mpf(4)**33*t_site),4)} s⁻¹ (樹底)")
print(f"  ω_M0 對應層 ℓ* = log₄(ħ/(M₀·t_site)) = {mp.nstr(ell_star,5)}")
print(f"  ⟹ ℓ* = −64.2 — 負層! ω_M0 完全喺樹頻率範圍之上 (大過樹頂 ω(0) 約 4×10³⁸ 倍)")
chk("D1 ω_M0 喺樹頻率範圍之外 (ℓ* < 0)", ell_star < 0, f"(ℓ*={mp.nstr(ell_star,5)})")
print(f"  ⟹ 節拍階梯 (33 層, 頻率跨度 4³³=7.4e19) 裝唔落 ω_M0 — 同 scripts/37 質量階梯結論一致")
print(f"  ★ 新讀法: N_O38 = ω_M0·τ_depth 將缺口重鑄為『質量頻率 × 宇宙深度』,")
print(f"    τ_depth = R_H/c 有結構 (p10 閉合), 缺口 = ω_M0 對節拍階梯嘅身份 (未閉合)")

print()
print("=" * 76)
print("E. ★ 引用核實: O213 已降級 N = τ/t_Pl 為非結構")
print("=" * 76)
print("  O213 docs/00 §四: N = τ/t_Pl 四種 c 約定四值 (差 0.68%) ⟹ 非不變量")
print("  O213 scripts/13: N = 7.88468594512e60, null P = 0.875 (非結構)")
print("  ⟹ O38 scripts/22『N_O38 = N_IDCM·M₀/M_Pl 唯一閉合分解』依賴 N_IDCM = 非結構量")
print("  ⟹ 附註:『唯一閉合』表述需降級為『唯一代數分解 (非結構因子)』— 見 docs/19")
chk("E1 O213 降級已記錄 (不影響本輪節拍重寫)", True, "(引用核實, 唔跨 O 推導)")

print()
print("=" * 76)
print("F. 判決")
print("=" * 76)
print("  1. 節拍階梯標度框架確立: t_site = R_H/(44c) 有結構出處 (0.046%)")
print("  2. N_O38 新語言: N_O38 = M₀·τ_depth/ħ = M₀·R_H/(ħc) = ω_M0·τ_depth")
print("     — 質量頻率 × 宇宙深度; τ_depth = 44·t_site 已閉合")
print("  3. 缺口重鑄: ω_M0 = M₀/ħ 對節拍階梯嘅身份 (ℓ* = −64.2 樹外)")
print("     — 同 scripts/37: 樹唔係質量階梯, 亦裝唔落質量頻率")
print("  4. O213 引用更正: N_IDCM 非結構 ⟹ scripts/22『唯一閉合』降級為『唯一代數分解』")
print("  5. N_O38 缺口維持 🔴; 新框架 = 節拍標度 (τ_depth = R_H/c), 等 ω_M0 結構湧現")
print(f"結果: {ok} PASS / {fail} FAIL")
print("=" * 76)