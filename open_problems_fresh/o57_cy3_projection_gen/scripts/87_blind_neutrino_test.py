#!/usr/bin/env python3
"""
O57 十六期 87: ★★ 中微子盲測 (Blind Test) — Peer 指定協議
============================================================
Peer 批判: ν/l「統一公式」係代數恆等式 (Tautology):
  m_ν_i/m_l_i 公式 = 自己定義嘅 m_ν 除自己定義嘅 m_l = X/X = 1
  → 唔係預言!

正確驗證法: 鎖定所有輸入參數, 預測「尚未被輸入該公式」嘅物理量

盲測協議 (scripts/test_blind_neutrino_predictions.py):
  INPUT (僅輸入):
    v = 246 GeV, γ₆ = 0.1807
    M_comp = 鎖定值 (兩個候選: 3.69e13 GeV 同 1.49e11 GeV)
    m_e, m_μ, m_τ (帶電輕子, 輸入用嚟做 Yukawa 尺度, 唔輸入 ν 數據)
  DO NOT INPUT:
    Δm²₂₁ (太陽), Δm²₃₁ (大氣), Σm_ν (Planck/DESI), m_ββ

  OUTPUT (盲測標的):
    1. m_ν₃ = (γ₆v)²/M_comp → Δm²₃₁ ≈ m₃² (m₁<<m₃)
    2. m_ν₂, m_ν₁: 測試兩種世代結構:
       a) φ 階梯 (m₂=m₃/φ, m₁=m₃/φ²) ← 之前用嘅, 懷疑係 artifact
       b) 正常化 Normal Hierarchy (m₂²-m₁²=Δm²₂₁ 求解)
    3. Δm²₂₁ / Δm²₃₁ 比例 vs 實驗 ~0.031
    4. Σm_ν vs Planck/DESI 限制 (<0.12, <0.072)
    5. m_ββ = |Σ U_ei² m_νi| (假設大混合角)
"""
import sys, os, math
import json
import numpy as np

phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 十六期 87: ★★ 中微子盲測")
print("=" * 72)

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

# ============ 1. 鎖定輸入 ============
print("\n[1] 鎖定輸入參數 (Peer 協議)")
v = 246.0  # GeV
gamma6 = 0.18073600929096323
m_e, m_mu, m_tau = 0.511e-3, 105.66e-3, 1.77686  # GeV (輸入輕子)

# 實驗標的 (盲測完先揭示)
dm21_exp = 7.53e-5   # eV²
dm31_exp = 2.434e-3  # eV²
sum_nu_planck = 0.12  # eV
sum_nu_desi = 0.072   # eV (DESI 2024)

print(f"  v = {v} GeV")
print(f"  γ₆ = {gamma6:.6f}")
print(f"  m_e = {m_e*1e3:.3f} MeV, m_μ = {m_mu*1e3:.2f} MeV, m_τ = {m_tau*1e3:.2f} MeV")
print(f"  M_comp: 候選 1 = 3.69e13 GeV, 候選 2 = 1.49e11 GeV")

# ============ 2. M_comp 掃描 ============
print("\n[2] M_comp 掃描 — m_ν₃ = (γ₆v)²/M_comp")
for M_comp in [3.69e13, 1.49e11, 1.22e19]:
    m3 = (gamma6 * v)**2 / M_comp  # GeV
    print(f"  M_comp = {M_comp:.2e} GeV → m_ν₃ = {m3*1e9:.4f} eV")
    print(f"    Δm²₃₁ ≈ m₃² = {(m3*1e9)**2:.3e} eV² (實驗 2.434e-3)")

# ============ 3. 主測試: M_comp = 3.69e13 (由 m_ν₃≈0.05 eV 反推) ============
print("\n[3] 主測試: M_comp = 3.69e13 GeV")
M_comp = 3.69e13
m3 = (gamma6 * v)**2 / M_comp  # GeV
m3_eV = m3 * 1e9
print(f"  m_ν₃ = {m3_eV:.4f} eV")

