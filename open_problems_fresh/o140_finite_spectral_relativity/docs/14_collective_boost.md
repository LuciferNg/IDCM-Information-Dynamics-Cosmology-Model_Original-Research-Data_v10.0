# 14 — velocity-composition collective sector 攻破（2026-10-09）

**狀態**: scripts/16_collective_boost.py — **7/7 PASS**
**數據**: data/collective_boost.json
**目標**: register 剩餘「⊕_FSR collective sector 算符」— 多粒子態嘅 boost 結構

---

## 結論：collective sector 封閉——boost = 張量積，物理空間 = 快度 ℝ

### 1. Boost generator 可加性

- U_i(η) 作用喺唔同粒子 Hilbert 空間 ⟹ [U_1(η₁), U_2(η₂)] = 0
- U_total(η) = ⊗ U_i(η)（張量積）⟹ 群性質自動繼承，collective boost 無額外路徑依賴

### 2. Collective 4-動量 = 線性相加（同 SR）

- 單粒子：E_n = m·csc(πn/88)，p_n = m·cot(...)·cos，E²−p² = m² 精確（全 n 驗證）
- 同速度粒子 pair：(1,1), (7,7), (20,20) 全部 M² = 4 = (2m)²——不變質量可加
- 不同速度 pair：(1,7) M² = 9.178——不變質量由質心能定義（同 SR 一樣）
- 足球問題（06 W1b）確認：p_total = 1e23 × p_max 線性相加，無單粒子階梯封閉要求

### 3. 剩爭議解決：rung 空間 vs 快度空間

- rung 係 R^44 離散子集，boost 唔保持 rung ⟹ collective sector 冇閉合嘅離散對稱群
- **collective 可觀測 = 快度（連續 ℝ），唔係 rung（離散）**
- rung 只係「測量顯示」，物理空間係快度 ℝ——同量子力學測量公理一致（Zeno 已證）

### 4. 三粒子 associativity 數值確認

| 組合 | 一次過 vs 連續 | 偏差 |
|:-----|:-------------|:-----|
| (1,7,20) | E = 10.6962634898 相同 | 2.3e-12 |
| (3,11,22) | 相同 | 2.7e-13 |
| (7,20,33) | 相同 | 2.2e-15 |

快度 ℝ 加法喺多粒子層面精確成立（無中間投影時）。

---

## 判定

- **O140/velocity-composition: 🟢 完全封閉**（單粒子 ⊕_FSR + collective 張量積）
- 剩爭議清除：rung 係測量顯示，快度係物理空間
- 同 09（Zeno）、07（no-go + ⊕_FSR）一致閉合