# O129 — SYNC 轉折點 σ_sync

## 狀態: 🟡 交回重驗完成 (σ_sync = 算子, 非 dip 位置; dip 🔴 撤回; 算子歸屬 O100/O133/O128)

## 結論
O129 之 σ_sync 係 v9.0 **諧波尺度變異數算子** `σ_sync²(R_n) = ∫ ξ(s)·W(s;R_n) ds` at `R_n = λ_sync/(2n)`
（寬度／振幅量, 取代 σ₈），**唔係** sync dip **位置**；dip 位置 `z_c = F₄/F₅ = 0.6` 屬另一 v9.0 物件，
已由 O126 §D 撤回（本 O 獨立重驗 5/5 確認）。σ_sync 算子之幾何（λ_sync）喺 v9.0 ≡ v10.0，
但 v9.0 形式係**純數據測量**（BOSS ξ(s)），無第一性原理內容；其 v10.0-native 歸屬 = O100/O133/O128。
前置 O118 由 🔴 → 🟢 前提作廢。

## 關鍵公式
- σ_sync 定義：`σ_sync²(R_n) = ∫ ξ(s)·W(s;R_n) ds`，`R_n = λ_sync/(2n)`（on-ladder 變異數）
- 幾何：`λ_sync = 2πR_H/88 = πR_world/44 = 294.877 Mpc`（v9.0 ≡ v10.0，dev = 0）
- dip 位置（🔴 撤回）：`z_c = F₄/F₅ = 3/5 = 0.6`；φ⁻¹ = 0.618034（gap 1.8034% / 相對 3.0057%）
- z 離散階（O76）：`1+z = 4^ℓ`，rungs z = {0, 3, 15, 63}；`ℓ(0.6) = 0.339036`（非整數）
- Ω_Λ 常數（O215/O39）：`Ω_Λ = (N_d−B+1)/(N_d+B²) = 61.5/90 = 41/60` EXACT
- σ₈ 尺度錯配：8 h⁻¹Mpc = 11.021 Mpc ⟹ ladder 級 n = 13.378（非整數）
- O118 前提作廢：`χ² 18.092/7 (2.585) → 1.7154/7 (0.2451)`

## 依賴
O76 (z 離散階) → O215/O39 (Ω_Λ = 41/60) → O118 (前提作廢, 🟢) → O126 (交回) → O129
O129 → O100 / O133 / O128（σ_sync 算子歸屬, 已有主）; O99 docs/11（σ₈ 純首推 🔴 sub-grid）

## 密度基準
- N_search = 1（性質判定 = 結構分類：σ_sync 定義係算子 `σ_sync²(R_n)=∫ξW ds`，唯一；無擬合自由度）
- 數值全部重算：BOSS DR12 重算 σ_sync 對 v9.0 表 max dev 0.040%；O118 χ² 由零複現
- MC null: 唔適用（分類/複現任務，無新常數掃描）
- 驗證統計: `scripts/01` = 8/8 PASS + 7 CLAIM; `scripts/02` = 18/18 PASS + 4 CLAIM ⟹ **26/26 PASS**

## 交回重驗 (O126 §D, 2026-09-27)
| # | 要求 | 結果 |
|:-:|:-----|:-----|
| ① | σ_sync = dip 位置 抑或 轉折寬度/其他量 | ✅ σ_sync = **變異數算子（寬度）**, 唔係位置 |
| ② | 逐項獨立檢驗 O126 §D 五點 | ✅ 5/5 確認（由零重算, 唔 import O126/O118） |
| ③ | v10.0 對應結構量 | ✅ 歸屬 O100/O133/O128（σ8=0.7482）; 無獨立新缺口 |
| ④ | 更新前置 O118 🔴 → 🟢 | ✅ 已更新 |

## 待裁定
O129 目錄之處置（保留作歷史記錄 / 合併入 O128）待調律者明示 — 本 session 未作合併動作。

<!-- conclusion-history:start -->
## 迭代史（machine-generated from register.conclusion；append-only）

| concl_hash | 日期 | verdict | 結論摘要 | 支撐 | 取代 |
|---|---|---|---|---|---|
| `0e8ee4accf630351` | 2026-10-24 | partial | O129 之 σsync 係 v9.0 諧波尺度變異數算子 σsync²(Rn) = ∫ ξ(s)·W(s;Rn) ds at Rn = λsync/(2n) （寬度／振幅量, 取代 σ₈），唔係 sync dip 位置；dip 位置 z… | open_problems_fresh/o129_sigma_sync_transition/final_result.md | — |
<!-- conclusion-history:end -->
