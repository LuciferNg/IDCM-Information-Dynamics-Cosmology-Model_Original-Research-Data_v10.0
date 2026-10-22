# O70 — 155 Curves Facet 結構分析報告

> **日期**: 2026-08-31
> **狀態**: 🟡 **深化分析完成 — 結構更新**
> **前置**: O57 docs/02-03 (155 curves), O57 docs/24 (開放問題 #7)
> **腳本**: scripts/01-04, data/01-04

---

## 一、結構確認（155 幾何）

### 155 = 2×73 + 9 ✅

| 項 | 值 | 推導 |
|:---|:---|:------|
| 155 | C(36,2) − 475 | 630 − 475 = 155 sr_ideal complement |
| 2×73 | 146 | C(36,2) − 475 − 9 = 146 |
| 9 | 3² = N_gen² | 9 duplicate sr_ideal entries (5 unique pairs) |
| 73 | Nd + L₇ = 44 + 29 | ✅ |
| 73 | L₆×4+1 = 18×4+1 | ✅ |
| 73 | CPX projection rank (O53) | ✅ |

### 9 Duplicate sr_ideal 結構

| 對 | 次數 | 多餘 |
|:--|:----:|:----:|
| (12, 14) | 4 | 3 |
| (6, 17) | 3 | 2 |
| (10, 12) | 3 | 2 |
| (1, 6) | 2 | 1 |
| (6, 15) | 2 | 1 |

涉及 points: {1, 6, 10, 12, 14, 15, 17} — 7 個點，其中 point 6 出現 3 次

### 155 Curves Volume Vectors

| 量 | 值 | 身份 |
|:---|:---|:-----|
| Nonzero vectors | 52/155 | Nd+2B = 44+8 ✅ |
| Rank | 30 | 2L₅+2B = 22+8 ✅ |
| Null directions | 6 | 36 − 30 |

---

## 二、★★ 重要更正：155 Curves ⊂ K 態，唔係 C 態

**O57 docs/03 原本寫法**: "155 curves rank 30 = 2L₅+2B = C sector（最強閉合）"

**實際數據**: 155 curves 嘅 30-dim subspace 係 **K 態空間嘅子空間**，唔係 C 態！

| 測試 | 結果 |
|:-----|:-----|
| C 態投影到 155 curves | **0.0000** — 完全正交 |
| K 態投影到 155 curves | **0.9029** mean — 高度重疊 |
| K 態 >0.9 overlap | **27/36** |
| Null directions ↔ K 態 | **6 個 principal angles ≈ 0** |

### 正確解讀

```
155 curves (30-dim) ⊂ K 態空間 (36-dim)
K 態空間 = 155 curves (30) ⊕ 獨立 (6)
C 態空間 (30-dim) = 完全正交於 155 curves
```

**6 個 K 態不在 155 curves 入面** = 6 null directions = 36 − 30

---

## 三、Kähler Cone 分析

### 方法 A: Halfspace Intersection
- **J* 唔係 cone interior**: 31 positive, 21 negative, 103 zero
- 155 curves 定義 155 個 hyperplane constraints
- 但 rank 30 → 只有 30 個獨立 constraint

### 方法 B: SVD 分析
- 155 curves → 52 nonzero → rank 30
- 6 null directions = cone unbounded directions
- Kähler cone 需要 32 個獨立約束，curves 只給 30

### 方法 C: CYTools curve_basis
- curve_basis = 32（同 divisor_basis 相同 indices）
- curve_basis indices: [1, 2, 5, 6, 9, 10, ..., 36]
- 4 missing [3, 4, 7, 8] = N_gen, B, L₄, 2B

### 缺失 Divisors 參與 155 Curves
- 35 adjacency pairs involve missing divisors
- 120 pairs involve only present divisors
- 19/35 missing-divisor pairs have nonzero volume
- 33/120 present-divisor pairs have nonzero volume

---

## 四、Curve 數量對照表

| 類型 | 數量 | 定義 | 來源 |
|:-----|:----:|:-----|:-----|
| Adjacency curves | 155 | C(36,2) − unique sr_ideal | sr_ideal complement |
| CYTools curve_basis | 32 | Mori cone generating set | cy.curve_basis() |
| Total toric curves | 185 | All curves | cy.compute_curve_volumes() |
| C sector | 30 | 66 態嘅 CPX 態 | 66 態投影 |
| K sector | 36 | 66 態嘅 Kähler 態 | 66 態投影 |

---

## 五、更新狀態

### 🟢 已閉合（This session）
1. 155 = 2×73+9 結構完全驗證 ✅
2. 73 = Nd+L₇ = 44+29, 73 = L₆×4+1 ✅
3. 9 = 3² = N_gen² = 9 duplicate sr_ideal entries ✅
4. 52 nonzero = Nd+2B, rank 30 = 2L₅+2B ✅
5. ★★ 155 curves ⊂ K 態空間（唔係 C 態）— O57 docs/03 更正 ✅

### 🟡 仍然開放
1. **36-dim Kähler cone extremal rays** — CYTools 卡死，替代方法未完成
2. **155 curves ↔ Kähler cone facet 對應** — rank 30 支持但未證
3. **質量階層機制** — 155 curves 同 66 態嘅質量預言
4. **J* e^{−V} 範圍 1.85** — 唔夠 SM 10⁸

---

## 六、檔案

```
scripts/
├── 01_155_structure_analysis.py    ✅ 155 結構驗證
├── 01b_corrected_count.py          ✅ 計數核對
├── 02_cone_analysis.py             ✅ Kähler cone 替代方法
├── 03_curve_counts_cytools.py      ✅ Curve 數量對照
└── 04_66_states_connection.py      ✅ 66 態關聯分析

data/
├── 01_155_structure.json
├── 01b_corrected_count.json
├── 02_cone_analysis.json
├── 03_curve_counts.json
└── 04_66_states_connection.json
```