# O165 — e⁻ⁿ 權重嘅本體: κ 閘極「比較尺」嘅起源 (Origin of the Exponential Visibility Weight)

> **創建日期**: 2026-09-10
> **狀態**: 🟢 **已閉合** (2026-09-10, 4 scripts 38 PASS / 0 FAIL, final_result.md 已建)
> **前置**: O163 (κ = γ_max⁻² = 1/16 已閉合) → O116 (κ 閘極: e⁻² > κ > e⁻³ → 3 可見模式)

## 問題陳述

O163 已證明 κ = γ_max⁻² = 1/16 (88-site Laplacian 最大特徵值平方倒數)。但 κ 嘅「比較尺」仍然開放:

**點解可見性權重係指數衰減 e⁻ⁿ, 而唔係其他衰減 (幂律 n⁻ᵖ, 高斯 e⁻ⁿ², 等等)?**

- O116 定理: 模式 n 可見 ⇔ e⁻ⁿ > κ
- O163: κ = γ_max⁻² = 1/16 → e⁻² > κ > e⁻³ → n = 0,1,2 可見 (3 = N_gen)
- 但「e⁻ⁿ 權重」本身冇推導 — 點解係 e 底指數? 點解係 n 一次冪?

## ✅ 閉合答案

**權重唔係 e⁻ⁿ — 係 K_Tree 層振幅平方 φ⁻²ˡ。e 係 φ² ≈ e (3.69%) 嘅近似標籤。**

| 子問題 | 答案 | 位置 |
|:-------|:-----|:-----|
| e⁻ⁿ 嘅譜來源 | 鏈譜無局部化 (IPR 全延展); 來源係樹層縮放 P = φ⁻¹·I₄₄ → φ⁻²ˡ | docs/02, 04 |
| 玻爾茲曼因子身份? | 幾何 ≡ 玻爾茲曼線性能階 E_ℓ = 2ℓ·lnφ·kT — 樹層 RG 階梯, 非鏈模式 | docs/03 |
| 泊松/量子諧振子身份? | 非 Poisson (λⁿ/n! 超指數), 非 QHO 高斯 (2 可見 FAIL) | docs/03 |
| κ 夾層嘅必然性 | 精確: φ⁻⁴ > κ > φ⁻⁶ ⇔ 3φ+2 < 16 < 8φ+5 (純代數); κ = B⁻² 同源 | docs/02 |
| n=0,1,2 嘅本體 | 可見樹層 {0,1,2} = N_gen = 三面型 — o163 全鏈一致 | docs/04 |

## 判準核對

- 零新常數: ✅ φ⁻¹ 已文檔化 (ktree_structure §5B)
- 結構強逼唯一解: ✅ 樹強逼 r = φ⁻²; 高斯/冪律/退化候選全排除
- 反秘數: ✅ e (超越數) 剔除 — R12 域定理勝利
- 觀察者交叉: ✅ φ ∈ Q(√5)

## 收檔

- scripts/: 01_weight_audit (9/9), 02_phi_weight_derivation (14/14), 03_uniqueness (10/10), 04_chain_eigenvector_check (5/5) = **38 PASS / 0 FAIL**
- docs/: 01_ekappa_label_audit, 02_phi_weight_derivation, 03_uniqueness, 04_ontology_and_handoff
- 交接: o164 (世界=拍子) — 本權重靠層比 φ⁻¹, 與 o164 嘅 μ₀ 絕對尺度正交

## 推導時序索引 (2026-09-10, 嚴格遞增無回溯)

| # | 時間 | 檔案 | 內容 | 驗證 |
|:-:|:-----|:-----|:-----|:----:|
| 1 | 15:17 | scripts/00_exploration.py | φ-權重假設探索: 夾層/近似/唯一性/質量偏移/譜檢查 | 手動確認 |
| 2 | 15:18 | scripts/01_weight_audit.py | e⁻ⁿ 標籤審計 (R12, φ²≈e 混淆源) | 9/9 |
| 3 | 15:18 | scripts/02_phi_weight_derivation.py | φ⁻²ˡ 第一性推導 + 夾層 + 質量修正 | 14/14 |
| 4 | 15:20 | scripts/03_uniqueness.py | 高斯/冪律/幾何三族裁決 + 玻爾茲曼身份 | 10/10 |
| 5 | 15:21 | scripts/04_chain_eigenvector_check.py | Q1 誠實檢查 (IPR 全延展, Green's site 衰減) | 5/5 |
| 6 | 15:22 | docs/01_ekappa_label_audit.md | 文檔 1: 命名≠解釋 審計 | 引用 script 01 |
| 7 | 15:22 | docs/02_phi_weight_derivation.md | 文檔 2: 推導鏈 | 引用 script 02 |
| 8 | 15:23 | docs/03_uniqueness.md | 文檔 3: 唯一性 | 引用 script 03 |
| 9 | 15:23 | docs/04_ontology_and_handoff.md | 文檔 4: 本體 + o164 交接 | 引用 script 04 |
| 10 | 15:24 | 01_problem_record.md | 本記錄 (開題→閉合) | — |
| 11 | 15:24 | SESSION_START.md | 起點更新為閉合 | — |
| 12 | 15:36 | final_result.md | 收檔摘要 | — |
| 13 | 15:46 | scripts/05_audit_independent.py | **審計輪**: 全部數值獨立重算 | **58/58** |
| 14 | 15:47 | docs/05_audit_independent.md | 審計文檔 (數值+時序+污染檢查) | 引用 script 05 |

**審計輪 (14)**: 58 PASS / 0 FAIL — docs/01-04 + final_result 全部數值由原始定義獨立重算確認; 時序嚴格遞增; 跨文檔僅 3 處標記 pointer (o163×2, o116×1), 無新推導污染。

## 待辦 (全部完成 ✅)

- [x] 開題: K_chain 特徵向量譜分析 (IPR 全延展 — 鏈譜無指數; 來源係樹)
- [x] P1: e⁻ⁿ 譜來源 (局部化模?) — 裁決: 樹層縮放, 非鏈譜
- [x] P2: 唯一性 (幂律/高斯 vs 指數) — 樹強逼 φ⁻², 唯一
- [x] P3: 玻爾茲曼/諧振子身份 — 樹層線性階梯, 非鏈模式
- [x] 結構強逼唯一性
