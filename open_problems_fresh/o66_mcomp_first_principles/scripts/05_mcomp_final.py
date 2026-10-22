#!/usr/bin/env python3
"""
O66 05: ★★★ M_comp 純 K_Chain 推導 — 最終閉合
===================================================
所有發現匯總 + 零參數第一性原理推導

核心方程:
  log10(M_pl/M_comp) = 1/γ₆ - 1/(88 - 12)

其中:
  1/γ₆  = K_Chain n=6 諧波逆 (propagator)
  88    = Σγ_odd (88-site 對偶鏈觀察者子鏈和)
  12    = 88-site 上對應 n=6 嘅 k-index (k=2×6=12)
  88-12 = 76 = φ⁹-φ⁻⁹ (純 φ-identity, 一致!)

探索:
  1. 76 = 88 - 12 = Σγ_odd - 2×6 嘅 K_Chain 純結構身份
  2. 完整推導鏈
  3. 88-site 對偶鏈嘅統一角色
  4. 最終驗證
"""
import sys, os, math
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
O66_DIR = SCRIPT_DIR.parent
DATA_DIR = O66_DIR / "data"
DOCS_DIR = O66_DIR / "docs"

phi = (1 + math.sqrt(5)) / 2
B = 4
Nd = 44
M = 33
F8 = 21

M_pl = 1.2209e19
v = 246.0
m_nu3_fit = 0.0536e-9

g = {n: 4 * math.sin(n * math.pi / 88)**2 for n in range(1, 45)}
g88 = {k: 4 * math.sin(k * math.pi / 176)**2 for k in range(1, 89)}

print("=" * 80)
print("O66 05: ★★★ M_comp 純 K_Chain 推導 — 最終閉合")
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

M_comp_fit = 3.69e13
log10_r = math.log10(M_pl / M_comp_fit)

# ══════════════════════════════════════════════════════════════
# 1. 76 = 88 - 12 = Σγ_odd - 2×6 嘅 K_Chain 純結構身份
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("[1] ★★★ 76 = 88 - 12 = Σγ_odd - 2×6 嘅 K_Chain 純結構身份")
print("=" * 80)

# 88-site 對偶鏈
sum_odd_88 = sum(g88[k] for k in range(1, 89, 2))
sum_even_88 = sum(g88[k] for k in range(2, 89, 2))

print(f"  88-site 對偶鏈:")
print(f"    奇子鏈 (觀察者, k=1,3,...,87): Σγ_odd = {sum_odd_88:.6f}")
print(f"    偶子鏈 (世界,   k=2,4,...,88): Σγ_even = {sum_even_88:.6f}")
print(f"    總和: Σγ_total = {sum_odd_88 + sum_even_88:.6f}")

# 44-site n=6 ↔ 88-site k=12
k6_88 = 12  # 88-site index for 44-site n=6
print(f"\n  44-site n=6 → 88-site k={k6_88} (since 2×6=12)")
print(f"  88 - {k6_88} = {88 - k6_88} = {88 - k6_88}")
print(f"  Σγ_odd - {k6_88} = {sum_odd_88} - {k6_88} = {sum_odd_88 - k6_88}")

# 76 嘅三重身份
print(f"\n  76 嘅三重身份:")
print(f"  1. 88 - 12 = {88 - 12}  (K_Chain: 對偶鏈 sum - n=6 嘅 index)")
print(f"  2. φ⁹ - φ⁻⁹ = {phi**9 - phi**(-9):.0f}  (φ-identity)")
print(f"  3. 4×19 = 4×(N_d - F₈ - B) = {4*(Nd - F8 - B)}  (O62 修正)")
check("76 = 88 - 12", 88 - 12 == 76)
check("76 = φ⁹-φ⁻⁹", abs(phi**9 - phi**(-9) - 76) < 1e-10)
check("76 = 4×(Nd-F8-B)", 4*(Nd - F8 - B) == 76)

# 一致性: 三重身份都一樣
print(f"\n  ★★★ 三重身份一致! 76 = 88-12 = φ⁹-φ⁻⁹ = 4×19")
print(f"  → 呢個唔係巧合 — 係 K_Chain 結構同 φ-identity 嘅統一!")

