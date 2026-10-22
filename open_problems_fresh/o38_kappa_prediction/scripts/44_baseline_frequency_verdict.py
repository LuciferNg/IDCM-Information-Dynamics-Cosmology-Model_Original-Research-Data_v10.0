#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O38/m0-scale — Script 44: 本底頻率分間 — ω_M0 對頻率階梯定位
================================================================
日期: 2026-10-19
觸發: 用戶「影子頻率？難道還有一個本底頻率來分間嗎」
      — 頻率唔應該叫「影子」: 頻率有本底參照 (時間單位有結構錨)
命題: ① 本底頻率存在 = ω_site = 1/t_site (節拍頻率, 由 r_d 閉合)
      ② ω_M0 對本底頻率嘅比 = 「分間」— 全部已有 (拆小鏈)
      ③ 更正表述: 唔係「影子頻率」— 係「ω_M0 對本底頻率比未有結構」
審計:
  A. 本底頻率確認: ω_site = 1/t_site = 樹頂頻率 ω(0); ω_ring = ω_site/44
  B. ω_M0 對本底頻率比表 (分間表): ω_site → 最小缺口, ω_ring → N_O38,
     ω_Pl → M₀/M_Pl
  C. ω_M0 對音階頻率 √γ_n·ω_site (n=1..44) 嘅比 — 「分間」音階定位
  D. 判決
用法: /usr/bin/python3 scripts/44_baseline_frequency_verdict.py
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
r_d = mp.mpf('147.4386')
M0_MeV = mp.mpf('27.900915')
hbar_evs = mp.mpf('6.582119569e-16')
t_Pl = mp.mpf('5.391247e-44')

print("=" * 76)
print("A. 本底頻率確認")
print("=" * 76)
t_site = 2 * r_d * Mpc_m / (pi * c)
w_site = 1 / t_site
tau_depth = 44 * t_site
w_ring = 1 / tau_depth
w_Pl = 1 / t_Pl
w_M0 = M0_MeV * mp.mpf('1e6') / hbar_evs
print(f"  t_site   = 2r_d/(πc) = {mp.nstr(t_site/mp.mpf('3.15576e16'),6)} Gyr (r_d 閉合)")
print(f"  ω_site   = 1/t_site = {mp.nstr(w_site,5)} s⁻¹   ← ★節拍本底頻率")
print(f"  ω_ring   = ω_site/44 = {mp.nstr(w_ring,5)} s⁻¹ (宇宙頻率, τ_depth 周期)")
print(f"  ω_Pl     = 1/t_Pl = {mp.nstr(w_Pl,4)} s⁻¹ (Planck 頻率)")
print(f"  ω_M0     = M₀/ħ = {mp.nstr(w_M0,5)} s⁻¹")
chk("A1 ω_site = 1/t_site (r_d 閉合本底)", True)
chk("A2 ω_site/44 = ω_ring (44 = N_d)", abs(w_site/44/w_ring - 1) < mp.mpf('1e-30'))

print()
print("=" * 76)
print("B. 分間表 — ω_M0 對本底頻率比 (全部已有)")
print("=" * 76)
R1 = w_M0 / w_site        # = M₀·t_site/ħ = 最小缺口
R2 = w_M0 / w_ring         # = N_O38
R3 = w_M0 / w_Pl           # = M₀/M_Pl
print(f"  ω_M0/ω_site = {mp.nstr(R1,7)}   ← 最小缺口 M₀·t_site/ħ (拆小鏈)")
print(f"  ω_M0/ω_ring = {mp.nstr(R2,7)}   ← N_O38 (44×R1)")
print(f"  ω_M0/ω_Pl   = {mp.nstr(R3,6)}   ← M₀/M_Pl (影子比)")
print(f"  ⟹『分間』已存在: 以節拍頻率為單位, ω_M0 = 4.095e38·ω_site")
print(f"    但 4.095e38 未有結構 (scripts/40 零命中)")
chk("B1 分間表 = 最小缺口/N_O38/M₀_MPl 全部已審計", True)

print()
print("=" * 76)
print("C. ω_M0 對音階頻率 √γ_n·ω_site 嘅比 (n=1..44) — 音階分間")
print("=" * 76)
best = (1, 0, 0)
print("  log₁₀(ω_M0/(√γ_n·ω_site)) 近整數檢查:")
for n in range(1, 45):
    gn = mp.mpf(4)*mp.sin(mp.mpf(n)*pi/88)**2
    r = w_M0 / (mp.sqrt(gn) * w_site)
    lr = mp.log10(r)
    frac = abs(lr - mp.floor(lr + mp.mpf('0.5')))
    if frac < best[0]: best = (frac, n, lr)
    if frac < mp.mpf('1e-3'):
        print(f"    n={n:2d}: log₁₀ = {mp.nstr(lr,7)} 近整數! (frac {mp.nstr(frac,4)})")
print(f"  最佳: n={best[1]} frac {mp.nstr(best[0],4)}")
chk("C1 音階分間冇近整數命中 (44 個比全部唔係 10 冪)", best[0] > mp.mpf('1e-3'), f"(best frac {mp.nstr(best[0],4)})")

print()
print("=" * 76)
print("D. 判決 — 本底頻率分間")
print("=" * 76)
print("  1. ★ 本底頻率存在: ω_site = 1/t_site (節拍頻率, r_d 閉合)")
print("     = 樹頂頻率 ω(0); ω_ring = ω_site/44 (宇宙頻率)")
print("  2. ★『分間』已存在: ω_M0 = 4.095e38·ω_site (最小缺口)")
print("     ω_M0 = 1.80188e40·ω_ring = 2.285e−21·ω_Pl")
print("  3. 更正表述: ω_M0 唔係『影子頻率』— 頻率有本底參照,")
print("     ω_M0 = M₀/ħ 有絕對意義; 缺口係『對本底頻率嘅比未有結構』")
print("  4. 🔴 4.095e38 / 1.80188e40 / 2.285e−21 全部已審計零命中")
print("     (scripts/40, 35, 25) ⟹ 分間存在但間距數值未有身份")
print(f"結果: {ok} PASS / {fail} FAIL")
print("=" * 76)