#!/usr/bin/env python3
"""
O66 01: M_comp 第一性原理 — 結構分析
======================================
M_comp = 3.69e13 GeV (中微子 Seesaw 壓抑尺度)
已知: log10(M_pl/M_comp) = 5.5197 ≈ 1/γ₆ = 5.5329 (0.24%)

目標: 揾出精確結構形式 + 機制鏈

核心線索:
  ★ log10(M_pl/M_comp) = 5.5197 ≈ 1/γ₆ = 5.5329 (0.24%)
  → M_comp = M_pl × 10^(-1/γ₆) = 3.58e13 (2.96%)

探索方向:
  1. 精確值: log10(M_pl/M_comp) 嘅精確結構
  2. 1/γ₆ 修正: 1/γ₆ - δ 嘅 δ 結構
  3. 物理機制: RGE / warp / instanton
  4. 同 O62 Λ 嘅 γ₆ 雙重角色
"""
import sys, os, math
import json
from pathlib import Path

# ──────────────────────────────────────────────
# 路徑設置
# ──────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
O66_DIR = SCRIPT_DIR.parent
DATA_DIR = O66_DIR / "data"
DOCS_DIR = O66_DIR / "docs"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────
# 常數
# ──────────────────────────────────────────────
phi = (1 + math.sqrt(5)) / 2
psi = (1 - math.sqrt(5)) / 2  # algebraic conjugate
B = 4
Nd = 44
M = 33

# 物理常數
M_pl = 1.2209e19  # GeV
v = 246.0  # GeV (Higgs VEV)
m_nu3 = 0.0536e-9  # GeV (ν₃ 質量)

# K_Chain 諧波
g = {n: 4 * math.sin(n * math.pi / 88)**2 for n in range(1, 45)}

# 已知 M_comp (由 m_ν₃ = (γ₆v)²/M_comp 定義)
M_comp_fit = 3.69e13  # GeV
M_comp_exact = (g[6] * v)**2 / m_nu3  # 精確由 Seesaw 反推

# φ-恆等式 (odd n: φ^n - φ^{-n})
phi_odd = {1: 1, 3: 4, 5: 11, 7: 29, 9: 76, 11: 199}

# Lucas 數
L = {0: 2, 1: 1, 2: 3, 3: 4, 4: 7, 5: 11, 6: 18, 7: 29, 8: 47, 9: 76, 10: 123}

# Fibonacci 數
F = {0: 0, 1: 1, 2: 1, 3: 2, 4: 3, 5: 5, 6: 8, 7: 13, 8: 21, 9: 34, 10: 55}

print("=" * 80)
print("O66 01: M_comp 第一性原理 — 結構分析")
print("=" * 80)

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

# ============================================================
# 0. 基礎
# ============================================================
print("\n[0] 基礎數值")
print(f"  M_pl = {M_pl:.6e} GeV")
print(f"  M_comp (fit) = {M_comp_fit:.6e} GeV")
print(f"  M_comp (Seesaw exact) = {M_comp_exact:.6e} GeV")
ratio = M_pl / M_comp_fit
ratio_exact = M_pl / M_comp_exact
log10_r = math.log10(ratio)
log10_r_exact = math.log10(ratio_exact)
ln_r = math.log(ratio)
print(f"  M_pl/M_comp = {ratio:.4e}")
print(f"  log10(M_pl/M_comp) = {log10_r:.6f} (fit)")
print(f"  log10(M_pl/M_comp) = {log10_r_exact:.6f} (Seesaw exact)")
print(f"  ln(M_pl/M_comp) = {ln_r:.6f}")
print(f"  γ₆ = {g[6]:.10f}")
print(f"  1/γ₆ = {1/g[6]:.6f}")
print(f"  1/γ₆ vs log10_r: Δ = {1/g[6] - log10_r:.6f} " +
      f"({abs(1/g[6]-log10_r)/log10_r*100:.4f}%)")
print(f"  1/γ₆ vs log10_r_exact: Δ = {1/g[6] - log10_r_exact:.6f} " +
      f"({abs(1/g[6]-log10_r_exact)/log10_r_exact*100:.4f}%)")

# ============================================================
# 1. log10(M_pl/M_comp) 精確值探索
# ============================================================
print("\n" + "=" * 80)
print("[1] log10(M_pl/M_comp) = 5.5197 精確結構")
print("=" * 80)

# 目標值
target = log10_r
print(f"  目標 = {target:.10f}")

# 1a. 1/γ₆ 家族
print("\n  1a. 1/γ₆ 家族:")
inv_g6 = 1/g[6]
print(f"    1/γ₆ = {inv_g6:.10f} (Δ = {inv_g6 - target:.6f}, {abs(inv_g6-target)/target*100:.4f}%)")

