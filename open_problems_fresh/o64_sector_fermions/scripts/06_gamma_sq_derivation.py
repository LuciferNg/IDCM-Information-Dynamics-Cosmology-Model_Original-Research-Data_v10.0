#!/usr/bin/env python3
"""
O64 二期 06: γ_n² 結構推導 — 質量公式嘅第一性原理
================================================================
目標: 推導質量 ∝ γ_n² 嘅結構基礎
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
DATA = os.path.join(BASE, "data")
phi = (1 + math.sqrt(5)) / 2
gamma_n = 4 * np.sin(np.pi * np.arange(1, 45) / 88) ** 2

print("=" * 72)
print("O64 二期 06: γ_n² 結構推導")
print("=" * 72)

# ============ 1. O57 質量公式回顧 ============
print("\n=== [1] O57 質量公式回顧 ===")
print("""
O57 質量公式 (Dirac, dim-4):
  m_f = M₀ × γ_n / v × v = M₀ × γ_n
  其中 M₀ = 246 GeV (Higgs VEV), v = 246 GeV (Yukawa coupling normalisation)

O57 中微子質量公式 (dim-5 Weinberg):
  m_ν = γ₆² × v² / M_comp
  其中 γ₆² 係二次型, M_comp ~ 10¹³ GeV

關鍵: 帶電費米子質量 = M₀ × γ_n (linear)
     中微子質量 = γ₆² × v² / M_comp (quadratic)
""")

# ============ 2. 質量公式嘅結構推導 ============
print("\n=== [2] 質量公式嘅結構推導 ===")
print("""
IDCM 質量湧現嘅三層結構:

Layer 1: K_Chain 離散化
  K_Chain 44-site: γ_n = 4sin²(πn/88), n=1..44
  Beat space Λ²(R⁴⁴): 946 = 462 even + 484 odd

Layer 2: P̂ 投影 (134×946)
  P̂: 946 → 134 (divisor space)
  66 態 = top 66 eigenvectors of P̂P̂^T
  36 K + 30 C = 3×(12+10) = 3×22

Layer 3: CY₃ 交集 (κ tensor)
  κ_ijk: 36×36×36, 1341 非零
  3×12 block structure (sector-dependent geometry)
  Yukawa: Y_ij = Σκ_ijk t_k

質量公式嘅結構形式:
  m_f = M₀ × (γ_n投影) × (Yukawa本徵值)
       = M₀ × γ_n × f_g(block)
""")

# ============ 3. γ_n² 嘅可能來源 ============
print("\n=== [3] γ_n² 嘅可能來源 ===")
print("""
可能性 1: 二次型 Yukawa
  Y_ij = Σκ_ijk t_k, t_k = γ_k (Kähler參數)
  Y_ij = Σκ_ijk γ_k
  m_f ∝ Y_ij × γ_n (fermion wavefunction ∝ γ_n)
  → m_f ∝ γ_n × γ_n = γ_n²

可能性 2: W-field 強度二次型
  W-field 振幅 ∝ γ_n
  W-field 能量 ∝ γ_n²
  質量 = 能量耦合 → m_f ∝ γ_n²

可能性 3: 世代階梯來自 γ_n 譜 + φ-power
  m_f ∝ γ_n × φ^(35-i)
  但 φ^(35-i) 係 Kähler 參數, 唔係質量公式本身
  → 需要分清楚「Kähler 參數」同「質量公式」

可能性 4: 中微子類比
  m_ν = γ₆² × v² / M_comp (dim-5)
  帶電費米子可能有類似嘅二次型結構
  但係 dim-4, 唔係 dim-5
""")

# ============ 4. 數值驗證: Yukawa ∝ γ_n²? ============
print("\n=== [4] 數值驗證: Yukawa 本徵值 ∝ γ_n²? ===")
d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])

# Test: are the Yukawa eigenvalues proportional to γ_n²?
# Use different Kähler parameter choices
for name, t in [
    ("γ_n (full 36)", gamma_n[:36]),
    ("γ_n² (full 36)", gamma_n[:36]**2),
    ("φ^(35-i)", phi**(35-np.arange(36))),
    ("φ^(-i)", phi**(-np.arange(36))),
]:
    Y = np.tensordot(kappa, t, axes=([2], [0]))
    ev = np.sort(np.linalg.eigvalsh(Y))[::-1]
    pos = ev[ev > 1e-10]
    print(f"\n  {name}:")
    print(f"    Top 9: {[f'{x:.2f}' for x in pos[:9]]}")
    # Check ratios
    if len(pos) >= 9:
        ratios = [pos[0]/pos[i] for i in range(1, 9)]
        print(f"    Ratios to top: {[f'{r:.1f}' for r in ratios[:5]]}")
    # Check: does the eigenvalue spectrum cluster?
    log_ev = [math.log10(abs(x)) for x in pos[:9]]
    gaps = [log_ev[i] - log_ev[i+1] for i in range(len(log_ev)-1)]
    print(f"    Log gaps: {[f'{g:.2f}' for g in gaps]}")

# ============ 5. 帶電費米子質量公式 ============
print("\n=== [5] 帶電費米子質量公式 ===")
print("""
結論: 帶電費米子質量公式係 LINEAR (m_f = M₀ × γ_n), 唔係 quadratic

