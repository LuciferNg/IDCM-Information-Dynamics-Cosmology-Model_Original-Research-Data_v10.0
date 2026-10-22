#!/usr/bin/env python3
"""
O66 02: M_comp 機制深層分析 — 1/γ₆ - 1/76 嘅結構意義
======================================================
最佳候選: log10(M_pl/M_comp) = 1/γ₆ - 1/76 (誤差 0.0277%)
76 = φ⁹ - φ⁻⁹ (純 φ-identity)

探索:
  1. 1/γ₆ 嘅幾何意義 (K_Chain 諧波周期)
  2. 1/76 嘅 φ-identity 角色
  3. 組合: 1/γ₆ - 1/76 嘅統一結構
  4. 自我一致條件: m_ν₃ = (γ₆v)²/M_comp + M_comp = M_pl×10^(-(1/γ₆-1/76))
  5. 同 O62/O65 嘅連結
"""
import sys, os, math
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
O66_DIR = SCRIPT_DIR.parent
DATA_DIR = O66_DIR / "data"
DOCS_DIR = O66_DIR / "docs"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

phi = (1 + math.sqrt(5)) / 2
B = 4
Nd = 44
M = 33

M_pl = 1.2209e19
v = 246.0
m_nu3 = 0.0536e-9

g = {n: 4 * math.sin(n * math.pi / 88)**2 for n in range(1, 45)}

# φ-恆等式 (odd n)
phi_odd = {1: 1, 3: 4, 5: 11, 7: 29, 9: 76, 11: 199}

# Lucas
L = {0: 2, 1: 1, 2: 3, 3: 4, 4: 7, 5: 11, 6: 18, 7: 29, 8: 47, 9: 76, 10: 123}

print("=" * 80)
print("O66 02: M_comp 機制深層分析")
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

# 目標值
M_comp_fit = 3.69e13
log10_r = math.log10(M_pl / M_comp_fit)

# 最佳候選
candidate = 1/g[6] - 1/76
M_comp_cand = M_pl * 10**(-candidate)

print(f"\n  最佳候選: 1/γ₆ - 1/76 = {candidate:.10f}")
print(f"  M_comp = {M_comp_cand:.4e} GeV")
print(f"  M_comp(fit) = {M_comp_fit:.4e} GeV")
print(f"  誤差 = {abs(M_comp_cand - M_comp_fit)/M_comp_fit*100:.4f}%")

# ============================================================
# 1. 1/γ₆ 嘅幾何意義
# ============================================================
print("\n" + "=" * 80)
print("[1] 1/γ₆ 嘅 K_Chain 幾何意義")
print("=" * 80)

# γ₆ = 4sin²(6π/88) = 4sin²(3π/44)
# In the small-angle approx: sin(3π/44) ≈ 3π/44
# γ₆ ≈ 4(3π/44)² = 36π²/484 = 9π²/121

print(f"  γ₆ = 4sin²(3π/44) = {g[6]:.10f}")
print(f"  小角近似: 4(3π/44)² = {4*(3*math.pi/44)**2:.10f}")
print(f"  誤差: {abs(g[6] - 4*(3*math.pi/44)**2)/(4*(3*math.pi/44)**2)*100:.2f}%")
print(f"  精確: 4sin²(3π/44) = 4(1-cos(3π/22))/2 = 2(1-cos(3π/22))")

# 1/γ₆ 嘅周期意義
print(f"\n  1/γ₆ = {1/g[6]:.6f}")
print(f"  88/γ₆ = {88/g[6]:.6f} (88-site 對偶鏈周期)")
print(f"  44/γ₆ = {44/g[6]:.6f} (44-site 世界鏈周期)")
print(f"  1/γ₆ × 44 = {1/g[6]*44:.6f} (44 個諧波周期)")
print(f"  1/γ₆ × 88 = {1/g[6]*88:.6f} (88 個對偶周期)")

# 1/γ₆ 同 88-site 對偶鏈嘅關係
print(f"\n  γ₆ 喺 88-site 對偶鏈嘅位置:")
print(f"  n=6 (44-site) ↔ 對偶鏈 n=12 (88-site)")
print(f"  γ₁₂(88-site) = 4sin²(12π/176) = 4sin²(3π/44) = γ₆ ✅")
print(f"  88-site 對偶鏈: 奇子鏈 sum = 88, 偶子鏈 sum = 90")
print(f"  1/γ₆ × 88 = {88/g[6]:.6f} = 88-site 尺度")
print(f"  1/γ₆ / 88 = {1/g[6]/88:.6f} = 每 site 貢獻")

