# O58 — HF polytopes-4d Metadata 系統性錯誤：h11/h12 對調

> **狀態**: 🟢 已確認 — 系統性問題
> **日期**: 2026-08-24
> **嚴重性**: 🔴 高 — 影響所有依賴 HF metadata 嘅分析

---

## 核心發現

**HuggingFace `calabi-yau-data/polytopes-4d` 數據集嘅 h11/h12 metadata 係對調嘅（swapped）！**

### 證據

**08-vertices 檔案（15/15 樣本）：**

| meta (h11,h12) | PALP (h11,h21) | swap 一致? |
|:---|:---|:---|
| (72,18) | (18,72) | ✅ |
| (40,34) | (34,40) | ✅ |
| (37,31) | (31,37) | ✅ |
| (66,14) | (14,66) | ✅ |
| ... | ... | ✅ 15/15 |

**20-vertices 檔案（2/2 命中）：**

| meta | PALP | 真實 |
|:---|:---|:---|
| (36,98) row 0 | (98,36) | **h11=98, h21=36** |
| (36,98) row 1 | (98,36) | **h11=98, h21=36** |

### 結論

1. **HF metadata h11/h12 對調**：HF 標 (a,b) 嘅 polytope 真實係 **(b,a)**
2. **HF 標 (36,98) 嘅兩個實例 = 真實 (98,36)** — 唔係 (36,98)！
3. **O53 嘅「HF (36,98) 實例」全部係 (98,36)** — 即 h11=98, h21=36 嘅 mirror polytope

### 點解 O53 話 (43,37)？

`cy36_98_hf.poly`（o53 提取嘅檔案）PALP 話 H:37,43 → 真實 (43,37)。呢個唔符合 swap 規則 — 因為 **o53 提取時揀咗錯誤嘅 row**（可能 metadata 混亂 + vertex 次序唔同）。呢個檔案唔係 20-vert parquet 兩個 (36,98) row 嘅直接 copy（vertex 次序唔同）。

### 影響

| 分析 | 影響 |
|:-----|:-----|
| O53「(36,98) 喺 HF 有 2 實例」 | ❌ 實際係 (98,36) 2 實例 |
| O53「h12=98 孤島」統計 | ⚠️ 要重做（用 swap 修正後） |
| 任何用 HF h11/h12 做 filter 嘅分析 | ⚠️ 全部要 swap |
| `20-vertices.parquet` h12=98 有 210 個 | ⚠️ 呢 210 個其實係 h11=98 |

### 但係 — canonical (36,98) 仍然穩固！

- **PALP 直接確認**：`polytope_36_98.txt`（canonical 6-vertex）H:98,36 = h21=98, h11=36 ✅
- **CYTools 直接確認**：h11=36, h21=98 ✅
- **all_36_98.poly 100 實例**：全部 H:98,36 ✅（PALP 直接驗證）
- O53 嘅 3×12 block 結構、孤島統計（用 all_36_98.poly + CYTools）**不受影響**

### 修正建議

用 HF 數據時：**swap h11 ↔ h12**（或者直接重新用 PALP/CYTools 驗證每個 polytope）

## 檔案

```
scripts/11_hf_metadata_audit.py   # 原版（CYTools 慢）
scripts/11b_hf_metadata_palp.py   # PALP 版
data/hf_metadata_audit.json
```
