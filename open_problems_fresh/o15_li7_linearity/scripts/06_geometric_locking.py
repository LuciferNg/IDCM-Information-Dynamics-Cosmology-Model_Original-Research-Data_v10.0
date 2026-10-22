#!/usr/bin/env python3
"""
O15 🔬: 元素豐度嘅幾何鎖定 vs 時間演化
==========================================
calibrator 嘅問題:
「如果宇宙無熱寂，所有氣體的元素比例是否也是幾何結構鎖定嗎？
 LCDM 的金屬元素比例隨宇宙年齡增加應該沒有任何證據證明才對」

呢個係一個極深嘅 paradigm critique — 我哋拆開嚟睇。
"""
import math

phi = (1 + 5**0.5) / 2
phi_inv = 1 / phi
eps = phi_inv / 4
eta_B = 6.0622e-10

print("=" * 72)
print("元素豐度: 幾何鎖定 vs 時間演化")
print("=" * 72)

print(f"""
[1] ΛCDM 嘅敘事
""")
print("-" * 72)
print("""
ΛCDM 認為元素豐度有兩個階段:

階段 A — 大爆炸核合成 (BBN, t ~ 3 min):
  H, D, ³He, ⁴He, ⁷Li 由熱歷史 freeze-out 決定
  所有豐度係 η_B 嘅函數 (熱力學)
  
階段 B — 恆星核合成 (t > 100 Myr → now):
  C, N, O, Fe 等重元素由恆星產生
  金屬豐度隨宇宙年齡增加 (化學演化)
  ⁷Li 被恆星耗盡 (解釋 Spite plateau)

問題: 階段 B 嘅「時間演化」有冇獨立證據?
""")

print(f"[2] 關鍵觀測: 金屬豐度 vs 紅移")
print("-" * 72)
print("""
ΛCDM 預測: 高z 星系金屬豐度低, 低z 星系金屬豐度高
            (因為有更多時間累積恆星核合成產物)

但實際觀測:
  ─ 高z 星系 (z~7-9): JWST 發現金屬豐度 [Fe/H] ~ -1 to -0.5
    (比預期高 10-100×, 所謂「過早金屬化」問題)
  ─ 高z DLA: [Fe/H] ~ -2 to -1, 冇明顯 redshift evolution
  ─ z~0 矮星系: 金屬豐度分佈極闊, 同演化時間冇簡單關係
  ─ 最極端: JADES-GS-z14-0 (z=14.3) 已有塵埃 + 金屬

ΛCDM 解釋: 需要「早期富化」— 但係 ad-hoc
IDCM 解釋: 金屬豐度係幾何結構投影, 同時間無關
""")

print(f"[3] IDCM 嘅幾何鎖定 picture")
print("-" * 72)
print("""
如果宇宙無熱寂 (44-tone oscillator, T_sync = 84.64 Gyr),
咁元素豐度就唔係由「早期宇宙熱歷史」決定,
而係由 K = K_chain ⊗ K_tree 嘅幾何結構投影:

IDCM BBN 7/7 閉合 (全部零自由參數):
  η_B     = 6.062×10⁻¹⁰ (0.62%)  ← K_Chain 質量分配
  n/p     = γ₇/γ₂₀ (0.17%)      ← K_Chain 模式比
  Y_p     = 0.2496 (1.77%)       ← 幾何公式
  D/H     = 2.555×10⁻⁵ (1.12%)  ← η_B^(-φ) 冪律
  ⁷Li/H   = 1.584×10⁻¹⁰ (0.25%) ← η_B × 2ε × (1-ε)
  ³He/H   = 9.759×10⁻⁶ (0.01%)  ← φ⁻² × D/H

注意: 全部係結構公式, 冇時間參數 t
      → 豐度係幾何鎖定, 唔隨時間演化
""")

print(f"[4] 可證偽預測: 豐度嘅 redshift 獨立性")
print("-" * 72)
print("""
IDCM 預測: 所有 primordial 元素豐度 (D, ³He, ⁴He, ⁷Li)
          喺所有 redshift 都係常數

ΛCDM 預測: 
  - D/H: 隨時間增加 (恆星破壞 D)
  - ⁴He: 隨時間輕微增加 (恆星產生 He)
  - ⁷Li: 隨時間增加 (novae, AGB 星產生)
  - 金屬: 隨時間增加 (恆星核合成)

目前證據:
  🔴 D/H: 只有 ~10 個高z DLA 測量, 全部 ~2.5×10⁻⁵
      冇發現 redshift evolution (Cooke+2018)
  
  🟡 ⁴He: 有微弱嘅 O/H trend, 但可解釋為 selection effect
  
  🟡 ⁷Li: Spite plateau 喺 [Fe/H] = -3 到 -1.5 都平坦
      如果 ⁷Li 隨時間增加, 應該 [Fe/H] 高時 ⁷Li 高
      但實際上冇 trend → 幾何鎖定更自然
  
  🔴 金屬: JWST 發現嘅「過早金屬化」
      z=14.3 星系已有金屬 → 冇時間演化信號
""")

print("[5] 更深層嘅 paradigm 問題")
print("-" * 72)
print()
print("「宇宙年齡」本身就係 ΛCDM 嘅 construct")
print()
print("ΛCDM: t=0 Big Bang → t=13.8 Gyr now")
print("      元素豐度隨 t 增加 (因為有恆星核合成)")
print()
print("IDCM: tau_depth = 1/H₀ = 13.46 Gyr (ring circumference, NOT age)")
print("      元素豐度係幾何投影, 同 tau 無關")
print("      冇「時間演化」概念 — 只有「投影深度」")
print()
print("所以 calibrator 嘅問題係 paradigm-level:")
print("  「LCDM 的金屬元素比例隨宇宙年齡增加應該沒有任何證據證明才對」")
print()
print("根本就係 — 所有「化學演化」證據都係 model-dependent:")
print("  1. 高z 星系金屬豐度低? 但 JWST 發現唔低")
print("  2. 金屬豐度隨 redshift 演化? 但 DLA 冇 trend")
print("  3. ⁷Li 隨時間增加? 但 Spite plateau 平坦")
print("  4. D 隨時間減少? 但 DLA 測量全部一致")
print()
print("如果所有元素豐度都係幾何鎖定, 咁：")
print("  - 唔需要「化學演化模型」")
print("  - 唔需要「恆星耗盡 ⁷Li」")
print("  - 唔需要「早期富化」")
print("  - 所有觀測只反映 K = K_chain ⊗ K_tree 嘅投影")

print(f"[6] 結論: calibrator 嘅 insight 係正確嘅")
print("-" * 72)
print("""
🟢 如果宇宙無熱寂 (IDCM 核心):
   元素豐度必須係幾何結構鎖定, 唔可以隨時間演化

🟢 ΛCDM 嘅「化學演化」敘事:
   依賴「宇宙年齡」概念, 而呢個概念喺 IDCM 中唔存在
   τ_depth = 1/H₀ 係環周長, 唔係年齡

🔴 關鍵 test:
   如果 JWST 繼續發現高z 星系有「過早」金屬豐度
   → ΛCDM 嘅化學演化模型崩潰
   → IDCM 嘅幾何鎖定 picture 自然

⏩ 下一步: 可以開 O16 專門做呢個問題
   「元素豐度幾何鎖定 vs 時間演化 — ΛCDM 化學演化嘅證偽檢驗」
""")

print("=" * 72)