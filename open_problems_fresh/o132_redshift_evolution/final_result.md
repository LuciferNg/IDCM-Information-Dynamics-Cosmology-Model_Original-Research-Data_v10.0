# O132 — 紅移演化推導 (v9.0→v10.0 遷移)

## 狀態: 🟡 前置驗證完成 (判決 = 骨架遷移 / 頭條結果失效 / 原命題未實現; 目錄處置待調律者裁定)

## 結論
v9.0 `redshift_evolution/01_derive_evolution.py`（180 行，唯一檔案）之前置驗證完成：
**骨架層遷移**（`λ_sync` 幾何、諧波階梯 `s_n = λ_sync/n`、h⁻¹Mpc 慣例 — 公式恆等，dev=0），
**頭條結果全失效**（`A(z) ∝ (1+z)^α_evol` 嘅 α_evol = **15.530** 係**巡天振幅偽影**，唔係紅移演化；
「effective branching factor changes with redshift」同 v10.0 `B = L₃ = 4` 常數矛盾；
`ζ(z)`/`H₀=72.59` 已 demote/誤標）。
忠實重跑（只改數據路徑）**複現** v9.0 全部輸出（含 α_evol = 15.530）；
null 檢定：交換巡天 z 指派 ⟹ α → **−15.530**（|α| 不變）⟹ α 由「邊個巡天殘餘大」決定，非紅移量度。
跨 O 審計：v9.0 物件 ①-⑧ 全部已有 v10.0 現行擁有者（O31 🟢 / O76 / O73 / O129 / O130 / O133 / O135），
剩餘新 IDCM 結構內容 = **空集**（唯一無主項 ⑨ = 偽影，非推導）。
⟹ 原命題「紅移演化推導在 v10.0 非膨脹框架中的重新驗證」**未實現**。

## 關鍵公式 / 判決
- ✅ 遷移: `λ_sync = 2πR_H/88 ≡ πR_world/44 = 294.877 Mpc`（同輸入 dev = 0 EXACT）；`s_n = λ_sync/n`（擁有 = O31 🟢）；`h = 0.7259 = ω_ring/100`（慣例）
- 🔴 頭條: `A(z) ∝ (1+z)^α_evol`，`α_evol = 15.530`（v9.0 自印 `(1+z)^15.530`）— ΛCDM 增長指數應 ~ −1 至 −2 ⟹ 符號+量級全錯
- 🔴 偽影證據: `A_eBOSS/A_BOSS = 25.50` ≫ 原始 `ξ(10)` 振幅比 `5.05`；broadband 常數 C：BOSS −0.0243 vs eBOSS +0.5232
- 🔴 null: 交換 z 指派 ⟹ `α = −15.530`（|α| 不變）
- 🔴 矛盾: v10.0 `B = L₃ = 4` **常數**（O135/O51）vs v9.0「branching factor changes with z」
- 🔴 解析度: `Δs_n = λ_sync/[n(n+1)]`，BOSS bin 5 h⁻¹Mpc ⟹ 只 n ≤ 8 解析；v9.0 用 n=4..20 其中 12 個 sub-bin aliasing（同 O130 n_max = 8.53）

## 依賴
O73/O171 (ω_ring/R_world) → O31 (λ_sync 諧波階梯, 🟢) → **O132**
旁證: O76 (離散 z `1+z=4^ℓ`) · O129 (σ_sync) · O130 (解析度/方法依賴) · O133 (v9 P(k) 失效) · O135 (B=L₃ 常數、H₀ 誤標) · O213 (無演化方程) · O117 (D_H 🔴) · O118 (唔搬遷 SYNC 系列)

## 密度基準
- N_search = 1（純對照 + null 檢定任務：v9 物件對 v10 權威值逐項比對，無擬合自由度）
- N_mc = 唔適用（無新常數掃描；α_evol 由單一 z 對算出 = 1 dof）
- d_obs = 0（骨架層公式恆等 dev = 0 EXACT）
- q_obs = 唔適用（分類 + 偽影診斷任務）

## 驗證統計
- `scripts/01_v9_rerun_inventory.py` = **14/14 PASS**（忠實重跑 + 解析度新發現）
- `scripts/02_crosscheck_v9_v10.py` = **18/18 PASS** + 1 CLAIM（幾何恆等 + 偽影 null + 框架掃描）
- `scripts/03_cross_o_coverage.py` = **28/28 PASS**（跨 O 覆蓋）
- ⟹ **60/60 PASS + 2 CLAIM**

## 交付物
- `scripts/01_v9_rerun_inventory.py` · `02_crosscheck_v9_v10.py` · `03_cross_o_coverage.py`
- `docs/02_migration_verdict.md`（P/R/A/X 判決全文）· `docs/03_cross_o_coverage.md`
- `data/`（v9 原始碼 `.orig` + BOSS/eBOSS 數據 + 3 個 stdout/JSON）