# 3a. φ 階梯 (之前用嘅, 懷疑 artifact)
print("\n  [3a] φ 階梯: m₂=m₃/φ, m₁=m₃/φ²")
m3_f = m3_eV
m2_f = m3_f / phi
m1_f = m3_f / phi**2
dm31_f = m3_f**2 - m1_f**2
dm21_f = m2_f**2 - m1_f**2
ratio_f = dm21_f / dm31_f
print(f"    m₁ = {m1_f:.4f} eV, m₂ = {m2_f:.4f} eV, m₃ = {m3_f:.4f} eV")
print(f"    Δm²₂₁ = {dm21_f:.3e} eV² (實驗 7.53e-5)")
print(f"    Δm²₃₁ = {dm31_f:.3e} eV² (實驗 2.434e-3)")
print(f"    Δm²₂₁/Δm²₃₁ = {ratio_f:.3f} (實驗 0.031)")
check("φ 階梯 Δm²₂₁", abs(dm21_f - dm21_exp)/dm21_exp < 0.5, f"({dm21_f:.2e} vs {dm21_exp:.2e})")
check("φ 階梯比例", abs(ratio_f - 0.031)/0.031 < 0.5, f"({ratio_f:.3f} vs 0.031)")
check("φ 階梯 Δm²₃₁", abs(dm31_f - dm31_exp)/dm31_exp < 0.05, f"({dm31_f:.3e} vs {dm31_exp:.3e})")

# 3b. Σm_ν
print("\n  [3b] Σm_ν (φ 階梯)")
sum_f = m1_f + m2_f + m3_f
print(f"    Σm_ν = {sum_f:.4f} eV (Planck <0.12, DESI <0.072)")
check("Σm_ν < Planck 0.12", sum_f < sum_nu_planck, f"({sum_f:.4f})")
check("Σm_ν < DESI 0.072", sum_f < sum_nu_desi, f"({sum_f:.4f} vs 0.072)")

# 3c. m_ββ (大混合角假設 U_ei ≈ 1/√3)
print("\n  [3c] m_ββ (假設 U_ei ≈ 1/√3, 大混合角)")
mbb_f = abs(m1_f + m2_f + m3_f) / 3  # 粗略: |Σ U_ei² m_i|, U_ei²≈1/3
print(f"    m_ββ ≈ {mbb_f*1e3:.1f} meV (KamLAND-Zen/LEGEND 敏感區 10-50 meV)")
check("m_ββ 落入 10-50 meV", 10 <= mbb_f*1e3 <= 50, f"({mbb_f*1e3:.1f} meV)")

# 3d. 正常化 NH: 用 m₃ 同實驗 Δm² 求 m₁, m₂
print("\n  [3d] 正常化 NH (m₃ 固定, 由 Δm² 反解 m₁,m₂)")
# m₃²-m₁² = Δm²₃₁ → m₁ = sqrt(m₃²-Δm²₃₁)
# m₂²-m₁² = Δm²₂₁ → m₂ = sqrt(m₁²+Δm²₂₁)
m3_sq = m3_eV**2
m1_nh = math.sqrt(max(m3_sq - dm31_exp, 0))
m2_nh = math.sqrt(m1_nh**2 + dm21_exp)
print(f"    m₁ = {m1_nh:.4f} eV, m₂ = {m2_nh:.4f} eV, m₃ = {m3_eV:.4f} eV")
print(f"    m₂/m₁ = {m2_nh/m1_nh:.4f} (φ = {phi:.4f})")
print(f"    驗證: Δm²₃₁ = {m3_eV**2-m1_nh**2:.3e} (應 2.434e-3)")
print(f"    驗證: Δm²₂₁ = {m2_nh**2-m1_nh**2:.3e} (應 7.53e-5)")
check("NH m₂/m₁ ≈ 1 (近簡併)", abs(m2_nh/m1_nh - 1) < 0.3, f"({m2_nh/m1_nh:.3f})")
check("NH m₂/m₁ ≠ φ", abs(m2_nh/m1_nh - phi) > 0.5, f"({m2_nh/m1_nh:.3f} vs φ={phi:.3f})")

# 3e. Σm_ν (NH)
sum_nh = m1_nh + m2_nh + m3_eV
print(f"\n  [3e] Σm_ν (NH) = {sum_nh:.4f} eV")
check("NH Σm_ν < Planck 0.12", sum_nh < sum_nu_planck, f"({sum_nh:.4f})")
check("NH Σm_ν < DESI 0.072", sum_nh < sum_nu_desi, f"({sum_nh:.4f} vs 0.072)")

# 3f. m_ββ (NH)
mbb_nh = abs(m1_nh + m2_nh + m3_eV) / 3
print(f"\n  [3f] m_ββ (NH) ≈ {mbb_nh*1e3:.1f} meV")
check("NH m_ββ 落入 10-50 meV", 10 <= mbb_nh*1e3 <= 50, f"({mbb_nh*1e3:.1f} meV)")

# ============ 4. M_comp = 1.49e11 (Peer 候選) ============
print("\n[4] M_comp = 1.49e11 GeV (Peer 建議)")
M_comp2 = 1.49e11
m3_2 = (gamma6 * v)**2 / M_comp2 * 1e9  # eV
print(f"  m_ν₃ = {m3_2:.2f} eV")
print(f"  Δm²₃₁ ≈ m₃² = {m3_2**2:.2e} eV² (實驗 2.434e-3)")
check("M_comp=1.49e11 Δm²₃₁", abs(m3_2**2 - dm31_exp)/dm31_exp < 0.5,
      f"({m3_2**2:.1e} vs {dm31_exp:.1e})")

