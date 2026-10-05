# O53 發現 — HuggingFace polytopes-4d metadata 錯誤率 40%

> **日期**: 2026-08-22
> **狀態**: 🔴 **數據集警示 — HF metadata 不可靠；我哋嘅 Sage export 先係正確 (36,98)**
> **腳本**: scripts/85-88

---

## 一、發現

1. HF 提取嘅 (36,98) polytope（20 vertices）用 CYTools 計出 **h11=43, h12=37**（唔係 36,98）
2. 同我哋嘅 Sage export（48 points, h11=36, h12=98）**唔等價**（linearly/affinely 都 False）
3. 抽樣 10 個 h11=36 entries：**只有 6 個 h12 匹配，4 個唔匹配（40% 錯誤率）**
4. 連「h11=36」都唔準 — 匹配嗰啲計出嚟 h11=37/40/41

## 二、影響

| 用途 | 影響 |
|:-----|:-----|
| 對照 polytope (36,94) | 🔴 唔可靠（HF 版本唔係真 (36,94)）|
| 用 HF 做 h11=36 家族分析 | 🔴 唔可靠（40% 錯誤）|
| **我哋嘅 Sage export** | ✅ **正確（CYTools 確認 h11=36, h12=98）** |

## 三、教訓

1. **HF polytopes-4d 數據集 metadata 有系統性問題**（可能 h11/h12 column 對錯）
2. **我哋一直用嘅 Sage export 係正確嘅** — 唔好因為 HF 出現而懷疑原有數據
3. 對照測試需要用其他方法（例如 CYTools fetch 或者直接搜尋）

## 四、狀態

- ✅ 3×12 block-triangular（真 κ）— 不受影響
- ✅ Sage export 係唯一可靠 (36,98) 來源
- 🔴 對照 polytope 分析需要新方法（CYTools fetch 或者 hep 數據庫）