# 1b. 1/γ₆ - φ-identity 修正
print("\n  1b. 1/γ₆ - φ-identity 修正:")
for name, val in [("1/76", 1/76), ("1/29", 1/29), ("1/11", 1/11), 
                   ("1/4", 1/4), ("1/199", 1/199), ("1/φ⁵", 1/phi**5),
                   ("1/φ⁷", 1/phi**7), ("1/φ⁹", 1/phi**9)]:
    cand = inv_g6 - val
    err = abs(cand - target) / target * 100
    print(f"    1/γ₆ - {name} = {cand:.10f} (Δ = {cand - target:.6f}, {err:.4f}%)")

# 1c. 1/γ₆ - n/Nd 修正
print("\n  1c. 1/γ₆ - n/Nd 修正:")
for n in [1, 2, 3, 4, 5, 6, 7, 8, 11, 22, 44]:
    cand = inv_g6 - n/Nd
    err = abs(cand - target) / target * 100
    print(f"    1/γ₆ - {n}/{Nd} = {cand:.10f} (Δ = {cand - target:.6f}, {err:.4f}%)")

# 1d. 946/171 候選
print("\n  1d. 946/171 候選:")
cand_946 = 946/171
err = abs(cand_946 - target) / target * 100
print(f"    946/171 = {cand_946:.10f} (Δ = {cand_946 - target:.6f}, {err:.4f}%)")
print(f"    946 = C(44,2) = 44×43/2 = Beat 空間維度")
print(f"    171 = T₁₈ = 18×19/2 = 三角數")
print(f"    171 = 9×19 = N_gen² × (N_d - F₈ - B)")
print(f"    946/171 = (44×43)/(18×19) = 1892/342 = 5.53216")

# 1e. 其他候選
print("\n  1e. 其他候選:")
candidates = {
    "L₅/2 (11/2)": 11/2,
    "Nd/8 (44/8)": Nd/8,
    "F₆-F₅ (8-5)": 3,
    "L₆-φ² (18-φ²)": 18 - phi**2,
    "L₆-φ (18-φ)": 18 - phi,
    "L₅-φ⁻¹ (11-φ⁻¹)": 11 - 1/phi,
    "L₄+L₃-φ⁻¹ (7+4-φ⁻¹)": 7+4-1/phi,
    "F₆+L₄-φ (8+7-φ)": 8+7-phi,
    "F₇+L₃-φ² (13+4-φ²)": 13+4-phi**2,
    "L₆-φ⁻³ (18-φ⁻³)": 18 - phi**(-3),
    "L₆-φ⁻⁴ (18-φ⁻⁴)": 18 - phi**(-4),
    "L₇-φ⁵ (29-φ⁵)": 29 - phi**5,
    "L₆/φ² (18/φ²)": 18/phi**2,
    "L₆/φ (18/φ)": 18/phi,
    "L₅/φ (11/φ)": 11/phi,
    "L₅/φ² (11/φ²)": 11/phi**2,
    "√(L₇×L₃) (√(29×4))": math.sqrt(29*4),
    "√(L₆×L₄) (√(18×7))": math.sqrt(18*7),
    "F₉/L₄ (34/7)": 34/7,
    "F₈/L₃ (21/4)": 21/4,
    "F₇/L₂ (13/3)": 13/3,
    "F₆/L₁ (8/1)": 8/1,
    "γ₆⁻¹×(1-γ₆)": 1/g[6]*(1-g[6]),
    "γ₆⁻¹×(1-γ₆/2)": 1/g[6]*(1-g[6]/2),
    "γ₆⁻¹ - γ₆": 1/g[6] - g[6],
    "γ₆⁻¹ - γ₆/2": 1/g[6] - g[6]/2,
    "γ₆⁻¹ - γ₆²": 1/g[6] - g[6]**2,
    "γ₆⁻¹ - γ₆²/2": 1/g[6] - g[6]**2/2,
    "γ₆⁻¹ - γ₆³": 1/g[6] - g[6]**3,
    "γ₆⁻¹ - ε²/γ₆": 1/g[6] - (phi**(-1)/4)**2/g[6],
    "γ₆⁻¹ - 1/(L₄×φ²)": 1/g[6] - 1/(7*phi**2),
    "γ₆⁻¹ - 1/(L₅+L₄)": 1/g[6] - 1/(11+7),
    "γ₆⁻¹ - 1/(2×F₇)": 1/g[6] - 1/(2*13),
    "γ₆⁻¹ - 1/(F₇+L₆)": 1/g[6] - 1/(13+18),
    "γ₆⁻¹ - 1/(2×Nd)": 1/g[6] - 1/(2*Nd),
    "γ₆⁻¹ - 1/(L₅+L₆)": 1/g[6] - 1/(11+18),
    "γ₆⁻¹ - 1/(h11)": 1/g[6] - 1/36,
    "γ₆⁻¹ - 1/(h21)": 1/g[6] - 1/98,
    "γ₆⁻¹ - 1/(B×Nd)": 1/g[6] - 1/(4*44),
    "γ₆⁻¹ - 1/(M×γ₆)": 1/g[6] - 1/(33*g[6]),
    "γ₆⁻¹ - 1/(|χ|)": 1/g[6] - 1/124,
    "γ₆⁻¹ - 1/(|χ|+B)": 1/g[6] - 1/(124+4),
    "γ₆⁻¹ - 1/(|χ|+Nd)": 1/g[6] - 1/(124+44),
    "γ₆⁻¹ - 1/(CY₃)": 1/g[6] - 1/134,
    "γ₆⁻¹ - 1/(2×CY₃)": 1/g[6] - 1/(2*134),
    "γ₆⁻¹ - 1/(946)": 1/g[6] - 1/946,
    "γ₆⁻¹ - 1/(946/2)": 1/g[6] - 1/(946/2),
    "γ₆⁻¹ - 1/(Σγ)": 1/g[6] - 1/90,
    "γ₆⁻¹ - 1/(Σγ_odd)": 1/g[6] - 1/88,
    "γ₆⁻¹ - 1/(90×φ)": 1/g[6] - 1/(90*phi),
    "γ₆⁻¹ - 1/(L₅×L₄)": 1/g[6] - 1/(11*7),
    "γ₆⁻¹ - 1/(L₅²)": 1/g[6] - 1/121,
    "γ₆⁻¹ - 1/(3×L₅)": 1/g[6] - 1/(3*11),
    "γ₆⁻¹ - 1/(4×L₅)": 1/g[6] - 1/(4*11),
    "γ₆⁻¹ - 1/(5×L₅)": 1/g[6] - 1/(5*11),
    "γ₆⁻¹ - 1/(6×L₅)": 1/g[6] - 1/(6*11),
    "γ₆⁻¹ - 1/(7×L₅)": 1/g[6] - 1/(7*11),
    "γ₆⁻¹ - 1/(8×L₅)": 1/g[6] - 1/(8*11),
    "γ₆⁻¹ - 1/(9×L₅)": 1/g[6] - 1/(9*11),
    "γ₆⁻¹ - 1/(B×L₅)": 1/g[6] - 1/(4*11),
    "γ₆⁻¹ - 1/(γ₆×100)": 1/g[6] - 1/(g[6]*100),
    "γ₆⁻¹ - 1/(γ₆×L₅)": 1/g[6] - 1/(g[6]*11),
    "γ₆⁻¹ - 1/(γ₆×Nd)": 1/g[6] - 1/(g[6]*Nd),
    "γ₆⁻¹ - 1/(γ₆²×100)": 1/g[6] - 1/(g[6]**2*100),
    "γ₆⁻¹ × (1 - γ₆/ln(10))": 1/g[6]*(1 - g[6]/math.log(10)),
    "γ₆⁻¹ × (1 - γ₆/Nd)": 1/g[6]*(1 - g[6]/Nd),
    "γ₆⁻¹ × (1 - γ₆/M)": 1/g[6]*(1 - g[6]/M),
}

