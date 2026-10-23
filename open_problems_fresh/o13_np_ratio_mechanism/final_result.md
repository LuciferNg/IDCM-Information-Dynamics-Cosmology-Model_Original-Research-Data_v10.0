# O13 — n/p 比 γ₇/γ₂₀ 機制

## 狀態: 🟢 已閉合 (2026-08-20) — 3/3 子問題全部推導，零自由參數

## 結論
n/p = γ₇/γ₂₀ = 0.142618 (0.17%) 係結構常數比，唔係 freeze-out/freeze-in 動力學產物：u quark 投影到 K_Chain 模式 n=20 (B×F₅)，d quark 投影到 n=7 (L₄=φ⁴+φ⁻⁴)，重子耦合 = 三個夸克 γₙ 乘積，K_Tree 層級約化消去 → n(udd)/p(uud) = γ₇/γ₂₀。

## 關鍵公式
- n/p = γ₇/γ₂₀ = 4sin²(7π/88)/4sin²(20π/88) = 0.142618 (≈1/7, 0.17%)
- Y_p = 2(n/p)/(1+n/p) = 0.2496 (1.77%)
- 7 = L₄ = φ⁴+φ⁻⁴ = N_gen + B (DM 模式)
- 20 = B×F₅ = 4×5 = M−F₇ (重子模式)
- 7+20 = 27 = 3³ = N_gen³ (isospin 雙重態)
- ³He/D = φ⁻² = 0.381966 (0.008%)
- ³He/H = φ⁻² × D/H = 9.759×10⁻⁶ (O12 吻合)

## 驗證結果

| 步驟 | Script | PASS | 核心發現 |
|:-----|:------:|:----:|:---------|
| 結構推導 | 01 | 14/14 | 7=L₄, 20=B×F₅, 27=3³, Z₂ 對偶保持差 13=F₇, (7,20) 唯一 |
| 完整閉合 | 02 | 20/20 | 3/3 子問題: 投影機制 / DM 選擇 / ³He/D 預測 |
| 獨立核對 | — | 28/28 | 全文檔公式/數值一致，零矛盾 |

## 依賴
bbn (06_complete_record, n/p 發現) → O13 (機制閉合) → O33 (投影機制), O12 (³He/H 印證)

## 時序
T0 (問題建立) → T1 (結構推導) → T2 (01 驗證 14/14) → T3 (完整閉合 3/3) → T4 (02 驗證 20/20) → T5 (README) → T6 (problem_record 更新) → T7 (SESSION_START 完成) → T8 (獨立核對 28/28)

<!-- conclusion-history:start -->
## 迭代史（machine-generated from register.conclusion；append-only）

| concl_hash | 日期 | verdict | 結論摘要 | 支撐 | 取代 |
|---|---|---|---|---|---|
| `a6607bc554c28f76` | 2026-10-24 | — | n/p = γ₇/γ₂₀ = 0.142618 (0.17%) 係結構常數比，唔係 freeze-out/freeze-in 動力學產物：u quark 投影到 KChain 模式 n=20 (B×F₅)，d quark 投影到 n=7 … | open_problems_fresh/o13_np_ratio_mechanism/final_result.md | — |
<!-- conclusion-history:end -->