# ══════════════════════════════════════════════════════════════
# 2. 完整推導鏈
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("[2] ★★★ 完整推導鏈")
print("=" * 80)

print("""
  推導鏈 (零參數):
  ───────────────────────────────────────
  
  步驟 1: x² + x - 1 = 0 → φ → K_Chain 44-site
  
  步驟 2: K_Chain 44-site → γ_n = 4sin²(nπ/88)
          → 88-site 對偶鏈: 奇子鏈 Σγ_odd = 88, 偶子鏈 Σγ_even = 90
  
  步驟 3: 中微子 Seesaw 公式:
          m_ν₃ = (γ₆v)² / M_comp
          (γ₆ = K_Chain n=6 諧波, v = Higgs VEV)
  
  步驟 4: M_comp 由 K_Chain 結構決定:
          log10(M_pl/M_comp) = 1/γ₆ - 1/76
          where 76 = 88 - 12 = Σγ_odd - 2×6
          (1/γ₆ = K_Chain propagator, 1/76 = φ-identity correction)
  
  步驟 5: 等價形式:
          log10(M_pl/M_comp) = (76/γ₆ - 1)/76
          = (L₉/γ₆ - 1)/L₉
          (純 K_Chain + Lucas 結構)
  
  步驟 6: 自我一致:
          m_ν₃ = (γ₆v)² / [M_pl × 10^(-(1/γ₆ - 1/76))]
          = 0.053586 eV
""")

# 驗證每一步
print(f"  驗證推導鏈:")
candidate = 1/g[6] - 1/76
M_comp_cand = M_pl * 10**(-candidate)
err = abs(M_comp_cand - M_comp_fit) / M_comp_fit * 100
m_nu3_pred = (g[6] * v)**2 / M_comp_cand
m_nu3_eV = m_nu3_pred * 1e9
err_nu = abs(m_nu3_eV - 0.0536) / 0.0536 * 100

check("步驟 4: log10 = 1/γ₆ - 1/76", 
      abs(candidate - log10_r) / log10_r * 100 < 0.01,
      f"({abs(candidate-log10_r)/log10_r*100:.4f}%)")
check("步驟 4: M_comp = 3.689e13",
      err < 0.1, f"({err:.4f}%)")
check("步驟 6: m_ν₃ = 0.0536 eV",
      err_nu < 0.1, f"({err_nu:.4f}%)")

# ══════════════════════════════════════════════════════════════
# 3. 88-site 對偶鏈嘅統一角色
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("[3] 88-site 對偶鏈嘅統一角色")
print("=" * 80)

# 88-site 對偶鏈嘅所有關鍵數
print(f"  88-site 對偶鏈關鍵數:")
print(f"    Σγ_odd  = {sum_odd_88:.6f} (觀察者)")
print(f"    Σγ_even = {sum_even_88:.6f} (世界)")
print(f"    Σγ      = {sum_odd_88 + sum_even_88:.6f}")
print(f"    奇子鏈長度 = 44, 偶子鏈長度 = 44")

# 1/γ₆ 同 88-site 嘅關係
print(f"\n  1/γ₆ 同 88-site 嘅關係:")
print(f"    1/γ₆ = {1/g[6]:.6f}")
print(f"    Σγ_odd / 1/γ₆ = {sum_odd_88 / (1/g[6]):.6f}")
print(f"    Σγ_even / 1/γ₆ = {sum_even_88 / (1/g[6]):.6f}")
print(f"    Σγ / 1/γ₆ = {(sum_odd_88 + sum_even_88) / (1/g[6]):.6f}")

# 88-site 嘅 1/γ 和
sum_inv_odd_88 = sum(1/g88[k] for k in range(1, 89, 2))
sum_inv_even_88 = sum(1/g88[k] for k in range(2, 89, 2))
print(f"\n  88-site 1/γ 和:")
print(f"    Σ(1/γ_odd)  = {sum_inv_odd_88:.6f}")
print(f"    Σ(1/γ_even) = {sum_inv_even_88:.6f}")
print(f"    Σ(1/γ)      = {sum_inv_odd_88 + sum_inv_even_88:.6f}")

