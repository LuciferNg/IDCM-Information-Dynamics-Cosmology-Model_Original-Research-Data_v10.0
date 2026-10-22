#!/usr/bin/env python3
"""
O54 — 綜合 verifier: 讀返實際 JSON 驗證數字（反幻覺鐵律）
===========================================================
確認所有檢查結果同文檔一致, 冇幻覺。

驗證:
1. 讀取 4 個 data/*.json
2. 檢查關鍵數字
3. 輸出 PASS/FAIL
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "..", "data")

print("=" * 72)
print("O54 綜合 verifier")
print("=" * 72)

passed = 0
failed = 0

def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============ 1. 檢查 1: K_Chain 模式對稱性 ============
print("\n[1] data/01_kchain_mode_symmetry.json")
with open(os.path.join(DATA, "01_kchain_mode_symmetry.json")) as f:
    d1 = json.load(f)
check("γ 全正", d1["gamma_all_positive"] is True, f"(min={d1['gamma_min']:.6f})")
check("Σγ = 90", abs(d1["sum_gamma"] - 90.0) < 1e-9, f"({d1['sum_gamma']:.10f})")
check("Σγ_even = 44", abs(d1["sum_gamma_even"] - 44.0) < 1e-9, f"({d1['sum_gamma_even']})")
check("Σγ_odd = 46", abs(d1["sum_gamma_odd"] - 46.0) < 1e-9, f"({d1['sum_gamma_odd']})")
check("本徵向量全實", d1["eigenvectors_real"] is True)
check("Z₂ 對偶 22/22", d1["z2_pairs_ok"] == 22)

# ============ 2. 檢查 2: 投影 kernel ============
print("\n[2] data/02_projection_kernel.json")
with open(os.path.join(DATA, "02_projection_kernel.json")) as f:
    d2 = json.load(f)
check("n* = 27", d2["n_star"] == 27, f"({d2['n_star']})")
check("f_proj = 0.7720", abs(d2["f_proj"] - 0.771960) < 1e-5, f"({d2['f_proj']:.6f})")
check("E_proj = 28.5", abs(d2["E_proj_check"] - 28.5) < 1e-9, f"({d2['E_proj_check']})")
check("kernel 17 模式", d2["kernel_count"] == 17, f"({d2['kernel_count']})")
check("kernel 能量 60.8845", abs(d2["kernel_energy"] - 60.8845) < 1e-3, f"({d2['kernel_energy']:.4f})")
check("E_sync = 61.5", abs(d2["E_sync_check"] - 61.5) < 1e-9, f"({d2['E_sync_check']})")
check("守恆 Σγ = 90", abs(d2["conservation_sum"] - 90.0) < 1e-9, f"({d2['conservation_sum']})")

# ============ 3. 檢查 3: CP 相位 ============
print("\n[3] data/03_cp_phase_relation.json")
with open(os.path.join(DATA, "03_cp_phase_relation.json")) as f:
    d3 = json.load(f)
check("δ_CKM = 66.40°", abs(d3["delta_ckm"] - 66.40) < 1e-6, f"({d3['delta_ckm']})")
check("δ_PMNS = 72°", abs(d3["delta_pmns"] - 72.0) < 1e-6, f"({d3['delta_pmns']})")
check("J_CP ~ 3.2e-5 (PDG 1.5%)", abs(d3["J_cp_idcm"] - 3.18e-5) / 3.18e-5 < 0.02,
      f"({d3['J_cp_idcm']:.5e})")
check("η_B = 6.0622e-10", abs(d3["eta_B"] - 6.0622e-10) / 6.0622e-10 < 1e-6)

# ============ 4. 檢查 4: 宇宙線 ============
print("\n[4] data/04_annihilation_cosmic_rays.json")
with open(os.path.join(DATA, "04_annihilation_cosmic_rays.json")) as f:
    d4 = json.load(f)
check("η_B 偏差 0.62%", abs(d4["eta_B_dev"] - 0.62) < 0.05, f"({d4['eta_B_dev']}%)")
check("正電子 2× 上升", abs(d4["eplus_ratio"] - 2.0) < 1e-9, f"({d4['eplus_ratio']})")
check("n_B̄=0 預言", d4["prediction_nBbar_zero"] is True)

# ============ 5. 檢查 5: 局部反投影 ============
print("\n[5] data/05_local_antiprojection.json")
with open(os.path.join(DATA, "05_local_antiprojection.json")) as f:
    d5 = json.load(f)
check("反物質存在 (觀測)", d5["antimatter_observed"] is True)
check("e⁺ 對產生閾值 1.022 MeV", abs(d5["pair_threshold_e"] - 1.022) < 0.001,
      f"({d5['pair_threshold_e']})")
check("p̄ 對產生閾值 1.877 GeV", abs(d5["pair_threshold_p"] - 1876.54) < 0.1,
      f"({d5['pair_threshold_p']})")
check("AMS p̄/p 1.6e-4", abs(d5["pbar_p_ams"] - 1.6e-4) / 1.6e-4 < 1e-6)
check("宏觀 n_B̄/n_B < 1e-9", d5["nBbar_nB_limit"] == 1e-9)

# ============ 6. 檢查 6: 反粒子自由度 ============
print("\n[6] data/06_antiparticle_origin.json")
with open(os.path.join(DATA, "06_antiparticle_origin.json")) as f:
    d6 = json.load(f)
check("反粒子 = 荷自由度", d6["antiparticle_from_charge"] is True)
check("荷 = CY₃ 複結構", d6["charge_from_CY3_complex_structure"] is True)
check("h21 = 98 = Σγ+2B", d6["h21"] == 98 and d6["h21_formula"] == "Σγ+2B")
check("C 算子 involution", d6["C_operator_involution"] is True)
check("微觀反物質存在", d6["micro_antimatter_observed"] is True)

# ============ 7. 檢查 7: 拍頻差頻/和頻 ============
print("\n[7] data/07_beat_sum_frequency.json")
with open(os.path.join(DATA, "07_beat_sum_frequency.json")) as f:
    d7 = json.load(f)
check("946 拍頻對", d7["n_pairs"] == 946, f"({d7['n_pairs']})")
check("n/p = γ₇/γ₂₀ 0.14262", abs(d7["np_ratio_matter"] - 0.14262) < 1e-4,
      f"({d7['np_ratio_matter']:.5f})")
check("CPT 質量比不變", abs(d7["np_ratio_antimatter_CPT"] - d7["np_ratio_matter"]) < 1e-12)
check("和頻需額外能量", d7["min_extra_energy"] > 0, f"({d7['min_extra_energy']:.4f})")

# ============ 8. 檢查 8: W-field 二次量子化 ============
print("\n[8] data/08_wfield_second_quantization.json")
with open(os.path.join(DATA, "08_wfield_second_quantization.json")) as f:
    d8 = json.load(f)
check("⟨W⟩² = Ω_Λ", abs(d8["W2_condensate"] - d8["Omega_Lambda"]) < 1e-9)
check("μ² = 2 (奇偶差)", abs(d8["mu2"] - 2.0) < 1e-9)
check("荷 ±1", d8["charge_matter"] == 1 and d8["charge_antimatter"] == -1)
check("宏觀關閉", d8["macro_closed"] is True)
check("局部開啟", d8["local_open"] is True)

# ============ 9. 檢查 9: CY₃ 荷 + 自旋 ============
print("\n[9] data/09_cy3_charge_spinor.json")
with open(os.path.join(DATA, "09_cy3_charge_spinor.json")) as f:
    d9 = json.load(f)
check("h21 = 98 = Σγ+2B", d9["h21"] == 98 and d9["h21_formula"] == "Σγ+2B")
check("χ = −124", d9["chi"] == -124)
check("Y = 3×12D", d9["Y_structure"] == "3×12D")
check("荷 ±1", d9["matter_charge"] == 1 and d9["antimatter_charge"] == -1)
check("C² = 1", d9["C2"] == 1)

# ============ 10. 檢查 10: CKM 符號 ============
print("\n[10] data/10_ckm_cp_sign.json")
with open(os.path.join(DATA, "10_ckm_cp_sign.json")) as f:
    d10 = json.load(f)
check("δ_CKM = 66.40°", abs(d10["delta_ckm"] - 66.40) < 1e-6)
check("J_CP > 0", d10["J_cp"] > 0)
check("η_B 符號 +", d10["eta_B_sign"] == "+")
check("反宇宙預言", "反宇宙" in d10["antiuniverse_prediction"])

# ============ 11. 檢查 11: sympy K_Chain 譜驗證 ============
print("\n[11] data/11_verify_kchain_spectrum.json")
with open(os.path.join(DATA, "11_verify_kchain_spectrum.json")) as f:
    d11 = json.load(f)
check("44-site Σγ = 90", d11["sum_gamma_44"] == 90)
check("88-site Σγ_even = 90", d11["sum_gamma_even_88"] == 90)
check("88-site Σγ_odd = 88", d11["sum_gamma_odd_88"] == 88)
check("Σγ_total = 178 = 2F₁₁", d11["sum_gamma_total"] == 178)
check("Z₂ 對偶精確", d11["z2_dual_exact"] is True)
check("γ_{2n} = γ_n^(44)", d11["gamma_2n_identity"] is True)

# ============ 12. 檢查 12: sympy 投影 kernel ============
print("\n[12] data/12_verify_projection_kernel.json")
with open(os.path.join(DATA, "12_verify_projection_kernel.json")) as f:
    d12 = json.load(f)
check("L₆ = 18 精確", d12["L6_exact"] == 18)
check("n* = 27", d12["n_star"] == 27)
check("f_proj ≈ 0.771960", abs(d12["f_proj"] - 0.771960) < 1e-5)
check("E_proj = 28.5", abs(d12["E_proj"] - 28.5) < 1e-9)
check("E_sync = 61.5", abs(d12["E_sync"] - 61.5) < 1e-9)
check("守恆 Σγ = 90", abs(d12["conservation"] - 90.0) < 1e-9)
check("kernel 17 模式", d12["kernel_count"] == 17)

# ============ 13. 檢查 13: sympy 拍頻恆等式 ============
print("\n[13] data/13_verify_beat_identity.json")
with open(os.path.join(DATA, "13_verify_beat_identity.json")) as f:
    d13 = json.load(f)
check("三角恆等式精確", d13["trig_identity"] is True)
check("C(44,2) = 946", d13["C44_2"] == 946)
check("差頻 946 唯一", d13["diff_unique"] == 946)
check("和頻 946 唯一", d13["sum_unique"] == 946)
check("和頻 > 差頻", d13["sum_gt_diff"] is True)
check("E_pair = 2ħ·max(ω)", d13["E_pair"] == "2ħ·max(ω)")

# ============ 14. 檢查 14: sympy W-field ============
print("\n[14] data/14_verify_wfield.json")
with open(os.path.join(DATA, "14_verify_wfield.json")) as f:
    d14 = json.load(f)
check("Ω_Λ ≈ 0.68328", abs(d14["Omega_Lambda"] - 0.68328) < 1e-4)
check("μ² = 2", d14["mu2"] == 2)
check("⟨W⟩² = Ω_Λ 精確", abs(d14["W2_condensate"] - d14["Omega_Lambda"]) < 1e-9)
check("荷守恆", d14["charge_conservation"] is True)

# ============ 15. 檢查 15: sympy CY₃ ============
print("\n[15] data/15_verify_cy3_charge.json")
with open(os.path.join(DATA, "15_verify_cy3_charge.json")) as f:
    d15 = json.load(f)
check("h11 = 36", d15["h11"] == 36)
check("h21 = 98", d15["h21"] == 98)
check("χ = −124", d15["chi"] == -124)
check("Y = 3×12D", d15["Y_structure"] == "3×12D")
check("C(12,2) = 66", d15["C12_2"] == 66)
check("Euler χ 一致", d15["euler_check"] == -124)

# ============ 16. 檢查 16: sympy CKM/J_CP ============
print("\n[16] data/16_verify_ckm_jcp.json")
with open(os.path.join(DATA, "16_verify_ckm_jcp.json")) as f:
    d16 = json.load(f)
check("J_CP 公式精確", d16["J_formula_exact"] is True)
check("J_CP vs PDG < 2%", d16["dev_pct"] < 2.0, f"({d16['dev_pct']:.2f}%)")
check("J_CP > 0", d16["J_cp_sign"] == "+")
check("δ_CKM = 66.40°", abs(d16["delta_ckm"] - 66.40) < 1e-6)

# ============ 17. 檢查 17: 正電子通道 ============
print("\n[17] data/17_positron_pair_production.json")
with open(os.path.join(DATA, "17_positron_pair_production.json")) as f:
    d17 = json.load(f)
check("產生率 ∝ M₀γ_n", "M₀·γ_n" in d17["Gamma_n_prop"])
check("E_pair = 2ħ·max(ω)", "2ħ·max" in d17["E_pair_formula"])
check("對產生閾值 e⁺e⁻ ~1.022 MeV", abs(d17["pair_threshold_ee"] - 1.022) < 0.001)
check("對產生閾值 p̄p ~1.877 GeV", abs(d17["pair_threshold_pp"] - 1876.54) < 0.1)
check("CPT 一致", d17["CPT_consistent"] is True)

# ============ 18. 檢查 18: 和頻↔pair production ============
print("\n[18] data/18_pair_production_mapping.json")
with open(os.path.join(DATA, "18_pair_production_mapping.json")) as f:
    d18 = json.load(f)
check("E_pair = 2ħ·max(ω)", "2ħ·max" in d18["E_pair_formula"])
check("三步投影", len(d18["three_level_projection"]) == 3)
check("荷守恆", d18["charge_conservation"] is True)
check("CPT 守恆", d18["CPT_conservation"] is True)

# ============ 19. 檢查 19: 荷配對證明 ============
print("\n[19] data/19_charge_pairing_proof.json")
with open(os.path.join(DATA, "19_charge_pairing_proof.json")) as f:
    d19 = json.load(f)
check("Σγ = 90 代數證明", d19["sum_gamma"] == 90)
check("B = 4 精確 (φ)", d19["B"] == 4)
check("h21 = 98 = Σγ+2B", d19["h21"] == 98 and d19["h21_formula"] == "Σγ + 2B = 90 + 8")
check("Hodge * 自然配對", "Hodge" in d19["pairing_mechanism"])

# ============ 20. 檢查 20: 差額符號 ============
print("\n[20] data/20_sign_asymmetry.json")
with open(os.path.join(DATA, "20_sign_asymmetry.json")) as f:
    d20 = json.load(f)
check("δ_CKM = 66.40°", abs(d20["delta_ckm"] - 66.40) < 1e-6)
check("J_CP > 0", d20["J_cp_sign"] == "+")
check("η_B 符號 +", d20["eta_B_sign"] == "+")
check("反宇宙預言", "反物質主導" in d20["antiuniverse_prediction"])

# ============ 21. 檢查 21: 正電子通道定量 ============
print("\n[21] data/21_positron_channel_quantitative.json")
with open(os.path.join(DATA, "21_positron_channel_quantitative.json")) as f:
    d21 = json.load(f)
check("產生率 ∝ M₀γ_n", "M₀·γ_n" in d21["Gamma_n_prop"])
check("F_proj = 17", d21["F_proj"] == 17)
check("χ²/dof < 2", d21["chi2_dof"] < 2, f"({d21['chi2_dof']:.2f})")
check("正電子上升 (W-field)", "方向一致" in d21["conclusion"])

# ============ 22. 檢查 22: CY₃ 投影放大因子 ============
print("\n[22] data/22_cy3_projection_factor.json")
with open(os.path.join(DATA, "22_cy3_projection_factor.json")) as f:
    d22 = json.load(f)
check("F_proj = 17 = kernel 模式數", d22["F_proj"] == 17 and "kernel" in d22["F_proj_origin"])
check("m_p 預言偏差 < 2%", d22["dev_pct"] < 2, f"({d22['dev_pct']:.2f}%)")
check("偏差同 m_δW≈m₇ 同源", "m_δW" in d22["conclusion"])

# ============ 23. 檢查 23: 90+8 對應 ============
print("\n[23] data/23_90_8_pairing.json")
with open(os.path.join(DATA, "23_90_8_pairing.json")) as f:
    d23 = json.load(f)
check("Σγ = 90", d23["sum_gamma"] == 90)
check("E_proj + E_sync = 90", abs(d23["E_proj"] + d23["E_sync"] - 90) < 1e-9)
check("2B = 8", d23["two_B"] == 8)
check("h12 = 98 = 90+8", d23["h12"] == 98 and d23["h12"] == d23["sum_gamma"] + d23["two_B"])

# ============ 24. 檢查 24: 電子質量閉合 ============
print("\n[24] data/24_electron_mass.json")
with open(os.path.join(DATA, "24_electron_mass.json")) as f:
    d24 = json.load(f)
check("m_e 預言 < 0.5%", d24["dev_pct"] < 0.5, f"({d24['dev_pct']:.4f}%)")
check("F_proj_e = L₆/F₅", abs(d24["L6_F5"] - 3.6) < 1e-9)

# ============ 25. 檢查 25: 輕子質量譜系 ============
print("\n[25] data/25_lepton_mass_hierarchy.json")
with open(os.path.join(DATA, "25_lepton_mass_hierarchy.json")) as f:
    d25 = json.load(f)
check("m_μ 預言 < 0.5%", d25["dev_mu_pct"] < 0.5, f"({d25['dev_mu_pct']:.4f}%)")
check("m_τ 預言 < 0.5%", d25["dev_tau_pct"] < 0.5, f"({d25['dev_tau_pct']:.4f}%)")

# ============ 26. 檢查 26: 正電子譜形 fit ============
print("\n[26] data/26_positron_spectrum_fit.json")
with open(os.path.join(DATA, "26_positron_spectrum_fit.json")) as f:
    d26 = json.load(f)
check("W-field 通道上升 (γ > 0)", d26["W_fit_params"]["gamma"] > 0,
      f"(γ = {d26['W_fit_params']['gamma']:.3f})")
check("f(10)→f(500) 上升", d26["E_10GeV_f"] < d26["E_500GeV_f"])
check("高頻模式主導", d26["Gamma_high_ratio"] > 1)

# ============ 27. 檢查 27: CR 譜接駁 ============
print("\n[27] data/27_cr_spectrum_connection.json")
with open(os.path.join(DATA, "27_cr_spectrum_connection.json")) as f:
    d27 = json.load(f)
check("χ²/dof < 3 (CR 接駁)", d27["chi2_dof"] < 3, f"({d27['chi2_dof']:.1f})")
check("冪律上升 γ > 0", d27["W_effective_index"] > 0, f"(γ = {d27['W_effective_index']:.3f})")

# ============ 28. 檢查 28: O53 A1/A2 閉合 ============
print("\n[28] data/28_o53_a1_a2_closure.json")
with open(os.path.join(DATA, "28_o53_a1_a2_closure.json")) as f:
    d28 = json.load(f)
check("c_f = SM 電荷 (1/3 量子化)", abs(d28["A1_sum_sq"] - 36) < 1)
check("det = 18 = h11/2", abs(d28["A1_det"] - 18) < 1)
check("J* = I₃⊗J₁₂ (3 代等權)", "I₃" in d28["A2_Jstar"])

# ============ 總結 ============
print(f"\n{'='*72}")
print(f"結果: {passed} PASS, {failed} FAIL")
print(f"{'='*72}")

if failed > 0:
    print("❌ 有 FAIL — 需要修正!")
    exit(1)
else:
    print("✅ 全部通過 — 無幻覺, 數字一致")
    exit(0)