best = []
for name, val in candidates.items():
    err = abs(val - target) / target * 100
    best.append((err, name, val))
    if err < 1:
        print(f"    {name} = {val:.10f} (Δ = {val - target:.6f}, {err:.4f}%)")

best.sort()
print(f"\n  最佳 5 個:")
for err, name, val in best[:5]:
    print(f"    {err:.4f}% | {name} = {val:.10f}")

# ============================================================
# 2. 1/γ₆ 精確修正: 1/γ₆ - 1/76 假設
# ============================================================
print("\n" + "=" * 80)
print("[2] ★ 1/γ₆ - 1/76 假設驗證")
print("=" * 80)

# 76 = φ⁹ - φ⁻⁹ (φ-identity)
cand = 1/g[6] - 1/76
err = abs(cand - target) / target * 100
print(f"  1/γ₆ - 1/76 = {cand:.10f}")
print(f"  目標 = {target:.10f}")
print(f"  Δ = {cand - target:.6f}")
print(f"  誤差 = {err:.4f}%")
print(f"  76 = φ⁹ - φ⁻⁹ = {phi**9 - phi**(-9):.0f} ✅ 純 φ-identity")
check("1/γ₆ - 1/76 誤差 < 0.01%", err < 0.01, f"({err:.4f}%)")

# 驗證: 呢個係巧合定結構?
# 檢查其他 φ-identity 修正
print(f"\n  對照: 其他 φ-identity 修正:")
for n in [1, 3, 5, 7, 9, 11]:
    val = phi_odd[n]
    if val != 76:
        c = 1/g[6] - 1/val
        e = abs(c - target) / target * 100
        print(f"    1/γ₆ - 1/φ^{n}-φ⁻^{n}(={val}) = {c:.10f} (誤差 {e:.4f}%)")

