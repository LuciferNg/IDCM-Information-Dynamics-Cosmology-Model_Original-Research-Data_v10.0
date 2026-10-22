# O62 十期 — 深入攻堅: SR ideal 完整閉合 (2026-08-24)

**狀態**: 🟢 完整閉合
**Scripts**: 56-67 (12 個)

---

## ★★★ SR Ideal 完整結構（cytools 權威）

```
cytools tri.sr_ideal() = 450 pairs (2-ary) + 34 triples (3-ary) = 484
sage 484 raw = 475 unique + 9 重複

★★★ sage unique 475 = no_edge37 (450) + anomaly (25) 完全相等!

分解:
  450 pairs = 421 (0-35) + 29 (涉 point 36 = -L₇ 反點)
  34 triples = 3-ary generators ({i,j,k} 唔係任何 2D face)
  25 anomaly = 34 triples 嘅 pair-subsets
    (1,3)⊂(1,3,22), (1,6)⊂(1,6,17), (6,15)⊂(6,15,16)...
  9 重複 = anomaly pairs 喺多個 simplex 出現

★★★ 34 triples 全部 κ=0 (34/34)!
  全部唔喺 co-simplex (34/34) — 即 {i,j,k} 唔係任何 face
  → 3-ary generators = 三互異零嘅代數根源!
```

## 25 Anomaly 深入

```
25 anomaly: 有共同 edge 但列 SR
  原因: 佢哋係 34 triples 嘅 pair-subsets
  cytools 用 minimal 表示 (3-ary 唔拆), sage 拆做 pairs 列出
  → 表示法差異, 唔係定義衝突!

特徵:
  edge star 3-7 (mean 4.5) — 全部低連接
  涉及點: 5 個動態點 {6,12,14,17,30} + 固定點
  點 6 出現 7 次, 點 12 出現 6 次

point 36 身份: (-1,-1,0,0) = -point 8 = -L₇ 反點!
  29 個 (·,36) pairs 涉 point 36 (star=8, 唔係 kappa divisor)
```

## 真正消去機制（修正後完整版）

```
★★★ 之前「SR pair 消去」嘅理解錯咗:
  SR pair (x_i x_j = 0) 唔保證 κ_ijk = 0 (45 反例)
  真正必要條件: (i,j,k) 必須共 simplex (350/350, 0 違反)

全域三層:
  8436 triples (i≤j≤k) = 904 co-simplex + 7532 非 co-simplex
  非 co-simplex 全部 κ=0 (7532) — SR 幾何消去 (共 simplex 必要條件)
  co-simplex 內: 554 零 + 350 非零
  554 零 = 331 三互異 + 220 兩同 + 3 全同 (i∈{3,7,14})

代數根源:
  2-ary SR (450 pairs) → 兩同相交零 (no-edge → κ_iij=κ_ijj=0)
  3-ary SR (34 triples) → 三互異零 ({i,j,k} 唔係 face)
```

## 檔案

```
scripts/56-60: anomaly edge/div0/star 深入
scripts/61-63: SR 定義測試 (A/B/C 等價 450)
scripts/64-65: cytools 權威 SR (450+34/35)
scripts/66-67: ★★★ SR 完整閉合 Audit (8/8)
```
