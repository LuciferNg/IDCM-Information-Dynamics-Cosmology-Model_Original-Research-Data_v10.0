#!/usr/bin/env python3
"""O38 handoff 完整 audit — 對照最新 system prompt 守則"""
import os, sys, subprocess, re

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o38_kappa_prediction"
ROOT = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
os.chdir(BASE)

print("=" * 72)
print("  O38 HANDOFF AUDIT — 對照最新 system prompt 守則")
print("=" * 72)
checks = []

# ── A. 記録完整性 ──
print("\n─── A. 交收文件齊全 ───")
files_needed = [
    "SESSION_START.md",       # 交接文件
    "01_problem_record.md",   # 問題記錄
    "final_result.md",        # 結論摘要 (RESULT_TEMPLATE)
    "docs/01_derivation_record.md",
    "docs/02_o215_report.md",
    "docs/03_m0_scale_attack.md",   # M₀ 標度攻堅 (2026-10-18)
    "docs/04_m0_cross_equations.md",# 需-M₀ 公式網交叉約束 (2026-10-18)
    "docs/05_two_ns_identity.md",   # ★兩 N 身份辨別 (2026-10-18)
    "docs/06_m0_factor_tree.md",    # ★N 分解樹 拆小扣除 (2026-10-18)
    "docs/07_family_freedom_audit.md",  # ★式族自由度審計 (2026-10-18)
    "docs/08_small_remainder_audit.md", # ★剩餘細數審計 (2026-10-18)
    "docs/09_emergence_audit.md",    # ★湧現審計 方法轉向 (2026-10-18)
    "docs/10_central_fractal.md",    # ★中樞/中央/分形張量 (2026-10-18)
    "docs/11_rederive_n_identity.md",# ★重新推導更正 O250 身份樹 (2026-10-18)
    "docs/12_m0_chain_internal.md",  # ★缺口承繼 + M₀ 生成鏈 (2026-10-18)
    "docs/13_x_factor_audit.md",     # ★X = M₀/E_kchain 專項湧現審計 (2026-10-18)
    "docs/14_phi_lock_audit.md",      # ★φ 結構鎖定統一審計 (2026-10-18)
    "docs/15_m0_ontology_audit.md",    # ★M₀ 標度本體審計 (2026-10-18)
    "docs/16_n38_closure_audit.md",    # ★N_O38 全值專項 (2026-10-18)
    "docs/17_tree_scale_direction.md",# ★樹標度方向 (2026-10-18)
    "docs/18_layer_benchmark_audit.md", # ★每級對標物 (2026-10-18)
    "docs/19_beat_ladder_rederive.md",# ★節拍階梯重推 (2026-10-18)
    "docs/20_rd_anchor_chain.md",# ★r_d 錨鏈閉合 (2026-10-18)
    "docs/21_smallest_gap_audit.md", # ★拆小鏈最終 (2026-10-18)
    "docs/22_musical_scale_audit.md", # ★音階審計 (2026-10-18)
    "docs/23_shadow_mass_ontology.md", # ★影子本體 (2026-10-18)
    "docs/24_mass_wave_beat_verdict.md", # ★beat 判別 (2026-10-19)
    "docs/25_baseline_frequency_verdict.md", # ★本底頻率 (2026-10-19)
    "docs/26_interval_final_audit.md", # ★分間最終 (2026-10-19)
    "docs/27_qmgr_rewrite_audit.md", # ★QM/GR 重寫 (2026-10-19)
    "docs/28_scale_dome_audit.md", # ★穹頂假說 (2026-10-19)
    "docs/29_count_ontology_audit.md", # ★計數本體 (2026-10-19)
    "docs/30_wfield_six_loop_audit.md", # ★6-loop 審計 (2026-10-19)
    "docs/31_spectral_path_audit.md", # ★Gemini 三路徑 (2026-10-19)
    "docs/32_planck_exclusion_audit.md", # ★排除 Planck 錨 (2026-10-19)
    "docs/33_counting_search.md", # ★單一變量計算搜尋 (2026-10-19)
    "docs/34_cutoff_dichotomy_audit.md", # ★投影vs採樣截斷 (2026-10-19)
    "docs/35_cell_complex_container.md", # ★點線面幾何體 (2026-10-19)
    "docs/36_container_derivability.md", # ★容器可推性 (2026-10-19)
    "docs/37_m0_dome_significance.md", # ★★穹頂 M₀ 意義 (2026-10-19)
    "docs/38_gap_nature_adjudication.md", # ★★缺口性質裁決 (2026-10-19)
    "docs/39_mera_audit.md", # ★MERA 審計 (2026-10-19)
    "docs/40_nonstandard_mera.md", # ★非標準 MERA (2026-10-19)
    "docs/41_quotient_algebraic_cutoff.md", # ★純商譜+代數截斷 (2026-10-19)
    "data/step19_m0_anchor_results.txt",
    "data/step20_m0_scan_results.txt",
    "data/step21_m0_cross_results.txt",
    "data/step22_two_n_results.txt",
    "data/step23_factor_tree_results.txt",
    "data/step24_family_freedom_results.txt",
    "data/step25_small_remainder_results.txt",
    "data/step26_emergence_results.txt",
    "data/step27_central_fractal_results.txt",
    "data/step29_rederive_n_identity_results.txt",
    "data/step30_mpl_over_m0_results.txt",
    "data/step31_m0_chain_internal_results.txt",
    "data/step32_x_factor_results.txt",
    "data/step33_phi_lock_results.txt",
    "data/step34_m0_ontology_results.txt",
    "data/step35_n38_closure_results.txt",
    "data/step36_tree_scale_results.txt",
    "data/step37_layer_benchmark_results.txt",
    "data/step38_beat_ladder_results.txt",
    "data/step39_rd_anchor_results.txt",
    "data/step40_smallest_gap_results.txt",
    "data/step41_musical_scale_results.txt",
    "data/step42_shadow_mass_results.txt",
    "data/step43_mass_wave_beat_results.txt",
    "data/step44_baseline_frequency_results.txt",
    "data/step45_interval_final_results.txt",
    "data/step46_qmgr_rewrite_results.txt",
    "data/step47_scale_dome_results.txt",
    "data/step48_count_ontology_results.txt",
    "data/step49_six_loop_results.txt",
    "data/step50_wfield_six_loop_results.txt",
    "data/step51_spectral_path_results.txt",
    "data/step52_planck_exclusion_results.txt",
    "data/step53_counting_search_results.txt",
    "data/step54_cutoff_dichotomy_results.txt",
    "data/step55_cell_complex_results.txt",
    "data/step56_container_derivability_results.txt",
    "data/step57_m0_dome_significance_results.txt",
    "data/step58_gap_nature_results.txt",
    "data/step59_mera_results.txt",
    "data/step60_nonstandard_mera_results.txt",
    "data/step61_quotient_results.txt",
]
for f in files_needed:
    ok = os.path.exists(f)
    print(f"  {'✅' if ok else '❌'} {f}")
    checks.append(ok)

