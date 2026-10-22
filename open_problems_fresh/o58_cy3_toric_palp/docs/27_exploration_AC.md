# O58 — 探索 AC：e-position Lucas 傾向係排序偏好，唔係 (36,98) 結構

> **狀態**: 🟢 完成（2026-08-24）
> **🔴 撤回 AA 嘅「(36,98) 特殊 Lucas 結構」claim**

---

## 問題

AA 發現 (36,98) e₁-e₄ 位置 55.6% 係 Lucas（z=10.45σ vs 均勻 16.4%）。係咪 (36,98) 特殊？

## 答案：唔係 — 係 HF 數據庫普遍嘅「細數字優先」排序偏好

### Control 家族（h11=35, 37, 40）掃描

| 家族 | excl e₁ Lucas 率 |
|:---|:---|
| h11=35 | 42%（8/19）|
| h11=37 | 36%（8/22）|
| h11=40 | **59%（13/22）**|
| control pooled | **46%（29/63）**|
| (36,98) | 55.6%（50/90）|

### 統計

```
z((36,98) vs control) = 1.82 — 冇顯著性！
```

### Control e-positions 分佈（excl e₁）

- **細數字主導：3（16）、4（11）、5（10）** — pts ordering 偏好細數字
- 2,3,4,5,7 係 Lucas 且係細數字 → Lucas 率高係自然結果
- 高 pts（28-55）出現率低

### 核心教訓

**AA 用嘅 baseline（9/55 均勻分佈 = 16.4%）錯咗！** 真正 baseline 應該係「細數字優先」分佈（46%）。當用正確 control 對比，z 跌到 1.82 — 冇顯著性。

### 🔴 撤回

- **AA「e₁-e₄ 位置傾向 Lucas 係 (36,98) 真結構」→ 撤回**
- 正確理解：e-positions 傾向細數字（pts ordering 偏好），細數字好多係 Lucas → Lucas 率高係普遍現象
- (36,98) 55.6% 同 h11=40 嘅 59% 冇分別

### 保留

- Canonical e₁-e₄ = {1,3,7,47} 全 Lucas 仍然成立（但係 polytope 排序嘅極端例子，唔係結構）

## 檔案

```
scripts/70_e_positions_control.py
data/e_positions_control_families.json
```