# ============ 5. M_comp 有冇結構? ============
print("\n[5] M_comp = 3.69e13 GeV 結構檢查")
M_pl = 1.2209e19  # GeV
print(f"  M_comp/M_pl = {M_comp/M_pl:.3e}")
print(f"  log10(M_comp) = {math.log10(M_comp):.4f}")
print(f"  log10(M_pl) = {math.log10(M_pl):.4f}")
print(f"  log10(M_pl/M_comp) = {math.log10(M_pl/M_comp):.4f}")
print(f"  γ₆⁻¹ = {1/gamma6:.4f}")
print(f"  44/γ₆ = {44/gamma6:.2f}")
print(f"  M_pl × γ₆⁸ = {M_pl*gamma6**8:.2e}")
print(f"  M_pl × γ₆⁷ = {M_pl*gamma6**7:.2e}")
print(f"  M_pl × γ₆⁷.5 = {M_pl*gamma6**7.5:.2e}")
print(f"  (v/γ₆)² /M_pl = {(v/gamma6)**2/M_pl:.2e}")
print(f"  v/γ₆² = {v/gamma6**2:.2e}")
check("M_comp 有簡單結構", False, "M_comp = 3.69e13 GeV 未由第一性原理推導 → 本身係 fit 參數!")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("十六期 87 盲測總結:")
print("=" * 72)
print(f"""
  ★★★ 盲測結果 (Peer 協議):
  ─────────────────────────────────
  1. M_comp = 3.69e13 GeV:
     m_ν₃ = {m3_eV:.4f} eV (絕對尺度預言)
     Δm²₃₁ ≈ {dm31_f:.3e} (φ階梯) / {m3_eV**2-m1_nh**2:.3e} (NH) vs 2.434e-3
     Δm²₂₁ = {dm21_f:.3e} (φ階梯) — ❌ 實驗 7.53e-5 差 {dm21_f/dm21_exp:.0f} 倍!
     Δm²₂₁/Δm²₃₁ = {ratio_f:.3f} (φ階梯) vs 實驗 0.031 — ❌ 差 {ratio_f/0.031:.0f} 倍!
     Σm_ν = {sum_f:.4f} eV (φ階梯) / {sum_nh:.4f} eV (NH)
     m_ββ ≈ {mbb_f*1e3:.1f} meV (φ階梯) / {mbb_nh*1e3:.1f} meV (NH)

  2. 🔴 φ 階梯盲測 FAIL:
     Δm²₂₁ 差 9 倍, 比例差 9 倍
     → ν 世代 φ 階梯 (m₂=m₃/φ) 係錯誤假設
     → 同十四期「φ 階梯係 artifact」結論一致!

  3. ✅ 真正嘅預言: m_ν₃ = (γ₆v)²/M_comp = {m3_eV:.4f} eV
     Δm²₃₁ ≈ m₃² (m₁<<m₃ 時) = {m3_eV**2:.3e} eV² vs 2.434e-3 ({abs(m3_eV**2-dm31_exp)/dm31_exp*100:.1f}%)
     → 呢個先係非 tautology 預言 (M_comp 需獨立鎖定)

  4. 🔴 M_comp = 3.69e13 GeV 本身係 fit 參數 (未推導):
     M_comp/M_pl = 3.02e-6, log 比例 5.52
     冇簡單 IDCM 結構 → 需 O62 第一性原理推導

  5. 🔴 Σm_ν = {sum_f:.3f} eV (φ) / {sum_nh:.3f} eV (NH):
     可能違反 DESI 2024 <0.072 eV → 需注意
""")

results = {
    "test": "O57 十六期 87: 盲測",
    "M_comp_candidates": [3.69e13, 1.49e11],
    "m3_eV": float(m3_eV),
    "phi_ladder": {"m1": float(m1_f), "m2": float(m2_f), "m3": float(m3_f),
                   "dm21": float(dm21_f), "dm31": float(dm31_f), "ratio": float(ratio_f)},
    "nh": {"m1": float(m1_nh), "m2": float(m2_nh), "m3": float(m3_eV),
           "sum": float(sum_nh), "mbb": float(mbb_nh*1e3)},
    "phi_sum": float(sum_f), "phi_mbb": float(mbb_f*1e3),
    "passed": passed, "failed": failed
}
with open("data/87_blind_neutrino.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
print("🎉 十六期 87 盲測完成 (誠實記錄)")
exit(0)