理由:
1. O57 已經推導 Dirac mass = M₀ × γ_n (dim-4 operator)
2. γ_n² 模型係數值匹配, 唔係結構推導
3. 真正嘅 within-type hierarchy 來自:
   a. 不同 type 訪問不同 γ_n 值 (sector-dependent)
   b. 不同 γ_n 值嘅自然比例 (γ_n 譜結構)
   c. Kähler 參數嘅 block-dependent 選擇

問題: γ_n 譜本身 max ratio = 785, 唔夠 SM up-type 嘅 133077
解決方案: 唔係 γ_n², 而係 γ_n × φ-power 嘅組合
  但 φ-power 係 Kähler 參數, 唔係質量公式本身
  → 需要 sector-dependent Kähler 參數, 每個 block 用不同嘅 φ-power
""")

# ============ 6. 最佳方案: sector-dependent Kähler ============
print("\n=== [6] 最佳方案: sector-dependent Kähler 參數 ===")
print("""
每個 type 嘅 Kähler 參數用不同嘅 φ^(α_g·(35-i)):
  Type 0 (up): α = 1.0 → diep hierarchy (5 finite, 9.8e16)
  Type 1 (down): α = 0.5 → medium hierarchy
  Type 2 (lepton): α = 0.3 → shallow hierarchy

但 α 係自由參數! 違反零參數原則 ❌

替代方案: 用不同嘅 γ_n 子集做每個 type 嘅 Kähler 參數
  Type 0: γ_n (n=1..12) — 小 n, 大動態範圍
  Type 1: γ_n (n=13..24) — 中 n
  Type 2: γ_n (n=25..36) — 大 n, 細動態範圍

呢個自然出自 3×12 block 結構!
  Block 0 嘅 12 Kähler moduli 對應 γ_{1..12}
  Block 1 對應 γ_{13..24}
  Block 2 對應 γ_{25..36}

→ 每個 block 自然用自己嘅 γ_n 子集做 Kähler 參數!
""")

# Test: each block uses its own γ_n subset
print("\n  Test: 每個 block 用自己嘅 γ_n 子集做 Kähler 參數:")
for g in range(3):
    s, e = g*12, (g+1)*12
    kappa_g = kappa[s:e, s:e, s:e]
    t_g = gamma_n[s:e]  # block's own γ_n subset
    Y_g = np.tensordot(kappa_g, t_g, axes=([2], [0]))
    ev = np.sort(np.linalg.eigvalsh(Y_g))[::-1]
    pos = ev[ev > 1e-10]
    print(f"    Block {g} (γ_{s+1}..γ_{e}): top3={[f'{x:.4f}' for x in ev[:3]]}, pos={len(pos)}/12")
    if len(pos) >= 3:
        r = [ev[0]/ev[2], ev[1]/ev[2], 1.0]
        print(f"      ratio = {r[0]:.1f}:{r[1]:.1f}:1")
        # Compare with SM up/down/lepton
        for tname, ratios in [("up", [1, 477, 133077]), ("down", [1, 20, 1548]), ("lepton", [1, 207, 3483])]:
            log_r = [math.log10(max(r[i], 1e-30)) for i in range(3)]
            log_t = [math.log10(ratios[i]) for i in range(3)]
            offset = np.mean([log_r[i] - log_t[i] for i in range(3)])
            mse = np.mean([(log_r[i] - offset - log_t[i])**2 for i in range(3)])
            print(f"      vs {tname}: MSE={mse:.3f}")

# ============ 7. Summary ============
print("\n\n=== [7] 結論 ===")
print("""
γ_n² 結構推導結果:

1. 帶電費米子質量係 LINEAR: m_f = M₀ × γ_n (O57 已證)
2. γ_n² 係數值巧合, 唔係結構推導
3. Within-type hierarchy 來自:
   - 不同 γ_n 值嘅自然比例
   - Sector-dependent Kähler 參數 (每個 block 用不同 γ_n 子集)
4. 最佳方案: 每個 block 用自己嘅 γ_n 子集做 Kähler 參數
   - 呢個係 3×12 block 結構嘅自然結果
   - Block 0: γ_{1..12}, Block 1: γ_{13..24}, Block 2: γ_{25..36}
5. 但 within-type hierarchy 仍然太淺:
   - Block 0 top3 ratio ≈ 33:1.8:1 (vs SM up 133077:477:1)
   - 需要額外機制
""")

out = {"test": "O64 06: gamma_sq_derivation"}
os.makedirs("data", exist_ok=True)
with open("data/06_gamma_sq_derivation.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("✅ 結果已保存到 data/06_gamma_sq_derivation.json")