# O243 docs/05 — R4: Gemini claim 逐條結構反駁表

> **日期**: 2026-10-08｜**script**: scripts/04_gemini_rebuttal.py (**9/9 PASS**)
> **對應**: O243 問題記錄 §三 G-rebuttal / §四 R4

---

## 反駁表 (Gemini 2026-10-08 原文 → 結構裁決)

| # | Gemini 主張 | 裁決 | 數學依據 |
|:--|:-----------|:----:|:---------|
| G1 | 一階/穿隧/bounce 被封死 | ✅ 部分正確 | O241 Q5 + script 01: 唯一極小, 冇 false vacuum |
| G2 | 二階/連續相變依然可以發生 | ❌ 錯 | script 02 P2b: 二階相變需控制參數 g; g 係新自由度 ⟹ dof>1 ⟹ O212 排除 |
| G3 | φ₀ 從原點光滑滑到新位置 | ❌ 錯 | script 01 P1c: 原點 V''(0)=-4<0 係 local MAX, 唔係極小; script 02 P2c: SSB 已實現, 冇對稱相 |
| G4 | 有效溫度/流形曲率變化令勢能面形變 | ❌ 錯 | script 02 P2d/P2e: T_ring、R_world 係結構輸出 (O121/O171), 唔係 dial |
| G5 | 特徵譜線交叉重組 (Band Crossing) | ❌ 錯 | script 03 P3a/P3b: γ_n 非簡併嚴格遞增 + 冇 H(λ); min gap=5.1e-3 |
| G6 | winding number/幾何相位改變, 全域連續 | ❌ 錯 (部分) | script 03 P3d/P3e: O7 係離散局部位元寫入 (ΔE=2\|h_i\|, 沿 Goldstone flat direction), 唔係全域連續; Berry phase 喺 0 維參數流形恆 0 |
| G7 | 認識論轉向: 單向時間箭頭 | 🔶 方向啱, 機制錯 | script 04 G7a/G7b: 單向箭頭 = O121 投影冪等 + O213 ℓ-細化流→c (正確內核); 但「真空弛豫」錯 — v10 真空固定喺 w0, 宇宙演化係觀察者投影, 唔係勢能面滑移 |

## 核心錯誤分類

Gemini 嘅論證錯誤**唔係**「數值錯」, 而係**類別錯位 (category error)**:

1. **借咗 QFT 語言**: 二階相變/拓撲相變係 QFT (熱浴/哈密頓參數族) 嘅概念; IDCM W-field = DTO, 唔係 thermal/QFT vacuum;
2. **將輸出當 dial**: 溫度同曲率喺 IDCM 係結構輸出 (T_ring, R_world), 唔係環境控制鈕;
3. **將事件當相變**: O7 相位滑移 (離散資訊寫入) 被放大成「全域譜重組」。

## 正確嘉許 (誠實記錄)

- G1 對一階嘅理解正確 (唯一極小 ⟹ 冇穿隧);
- G7 嘅「單向」方向正確 — 對應 O121/O213 已閉合嘅時間箭頭結構。