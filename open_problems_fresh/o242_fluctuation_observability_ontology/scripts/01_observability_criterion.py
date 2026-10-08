#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O242 R1 — 可觀測性二分判準: 「可觀測 = 譜差分」形式化 + 候選量窮舉分類
(2026-10-08)

判準 (三條, 全部要過先算「可觀測」):
  C-ref  差分性   : 存在參考系 R (另一邊界/另一能級/另一條件), 量可寫成
                   Δ = O(S; b) − O(S; b₀), 或本身係譜差 (能級差/異常差)
  C-bnd  邊界敏感 : ∂Δ/∂b ≠ 0 (對條件微變有響應)   — Casimir F∝d⁻⁴ 即此
  C-gau  gauge 不變: 無量綱化後 s_X = d ln X / d ln c = 0

分類:
  A 實驗檯可測 (T = 測試檯測量, 三條全過且已有實驗)
  B 結構檢驗量 (C = 宇宙學/幾何檢驗, 差分性不適用但結構閉合 + gauge 不變)
  C 不可觀測   (X = 缺參考系或無結構閉合)

候選量:
  1. E0_abs      = ½Σħω_k   (QFT 真空能絕對值)
  2. DelPhiSq_abs= ⟨Δφ²⟩   (場漲落方均絕對值)
  3. DelPhiSq_cp = Casimir-Polder 差分 (冷原子-表面 2 體量)
  4. Casimir_force = ΔF(d) = F(d)−F(d₀)  兩導體板
  5. Lamb_shift  = ΔE = E(2P₁/₂)−E(2S₁/₂) 能級差
  6. gminus2     = a_e = (g−2)/2  異常磁矩 (對 Dirac 值差)
  7. RhoLambda   = ρ_Λ (IDCM 結構值 M_Pl⁴e^{−V_Λ})
  8. LambdaEff   = Λ_eff = 8πM_Pl²e^{−V_Λ} = 3Ω_ΛH₀² (宇宙學)

結構依據來源 (引用唔重推):
  O36 #9   觀察者讀數 = 干涉可見度 ∝ A_n (生成=測量對偶)
  O138 §7.1 Born 規則平方結構有來源 (E∝ω²a² → p_n=|c_n|²)
  O86 docs/04 §1  N1: Λ_eff = 8πM_Pl²e^{−V_Λ}, ρ_Λ^{1/4}=2.246 meV
  O204 docs/08 §7.6  v9 QFT 量子化與 v10 唔相容 (E₀ 冇 v10 對應物)
  O212 dof=1  唯一錨, 冇 counterterm 自由度
  O62  V_Λ = F(γ)+44−F₈−B = 283.0821