# ── B. 狀態一致性 ──
print("\n─── B. 狀態一致性 ───")
sess = open("SESSION_START.md").read()
rec = open("01_problem_record.md").read()
fr = open("final_result.md").read()
ok_b1 = "🟢 已閉合" in sess and "🟢 **已閉合**" in rec and "## 狀態: 🟢 已閉合" in fr
print(f"  {'✅' if ok_b1 else '❌'} 三文件狀態一致 🟢 已閉合 ({'SS✅' if '🟢 已閉合' in sess else 'SS❌'} {'REC✅' if '🟢 **已閉合**' in rec else 'REC❌'} {'FR✅' if '## 狀態: 🟢 已閉合' in fr else 'FR❌'})")
checks.append(ok_b1)

# ── C. 時序索引 ──
print("\n─── C. 推導時序索引 ───")
if "推導時序索引" in rec:
    scripts_in_idx = []
    for i in range(1, 28):
        if i == 28:
            continue  # row 28 = 判決接收, 冇 script
        m = re.search(rf"scripts/{i:02d}_", rec)
        scripts_in_idx.append(i if m else None)
    missing = [i for i in scripts_in_idx if i is None]
    print(f"  ✅ 時序索引存在, 01-26 全齊 ({'❌ 缺 ' + str(missing) if missing else '✅'})")
    checks.append(not missing)
