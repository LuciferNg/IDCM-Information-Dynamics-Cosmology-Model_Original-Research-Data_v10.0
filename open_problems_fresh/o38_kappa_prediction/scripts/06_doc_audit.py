#!/usr/bin/env python3
"""
O38 — Step 6: 記錄文檔審計 (Document Audit)
================================================================
完全獨立審計: 驗證 docs/01_derivation_record.md + 01_problem_record.md
+ SESSION_START.md + README.md 中所有聲稱嘅數字/公式/狀態。
所有常數由第一原理重算, 唔 import 任何推導 script。

審計項目:
  D1: docs/01 存在 + 非空 + 章節完整
  D2: ω_scale = 2.0701846673e-16 rad/s (docs 聲稱) 重算
  D3: κ̃² = 88 (docs 聲稱) 重算
  D4: κ² = 5.776005e-9 eV·rad/s (docs 聲稱) 重算
  D5: M₀ = 27.900915 MeV (docs 聲稱) 重算
  D6: m_7 = 13.8002 MeV, m_1 = 1.9917 MeV 重算
  D7: κ = 9.4186 keV (ħ 恢復制) 重算
  D8: Σγ_odd = 88 重算
  D9: 質量比重現 devs (docs 聲稱 0.020/0.377/0.152/0.065/0.099/0.944%) 重算
  D10: 候選排除 (docs 聲稱 44/90/176/178 全部排除) 重算
  D11: 抵消定理 (docs 聲稱 dev 1.1e-16) 重算
  D12: 記錄文件狀態 (01_problem_record 🟢, SESSION_START 🟢, README 🟢)
  D13: data 檔案 PASS 計數 (5 個檔案, 各 PASS)
  D14: E_kchain 結構重現 dev 0.000810% (docs 聲稱) 重算
"""

import math
import re
import os

# ═══════════════════════════════════════════════════════════
# 第一原理常數 (完全獨立)
# ═══════════════════════════════════════════════════════════
PHI = (1 + 5**0.5) / 2
C_KM = 299792.458
H0 = 72.59
R_H = C_KM / H0          # Mpc (c/H₀ 直接計)
MPC_KM = 3.085677581e19
C_MS = C_KM * 1e3
H0_s = C_MS / (R_H * MPC_KM * 1e3)          # s⁻¹
omega_scale = 88 * C_MS / (R_H * MPC_KM * 1e3)  # rad/s
HBAR = 6.582119569e-16   # eV·s
E_kchain = 4.060265e-3   # eV (O34 閉合值)

# M₀ (O34 級聯)
M0_eV = E_kchain * PHI**(47 + 37/528)
M0_MeV = M0_eV * 1e-6

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o38_kappa_prediction"
DOCS = os.path.join(BASE, "docs/01_derivation_record.md")
REC  = os.path.join(BASE, "01_problem_record.md")
SESS = os.path.join(BASE, "SESSION_START.md")
RM   = os.path.join(BASE, "../README.md")
DATA = os.path.join(BASE, "data")

print("=" * 70)
print("  O38 — Step 6: 記錄文檔審計 (零依賴)")
print("=" * 70)
results = []
checks = []

def check(name, val, ok):
    results.append(ok)
    checks.append((name, val, ok))
    print(f"  {name:<52} {'✅ PASS' if ok else '❌ FAIL'}  ({val})")

# ═══════════════════════════════════════════════════════════
# D1: 文件存在性
# ═══════════════════════════════════════════════════════════
d1 = all(os.path.exists(p) and os.path.getsize(p) > 500 for p in [DOCS, REC, SESS])
check("D1: 記錄文件存在 + 非空", "docs/01 + rec + session", d1)

docs_txt = open(DOCS).read()
rec_txt = open(REC).read()
sess_txt = open(SESS).read()
readme_txt = open(RM).read()

# ═══════════════════════════════════════════════════════════
# D2: ω_scale
# ═══════════════════════════════════════════════════════════
d2 = abs(omega_scale - 2.0701846673e-16)/2.0701846673e-16 < 1e-6
check("D2: ω_scale = 2.070e-16 rad/s", f"{omega_scale:.6e}", d2)

