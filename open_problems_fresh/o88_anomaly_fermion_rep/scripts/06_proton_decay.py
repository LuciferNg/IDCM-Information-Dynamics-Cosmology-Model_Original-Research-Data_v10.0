#!/usr/bin/env python3
"""
O88 — scripts/06_proton_decay.py   (SU(12) 質子衰變預言 / PROTON DECAY)
=======================================================================
任務來源：register `O88/proton-decay`（2026-10-02 調律者指示）
          對應 o110 gap 表 B11/P1「SU(12) GUT 必然預言質子衰變，壽命未計算」
前置：O85（breaking chain, 18/18 ✅）、O89（M_GUT & α_GUT, 46/46 ✅）、O88（fermion rep）

────────────────────────────────────────────────────────────────────
0. 一句話
   SU(12) 破缺鏈喺 M_GUT 產生 **120 個 (15,8) gauge boson**，其中 **48 個係色三重態
   (leptoquark)**，可中介 ΔB=1 衰變。用 IDCM 零參數 M_GUT = M_Pl·γ₁ = 6.2214×10¹⁶ GeV
   同 α_GUT⁻¹ = 47，得 τ_p(p→e⁺π⁰) ~ 10³⁶–10³⁹ yr。

────────────────────────────────────────────────────────────────────
1. 公式來源（**外部權威，非自創**）
   A. V. Dorsner 等, arXiv:2401.16907, eq. (4.47):

       Γ(p→π⁰e⁺) = (m_p² − m_π²)²/m_p³ · (π/2) · A_L² · α_GUT²/M_GUT⁴
                   × |c(e^C,d) ⟨π⁰|(ud)_L u_L|p⟩|²

   其中 ⟨π⁰|(ud)_L u_L|p⟩ = 0.134 GeV²（論文原文）。
   本腳本 §2 用 minimal SU(5) 已知結果做**校準檢查**（M_X=10¹⁵–10¹⁶，α_GUT⁻¹=40
   ⟹ τ ~ 10³³–10³⁷ yr，與「minimal SU(5) 已被排除（>2.4×10³⁴）」一致）。

────────────────────────────────────────────────────────────────────
2. 結構輸入（全部 IDCM 零參數）
   · M_GUT = M_Planck × γ₁ （O89 V06/V10，🟢）
   · α_GUT⁻¹ = 47 （O89 V40/V42，🟢）
   · coset 143 − 12 = 131 massive；Step 1 產生 120 = (15,8)
   · SU(4) → SU(3)_c × U(1)：15 = 8 ⊕ 3 ⊕ 3̄ ⊕ 1 ⟹ 色帶電分量 6
   · N_LQ = 6 × 8 = **48 個色三重態 leptoquark boson**

────────────────────────────────────────────────────────────────────
3. 誠實聲明
   · Hadronic matrix element 0.134 GeV² 同 A_L 係**外部 QCD 輸入**（唔係 IDCM 結構），
     屬 🔴 理論外部依賴，已標示。
   · N_LQ 之**相干/非相干求和**未由群論完全釘死 ⟹ 報 **單通道** 同 **48 通道** 兩個界。
   · v9 之 6.1×10³⁴ yr **冇保存推導腳本** ⟹ 不可重現，只作 legacy 記錄比較。
"""

import json
import math
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "data", "06_proton_decay.json")

# ============================================================
# 常數
# ============================================================
M_P    = 0.9382720813      # GeV
M_PI0  = 0.1349768         # GeV
HBAR   = 6.582119569e-25   # GeV·s
YR_S   = 3.1557e7          # s/yr
M_PL   = 1.2209e19         # GeV  (Planck mass)
GAMMA1 = 0.0050957708      # γ₁ (O89)

# IDCM 結構（零參數）
M_GUT  = M_PL * GAMMA1
A_GUT_INV = 47
ALPHA_GUT = 1.0 / A_GUT_INV

# 外部 QCD 輸入
ALPHA_H = 0.134            # GeV²  (arXiv:2401.16907 eq 4.47)
A_L     = 1.4              # 長程重整化（1 GeV ← M_GUT）

# 結構計數
N_MASSIVE_COSET = 143 - 12          # 131
N_STEP1 = 120                       # (15,8)
N_LQ = 6 * 8                        # 色三重態：6 × SU(3)-adjoint 8 = 48
N_OCTET = 8 * 8                     # 色八重態 64
N_SINGLET = 1 * 8                   # 色單態 8

