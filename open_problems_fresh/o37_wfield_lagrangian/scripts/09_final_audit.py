#!/usr/bin/env python3
"""
O37 — Step 9: 最終整合驗證 (Final Integration Audit)
======================================================
目標: 驗證本 session 全部推導、計算、驗證結果正確寫入記錄文檔,
      + 全部 scripts 重跑 + 檔案完整性 + 公式交叉核對!

驗證:
  [1] scripts 01-08 全部重跑 PASS
  [2] docs/01_derivation_record.md 存在 + 包含關鍵閉合
  [3] 01_problem_record.md 已更新 (🟢 閉合)
  [4] SESSION_START.md 已更新
  [5] data/ 檔案齊全 (8 個結果檔案)
  [6] 核心公式數值核對 (M₀, ⟨W⟩, m_δW, κ_eff)
  [7] 總計 PASS 數
"""

import os, re, subprocess, sys

print("=" * 70)
print("  O37 — Step 9: 最終整合驗證")
print("=" * 70)
results = []

# ═══════════════════════════════════════════════════════════════
# [1] scripts 01-08 重跑
# ═══════════════════════════════════════════════════════════════
print("\n─── [1] scripts 01-08 重跑 ───")
scripts = [
    "01_wfield_type", "02_condensate_potential", "03_lagrangian_source",
    "04_sm_higgs", "05_verification_audit", "06_file_verifier",
    "07_sympy_verification", "08_legacy_closure",
]
total_pass = 0
total_tests = 0
all_ok = True
for s in scripts:
    out = subprocess.run([sys.executable, f"scripts/{s}.py"], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__))+"/..")
    m = re.search(r"結果: (\d+)/(\d+) PASS", out.stdout)
    if m:
        p, t = int(m.group(1)), int(m.group(2))
        total_pass += p
        total_tests += t
        ok = p == t
        all_ok &= ok
        print(f"  {s}: {p}/{t} PASS {'✅' if ok else '❌'}")
    else:
        all_ok = False
        print(f"  {s}: ❌ 執行失敗")
        print(out.stderr[-500:])
print(f"  總計: {total_pass}/{total_tests} PASS")
results.append(("R1 scripts 全 PASS", all_ok))

# ═══════════════════════════════════════════════════════════════
# [2] docs/01 完整性
# ═══════════════════════════════════════════════════════════════
print("\n─── [2] docs/01_derivation_record.md 完整性 ───")
base = os.path.dirname(os.path.abspath(__file__)) + "/.."
doc = open(f"{base}/docs/01_derivation_record.md").read()
key_items = [
    "L_W = (∂_μW)²/2 − 2|W|² + ((φ⁴−1)/4)|W|⁴",
    "V(W) = −μ²|W|² + λ|W|⁴",
    "⟨W⟩² = Ω_Λ",
    "g_n = κ·ω_n",
    "μ² = Σγ_even − Σγ_odd",
    "三合一",
    "q² 型耦合排除",
    "real scalar",
    "M₀·√2 = 39.46 MeV",
    "Σγ = 90 閉合形式證明",
    "ΔE_n = −g_n²/ω_n = −κ²ω_n",
    "倍頻陷阱",
    "m_δW = 2M₀√κ",
    "κ_eff_E = 2λM₀/√90",
    "sympy 精確代數",
    "degree 論證",
    "λ_B/λ_C = 90(1 + λ_B·fib)",
    "√123/8",
    "DM = W 凝聚漲落",
]
missing = [k for k in key_items if k not in doc]
print(f"  關鍵內容 {len(key_items)-len(missing)}/{len(key_items)} 有寫入")
if missing:
    print(f"  ❌ 缺失: {missing}")
ok_doc = len(missing) == 0
results.append(("R2 docs/01 完整", ok_doc))

# ═══════════════════════════════════════════════════════════════
# [3] 01_problem_record.md 已更新
# ═══════════════════════════════════════════════════════════════
print("\n─── [3] 01_problem_record.md 狀態 ───")
pr = open(f"{base}/01_problem_record.md").read()
ok_pr = "🟢 **已閉合**" in pr and ("63/63" in pr or "47/47" in pr)
print(f"  已閉合標記: {'✅' if ok_pr else '❌'}")
results.append(("R3 problem_record 更新", ok_pr))

