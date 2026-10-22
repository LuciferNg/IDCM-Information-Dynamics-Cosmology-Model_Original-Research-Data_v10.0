# docs/01 — Claude 九圈 N=4 SYM 散射振幅解法摘要

> **2026-10-04** | 來源: Anthropic (2026-09-25), 驗證: CellCog, 原始數據: smsharma.io

---

## 一、問題陳述

計算 **planar N=4 Super Yang-Mills** 在 **九圈** 的 **六粒子 (hexagon) MHV 散射振幅**。

- N=4 SYM：每個粒子攜帶四個超對稱夥伴的 toy model（數學上更易處理，但非真實世界理論）
- Planar：大 N_c 極限（只有平面費曼圖），振幅具有可積性結構
- MHV (Maximally Helicity Violating)：最簡單的 helicity 配置
- 先前紀錄：8 圈 (Lance Dixon & Andy Liu, 2023, arXiv:2308.08199)

## 二、解法概述（雙路線）

### 路線 A：形狀因子 bootstrap（主要）

1. **起點**：從 chiral stress-tensor 多重態的三點形狀因子 (form factor) 開始
2. **條件**：extended-Steinmann 約束、奇偶守恆、符號 alphabet
3. **Antipodal duality**：將 form factor 映射到奇偶守恆面 Δ=0 上的六粒子振幅
4. **提升**：用雙膠子通量管數據 (pentagon OPE at order T²) 固定剩餘歧義，離開 Δ=0 面

### 路線 B：直接 bootstrap
- 在 hexagon 函數空間中直接 bootstrap 九圈 symbol
- 兩種表示法一致（驗證通過）

## 三、關鍵參數與維度

| 量 | 值 | 說明 |
|:---|:---|:-----|
| weight-13 symbol 空間 | dim 5,431 | extended-Steinmann hexagon 空間基底 |
| 五重 coproduct 數 | 424 | `S[E^(9)] = Σ α E_α ⊗ S_α` |
| 非零坐標 | 1,018,297 | 其中 99.62% (1,014,476) 可證為有理數 |
| 全 weight-18 項 | ~30 × 10⁹ | 完整 symbol 寫出的項數 |
| 七重 final entries | 8,028 | 完整振幅定義的最終條目 |
| weight-11 基底函數 | 251 | 其中 symbol 為零者 |
| 積分常數 (weight 12-18) | 72 | 多重 Zeta 值表示 |
| 振幅常數 n₁…n₆ | 6 個 | equation (10.5) 型 |
| E^(9)(1,1,1) | 673,807,654.734… | 振幅在對稱點的值 |
| E^(9)/E^(8) | −14.1114787… | 振幅比值 |

## 四、使用的數學結構

| 概念 | 角色 |
|:-----|:-----|
| **Extended-Steinmann 約束** | 限定 symbol 可居住的 cohomology 空間；物理振幅必須滿足的解析性條件 |
| **Antipodal duality** | Form factor ↔ Amplitude 的對偶映射（Dixon-Liu 2023 的關鍵對稱性） |
| **Symbol 代數** | 把多對數函數的超越結構編碼為張量積，可程式化處理 |
| **Pentagon OPE** | 近共線極限的通量管展開（finite-coupling flux-tube 公式），提供 T² 階數據以固定歧義 |
| **Hexagon 函數空間** | 專為 planar N=4 SYM 六粒子振幅設計的函數空間（含 extended-Steinmann + 多重 final-entry 條件） |
| **多素數驗證** | 在兩個 31-bit 素數和四個 21-bit 素數上獨立計算，確保結構一致 |

## 五、技術亮點

- **無監督運行**：一句提示啟動，之後只重複「繼續做直到我叫停」，運行數天
- **計算成本**：bootstrap 步驟用 Python + SymPy，約 $100 (96 CPU 一週)；Claude 用量約 $1,000-2,000
- **驗證**：Lance Dixon 獨立確認（主要通過 form factor → amplitude 回溯）；Song He 組同期獨立接近完成
- **框架**：Fable 5.1 harness (Claude Science)

## 六、局限

- 方法已知（非新概念），主要是計算可靠性突破
- 程序不公開（只有結果檔案公開）
- 3,821 個坐標 (0.38%) 尚未被雙素數認證為有理數
- 尚未同行評審（物理論文由人類研究組撰寫）

## 七、Source

- Anthropic: https://www.anthropic.com/research/yes-claude-can-do-nine-loops
- 九圈振幅數據: https://smsharma.io/cosmic-nine-loops/
- Zenodo (Song He 組): https://doi.org/10.5281/zenodo.22800071
- 8 圈先例: arXiv:2308.08199
- Matt von Hippel 挑戰: https://4gravitons.com/2026/08/07/it-only-counts-when-ai-gets-to-my-field/