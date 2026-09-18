"""
O73 攻堅 20: 🔴 ΛCDM I 分歧深挖 — 1.6% 有冇結構來源?
=================================================================
已知:
  H₀_CMB = ω_ring × 7I/24 (IDCM θ* + r_s + ΛCDM 幾何)
  要得 67.41 → I = 24(1-π/44)/7 = 3.1838
  實際 ΛCDM I(Planck Ω) = 3.1311 (含 radiation)
  分歧 = 1.6%

問題:
  1. I 嘅 1.6% 分歧有冇結構解釋? (44 系? φ?)
  2. I 嘅組成: 物質/輻射/Λ 各自貢獻幾多?
  3. 如果 IDCM 冇膨脹, I 應該點計?

⚠️ 更正 (2026-09-18 重驗, 原文保留):
  上面「I = 3.1311 (含 radiation)」係**標籤錯** — 3.1311 係「無 radiation」值。
  本 script 實算: I_full (含 radiation) = 3.11588, I_no_rad = 3.13109。
  分歧 = 2.179% (含 radiation) / 1.69% (無 radiation), 唔係 1.6%。
  (原 1.6% 來自 docs/08 引用 3.1311 做含 radiation — 已由 docs/12 §0 記錄修正)
  ⚠️ O169 更正 (09-15): 本 script 印出嘅 D_app(ℓ) 伸長因子 (1+2φ⁻¹ℓ) **已證偽**
  (DESI DR2 D_M×6 4.88σ) → 新式 E(ℓ) = ℓ + 1.11911398。O73 θ*/I* 推導唔經此路,
  結論不受影響 (見 scripts/22_o169_crosscheck.py)。
"""
import numpy as np
import mpmath as mp

print("=" * 74)
print("1. I 嘅結構分解 (ΛCDM 積分)")
print("=" * 74)

def I_LCDM(Om, Ol, zstar=1090, Or=9.15e-5):
    zs = np.linspace(0, zstar, 500000)
    E = np.sqrt(Om*(1+zs)**3 + Ol + Or*(1+zs)**4)
    return np.trapezoid(1/E, zs)

# Planck 2018 參數
Om = 0.3153
Ol = 0.6847
Or = 9.15e-5
I_full = I_LCDM(Om, Ol, Or=Or)
I_no_rad = I_LCDM(Om, Ol, Or=0)
print(f"  I_full (含 radiation) = {I_full:.5f}")
print(f"  I_no_rad (無 radiation) = {I_no_rad:.5f}")
print(f"  radiation 貢獻 = {I_no_rad - I_full:.5f} ({(I_no_rad-I_full)/I_full*100:.2f}%)")
print()

print("=" * 74)
print("2. IDCM 需要嘅 I* = 3.1838")
print("=" * 74)
I_star = 24 * (1 - mp.pi/44) / 7
I_star_f = float(I_star)
print(f"  I* = 24(1-π/44)/7 = {mp.nstr(I_star, 6)}")
print(f"  I* - I_full = {I_star_f - I_full:.5f}")
print(f"  dev = {(I_star_f-I_full)/I_full*100:.3f}%")
print()

print("=" * 74)
print("3. 2.18% 分歧有冇結構來源? (原記 1.6%, 已更正 — docs/12 §0)")
print("=" * 74)
# 檢查: I* / I_full = ?
ratio = I_star_f / I_full
print(f"  I*/I_full = {ratio:.6f}")
print(f"  1 - I*/I_full = {1-ratio:.6f} = {(1-ratio)*100:.3f}%")
print()
# 候選結構: 1/88, 1/44, π/44, φ⁻¹, φ⁻²
cands = {
    "1/88": 1/88,
    "1/44": 1/44,
    "π/44": np.pi/44,
    "φ⁻¹": 1/1.61803398875,
    "φ⁻²": 1/1.61803398875**2,
    "2π/88": 2*np.pi/88,
}
diff = 1 - ratio  # 0.0165
print(f"  目標差: 1 - I*/I_full = {diff:.6f}")
for name, v in cands.items():
    print(f"  {name:8s} = {v:.6f}   ratio to diff = {v/diff:.3f}")
print()

