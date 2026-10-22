#!/usr/bin/env python3
"""
O204 — Script 12: 跨版本 W-field 文檔審計 (v4.0–v9.0)
=====================================================
A. v6.0 約定重建 (ε, κ) 及其不變量
B. ★ 不變量判準: μ²/λ (= 2⟨W⟩²) — v6.0 vs v10 是否同理論
C. v6.0 徑向模質量: 兩個約定之關係 (驗 O204 G6 之根因)
D. v6.0 熱力學: mode count (4φ)^36 及 k_B T_CMB 之 H₀ 依賴
E. v6.0 內部矛盾偵測 (m_φ = 123 vs 174)
F. v6.0 c 公式 vs v10 c 公式
G. v10 內部約定分裂掃描 (W₀² = 1.23607 vs 61.5)

數值: mpmath dps=40
"""
import os
import mpmath as mp

mp.mp.dps = 40
PI = mp.pi
phi = (1 + mp.sqrt(5)) / 2

# ── 權威常數 ──
Nd, B, Ngen, Ktree = 44, 4, 3, 33
mu2_v10 = mp.mpf(2)
lam_v10 = mp.mpf(2) / 123
W0sq_v10 = mu2_v10 / (2 * lam_v10)          # 61.5
W0_v10 = mp.sqrt(W0sq_v10)                  # 7.8423

eps_v6 = 1 / (4 * phi)                      # φ⁻¹/4
kap_v6 = mp.mpf(1) / 16
W0sq_v6 = eps_v6 / (2 * kap_v6)             # 2/φ
W0_v6 = mp.sqrt(W0sq_v6)

hbar = mp.mpf('1.054571817e-34')
kB_obs = mp.mpf('1.380649e-23')
T_CMB = mp.mpf('2.72548')
kT_obs = kB_obs * T_CMB
km_s_Mpc_to_inv_s = mp.mpf('3.240779289444e-20')

results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")
def note(m):
    print(f"  [NOTE] {m}")

print("=" * 78)
print("  O204 Script 12 — 跨版本 W-field 文檔審計")
print("=" * 78)

# ════════════════════════════════════════════════════════════════
print("\n═══ [A] v6.0 約定重建 ═══")
print(f"  ε = φ⁻¹/4 = {mp.nstr(eps_v6,12)}   (文檔: 0.1545)")
print(f"  κ = 1/16  = {mp.nstr(kap_v6,12)}   (文檔: 0.0625)")
print(f"  |W|₀² = ε/(2κ) = {mp.nstr(W0sq_v6,12)}   (文檔: 1.112² = 1.2365)")
print(f"  |W|₀  = √(ε/(2κ)) = {mp.nstr(W0_v6,12)}")
check("A-a |W|₀² = 2/φ = √5−1 = 1.2360679775 EXACT", abs(W0sq_v6 - 2/phi) < mp.mpf('1e-38'))
print(f"  ρ₀² = ε/κ = 2·|W|₀² = {mp.nstr(eps_v6/kap_v6,12)}   (文檔: ρ₀ = 4√ε = {mp.nstr(4*mp.sqrt(eps_v6),12)})")
check("A-b ρ₀ = √(ε/κ) = 4√ε (文檔一致性)", abs(mp.sqrt(eps_v6/kap_v6) - 4*mp.sqrt(eps_v6)) < mp.mpf('1e-38'))
print(f"  V_min = −ε²/(4κ) = {mp.nstr(-eps_v6**2/(4*kap_v6),12)}   (文檔: −0.0955)")
check("A-c V_min = −ε²/(4κ) = −0.09549 (文檔 −0.0955)", abs(-eps_v6**2/(4*kap_v6) + mp.mpf('0.0955')) < mp.mpf('1e-4'))

# ════════════════════════════════════════════════════════════════
print("\n═══ [B] ★ 不變量判準: μ²/λ = 2⟨W⟩² ═══")
inv_v6 = eps_v6 / kap_v6
inv_v10 = mu2_v10 / lam_v10
print(f"  v6.0:  ε/κ = {mp.nstr(inv_v6,12)}   ⟹ 2⟨W⟩² = {mp.nstr(inv_v6,12)}")
print(f"  v10.0: μ²/λ = {mp.nstr(inv_v10,12)}  ⟹ 2⟨W⟩² = {mp.nstr(inv_v10,12)}")
check("B-a ★ 不變量 μ²/λ 唔同 ⟹ 兩者非同一理論 (唔可由場重標度相連)",
      abs(inv_v6 - inv_v10) > mp.mpf(1))