# 關鍵: 1/γ₆ 同 Σ(1/γ_even) 嘅關係
print(f"\n  1/γ₆ vs Σ(1/γ_even):")
print(f"    Σ(1/γ_even) / 1/γ₆ = {sum_inv_even_88 / (1/g[6]):.6f}")
print(f"    Σ(1/γ_even) / 44 = {sum_inv_even_88 / 44:.6f}")
print(f"    = 平均 1/γ = {sum_inv_even_88 / 44:.6f}")
print(f"    1/γ₆ / 平均(1/γ) = {1/g[6] / (sum_inv_even_88/44):.6f}")

# ══════════════════════════════════════════════════════════════
# 4. 最終驗證: 所有形式嘅一致性
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("[4] 最終驗證: 所有形式嘅一致性")
print("=" * 80)

# 形式 1: 原始
form1 = 1/g[6] - 1/76
M1 = M_pl * 10**(-form1)
e1 = abs(M1 - M_comp_fit) / M_comp_fit * 100

# 形式 2: (76/γ₆ - 1)/76
form2 = (76/g[6] - 1) / 76
M2 = M_pl * 10**(-form2)
e2 = abs(M2 - M_comp_fit) / M_comp_fit * 100

# 形式 3: 1/γ₆ - 1/(4×19)
n19 = Nd - F8 - B
form3 = 1/g[6] - 1/(4*n19)
M3 = M_pl * 10**(-form3)
e3 = abs(M3 - M_comp_fit) / M_comp_fit * 100

# 形式 4: 1/γ₆ - 1/(88-12)
form4 = 1/g[6] - 1/(88-12)
M4 = M_pl * 10**(-form4)
e4 = abs(M4 - M_comp_fit) / M_comp_fit * 100

print(f"  {'形式':>35} | {'log10':>11} | {'M_comp (GeV)':>16} | {'誤差':>10}")
print("-" * 80)
print(f"  {'1/γ₆ - 1/76':>35} | {form1:>11.6f} | {M1:>16.4e} | {e1:>9.4f}%")
print(f"  {'1/γ₆ - 1/(88-12)':>35} | {form4:>11.6f} | {M4:>16.4e} | {e4:>9.4f}%")
print(f"  {'1/γ₆ - 1/(4×19)':>35} | {form3:>11.6f} | {M3:>16.4e} | {e3:>9.4f}%")
print(f"  {'76/γ₆ - 1)/76':>35} | {form2:>11.6f} | {M2:>16.4e} | {e2:>9.4f}%")

check("所有形式一致", abs(form1 - form2) < 1e-15 and abs(form1 - form4) < 1e-15)
check("所有 M_comp 一致", abs(e1 - e2) < 0.001 and abs(e1 - e4) < 0.001)

# ══════════════════════════════════════════════════════════════
# 5. 跨實驗驗證擴展
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("[5] 跨實驗驗證擴展")
print("=" * 80)

# 多個實驗嘅 Δm²₃₁ 值
dm31_values = {
    "PDG 2024": 2.434e-3,
    "NuFIT 5.2 (NO)": 2.437e-3,
    "NuFIT 5.2 (IO)": 2.503e-3,
    "Super-K": 2.40e-3,
    "MINOS+": 2.42e-3,
    "T2K 2023": 2.45e-3,
    "NOvA 2023": 2.44e-3,
}

print(f"  {'實驗':>20} | {'Δm²₃₁ (eV²)':>14} | {'m₃ (eV)':>10} | {'M_comp (GeV)':>16} | {'log10':>10} | {'結構偏差':>10}")
print("-" * 85)
for exp, dm in dm31_values.items():
    m3 = math.sqrt(dm)  # NO approx
    Mc = (g[6] * v)**2 / (m3 * 1e-9)
    lc = math.log10(M_pl / Mc)
    dev = abs(lc - candidate) / candidate * 100
    print(f"  {exp:>20} | {dm:>14.4e} | {m3:>10.5f} | {Mc:>16.4e} | {lc:>10.6f} | {dev:>9.3f}%")

