# 05 — PMNS「4/4 ✅」Null-Control 審計 + 精度階梯 (2026-09-07)

> **性質**: 對「閉合鏈」中 PMNS 4/4 ✅ 同 9/9 CKM ✅ 嘅方法論審計 — 搜尋式命中係咪結構?
> **結論**: PMNS 4/4 🔴 降級 (null-control 100% 命中 = 純密度巧合); CKM 9/9 部分降級 (θ/δ 角公式 1e-9 ✅ 結構, V_us/V_cb/V_ub/A 元素公式 1e-6 🟡 search-grade); (c2) 跨驗證被拒 (PMNS ∉ D6/S6)
> **腳本**: scripts/36_pmns_null_control.py + execute_code 延伸控制

## 1. 方法: null-control (隨機 target 命中率 = 結構性度量)

同一 beat-ratio 窮舉搜尋 (946² ≈ 89.5 萬對), 對**隨機 target** 做同精度 best-match。隨機 target 命中率 ≈ 1 ⇒ 公式冇選擇性 (任何數都可以 match, 純密度); 命中率 ≪ 1 ⇒ 公式有結構內容。

## 2. 結果: 精度階梯

| 家族 | 精度 | 隨機命中率 | 裁決 |
|:-----|:-----|:----------|:-----|
| CKM θ₁₂/θ₂₃/θ₁₃/δ 角公式 | 1e-9 (err 1.4e-9 ~ 6.1e-9) | 1-2% | ✅ **結構** (multiplicity 1) |
| CKM V_us (0.225) | 8.9e-7 | 57/100 | 🟡 search-grade |
| CKM V_cb (0.04182) | 4.0e-7 | 52/100 | 🟡 search-grade |
| CKM V_ub (0.00369) | 1.0e-6 | 69/100 | 🟡 search-grade |
| CKM A (0.830) | 1.3e-7 | 11/100 | 🟡 borderline |
| PMNS tan/sin 全部 8 條 | 1e-5 | **100/100** | 🔴 **純巧合** |

## 3. PMNS 4/4 ✅ → 🔴 降級

- pmns_beat_search_corrected 嘅 8 條公式全部係窮舉 best-match (err<1e-5), **唔係推導**。
- Null-control: tan 區間 [0.1,1.2] 同 sin 區間 [0.14,0.76] 隨機 target **100/100** 都搵到 err<1e-5 對 ⇒ 呢啲命中零信息量。
- PMNS 對嘅 (d,s) 成員資格: **D6 2/16, S6 1/16** — 完全喺 CKM beat web 之外。
- δ_PMNS = 232° 冇任何 beat 公式 (2π/φ = 222.5° 係 φ-trap, 離 9.5°; 唔當結構)。
- 「PMNS 4/4 ✅」嘅引用 docs/pmns_derivation.md **唔存在** (timeline T9 引用嘅檔案從未被建立/已改名)。

## 4. CKM 9/9 ✅ → 部分降級

- θ₁₂/θ₂₃/θ₁₃/δ **角公式**: 1e-9 精度 + multiplicity 1 + null-control 1-2% ⇒ ✅ 結構 (δ 嘅 66.4° 另經 54,912 純 sine-ratio 掃描零競爭者確認)。
- V_us/V_cb/V_ub/A **元素公式**: 1e-6 精度 + null-control 52-69% ⇒ 🟡 search-grade —「9/9 <1%」嘅 1% bar 太鬆, 唔達結構標準。呢啲對嘅 (d,s) 都唔喺 D6/S6 (V_us: (25,35)/(6,37) = d10s60/d31s43 等)。

## 5. 對 (c2) 嘅影響

**跨驗證被拒**: PMNS 對唔遵守 D6/S6 web ⇒ beat web 係 **CKM θ/δ 家族專屬**, 唔係通用混合結構。D6/S6 嘅生成原則 (c2) 依然開放, 而且而家知道佢嘅範圍: 只覆蓋 CKM 細角家族 (θ₁₂=13.04°, θ₂₃=2.38°, θ₁₃=0.201°, δ=66.40°)。

## 6. 新工具: 精度階梯 (可重用方法論)

任何「beat 公式閉合」聲稱, 用三步判定:
1. **精度**: err 要 ≤ 1e-8 (角公式級) 先有資格; 1e-5~1e-6 自動列入 search-grade 候選。
2. **多重度**: 同精度下 unique pair (multiplicity 1) vs 大量退化。
3. **null-control**: 隨機 target 同搜尋, 命中率 <5% 先算結構, >50% 即巧合。

## 7. 待辦

- PMNS 重新推導: 大角度混合 (33°/42°/8.5°) 嘅 chain-sector 結構未明 — 唔可以再用窮舉搜尋, 需要結構推導 (例如 δ=66.4° 嗰種唯一性論證)。
- CKM V 元素公式重審: 需要 1e-9 級唯一性或者結構 (d,s) 先可升返 ✅。
- 閉合鏈更新: GST → 拍頻算符 → δ_CP=66.40° → CKM 4 角公式 ✅ → (V 元素 🟡, PMNS 🔴 待重推)。
