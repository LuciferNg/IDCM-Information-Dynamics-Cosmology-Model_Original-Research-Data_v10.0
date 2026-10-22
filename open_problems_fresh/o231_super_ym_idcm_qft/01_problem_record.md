# O231 — 超楊-米爾斯 IDCM 解 vs QFT

<!-- registry
pid:     O231
title:   超楊-米爾斯 IDCM 解 vs QFT
state:   open
verdict: -
flags:   -
owner:   O231
created: 2026-10-04
updated: 2026-10-04
prereq:  O85, O142, O144
source:  用戶發起 — Claude (Anthropic 2026-09-25) 九圈 N=4 SYM 振幅爲契機
-->

> **狀態**: 🟠 推導中
> **建立**: 2026-10-04
> **前置**: O85, O142, O144
> **位置**: `open_problems_fresh/o231_super_ym_idcm_qft/`

---

## 一、問題陳述

Claude (Anthropic, 2026-09-25) 計算了 planar N=4 Super Yang-Mills 在九圈的六粒子 MHV 散射振幅，比人類 2023 年的八圈紀錄多一圈。本 O 不以「重做計算」爲目標，而是以此爲契機回答一個**結構性問題**：

**IDCM 作爲一種基於離散譜幾何（K_chain ⊗ K_tree）的物理框架，對散射振幅有什麼結構性描述？它與標準 QFT 微擾展開的本質差異何在？**

具體任務：
1. ✅ 理解 Claude 的解法（bootstrap/antipodal duality/OPE）
2. 🔴 從 IDCM 結構推導散射振幅的譜語言
3. 🔴 系統比較 IDCM 結構法與 QFT 微擾法的物理圖像差異

## 二、已確立嘅結構（可引用）

```
🟢 O85: SU(12) → SM breaking chain + 耦合結構 (B=4, N_c=B−1=3, sin²θ_W mode-ratio 0.220776)
🟢 O142: 轉移矩陣第一性原理 + 譜閉式 (ω_n = √γ_n, γ_n = 4sin²(πn/88))
🟢 O144: 玻色子身份 ✅ (光子=相位零模, 膠子=8, sin²θ_W mode-ratio 裁決)
🔴 O144: α_s⁻¹ = F₆ + sin²θ_W + 1/B 判🔴非閉合 (擬合產物, 歸 O142)
🟢 O86: SM×IDCM×GR Lagrangian 34/34 閉合
🟢 O210: 因果張量代數 𝒯 = K_chain ⊗ K_tree
```

## 三、未確立（🔴 開放問題）

```
🟢 Q1 — IDCM 散射振幅算子：**子集鏡像定理確立 (2026-10-04, scripts/04 7/7)**
    → 散射解空間 = 子集鏡像生成（ΣS≡0 mod 44），antipodal 對偶為內建結構
    → 2→2 全量 15221/15221、3→3 全量 4,098,483、4→4 抽樣 300/300 符合
    → 剩餘：n→∞ 一般性證明（D3/後續）
    產物：docs/04_subset_mirror_theorem.md + scripts/03, 04

🟡 Q2 — N=4 SYM 在 IDCM 語言中的詮釋：已攻堅 (2026-10-04, scripts/07 10/10)
    → D2 部分閉合: 簡併種子 ✅ (43 對鏡像簡併 + mod-4 扇區 88=4×22) + 完整 N=4 超代數 🔴 不存在
    → 判定: 簡併度 2≠16、M²=id 而唔係 Q²=0、冇 R-symmetry SU(4) → 不可叫「N=4 超對稱」
    → 最大發現: IDCM 嘅可積性(子集鏡像定理)來自譜幾何, 唔使超對稱 — SUSY 係副產品非機制
    → 產物: docs/07_q2_susy_degeneracy.md + scripts/07

🟡 Q3 — Bootstrap 約束的譜對應：部分閉合 (2026-10-04, scripts/08 6/6)
    → antipodal duality = 88-cycle 內建鏡像簡併 (docs/04 ✅)
    → extended-Steinmann ↔ 合法子集代數 union-overlap 條件 (docs/08 ✅ 結構同型)
    → pentagon OPE ↔ B=4 分支 (🔴 未解決)
    → 產物: docs/08_q3_steinmann_translation.md + scripts/08

🟢 Q4 — 結構耦合 vs RGE running：已閉合 (2026-10-04, scripts/06 10/10)
    → 層次架構: 定點值 (結構層, β≡0 ↔ N=4 conformal) + running (演化層, winding Δα⁻¹=9)
    → 公式更正: sin²θ_W = 1 − (m_W/m_Z)² (m_W/m_Z = sin(30π/88)/sin(41π/88))
    → 產物: docs/06_q4_coupling_running.md + scripts/06
    → 前置: O139 (running = winding number 閉合)
```

