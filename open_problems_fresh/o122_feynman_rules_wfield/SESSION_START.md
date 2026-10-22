# O122 — Feynman 規則從 W-field 晶格推導

> **Session**: 2026-09-03 (閉合 session — 由 2026-08-29 建立, v9.0 遷移)
> **狀態**: 🟢 **已閉合 — 47/47 PASS** (2026-09-03)
> **來源**: v9.0 項目審計後發現不屬於 v10.0 O1-O114 任何現有系列
> **v10.0 位置**: `IDCM-v10.0--It-From-Beat/open_problems_fresh/o122_feynman_rules_wfield/`
> **v9.0 來源**: `open_problems_fresh/p_fr_feynman_rules/`

## 問題

見 `docs/01_problem_record.md`

## 前置驗證：v9.0 推導先行驗證 ✅

⚠️ 已完成 — **v9.0 推導在 v10.0 中失效，需要重建 (非遷移)。**

1. ✅ 讀取 `open_problems_fresh/p_fr_feynman_rules/` 原始推導 (docs/02 §一)
2. ✅ 識別依賴膨脹宇宙假設的部分 (docs/02 §二): 連續極限 N_d→∞, GeV 標度 (123.11 GeV, V_EW), a = 1/M_GUT, 單一 scalar φ⁴
3. ✅ 在 v10.0 非膨脹框架中重新驗證每個公式 (docs/02 §二): 4 個根本衝突確認
4. ❌ v9.0 推導在 v10.0 中失效 → **重建新推導** (docs/03)

## 閉合摘要 (2026-09-03)

- **新推導**: 離散 Feynman 規則 (基於 O80 Lagrangian, 88-site 物理 cutoff)
- **驗證**: 47/47 PASS (scripts/01-03)
- **保留**: O80 傳播子/自能, O37 m_δW, O82 質量譜 — 全部直接引用
- **新貢獻**: 完整傳播子表 + 頂點因子 + 2→2 散射 + tree-level unitarity (全域上界 0.00274 / kinematically-allowed 0.00039) + 模式對角守恆

## 前置

O80 (W-field Lagrangian) 🟢, O82 (質量生成) 🟢, O37 (Lagrangian) 🟢
