#!/usr/bin/env python3
"""
O66 04: M_comp 深層推導 — O62-O66 連結 + 機制探索
====================================================
已發現:
  log10(M_pl/M_comp) = 1/γ₆ - 1/76
  76 = 4×19 = 4×(N_d - F₈ - B)  ← O62 Λ 嘅 19 完全相同!

O62: V_Λ = F(γ) + 19 = 283.0821
O66: 1/76 = 1/(4×19) = 1/(4×(N_d - F₈ - B))

探索:
  1. O62-O66 嘅 19 統一 — 物理意義
  2. 1/γ₆ 指數形式嘅 K_Chain 機制
  3. log10(M_pl/M_comp) = 1/γ₆ - 1/(4×19) 嘅完整結構
  4. 跨實驗驗證 (用唔同嘅 M_comp 值)
  5. 如果機制係 K_Chain 穿透/隧道效應
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
F8 = 21  # Fibonacci 8

# 物理常數
M_pl = 1.2209e19
v = 246.0
m_nu3_fit = 0.0536e-9

# K_Chain 諧波
g = {n: 4 * math.sin(n * math.pi / 88)**2 for n in range(1, 45)}

# φ-恆等式
phi_odd = {1: 1, 3: 4, 5: 11, 7: 29, 9: 76, 11: 199}

print("=" * 80)
print("O66 04: M_comp 深層推導 — O62-O66 連結 + 機制探索")
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
# 1. O62-O66 嘅 19 統一
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("[1] ★★★ O62-O66 嘅 19 統一")
print("=" * 80)

# O62: 19 = N_d - F₈ - B
n19 = Nd - F8 - B
print(f"  19 = N_d - F₈ - B = {Nd} - {F8} - {B} = {n19}")
print(f"  76 = 4 × 19 = 4 × {n19}")
print(f"  1/76 = 1/(4×19) = 1/(4×{n19}) = {1/(4*n19):.10f}")

# 驗證身份
check("19 = Nd - F8 - B", n19 == 19)
check("76 = 4×19", 4*n19 == 76)
check("76 = φ⁹-φ⁻⁹", abs(phi**9 - phi**(-9) - 76) < 1e-10)

# 兩個公式嘅比較
print(f"\n  O62 Λ:  V_Λ = F(γ) + {n19} = 283.0821")
print(f"  O66 M_comp:  1/76 = 1/(4×{n19})")
print(f"  → 兩個公式都用到 19 = N_d - F₈ - B")
print(f"  → O62 用 19 做加法修正 (線性)")
print(f"  → O66 用 1/(4×19) 做指數修正 (倒數)")

# 統一形式
print(f"\n  統一結構:")
print(f"  O62:  V_Λ = F(γ) + 19")
print(f"  O66:  log10(M_pl/M_comp) = 1/γ₆ - 1/(4×19)")
print(f"  → 同一數字 19 喺兩個尺度出現!")
print(f"  → Λ (macro) 同 M_comp (micro) 共享幾何修正")

# 檢查 19 嘅其他身份
print(f"\n  19 嘅其他身份:")
print(f"  19 = L₅ + F₆ = 11 + 8 = {11+8}")
print(f"  19 = L₆ + 1 = 18 + 1 = {18+1}")
print(f"  19 = F₇ + L₃ = 13 + 4 + 2? 唔係")
print(f"  19 = 44 - 25 = N_d - (F₈ + B) = {Nd - F8 - B}")
print(f"  19 = 25 - 6 = (F₈+B) - 2×N_gen = {F8+B} - {2*3}")
print(f"  19 = 98 - 73 + 6? 98 - 73 = 25? 唔係")
print(f"  19 = 36 - 17 = h¹¹ - 17")

# ══════════════════════════════════════════════════════════════
# 2. 1/γ₆ 指數形式嘅 K_Chain 機制
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("[2] 1/γ₆ 指數形式嘅 K_Chain 機制")
print("=" * 80)

# 2a. K_Chain 譜積分
print("\n  2a. K_Chain 譜積分:")
sum_inv_g = sum(1/g[n] for n in range(1, 45))
print(f"  Σ 1/γ_n = {sum_inv_g:.6f}")
sum_g = sum(g[n] for n in range(1, 45))
print(f"  Σ γ_n = {sum_g:.6f}")
print(f"  (Σ 1/γ_n) / (Σ γ_n) = {sum_inv_g/sum_g:.6f}")
print(f"  (Σ 1/γ_n) / Nd = {sum_inv_g/Nd:.6f}")

# 2b. 1/γ₆ 同其他 1/γ_n 嘅關係
print("\n  2b. 1/γ₆ 同其他 1/γ_n:")
for n in [1, 2, 3, 4, 5, 6, 7, 8, 11, 22, 33, 44]:
    ratio = 1/g[n] / 1/g[6]
    print(f"  1/γ_{n} / 1/γ₆ = {1/g[n]/g[6]:.6f}")

# 2c. 1/γ₆ 嘅對偶鏈位置
print("\n  2c. 1/γ₆ 嘅對偶鏈位置:")
# 88-site 對偶鏈
g88 = {k: 4*math.sin(k*math.pi/176)**2 for k in range(1, 89)}
# n=6 (44-site) = k=12 (88-site)
print(f"  44-site n=6 → 88-site k=12")
print(f"  γ₁₂(88) = {g88[12]:.10f}")
print(f"  1/γ₁₂(88) = {1/g88[12]:.10f}")
print(f"  88-site 奇子鏈 (k=1,3,5,...,87):")
sum_odd_88 = sum(g88[k] for k in range(1, 89, 2))
sum_even_88 = sum(g88[k] for k in range(2, 89, 2))
print(f"    Σγ_odd = {sum_odd_88:.6f}")
print(f"    Σγ_even = {sum_even_88:.6f}")
print(f"    Σγ_total = {sum_odd_88 + sum_even_88:.6f}")

# 2d. 88-site 嘅 1/γ 和
print("\n  2d. 88-site 嘅 1/γ 和:")
sum_inv_88 = sum(1/g88[k] for k in range(1, 89))
print(f"  Σ(1/γ_k) (k=1..88) = {sum_inv_88:.6f}")
sum_inv_odd_88 = sum(1/g88[k] for k in range(1, 89, 2))
sum_inv_even_88 = sum(1/g88[k] for k in range(2, 89, 2))
print(f"  Σ(1/γ_odd) = {sum_inv_odd_88:.6f}")
print(f"  Σ(1/γ_even) = {sum_inv_even_88:.6f}")

# 2e. 關鍵: 1/γ₆ 可能係某種「K_Chain 穿透積分」
print(f"\n  2e. 1/γ₆ 作為有效穿透積分:")
print(f"  1/γ₆ = {1/g[6]:.6f}")
print(f"  = 5.5329")
print(f"  如果 1/γ₆ = ∫ dx / √(E - V(x)) 型穿透積分")
print(f"  即 K_Chain 上嘅有效 barrier 同 γ₆ 成反比")

# ══════════════════════════════════════════════════════════════
# 3. 完整公式: log10(M_pl/M_comp) = 1/γ₆ - 1/(4×19)
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("[3] ★★★ 完整公式: log10(M_pl/M_comp) = 1/γ₆ - 1/(4×19)")
print("=" * 80)

# 用 4×19 取代 76
candidate = 1/g[6] - 1/(4*n19)
M_comp_cand = M_pl * 10**(-candidate)
err = abs(M_comp_cand - M_comp_fit) / M_comp_fit * 100

print(f"  1/γ₆ - 1/(4×19) = {1/g[6]:.10f} - 1/{4*n19}")
print(f"                    = {1/g[6]:.10f} - {1/(4*n19):.10f}")
print(f"                    = {candidate:.10f}")
print(f"  log10(M_pl/M_comp) = {log10_r:.10f}")
print(f"  誤差 = {abs(candidate - log10_r)/log10_r*100:.4f}%")
print(f"  M_comp = {M_comp_cand:.4e} GeV (fit: {M_comp_fit:.4e})")
print(f"  M_comp 誤差 = {err:.4f}%")
check("完整公式: 1/γ₆ - 1/(4×19)", err < 0.1, f"({err:.4f}%)")

# 3b. 自我一致
m_nu3_pred = (g[6] * v)**2 / M_comp_cand
m_nu3_eV = m_nu3_pred * 1e9
print(f"\n  m_ν₃ = {m_nu3_eV:.6f} eV (fit: {m_nu3_fit*1e9:.6f})")
err_nu = abs(m_nu3_eV - m_nu3_fit*1e9) / (m_nu3_fit*1e9) * 100
check("m_ν₃ 一致", err_nu < 0.1, f"({err_nu:.4f}%)")

# 3c. 19 嘅 K_Chain 幾何意義
print(f"\n  3c. 19 嘅 K_Chain 幾何意義:")
print(f"  19 = N_d - F₈ - B")
print(f"     = {Nd} - {F8} - {B} = {n19}")
print(f"  F₈ = 21 (Fibonacci 8) = 固定 beats 數")
print(f"  B = 4 (K_Tree branching)")
print(f"  N_d = 44 (世界鏈長度)")
print(f"  → 19 = 世界鏈長度減去固定 beats 同分支")
print(f"  → 即係「自由諧波」數目")

# ══════════════════════════════════════════════════════════════
# 4. 跨實驗驗證
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("[4] 跨實驗驗證")
print("=" * 80)

# 唔同實驗嘅 m_ν₃ 值會導致唔同 M_comp
# 但 m_ν₃ 唔係直接觀測量 — 要從 Δm² 推
# 從 Δm²₃₁ 推 m_ν₃ (假設 NO, m₁ << m₃)
dm31_PDG = 2.434e-3  # eV²
m3_from_dm31 = math.sqrt(dm31_PDG)
M_comp_from_dm31 = (g[6] * v)**2 / (m3_from_dm31 * 1e-9)

print(f"  從 PDG Δm²₃₁ = {dm31_PDG} eV² 推:")
print(f"    m₃ ≈ {m3_from_dm31:.5f} eV")
print(f"    M_comp = (γ₆v)²/m₃ = {M_comp_from_dm31:.4e} GeV")
print(f"    log10(M_pl/M_comp) = {math.log10(M_pl/M_comp_from_dm31):.6f}")
print(f"    結構預言: 1/γ₆ - 1/76 = {candidate:.6f}")

# 比較
cand_from_dm31 = math.log10(M_pl / M_comp_from_dm31)
err_dm31 = abs(cand_from_dm31 - candidate) / candidate * 100
print(f"    結構 vs Δm² 推: Δ = {cand_from_dm31 - candidate:.6f} ({err_dm31:.2f}%)")

# 從 DESI Σm_ν 邊界推
print(f"\n  從 DESI 2024 Σm_ν < 0.072 eV (NO):")
# NO: m₁ < m₂ < m₃, Σm = m₁ + m₂ + m₃
# 如果 m₃ >> m₂ > m₁, Σm ≈ m₃ (close to bound)
# 更保守: m₃ ≈ Σm_ν/2.5 (NO approx)
for sum_bound in [0.072, 0.12]:
    m3_from_sum = sum_bound / 2.5  # rough NO approx
    M_comp_from_sum = (g[6] * v)**2 / (m3_from_sum * 1e-9)
    log10_from_sum = math.log10(M_pl / M_comp_from_sum)
    print(f"    Σm_ν < {sum_bound} eV → m₃ ≲ {m3_from_sum:.4f} eV")
    print(f"    → M_comp > {M_comp_from_sum:.4e} GeV")
    print(f"    → log10(M_pl/M_comp) < {log10_from_sum:.6f}")

# 直接比較唔同 M_comp 值
print(f"\n  M_comp 值比較:")
print(f"  {'來源':>20} | {'M_comp (GeV)':>16} | {'log10':>10} | {'結構誤差':>10}")
print("-" * 62)
print(f"  {'結構公式 (1/γ₆-1/76)':>20} | {M_comp_cand:>16.4e} | {candidate:>10.6f} | {'0.0277%':>10}")
print(f"  {'原始 fit (m_ν=0.0536)':>20} | {M_comp_fit:>16.4e} | {log10_r:>10.6f} | {'0.00%':>10}")
print(f"  {'從 PDG Δm²₃₁':>20} | {M_comp_from_dm31:>16.4e} | {cand_from_dm31:>10.6f} | {err_dm31:>9.2f}%")

# ══════════════════════════════════════════════════════════════
# 5. 機制假設: K_Chain 穿透 (K_Chain Tunneling)
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("[5] 機制假設: K_Chain 穿透 (K_Chain Tunneling)")
print("=" * 80)

# 假設: M_comp 係 K_Chain 上嘅「穿透振幅」
# 喺 discrete lattice 上, 穿透振幅 = exp(-S)
# S = ∫√(2m(E-V)) dx ≈ N_sites × √(γ_barrier - γ₆)
# 如果 barrier 係平均諧波 <γ>, 穿透距離 = 部分 chain

print(f"""
  K_Chain 穿透模型:
  ─────────────────
  M_comp = M_pl × exp(-S_tunnel)
  S_tunnel = ln(10)/γ₆ - ln(10)/76 ≈ 12.74 - 0.030
  
  物理圖像:
  K_Chain 上嘅 heavy mode (n=6) 需要穿透一個有效 barrier
  穿透 action S = ln(10)/γ₆ ≈ 12.74
  修正 ln(10)/76 ≈ 0.030 係 threshold correction
  
  關鍵: 1/γ₆ 係 K_Chain 諧波嘅逆 = 有效穿透距離
  (類似於: 能量越高, 波長越短, 穿透越易)