# ============================================================
# 2. 1/76 嘅 φ-identity 角色
# ============================================================
print("\n" + "=" * 80)
print("[2] 1/76 嘅 φ-identity 角色")
print("=" * 80)

print(f"  76 = φ⁹ - φ⁻⁹ = {phi**9 - phi**(-9):.6f}")
print(f"  76 = L₉ (Lucas 9)")
print(f"  76 = 4×19 = 4×(N_d - F₈ - B)")
print(f"  76 = 2×38 = 2×(L₇+L₆)")
print(f"  76 = 3² + 4² + 5² + 6² - 1² = 9+16+25+36-1?")

# 76 係 λ_sync 嘅一部份
print(f"\n  76 同 λ_sync 關係:")
print(f"  λ_sync = 294.88 (memory)")
print(f"  294.88 - 76 = {294.88 - 76:.2f}")
print(f"  294.88 / 76 = {294.88/76:.4f}")

# 1/76 嘅數值意義
print(f"\n  1/76 = {1/76:.10f}")
print(f"  1/76 × 44 = {1/76*44:.6f}")
print(f"  1/76 × 88 = {1/76*88:.6f}")
print(f"  1/76 × 946 = {1/76*946:.6f}")

# 對照: 其他 φ-identity 嘅 1/n
print(f"\n  φ-identity 倒數系列:")
for n in [1, 3, 5, 7, 9, 11]:
    val = phi_odd[n]
    inv = 1/val
    print(f"  1/(φ^{n}-φ⁻^{n}) = 1/{val} = {inv:.10f}")

# 檢查 1/γ₆ - 1/n 對所有 φ-identity n
print(f"\n  1/γ₆ - 1/n 對 φ-identity:")
for n in [1, 3, 5, 7, 9, 11]:
    val = phi_odd[n]
    cand = 1/g[6] - 1/val
    err = abs(cand - log10_r) / log10_r * 100
    print(f"    n={n} ({val}): 1/γ₆-1/{val} = {cand:.10f}, 誤差 {err:.4f}%")

# ============================================================
# 3. 自我一致條件: m_ν₃ 循環
# ============================================================
print("\n" + "=" * 80)
print("[3] ★ 自我一致條件: m_ν₃ ↔ M_comp 循環")
print("=" * 80)

# 用結構公式 M_comp = M_pl × 10^(-(1/γ₆ - 1/76))
# 代入 m_ν₃ = (γ₆v)²/M_comp
print(f"\n  M_comp (結構) = M_pl × 10^(-(1/γ₆ - 1/76))")
print(f"               = {M_comp_cand:.4e} GeV")
print(f"  m_ν₃ (結構) = (γ₆v)²/M_comp")
print(f"              = ({g[6]:.6f} × {v})² / {M_comp_cand:.4e}")
m_nu3_pred = (g[6] * v)**2 / M_comp_cand
m_nu3_eV = m_nu3_pred * 1e9
print(f"              = {m_nu3_pred:.6e} GeV = {m_nu3_eV:.6f} eV")
print(f"  m_ν₃ (fit)  = {m_nu3*1e9:.6f} eV")
err_nu = abs(m_nu3_eV - m_nu3*1e9) / (m_nu3*1e9) * 100
print(f"  誤差 = {err_nu:.4f}%")
check("m_ν₃ 結構預言 < 1%", err_nu < 1, f"({err_nu:.4f}%)")

# Δm²₃₁ 預言
print(f"\n  Δm²₃₁ 預言 (假定 m₁ << m₃):")
dm31_pred = m_nu3_eV**2
print(f"  Δm²₃₁ = m₃² ≈ {dm31_pred:.4e} eV²")
print(f"  PDG: 2.434e-3 eV²")
err_dm31 = abs(dm31_pred - 2.434e-3) / 2.434e-3 * 100
print(f"  誤差 = {err_dm31:.2f}%")

# Σm_ν (保守 NO)
print(f"\n  Σm_ν 預言 (NO, 保守):")
dm21_exp = 7.53e-5
m1 = math.sqrt(max(m_nu3_eV**2 - 2.434e-3, 0))
m2 = math.sqrt(m1**2 + dm21_exp)
sum_nu = m1 + m2 + m_nu3_eV
print(f"  m₁ = {m1:.4f} eV, m₂ = {m2:.4f} eV, m₃ = {m_nu3_eV:.4f} eV")
print(f"  Σm_ν = {sum_nu:.4f} eV")
print(f"  DESI 2024: < 0.072 eV")
print(f"  Planck 2018: < 0.12 eV")