# ═══════════════════════════════════════════════════════════════
# [4] SESSION_START.md 已更新
# ═══════════════════════════════════════════════════════════════
print("\n─── [4] SESSION_START.md 狀態 ───")
ss = open(f"{base}/SESSION_START.md").read()
ok_ss = "🟢 **已閉合**" in ss and "g_n = κ·ω_n" in ss
print(f"  已閉合標記: {'✅' if ok_ss else '❌'}")
results.append(("R4 SESSION_START 更新", ok_ss))

# ═══════════════════════════════════════════════════════════════
# [5] data/ 檔案齊全
# ═══════════════════════════════════════════════════════════════
print("\n─── [5] data/ 檔案齊全 ───")
expected_data = [f"step{i}_results.txt" for i in range(1, 9)]
# 實際名稱
expected_names = [
    "step1_wfield_type_results.txt",
    "step2_condensate_potential_results.txt",
    "step3_lagrangian_source_results.txt",
    "step4_sm_higgs_results.txt",
    "step5_verification_audit_results.txt",
    "step6_file_verifier_results.txt",
    "step7_sympy_verification_results.txt",
    "step8_legacy_closure_results.txt",
]
all_data = True
for fname in expected_names:
    exists = os.path.exists(f"{base}/data/{fname}")
    all_data &= exists
    print(f"  {fname}: {'✅' if exists else '❌'}")
results.append(("R5 data 齊全", all_data))

# ═══════════════════════════════════════════════════════════════
# [6] 核心數值核對 (獨立重算)
# ═══════════════════════════════════════════════════════════════
print("\n─── [6] 核心數值核對 (mpmath 獨立) ───")
from mpmath import mp, mpf, sin, sqrt, pi
mp.dps = 40
phi = (1+sqrt(5))/2
E_kchain = mpf('4.060265e-3')
M0 = E_kchain * phi**(mpf(47) + mpf(37)/mpf(528))
M0_MeV = float(M0)*1e-6
print(f"  M₀ = {M0_MeV:.6f} MeV (期望 27.9009)")
ok_m0 = abs(M0_MeV - 27.9009)/27.9009 < 1e-4

m_dW = M0_MeV/2
print(f"  m_δW = M₀/2 = {m_dW:.4f} MeV")
ok_mdw = abs(m_dW - 13.9505)/13.9505 < 1e-3

kappa_eff = 2*(1/32)*M0_MeV/sqrt(90)
print(f"  κ_eff_E = 2λM₀/√90 = {float(kappa_eff):.6f} MeV")
ok_keff = abs(float(kappa_eff) - 0.183813)/0.183813 < 1e-3

sum_gamma = sum(4*sin(mpf(n)*pi/mpf(88))**2 for n in range(1, 45))
print(f"  Σγ = {float(sum_gamma):.1f} (期望 90)")
ok_gamma = abs(float(sum_gamma) - 90) < 1e-10
results.append(("R6 核心數值", ok_m0 and ok_mdw and ok_keff and ok_gamma))

# ═══════════════════════════════════════════════════════════════
# [7] 總計
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*70}")
print(f"  O37 Step 9 結果: {sum(ok for _, ok in results)}/{len(results)} PASS")
for name, ok in results:
    print(f"  {name}: {'✅' if ok else '❌'}")
print(f"  全部 scripts 總計: {total_pass}/{total_tests} PASS")
print(f"{'═'*70}")

with open(f"{base}/data/step9_final_audit_results.txt", "w") as f:
    f.write("O37 — Step 9: 最終整合驗證\n")
    f.write("=" * 70 + "\n\n")
    for name, ok in results:
        f.write(f"  {name}: {'PASS' if ok else 'FAIL'}\n")
    f.write(f"\n全部 scripts 總計: {total_pass}/{total_tests} PASS\n")
print(f"\n  結果已寫入 data/step9_final_audit_results.txt")