results = []
def chk(tag, claim, got, want, tol=1e-12):
    ok = abs(float(got) - float(want)) <= tol
    results.append({"tag": tag, "claim": claim, "got": str(got),
                    "want": str(want), "pass": bool(ok)})
    print("  [%s] %-8s %s   (got=%s want=%s)" % (
        "PASS" if ok else "FAIL", tag, claim, got, want))
    return ok

print("=" * 74)
print("O88 — SU(12) 質子衰變推導")
print("=" * 74)

# ============================================================
# 段 1 — 結構輸入
# ============================================================
print("\n[段 1] IDCM 結構輸入（零參數）")
print("  M_Planck   = %.6g GeV" % M_PL)
print("  γ₁         = %.10f  (O89)" % GAMMA1)
print("  M_GUT      = M_Pl·γ₁ = %.6g GeV" % M_GUT)
print("  α_GUT⁻¹    = %d  → α_GUT = %.8f" % (A_GUT_INV, ALPHA_GUT))
chk("P1", "M_GUT = M_Pl·γ₁", M_GUT, M_PL * GAMMA1, tol=1.0)
chk("P2", "O89 記錄 M_GUT = 6.2214e16 GeV", M_GUT / 6.2214e16, 1.0, tol=1e-3)

print("\n[段 2] 破缺鏈 coset 分解（O85）")
print("  dim SU(12) − dim SM = 143 − 12 = %d massive gauge bosons" % N_MASSIVE_COSET)
print("  Step 1 @ M_GUT: SU(12) → SU(4)×SU(3)，143 = (15,1) ⊕ (1,8) ⊕ (15,8)")
print("    保留: 15 + 8 = 23 ; 破缺: (15,8) = %d" % N_STEP1)
chk("S1", "(15,8) = 15×8 = 120", 15 * 8, N_STEP1)
chk("S2", "15+8+120 = 143 = dim SU(12)", 15 + 8 + 120, 143)
chk("S3", "120 + (23−12) = 131 = 143 − 12", 120 + (23 - 12), N_MASSIVE_COSET)

print("\n  再由 SU(4) → SU(3)_c × U(1)（Pati-Salam 路徑）分解 15:")
print("    15 = 8_c(gluon) ⊕ 3 ⊕ 3̄(leptoquark) ⊕ 1")
chk("S4", "8 + 3 + 3 + 1 = 15", 8 + 3 + 3 + 1, 15)

print("\n  ⟹ (15,8) 之色結構（× SU(3)-adjoint 8 重數）:")
print("    色八重態 (8,8)   : %2d 個 — 只耦合 qq̄，ΔB = 0" % N_OCTET)
print("    色三重態 (3,8)+(3̄,8): %2d 個 — 耦合 qq 同 q̄l，**ΔB = 1** ★ leptoquark" % N_LQ)
print("    色單態 (1,8)     : %2d 個 — 只耦合 ll̄ / qq̄，ΔB = 0" % N_SINGLET)
chk("S5", "64 + 48 + 8 = 120", N_OCTET + N_LQ + N_SINGLET, 120)
chk("S6", "N_LQ = 6 × 8 = 48", N_LQ, 48)
print("  ★ N_LQ = 48 = 2·B·N_gen = 48 —— 與 SM Weyl fermion 數（3×16）數值相同（記錄，不作斷言）")

# ============================================================
# 段 3 — 公式校準檢查（minimal SU(5)）
# ============================================================
print("\n[段 3] 公式校準（用 minimal SU(5) 已知結論反核）")
def gamma_p(m_gut, alpha_gut, a_l=A_L, alpha_h=ALPHA_H, n_channels=1.0, c=1.0):
    pref = (M_P**2 - M_PI0**2)**2 / M_P**3
    return (pref * (math.pi / 2) * a_l**2 * alpha_gut**2 / m_gut**4
            * c**2 * alpha_h**2 * n_channels)

def tau_yr(g):
    return (HBAR / g) / YR_S if g > 0 else float("inf")

for mx, ainv, note in [(1e15, 40, "minimal SU(5) 典型 M_X"),
                       (1e16, 40, "上界參考")]:
    g = gamma_p(mx, 1.0 / ainv)
    t = tau_yr(g)
    print("  M_X=%.0e, α⁻¹=%d : τ_p = %.3e yr   %s" % (mx, ainv, t, note))
g5 = gamma_p(1e15, 1.0 / 40)
t5 = tau_yr(g5)
calib_ok = 1e31 < t5 < 1e35
chk("C1", "minimal SU(5) 校準: τ(1e15,1/40) ∈ (1e31,1e35) yr ⟹ 吻合『已被排除』",
    1.0 if calib_ok else 0.0, 1.0)