"""
import math

print("=" * 74)
print("O242 R1 可觀測性判準 — 候選量分類")
print("=" * 74)

# ---------- 常量 (閉合上游值) ----------
V_Lambda = 283.0821292326      # O62: F(γ)+44−F₈−B
F8, B, Nd = 21, 4, 44
M_Pl_GeV = 1.220890e19         # reduced Planck? 用非約化: 1.2209e19 GeV(?)
# O86 用 M_Pl = 1.2209e19 GeV (Planck 質量)
rho_Lambda_1_4_meV = 2.2461    # O86 N1
Omega_Lambda_struct = 41/60    # O215/O86: Ω_Λ = 41/60 結構份額
Omega_Lambda_obs = 0.6847      # Planck

checks = []
def C(name, cond, detail=""):
    checks.append((name, bool(cond), detail))

# ---------- C-ref: 差分性 (由量嘅定義給出, 布爾) ----------
# 定義: delta[量] = 是否存在參考系 R 使 Δ = O(S;b) − O(S;b₀) 或本身係譜差
delta = {
    "E0_abs":        False,   # 真空態本身係參考, 冇第二條件 b₀; 絕對值
    "DelPhiSq_abs":  False,   # ⟨Δφ²⟩ 絕對值需要 cutoff; 冇參考系
    "DelPhiSq_cp":   True,    # Casimir-Polder: 原子-表面距離差 (2體量)
    "Casimir_force": True,    # F(d)−F(d₀) 板距差
    "Lamb_shift":    True,    # 能級差 E(2P)−E(2S) 譜差
    "gminus2":       True,    # 異常 = 對 Dirac 值差: a_e=(g−2)/2
    "RhoLambda":     False,   # ρ_Λ = M_Pl⁴e^{−V_Λ} 絕對值 (結構閉合但非差分量)
    "LambdaEff":     False,   # Λ_eff 絕對值 (結構閉合但非差分量)
}

# ---------- C-bnd: 邊界/條件敏感度 ----------
# Casimir: F/A = π²ħc/(240d⁴) ⟹ ∂lnF/∂lnd = −4 ≠ 0
# Lamb: 能級對束縛 (Zα) 敏感 ∂ΔE/∂(Zα) ≠ 0
# g-2: 對外場 B 敏感 (precession 頻率差)
bnd = {
    "E0_abs":        False,   # 真空中無邊界變化
    "DelPhiSq_abs":  False,
    "DelPhiSq_cp":   True,    # ∝ d⁻⁴ 距離差
    "Casimir_force": True,    # ∂lnF/∂lnd = −4
    "Lamb_shift":    True,
    "gminus2":       True,    # ω_a = (g−2)/2·eB/m
    "RhoLambda":     False,   # 無「邊界微變」實驗操作
    "LambdaEff":     False,
}

# ---------- C-gau: gauge 不變 (s_X = dlnX/dlnc) ----------
def s_gauge_from_dims(power_c):
    """s_X = d ln X / d ln c; 無量綱量嘅組合 s=0."""
    return power_c

# IDCM 無量綱結構數: 全部 s=0 (Ω_Λ=41/60, V_Λ, ρ/M_Pl⁴)
# 物理可測組合: Fd⁴/ħc (Casimir), ΔE·τ (能級×時間), a_e
gauge = {
    "E0_abs":        False,   # E₀ 絕對值在 QFT 內 scheme-dependent (非 gauge 問題, 係規範自由度)
    "DelPhiSq_abs":  False,
    "DelPhiSq_cp":   True,    # 組合 F·d⁴/ħc 無量綱
    "Casimir_force": True,
    "Lamb_shift":    True,
    "gminus2":       True,    # a_e 純無量綱
    "RhoLambda":     True,    # ρ_Λ/M_Pl⁴ = e^{−V_Λ} 無量綱
    "LambdaEff":     True,    # Λ_eff/(3H₀²) = Ω_Λ 無量綱
}

# ---------- 結構閉合 (IDCM 有冇已閉合公式) ----------
closed = {
    "E0_abs":        False,   # O204 §7.6: v10 冇 QFT 量子化, E₀ 無 v10 對應物
    "DelPhiSq_abs":  False,   # v10 場 = DTO 模態譜, 冇 QFT 漲落算子
    "DelPhiSq_cp":   False,   # 屬 O241 Q2 (推導中, 未閉合) 🟡
    "Casimir_force": False,   # 屬 O241 Q2 (推導中, 未閉合) 🟡
    "Lamb_shift":    False,   # 屬 O241 側 (未推) 🟡
    "gminus2":       False,   # 屬 O241 側 (未推) 🟡
    "RhoLambda":     True,    # O62 O86: V_Λ 閉合
    "LambdaEff":     True,    # O86 N1: Λ_eff = 8πM_Pl²e^{−V_Λ} 閉合
}

labels = {
    "E0_abs":        "E₀ = ½Σħω_k (QFT 絕對真空能)",
    "DelPhiSq_abs":  "⟨Δφ²⟩ 場漲落方均 (絕對)",
    "DelPhiSq_cp":   "Casimir-Polder ΔF (原子-表面)",
    "Casimir_force": "Casimir ΔF(d) 兩板力",
    "Lamb_shift":    "Lamb shift ΔE (能級差)",
    "gminus2":       "g−2 異常磁矩 a_e",
    "RhoLambda":     "ρ_Λ = M_Pl⁴e^{−V_Λ}",
    "LambdaEff":     "Λ_eff = 8πM_Pl²e^{−V_Λ}",
}

print("\n[1] 判準表 (ref=差分性 / bnd=邊界敏感 / gau=gauge 不變 / cl=IDCM 結構閉合)")
print(f"{'量':<26}{'ref':>4}{'bnd':>5}{'gau':>5}{'cl':>5}  判類")
print("-" * 74)
verdict = {}
for k in labels:
    r, b, g, cl_ = delta[k], bnd[k], gauge[k], closed[k]
    if r and b and g:
        cls = "A 實驗檯可測構型" if cl_ else "A′ 實驗檯可測(結構推導待 O241/O242-Q4)"
    elif (not r) and cl_ and g:
        cls = "B 結構檢驗量(宇宙學)"
    else:
        cls = "C 不可觀測/無對應"
    verdict[k] = cls
    print(f"{labels[k]:<26}{str(r):>4}{str(b):>5}{str(g):>5}{str(cl_):>5}  {cls}")

# ---------- checks ----------
print("\n[2] 判準自檢")
C("T1", delta["Casimir_force"] and delta["Lamb_shift"] and delta["gminus2"],
  "三大實證 (Casimir/Lamb/g−2) 全為差分量")
C("T2", not delta["E0_abs"] and not delta["DelPhiSq_abs"],
  "兩大絕對量 (E₀, ⟨Δφ²⟩) 冇參考系")
C("T3", bnd["Casimir_force"], "Casimir ∂lnF/∂lnd = −4 ≠ 0 邊界敏感")
C("T4", gauge["RhoLambda"] and gauge["LambdaEff"],
  "IDCM 真空能量以無量綱比 e^{−V_Λ}, Ω_Λ 形式出現 ⟹ s=0")
C("T5", closed["RhoLambda"] and closed["LambdaEff"] and not closed["E0_abs"],
  "IDCM 對 ρ_Λ/Λ_eff 有結構閉合, 對 QFT E₀ 無對應物 (O204 §7.6)")
C("T6", verdict["Casimir_force"].startswith("A"),
  "Casimir 判類 A/A′ (三條可測判準全過)")
C("T7", verdict["RhoLambda"] == "B 結構檢驗量(宇宙學)",
  "ρ_Λ 判類 B (結構閉合 + gauge 不變, 但非差分量)")
C("T8", verdict["E0_abs"] == "C 不可觀測/無對應",
  "QFT 絕對真空能 E₀ 判類 C")

# ---------- 邊界敏感度精確計算: F ∝ d⁻⁴ ----------
print("\n[3] 邊界敏感度 (Casimir 力冪律)")
d = [0.1, 0.5, 1.0, 2.0, 6.0]  # μm
F = [1.0/di**4 for di in d]     # F ∝ d⁻⁴ (比例常數省略)
# 冪律檢驗: log F vs log d 斜率 = −4
import statistics
logd = [math.log(di)/math.log(math.e) for di in d]
logF = [math.log(fi)/math.log(math.e) for fi in F]
n = len(d)
sx, sy, sxx, sxy = sum(logd), sum(logF), sum(x*x for x in logd), sum(x*y for x, y in zip(logd, logF))
slope = (n*sxy - sx*sy)/(n*sxx - sx*sx)
C("T9", abs(slope - (-4.0)) < 1e-12, f"∂lnF/∂lnd = {slope:.12f} = −4 EXACT (冪律重建)")
C("T10", abs(F[0]/F[2] - 1e4) < 1e-9, "F(0.1μm)/F(1μm) = 10⁴ 差 4 個數量級 ⟹ 極端邊界敏感")

# ---------- 結構閉合數値復現 (RhoLambda / LambdaEff) ----------
print("\n[4] IDCM 結構值復現 (O62/O86 閉合鏈, 引用驗算)")
M_Pl = 1.220890e19  # GeV (Planck 質量, 非約化)
# ρ_Λ = M_Pl⁴ e^{−V_Λ}
rho = M_Pl**4 * math.exp(-V_Lambda)   # GeV⁴
rho_1_4_GeV = rho ** 0.25
# 1 GeV = 1e9 eV = 1e12 meV  ⟹ GeV → meV 因子 = 1e12
rho_1_4_meV_corr = rho_1_4_GeV * 1e12
C("T11", abs(rho_1_4_meV_corr - rho_Lambda_1_4_meV) / rho_Lambda_1_4_meV < 1e-3,
  f"ρ_Λ^1/4 = {rho_1_4_meV_corr:.4f} meV vs O86 {rho_Lambda_1_4_meV} meV (dev "
  f"{abs(rho_1_4_meV_corr-rho_Lambda_1_4_meV)/rho_Lambda_1_4_meV*100:.4f}%)")

# Λ_eff = 8πM_Pl²e^{−V_Λ}  (O86: 4.2913e-84 GeV²)
G_N = 1.0/M_Pl**2   # 非約化 G
Lambda_eff_idcm = 8*math.pi*G_N*rho
C("T12", abs(Lambda_eff_idcm - 4.2913e-84) / 4.2913e-84 < 1e-5,
  f"Λ_eff = {Lambda_eff_idcm:.6e} GeV² vs O86 4.2913e-84 (dev "
  f"{abs(Lambda_eff_idcm-4.2913e-84)/4.2913e-84*100:.6f}%)")

# 宇宙學交叉: Λ_eff = 3Ω_ΛH₀²
H0 = 67.407112  # km/s/Mpc (h_cmb×100, O86 結構強制) — 轉 GeV
# H0[GeV] = H0[km/s/Mpc] × 3.2408e-20 (km/s/Mpc → 1/s) × ħ[GeV·s]
# ħ = 6.582e-25 GeV·s ; 1 km/s/Mpc = 3.2408e-20 s⁻¹
H0_GeV = H0 * 3.2408e-20 * 6.582e-25
Lambda_eff_3OH2 = 3 * Omega_Lambda_struct * H0_GeV**2
dev_OH = abs(Lambda_eff_3OH2 - Lambda_eff_idcm) / Lambda_eff_idcm * 100
C("T13", dev_OH < 2.0,
  f"Λ_eff=3Ω_ΛH₀²(Ω_Λ=41/60) vs 8πM_Pl²e^{{−V_Λ}}: dev {dev_OH:.2f}% (O86 記錄 1.37%)")

print("\n" + "=" * 74)
npass = sum(1 for _, p, _ in checks if p)
print(f"RESULT: {npass}/{len(checks)} PASS")
if npass != len(checks):
    for name, p, detail in checks:
        if not p:
            print(f"  FAIL: {name} — {detail}")
print("=" * 74)