# 檢查其他 Lucas 數修正
print(f"\n  對照: Lucas 數修正:")
for n in range(0, 11):
    val = L[n]
    if val > 0 and val != 76:
        c = 1/g[6] - 1/val
        e = abs(c - target) / target * 100
        print(f"    1/γ₆ - 1/L_{n}(={val}) = {c:.10f} (誤差 {e:.4f}%)")

# 檢查 Fibonacci 數修正
print(f"\n  對照: Fibonacci 數修正:")
for n in range(0, 11):
    val = F[n]
    if val > 0:
        c = 1/g[6] - 1/val
        e = abs(c - target) / target * 100
        print(f"    1/γ₆ - 1/F_{n}(={val}) = {c:.10f} (誤差 {e:.4f}%)")

# ============================================================
# 3. 10^(-1/γ₆) 指數結構分析
# ============================================================
print("\n" + "=" * 80)
print("[3] 10^(-1/γ₆) 指數結構 — 機制分析")
print("=" * 80)

# 3a. 自然指數形式
print("\n  3a. 自然指數形式:")
ln_comp = math.log(M_pl / M_comp_fit)
print(f"  ln(M_pl/M_comp) = {ln_comp:.6f}")
print(f"  ln(10)/γ₆ = {math.log(10)/g[6]:.6f}")
print(f"  ln(10)/γ₆ - ln(M_pl/M_comp) = {math.log(10)/g[6] - ln_comp:.6f}")

# 3b. 候選 instanton action
print("\n  3b. Instanton action S = ln(M_pl/M_comp):")
print(f"  S = {ln_comp:.6f}")
cands_S = {
    "ln(10)/γ₆": math.log(10)/g[6],
    "44/φ²": Nd/phi**2,
    "M/φ": M/phi,
    "φ⁵+1.62": phi**5 + 1.62,
    "L₆+L₄-2.29": 18+7-2.29,
    "2π²": 2*math.pi**2,
    "π²+3": math.pi**2+3,
    "F₇/F₃": 13/3,
    "L₇-L₅": 29-11,
    "γ₆×L₆": g[6]*18,
    "γ₆×Nd": g[6]*Nd,
    "γ₆×M": g[6]*M,
    "γ₆×h11": g[6]*36,
    "γ₆×h21": g[6]*98,
    "γ₆×CY₃": g[6]*134,
    "γ₆×Σγ": g[6]*90,
    "γ₆×Σγ_odd": g[6]*88,
    "γ₆×946": g[6]*946,
    "γ₆×F(γ)": g[6]*264.0821,
    "γ₆×V_Λ": g[6]*283.0821,
    "γ₆²×Nd": g[6]**2*Nd,
    "γ₆²×M": g[6]**2*M,
    "γ₆⁴×Nd": g[6]**4*Nd,
    "γ₆⁴×M": g[6]**4*M,
    "γ₆×LNd": g[6]*math.log(Nd),
    "γ₆×LM": g[6]*math.log(M),
    "γ₆×Lh11": g[6]*math.log(36),
    "γ₆×Lh21": g[6]*math.log(98),
    "γ₆×LCY3": g[6]*math.log(134),
    "γ₆×L946": g[6]*math.log(946),
}
best_S = []
for name, val in cands_S.items():
    err = abs(val - ln_comp) / ln_comp * 100
    best_S.append((err, name, val))
best_S.sort()
print(f"  最佳 S 候選:")
for err, name, val in best_S[:5]:
    print(f"    {err:.4f}% | {name} = {val:.6f}")

# 3c. RGE 形式: M_comp = M_pl × exp(-1/(β₀α))
print("\n  3c. RGE 形式:")
print(f"  M_comp/M_pl = {M_comp_fit/M_pl:.4e} = exp(-{ln_comp:.4f})")
print(f"  → 若 α = γ₆, 則 β₀ = γ₆/ln(M_pl/M_comp) = {g[6]/ln_comp:.6f}")
print(f"  → 若 α = 1/γ₆, 則 β₀ = 1/(γ₆·ln(M_pl/M_comp)) = {1/(g[6]*ln_comp):.6f}")
print(f"  → 若 α = γ₆², 則 β₀ = γ₆²/ln(M_pl/M_comp) = {g[6]**2/ln_comp:.6f}")
print(f"  → 若 α = γ₆×Nd, 則 β₀ = γ₆×Nd/ln(M_pl/M_comp) = {g[6]*Nd/ln_comp:.6f}")

# 檢查 β₀ 係唔係結構數
print(f"  β₀(α=γ₆) = {g[6]/ln_comp:.6f}")
print(f"    = 1/γ₆? {abs(g[6]/ln_comp - 1/g[6])/g[6]*100:.2f}% away")
print(f"    = 1/L₅? {abs(g[6]/ln_comp - 1/11)/11*100:.2f}% away")
print(f"    = 1/Nd? {abs(g[6]/ln_comp - 1/Nd)/Nd*100:.2f}% away")
print(f"    = ε? {abs(g[6]/ln_comp - phi**(-1)/4)/(phi**(-1)/4)*100:.2f}% away")

