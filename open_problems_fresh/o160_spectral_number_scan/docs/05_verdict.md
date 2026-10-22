# O160 docs/05 — 最終誠實清單 (Verdict)

> 2026-09-08 | R1-R6 全答

## R 對應

| R# | 問題 | 答案 | 位置 |
|:---|:-----|:-----|:-----|
| R1 | 工具註冊 | ✅ 4 套工具 → skill + tools/ registry + CLI, 16/16 + integration 全 PASS | docs/01 |
| R2 | 不變量族設計 | ✅ 13 族 (純鏈 3 + 鏈×樹 4 + FULL 4 + SUM 2), 恆等 2 條 | docs/00 |
| R3 | 排除法命中集 | ✅ 255,552 格 → 15 distinct 精確命中 + 7 novel | docs/02 |
| R4 | 新交叉身份 | ✅ **λ₁₇ = μ² = 2** (樹 F_proj mode = 自對偶) — 新結構事實 | docs/03 |
| R5 | null-control | ✅ 精確命中全顯著 (p≤0.005); obs 1/222 過關 | docs/04 |
| R6 | 最終連結清單 | ✅ 244 rows inventory (15 🟢 + 1 🟢 obs + 7 🔮 + 221 ⚠️) | data/link_inventory.* |

## 閉合 (🟢)

1. **★ λ₁₇ = 2 = μ² EXACT** — K_Tree Dirichlet 譜第 F_proj (=17) 個 mode = 自對偶值 (17π/68 = π/4)。樹側嘅「INDEX 中心 = ENERGY 特殊值」重合點, 平行於鏈側 γ₄₄ = 2 (44 = N_d/2)。
2. **15 個 web 閉合連結** — 全部 mpmath 50dps 驗證, 全部由 λ₁₇ + 錨點算術生成。
3. **m_W/m_Z O88(21,24) 唯一結構連結** — 全空間唯一, null p≈2e-4, = 已知 O158 張力解 (0.04σ)。

## 候選 (🟡)

- 422 trap targets (1e-5~1e-3 窗) — 全數 R12 φ-trap, 唔閉合
- novel 值 10 = 2F₅ (SUM_plus(88,88,17)) — 冇閉合身份, 🔮 待解釋

## 誠實清單 (🔴/開放)

1. **λ₁₇ = μ² 嘅「意思」未推導**: 點解樹嘅 F_proj mode 係 π/4? (17 = F_proj = L₆−1 有身份, 但 π/4 = 17π/68 嘅機制 — 68 = 2(K_tree+1) = 4×17 ⇒ 17/68 = 1/4 先係源頭 — 呢個係算術必然: c = 68/4 = 17 即樹譜嘅四分之一點。真正問題: 點解 1/4 (即 B⁻¹) 點係特殊?) — 承接 O157「λ 譜內建身份」開放面
2. **ΣΓ 5940 嘅單格分解未掃**: 今次掃描只做 ratio/sum/beat contraction, 未做 Γ = γ⊗λ 全格乘積嘅逐格身份掃描 (ΣΓ = 5940 係總跡)
3. **μ-ladder (φ 譜) 未入掃描** — R12 域分離 (λ ∈ Q(ζ₆₈)⁺, μ ∈ Q(√5)) 係分開層, 唔可以混入同一掃描
4. **44-chain 次框架只做對照** — FULL 家族喺 44 鏈冇跑 (維度唔夠 45-家族結構)
5. **obs 密度清洗方法**: 均勻密度解析估計低估 γ-比密集區背景 — 保守規則 (count≥3 或 ratio<100× 一律唔宣稱) 已應用

## 驗證統計

- scripts/01: 16/16 + integration 9/9
- scripts/02: web 68 targets + 22 obs
- scripts/03: 1.6M 格值掃描
- scripts/04: 21/21 (mpmath 50dps)
- scripts/05: MC 200 trials/family
- scripts/06: 244 rows

## 命名

- λ₁₇ = **樹自對偶模** (Tree Self-Dual Mode) — 樹譜第 F_proj 個 mode = μ², 建議入 O75 命名規範候選
- 新數字 10 = 2F₅ — 未有命名, 保持 🔮

## 依賴鏈

O155 (λ 譜, 補對和) → O157 (KTreeSpectralGeometry 平台) → O152 (operator dictionary → constant web) → O158 ((21,24) 張力解) → **O160 (全掃描)** → 開放面 → O157/O161+