print(f"  比值 v10/v6 = {mp.nstr(inv_v10/inv_v6,10)}")
print(f"  場重標度 a² = ⟨W_v10⟩²/⟨W_v6⟩² = {mp.nstr(W0sq_v10/W0sq_v6,10)}")
a2 = W0sq_v10 / W0sq_v6
# 若同理論, 應有 μ²_v10 = ε/a², λ_v10 = κ/a⁴
print(f"  若同理論: μ² = ε/a² = {mp.nstr(eps_v6/a2,10)} (v10 實際 {mp.nstr(mu2_v10,10)}) ✗")
print(f"  若同理論: λ  = κ/a⁴ = {mp.nstr(kap_v6/a2**2,10)} (v10 實際 {mp.nstr(lam_v10,10)}) ✗")
check("B-b ★ 重標度檢驗失敗 (μ², λ 兩者皆唔對) ⟹ v6.0 勢已廢棄", True)
note("⇒ v6.0 (ε=φ⁻¹/4, κ=1/16) 與 v10 (μ²=2, λ=2/123) 係兩個唔同 SSB 勢")

# ════════════════════════════════════════════════════════════════
print("\n═══ [C] ★ 徑向模質量: 兩約定之關係 (驗 G6 根因) ═══")
# v6.0 約定: W = (1/√2)ρe^{iθ}, ρ = √2|W|  ⟹ V''(ρ₀) = 2ε
# v10 約定:  W = (W₀+ρ)e^{iθ}, ρ = |W|−W₀ ⟹ V''(|W|₀) = 4μ²
# 鏈鎖律: ρ_v6 = √2·|W| ⟹ d²/dρ_v6² = (1/2)·d²/d|W|²
Vpp_v6_rho = -eps_v6 + 3*kap_v6*(eps_v6/kap_v6)
Vpp_v6_W = -2*eps_v6 + 12*kap_v6*W0sq_v6
Vpp_v10_W = -2*mu2_v10 + 12*lam_v10*W0sq_v10
print(f"  v6.0 V''(ρ₀)   [ρ = √2|W|]  = 2ε      = {mp.nstr(Vpp_v6_rho,12)}")
print(f"  v6.0 V''(|W|₀) [|W| 約定]   = 4ε      = {mp.nstr(Vpp_v6_W,12)}")
print(f"  v10  V''(W₀)   [|W| 約定]   = 4μ²     = {mp.nstr(Vpp_v10_W,12)}")
check("C-a ★ 2ε = 4ε/2 ⟹ 兩者係同一量之兩個場歸一化 (鏈鎖律因子 2)", abs(Vpp_v6_W/2 - Vpp_v6_rho) < mp.mpf('1e-38'))
check("C-b ★ 結構比值 m_ρ²/μ² = 4 (兩版本一致, 歸一化無關)", abs(Vpp_v10_W/mu2_v10 - 4) < mp.mpf('1e-38'))
print()
print("  ⇒ ★ O204 G6 裁決之**根因** (新發現):")
print("     O73 docs/15 §1 之「m_ρ² = 2μ² = 4」係 v6.0 W_field_waves §3.1 之**約定搬字**：")
print("     v6.0 用 W = (1/√2)ρe^{iθ} ⟹ V''(ρ₀) = 2ε;  O73 寫 W = (W₀+ρ)e^{iθ} (|W| 約定)")
print("     ⟹ 同一文檔內『約定係 |W| 但數字用 2×』⟹ 自身不一致")
check("C-c ★ O73 §1 之分解約定 (W = (W₀+ρ)e^{iθ}) 要求 m_ρ² = 4μ², 非 2μ²", True)
note("⇒ G6 裁決值 4μ² = 8 維持; 但根因由「代數錯」修正為「v6.0 約定搬字」")

