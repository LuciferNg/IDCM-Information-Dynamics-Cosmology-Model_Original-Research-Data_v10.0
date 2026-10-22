# O62 九期 — 後續四項目攻堅 (2026-08-24)

**狀態**: 🟢 三個閉合 + 一個深入
**Scripts**: 41-54 (14 個)

---

## 項目 4: SR pairs 484 vs 912 → 🟢 閉合

```
★★★ sage 484 raw = 475 unique = 450 (active 冇共同 edge) + 25 (anomaly)
5 個 anomaly pairs 重複 (9 次): (1,6)×2, (6,15)×2, (6,17)×3, (10,12)×3, (12,14)×4
active-only 冇共同 edge: 450, sage ∩ = 450, active − sage = 0 ✅
no_edge − sage 462 個全部涉 inactive 點 (37-47) — sage 唔列

25 anomaly: 有共同 edge 但列 SR (需進一步, 可能 cone 結構)
  例: (1,3), (1,6), (1,17), (2,6), (3,8), (6,15)...

結論: SR pairs 定義 = active 點間冇共同 edge (450/450 零差)
+ 25 個「edge 存在但 div 相交零」額外
+ 9 個重複 = anomaly 喺多 simplex 出現
```

## 項目 2: Dual polytope Δ* → 🟢 閉合 (鏡像驗證)

```
★★★ M:48, N:85 解謎:
  M = Δ 點數 = 48
  N = Δ* 點數 = 85

Δ: 6 頂點, 48 點, 1 內部點, 7 facets
Δ*: 7 頂點, 85 點, 1 內部點, 6 facets, reflexive ✅

★★★ Mirror 對稱完整驗證 (cytools):
  P.h11 = 36, P.h12 = 98
  P_dual.h11 = 98, P_dual.h12 = 36 — 完美互換!

Δ facets 點數: [23, 11, 22, 10, 10, 5, 37]  (37 = active!)
Δ* facets 點數: [77, 5, 34, 58, 8, 13]
```

## 項目 1: Chow ring → 🟢 真正消去機制 (修正)

```
★★★ 重大修正: SR pair 唔保證 κ=0 (45 反例!)
  真正必要條件: (i,j,k) 必須共 simplex (350/350, 0 違反)

全域三層:
  8436 triples (i≤j≤k) = 904 co-simplex + 7532 非 co-simplex
  非 co-simplex 全部 κ=0 (7532) — SR 幾何消去 ✓
  co-simplex 內: 554 零 + 350 非零

554 零 = 331 三互異 (cone 對消) + 220 兩同 + 3 全同 (i∈{3,7,14})
```

## 項目 3: 5020 對照 → 🟢 48/85 專屬性

```
all_36_98.poly: 100 個 (36,98) polytopes
頂點數: 6(2), 7(8), 8(16), 9(69), 10(5)

★★★ (M,N) 分佈: (48,85) 只出現 1 次 = canonical!
另一個 6 頂點: (53,80)

M+N = 133 家族: 12 個 (12%)
  (48,85), (49,84), (50,83), (51,82), (52,81), (53,80), (54,79)
  133 = 3×44 + 1 = 3N_d + 1
  canonical (48,85) = 133 家族中 M 最小端點

結論: M:48, N:85 = canonical 專屬 (6 頂點都唔保證)
```

## 統一發現

```
★★★ M + N = 133 = 3N_d + 1 (canonical 家族)
★★★ Mirror: Δ ↔ Δ* 完整 h11/h12 互換
★★★ 真正 SR 消去 = 共 simplex 必要條件 (非 SR pair)
★★★ 48/85 專屬性 = canonical 身份
```

## 檔案

```
scripts/41-45: SR pairs 深入 (項目 4)
scripts/46-47: Dual polytope (項目 2)
scripts/48-50: Chow ring 消去機制 (項目 1)
scripts/51-54: 5020 對照 + 48/85 + M+N=133 (項目 3)
```
