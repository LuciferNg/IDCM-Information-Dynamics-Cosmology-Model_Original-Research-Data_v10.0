# O58 — (36,98) 真實 Toric 構造（PALP 鑑定）

> **狀態**: 🟢 完成（PALP + CYTools 交叉驗證）
> **日期**: 2026-08-24
> **問題**: (36,98) 對應邊個具體反射多面體？（O53 開放問題 3）

---

## 核心結論

### 1. (36,98) 唔係 Weighted-Projective（CWS）構造 — 係 General Toric

- **CWS 搜尋**: `w5.ip.gz`（184,026 條 5-權重 CWS）+ `w44.ip.gz`（16,040 條雙 CWS）**全部掃描 0 hits**
  （`poly.x -g` batch 模式，12 秒掃完 200,066 條，~1000× 加速）
- **O53 已確認**: `wp4.spec`（2,781 weighted-projective pairs）冇 (36,98)
- **結論**: (36,98) 只存在於 general toric 家族（`alltoric.spec` 有記錄），**冇單一 CWS 表示**

### 2. Canonical 多面體（K_Chain 完美匹配）

```
# polytope_36_98.txt / all_36_98.poly #0
6 vertices, 4D reflexive
M:48 6  N:85 7  H:98,36 [124]
```

| 性質 | 值 | K_Chain 對應 |
|:-----|:---|:------------|
| M 點數 | **48** | = N_d + B = 44 + 4 ✅ |
| M 頂點 | 6 | — |
| N 點數 | 85 | = 44+44−3? （探索） |
| N 頂點 | 7 | — |
| Hodge | h21=98, h11=36 | = Σγ+2B, N_d−2B ✅ |
| χ | 124 (PALP 慣例) / −124 (IDCM) | 2(h11−h21) = −124 ✅ |
| GL(Z,4) 對稱 | 1（無） | — |

### 3. HuggingFace `polytopes-4d` 20-vertices 實例 — Metadata 系統性 swap！

| 實例 | parquet metadata | 實際 CYTools Hodge | 等價性 |
|:-----|:----------------|:------------------|:-------|
| instance 0 (`cy36_98_hf.poly`) | h11=36, h12=98 | **h11=43, h21=37** ❌ | 唔係 (36,98) |
| instance 1 | h11=36, h12=98 | **h11=98, h21=36**（= (98,36)）| 係 mirror，唔係 (36,98) |

⚠️ **HF metadata h11/h12 對調**（15/15 + 2/2 PALP 確認，詳見 docs/04）— 必須 swap 或用 CYTools/PALP 重新驗證。HF 標 (36,98) 實為 (98,36)。**真實 (36,98) 有 5,021 個**（docs/06）。

### 4. KS 家族結構 — 至少 100 個唔同 polytope

- `all_36_98.poly` 100 個實例：**100/100 全部線性不等價**（CYTools `is_linearly_equivalent` 精確檢驗）
- Vertex 分佈：6v ×2、7v ×8、8v ×16、9v ×69、10v ×5
- **Canonical #0（48 pts）係唯一 M 點數 = 44+4 嘅實例**
- 其他實例 M 點數：44、49、50、51、52、53、54、55...

### 5. N-lattice（dual polytope）結構

- 85 點：coord 3 有 17 個 distinct 值（−1..15）長鏈結構
- 冇簡單 Z₂ 坐標鏡像對稱（只有 1 對 ± pair）
- 含原點 ✅（reflexive 必有）
- **Z₂ mirror（n↔44−n）係頻率/beat-space 性質，唔係 N-lattice 坐標空間性質**

---

## 方法論

| 步驟 | 工具 | 結果 |
|:-----|:-----|:-----|
| 1. Hodge 確認 | `poly.x -g` | 100/100 H:98,36 |
| 2. CWS 排除 | `poly.x -g` batch × 200K | 0 hits → general toric |
| 3. HF 實例驗證 | CYTools `Polytope().h11()/h21()` | inst0=(43,37)❌, inst1=(36,98)✅ |
| 4. 等價類 | CYTools `is_linearly_equivalent` | 100/100 獨立 class |
| 5. N-lattice | `poly.x -d` + 分析 | 85 點, coord3 長鏈 |

## 檔案

```
scripts/01_palp_identify.py      # 100 實例 Hodge 鑑定
scripts/02_search_cws.py         # CWS 200K 掃描（batch）
scripts/03_canonical_structure.py # canonical 結構 audit
scripts/04_fingerprints.py       # normal form 指紋（PALP -N）
scripts/05_family_structure.py   # 家族統計
scripts/06_true_classes.py       # 真等價類（CYTools）
scripts/07_n_lattice_z2.py       # N-lattice Z₂ 結構
data/polytope_36_98.txt          # canonical 6-vertex
data/all_36_98.poly              # 100 實例
data/cy36_98_hf.poly             # HF inst0（⚠️ 實為 43,37）
data/cws_hits.json               # CWS 搜尋結果（0 hits）
data/polytope_fingerprints.json  # normal form 數據
data/true_equivalence_classes.json # 100 獨立 class
data/n_lattice_structure.json    # N-lattice 分析
```

## 開放問題（承接 O53/O57）

- 🔴 **A1 (n/3 起源)**: 冇 K_Chain 直接對應 — 需要 Kähler cone / d_ijk 幾何驗證
- 🟡 **M 點數 48 唯一性**: 其他 (36,98) 實例有 44-55 點，點解 canonical 係 48=44+4？
- 🔴 **N 點數 85 = ?**: 85 = 44+41 = 44+Σγ/2−4?（探索）
- 🟡 **HF metadata 錯誤率**: inst0/inst1 有一個錯 → 需要系統性檢查 HF dataset 其他 h12

## 驗證狀態

| 項目 | 狀態 |
|:-----|:-----|
| PALP 100/100 (36,98) | ✅ |
| CWS 排除 (general toric) | ✅ |
| canonical 48 = 44+4 | ✅ |
| HF inst0 metadata 錯誤發現 | ✅ |
| 100 實例獨立性 | ✅ |
| N-lattice 85 點 | ✅ |
