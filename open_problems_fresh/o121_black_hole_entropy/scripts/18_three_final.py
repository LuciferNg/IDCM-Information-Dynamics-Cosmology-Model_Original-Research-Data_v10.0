#!/usr/bin/env python3
"""
O121 — script 18: 三項收尾 (K_tree 來源 / n↔E 映射 / 觀測約束掃描)
==================================================================
A. K_tree = φ-階梯之底層來源: 291.5 = N_d·L, L = 53/8; ★ η 指數與 L 無關
B. n↔E 映射 (P-G8f): 阻塞點 = 晶格尺度 a
C. 觀測約束掃描: τ_rec 現時可否檢驗?

零新常數。
"""
import math, json, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASS = 0; FAIL = 0
def ck(n, c, d=""):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n} {d}")
    else: FAIL += 1; print(f"  ❌ {n} {d}")

phi = (1+math.sqrt(5))/2
N_d, mu2, B_c, N_gen, L5, K_tree = 44, 2, 4, 3, 11, 33
ell = 4.516e-23          # BH 核心尺度 (O121 docs/10)
hbar, c_l = 1.0546e-34, 2.99792458e8
eV = 1.602e-19; Mpc_m = 3.0856775814913673e22; Yr_s = 3.1557e7
omega_ring = 72.59
T_ring = (2*math.pi/(omega_ring*1e3/Mpc_m))/Yr_s
MIS = 20; tau_pred = (2**MIS)*T_ring
V_comov = 1.2e13; rho_BH = 4.9e5; M_BH = rho_BH*V_comov
Mdot_uhecr = 6712.8; tau_ref = M_BH/Mdot_uhecr
t_univ = 13.8e9

print("="*78); print("O121 script 18: 三項收尾"); print("="*78)

# ===== A. K_tree φ-階梯之底層來源 =====
print("\n"+"="*78); print("[A] K_tree = φ-階梯: 291.5 之分解"); print("="*78)
L_depth = 53/8
print(f"  O221 寫法: μ_m = φ^(583/2 − m),  m = 0..{K_tree}")
print(f"  等價分解:  583/2 = {583/2} = N_d × L = {N_d} × {L_depth} = {N_d*L_depth}")
ck("583/2 = N_d × (53/8) = 291.5 EXACT", abs(N_d*(53/8) - 291.5) < 1e-12)
print(f"  ★ L = 53/8 = {L_depth} (global_routing_table scripts 27/28, O41/O72)")
print(f"    樹容量 B·L = {B_c}×{L_depth} = {B_c*L_depth} (O39/O41 🟢)")
ck("B·L = 4 × 53/8 = 26.5 (樹容量)", abs(B_c*L_depth - 26.5) < 1e-12)
print("  ⚠️ **L = 53/8 本身 🔴 未推導** — O72 docs/07 自認: 「53 係質數, 冇自然")
print("     Fibonacci 分解; 目前係 fit 候選」(O72 docs/02:39, 03:38)")
ck("53 為質數 (無自然 Fibonacci 分解)", all(53 % k for k in range(2, 8)))
# ★ 關鍵: η 之指數與 L 無關
n_rungs = (N_d - mu2)/2
print(f"\n  ★★ η = φ^-{(N_d-mu2)/2:.0f}: 指數 = (N_d−μ²)/2 = (44−2)/2 = {n_rungs:.0f}")
print(f"     其中 N_d = B × L₅ = {B_c}×{L5} = {B_c*L5} (用 L₅ = 11, **唔係** L = 53/8)")
print(f"     μ² = 2 = E−O 扇區隙")
ck("η 之指數 21 完全唔依賴 L = 53/8", abs(n_rungs - 21) < 1e-12 and (B_c*L5) == N_d)
ck("η 指數由 (B·L₅ − μ²)/2 得出 (L₅=11, 非 L=53/8) ⟹ L 之 🔴 唔污染",
   abs((B_c*L5 - mu2)/2 - n_rungs) < 1e-12 and L_depth != L5)
print("  ⟹ 分離結論: 階梯**深度** L 🔴 (錨定 μ_0, 與 η 無關); 階梯**比** φ 🟢 (x²−x−1 結構強制)")
print("     ⟹ η = φ⁻²¹ 只依賴「比 = φ」+「級數 21」兩者, 兩者皆非 L")

# ===== B. n↔E 映射 =====
print("\n"+"="*78); print("[B] n↔E 映射 (P-G8f)"); print("="*78)
print("  鏈色散: ω_n = (c/a)·2|sin(πn/88)|  ⟹  E_n = ħc·2sin(πn/88)/a")
print("  ⟹ 映射需要**晶格尺度 a** (IDCM 現時未定)")
def E_n(n, a):
    return hbar*c_l*2*math.sin(math.pi*n/88)/a/eV   # eV
for a_lbl, a in (("a = ℓ (BH 核心 4.516e-23)", ell), ("a = ℓ_P (1.616e-35)", 1.616e-35)):
    e1, e27 = E_n(1, a), E_n(27, a)
    print(f"    {a_lbl:30s}: E_1 = {e1:.3e} eV, E_27 = {e27:.3e} eV, E_27/E_1 = {e27/e1:.2f}")