""")

# 檢查穿透模型嘅預言
print(f"  穿透模型檢驗:")
print(f"  S_tunnel = ln(10)/γ₆ - ln(10)/76 = {math.log(10)/g[6] - math.log(10)/76:.6f}")
print(f"  S_tunnel = ln(M_pl/M_comp) = {math.log(M_pl/M_comp_cand):.6f}")
print(f"  S_tunnel / γ₆ = {(math.log(10)/g[6] - math.log(10)/76)/g[6]:.6f}")
print(f"  S_tunnel × γ₆ = {(math.log(10)/g[6] - math.log(10)/76)*g[6]:.6f}")
print(f"  = ln(10) - ln(10)×γ₆/76 = {math.log(10) - math.log(10)*g[6]/76:.6f}")

# 自然穿透 action
print(f"\n  自然穿透 action:")
print(f"  S = ln(M_pl/M_comp) = {math.log(M_pl/M_comp_cand):.6f}")
print(f"  S 候選:")
for name, val in [
    ("2π/γ₆", 2*math.pi/g[6]),
    ("π/γ₆", math.pi/g[6]),
    ("44/γ₆", Nd/g[6]),
    ("88/γ₆", 88/g[6]),
    ("M/γ₆", M/g[6]),
    ("44", float(Nd)),
    ("44φ", Nd*phi),
    ("44φ²", Nd*phi**2),
    ("44×φ⁻¹", Nd*phi**(-1)),
    ("44×ε", Nd*phi**(-1)/4),
    ("F(γ)/γ₆", 264.0821/g[6]),
    ("V_Λ/γ₆", 283.0821/g[6]),
    ("F(γ)/44", 264.0821/Nd),
    ("V_Λ/44", 283.0821/Nd),
]:
    if val < 1000:
        e = abs(val - math.log(M_pl/M_comp_cand)) / math.log(M_pl/M_comp_cand) * 100
        if e < 50:
            print(f"    {name} = {val:.6f} (誤差 {e:.2f}%)")

# ══════════════════════════════════════════════════════════════
# 6. 統一結構: 將 1/γ₆ - 1/76 寫成單一 K_Chain 表達式
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("[6] 統一結構: 1/γ₆ - 1/76 嘅單一 K_Chain 表達式")
print("=" * 80)

# 6a. 1/γ₆ × (1 - γ₆/76) 形式
print("\n  6a. 因式分解:")
print(f"  1/γ₆ - 1/76 = 1/γ₆ × (1 - γ₆/76) = {1/g[6]*(1 - g[6]/76):.10f}")
print(f"  1 - γ₆/76 = {1 - g[6]/76:.10f}")
print(f"  = 1 - 0.180736/76 = 1 - 0.002378 = 0.997622")

# 6b. 76 = Σγ_odd - 12? 或者 76 = 88 - 12?
print(f"\n  6b. 76 同 88-site 對偶鏈:")
print(f"  88 - 12 = {88 - 12}")
print(f"  88 - 76 = {88 - 76}")
print(f"  44 - 19 = {44 - 19}")
print(f"  44 + 19 = {44 + 19}")
print(f"  90 - 14 = {90 - 14}")
print(f"  88 - 14 = {88 - 14}")

# 6c. γ₆ × 76 = ?
print(f"\n  6c. γ₆ × 76 = {g[6] * 76:.6f}")
print(f"  76/γ₆ = {76/g[6]:.6f}")
print(f"  76/γ₆ - 1 = {76/g[6] - 1:.6f} ← 乘 76 後嘅形式")

# 6d. 可能嘅統一形式
print(f"\n  6d. 可能嘅統一形式:")
print(f"  log10(M_pl/M_comp) = (76/γ₆ - 1) / 76")
print(f"                    = {76/g[6] - 1:.10f} / 76")
print(f"                    = {(76/g[6] - 1)/76:.10f}")
print(f"  76/γ₆ = {76/g[6]:.6f} = 420.50")
print(f"  76/γ₆ - 1 = {76/g[6] - 1:.6f} = 419.50")
print(f"  (76/γ₆ - 1) / 76 = {(76/g[6] - 1)/76:.10f}")

# 6e. 更簡潔: log10 = (76/γ₆ - 1)/76
print(f"\n  6e. 最簡形式:")
print(f"  log10(M_pl/M_comp) = (76/γ₆ - 1)/76")
print(f"  = (φ⁹-φ⁻⁹)/γ₆ - 1) / (φ⁹-φ⁻⁹)")
print(f"  呢個形式將 K_Chain 諧波同 φ-identity 合併:")
print(f"  - 分子: 76/γ₆ - 1 = K_Chain 尺度 ÷ φ-identity")
print(f"  - 分母: 76 = φ-identity 本身")

# 驗證最簡形式
candidate_simple = (76/g[6] - 1) / 76
M_comp_simple = M_pl * 10**(-candidate_simple)
err_simple = abs(M_comp_simple - M_comp_fit) / M_comp_fit * 100
print(f"\n  驗證: log10 = (76/γ₆ - 1)/76 = {candidate_simple:.10f}")
print(f"        M_comp = {M_comp_simple:.4e} GeV")
print(f"        誤差 = {err_simple:.4f}%")
check("最簡形式一致", err_simple < 0.1, f"({err_simple:.4f}%)")

# ══════════════════════════════════════════════════════════════
# 7. 總結
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("O66 04 總結")
print("=" * 80)

print(f"""
★★★ O66 O62 統一連結 + 機制探索:

1. O62-O66 嘅 19 統一:
   O62: V_Λ = F(γ) + 19
   O66: 1/76 = 1/(4×19) where 19 = N_d - F₈ - B
   → 同一幾何修正 19 喺兩個尺度出現!
   → Λ (macro) 同 M_comp (micro) 共享 19

2. 完整公式:
   log10(M_pl/M_comp) = 1/γ₆ - 1/(4×19)
                       = {1/g[6] - 1/(4*n19):.10f}
   M_comp = {M_comp_cand:.4e} GeV (誤差 {err:.4f}%)

3. 最簡形式:
   log10(M_pl/M_comp) = (76/γ₆ - 1)/76
   = (L₉/γ₆ - 1)/L₉
   → 純 K_Chain + Lucas 結構

4. 機制方向:
   - K_Chain 穿透模型: S = ln(10)/γ₆ - ln(10)/76
   - 1/γ₆ 作為有效穿透距離
   - 1/76 作為 threshold correction

5. 開放問題:
   🟡 1/γ₆ 指數形式仍需動力學推導
   🟡 Σm_ν = {m_nu3_eV + math.sqrt(m_nu3_eV**2 - 2.434e-3) + math.sqrt(m_nu3_eV**2 - 2.434e-3 + 7.53e-5):.4f} eV > DESI
   🔴 跨實驗驗證: 從 Δm²₃₁ 推 M_comp 有 {err_dm31:.1f}% 偏差
""")

results = {
    "test": "O66 04: M_comp 深層推導",
    "o62_o66_connection": f"19 = Nd - F8 - B = {n19}, 76 = 4×19",
    "formula_compact": "log10(M_pl/M_comp) = (76/γ₆ - 1)/76",
    "log10_value": float(candidate),
    "M_comp_GeV": float(M_comp_cand),
    "err_pct": float(err),
    "m_nu3_eV": float(m_nu3_eV),
    "dm31_from_structure": float(m_nu3_eV**2),
    "dm31_from_PDG": 2.434e-3,
    "dm31_deviation_pct": float(err_dm31),
    "mechanism_hint": "K_Chain tunneling: S = ln(10)/γ₆ - ln(10)/76",
    "passed": passed, "failed": failed
}
with open(DATA_DIR / "04_mcomp_deep.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Passed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 O66 04 完成!")