# 3d. Warp 形式: M_comp = M_pl × e^{-πkR}
print("\n  3d. Warp 形式 (RS):")
print(f"  M_comp = M_pl × e^(-πkR)")
print(f"  → πkR = ln(M_pl/M_comp) = {ln_comp:.6f}")
print(f"  → kR = ln(M_pl/M_comp)/π = {ln_comp/math.pi:.6f}")
print(f"  kR 候選:")
kR = ln_comp/math.pi
cands_kR = {
    "44/γ₆": Nd/g[6],
    "M/γ₆": M/g[6],
    "h11/γ₆": 36/g[6],
    "h21/γ₆": 98/g[6],
    "CY₃": 134,
    "Nd×φ": Nd*phi,
    "Nd×ε": Nd*phi**(-1)/4,
    "B×φ⁵": 4*phi**5,
    "L₆+φ": 18+phi,
    "L₇": 29,
    "F₈": 21,
    "F₉": 34,
    "Σγ": 90,
    "Nd×B": 44*4,
    "M×φ": 33*phi,
    "Nd×φ²": 44*phi**2,
    "F₉+L₄": 34+7,
    "F₈+L₆": 21+18,
    "L₆+L₅": 18+11,
    "L₇+L₅": 29+11,
    "L₇+L₆": 29+18,
    "L₇+L₄": 29+7,
    "L₅+L₄+L₃": 11+7+4,
    "L₆+L₅+L₄": 18+11+7,
}
best_kR = []
for name, val in cands_kR.items():
    err = abs(val - kR) / kR * 100
    best_kR.append((err, name, val))
best_kR.sort()
print(f"  kR = {kR:.6f}")
for err, name, val in best_kR[:5]:
    print(f"    {err:.4f}% | {name} = {val:.6f}")

# ============================================================
# 4. γ₆ 雙重角色: Λ (linear) vs M_comp (exponential)
# ============================================================
print("\n" + "=" * 80)
print("[4] γ₆ 雙重角色: Λ (linear) vs M_comp (exponential)")
print("=" * 80)

print(f"""
  γ₆ 喺 IDCM 嘅所有角色:
  ────────────────────────
  1. m_ν₃ = (γ₆v)²/M_comp  (中微子質量, 平方)
  2. Δm² 比 = 2B² = 32      (平方差比)
  3. PMNS θ₁₃ = γ₆/2³       (混合角, 線性)
  4. CKM λ³ = γ₆/2⁴         (CKM 元素, 線性)
  5. Λ = 44γ₆ = 7.95        (O57 近似, 線性)
  6. V_Λ = F(γ)+19          (O62 全譜, 立方)
  7. M_comp = M_pl×10^(-1/γ₆) (Seesaw 尺度, 指數)

  ★ 關鍵: Λ 用 γ₆ 線性, M_comp 用 1/γ₆ 指數
  → 兩者都係 γ₆, 但角色完全相反
  → 強烈暗示一個統一機制
""")

# 檢查 Λ 同 M_comp 嘅 γ₆ 關係
print(f"  Λ 44γ₆ = {44*g[6]:.4f}")
print(f"  M_comp 指數: ln(10)/γ₆ = {math.log(10)/g[6]:.4f}")
print(f"  44γ₆ × ln(10)/γ₆ = 44×ln(10) = {44*math.log(10):.4f}")
print(f"  44γ₆ + ln(10)/γ₆ = {44*g[6] + math.log(10)/g[6]:.4f}")
print(f"  (44γ₆) / (ln(10)/γ₆) = 44γ₆²/ln(10) = {44*g[6]**2/math.log(10):.4f}")

# ============================================================
# 5. M_comp 同 CY₃ 幾何 (O62 連結)
# ============================================================
print("\n" + "=" * 80)
print("[5] M_comp 同 CY₃ 幾何 (O62 連結)")
print("=" * 80)

# O62 關鍵數值
F_gamma = 264.0821292326  # F(γ) = (1/6)κ_ijk γ_i γ_j γ_k
V_lambda = 283.0821292326  # V_Λ = F(γ) + 19
sigma_kappa = -8  # Σκ = -2B

print(f"  O62 F(γ) = {F_gamma:.6f}")
print(f"  O62 V_Λ = {V_lambda:.6f}")
print(f"  Σκ = {sigma_kappa} = -2B")

# 檢查 M_comp 同 F(γ) 嘅關係
print(f"\n  M_comp 同 F(γ) 關係:")
print(f"  log10(M_pl/M_comp) × F(γ) = {log10_r * F_gamma:.6f}")
print(f"  log10(M_pl/M_comp) × V_Λ = {log10_r * V_lambda:.6f}")
print(f"  F(γ)/log10(M_pl/M_comp) = {F_gamma/log10_r:.6f}")
print(f"  V_Λ/log10(M_pl/M_comp) = {V_lambda/log10_r:.6f}")