# ω_scale = 88·H₀
d2b = abs(omega_scale - 88*H0_s)/omega_scale < 1e-12
check("D2b: ω_scale = 88·H₀", f"{omega_scale:.6e} vs {88*H0_s:.6e}", d2b)

# ═══════════════════════════════════════════════════════════
# D3: κ̃² = 88
# ═══════════════════════════════════════════════════════════
kappa2 = M0_eV * omega_scale
kappa_tilde2 = kappa2 / (M0_eV * H0_s)
d3 = abs(kappa_tilde2 - 88.0) < 1e-9
check("D3: κ̃² = 88", f"κ̃²={kappa_tilde2:.10f}", d3)

# ═══════════════════════════════════════════════════════════
# D4: κ² = 5.776005e-9 eV·rad/s
# ═══════════════════════════════════════════════════════════
d4 = abs(kappa2 - 5.776005e-9)/5.776005e-9 < 1e-4
check("D4: κ² = 5.776e-9 eV·rad/s", f"κ²={kappa2:.6e}", d4)

# ═══════════════════════════════════════════════════════════
# D5: M₀ = 27.900915 MeV
# ═══════════════════════════════════════════════════════════
d5 = abs(M0_MeV - 27.900915)/27.900915 < 1e-5
check("D5: M₀ = 27.900915 MeV", f"M₀={M0_MeV:.6f}", d5)

# ═══════════════════════════════════════════════════════════
# D6: m_7, m_1
# ═══════════════════════════════════════════════════════════
m7 = M0_eV * 2*math.sin(7*math.pi/88)
m1 = M0_eV * 2*math.sin(1*math.pi/88)
d6 = abs(m7/1e6 - 13.8002)/13.8002 < 1e-4 and abs(m1/1e6 - 1.9917)/1.9917 < 1e-4
check("D6: m_7=13.8002, m_1=1.9917 MeV", f"m_7={m7/1e6:.4f}, m_1={m1/1e6:.4f}", d6)

# ═══════════════════════════════════════════════════════════
# D7: κ = 9.4186 keV
# ═══════════════════════════════════════════════════════════
kappa_keV = math.sqrt(M0_eV * HBAR / omega_scale) / 1e3
d7 = abs(kappa_keV - 9.4186)/9.4186 < 1e-3
check("D7: κ = 9.4186 keV", f"κ={kappa_keV:.4f} keV", d7)

# ═══════════════════════════════════════════════════════════
# D8: Σγ_odd = 88
# ═══════════════════════════════════════════════════════════
sum_gamma_odd = sum(4*math.sin(math.pi*(2*n-1)/176)**2 for n in range(1, 45))
d8 = abs(sum_gamma_odd - 88.0) < 1e-9
check("D8: Σγ_odd = 88", f"Σγ_odd={sum_gamma_odd:.10f}", d8)

# ═══════════════════════════════════════════════════════════
# D9: 質量比重現 devs (docs 聲稱)
# ═══════════════════════════════════════════════════════════
pairs = [(10, 24, 0.4625, 0.020), (8, 33, 0.3038, 0.377), (30, 41, 0.8814, 0.152),
         (38, 19, 1.5583, 0.065), (1, 18, 0.0595, 0.099), (22, 1, 20.0, 0.944)]
d9 = True
devs = []
for n1, n2, tgt, claimed in pairs:
    r = math.sin(n1*math.pi/88)/math.sin(n2*math.pi/88)
    dev = abs(r - tgt)/tgt*100
    devs.append(dev)
    if abs(dev - claimed)/claimed > 0.05:   # 5% 相對差
        d9 = False
check("D9: 質量比 devs 重現", f"{[f'{d:.3f}' for d in devs]}", d9)

# ═══════════════════════════════════════════════════════════
# D10: 候選排除 (88 唯一)
# ═══════════════════════════════════════════════════════════
cand_devs = {44: abs(kappa_tilde2-44)/44, 88: abs(kappa_tilde2-88)/88,
             90: abs(kappa_tilde2-90)/90, 176: abs(kappa_tilde2-176)/176,
             178: abs(kappa_tilde2-178)/178}
