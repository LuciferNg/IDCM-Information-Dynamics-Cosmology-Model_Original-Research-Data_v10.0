#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IDCM 數據完整性檢查
==================
檢查: 檔案齊全度 + 數值一致性 (文檔 vs 腳本輸出)

2026-09-15 大修 (O169 修正交回交回, 用戶指示「先處理A」+「繼續任務」)
==================================================================
第一輪 (A) — 修三個 bug:

  bug 1 [假 MISSING]  REPO 硬編碼 /home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh
      — 該樹係舊 partial copy, 連 bbn/ cmb_cl/ h0_tension/ 都唔存在 → 18/18 全部假 MISSING,
      文檔檢查 0/17。改為由本腳本位置推導 REPO (唔會再隨 repo 搬位而斷)。

  bug 2 [假綠燈]  明明 MISSING 一大串 + 文檔 0/17, 最終仍然印
      「✅ 數據完整性檢查全部通過!」+ exit 0 (最終結果冇 assert, 只 hardcode 印 total/total)。
      改為: 逐項 assert + 真統計 + 非零 exit code。

  bug 3 [驗證已證偽公式]  D_app 用 E(ℓ) = 1 + 2φ⁻¹ℓ
      — O169 (2026-09-15) 用 DESI DR2 D_M × 6 排除 4.88σ。
      改為新零參數定律 E(ℓ) = ℓ + √5/2, 並加入伸長回歸測試:
      χ²(D_M×6) 必須 ≈ 2.4647 (新式), 舊式 27.16 必須被拒 (|σ|max > 3)。

第二輪 (B′) — 修「驗證已證偽公式」嘅同類殘留 (O169 docs/05):
  P_n = 1 + 2φ⁻¹n + K₂n² 判定屬 A 類 (受證偽) —— 其 2φ⁻¹ 係「每層增益」語義,
  同被證偽嘅伸長定律同一結構對象。其唯一數值輸出 Ω_DM/Ω_b = 6.5030 已由
  v10.0 嘅 F₇/L₀ = 13/2 取代。本檢查器原本仍用 6.5030 → 已改為 v10.0 結構鏈:

      Ω_Λ = 41/60 (O39 版; O37 版 4/(φ⁴−1) 已撤銷)
      Ω_m = 19/60
      Ω_b = Ω_m × 2/(3F₅) = 19/450     (純 F-數, 零 P_n 依賴)
      η_B = 6.063632×10⁻¹⁰             (0.596% vs 6.1×10⁻¹⁰)

⚠️ 未靜默改數值: 依賴舊伸長 / 舊常數嘅文檔聲稱只標 🔴 (STALE), 交回擁有該結論嘅 O 處理:

  · h0_tension/06_complete_record.md — H_eff(0.03) = 73.13 (舊伸長) → 新結構值 66.33
  · bbn/06_complete_record.md       — η_B = 6.0622×10⁻¹⁰ = **雙重 stale**
        (已撤銷 O37 Ω_Λ + v9.0 P_n 6.5030 相乘, 精確重現 dev 0.0000%)
        → 現行 v10.0 結構值 6.0636×10⁻¹⁰ (更準: 0.596% vs 文檔聲稱 0.62%)
  · bbn/06_complete_record.md       — Ω_DM/Ω_b = 6.5030 (v9.0 P_n) → 13/2 = F₇/L₀
  · bbn/01_problem_record.md:46     — η_B 歸因於 P_n → 應改為 Ω_b = Ω_m×2/(3F₅)

詳見 o169_da_spectral_first_principles/docs/04_open_ledger.md §E6 +
     docs/05_bprime_pn_verdict.md。