# 檢查 F(γ) 同 1/γ₆ 嘅關係
print(f"\n  F(γ) 同 1/γ₆ 關係:")
print(f"  F(γ)/γ₆ = {F_gamma/g[6]:.6f}")
print(f"  F(γ)×γ₆ = {F_gamma*g[6]:.6f}")
print(f"  F(γ)/γ₆² = {F_gamma/g[6]**2:.6f}")
print(f"  F(γ)×γ₆² = {F_gamma*g[6]**2:.6f}")
print(f"  F(γ)/Nd = {F_gamma/Nd:.6f}")
print(f"  F(γ)/M = {F_gamma/M:.6f}")

# ============================================================
# 6. 物理機制: 從 K_Chain 到指數
# ============================================================
print("\n" + "=" * 80)
print("[6] 物理機制: 從 K_Chain 到指數")
print("=" * 80)

# 6a. K_Chain log 積分
print("\n  6a. K_Chain log 積分:")
# 積分 Σ ln(γ_n) 或類似
sum_log_gamma = sum(math.log(g[n]) for n in range(1, 45))
print(f"  Σ_{{n=1}}^{{44}} ln(γ_n) = {sum_log_gamma:.6f}")
print(f"  Σ ln(γ_n) / Nd = {sum_log_gamma/Nd:.6f}")
print(f"  Σ ln(γ_n) / 44 = {sum_log_gamma/44:.6f}")
print(f"  -Σ ln(γ_n) = {-sum_log_gamma:.6f}")
print(f"  -Σ ln(γ_n) / ln(10) = {-sum_log_gamma/math.log(10):.6f}")

# 6b. 特定 harmonic 積分
print("\n  6b. 特定 harmonic 積分:")
for n in [1, 3, 6, 7, 11, 22, 33, 44]:
    ln_g = math.log(g[n])
    print(f"  ln(γ_{n}) = {ln_g:.6f}")
    print(f"  -ln(γ_{n})/ln(10) = {-ln_g/math.log(10):.6f}")

# 6c. 對偶鏈和
print("\n  6c. 對偶鏈和:")
sum_g_odd = sum(g[n] for n in range(1, 45, 2))  # odd chain
sum_g_even = sum(g[n] for n in range(2, 45, 2))  # even chain
print(f"  Σγ_odd = {sum_g_odd:.6f}")
print(f"  Σγ_even = {sum_g_even:.6f}")
print(f"  Σγ_odd/γ₆ = {sum_g_odd/g[6]:.6f}")
print(f"  Σγ_even/γ₆ = {sum_g_even/g[6]:.6f}")

# 6d. 88-site 對偶鏈
print("\n  6d. 88-site 對偶鏈完整分析:")
# 88-site: n=1..88, γ_k = 4sin²(πk/176)
g88 = {k: 4*math.sin(k*math.pi/176)**2 for k in range(1, 89)}
g6_88 = g88[12]  # n=6 on even chain = site 12 on 88-chain
print(f"  γ₆ (44-site) = {g[6]:.10f}")
print(f"  γ₁₂ (88-site) = {g6_88:.10f}")
print(f"  γ₁₂ (88-site) = γ₆ (44-site): {abs(g[6]-g6_88) < 1e-15}")

# 6e. 1/γ₆ 嘅 88-site 意義
print(f"\n  6e. 1/γ₆ 嘅 88-site 意義:")
print(f"  1/γ₆ = {1/g[6]:.6f}")
print(f"  88/γ₆ = {88/g[6]:.6f}")
print(f"  88γ₆ = {88*g[6]:.6f}")
print(f"  88-site 對偶鏈 Σγ = {sum(g88[k] for k in range(1, 89)):.6f}")
print(f"  88-site Σγ / γ₆ = {sum(g88[k] for k in range(1, 89))/g[6]:.6f}")

# ============================================================
# 7. 零參數結構: M_comp 嘅精確公式
# ============================================================
print("\n" + "=" * 80)
print("[7] ★ 零參數結構候選")
print("=" * 80)

# 候選 1: M_comp = M_pl × 10^(-1/γ₆ + 1/76)
# By symmetry, maybe M_comp = M_pl × 10^(-(1/γ₆ - 1/76))
print("\n  候選 1: M_comp = M_pl × 10^(-(1/γ₆ - 1/76))")
cand1 = M_pl * 10**(-(1/g[6] - 1/76))
err1 = abs(cand1 - M_comp_fit) / M_comp_fit * 100
print(f"    1/γ₆ - 1/76 = {1/g[6] - 1/76:.10f}")
print(f"    M_comp = {cand1:.4e} GeV")
print(f"    M_comp(fit) = {M_comp_fit:.4e} GeV")
print(f"    誤差 = {err1:.4f}%")
check("候選1: M_comp < 1%", err1 < 1, f"({err1:.4f}%)")

