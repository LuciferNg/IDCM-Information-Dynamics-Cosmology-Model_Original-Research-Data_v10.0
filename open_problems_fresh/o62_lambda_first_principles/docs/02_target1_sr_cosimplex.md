# O62 八期 — 目標一閉合: Co-simplex 消去定理 (第一性原理)

**日期**: 2026-08-24
**狀態**: 🟢 核心定理重現 + 三層消去分類
**Scripts**: 24-30 (7 個)

---

## 一、定理陳述

### 定理 1 (SR 必要條件 — 已嚴格證明)

```
κ_ijk ≠ 0  ⇒  (i,j,k) 必須共 simplex (即三個 index 同時出現喺至少一個 4-simplex)
```

**驗證**: 全域 36 模 (i≤j≤k) 非零數 = 350, 全部 co-simplex, **0 違反** ✅

幾何本質: 若三射線 v_i, v_j, v_k 唔喺同一 maximal cone, 對應嘅 toric divisor
無公共交點 → 三重相交恆零 (Stanley-Reisner ideal 直接強制)。

### 定理 2 (904 分解 — 完全重現)

```
904 co-simplex triples (i≤j≤k) = 554 κ=0 + 350 κ≠0
```

- 350 非零 = **119 三互異 + 198 兩同 + 33 全同**
- 554 零   = **331 三互異 + 220 兩同 + 3 全同**
- 確認 O58 嘅 kappa_36d_true.npy (350 nnz) = intersection_full 本質非零 (pattern 8436/8436 一致)

### 定理 3 (554 三層消去機制)

```
層 1 — SR 消去: 非 co-simplex → κ=0 (6690 三互異全部零)
層 2 — 全同零 (3): κ_iii = 0 for i ∈ {3, 7, 14}
         (self-intersection 零 — 特殊 divisor; 出現喺 28/28/24 simplices)
層 3 — 兩同零 (220): κ_iik = 0 行結構
         Σ_k κ_iik ≠ 0 只喺 i ∈ {1, 21} (±1)
         → 34/36 行全零 (κ_iik 極度稀疏)
層 4 — 三互異零 (331): co-simplex 但 cone 體積對消
         div0 傾向: 43.5% vs 非零 25.2% (1.7×)
         block 偏序: 0 違反 (triangulation 性質)
```

---

## 二、關鍵數據

| 數量 | 值 | 註 |
|:-----|:---|:---|
| 4-simplices | 144 | triangulation |
| 3D cones (facets) | 432 | 144×5/2 去重 |
| 點數 | 48 | 6 頂點 + 42 內部 |
| SR pairs | 484 (sage) / 912 (我計) | ⚠️ 定義差異 — sage 用 qhull 方向 |
| co-simplex triples | 904 | i≤j≤k |
| κ 本質非零 | 350 | 119+198+33 |
| κ 本質零 | 554 | 331+220+3 |
| 三互異非零 | 119 | 全部 co-simplex |
| κ_iii 對角 | [-360, 4, 2, 0, 8, ...] | i=0: -360, i=8: -232 |

## 三、新結構發現

1. **全同零 i ∈ {3,7,14}** — 三個特殊 divisor, self-intersection 零
   - i=3: κ=-360 嘅鄰居? (3 喺低 block)
   - i=7: 中 block 第一個
   - i=14: 高 block 第二個
2. **κ_iik 行和只喺 i∈{1,21} 非零 (±1)** — 極度稀疏嘅二次相交結構
3. **div0 (i=0) 強烈消去傾向** — 43.5% vs 25.2% (O58 亦發現 33.8% vs 16.6%)
4. **block 偏序對所有 904 co-simplex 成立 (0 違反)** — triangulation 本身性質

## 四、SR pairs 定義差異 (已解決 — 見 docs/06 十期完整閉合)

```
sage export: 484 raw = 475 unique = 450 (active 冇共同 edge) + 25 (anomaly)
★★★ 解決 (scripts 64-67, cytools 權威):
  cytools SR ideal = 450 pairs + 34 triples = 484
  25 anomaly = 34 triples 嘅 pair-subsets (表示法差異, 唔係定義衝突)
  462 個涉 inactive 點 pairs sage 唔列 (inactive 點唔係 toric divisors)
```

## 五、狀態

```
✅ 定理 1: SR 必要條件 (0 違反)
✅ 定理 2: 904 = 554 + 350 重現
✅ 定理 3: 三層消去分類 (3+220+331)
🟡 兩同零 220 嘅幾何機制 (D_i² support) — 部分
✅ SR pairs 484 vs 912 定義差異 (docs/06: 475=450+25, anomaly=triple subsets)
🟡 toric 體積公式 naive det 處理唔到 self-intersection
🔴 完整 Chow ring 計算 (需要 Macaulay2/Sage)
```

## 六、檔案

```
scripts/24_sr_ideal.py      ✅ SR 消去必要條件
scripts/25_554_search.py    ✅ κ 非零分佈 (119+198+33)
scripts/26_co_simplex.py    ✅ 三互異 co-simplex 450
scripts/27_cosimplex_full.py ✅ 904 = 554+350 (i≤j≤k) ★
scripts/28_toric_kappa.py   🟡 naive det 公式 (self-intersection 失敗)
scripts/29_chow_ring.py     ✅ κ 檔案對照 + 分類
scripts/30_cancellation.py  ✅ 三層消去分類 ★
```