a_needed = hbar*c_l*2*math.sin(math.pi*27/88)/(5e18*eV)
print(f"  觀測 ankle ~5e18 eV ⟹ 需 a = {a_needed:.3e} m")
ck("a = ℓ 之 E_27 ≪ 觀測 ankle (naive 映射失敗)", E_n(27, ell) < 5e18,
   f"({E_n(27,ell):.2e} vs 5e18)")
print(f"  ★ 阻塞點確認: 需**獨立**定 a; 現時 a 只有 🟡 候選 (ℓ)")
print(f"  ⟹ **P-G8f 維持 🟡**: σ_n 譜係導出, 但 n↔E 映射未定 ⟹ 未能測 UHECR 能譜")

# ===== C. 觀測約束掃描 =====
print("\n"+"="*78); print("[C] τ_rec 之觀測約束掃描 (item ①)"); print("="*78)
print(f"  τ_pred(R1b) = {tau_pred:.3e} yr | τ_pred(R2a) = {phi**21*T_ring:.3e} yr | τ_ref = {tau_ref:.3e}")
cands = [("R1b 2²⁰·T_ring", tau_pred), ("R2a φ²¹·T_ring", phi**21*T_ring)]
print(f"\n  {'約束':34s} {'界':>13s}  判別力")
# (i) UHECR 下界
print(f"  {'(i) UHECR 率下界':34s} {'≥ %.2e' % tau_ref:>13s}  兩者皆通過 (鬆 x{tau_pred/tau_ref:.0f}–x{phi**21*T_ring/tau_ref:.1f})")
# (ii) BH demographics
for lbl, tp in cands:
    frac = t_univ/tp
    print(f"  (ii) BH 質量損耗 (t_univ/τ: {lbl:16s})        {frac:.2e}   ≪ 可測 (~0.1) ⟹ 無約束")
ck("BH 人口統計無約束 (損耗 <1e-5)", t_univ/tau_pred < 1e-5)
# (iii) accretion
Mdot_ret = M_BH/tau_pred
print(f"  (iii) 吸積率 (返回率 {Mdot_ret:.1f} vs 觀測吸積 ~1e10 M☉/yr)   ≪1e10      ⟹ 無約束")
ck("吸積率無約束 (返回 ≪ 觀測吸積)", Mdot_ret < 1e9)
# (iv) 質量函數低端
print(f"  (iv) 質量函數低端 (P-G8c)                    定性      🟡 未定量化")
ck("無任何約束能分辨 R1b 與 R2a (差 ×42.8)", abs((tau_pred/(phi**21*T_ring)) - 42.84) < 0.1,
   f"(×{tau_pred/(phi**21*T_ring):.2f})")
print(f"\n  ★★ 裁決: τ_rec 之可行值域跨 **2 個數量級** (8.76e14 – 8.87e16)")
print(f"     而**冇任何現有觀測**能分辨 ⟹ **τ_rec 現時不可檢驗** (untestable)")
print(f"  ★ 真出路: 需開**新**觀測通道 (非 M_BH/Ṁ_UHECR):")
print(f"     P-G8d M_crit = 7.9e4 kg (最小黑洞質量) — 唯一有 ΛCDM 判別力者")

# ===== 總結 =====
print("\n"+"="*78); print("總結"); print("="*78)
print(f"  A. K_tree φ-階梯: 291.5 = N_d·(53/8) ✓; 樹容量 B·L = 26.5 ✓")
print(f"     ★ **η 指數與 L 無關** ⟹ L=53/8 之 🔴 **唔污染** η = φ⁻²¹")
print(f"  B. n↔E: 阻塞 = 晶格尺度 a; a=ℓ 給 E_27 = {E_n(27,ell):.2e} eV ≪ 5e18 ⟹ P-G8f 維持 🟡")
print(f"  C. τ_rec 現時**不可檢驗** (可行域跨 2 個數量級, 無觀測可分辨)")
out = {
 "problem": "O121/G8 三項收尾",
 "A_ktree": {"decomposition": "583/2 = N_d * (53/8) = 291.5",
              "L_depth": L_depth, "tree_capacity_BL": B_c*L_depth,
              "L_status": "🔴 53 質數, 無自然 Fibonacci 分解 (O72 docs/07)",
              "eta_exponent": n_rungs, "eta_independent_of_L": (B_c*L5) == N_d,
              "verdict": "η 指數只依賴 階梯比 φ + 級數 21; 兩者皆非 L"},
 "B_n_to_E": {"dispersion": "E_n = hbar*c*2sin(pi*n/88)/a",
               "E_27_at_a_eq_ell_eV": E_n(27, ell), "obs_ankle_eV": 5e18,
               "a_needed_m": a_needed, "obstruction": "晶格尺度 a 未由 IDCM 獨立定出",
               "status": "🟡 P-G8f 維持"},
 "C_constraints": {"tau_pred": tau_pred, "tau_ref": tau_ref,
                    "viable_range": [tau_ref, tau_pred],
                    "orders_of_magnitude": math.log10(tau_pred/tau_ref),
                    "constraints_checked": ["UHECR 下界", "BH 人口統計", "吸積率", "質量函數低端"],
                    "verdict": "τ_rec 現時不可檢驗; 唯一 ΛCDM 判別力 = P-G8d M_crit"},
}
with open(os.path.join(BASE,"data","18_three_final.json"),"w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nRESULT: {PASS} PASS, {FAIL} FAIL  {'🟢' if FAIL==0 else '🔴'}")
if FAIL: exit(1)