# 候選 2: M_comp = M_pl × 10^(-L₅/2)  (L₅/2 = 11/2 = 5.5)
print("\n  候選 2: M_comp = M_pl × 10^(-L₅/2)")
cand2 = M_pl * 10**(-11/2)
err2 = abs(cand2 - M_comp_fit) / M_comp_fit * 100
print(f"    L₅/2 = 5.5")
print(f"    M_comp = {cand2:.4e} GeV")
print(f"    M_comp(fit) = {M_comp_fit:.4e} GeV")
print(f"    誤差 = {err2:.4f}%")

# 候選 3: M_comp = M_pl × 10^(-(L₅/2 - 1/76))
print("\n  候選 3: M_comp = M_pl × 10^(-(L₅/2 - 1/76))")
cand3 = M_pl * 10**(-(11/2 - 1/76))
err3 = abs(cand3 - M_comp_fit) / M_comp_fit * 100
print(f"    L₅/2 - 1/76 = {11/2 - 1/76:.10f}")
print(f"    M_comp = {cand3:.4e} GeV")
print(f"    M_comp(fit) = {M_comp_fit:.4e} GeV")
print(f"    誤差 = {err3:.4f}%")

# 候選 4: M_comp = M_pl × 10^(-(946/171 - 1/76))
print("\n  候選 4: M_comp = M_pl × 10^(-(946/171 - 1/76))")
cand4 = M_pl * 10**(-(946/171 - 1/76))
err4 = abs(cand4 - M_comp_fit) / M_comp_fit * 100
print(f"    946/171 - 1/76 = {946/171 - 1/76:.10f}")
print(f"    946/171 = {946/171:.10f}")
print(f"    M_comp = {cand4:.4e} GeV")
print(f"    M_comp(fit) = {M_comp_fit:.4e} GeV")
print(f"    誤差 = {err4:.4f}%")

# 候選 5: M_comp = M_pl / (2 × h¹¹ × h²¹ × N_d)  (CKM script 嘅)
print("\n  候選 5: M_comp = M_pl / (2 × h¹¹ × h²¹ × N_d)")
cand5 = M_pl / (2 * 36 * 98 * Nd)
err5 = abs(cand5 - M_comp_fit) / M_comp_fit * 100
print(f"    M_comp = {cand5:.4e} GeV")
print(f"    M_comp(fit) = {M_comp_fit:.4e} GeV")
print(f"    誤差 = {err5:.4f}%")

# 候選 6: M_comp = M_pl × 10^(-(1/γ₆ - γ₆/2))
print("\n  候選 6: M_comp = M_pl × 10^(-(1/γ₆ - γ₆/2))")
cand6 = M_pl * 10**(-(1/g[6] - g[6]/2))
err6 = abs(cand6 - M_comp_fit) / M_comp_fit * 100
print(f"    1/γ₆ - γ₆/2 = {1/g[6] - g[6]/2:.10f}")
print(f"    M_comp = {cand6:.4e} GeV")
print(f"    M_comp(fit) = {M_comp_fit:.4e} GeV")
print(f"    誤差 = {err6:.4f}%")

# 候選 7: 用 e 底: M_comp = M_pl × e^(-ln(10)/γ₆)
print("\n  候選 7: M_comp = M_pl × e^(-ln(10)/γ₆)")
cand7 = M_pl * math.exp(-math.log(10)/g[6])
err7 = abs(cand7 - M_comp_fit) / M_comp_fit * 100
print(f"    ln(10)/γ₆ = {math.log(10)/g[6]:.6f}")
print(f"    M_comp = {cand7:.4e} GeV")
print(f"    M_comp(fit) = {M_comp_fit:.4e} GeV")
print(f"    誤差 = {err7:.4f}%")

# 候選 8: M_comp = M_pl × 10^(-946/171)  (純 beat 空間)
print("\n  候選 8: M_comp = M_pl × 10^(-946/171)")
cand8 = M_pl * 10**(-946/171)
err8 = abs(cand8 - M_comp_fit) / M_comp_fit * 100
print(f"    946/171 = {946/171:.10f}")
print(f"    M_comp = {cand8:.4e} GeV")
print(f"    M_comp(fit) = {M_comp_fit:.4e} GeV")
print(f"    誤差 = {err8:.4f}%")

# 候選 9: M_comp = M_pl × 10^(-(1/γ₆ - 1/L₉))  (L₉=76)
print("\n  候選 9: M_comp = M_pl × 10^(-(1/γ₆ - 1/L₉))")
cand9 = M_pl * 10**(-(1/g[6] - 1/L[9]))
err9 = abs(cand9 - M_comp_fit) / M_comp_fit * 100
print(f"    1/γ₆ - 1/L₉ = {1/g[6] - 1/L[9]:.10f}")
print(f"    L₉ = {L[9]}")
print(f"    M_comp = {cand9:.4e} GeV")
print(f"    M_comp(fit) = {M_comp_fit:.4e} GeV")
print(f"    誤差 = {err9:.4f}%")