# ============================================================
# 4. 統一結構: 1/γ₆ - 1/76 = ?
# ============================================================
print("\n" + "=" * 80)
print("[4] 統一結構: 1/γ₆ - 1/76 = ?")
print("=" * 80)

# 嘗試將 1/γ₆ - 1/76 表達為單一結構
combined = 1/g[6] - 1/76
print(f"  1/γ₆ - 1/76 = {combined:.10f}")

# 檢查呢個數嘅其他身份
print(f"\n  = ?")
print(f"  = 5.5 + 0.019774 (L₅/2 + 0.019774)")
print(f"  = 44/8 + 0.019774 (Nd/8 + 0.019774)")
print(f"  = 1/γ₆ × (1 - γ₆/76) = {1/g[6]*(1 - g[6]/76):.10f}")
print(f"  = 1/γ₆ × (1 - γ₆/76) = {1/g[6]*(1 - g[6]/76):.10f}")

# 檢查 (1/γ₆ - 1/76) × 76
print(f"\n  (1/γ₆ - 1/76) × 76 = {combined * 76:.10f}")
print(f"  = 76/γ₆ - 1 = {76/g[6] - 1:.10f}")
print(f"  76/γ₆ = {76/g[6]:.6f}")

# 檢查 (1/γ₆ - 1/76) × γ₆
print(f"\n  (1/γ₆ - 1/76) × γ₆ = {combined * g[6]:.10f}")
print(f"  = 1 - γ₆/76 = {1 - g[6]/76:.10f}")

# 檢查 (1/γ₆ - 1/76) × 44
print(f"\n  (1/γ₆ - 1/76) × 44 = {combined * 44:.10f}")
print(f"  = 44/γ₆ - 44/76 = {44/g[6] - 44/76:.10f}")

# ============================================================
# 5. 同 O62 F(γ) 嘅連結
# ============================================================
print("\n" + "=" * 80)
print("[5] 同 O62 F(γ) 嘅連結")
print("=" * 80)

F_gamma = 264.0821292326
V_lambda = 283.0821292326

# F(γ) = 264.082 = 6Nd + 0.0821
# 1/γ₆ - 1/76 = 5.51977
# 注意: 264 × 0.0821 = ... 唔係
# 但: 264 × (1/γ₆ - 1/76) = ?

print(f"  F(γ) = {F_gamma:.6f}")
print(f"  V_Λ = {V_lambda:.6f}")
print(f"  1/γ₆ - 1/76 = {combined:.6f}")

print(f"\n  F(γ) × (1/γ₆ - 1/76) = {F_gamma * combined:.6f}")
print(f"  F(γ) / (1/γ₆ - 1/76) = {F_gamma / combined:.6f}")
print(f"  V_Λ × (1/γ₆ - 1/76) = {V_lambda * combined:.6f}")
print(f"  V_Λ / (1/γ₆ - 1/76) = {V_lambda / combined:.6f}")

# 檢查: 264 = 6Nd, 同 1/γ₆ - 1/76 嘅關係
print(f"\n  264 / (1/γ₆ - 1/76) = {264 / combined:.6f}")
print(f"  264 × (1/γ₆ - 1/76) = {264 * combined:.6f}")

# 檢查 γ₆ 嘅統一角色
print(f"\n  γ₆ 統一角色:")
print(f"  Λ: 44γ₆ = {44*g[6]:.6f} (O57)")
print(f"  Λ: F(γ) = {F_gamma:.6f} (O62)")
print(f"  M_comp: 1/γ₆ - 1/76 = {combined:.6f}")
print(f"  m_ν₃: (γ₆v)²/M_comp = {m_nu3_eV:.6f} eV")
print(f"  PMNS: γ₆/8 = {g[6]/8:.6f}")
print(f"  CKM: γ₆/16 = {g[6]/16:.6f}")

# ============================================================
# 6. 物理機制: 10^(-(1/γ₆ - 1/76)) 嘅 K_Chain 詮釋
# ============================================================
print("\n" + "=" * 80)
print("[6] 物理機制: 10^(-(1/γ₆ - 1/76)) 嘅 K_Chain 詮釋")
print("=" * 80)

# 將指數寫成: -ln(10)/γ₆ + ln(10)/76
# = -(ln(10)/γ₆) × (1 - γ₆/76)
print(f"\n  M_comp = M_pl × exp(-ln(10)/γ₆ + ln(10)/76)")
print(f"         = M_pl × exp(-ln(10)/γ₆) × exp(ln(10)/76)")
print(f"         = M_pl × exp(-ln(10)/γ₆) × 10^(1/76)")

# 檢查 10^(1/76) 嘅結構意義
print(f"\n  10^(1/76) = {10**(1/76):.6f}")
print(f"  = 1 + 0.0308")