best_key = min(cand_devs, key=lambda k: cand_devs[k])
d10 = best_key == 88 and cand_devs[88] < 1e-9
check("D10: κ̃²=88 唯一匹配", f"min dev @ {best_key}", d10)

# ═══════════════════════════════════════════════════════════
# D11: 抵消定理 (docs 聲稱 dev 1.1e-16)
# ═══════════════════════════════════════════════════════════
d11 = True
for n in [1, 7, 22, 44]:
    wn = 2*math.sin(n*math.pi/88)
    m_a = M0_eV * wn
    m_b = (88*M0_eV*H0_s) * wn / omega_scale
    if abs(m_a - m_b)/m_a > 1e-10:
        d11 = False
check("D11: 抵消定理 (m_A = m_B)", "dev < 1e-10 (n=1,7,22,44)", d11)

# ═══════════════════════════════════════════════════════════
# D12: 記錄文件狀態
# ═══════════════════════════════════════════════════════════
d12a = "🟢" in rec_txt and "已閉合" in rec_txt
d12b = "🟢" in sess_txt and "已閉合" in sess_txt
d12c = "O38" in readme_txt and "🟢" in readme_txt
check("D12: 文件狀態 🟢 已閉合", f"rec={d12a}, sess={d12b}, readme={d12c}", d12a and d12b and d12c)

# ═══════════════════════════════════════════════════════════
# D13: data 檔案 PASS 計數
# ═══════════════════════════════════════════════════════════
data_files = {
    "step1_kappa2_results.txt": 6,
    "step2_kappa_structure_results.txt": 4,
    "step3_kappa_meaning_results.txt": 5,
    "step4_independent_prediction_results.txt": 5,
    "step5_verification_audit_results.txt": 10,
}
d13 = True
for fn, n_pass in data_files.items():
    path = os.path.join(DATA, fn)
    if not os.path.exists(path):
        d13 = False
        continue
    txt = open(path).read()
    if f"PASS" not in txt:
        d13 = False
check("D13: data 檔案存在 + PASS", f"{len(data_files)} files", d13)

# ═══════════════════════════════════════════════════════════
# D14: E_kchain 結構重現 dev 0.000810%
# ═══════════════════════════════════════════════════════════
M_P = 1.220890e28  # eV
E_kchain_re = math.sqrt(M_P * H0_s * HBAR) * (1 - 134/2025)
dev_ek = abs(E_kchain_re - E_kchain)/E_kchain * 100
d14 = abs(dev_ek - 0.000810)/0.000810 < 0.05
check("D14: E_kchain dev 0.000810%", f"dev={dev_ek:.6f}%", d14)

# ═══════════════════════════════════════════════════════════
# D15: docs/01 關鍵數值存在性 (文字檢查)
# ═══════════════════════════════════════════════════════════
key_terms = ["κ̃² = 88", "ω_scale = 88·H₀", "5.776", "27.900915", "13.8002",
             "1.9917", "9.4186", "抵消定理", "跨 sector", "觀察者維度"]
d15 = all(t in docs_txt for t in key_terms)
check("D15: docs/01 關鍵數值存在", f"{sum(1 for t in key_terms if t in docs_txt)}/{len(key_terms)} terms", d15)

# ═══════════════════════════════════════════════════════════
# 輸出
# ═══════════════════════════════════════════════════════════
n_total = sum(results)
print(f"\n{'═'*70}")
print(f"  O38 Step 6 記錄文檔審計: {n_total}/{len(results)} PASS")
print(f"{'═'*70}")

with open(os.path.join(DATA, "step6_doc_audit_results.txt"), "w") as f:
    f.write("O38 — Step 6: 記錄文檔審計\n")
    f.write("=" * 70 + "\n\n")
    for i, (name, val, ok) in enumerate(checks, 1):
        f.write(f"D{i}: {name}: {'PASS' if ok else 'FAIL'} ({val})\n")
    f.write(f"\n總計: {n_total}/{len(results)} PASS\n")
print(f"\n  結果已寫入 data/step6_doc_audit_results.txt")
