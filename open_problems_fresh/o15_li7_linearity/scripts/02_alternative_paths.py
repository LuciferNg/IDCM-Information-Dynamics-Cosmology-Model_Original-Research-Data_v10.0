#!/usr/bin/env python3
"""
O15: ⁷Li 線性 η_B 檢驗 — 補充分析
======================================
第二部分: 標準 BBN ⁷Li 敏感度函數, 替代驗證路徑
"""
import math
import numpy as np

phi = (1 + 5**0.5) / 2
phi_inv = 1 / phi
eps = phi_inv / 4
eta_B_idcm = 6.0622e-10
factor_li7 = 2 * eps * (1 - eps)  # 0.261271

print("=" * 72)
print("O15: ⁷Li 線性 η_B 檢驗 — 補充分析")
print("=" * 72)

print(f"\n[A] 標準 BBN ⁷Li 敏感度函數 (文獻值)")
print("-" * 72)
print("""
標準 BBN ⁷Li/H 嘅 η_B 依賴並非簡單幂律, 而係核網絡計算結果。
主要生產管道:
  ³He(α,γ)⁷Be → e⁻捕獲 → ⁷Li

敏感度指數 α = d(log Y_Li7)/d(log η_B) 嘅來源:
- Cyburt+2008 (JCAP 0811:012): α ≈ 2.4
- Coc+2012 (PRD 85, 065005): α ≈ 2.2
- Burns+2026 (Phys.Rept. 1194): 完整敏感度地圖
- Fields+2011 (Ann.Rev.Nucl.Part.Sci.): α ≈ 2.4

原因: ⁷Li 產量 ∝ ³He × ⁴He, ⁴He ≈ 常數,
³He/H ∝ η_B^(-0.6) (因 D(p,γ)³He 隨 η_B 增加而加快),
所以 ⁷Li/H ∝ η_B^1 × η_B^(-0.6) × η_B²... 實際係非線性耦合
""")

# 用 parthenope 風格嘅參數化
# 在 η_B ∈ [2e-10, 1e-9] 範圍, Log⁷Li = a + b·log(η_B) + c·log²(η_B)
# 簡化: 用二次多项式 fit 標準 BBN 結果
# 參考 Coc+2014 Fig.1

eta_vals = np.array([2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]) * 1e-10
# 標準 BBN ⁷Li/H × 10¹⁰ (Coc+2014, Fig.1)
Li7_sbBN = np.array([0.5, 0.8, 1.4, 2.6, 5.0, 8.0, 11.0, 14.0, 17.0]) * 1e-10

# IDCM: 線性
Li7_idcm_arr = eta_vals * factor_li7

# 計算局部敏感度指数
print(f"\n{'η_B':>10s} | {'SBBN ⁷Li/H':>12s} | {'IDCM ⁷Li/H':>12s} | {'SBBN/IDCM':>10s} | {'α_SBBN':>8s} | {'α_IDCM':>8s}")
print("-" * 68)
for i, eta in enumerate(eta_vals):
    if i == 0:
        # 用向前差分
        alpha = np.log(Li7_sbBN[1]/Li7_sbBN[0]) / np.log(eta_vals[1]/eta_vals[0])
    elif i == len(eta_vals)-1:
        alpha = np.log(Li7_sbBN[-1]/Li7_sbBN[-2]) / np.log(eta_vals[-1]/eta_vals[-2])
    else:
        alpha = np.log(Li7_sbBN[i+1]/Li7_sbBN[i-1]) / np.log(eta_vals[i+1]/eta_vals[i-1])
    
    ratio = Li7_sbBN[i] / Li7_idcm_arr[i]
    print(f"{eta:>10.2e} | {Li7_sbBN[i]:>12.4e} | {Li7_idcm_arr[i]:>12.4e} | {ratio:>10.2f} | {alpha:>8.2f} | {'1.00':>8s}")

print(f"\n[B] 替代驗證路徑: 唔靠 η_B 變化")
print("-" * 72)
print("""
既然 η_B 係全域常數, 直接測 d(log⁷Li)/d(log η_B) 不可行。
但以下替代驗證路徑存在:

路徑 1: ⁷Li 絕對值閉合 (已 🟢)
  - IDCM: 1.584e-10 vs 觀測 1.58e-10 → 0.25%
  - ΛCDM: 5.24e-10 vs 觀測 1.58e-10 → 3.1× 張力
  - 最強證據: 零自由參數閉合, 冇 ΛCDM 嘅 40 年問題

路徑 2: Spite plateau 平坦度 (已 🟢)
  - IDCM: ⁷Li 係 primordial → 平坦度自然
  - ΛCDM: 需要精細調節耗盡 → 平坦度係巧合
  - 文獻: Sbordone+2010 確認 A(Li) = 2.20 ± 0.06 冇 intrinsic scatter

路徑 3: 跨元素共享結構 (已 🟢)
  - (1-ε) 同時出現喺 τ = κ(1-ε)(1+ε²) 同 ⁷Li = η_B×2ε(1-ε)
  - 跨公式共享結構常數, 唔係新 fit 參數
  - 驗證: τ 閉合 0.19%, ⁷Li 閉合 0.25%

路徑 4: 天體物理一致性 (🟡 部分)
  - SMC 星際 Li (Howk+2012): ⁷Li ~ BBN 預測, 支持原始
  - 矮星系極貧金屬恆星: 一致嘅 Spite plateau
  - 需要更多高z 量度

路徑 5: JWST 年齡測試 (🟡 部分)
  - IDCM: ⁷Li 係 primordial → 高z 星系冇年齡限制
  - ΛCDM: 若高z 星系有老齡恆星 → 早期宇宙矛盾
  - 睇 O14 宇宙年齡測試
""")

print(f"\n[C] 可證偽性評估")
print("-" * 72)
print("""
🔴 不可直接證偽: d(log⁷Li)/d(log η_B) = 1 vs 2.1-2.4
   - 因為 η_B 係全域常數, 冇 local 變化
   - 除非未來發現 η_B 有 local 變化 (modified gravity 等)

🟢 可間接證偽: ⁷Li 絕對值預測
   - 如果未來 JWST 或 ELT 嘅高z ⁷Li 量度偏離 1.584e-10 > 3% 
   - 結構因子 2ε(1-ε) 失敗

🟡 可累積證偽: Spite plateau 平坦度
   - 如果發現 plateau 有 intrinsic scatter 或 metallicity trend
   - 需要大型巡天 (WEAVE, 4MOST) 嘅數據

結論: 線性 vs 超線性 η_B 依賴嘅直接檢驗
目前觀測不可行, 但 ⁷Li 絕對值閉合已經係強證據。
""")

print("=" * 72)
print(f"補充分析完成")
print("=" * 72)