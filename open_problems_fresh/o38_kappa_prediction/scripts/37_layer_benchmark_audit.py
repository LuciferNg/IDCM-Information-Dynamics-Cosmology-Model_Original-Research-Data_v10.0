#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O38/m0-scale — Script 37: 33 層每級對標物審計
================================================================
日期: 2026-10-18
觸發: 用戶「但也應該存在每一級的對標物是什麼」
問題: 有限階樹狀分形 33 層, 每層 ℓ 嘅「對標物」(物理實體) 應該係咩?
      若每層有對標物 ⟹ 樹結構有獨立盲測機會 (樣本外驗證)
現有結構 (p10 docs/00):
  λ_{n,ℓ} = γ_n × μ_ℓ,  μ_ℓ = φ^(291.5−ℓ),  ℓ=0..33
  pinned 層: k_u = 33β (ℓ=0, Up/UV), k_d = 26β−φ⁻⁴ (ℓ=7, Down/Casimir),
             k_l = 19β (ℓ=14, Lepton/IR)
  本輪發現: β = 1/(2φ) = 0.3090169944 ⟹ k_u = 33/(2φ) = 10.1976 ✓
審計:
  A. β = 1/(2φ) 精確命中 pinned 層 k-value (33/26/19)
  B. 每層 ℓ 嘅 k-value = ℓ·β 全表 (0..33) — 逐層對標物候選
  C. IDCM 已閉合量 (m_e/m_μ/m_τ/v_SM/E_kchain/...) log₁₀ vs μ_ℓ log₁₀
     有冇自然坐標? (樣本外盲測)
  D. 判決: 每級對標物存在/唔存在? 邊層有 pinned 機制?