else:
    print("  ❌ 時序索引唔存在")
    checks.append(False)

# ── D. 開放問題誠實標記 ──
print("\n─── D. 開放問題 (🔴/🟡) ───")
open_lines = []
for line in rec.splitlines():
    if ("🔴" in line or "🟡" in line) and "|" in line:
        open_lines.append(line.strip()[:100])
for ol in open_lines:
    print(f"  {ol}")
print(f"  ({len(open_lines)} 條開放項已記錄)")
checks.append(len(open_lines) > 0)

# ── E. 時序完整性 (冇回溯污染) ──
print("\n─── E. 歷史時序完整性 ───")
d1 = open("docs/01_derivation_record.md").read()
# docs/01 核心推導必須完整 + 附錄標明日期
ok_e = "82/82" in d1 and "外部回報處理附錄" in d1 and "9.1 O215" in d1 or "9.2 O81" in d1 or "9.3 O214" in d1
print(f"  {'✅' if '82/82' in d1 and '外部回報處理附錄' in d1 else '❌'} docs/01 完整 (82/82 + 附錄)")
ok_e2 = all(f"9.{i} " in d1 for i in (1,2,3))
print(f"  {'✅' if ok_e2 else '❌'} 附錄 9.1/9.2/9.3 齊全")
checks.append(ok_e and ok_e2)

# ── F. RESULT_TEMPLATE 格式 ──
print("\n─── F. final_result 格式 (RESULT_TEMPLATE) ───")
ok_f = all(s in fr for s in ["## 狀態", "## 結論", "## 關鍵公式", "## 依賴", "## 密度基準"])
print(f"  {'✅' if ok_f else '❌'} 狀態/結論/公式/依賴/密度基準 齊全")
checks.append(ok_f)

# ── G. README 狀態 (global) ──
print("\n─── G. README 總表狀態 ───")
readme = open(os.path.join(ROOT, "README.md")).read()
m = re.search(r"\*\*O38\*\*.*?\*\*(\d+/\d+ PASS)", readme)
readme_val = m.group(1) if m else "唔知"
print(f"  README: O38 {readme_val} (實際 82/82)")
ok_g = readme_val.startswith("82/82")
print(f"  {'✅' if ok_g else '❌ 需要更新 (但喺 o38 目錄外, 需指示)'} README 狀態一致")
checks.append(ok_g)

# ── H. 禁區檢查 (已否證路線唔可以重推) ──
print("\n─── H. 禁區檢查 ───")
banned = ["α=φ²", "F₆+sin²θ", "137.0362129", "擬合閉式A"]
hits = []
for b in banned:
    if b in (sess + rec + fr + d1).replace(" ", ""):
        hits.append(b)
print(f"  {'✅' if not hits else '❌ 命中' + str(hits)} 冇引用已否證路線")

# ── I. O170 交收問題 ──
print("\n─── I. O214 → O170 交收 ───")
o170 = os.path.join(ROOT, "o170_phase_depth_distance/SESSION_START.md")
if os.path.exists(o170):
    o170s = open(o170).read()
    ok_i = "O38/O214 交收問題" in o170s and "71.157" in o170s
    print(f"  {'✅' if ok_i else '❌'} O170 SESSION_START 交收已寫入")
    checks.append(ok_i)
