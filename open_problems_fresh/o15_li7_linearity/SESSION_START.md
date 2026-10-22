# O15 新 Session 啟動文件 — ⁷Li 線性檢驗

## 所需 Skills

1. `web-access-protocol` (核心, 文獻)
2. `theoretical-physics-validation` (輔助)

## 前置資料

```
⁷Li/H = 1.584e-10 (0.25% ✅) = η_B × 2ε(1−ε)
|IDCM: ⁷Li/H = η_B × 2ε(1−ε)  →  ∝ η_B (線性)
ΛCDM: ⁷Li/H 標準 BBN 核網絡計算 → 敏感度 α ≈ 2.1–2.4 (超線性, 唔係簡單 η_B²)
ε = φ⁻¹/4
```

⚠️ **重要釐清 (2026-08-20):** 「ΛCDM: η_B²」只係粗略近似。標準 BBN 嘅 ⁷Li 敏感度指數 α = d(log Y_Li)/d(log η_B) 隨 η_B 變化 (1.2→3.3→1.8)，唔係固定 2。IDCM 真正嘅強證據係 **絕對值閉合 (0.25%)**，唔係 η_B 幂律。直接 η_B 斜率檢驗不可行，因為 η_B 係全域常數。

## 啟動 Prompt

```
開 O15 ⁷Li 線性專案: /home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o15_li7_linearity/

任務: 檢驗 ⁷Li ∝ η_B 線性預測 (vs ΛCDM 超線性 η_B^α, α≈2.1-2.4)

背景: IDCM ⁷Li = η_B × 2ε(1−ε) 閉合 (0.25%)
關鍵分辨: 線性 vs 超線性依賴 — 但 η_B 係全域常數
真正強證據: 絕對值閉合 1.584e-10 (0.25%)

步驟:
1. 文獻: η_B 敏感度指數 α 嘅標準 BBN 值
2. 直接斜率檢驗可行性評估
3. 替代驗證路徑 (絕對值閉合, Spite plateau, 共享結構)
4. 2ε 兩步管道微觀機制推導

載入 skills: web-access-protocol, theoretical-physics-validation
誠實: 如果直接斜率檢驗不可行 → 列替代路徑
最後: 更新 01_problem_record + README
```

## 常見坑

1. ⁷Li 觀測好少 — 大部分係 Spite plateau 恆星
2. 高z DLA ⁷Li 幾乎冇 — 樣本極少
3. 線性 vs 二次: 需要 η_B 範圍夠闊先分辨到 — 但 η_B 係全域常數
4. 恆星耗盡效應可能污染 — 要小心
5. 「ΛCDM: η_B²」只係粗略近似 — 實際敏感度指數 α ≈ 2.1-2.4 並隨 η_B 變化