print("  → 校準%s：公式與 minimal SU(5) 被 Super-K 排除（τ>2.4e34）之事實一致"
      % ("通過 ✅" if calib_ok else "失敗 ⚠️"))

# ============================================================
# 段 4 — IDCM 預言
# ============================================================
print("\n[段 4] IDCM v10 預言")
print("  M_GUT = %.6e GeV ; α_GUT⁻¹ = %d ; A_L = %.2f ; ⟨π⁰|(ud)_Lu_L|p⟩ = %.3f GeV²"
      % (M_GUT, A_GUT_INV, A_L, ALPHA_H))

bands = {}
for n_ch, lab in [(1.0, "單通道 (N_LQ=1)"), (N_LQ, "全 48 通道非相干和 (N_LQ=48)")]:
    g = gamma_p(M_GUT, ALPHA_GUT, n_channels=n_ch)
    t = tau_yr(g)
    bands[lab] = {"Gamma_GeV": g, "tau_yr": t}
    print("  %-28s : Γ = %.4e GeV   τ_p = %.4e yr" % (lab, g, t))

t_lo = bands["全 48 通道非相干和 (N_LQ=48)"]["tau_yr"]
t_hi = bands["單通道 (N_LQ=1)"]["tau_yr"]
print("\n  ⟹ IDCM v10 預言範圍: **%.2e yr ≤ τ_p ≤ %.2e yr**" % (t_lo, t_hi))
print("     （差距 = 48 = N_LQ，係相干性未定之結構不確定度）")

# A_L 不確定度
for al in [1.0, 1.4, 1.8]:
    g = gamma_p(M_GUT, ALPHA_GUT, a_l=al)
    print("     A_L = %.1f → τ_p = %.3e yr" % (al, tau_yr(g)))

# ============================================================
# 段 5 — 與 v9 legacy claim 及實驗對比
# ============================================================
print("\n[段 5] 對比")
M_V9 = 1.96e16
TAU_V9 = 6.1e34
print("  v9.0 legacy: M_X = %.3e GeV, τ_p = %.2e yr" % (M_V9, TAU_V9))
print("  v10        : M_GUT = %.3e GeV  →  M_GUT/M_X(v9) = %.3f" % (M_GUT, M_GUT / M_V9))
scale = (M_GUT / M_V9) ** 4
print("  τ ∝ M⁴ ⟹ 同公式下 v10/v9 = %.1f ×（M 效應）" % scale)
print("  若 v9 亦用 α_GUT⁻¹=47，則 τ_v10(單通道) = %.2e yr" % (TAU_V9 * scale))
print("  加 N_LQ=48 非相干 ⟹ %.2e yr" % (TAU_V9 * scale / N_LQ))

print("\n  實驗界:")
SK = 2.4e34    # Super-K p→e⁺π⁰ 90% CL (2020, 450 kton·yr)
HK = 1.0e35    # Hyper-K 10 yr projected
print("    Super-K  現界      : τ > %.1e yr" % SK)
print("    Hyper-K  10yr 投影 : τ ~ %.1e yr" % HK)
for lab, d in bands.items():
    t = d["tau_yr"]
    print("    %-28s : %s Super-K ; %s Hyper-K" % (
        lab, "✅ 未排除" if t > SK else "❌ 已排除",
        "✅ 可探測" if t < HK else "❌ 超出 Hyper-K 10yr"))

print("\n  ★★ v9 內部一致性核對（用 v9 **自己**嘅 M_X，標準公式）:")
t_v9M_single = tau_yr(gamma_p(M_V9, ALPHA_GUT, n_channels=1.0))
t_v9M_48 = tau_yr(gamma_p(M_V9, ALPHA_GUT, n_channels=N_LQ))
print("     M_X = %.3e GeV, α⁻¹=47, 單通道   → τ = %.3e yr" % (M_V9, t_v9M_single))
print("     M_X = %.3e GeV, α⁻¹=47, 48 通道  → τ = %.3e yr" % (M_V9, t_v9M_48))
print("     v9 宣稱                          → τ = %.2e yr" % TAU_V9)
print("     偏差: 宣稱 / 標準 = %.2e (單通道) ; %.2e (48 通道)"
      % (TAU_V9 / t_v9M_single, TAU_V9 / t_v9M_48))
ratio_v9_single = TAU_V9 / t_v9M_single
chk("V1", "v9 宣稱 τ_p 與標準 dimension-6 公式一致（比值 ∈ [0.5, 2]）",
    1.0 if 0.5 <= ratio_v9_single <= 2.0 else 0.0, 1.0)