# 檢查 ln(10)/γ₆ 嘅結構意義
print(f"\n  ln(10)/γ₆ = {math.log(10)/g[6]:.6f}")
print(f"  ln(10)/γ₆ = 12.740")
print(f"  = 44/φ²? {44/phi**2:.6f}")
print(f"  = 33/φ? {33/phi:.6f}")
print(f"  = φ⁵ + 1.62? {phi**5 + 1.62:.6f}")

# 但更重要: 1/γ₆ 喺底數 10 嘅指數
# 呢個可能係 K_Chain 嘅「log 積分」效應
print(f"\n  ★ 關鍵 insight:")
print(f"  log10(M_pl/M_comp) = 1/γ₆ - 1/76")
print(f"  = 5.51977")
print(f"  呢個數係 K_Chain 諧波 γ₆ 嘅逆 + φ-identity 修正")
print(f"  → K_Chain 諧波決定 Seesaw 抑制尺度")
print(f"  → φ-identity 提供高階修正")

# ============================================================
# 7. M_comp 同 M_pl 嘅精確比例
# ============================================================
print("\n" + "=" * 80)
print("[7] M_comp/M_pl 精確比例")
print("=" * 80)

ratio = M_comp_fit / M_pl
print(f"  M_comp/M_pl = {M_comp_fit/M_pl:.4e}")
print(f"  = 10^(-5.519654) = {10**(-5.519654):.4e}")
print(f"  = 10^(-(1/γ₆ - 1/76)) = {10**(-(1/g[6] - 1/76)):.4e}")

# 冇單位形式
print(f"\n  冇單位形式:")
print(f"  log10(M_pl/M_comp) = {log10_r:.6f}")
print(f"  ≈ 1/γ₆ - 1/76 = {1/g[6] - 1/76:.6f}")
print(f"  Δ = {(1/g[6] - 1/76) - log10_r:.6f}")
print(f"  (1/γ₆ - 1/76)/log10_r = {(1/g[6] - 1/76)/log10_r:.6f}")

# ============================================================
# 8. 總結
# ============================================================
print("\n" + "=" * 80)
print("O66 02 總結")
print("=" * 80)

print(f"""
★★★ M_comp 第一性原理結構:

  log10(M_pl/M_comp) = 1/γ₆ - 1/76 = {1/g[6] - 1/76:.10f}
  M_comp = M_pl × 10^(-(1/γ₆ - 1/76)) = {M_comp_cand:.4e} GeV
  
  誤差: {abs(M_comp_cand - M_comp_fit)/M_comp_fit*100:.4f}% (vs fit 3.69e13)
  
  結構:
  ──────
  1/γ₆:  K_Chain n=6 harmonic (discrete wave inverse)
  1/76:  φ-identity (76 = φ⁹ - φ⁻⁹)
  
  76 = φ⁹ - φ⁻⁹ = L₉ = 4×(N_d - F₈ - B) = 4×19

  自我一致:
  ────────
  m_ν₃ = (γ₆v)²/M_comp = {m_nu3_eV:.6f} eV (vs {m_nu3*1e9:.6f} eV)
  Δm²₃₁ ≈ {dm31_pred:.4e} eV² (vs 2.434e-3, {err_dm31:.1f}%)
  Σm_ν = {sum_nu:.4f} eV

  誠實標記:
  ────────
  🟢 1/γ₆ - 1/76 = 5.519774 (誤差 0.0277%) — 極強數值匹配
  🟡 結構匹配係 search 出嚟 (雖然有 φ-identity 支持)
  🟡 1/γ₆ 喺指數冇第一性原理動機 (RGE/warp/instanton 未定)
  🟡 m_ν₃ 預言需要獨立驗證 (Δm²₂₁, m_ββ)
  🔴 Σm_ν = {sum_nu:.4f} eV 可能違反 DESI 2024 < 0.072 eV
""")

results = {
    "test": "O66 02: M_comp 機制深層分析",
    "best_candidate": "1/γ₆ - 1/76",
    "log10_value": float(1/g[6] - 1/76),
    "M_comp_GeV": float(M_comp_cand),
    "err_pct": float(abs(M_comp_cand - M_comp_fit)/M_comp_fit*100),
    "m_nu3_pred_eV": float(m_nu3_eV),
    "dm31_pred_eV2": float(dm31_pred),
    "sum_nu_eV": float(sum_nu),
    "phi_identity_76": float(phi**9 - phi**(-9)),
    "passed": passed, "failed": failed
}
with open(DATA_DIR / "02_mcomp_mechanism.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Passed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 O66 02 完成!")