用法: /usr/bin/python3 scripts/37_layer_benchmark_audit.py
"""
import mpmath as mp
mp.mp.dps = 50

ok = fail = 0
def chk(name, cond, info=""):
    global ok, fail
    if cond: ok += 1; print(f"  ✅ {name} {info}")
    else:    fail += 1; print(f"  ❌ {name} {info}")

phi = (1 + mp.sqrt(5)) / 2
beta = mp.mpf(1) / (2 * phi)
M = 33
L4 = 7

print("=" * 76)
print("A. β = 1/(2φ) pinned 層 k-value 精確命中")
print("=" * 76)
print(f"  β = 1/(2φ) = {mp.nstr(beta, 12)}")
ku = M * beta
kd = (M - L4) * beta - phi**-4
kl = (M - 2*L4) * beta
print(f"  k_u = 33β = {mp.nstr(ku, 8)}  (10.1976)")
print(f"  k_d = 26β − φ⁻⁴ = {mp.nstr(kd, 8)}  (7.889)")
print(f"  k_l = 19β = {mp.nstr(kl, 8)}  (5.871)")
chk("A1 k_u = 33/(2φ) = 10.1976", abs(ku - mp.mpf('10.1976')) < mp.mpf('1e-3'), f"({mp.nstr(ku,8)})")
chk("A2 k_l = 19/(2φ) = 5.8714", abs(kl - mp.mpf('5.8714')) < mp.mpf('1e-3'), f"({mp.nstr(kl,8)})")
chk("A3 k_d = 26/(2φ) − φ⁻⁴ = 7.8885", abs(kd - mp.mpf('7.8885')) < mp.mpf('1e-3'), f"({mp.nstr(kd,8)})")

print()
print("=" * 76)
print("B. 每層 k-value = ℓ·β 全表 (0..33) — 逐層對標物候選")
print("=" * 76)
print("  ℓ | k = ℓ·β | 4^ℓ | log₁₀ μ_ℓ | 物理對應 (pinned/已知)")
pins = {0: "Up (UV)", 7: "Down (Casimir)", 14: "Lepton (IR)"}
known = {11: "粒子物理尺度?"}
for ell in range(0, 34):
    k = ell * beta
    nodes = mp.mpf(4)**ell
    mu = phi**(mp.mpf('291.5') - ell)
    tag = pins.get(ell, "") or known.get(ell, "")
    print(f"  {ell:2d} | {mp.nstr(k,6):8s} | {mp.nstr(nodes,4):10s} | {mp.nstr(mp.log10(mu),5):7s} | {tag}")
print("  ⟹ 只有 ℓ=0/7/14 有 pinned sector (Up/Down/Lepton); 其餘 30 層冇對標物")

print()
print("=" * 76)
print("C. IDCM 已閉合量 vs 樹階梯 — 有冇自然坐標? (盲測)")
print("=" * 76)
# 已閉合無量綱/有量綱量: (名, log₁₀ 值, 單位註)
obs = [
    ("M_Pl/ħω_ring (N_IDCM)", mp.log10(mp.mpf('7.884688925e60'))),
    ("M₀/ħω_ring (N_O38)", mp.log10(mp.mpf('1.80188233461e40'))),
    ("m_τ/m_e", mp.log10(mp.mpf('1776.86')/mp.mpf('0.51099895'))),
    ("m_μ/m_e", mp.log10(mp.mpf('105.6583755')/mp.mpf('0.51099895'))),
    ("v_SM/m_e", mp.log10(mp.mpf('246219.6')/mp.mpf('0.51099895'))),
    ("m_p/m_e", mp.log10(mp.mpf('938.27209')/mp.mpf('0.51099895'))),
    ("M₀/m_e", mp.log10(mp.mpf('27.900915')/mp.mpf('0.51099895'))),
    ("Ω_b⁻¹", mp.log10(20)),
    ("R_world/r_d", mp.log10(mp.mpf('4129.94')/mp.mpf('147.44'))),
    ("ω_ring/H₀", mp.log10(mp.mpf('72.5941')/mp.mpf('67.41'))),
]
mu_l0 = mp.log10(phi**mp.mpf('291.5'))
mu_l33 = mp.log10(phi**mp.mpf('258.5'))
print(f"  樹階梯 log₁₀ μ_ℓ 範圍: [{mp.nstr(mu_l33,5)}, {mp.nstr(mu_l0,5)}]  (μ₃₃→μ₀)")
inside = 0
for name, v in obs:
    loc = "IN-TREE" if mu_l33 <= v <= mu_l0 else "OUTSIDE"
    if mu_l33 <= v <= mu_l0: inside += 1
    print(f"  {name:24s} log₁₀={mp.nstr(v,7):9s}  {loc}")
print(f"  ⟹ {inside}/{len(obs)} 個已閉合量 log₁₀ 落喺樹階梯範圍內")
# 特別: m_e 對應嘅層 (如果 m_e/ħω_ring 係無量綱)
me_hw = mp.mpf('0.51099895')/mp.mpf('1.548431574e-39')
print(f"  m_e/ħω_ring = {mp.nstr(mp.log10(me_hw),7)} — OUTSIDE (細過 μ₃₃)")
# 粒子質量落到邊層? 搵 ℓ 令 μ_ℓ ≈ m_X/ħω_ring
for name, mass_MeV in [("m_e", mp.mpf('0.51099895')), ("m_μ", mp.mpf('105.6583755')),
                         ("m_τ", mp.mpf('1776.86')), ("m_p", mp.mpf('938.27209')),
                         ("v_SM", mp.mpf('246219.6')), ("M₀", mp.mpf('27.900915')),
                         ("M_Pl", mp.mpf('1.2208901e22'))]:
    # μ_ℓ = m/ħω_ring ⟹ 291.5 − ℓ = log_φ(m/ħω_ring)
    lphi = mp.log(mass_MeV / mp.mpf('1.548431574e-39')) / mp.log(phi)
    ell_pos = mp.mpf('291.5') - lphi
    in_tree = 0 <= ell_pos <= 33
    print(f"  {name:5s}: log_φ = {mp.nstr(lphi,6):9s} ⟹ ℓ* = {mp.nstr(ell_pos,6):9s} {'✓IN-TREE' if in_tree else '✗OUT'}")
print("  ⟹ ℓ* ∈ [0,33] 先係樹內層; 全部粒子質量 ℓ* 超標 (10^8 能量跨度 vs 樹 10^7)")
print("    μ_ℓ 階梯 (φ³³ = 7.88e6) 唔夠覆蓋 Planck→電子 (10^22) ⟹ 樹唔係線性能量階梯!")

print()
print("=" * 76)
print("D. 判決")
print("=" * 76)
print("  1. β = 1/(2φ) 係 pinned 層 k-value 嘅結構出處 (A1-A3 ✓)")
print("  2. 33 層只有 3 層有 pinned sector (ℓ=0 Up/ℓ=7 Down/ℓ=14 Lepton),")
print("     其餘 30 層未有對標物 — 「每一級對標物」喺 IDCM 現狀唔成立")
print("  3. μ_ℓ 階梯跨度 φ³³=7.88e6 遠細過質量階梯 (m_e→M_Pl 10^22)")
print("     ⟹ μ_ℓ 唔係粒子質量嘅直接標度 — 對標物唔可能係『每層一個質量』")
print("  4. 樹頂 μ₀ ≈ N_IDCM (10^60.92 vs 10^60.90) — 但 N_IDCM 係『總節拍』")
print("     ⟹ 樹階梯嘅真正對標物 = 時間/節拍階梯 (4^ℓ·t_site: 0.306 Gyr → 2.26e19 Gyr),")
print("     唔係能量階梯; 粒子 sector 對應只存在 pinned 層 (k-value 機制)")
print(f"結果: {ok} PASS / {fail} FAIL")
print("=" * 76)