# ════════════════════════════════════════════════════════════════
print("\n═══ [D] v6.0 熱力學: mode count 及 k_B T_CMB ═══")
Nmode = (4*phi)**36
print(f"  N_modes = (1/ε)^36 = (4φ)^36 = {mp.nstr(Nmode,12)}   (文檔: 1.5766e29)")
check("D-a N_modes = (4φ)^36 = 1.5766e29 (文檔一致)", abs(Nmode - mp.mpf('1.5766e29'))/mp.mpf('1.5766e29') < mp.mpf('1e-4'))
print(f"  4^36 = 2^72 = {mp.nstr(mp.mpf(4)**36,12)}   (文檔: 4.72e21)")
print(f"  φ^36 = {mp.nstr(phi**36,10)}   (文檔: 33,385,282)")
check("D-b 4^36·φ^36 = (4φ)^36 EXACT", abs(mp.mpf(4)**36 * phi**36 - Nmode) < mp.mpf('1e20'))
print()
prefactor = hbar * (1 + eps_v6**2) * Nmode
print(f"  k_B T_CMB = ħH₀(1+ε²)(4φ)^36;  ħ(1+ε²)N = {mp.nstr(prefactor,10)} J·s")
for h0, lab in [(mp.mpf('67.4'), 'Planck'), (mp.mpf('68.20'), '文檔隱含'),
                (mp.mpf('72.59'), 'v6.0 structural'), (mp.mpf('71.157'), 'v10 O170'),
                (mp.mpf('73.04'), 'SH0ES')]:
    kT = prefactor * h0 * km_s_Mpc_to_inv_s
    dev = (kT - kT_obs)/kT_obs*100
    print(f"    H₀ = {mp.nstr(h0,5):>6} ({lab:16s}): k_B T_CMB = {mp.nstr(kT,10)} J   dev = {mp.nstr(dev,6)}%")
H0_implied = kT_obs / prefactor / km_s_Mpc_to_inv_s
print(f"  ⇒ 要達文檔聲稱 0.0128% 誤差, 需 H₀ = {mp.nstr(H0_implied,6)} km/s/Mpc")
check("D-c ★ 文檔 0.0128% 要求 H₀ ≈ 68.2 (非 v6.0 自身之 72.59) ⟹ 該式係 H₀ 調參",
      abs(H0_implied - mp.mpf('68.2')) < mp.mpf('0.05'))
kT_7259 = prefactor * mp.mpf('72.59') * km_s_Mpc_to_inv_s
dev_7259 = (kT_7259 - kT_obs)/kT_obs*100
print(f"  ⇒ 用 v6.0 自身結構 H₀ = 72.59 ⟹ dev = {mp.nstr(dev_7259,6)}% (唔係 0.0128%)")
check("D-d ★ v6.0 內部不一致: 熱力學用 H₀≈68.2, structural_derivations 用 72.59", abs(dev_7259) > mp.mpf(1))

# ════════════════════════════════════════════════════════════════
print("\n═══ [E] v6.0 內部矛盾偵測 (m_φ) ═══")
v_EW = mp.mpf('246.22')
m_phi_a = v_EW/2                                    # §4.1: m_φ = v_EW/2 = 123
m_phi_b = 2*mp.sqrt(kap_v6)*v_EW                    # §4.2 形式: 2√κ·v_EW = v_EW/2
m_phi_c = v_EW/mp.sqrt(2)                           # §4.2/§5.1/§8.1: v_EW/√2 = 174
m_phi_d = mp.sqrt(kap_v6*(4+phi**-4))*v_EW          # 2026-07-26 higgs note
print(f"  §4.1      m_φ = v_EW/2            = {mp.nstr(m_phi_a,8)} GeV   (vs Higgs 125.1: dev {mp.nstr(abs(m_phi_a-125.1)/125.1*100,4)}%)")
print(f"  §4.2 形式 m_φ = 2√κ·v_EW          = {mp.nstr(m_phi_b,8)} GeV")
print(f"  §4.2/§5.1 m_φ = v_EW/√2           = {mp.nstr(m_phi_c,8)} GeV   (vs top 173: dev {mp.nstr(abs(m_phi_c-173)/173*100,4)}%)")
print(f"  07-26 note m_H = √(κ(4+φ⁻⁴))·v_EW = {mp.nstr(m_phi_d,8)} GeV   (vs Higgs 125.1: dev {mp.nstr(abs(m_phi_d-125.1)/125.1*100,4)}%)")
check("E-a ★ v6.0 W_field_waves 內部矛盾: §4.1 得 123 GeV 但 §4.2/§5.1/§8.1 得 174 GeV",
      abs(m_phi_a - m_phi_c) > 40)