print("=" * 74)
print("4. 更深: I* 同 1-π/44 嘅關係")
print("=" * 74)
print(f"  I* = 24(1-π/44)/7 = {I_star_f:.5f}")
print(f"  7I*/24 = 1-π/44 = {7*I_star_f/24:.6f} ✅ (定義)")
print()
print(f"  如果 I 由 ΛCDM 定義: I = ∫dz/E(z)")
print(f"  IDCM 要求 I* = 3.1838")
print(f"  → IDCM 版本嘅「有效 E(z)」要令積分 = 3.1838")
print(f"  → 對比 ΛCDM E(z) 積分 = {I_full:.5f} (含 radiation; 無 radiation {I_no_rad:.5f})")
print(f"  → 差 {(I_star_f-I_full)/I_full*100:.2f}% 即係「距離尺度差 {(I_star_f-I_full)/I_full*100:.2f}%」")
print(f"    [2026-09-18 更正: 原文寫 1.6% + 誤引 3.1311 做含 radiation — 見 docs/12 §0]")
print()
print(f"  但! IDCM 有 D_app(ℓ) (O51, 伸長因子 09-15 由 O169 更新):")
print(f"    舊 (已證偽): D_app(ℓ) = (44-44/4^ℓ)(R_world/44)(1+2φ⁻¹ℓ)")
print(f"    新 (零參數): D_app(ℓ) = R_world(1-4^-ℓ)·E(ℓ), E(ℓ) = ℓ + 1.11911398")
print(f"  → D_app 由世界環幾何定義, 冇 H(z) 積分!")
print(f"  → 「I 分歧」正正係因為 ΛCDM 用 H(z) 積分,")
print(f"     IDCM 用世界環幾何投影 — 兩套幾何!") 
print()

print("=" * 74)
print("5. ★ 關鍵洞見: I* = 3.1838 有冇直接結構?")
print("=" * 74)
# I* = 24(1-π/44)/7 = (24/7)(1-π/44)
# = (24/7) - (24/7)(π/44)
# = 24/7 - 6π/77
a = 24/7
b = 6*np.pi/77
print(f"  I* = 24/7 - 6π/77")
print(f"     = {a:.6f} - {b:.6f}")
print(f"     = {a-b:.6f}")
print()
print(f"  24/7 = {a:.6f} (D_A 因子, θ* = 7π/2112 來源)")
print(f"  6π/77 = {b:.6f} (π×6/77)")
print(f"  6 = 2B? 77 = 7×11? 11 = L₅?")
print(f"  77 = 7×11 = L₄ × L₅ (Lucas 4×5!)")
print(f"  6 = 2×3 = 2B? N_gen?")
print(f"  24 = 2BN_gen×4?")
print()

# 另一角度: I* 有冇可能 = 1/θ_site × 某因子?
theta_site = 2*np.pi/88
print(f"  I* × θ_site = {I_star_f * theta_site:.6f}")
print(f"  = 24(1-π/44)/7 × π/44")
print(f"  = 24π(1-π/44)/(7×44)")
print(f"  = {24*np.pi*(1-np.pi/44)/(7*44):.6f}")
print()
print(f"  I*/θ_site = {I_star_f/theta_site:.4f}")
print(f"  = 24(1-π/44)/(7π/44) = 24(44-π)/(7π)")
print(f"  = {24*(44-np.pi)/(7*np.pi):.4f}")
print(f"  14.19 ≈ 14.006 (44/π)?")
print(f"  44/π = {44/np.pi:.4f}")
print(f"  dev = {(24*(44-np.pi)/(7*np.pi))/(44/np.pi)-1:.4f}")
print()

print("=" * 74)
print("6. 結論")
print("=" * 74)
print(f"""
  I* = 3.1838 = 24(1-π/44)/7 = 24/7 - 6π/77

  結構: 
    24/7 = D_A 因子 (θ* = 7π/2112 同源!)
    6π/77 = π × 6/77, 77 = 7×11 = L₄×L₅, 6 = 2×3

  → I* 唔係獨立數字 — 係 (1-π/44) 嘅代數變形!
  → 「I 分歧 2.18% (含 radiation; 無 radiation 1.69%)」= ΛCDM 積分 I(Ω) 對比 IDCM 幾何嘅本質差異
  → IDCM 冇膨脹, 冇 H(z) 積分 — D_app(ℓ) 直接由世界環幾何嚟

  🔴 但: 6π/77 嘅 77 = 7×11 係「數值巧合」定「結構」?
     需要驗證: 77 喺 IDCM 有冇出現? (L₄×L₅ = 7×11 = 77)
     L₅ = 11 (Lucas 5 = φ⁵+φ⁻⁵ = 11.0) — 有!
     6 = 2B? (B=4 → 2B=8, 唔係 6)
     6 = N_gen × 2? (3×2)
     → 未確認結構, 標記 🟡
""")
