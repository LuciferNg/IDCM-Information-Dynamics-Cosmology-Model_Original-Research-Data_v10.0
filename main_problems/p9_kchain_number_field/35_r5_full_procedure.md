# R5 完整選擇程序閉合測試 — 35 (2026-10-17)

> **目標**: R5 (33/34 號) 昇做完整程序, 測試唯一鎖定 magic 5/5
> **Script**: `35_r5_full_procedure.py` → `data/35_r5_full_procedure.json`

---

## Q1 — anchor 覆蓋集唯一性 (★關鍵結果)

Cover triples (3-anchor 集令 G 覆蓋 magic 5/5) **只有 3 個**:

```
(5, 7, 11)   ← 唯一質數 triple! = {F₅, L₄, L₅}
(7, 10, 11)  ← 10 唔係質數 (10=2F₅)
(7, 11, 20)  ← 20 就係 magic 自己 (trivial, 用 magic 做 anchor)
```

**裁決**: 唯獨 `(5, 7, 11)` 係「三質數 anchor」且覆蓋 — F₅/L₄/L₅ 三質數 anchor 對嘅唯一性成立 (其他兩個 triple 要撈 magic 成員或者合數先得)。

## Q2/Q3 — 完整程序 (S1–S5) 喺數據上嘅決定性

```
S1 生成: G = {m×anchor} = [5,7,10,11,14,15,20,21,22,28,33] (11 個)

按 gcd 類:
  gcd1  [5, 7, 15, 21]    deg40   → 唯一 Lucas∧質數 = 7 ✓
  gcd2  [10, 14]          deg20   → 14 (Lucas 鏈) vs 10 (Fib 鏈)
  gcd8  [20]              deg5    → 20 ✓ (唯一)
  gcd11 [11, 33]          deg4    → 11=data 排除 → 33 ✓
  gcd16 [28]              deg5    → 28 未排除! (撞 deg5 層)
  gcd22 [22]              deg2    → 22 ✓ (唯一)

按 deg 層:
  deg40 [5, 7, 15, 21]   → 7
  deg20 [10, 14]         → 待判 (14 vs 10)
  deg5  [20, 28]         → 撞! (gcd8 vs gcd16)
  deg4  [11, 33]         → 33
  deg2  [22]             → 22
```

**Q3 答案**: gcd16 嘅 28 (4L₄) 同 gcd8 嘅 20 撞喺 deg5 層 — 假設 S3「每 deg 層一代表」, 28 被排除。但點解 gcd8 優先於 gcd16? **未閉合** (兩個都係 4×anchor)。

**Q4 答案**: gcd2 内 14 = 2L₄ (Lucas 鏈) vs 10 = 2F₅ (Fib 鏈) — 兩者都係鏈, **未閉合**。

## Q5 — 自由參數審計 (overfit 檢查)

| 參數 | 狀態 |
|:--|:--|
| anchor 集 (7,11,5) | 後驗 — 但 Q1 顯示唯一質數 triple ✅ |
| 乘數 {1,2,3,4} | 後驗 (Lucas 頭四值) |
| S2 每類一代表 | 操作代表定義 (17 號文檔) ✅ |
| S3 每 deg 一代表 | 32 號 T1 結構事實 ✅ |
| S4 data-free | R1 嘅實用規則 (11=data) |
| S5 gcd1 唯一 Lucas∧質數 | 33/34 號新規則 |
| **gcd2: 14 vs 10** | **未閉合 — 兩者都係鏈** |
| **gcd16: 28 排除** | **未閉合 — 靠 S3 但唔知點解 gcd8 優先** |

## 開放項收窄

```
關閉咗: cover triple 唯一性 (5,7,11) = 質數 anchor 對
收窄咗: 完整程序剩 6 類, 其中 4 類已鎖 (gcd1/8/11/22)
仍開:   gcd2 (14 vs 10) 同 gcd16 (28 vs 20) 都要「Lucas > Fibonacci」優先判準
        但 20 = 4F₅ 係 Fibonacci, 33 = 3L₅, 22 = 2L₅ — magic 本身就混用!
```

## ★ 新洞察 — 「Lucas > Fib」唔成立 (magic 自己混用)

```
如果規則係「Lucas 鏈優先」:
  14 (L) vs 10 (F) → 14 ✓ 啱
  20 (F) vs 28 (L) → 20 ✗ 錯! 28 先應該 (28=4L₄ 係 Lucas)
⟹ Lucas 優先規則 FAIL — magic 自己 gc8 揀 20 (F) 而捨 gcd16 28 (L)
⟹ gcd8 vs gcd16 嘅判準唔可能係「鏈類型優先」
```

## 判定

| 輪 | 閉合狀態 |
|:--|:--|
| Cover triple (5,7,11) 唯一質數 anchor | ✅ 結構事實 |
| gcd2 内 14 vs 10 | 🔴 未閉合 |
| gcd16 内 28 排除 (vs gcd8 20) | 🔴 未閉合 — Lucas 優先規則 FAIL |
| R5 完整程序唯一鎖定 magic | ⚠️ **接近 — 6 類鎖 4, 剩 2 類開放** |

## 檔案
```
35_r5_full_procedure.py       — 本輪 script
data/35_r5_full_procedure.json
```