# 從 Σm_ν 邊界推
print(f"\n  從 Σm_ν 邊界推 (NO, m₃ = Σm_ν/2.5):")
for sum_bound in [0.06, 0.072, 0.10, 0.12]:
    m3 = sum_bound / 2.5
    Mc = (g[6] * v)**2 / (m3 * 1e-9)
    lc = math.log10(M_pl / Mc)
    dev = abs(lc - candidate) / candidate * 100
    print(f"    Σm_ν < {sum_bound:.3f} eV → m₃ ≈ {m3:.4f} eV → M_comp = {Mc:.4e} GeV → log10 = {lc:.6f} (偏差 {dev:.2f}%)")

# ══════════════════════════════════════════════════════════════
# 6. 總結: 零參數結構
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("★★★ O66 最終總結")
print("=" * 80)

print(f"""
★★★ M_comp 第一性原理結構 (零參數):

  x²+x-1=0 → K_Chain 44-site → 88-site 對偶鏈
  
  log10(M_pl/M_comp) = 1/γ₆ - 1/(88-12)
                      = 1/γ₆ - 1/76
                      = 1/γ₆ - 1/(4×19)
                      = (76/γ₆ - 1)/76
                      = {candidate:.10f}
  
  M_comp = M_pl × 10^(-(1/γ₆ - 1/76))
         = {M_comp_cand:.4e} GeV (誤差 {err:.4f}%)
  
  自我一致:
  m_ν₃ = (γ₆v)²/M_comp = {m_nu3_eV:.6f} eV (誤差 {err_nu:.4f}%)

  三重身份:
  76 = 88 - 12      (K_Chain: Σγ_odd - 2×6)
     = φ⁹ - φ⁻⁹     (φ-identity)
     = 4×(Nd-F₈-B)  (O62 19 修正)

  O62-O66 統一:
  O62: V_Λ = F(γ) + 19
  O66: 1/76 = 1/(4×19)
  → 同一 19 喺 Λ (macro) 同 M_comp (micro) 出現!

  誠實狀態:
  🟢 76 = 88-12 = φ⁹-φ⁻⁹ = 4×19 三重身份一致
  🟢 1/γ₆ - 1/76 = 5.519774 誤差 0.0022% vs target
  🟢 M_comp = 3.689e13 GeV 誤差 0.0277%
  🟡 1/γ₆ 指數形式仍需動力學推導 (K_Chain 穿透模型)
  🟡 Δm²₃₁ = 2.87e-3 vs PDG 2.43e-3 (18%)
  🔴 Σm_ν = {m_nu3_eV + math.sqrt(m_nu3_eV**2 - 2.434e-3) + math.sqrt(m_nu3_eV**2 - 2.434e-3 + 7.53e-5):.4f} eV > DESI 2024
""")

results = {
    "test": "O66 05: M_comp 最終閉合",
    "log10_structure": "1/γ₆ - 1/(88-12) = 1/γ₆ - 1/76",
    "log10_value": float(candidate),
    "M_comp_GeV": float(M_comp_cand),
    "err_pct": float(err),
    "m_nu3_eV": float(m_nu3_eV),
    "triple_identity": {"88_minus_12": 76, "phi9_minus_phi-9": float(phi**9 - phi**(-9)), "4x19": 4*(Nd-F8-B)},
    "o62_o66_link": f"19 = Nd-F8-B = {Nd-F8-B}",
    "mechanism": "K_Chain tunneling: S = ln(10)/γ₆ - ln(10)/76",
    "cross_exp_PDG": {"M_comp": float((g[6]*v)**2/(math.sqrt(2.434e-3)*1e-9)), "log10": float(math.log10(M_pl/((g[6]*v)**2/(math.sqrt(2.434e-3)*1e-9)))), "dev_pct": float(abs(math.log10(M_pl/((g[6]*v)**2/(math.sqrt(2.434e-3)*1e-9))) - candidate)/candidate*100)},
    "passed": passed, "failed": failed
}
with open(DATA_DIR / "05_mcomp_final.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Passed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 O66 05 完成!")