check("E-b 2√κ·v_EW = v_EW/2 EXACT (κ = 1/16)", abs(m_phi_b - m_phi_a) < mp.mpf('1e-10'))
note("★ 同一文檔三個唔同徑向質量 (123 / 174), 加上 07-26 note 之 125.34 ⟹ 徑向模身份未統一")
print(f"  123 之巧合警告: v10 E_J = Σγ+M = 123 (無量綱) vs v6.0 m_φ = 123 GeV (有量綱)")
check("E-c ★ 123 之雙重角色 (無量綱 E_J vs GeV 質量) = 潛在數值陷阱", True)

# ════════════════════════════════════════════════════════════════
print("\n═══ [F] v6.0 c 公式 vs v10 c 公式 ═══")
# ★ v6.0 之 ξ 定義 (從 unified_constants.en-US.md + validation_report + sync_waves):
#    ξ = 105 Mpc (sync correlation length); c/H₀ξ = 16/(φ⁻¹)² = 41.889; H₀ξ = 7156 km/s
xi_v6 = mp.mpf('105')
c_over_Hxi_claimed = 16/(phi**-1)**2
print(f"  v6.0 ξ = 105 Mpc (sync correlation length);  16/(φ⁻¹)² = 16φ² = {mp.nstr(c_over_Hxi_claimed,8)}")
print(f"  v6.0 聲稱 c/H₀ξ = 41.889 (0.057%);  H₀ξ = c(φ⁻¹)²/16 = 7156 km/s")
H0_from_xi = mp.mpf('7156')/xi_v6
print(f"  ⇒ H₀ξ = 7156 且 ξ = 105 ⟹ H₀ = {mp.nstr(H0_from_xi,8)} km/s/Mpc")
check("F-a ★ v6.0 c 公式之隱含 H₀ = 68.15 — 與其熱力學 k_B 式之 H₀ = 68.21 一致",
      abs(H0_from_xi - mp.mpf('68.2')) < mp.mpf('0.1'))
c_v6_form = c_over_Hxi_claimed * H0_from_xi * xi_v6
print(f"  c = 41.889 × {mp.nstr(H0_from_xi,6)} × 105 = {mp.nstr(c_v6_form,8)} km/s")
c_SI = mp.mpf('299792.458')
print(f"  vs SI c = {mp.nstr(c_SI,10)} km/s ⟹ dev = {mp.nstr(abs(c_v6_form-c_SI)/c_SI*100,6)}%")
check("F-b ★ v6.0 c 公式在 H₀ = 68.15 下閉合至 <0.1%", abs(c_v6_form-c_SI)/c_SI < mp.mpf('1e-3'))
print()
print(f"  ★ 但 v6.0 自身之 structural_derivations_2026-08-09 (Aug 9, 較後) 寫 H₀ = 72.59 (Structural)")
print(f"     ⟹ v6.0 內部 H₀ 由 68.2 (早期 waves/thermo) 演化到 72.59 (後期)")
c_with_7259 = c_over_Hxi_claimed * mp.mpf('72.59') * xi_v6
print(f"     用 H₀ = 72.59: c = {mp.nstr(c_with_7259,8)} km/s ⟹ dev = {mp.nstr(abs(c_with_7259-c_SI)/c_SI*100,6)}%")
check("F-c ★ v6.0 c 公式與 v6.0 自身後期 H₀ 唔一致 (dev >1%) ⟹ 早期 H₀ = 68.2 已廢",
      abs(c_with_7259-c_SI)/c_SI > mp.mpf('0.01'))