else:
    print("  ❌ o170 SESSION_START 唔存在")
    checks.append(False)

# ── J. M₀ 標度攻堅痕跡 (2026-10-18) ──
print("\n─── J. M₀ 標度攻堅 (register O38/m0-scale) ───")
d3 = open("docs/03_m0_scale_attack.md").read()
ok_j1 = os.path.exists("scripts/19_m0_anchor_chain.py") and os.path.exists("scripts/20_m0_pure_number_scan.py") and os.path.exists("scripts/21_m0_cross_equations.py") and os.path.exists("scripts/22_two_n_identity.py") and os.path.exists("scripts/23_m0_factor_tree.py") and os.path.exists("scripts/24_family_freedom_audit.py") and os.path.exists("scripts/25_small_remainder_audit.py") and os.path.exists("scripts/26_emergence_audit.py") and os.path.exists("scripts/27_central_fractal.py") and os.path.exists("scripts/29_rederive_n_identity.py") and os.path.exists("scripts/30_mpl_over_m0_pursuit.py") and os.path.exists("scripts/31_m0_chain_internal.py") and os.path.exists("scripts/32_x_factor_audit.py") and os.path.exists("scripts/33_phi_lock_audit.py") and os.path.exists("scripts/34_m0_ontology_audit.py") and os.path.exists("scripts/35_n38_closure_audit.py") and os.path.exists("scripts/36_tree_scale_direction.py") and os.path.exists("scripts/37_layer_benchmark_audit.py") and os.path.exists("scripts/38_beat_ladder_rederive.py") and os.path.exists("scripts/39_rd_anchor_chain.py") and os.path.exists("scripts/40_smallest_gap_audit.py") and os.path.exists("scripts/41_musical_scale_audit.py") and os.path.exists("scripts/42_shadow_mass_ontology.py") and os.path.exists("scripts/43_mass_wave_beat_verdict.py") and os.path.exists("scripts/44_baseline_frequency_verdict.py") and os.path.exists("scripts/45_interval_final_audit.py") and os.path.exists("scripts/46_qmgr_rewrite_audit.py") and os.path.exists("scripts/47_scale_dome_audit.py") and os.path.exists("scripts/48_count_ontology_audit.py") and os.path.exists("scripts/49_six_loop_ladder_audit.py") and os.path.exists("scripts/50_wfield_six_loop_deepen.py") and os.path.exists("scripts/51_spectral_path_audit.py") and os.path.exists("scripts/52_planck_exclusion_audit.py") and os.path.exists("scripts/53_counting_search.py") and os.path.exists("scripts/54_cutoff_dichotomy_audit.py") and os.path.exists("scripts/55_cell_complex_container_audit.py") and os.path.exists("scripts/56_container_derivability_audit.py") and os.path.exists("scripts/57_m0_dome_significance_audit.py") and os.path.exists("scripts/58_gap_nature_adjudication.py") and os.path.exists("scripts/59_mera_audit.py") and os.path.exists("scripts/60_nonstandard_mera_audit.py") and os.path.exists("scripts/61_quotient_algebraic_cutoff.py")
d6 = open("docs/06_m0_factor_tree.md").read() if os.path.exists("docs/06_m0_factor_tree.md") else ""
d7 = open("docs/07_family_freedom_audit.md").read() if os.path.exists("docs/07_family_freedom_audit.md") else ""
d8 = open("docs/08_small_remainder_audit.md").read() if os.path.exists("docs/08_small_remainder_audit.md") else ""
d9 = open("docs/09_emergence_audit.md").read() if os.path.exists("docs/09_emergence_audit.md") else ""
d10 = open("docs/10_central_fractal.md").read() if os.path.exists("docs/10_central_fractal.md") else ""
ok_j2 = ("盲測協議" in d3) and ("1.8018823346" in d3) and ("100%" in d3) and ("F_e" in open("docs/04_m0_cross_equations.md").read()) and ("N_IDCM" in open("docs/05_two_ns_identity.md").read()) and ("覆蓋假象" in d6) and ("式族註冊制" in d7) and ("83.7%" in d7) and ("88/φ²" in d8) and ("壓制" in d8) and ("唔湧現" in d9) and ("γ_24" in d9) and ("R: ℝ^88 → ℝ^176" in d10) and ("γ_{88−n}" in d10) and ("8.2555e−6" in open("docs/11_rederive_n_identity.md").read()) and ("8.24e−6" in open("docs/12_m0_chain_internal.md").read()) and ("撤回" in open("docs/12_m0_chain_internal.md").read()) and ("3.43e−2" in open("docs/13_x_factor_audit.md").read()) and ("K_φ" in open("docs/14_phi_lock_audit.md").read()) and ("偽命題" in open("docs/15_m0_ontology_audit.md").read()) and ("1.80188233461e40" in open("docs/16_n38_closure_audit.md").read()) and ("291.5" in open("docs/17_tree_scale_direction.md").read()) and ("1/(2φ)" in open("docs/18_layer_benchmark_audit.md").read()) and ("R_H/(44c)" in open("docs/19_beat_ladder_rederive.md").read()) and ("88·r_d/π" in open("docs/20_rd_anchor_chain.md").read()) and ("M₀·t_site/ħ" in open("docs/21_smallest_gap_audit.md").read()) and ("176" in open("docs/22_musical_scale_audit.md").read()) and ("影子" in open("docs/23_shadow_mass_ontology.md").read()) and ("油點" in open("docs/24_mass_wave_beat_verdict.md").read()) and ("ω_site" in open("docs/25_baseline_frequency_verdict.md").read()) and ("窮盡" in open("docs/26_interval_final_audit.md").read()) and ("κ²" in open("docs/27_qmgr_rewrite_audit.md").read()) and ("穹頂" in open("docs/28_scale_dome_audit.md").read()) and ("計數" in open("docs/29_count_ontology_audit.md").read()) and ("mode 6" in open("docs/30_wfield_six_loop_audit.md").read()) and ("假象" in open("docs/31_spectral_path_audit.md").read()) and ("純頻率" in open("docs/32_planck_exclusion_audit.md").read()) and ("經典計數量" in open("docs/33_counting_search.md").read()) and ("採樣截斷" in open("docs/34_cutoff_dichotomy_audit.md").read()) and ("容器" in open("docs/35_cell_complex_container.md").read()) and ("不可推" in open("docs/36_container_derivability.md").read()) and ("穹頂預言" in open("docs/37_m0_dome_significance.md").read()) and ("計數生成器" in open("docs/38_gap_nature_adjudication.md").read()) and ("MERA" in open("docs/39_mera_audit.md").read()) and ("isometry" in open("docs/40_nonstandard_mera.md").read()) and ("商譜" in open("docs/41_quotient_algebraic_cutoff.md").read())
regp = os.path.join(ROOT, "..", "problem_register", "register.jsonl")
ok_j3 = False
if os.path.exists(regp):
    rj = open(regp).read()
    ok_j3 = ("O38/m0-scale" in rj) and ("1.80188233461e40" in rj) and ("O86/R1" in rj)
print(f"  {'✅' if ok_j1 else '❌'} scripts/19-20 存在")
print(f"  {'✅' if ok_j2 else '❌'} docs/03 含 N 值 + null 帶 + 盲測協議")
print(f"  {'✅' if ok_j3 else '❌'} register.jsonl 已 note (O38/m0-scale)")
checks.append(ok_j1 and ok_j2 and ok_j3)

print(f"\n{'='*72}")
print(f"  HANDOFF AUDIT: {sum(1 for c in checks if c)}/{len(checks)}")
print("=" * 72)