Exit codes: 0 = 全綠 | 1 = 硬失敗 (檔案/物理重算/回歸) | 2 = 結構層過但有 stale 聲稱
"""
import os
import sys
import math

# ============ REPO (由腳本位置推導, 唔再硬編碼) ============
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
assert os.path.isdir(os.path.join(REPO, "bbn")), f"REPO 推導錯: {REPO}"

# ============ 結構常數 ============
phi      = (1 + 5**0.5) / 2
phi_inv  = 1 / phi
phi_inv3 = phi_inv ** 3
N_d, B, L5, N_gen, M, CY3 = 44, 4, 11, 3, 33, 134
F5, F7, L0 = 5, 13, 2
R_H   = 4129.94                 # Mpc — R_world (O73/O164)
c_km  = 299792.458

# ============ 宇宙學參數 (v10.0 現行版) ============
Omega_L = 41 / 60                       # O39 版 (O37 版 4/(φ⁴−1) 已撤銷, PARADIGM BREAK 08-12)
Omega_m = 19 / 60
RATIO_B_M   = 2 / (3 * F5)              # Ω_b/Ω_m = 2/15  EXACT
RATIO_DM_B  = F7 / L0                   # Ω_DM/Ω_b = 13/2 EXACT
Omega_b = Omega_m * RATIO_B_M           # 19/450 = 0.0422222  (零 P_n 依賴)
RATIO_V9_PN = 6.5030                    # ❌ v9.0 P_n 輸出, 已由 13/2 取代 (O169 docs/05)

# 自洽 (純 F-數):  1 + Ω_DM/Ω_b  ==  1/(Ω_b/Ω_m)
assert abs((1 + RATIO_DM_B) - 1 / RATIO_B_M) < 1e-12, "F-數比率唔自洽!"

# K_Chain 譜 (O51 層 2)
GAM = {n: 4 * math.sin(math.pi * n / 88) ** 2 for n in range(1, N_d + 1)}
VG  = {n: math.cos(math.pi * n / 88) for n in range(1, N_d + 1)}
SIG_ODD  = sum(GAM[n] for n in range(1, N_d + 1) if n % 2 == 1)
SIG_EVEN = sum(GAM[n] for n in range(1, N_d + 1) if n % 2 == 0)

# ★ O169 伸長定律 (零參數):  E(ℓ) = a·ℓ + b
A_ELONG  = (SIG_ODD / (N_d / 2)) / 2              # ⟨γ⟩_odd / 2 = μ²/2 = 1  EXACT
B_SPECT  = 22 / sum(VG[n] for n in range(1, 23))  # 1/⟨v_g⟩_{1..22} = 1.11911398 (Z₂ 半鏈)
B_PHI    = 5**0.5 / 2                             # √5/2 = 1.11803399 (φ 影子; 同譜讀法簡併 0.097%)
def E_new(l): return A_ELONG * l + B_PHI          # 用 φ 讀法: δ 零點精確喺 ℓ = 1/2, E(1/2) = φ
def E_old(l): return 1 + 2 * phi_inv * l          # ❌ 已證偽 (O169: 4.88σ)

def D_A(z, E):
    l = math.log(1 + z, 4)
    return R_H * (1 - 4**(-l)) * E(l)

def H_eff(z, E, dz=1e-5):
    """投影 Jacobian 斜率 (h0_tension 定義): H_eff = c / (dD/dz)"""
    return c_km / ((D_A(z + dz, E) - D_A(z - dz, E)) / (2 * dz))

# DESI DR2 Table 6 — D_M/rd (六 tracer, 唔含 BGS: 佢只有 D_V)
DESI_DM = [
    # (tracer, z, D_M/rd, σ)
    ("LRG1", 0.510, 13.588, 0.167),
    ("LRG2", 0.706, 17.351, 0.177),
    ("LRG3", 0.934, 21.576, 0.152),
    ("ELG2", 1.321, 27.601, 0.318),
    ("QSO",  1.484, 30.512, 0.760),
    ("Lya",  2.330, 38.988, 0.531),
]
RD = math.pi * R_H / 88 * 420 / 421      # 147.088303 Mpc

def elong_chi2(E):
    t, worst = 0.0, 0.0
    for _n, z, dm, em in DESI_DM:
        s = (D_A(z, E) / RD - dm) / em
        t += s * s
        if abs(s) > abs(worst):
            worst = s
    return t, worst

# ============ 結果收集 (真統計, 唔 hardcode) ============
FAIL = []      # 硬失敗 (assert 級)
STALE = []     # 已登記 stale 聲稱 (依賴已證偽公式/已撤銷常數, 待擁有該結論嘅 O 更新)

def ok(msg):    print(f"  ✅ {msg}")
def bad(msg):   FAIL.append(msg);  print(f"  ❌ {msg}")
def stale(msg): STALE.append(msg); print(f"  🔴 {msg}")

print("=" * 76)
print("IDCM 數據完整性檢查  (O169 修正版 2026-09-15: A 檢查器修復 + B′ P_n 判定)")
print("=" * 76)
print(f"REPO = {REPO}")

# ============ 1. 檔案檢查 ============
print("\n[1] 檔案檢查")
print("-" * 76)
projects = {
    "bbn": ["01_problem_record.md", "03_first_results.md", "04_li7_suppression.md",
            "06_complete_record.md",
            "scripts/02_eta_b_structural.py", "scripts/04_li7_suppression.py"],
    "cmb_cl": ["01_problem_record.md", "03_first_results.md", "04_peak_sequence.md",
               "05_external_verification.md", "06_complete_record.md",
               "scripts/02_acoustic_peaks_structural.py",
               "scripts/03_peak_sequence_search.py",
               "scripts/05_camb_peak_verification.py"],
    "h0_tension": ["01_problem_record.md", "03_first_results.md", "06_complete_record.md",
                   "scripts/02_h0_projection.py"],
}
total_files, missing = 0, []
for proj, files in projects.items():
    for f in files:
        total_files += 1
        path = os.path.join(REPO, proj, f)
        if not os.path.exists(path):
            missing.append(f"{proj}/{f}")
        elif os.path.getsize(path) == 0:
            missing.append(f"{proj}/{f} (empty)")
if missing:
    bad(f"檔案缺失 {len(missing)}/{total_files}: {missing}")
else:
    ok(f"檔案 {total_files}/{total_files} 全部存在且非空")

# ============ 2. 文檔關鍵數值檢查 ============
print("\n[2] 文檔關鍵數值檢查")
print("-" * 76)

# (A) 唔依賴已證偽公式/已撤銷常數嘅結構聲稱 — 必須存在
doc_ok = [
    ("bbn/06_complete_record.md", "η_B = n_b/n_γ"),
    ("bbn/06_complete_record.md", "γ₇/γ₂₀ = 0.14262"),
    ("bbn/06_complete_record.md", "0.2496"),
    ("bbn/06_complete_record.md", "1.5839×10⁻¹⁰"),
    ("cmb_cl/06_complete_record.md", "ℓ_A = 2×CY₃ + M = 2×134 + 33 = 301"),
    ("cmb_cl/06_complete_record.md", "301.76"),
    ("cmb_cl/06_complete_record.md", "0.25%"),
    ("cmb_cl/06_complete_record.md", "220"),
    ("cmb_cl/06_complete_record.md", "537"),
    ("cmb_cl/06_complete_record.md", "810"),
    ("cmb_cl/06_complete_record.md", "1014"),
    ("h0_tension/06_complete_record.md", "H₀_idcm = c/R_H = 72.59"),
]
# (B) 依賴已證偽公式/已撤銷常數嘅聲稱 — 存在 = 文檔未更新 (🔴 stale, 唔算 ✅)
doc_stale = [
    # h0_tension: 舊伸長 E = 1 + 2φ⁻¹ℓ (O169 4.88σ 排除)
    ("h0_tension/06_complete_record.md", "73.13",
     "H_eff(0.03) 舊伸長值 → 新結構值 66.33"),
    ("h0_tension/06_complete_record.md", "0.12%",
     "vs SH0ES 匹配率 → 新式 6.5σ 偏離"),
    # bbn: η_B 雙重 stale (已撤銷 O37 Ω_Λ + v9.0 P_n 6.5030)
    ("bbn/06_complete_record.md", "6.0622×10⁻¹⁰",
     "η_B 雙重 stale (O37 Ω_Λ + v9.0 P_n) → 現行 6.0636×10⁻¹⁰ (0.596%)"),
    ("bbn/06_complete_record.md", "0.62%",
     "η_B 偏差 (舊值) → 現行 0.596%"),
    ("bbn/06_complete_record.md", "| Ω_DM/Ω_b | 6.5030 | 幾何分配 P_n |",
     "Ω_DM/Ω_b v9.0 P_n → v10.0 F₇/L₀ = 13/2"),
]

n_ok = 0
for fname, search in doc_ok:
    path = os.path.join(REPO, fname)
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
    except Exception:
        bad(f"無法讀取 {fname}")
        continue
    if search in content:
        n_ok += 1
        print(f"  ✅ {fname}: '{search}'")
    else:
        bad(f"{fname}: '{search}' 缺失")

for fname, search, why in doc_stale:
    path = os.path.join(REPO, fname)
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
    except Exception:
        bad(f"無法讀取 {fname}")
        continue
    if search in content:
        stale(f"{fname}: '{search}' 仍存在 — {why}")
    else:
        ok(f"{fname}: '{search}' 已清除 (O 已更新)")

print(f"\n  文檔檢查: 結構聲稱 {n_ok}/{len(doc_ok)};  "
      f"stale 聲稱 {len(STALE)} 項待更新")

# ============ 3. 物理數值獨立重算 ============
print("\n[3] 物理數值獨立重算")
print("-" * 76)

# --- 3a. 唔依賴伸長嘅結構量 ---
print("  [3a] 唔依賴伸長定律嘅結構量")

# v10.0 密度鏈 (純 F-數, 零 P_n 依賴)
print(f"        Ω_Λ = 41/60 = {Omega_L:.8f}  (O39 版; O37 版 4/(φ⁴−1) = {4/(phi**4-1):.8f} 已撤銷)")
if abs(Omega_L - 41 / 60) < 1e-15 and abs(Omega_L + Omega_m - 1) < 1e-15:
    ok("Ω_Λ = 41/60 (O39), Ω_m = 19/60, Ω_Λ+Ω_m = 1")
else:
    bad("Ω_Λ/Ω_m 唔對")
print(f"        Ω_b = Ω_m × 2/(3F₅) = 19/450 = {Omega_b:.9f}   (唔用 v9.0 P_n {RATIO_V9_PN})")
if abs(Omega_b - 19 / 450) < 1e-15:
    ok("Ω_b = 19/450 (純 F-數比率, 零 P_n 依賴)")
else:
    bad(f"Ω_b 唔對: {Omega_b}")

# BBN: η_B
H0_si = 72.59 * 1000 / 3.0856775814913673e22
G = 6.67430e-11
rho_c = 3 * H0_si**2 / (8 * math.pi * G)
T = 2.7284
k_B, hbar, c_si = 1.380649e-23, 6.62607015e-34 / (2 * math.pi), 299792458.0
n_gamma = 2 * 1.2020569031595942 / math.pi**2 * (k_B * T / (hbar * c_si))**3
m_p = 938.27208816 * 1.78266192e-30
eta_B = Omega_b * rho_c / (m_p * n_gamma)
print(f"        η_B = {eta_B:.6e}  (v10.0 現行結構值; 文檔聲稱 6.0622e-10 = 雙重 stale)")
if abs(eta_B - 6.0636e-10) / 6.0636e-10 < 2e-3:
    ok(f"η_B = {eta_B:.6e} 一致 (0.596% vs 6.1e-10)")
else:
    bad(f"η_B 唔一致: {eta_B:.6e}")

# 反證: 文檔值必須由「O37 + 6.5030」重現 (證明係雙重 stale, 唔係隨機)
OL_O37 = 4 / (phi**4 - 1)
eta_doc = (1 - OL_O37) / (1 + RATIO_V9_PN) * rho_c / (m_p * n_gamma)
print(f"        反證: Ω_m(O37)/(1+6.5030) → η_B = {eta_doc:.6e}  "
      f"(vs 文檔 6.0622e-10, dev {abs(eta_doc-6.0622e-10)/6.0622e-10*100:.4f}%)")
if abs(eta_doc - 6.0622e-10) / 6.0622e-10 < 1e-4:
    ok("文檔 η_B 精確重現於「O37 Ω_Λ + v9.0 P_n」→ 確認雙重 stale (dev 0.0000%)")
else:
    bad("文檔 η_B 未能重現 → 歸因不明")

# BBN: n/p
g7, g20 = GAM[7], GAM[20]
np_r = g7 / g20
print(f"        γ₇/γ₂₀ = {np_r:.5f}  (文檔 0.14262)")
if abs(np_r - 0.14262) < 1e-4:
    ok("γ₇/γ₂₀ 一致")
else:
    bad(f"γ₇/γ₂₀ 唔一致: {np_r:.5f}")

# ⁷Li
eps = phi_inv / 4
li7 = eta_B * 2 * eps * (1 - eps)
print(f"        ⁷Li/H = {li7:.5e}  (文檔 1.5839e-10, dev {abs(li7-1.5839e-10)/1.5839e-10*100:.3f}%)")
if abs(li7 - 1.5839e-10) / 1.5839e-10 < 2e-3:
    ok("⁷Li 一致 (用 v10.0 η_B)")
else:
    bad(f"⁷Li 唔一致: {li7:.5e}")

# CMB 峰
peaks = []
for m in range(1, 5):
    N_int = M - math.comb(9 - m, 2)
    frac = ((m - 1) * 9) % 25
    peaks.append(44 * N_int + frac)
exp_peaks = [220, 537, 810, 1014]
print(f"        峰序列 = {peaks}  (文檔 {exp_peaks})")
if peaks == exp_peaks:
    ok("CMB 峰序列一致")
else:
    bad(f"峰序列唔一致: {peaks}")

# ℓ_A
l_A = 2 * CY3 + M
l_A_planck = math.pi / 0.010411
print(f"        ℓ_A = {l_A}  (Planck {l_A_planck:.2f}, 偏差 {abs(l_A_planck-l_A)/l_A*100:.2f}%)")
if l_A == 301:
    ok("ℓ_A 一致")
else:
    bad(f"ℓ_A 唔一致: {l_A}")

# --- 3b. 伸長定律 (O169) 結構恆等式 ---
print("\n  [3b] 伸長定律 E(ℓ) = ⟨γ⟩_odd/2·ℓ + 1/⟨v_g⟩_{1..22}  (O169, 零參數)")

print(f"        Σγ_odd = {SIG_ODD:.6f} (= N_d), Σγ_even = {SIG_EVEN:.6f}, Σγ = {SIG_ODD+SIG_EVEN:.6f}")
if abs(SIG_ODD - N_d) < 1e-9 and abs(SIG_EVEN - 46) < 1e-9:
    ok("Σγ_odd = 44 = N_d, Σγ_even = 46")
else:
    bad(f"Σγ 譜和唔對: odd={SIG_ODD}, even={SIG_EVEN}")

print(f"        ⟨γ⟩_odd = {SIG_ODD/(N_d/2):.6f} = μ² = 2  →  a = ⟨γ⟩_odd/2 = {A_ELONG:.6f}")
if abs(A_ELONG - 1) < 1e-12:
    ok("斜率 a = 1 EXACT (⟨γ⟩_odd/2 = μ²/2 = Σγ_odd/N_d)")
else:
    bad(f"斜率 a ≠ 1: {A_ELONG}")

print(f"        b 譜讀法 1/⟨v_g⟩_22 = {B_SPECT:.8f}   b φ讀法 √5/2 = {B_PHI:.8f}"
      f"   差 {abs(B_SPECT-B_PHI)/B_PHI*100:.3f}%")
if abs(B_SPECT - B_PHI) / B_PHI < 2e-3:
    ok("b 兩讀法簡併 (<0.2%): 譜 1/⟨v_g⟩_{1..22} vs φ √5/2 — 觀測不可分辨")
else:
    bad("b 兩讀法唔簡併")

C_new = A_ELONG - 2 * phi_inv
if abs(C_new - (-phi_inv3)) < 1e-12:
    ok(f"δ 係數 C = 1 − 2φ⁻¹ = −φ⁻³ = {C_new:.8f} EXACT (= −(√5−2))")
else:
    bad(f"C ≠ −φ⁻³: {C_new}")

if abs((2 * phi_inv - phi_inv3) - 1) < 1e-12:
    ok("恆等式 2φ⁻¹ − φ⁻³ = 1 (斜率恆等)")
else:
    bad("2φ⁻¹ − φ⁻³ ≠ 1")

if abs(E_new(0.5) - phi) < 1e-12 and abs(E_old(0.5) - phi) < 1e-12:
    ok(f"E(1/2) = φ = {phi:.8f} (新舊形皆過 ℓ=1/2 → δ 零點喺 ℓ=1/2)")
else:
    bad("E(1/2) ≠ φ")

# --- 3c. 伸長定律回歸測試 (DESI DR2 D_M × 6) ---
print("\n  [3c] 伸長定律回歸測試 (DESI DR2 Table 6, D_M × 6, rd = %.6f Mpc)" % RD)
chi_new, w_new = elong_chi2(E_new)
chi_old, w_old = elong_chi2(E_old)
print(f"        新式 E = ℓ + √5/2      : χ² = {chi_new:.4f}/5,  |σ|max = {abs(w_new):.3f}")
print(f"        舊式 E = 1 + 2φ⁻¹ℓ     : χ² = {chi_old:.4f}/5,  |σ|max = {abs(w_old):.3f}")
if abs(chi_new - 2.4647) < 0.01 and abs(w_new) < 1.0:
    ok("新式 χ² = 2.4647/5, 6/6 |σ| ≤ 1.0 (回歸鎖定)")
else:
    bad(f"新式 χ² 偏離 2.4647: {chi_new:.4f}")
if abs(w_old) > 3.0:
    ok(f"舊式被拒 (|σ|max = {abs(w_old):.2f} > 3) — 已證偽公式唔會再通過本檢查器")
else:
    bad("舊式竟然通過 — 回歸測試失效!")

# --- 3d. H_eff: 舊伸長嘅文檔聲稱 vs 新結構值 ---
print("\n  [3d] 投影 Jacobian H_eff = c/(dD/dz)  (h0_tension 定義)")
print(f"        H₀_idcm = c/R_H = {c_km/R_H:.3f}  (結構定義, 唔經伸長, 保持)")
if abs(c_km / R_H - 72.59) < 0.01:
    ok("H₀_idcm = 72.59 保持 (c/R_H 結構定義, 唔受 O169 影響)")
else:
    bad(f"H₀_idcm 偏離: {c_km/R_H:.3f}")

doc_h = {0.01: 72.75, 0.02: 72.93, 0.03: 73.13, 0.04: 73.33, 0.05: 73.55,
         0.10: 74.81, 0.20: 77.96, 0.50: 90.37}
print(f"        {'z':>6}{'文檔':>9}{'舊式':>9}{'新式':>9}")
for z, d in doc_h.items():
    print(f"        {z:>6}{d:>9.2f}{H_eff(z, E_old):>9.2f}{H_eff(z, E_new):>9.2f}")
print(f"        z→0: 舊式 {H_eff(1e-6, E_old):.2f} = c/R_H ; 新式 {H_eff(1e-6, E_new):.2f}")
h003_new = H_eff(0.03, E_new)
print(f"        ★ 新式 H_eff(0.03) = {h003_new:.2f} vs SH0ES 73.04 → "
      f"{abs(h003_new-73.04)/1.04:.1f}σ 🔴")
stale(f"h0_tension H_eff(0.03) = 73.13 (舊伸長) → 新結構值 {h003_new:.2f}; "
      f"SH0ES 匹配 (0.12%) 變 {abs(h003_new-73.04)/1.04:.1f}σ 偏離 → 需該 O 重新裁決")

# --- 3e. B′ 回歸: v9.0 P_n 輸出 6.5030 殘留掃描 ---
print("\n  [3e] B′ 回歸測試: v9.0 P_n 輸出 6.5030 殘留掃描 (O169 docs/05)")
print("        判定: P_n = 1+2φ⁻¹n+K₂n² 屬 A 類 (受證偽) — 其 2φ⁻¹ 係「每層增益」語義")
print(f"        v10.0 取代式: Ω_DM/Ω_b = F₇/L₀ = 13/2 = {RATIO_DM_B}  EXACT")
if abs(RATIO_DM_B - 6.5) < 1e-15:
    ok("Ω_DM/Ω_b = 13/2 EXACT (純 F-數, 唔經 P_n)")
else:
    bad(f"Ω_DM/Ω_b ≠ 13/2: {RATIO_DM_B}")

import re as _re
_pat = _re.compile(r"6\.5030|6\.503\b")
_live, _all = [], []
for _root, _dirs, _files in os.walk(REPO):
    _dirs[:] = [d for d in _dirs if d not in (".git", "data")]
    for _fn in _files:
        if not _fn.endswith((".py", ".md")):
            continue
        _p = os.path.join(_root, _fn)
        _rel = os.path.relpath(_p, REPO)
        try:
            with open(_p, encoding="utf-8", errors="ignore") as _f:
                if _pat.search(_f.read()):
                    _all.append(_rel)
                    if _fn.endswith(".py") and "o169_da_spectral" not in _rel:
                        _live.append(_rel)
        except Exception:
            pass
print(f"        殘留: 共 {len(_all)} 個檔案; 其中非 O169 嘅活躍 .py 腳本 {len(_live)} 個")
for _f in sorted(_live):
    print(f"          · {_f}")
print(f"        → 唔屬本檢查器職權 (要該 O 自行清理); 本檢查器自身已零 6.5030 依賴")

# ============ 4. 結果 ============
print("\n[4] 結果")
print("-" * 76)
print(f"  檔案:        {'✅ ' + str(total_files) + '/' + str(total_files) if not missing else '❌ ' + str(len(missing)) + ' 缺失'}")
print(f"  文檔結構聲稱: {n_ok}/{len(doc_ok)}")
print(f"  stale 聲稱:   {len(STALE)} 項 (待對應 O 更新)")
print(f"  物理重算:     {'✅ 全部通過' if not FAIL else '❌ ' + str(len(FAIL)) + ' 項失敗'}")
print(f"  B′ 殘留:      {len(_live)} 個活躍腳本 (待各 O 清理)")
print()
if FAIL:
    print("=" * 76)
    print(f"❌ 完整性檢查失敗 — {len(FAIL)} 項硬失敗:")
    for m in FAIL:
        print(f"   - {m}")
    print("=" * 76)
    sys.exit(1)
if STALE:
    print("=" * 76)
    print(f"🔴 完整性檢查: 結構層全部通過, 但 {len(STALE)} 項 stale 聲稱待更新:")
    for m in STALE:
        print(f"   - {m}")
    print("   (依賴已證偽公式/已撤銷常數嘅結論; 交回擁有該結論嘅 O 處理, 本檢查器唔代佢改數值)")
    print("=" * 76)
    sys.exit(2)
print("=" * 76)
print("✅ 數據完整性檢查全部通過!")
print("=" * 76)
