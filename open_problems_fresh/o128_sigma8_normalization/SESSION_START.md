# O128 — σ8 歸一化驗證

> **Session**: 2026-08-29 (新建立，從 v9.0 遷移)
> **狀態**: 🔴 未開始
> **來源**: v9.0 項目審計後發現不屬於 v10.0 O1-O114 任何現有系列
> **v10.0 位置**: `IDCM-v10.0--It-From-Beat/open_problems_fresh/o128_sigma8_normalization/`
> **v9.0 來源**: `open_problems_fresh/sigma8_norm/`

## 問題

見 `docs/01_problem_record.md`

## 前置驗證：v9.0 推導先行驗證

⚠️ **必須先驗證 v9.0 推導在 v10.0 非膨脹框架中是否仍然有效，然後才能開始攻堅。**

1. 讀取 `open_problems_fresh/sigma8_norm/` 中的原始推導
2. 識別依賴膨脹宇宙假設的部分（v9.0 使用 v9.0 框架）
3. 在 v10.0 非膨脹框架中重新驗證每個公式
4. 如果 v9.0 推導在 v10.0 中仍然有效，則直接遷移
5. 如果 v9.0 推導在 v10.0 中失效，則需要建立新推導

## 前置

O100 (C_ℓ→P(k)) 🟢, O99 (光本體論) 🟢, O92 (KiDS S8) 🟢