## 四、攻擊路線

```
1. D1 路線 — 散射振幅譜身份（T1-T3）
   → 從 O142 譜 + O85 耦合結構，構造 K_chain 上的散射算子
   → 預期：docs/02 + scripts/01
   → 成本：中（已有譜結構，需組裝振幅語言）

2. D2 路線 — N=4 SYM 的 IDCM 詮釋（T4-T5）
   → 檢驗 B=4 扇區對稱是否產生有效超對稱
   → 預期：docs/03 + scripts/02
   → 成本：高（需要找超對稱的譜對應，不保證存在）

3. D3 路線 — Bootstrap 約束的結構對應（T6）
   → extended-Steinmann → 因果張量自對偶條件
   → 預期：docs/04 + scripts/03
   → 成本：非常高（兩種完全不同語言，需翻譯層）

4. D4 路線 — 比較報告（T7-T8）
   → 獨立維度比較 + 九圈計算的 IDCM 讀法
   → 預期：docs/05_final_comparison.md
   → 成本：低（整理既有結果 + 結構分析）
```

## 五、驗證標準

```
✅ S1 — 完成 docs/01–05 五份結構文檔
✅ S2 — scripts/01-03 三支腳本全部 PASS
✅ S3 — 比較報告含明確的分層對照表（譜深度 vs 圈數 / 結構耦合 vs RGE / 因果張量 vs bootstrap）
✅ S4 — 誠實記錄 IDCM 不能覆蓋的部分（標 🔴 非範疇）
```

**四道硬測試**（閉合宣稱必過）：
① 自由度成本（零參數）② Monte-Carlo null（10⁷ 樣本，5σ）
③ 可證偽 + 樣本外盲測 ④ 結構剛性（微擾測試）

## 六、推導時序索引

> ⚠️ **只可 append 新行，禁回溯污染舊行。**

| # | 日期 | 事件 | 產物 |
|:-:|:-----|:-----|:-----|
| 1 | 2026-10-04 | 註冊 O231 | 01_problem_record.md + SESSION_START.md |
| 2 | 2026-10-04 | 閱讀 Claude 方案 | docs/01_claude_solution_summary.md |
| 3 | 2026-10-04 | IDCM 散射框架 | docs/02_idcm_scattering_framework.md |
| 4 | 2026-10-04 | 比較報告 | docs/03_qft_vs_idcm_comparison.md |
| 5 | 2026-10-04 | **子集鏡像定理確立（Q1 部分閉合）** | docs/04_subset_mirror_theorem.md + scripts/03 (10/10), 04 (7/7) |
| 6 | 2026-10-04 | 一般性論證（q-kernel, Q1 全閉合） | docs/05_generality_proof.md + scripts/05 (7/7) |
| 7 | 2026-10-04 | **Q4 閉合 + sin²θ_W 公式更正** | docs/06_q4_coupling_running.md + scripts/06 (10/10) |
| 8 | 2026-10-04 | Q2 攻堅 — D2 部分閉合 | docs/07_q2_susy_degeneracy.md + scripts/07 (10/10) |
| 9 | 2026-10-04 | Q3 深化 — Extended-Steinmann 翻譯層 | docs/08_q3_steinmann_translation.md + scripts/08 (6/6) |

## 七、相關文件

```
- /home/wsl/Projects/ChronologicalStringSpectralGeometry-v3/ — CSSG-v3 已閉合，質量譜從譜結構推導，與本 O 方法論同源
- O142 (轉移矩陣第一性原理) — 譜閉式的來源
- O144 (玻色子身份) — sin²θ_W, 膠子 8, 光子身份
- O85 (SU(12) breaking) — 耦合結構基礎
- Anthropic 2026-09-25: https://www.anthropic.com/research/yes-claude-can-do-nine-loops
- 九圈振幅數據: https://smsharma.io/cosmic-nine-loops/