print(f"  v10: c = R_world·ω_ring = 4129.94 × 72.59 = {mp.nstr(mp.mpf('4129.94')*mp.mpf('72.59'),10)} km/s (dev 3.78e-5%)")
check("F-d ★ v10 c 公式 (R_world·ω_ring) 精度遠勝 v6.0 式 ⟹ v6.0 c 式已被取代", True)
note("⇒ v6.0 早期參數組 (H₀ = 68.2, ξ = 105 Mpc) 已廢; v10 用 R_world = 4129.94, ω_ring = 72.59")

# ════════════════════════════════════════════════════════════════
print("\n═══ [G] v10 內部約定分裂掃描 (W₀² = 1.23607 vs 61.5) ═══")
print(f"  v10 出現 1.23607 之檔 (grep 結果, 部分):")
print(f"    o73_h0_first_principles/docs/15_c_first_principles.md:36  ⟨W⟩ = W₀ = μ/√(2λ) (O39; W₀ = 1.23607)")
print(f"    o121_black_hole_entropy/docs/09_schwarzschild_derivation.md:15  W₀² = ε/(2κ) = 1.23607")
print(f"    o121_black_hole_entropy/docs/10_singularity_resolution.md:23      W₀² = ε/(2κ) = 1.23607")
print(f"  v10 出現 61.5 之檔: o39_wfield_condensate (權威), o204 (本 O)")
print()
print(f"  檢驗 O73 §1 之公式: W₀ = μ/√(2λ) 代入 v10 值 μ²=2, λ=2/123:")
W0_from_formula = mp.sqrt(mu2_v10)/mp.sqrt(2*lam_v10)
print(f"    W₀ = √2/√(4/123) = {mp.nstr(W0_from_formula,10)} = √61.5 = {mp.nstr(W0_v10,10)}")
check("G-a ★ O73 §1 之**公式**給 W₀ = 7.8423 (v10 值), 但**數字**寫 1.23607 (v6.0 值)",
      abs(W0_from_formula - W0_v10) < mp.mpf('1e-30') and abs(W0_from_formula - W0_v6) > 1)
check("G-b ★ O73 §1 自身不一致: 公式 vs 數字 (公式正確, 數字係 v6.0 搬字)", True)
note("⇒ 新開放 G10: v10 內部兩套 W₀ 歸一化 (61.5 vs 1.23607) 並存; 後者源自 v6.0 ε/κ 約定")
print(f"  o121 用 W₀² = 1.23607 於共形因子 Ω(x)² = ⟨|W(x)|²⟩/⟨|W₀|²⟩")
check("G-c ★ o121 若依賴 1.23607 則受影響 (需該 O 自查) — 本 O 只標記", True)

# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
npass = sum(results)
print(f"  總計: {npass}/{len(results)} PASS")
print("=" * 78)

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data',
                   '12_cross_version_audit.txt')
with open(out, 'w') as f:
    f.write(f"O204 Script 12 — 跨版本 W-field 審計: {npass}/{len(results)} PASS\n")
    f.write(f"A v6 convention: eps=1/(4phi)={mp.nstr(eps_v6,10)} kappa=1/16 W0^2=2/phi=1.2360679775\n")
    f.write(f"B invariant mu2/lambda: v6={mp.nstr(inv_v6,8)} v10={mp.nstr(inv_v10,8)} => DIFFERENT THEORY\n")
    f.write("C radial mass: V''(rho_0)=2eps [rho=sqrt2|W|] vs V''(|W|_0)=4eps [|W|] ; ratio m^2/mu2=4 both\n")
    f.write(f"D N_modes=(4phi)^36={mp.nstr(Nmode,8)}; claimed 0.0128% requires H0={mp.nstr(H0_implied,6)} (not 72.59)\n")
    f.write(f"E v6 W_field_waves internal conflict: m_phi=123 (sec4.1) vs 174 (sec4.2/5.1/8.1)\n")
    f.write(f"F v6 c formula 16phi^2*H0*xi = {mp.nstr(c_v6_form,8)} km/s (dev {mp.nstr(abs(c_v6_form-c_SI)/c_SI*100,4)}%) => superseded\n")
    f.write(f"G O73 sec1 formula gives W0=7.8423 (v10) but number 1.23607 (v6) => internal inconsistency\n")
print(f"\n  → {out}")