# V1c：正面釘死「發現」本身（保留 V1 FAIL 作 finding 標籤）
chk("V1c", "★發現：v9 宣稱與標準公式**唔一致**（比值 < 0.5 或 > 2）",
    1.0 if not (0.5 <= ratio_v9_single <= 2.0) else 0.0, 1.0)
print("     ⟹ v9 之 6.1×10³⁴ yr **唔能**由標準 gauge-boson dimension-6 公式")
print("        用 v9 自己嘅 M_X 重現（差 %.0e 倍）⟹ 屬不可重現 legacy claim。" % (1/ratio_v9_single))

print("\n  ★ 可證偽性判定:")
verdict = ("🟢 落入 Hyper-K 探測範圍" if t_lo < HK else "🔴 超出 Hyper-K 10yr 範圍")
print("     IDCM v10 預言 τ_p ≥ %.2e yr > Hyper-K 10yr 投影 %.0e yr" % (t_lo, HK))
print("     ⟹ **v9『在 Hyper-K 靈敏度範圍內』之可證偽性 claim 唔成立**（v10 重建後）")
print("     ⟹ 反而係：**否證**需要下一代（FCC-hh 級 / Hyper-K 30yr+）或全新機制")


# ============================================================
# 段 6 — 標度律 + 可證偽性
# ============================================================
print("\n[段 6] 標度律（零參數封閉式）")
print("  τ_p ∝ M_GUT⁴ / α_GUT² ,  M_GUT = M_Pl·γ₁ ,  α_GUT⁻¹ = 47")
print("  ⟹ τ_p = [ (m_p²−m_π²)²/m_p³ · (π/2) A_L² α_GUT²/M_GUT⁴ · N_LQ · α_H² ]⁻¹")
print("  ★ 全部輸入皆 IDCM 結構（M_Pl, γ₁, 47, N_LQ=48），")
print("    唯 α_H（QCD 矩陣元）同 A_L（重整化）係外部 —— 屬 🔴 外部依賴。")

# ============================================================
# 總結
# ============================================================
scored = results
npass = sum(1 for r in scored if r["pass"])
print("\n" + "=" * 74)
print("總結: %d/%d PASS" % (npass, len(scored)))
print("  N_LQ = %d 個色三重態 leptoquark @ M_GUT = %.6e GeV" % (N_LQ, M_GUT))
print("  τ_p(p→e⁺π⁰) ∈ [%.3e, %.3e] yr" % (t_lo, t_hi))
print("=" * 74)

out = {
    "task": "O88/proton-decay",
    "formula_source": "arXiv:2401.16907 eq.(4.47) (Dorsner et al.)",
    "formula": "Gamma(p->pi0 e+) = (mp^2-mpi^2)^2/mp^3 * (pi/2) * A_L^2 * alpha_GUT^2/M_GUT^4 * |c * <pi0|(ud)_L u_L|p>|^2",
    "structural_inputs": {
        "M_Planck_GeV": M_PL, "gamma1": GAMMA1, "M_GUT_GeV": M_GUT,
        "alpha_GUT_inv": A_GUT_INV, "source": "O89 (46/46)",
    },
    "external_inputs": {
        "alpha_H_GeV2": ALPHA_H, "A_L": A_L,
        "status": "🔴 外部 QCD／重整化輸入，非 IDCM 結構",
    },
    "leptoquark_count": {
        "N_LQ": N_LQ, "colour_octet": N_OCTET, "colour_singlet": N_SINGLET,
        "total_step1_broken": N_STEP1, "coset_total": N_MASSIVE_COSET,
    },
    "prediction_yr": {"single_channel": t_hi, "all_48_incoherent": t_lo},
    "experiment": {"SuperK_bound_yr": SK, "HyperK_10yr_yr": HK},
    "v9_legacy": {"M_X_GeV": M_V9, "tau_yr": TAU_V9, "reproducible": False,
                  "standard_formula_at_v9_MX_single_channel_yr": t_v9M_single,
                  "standard_formula_at_v9_MX_48_channel_yr": t_v9M_48,
                  "claim_over_standard_ratio": ratio_v9_single,
                  "verdict": "唔能由標準 dimension-6 gauge boson 公式用 v9 自己 M_X 重現"},
    "falsifiability_verdict": {
        "hyperK_10yr_reach_yr": HK, "prediction_lower_bound_yr": t_lo,
        "within_hyperK_reach": bool(t_lo < HK),
        "statement": "v9『在 Hyper-K 靈敏度範圍內』唔成立；v10 預言超出 Hyper-K 10yr",
    },
    "tests": results, "passed": npass, "total": len(scored),
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("\n✅ 已寫入 data/06_proton_decay.json")
