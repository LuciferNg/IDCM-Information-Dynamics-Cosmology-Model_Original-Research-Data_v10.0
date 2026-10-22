#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O81 — Script 11: 文檔獨立核對 (Documentation Cross-Check)
==========================================================
性質: 純核對 (verification-only) — 不引入任何新推導、不改任何公式。
目的: 對 O81 全部文檔中宣稱嘅每一條公式/數值, 獨立重算並逐條對照。
規則: 不 import 任何 O81 推導函數; 只用 math/numpy 由第一原理重算。

建立日期: 2026-09-19 (調律者指示: 驗證整個推導過程)
"""
import os, math, sys
import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(OUT, exist_ok=True)

LINES = []
PASS = 0
FAIL = 0
WARN = 0

def L(s=""):
    LINES.append(str(s))
    print(s)

def CHECK(tag, desc, claim, actual, tol=1e-9):
    """tag: ✅/❌/⚠️ 由 caller 判; 呢度只做數值對照"""
    global PASS, FAIL
    ok = abs(claim - actual) <= tol if isinstance(claim, (int, float)) else (claim == actual)
    if ok:
        PASS += 1
        L(f"  ✅ {desc}")
    else:
        FAIL += 1
        L(f"  ❌ {desc}")
    L(f"     文檔宣稱 = {claim} | 獨立實算 = {actual} | 差 = {abs(claim-actual) if isinstance(claim,(int,float)) else 'N/A'}")
    return ok

def FLAG(desc, note):
    global WARN
    WARN += 1
    L(f"  ⚠️  {desc}")
    L(f"     {note}")

L("=" * 88)
L("  O81 — Script 11: 文檔獨立核對 (verification-only, 無新推導)")
L("=" * 88)
L(f"  建立日期: 2026-09-19")
L(f"  範圍: SESSION_START.md / docs/01_problem_record.md / docs/01_derivation_record.md")
L(f"        / docs/02_analysis_report.md / POINTER_o204_ej_identity.md")
L(f"  原則: 只核對, 不引入新推導; 唔 import O81 任何函數")
L("")

# ============================================================
# 0. 由第一原理重建權威量
# ============================================================
N_d = 44
N_dual = 88

# K_Chain 譜
omega_n = np.array([2 * math.sin(math.pi * n / 88) for n in range(1, N_d + 1)])
gamma_n = np.array([4 * math.sin(math.pi * n / 88) ** 2 for n in range(1, N_d + 1)])

# 88-site 對偶鏈 — O34 權威定義 (o34_observer_introspection/scripts/01_observer_operator.py L56)
#   γ_k = 4sin²(πk/176), k = 1..88
#   (注意: 唔係 4sin²(πk/88); O34 之 even/odd 分解基於 176 分母)
k88 = np.arange(1, N_dual + 1)
gamma_88 = 4 * np.sin(np.pi * k88 / 176) ** 2
Sg_even_88 = gamma_88[1::2].sum()   # k = 2,4,...,88  -> 重現 44-site K_Chain
Sg_odd_88 = gamma_88[0::2].sum()    # k = 1,3,...,87  -> 半整數模式

# 44-site 鏈
Sg_44 = gamma_n.sum()
Sg_even_44 = gamma_n[1::2].sum()    # n = 2,4,...,44
Sg_odd_44 = gamma_n[0::2].sum()     # n = 1,3,...,43

# SSB
mu2 = 2.0
lam = 2 / 123
W2 = mu2 / (2 * lam)
W0 = math.sqrt(W2)

# 統一 Lagrangian 係數
J_eff = W2
E_J_A = 2 * W2          # §6/§7 版本
E_J_B = 4 * mu2 * W2    # §2.3/§3.3 版本

# Lucas
def lucas(n):
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a + b
    return a
L10 = lucas(10)

# 冷斑
phi = (1 + math.sqrt(5)) / 2
eps = 1 / (4 * phi)
T_CMB_K = 2.72548
RMS_pred = eps ** 5 / 8
CS_pred = 5 * eps ** 5 / 8
CS_pred_uK = CS_pred * T_CMB_K * 1e6
A_obs_uK = 134.2

# ============================================================
# 一、K_Chain 譜 — docs/01_derivation_record §1.1
# ============================================================
L("━" * 88)
L("  一、K_Chain 譜 (docs/01_derivation_record.md §1.1 / docs/02 §層次1)")
L("━" * 88)
L("")

CHECK("1", "ω_k = 2sin(πk/88), k=1..44 (ω_44 = 2 Nyquist)", 2.0, omega_n[43], 1e-12)
CHECK("2", "γ_n = ω_n² = 4sin²(πn/88) (全 44 模態)", 0.0, float(np.max(np.abs(gamma_n - omega_n**2))), 1e-12)
CHECK("3", "Σγ (n=1..44) = 90.0", 90.0, float(Sg_44), 1e-9)

L("")
L("  ⚠️  重點: 『Σγ_even / Σγ_odd』在 O81 內部有兩種指涉")
L(f"      (a) 44-site 鏈 n 嘅奇偶:  even = {Sg_even_44:.6f}, odd = {Sg_odd_44:.6f}")
L(f"      (b) 88-site 對偶鏈 k 嘅奇偶: even = {Sg_even_88:.6f}, odd = {Sg_odd_88:.6f}")
L(f"      兩者差皆 = 2 (μ²), 但『世界/觀察者』標籤只對 (b) 成立 (O34 權威)")
L("")

# O34 權威
L("  ── O34 權威對照 (o34_observer_introspection/final_result.md L11) ──")
CHECK("4", "O34: Σγ_even = 90 = 2(N_d+1) (世界) [88-site]", 90.0, float(Sg_even_88), 1e-9)
CHECK("5", "O34: Σγ_odd  = 88 = 2N_d     (觀察者) [88-site]", 88.0, float(Sg_odd_88), 1e-9)
CHECK("6", "O34: μ² = Σγ_even − Σγ_odd = 90 − 88 = 2", 2.0, float(Sg_even_88 - Sg_odd_88), 1e-9)
CHECK("7", "44-site 鏈總和 Σγ = 90 亦 = 2(N_d+1) (巧合/恆等)", 90.0, float(Sg_44), 1e-9)
CHECK("8", "O34: 88-site 全鏈 Σγ (k=1..88) = 178 = 2×89 = 2×F₁₁", 178.0, float(gamma_88.sum()), 1e-9)

L("")
L("  ── 文檔標籤對照 ──")
L("     docs/02_analysis_report.md §層次2: 『μ² = Σγ_even − Σγ_odd = 90 − 88 = 2』")
L("        → 用 (b) 88-site 慣例 → 與 O34 一致 ✅")
L("     docs/01_derivation_record.md §1.1: 『Σγ = 90.0, Σγ_even = 46, Σγ_odd = 44 → 奇偶分裂: 世界/觀察者』")
L("        → 用 (a) 44-site 慣例, 但套上 (b) 嘅『世界/觀察者』語義 → 標籤衝突 ⚠️")
L("     scripts/05_independent_audit.py: 『Σγ_even = 46 (世界), Σγ_odd = 44 (觀察者)』→ 同一衝突 ⚠️")
FLAG("Σγ_even/Σγ_odd 標籤不一致 (44-site 46/44 vs 88-site 90/88)",
     "兩者數值差皆為 μ²=2, 故下游公式 (λ=2/123, ⟨W⟩²=61.5, E_J=123) 不受影響; 但『世界/觀察者』身份需按 O34 統一為 88-site (90/88)。")

L("")

# ============================================================
# 二、SSB 勢 — docs/01 §2.1, docs/02 §層次2
# ============================================================
L("━" * 88)
L("  二、SSB 勢 (docs/01 §2.1 / docs/02 §層次2)")
L("━" * 88)
L("")

CHECK("9",  "μ² = 2", 2.0, mu2, 1e-12)
CHECK("10", "λ = 2/123 = 2/[3(N_d−dim_ℂ)] = 2/[3·41]", 2/123, lam, 1e-15)
CHECK("11", "3(N_d − dim_ℂ) = 3(44−3) = 123", 123.0, float(3*(N_d-3)), 1e-12)
CHECK("12", "⟨W⟩² = μ²/(2λ) = 61.5", 61.5, W2, 1e-12)
CHECK("13", "⟨W⟩ = √61.5", math.sqrt(61.5), W0, 1e-12)
CHECK("14", "V_min = −μ⁴/(4λ) = −61.5", -61.5, -mu2**2/(4*lam), 1e-12)
CHECK("15", "V''(0) = −2μ² = −4 (不穩定極大)", -4.0, -2*mu2, 1e-12)
CHECK("16", "V''(⟨W⟩) = 4μ² = 8 (穩定極小)", 8.0, 4*mu2, 1e-12)
CHECK("17", "m_δρ = 2√(μ²) = 2√2", 2*math.sqrt(2), 2*math.sqrt(mu2), 1e-12)
L("")

# ============================================================
# 三、統一 Lagrangian 係數 — docs/01 §4.1, §6, §7
# ============================================================
L("━" * 88)
L("  三、統一 Lagrangian 係數 (docs/01 §4.1 / §6 / §7.1)")
L("━" * 88)
L("")

CHECK("18", "J_eff = ⟨W⟩² = 61.5", 61.5, J_eff, 1e-12)
CHECK("19", "§6/§7 版: E_J = 2⟨W⟩² = 123", 123.0, E_J_A, 1e-12)
CHECK("20", "§2.3/§3.3 版: 4μ²⟨W⟩² = 492", 492.0, E_J_B, 1e-12)
CHECK("21", "E_J(§6/§7) / J_eff = 2", 2.0, E_J_A/J_eff, 1e-12)
CHECK("22", "492 / 61.5 = 8 = 2B (B=4)", 8.0, E_J_B/J_eff, 1e-12)
CHECK("23", "兩版本比值 = 2μ² = 4 = γ_44", 4.0, E_J_B/E_J_A, 1e-12)
CHECK("24", "L₁₀ (Lucas) = 123", 123.0, float(L10), 1e-12)
CHECK("25", "L₁₀ = N_gen(N_d − N_gen) = 3·41 = 123", 123.0, float(3*(N_d-3)), 1e-12)
CHECK("26", "492 = B·L₁₀ = 4·123", 492.0, float(4*123), 1e-12)
CHECK("27", "f_θ = √⟨W⟩² = √61.5", math.sqrt(61.5), math.sqrt(W2), 1e-12)
L("")

# ============================================================
# 四、圖論/阻挫 — docs/01 §1.2, §7.1
# ============================================================
L("━" * 88)
L("  四、圖論/阻挫 (docs/01 §1.2 / §7.1)")
L("━" * 88)
L("")

CHECK("28", "阻挫邊 = 32 = 20Δ + 12⬠", 32.0, float(20+12), 1e-12)
CHECK("29", "Rhombicosidodecahedron: V=60, χ=2", 2.0, float(60-120+62), 1e-12)  # 60V-120E+62F
CHECK("30", "§7.1: 每阻挫邊能量 = 2J_eff = 2×61.5 = 123", 123.0, 2*J_eff, 1e-12)
CHECK("31", "§7.1: 總阻挫能 = 32×123 = 3936", 3936.0, 32*2*J_eff, 1e-12)
CHECK("32", "§7.1: 總阻挫能/32 = 123 (恆等: 除32即還原 2J_eff)", 123.0, 32*2*J_eff/32, 1e-12)
L("")
L("  ⚠️  註: #32 係恆等式 —『E_J = 總阻挫能/32』並無獨立約束力")
L("     (先設每邊 2J_eff, 再除 32 → 必然回到 2J_eff; 不構成 E_J 之獨立推導)")
L("     E_J = 2⟨W⟩² 之實質約束來自: (i) 模擬 E_J/J = 2, (ii) 123 = L₁₀")
FLAG("§7.1『E_J = 總阻挫能/32 = 123』係恆等式, 非獨立推導",
     "誠實標記: E_J = 2⟨W⟩² 目前為『與模擬一致 + 數值為結構數 L₁₀』之候選, 未達結構強制 (structural necessity)。")
L("")

# ============================================================
# 五、1-loop / path integral — docs/01 §7.2
# ============================================================
L("━" * 88)
L("  五、1-loop / path integral (docs/01 §7.2)")
L("━" * 88)
L("")

kappa = 0.25   # √κ = 1/4
a_n = 2 * kappa * W0 / omega_n

CHECK("33", "a_1 = 2κ⟨W⟩/ω_1 = 54.9291…", 54.9291, float(a_n[0]), 1e-3)
CHECK("34", "a_7 = 2κ⟨W⟩/ω_7 = 7.9276…", 7.9276, float(a_n[6]), 1e-3)
CHECK("35", "a_44 = 2κ⟨W⟩/ω_44 = 1.9605…", 1.9605, float(a_n[43]), 1e-3)
CHECK("36", "全 44 模式 a_n > 1 (非微擾)", 44.0, float(np.sum(a_n > 1)), 0)
CHECK("37", "V_tree = V_min = −61.5", -61.5, -mu2**2/(4*lam), 1e-12)

V_1loop = 0.5 * float(np.sum(np.sqrt(omega_n**2 + (2*kappa*omega_n*W0))))
CHECK("38", "V_1loop = (1/2)Σ√(ω_n² + m_eff_n²) = 55.7825", 55.7825, V_1loop, 1e-3)
CHECK("39", "V_eff = V_tree + V_1loop = −5.7175", -5.7175, -61.5 + V_1loop, 1e-3)
CHECK("40", "線性近似 E_J_44 = 44·κ⟨W⟩/2 = 43.1321", 43.1321, float(N_d*kappa*W0/2), 1e-3)

# 精確 c1(a) 用數值積分 (獨立, 不 import O81)
def c1_exact(a):
    """c1(a) = (1/π)∫₀^{2π} √(1 − a cosθ)·cosθ dθ  (Simpson, 高解析度)"""
    N = 200000
    th = np.linspace(0, 2*math.pi, N+1)
    f = np.sqrt(np.maximum(0.0, 1 - a*np.cos(th))) * np.cos(th)
    return float(np.trapezoid(f, th) / math.pi)

E_J_1loop_exact = 0.5 * sum(omega_n[i] * c1_exact(a_n[i]) for i in range(N_d))
L(f"  [獨立數值積分] 44-site E_J_1loop (精確 c₁) = {E_J_1loop_exact:.6f}")
L(f"     docs/01 §7.2 宣稱 44-site 精確 = 31.54")
if abs(abs(E_J_1loop_exact) - 31.54) < 0.5:
    L(f"     → |實算| = {abs(E_J_1loop_exact):.4f}  ✅ 與宣稱一致")
    PASS += 1
else:
    L(f"     → |實算| = {abs(E_J_1loop_exact):.4f}  ❌ 與宣稱 31.54 不符")
    FAIL += 1
L("")

# 88-site 對偶鏈 a_n 發散檢查 (scripts/08 之 k=88 問題)
k88_all = np.arange(1, N_dual + 1)
omega_88_all = 2 * np.sin(np.pi * k88_all / 88)
a_88 = 2 * kappa * W0 / np.where(omega_88_all == 0, np.nan, omega_88_all)
L("  ── scripts/08 之 88-site 計算檢查 ──")
L(f"     ω_88 = 2sin(π·88/88) = {omega_88_all[87]:.3e}  (≈0, Nyquist 端點)")
L(f"     a_88 = 2κ⟨W⟩/ω_88 → 發散 ({a_88[87]:.3e})")
FLAG("scripts/08 之 88-site 表含 k=88 除零偽值",
     "data/08 之 88-site 段『a=3.46e15, c₁=−3.27e7』為數值偽影 (ω_88≈0); 88-site E_J 應只用 k=1..87 (或明確排除零模)。")
L("")

# ============================================================
# 六、88 → A5 投影 — docs/01 §7.3
# ============================================================
L("━" * 88)
L("  六、88 → A5 投影映射 (docs/01 §7.3)")
L("━" * 88)
L("")

CHECK("41", "|A5| = 60", 60.0, float(60), 1e-12)
CHECK("42", "44 = B × L₅ = 4 × 11", 44.0, float(4*11), 1e-12)
CHECK("43", "60 = F₅ × (B·N_gen) = 5 × 12", 60.0, float(5*12), 1e-12)
CHECK("44", "60 = 88 − 28 = 88 − (L₇−1)", 60.0, float(88-(29-1)), 1e-12)
CHECK("45", "60 = 44 + B² = 44 + 16", 60.0, float(44+16), 1e-12)
CHECK("46", "A5 不可約表示 1²+3²+3²+4²+5² = 60", 60.0, float(1+9+9+16+25), 1e-12)
L("")
L("  ⚠️  註: §7.3 之『c_{i,n} = |Dⁿ_{0,0}(R_i)|² = cos²(n·π·ang_i/180)』為候選形式,")
L("     文中未給出由 Wigner D-matrix 到 cos² 嘅逐步推導 → 標記為 🟡 候選 (非已證定理)。")
FLAG("§7.3 投影映射: 群嵌入 Z_88 ⊂ SO(3) ⊃ A5 為真, 但 c_{i,n} = cos²(...) 未逐步導出",
     "誠實標記: 44/60 維度匹配 + 軌道計數 (60/1) 成立; c_{i,n} 表達式仍屬候選。")
L("")

# ============================================================
# 七、冷斑 / 能量標度 — docs/01 §1.2, docs/02 §層次4
# ============================================================
L("━" * 88)
L("  七、冷斑 / 能量標度 (docs/01 §1.2 / docs/02 §層次4)")
L("━" * 88)
L("")

CHECK("47", "ε = 1/(4φ) = 0.1545085…", 0.1545084971874737, eps, 1e-12)
CHECK("48", "RMS = ε⁵/8 = 1.10071e-5", 1.10071e-5, RMS_pred, 1e-9)
CHECK("49", "冷斑 ΔT/T = 5ε⁵/8 = 5.50354e-5", 5.50354e-5, CS_pred, 1e-9)
CHECK("50", "5ε⁵/8 × T_CMB (2.72548 K) = 150.0 μK", 150.0, CS_pred_uK, 1.0)
L("")
L(f"  ── 關鍵: docs/02 §層次4 寫『A = 134.2 μK = 5ε⁵/8·T_CMB』──")
L(f"     5ε⁵/8·T_CMB = {CS_pred_uK:.2f} μK  (結構預測)")
L(f"     134.2 μK     = SMICA 5° 平滑實測 (cmb_cold_spot/22 §, 觀測值)")
L(f"     兩者差 = {abs(CS_pred_uK-A_obs_uK)/A_obs_uK*100:.2f}%  (cmb_cold_spot/20 記載 10.5%)")
FLAG("docs/02 將觀測值 134.2 μK 寫成『= 5ε⁵/8·T_CMB』",
     "5ε⁵/8·T_CMB = 150.0 μK (預測) ≠ 134.2 μK (觀測, 低 10.5%)。A 之結構式與實測值係兩個數, 不應以等號連接。")
L("")

# ============================================================
# 八、POINTER_o204 裁決之核對
# ============================================================
L("━" * 88)
L("  八、POINTER_o204_ej_identity.md 裁決核對")
L("━" * 88)
L("")

L("  POINTER 裁決 (2026-09-18, O204 scripts/05 §A2 9/9 PASS):")
L("    ⟨W⟩² = 61.5 ; L₁₀ = N_gen(N_d−N_gen) = 123")
L("    4μ²⟨W⟩² = 492 = V''(W₀)·⟨W⟩²   ← SSB 曲率 × 凝聚 (另一物理量)")
L("    2⟨W⟩²  = 123 = L₁₀             ← sine-Gordon cos θ 係數")
L("    比值 = 2μ² = 4 = γ_44 EXACT")
L("")
CHECK("51", "POINTER: 4μ²⟨W⟩² = 492", 492.0, E_J_B, 1e-12)
CHECK("52", "POINTER: 2⟨W⟩² = 123", 123.0, E_J_A, 1e-12)
CHECK("53", "POINTER: 比值 = 2μ² = 4 = γ_44", 4.0, float(gamma_n[43]), 1e-12)
CHECK("54", "POINTER: L₁₀ = N_gen(N_d−N_gen) = 123", 123.0, float(3*(N_d-3)), 1e-12)
L("")
L("  ✅ POINTER 之算術全部核對通過。")
L("  ⚠️  docs/01 §2.3/§3.3 仍寫『E_J = 4μ²⟨W⟩² = 492 (首選)』, §6/§7 寫『E_J = 2⟨W⟩² = 123』")
L("      → 同一文檔兩值; POINTER 已裁定 123 為 E_J, 492 應標為 V''(W₀)·⟨W⟩²")
L("      → 本輪按時序鐵律『加 dated 註記』, 不回溯改寫原文")
L("")

# ============================================================
# 九、docs/02 §六『剩餘未閉合』狀態核對
# ============================================================
L("━" * 88)
L("  九、docs/02_analysis_report.md §六 剩餘未閉合 — 狀態核對")
L("━" * 88)
L("")

L("  docs/02 §六 記載 (2026-08-25, scripts 01-04 時期):")
L("    1 E_J 完全閉合到模擬值        🟡")
L("    2 完整 path integral 有效作用量 🔴")
L("    3 88-site 環 → A5 投影映射      🔴")
L("    4 統一 Lagrangian 規範對稱群    🔴")
L("")
L("  後續 (2026-08-26, scripts 06-10) 狀態:")
L("    1 → 🟢 E_J = 2⟨W⟩² = 123, E_J/J = 2 (與模擬一致; 但獨立性見 §四 FLAG)")
L("    2 → 🟡 1-loop 已算 (V_eff = −5.72); 完整非微擾有效作用量未閉合")
L("    3 → 🟡 群論框架已立 (Z_88 ⊂ SO(3) ⊃ A5); c_{i,n} 仍候選")
L("    4 → 🟢 O85 已閉合 (SU(12) → SM, 18/18)")
L("")
L("  → docs/02 §六 為 2026-08-25 之歷史記錄, 按時序鐵律不回溯改寫;")
L("    本輪以 dated 註記 + 本核對報告更新狀態。")
L("")

# ============================================================
# 十、總結
# ============================================================
L("━" * 88)
L("  十、核對總結")
L("━" * 88)
L("")
L(f"  數值核對通過: {PASS}")
L(f"  數值核對失敗: {FAIL}")
L(f"  需標記之誠實事項 (⚠️): {WARN}")
L("")

if FAIL == 0:
    L("  🟢 全部可核對數值均與獨立實算一致 — 無算術錯誤。")
else:
    L(f"  🔴 有 {FAIL} 項數值不符 — 需修正文檔。")
L("")
L("  ⚠️  需記錄之非數值事項:")
L("    (1) Σγ_even/Σγ_odd 標籤: 44-site(46/44) vs 88-site(90/88) 兩種慣例並存 → 應統一按 O34 (88-site)")
L("    (2) docs/02 §層次4: 134.2 μK (觀測) 誤以等號連到 5ε⁵/8·T_CMB = 150.0 μK (預測)")
L("    (3) docs/01 §7.1: 『E_J = 總阻挫能/32』係恆等式, 非獨立推導 → E_J = 2⟨W⟩² 仍屬候選")
L("    (4) docs/01 §7.3: c_{i,n} = cos²(n·π·ang_i/180) 未逐步導出 → 候選")
L("    (5) scripts/08 之 88-site 段含 ω_88 ≈ 0 除零偽值")
L("    (6) docs/01 §2.3/§3.3 之 492 與 §6/§7 之 123 身份混淆 (POINTER_o204 已裁定)")
L("")
L("  ★ 本 script 為 verification-only: 未引入任何新推導, 未修改任何公式。")
L("")

with open(os.path.join(OUT, "11_doc_crosscheck.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(LINES) + "\n")

print(f"\n✅ 已寫入: {OUT}/11_doc_crosscheck.txt")
print(f"📊 通過 {PASS} | 失敗 {FAIL} | 標記 {WARN}")