# 候選 10: M_comp = M_pl × 10^(-(1/γ₆ - γ₆²/2))
print("\n  候選 10: M_comp = M_pl × 10^(-(1/γ₆ - γ₆²/2))")
cand10 = M_pl * 10**(-(1/g[6] - g[6]**2/2))
err10 = abs(cand10 - M_comp_fit) / M_comp_fit * 100
print(f"    1/γ₆ - γ₆²/2 = {1/g[6] - g[6]**2/2:.10f}")
print(f"    M_comp = {cand10:.4e} GeV")
print(f"    M_comp(fit) = {M_comp_fit:.4e} GeV")
print(f"    誤差 = {err10:.4f}%")

# 候選 11: M_comp = M_pl × 10^(-(1/γ₆ - 1/264))  (264 = 6Nd)
print("\n  候選 11: M_comp = M_pl × 10^(-(1/γ₆ - 1/264))")
cand11 = M_pl * 10**(-(1/g[6] - 1/264))
err11 = abs(cand11 - M_comp_fit) / M_comp_fit * 100
print(f"    1/γ₆ - 1/264 = {1/g[6] - 1/264:.10f}")
print(f"    264 = 6Nd = 3×Σγ_odd")
print(f"    M_comp = {cand11:.4e} GeV")
print(f"    M_comp(fit) = {M_comp_fit:.4e} GeV")
print(f"    誤差 = {err11:.4f}%")

# 收集所有候選
all_candidates = [
    ("1/γ₆ - 1/76", 1/g[6] - 1/76, cand1, err1),
    ("L₅/2 (5.5)", 11/2, cand2, err2),
    ("L₅/2 - 1/76", 11/2-1/76, cand3, err3),
    ("946/171 - 1/76", 946/171-1/76, cand4, err4),
    ("M_pl/(2×h¹¹×h²¹×Nd)", None, cand5, err5),
    ("1/γ₆ - γ₆/2", 1/g[6]-g[6]/2, cand6, err6),
    ("e^(-ln(10)/γ₆)", None, cand7, err7),
    ("946/171", 946/171, cand8, err8),
    ("1/γ₆ - 1/L₉", 1/g[6]-1/L[9], cand9, err9),
    ("1/γ₆ - γ₆²/2", 1/g[6]-g[6]**2/2, cand10, err10),
    ("1/γ₆ - 1/264", 1/g[6]-1/264, cand11, err11),
]
all_candidates.sort(key=lambda x: x[3])

print(f"\n  ★ 所有候選排序 (按誤差):")
print(f"  {'候選':>30} | {'log10':>10} | {'M_comp (GeV)':>16} | {'誤差':>8}")
print("-" * 70)
for name, log10_val, mcomp, err in all_candidates:
    if log10_val is not None:
        log10_str = f"{log10_val:.6f}"
    else:
        log10_str = "N/A"
    print(f"  {name:>30} | {log10_str:>10} | {mcomp:>16.4e} | {err:>7.4f}%")

# ============================================================
# 8. 總結
# ============================================================
print("\n" + "=" * 80)
print("O66 01 總結")
print("=" * 80)
print(f"""
M_comp 結構分析結果:
─────────────────────────────────

核心線索 (已知):
  log10(M_pl/M_comp) = {target:.6f}
  ≈ 1/γ₆ = {1/g[6]:.6f} (誤差 {abs(1/g[6]-target)/target*100:.4f}%)

最佳候選 (新發現):
  {all_candidates[0][0]}: log10 = {all_candidates[0][1]:.10f}, M_comp = {all_candidates[0][2]:.4e}, 誤差 {all_candidates[0][3]:.4f}%

誠實標記:
  🟡 所有候選都係 search 出嚟 (唔係 derive)
  🟡 1/γ₆ 喺指數冇第一性原理動機
  🔴 需要機制推導 (RGE/warp/instanton)
  🔴 m_ν₃ 進一步驗證未做 (Σm_ν, Δm²₂₁, m_ββ)
""")

# 儲存結果
results = {
    "test": "O66 01: M_comp 結構分析",
    "log10_target": float(target),
    "inv_gamma6": float(1/g[6]),
    "inv_gamma6_err_pct": float(abs(1/g[6]-target)/target*100),
    "best_candidate": {
        "name": all_candidates[0][0],
        "log10_value": float(all_candidates[0][1]) if all_candidates[0][1] is not None else None,
        "M_comp": float(all_candidates[0][2]),
        "err_pct": float(all_candidates[0][3])
    },
    "top5_candidates": [
        {"name": c[0], "log10": float(c[1]) if c[1] is not None else None,
         "M_comp": float(c[2]), "err_pct": float(c[3])}
        for c in all_candidates[:5]
    ],
    "passed": passed, "failed": failed
}
with open(DATA_DIR / "01_mcomp_analysis.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 O66 01 完成!")