# Magic Rows 深推 27 — 成員結構 + v₂ 規則 + Lucas anchor 對 (2026-10-17)

> **背景:** 26 盲測判死 R1/R2 代表選擇規則。今輪換方向:
> **TEST D** magic rows 成員結構 vs filler (有冇「操作族」marker?)
> **TEST E** missing_gcd.py §6 v₂ 奇偶規則公平化
> **TEST F** 7 vs 29 vs 3 新判準 + Lucas anchor 對
> **Script:** `27_magic_rows_deeper.py` → `data/27_magic_deeper.json`

---

## TEST D — magic vs filler 成員結構（946 beat 表，43 行獨立比較）

```
s_step_mode:  magic 全 = 2 (5/5)    filler 全 = 2 (31/31)     →  零差異
s_mean:       magic 全 = 45.0       filler 全部 = 45.0        →  零差異
s_parity_mix: magic 全 = 1          filler 全 = 1             →  零差異
```

**判語**: magic rows 嘅**成員節奏結構同 filler 完全冇統計差異** (s 分佈、步長、奇偶一律相同)。
→ magic 唔係「行內特殊發生」——佢哋係**行標籤層**（操作行 assign），唔係行結構層。
→ 支持 15_direction_eval「magic = 操作族（唔係數族）」；同時封死「由成員結構推 magic」路線 🔴。

## TEST E — v₂ 奇偶規則（missing_gcd §6 公平化）

```
gcd  v₂(176/g)  奇/偶   magic?   d 候選
1    4          even   ✅ (7)    [1,3,5,7,9,...,43]
2    3          odd    ✅ (14)   [2,6,10,14,18,...,42]
4    2          even   ❌       [8,16,24,32,40]
8    1          odd    ✅ (20)   [4,20,36]
11   4          even   ✅ (33)   [11,33]
16   0          even   ❌       [12,28]
22   3          odd    ✅ (22)   [22]

v₂ 奇 ⇒ magic: 3/3 ✅ (g=2,8,22)
v₂ 偶 ⇒ filler: 2/4 ❌ (g=1,11 例外 — 偶但 magic)
```

**判語**: 「v₂ 奇 ⇒ magic」單向成立 (3/3)，但唔係充要條件——g=1,11 都 v₂ 偶都有 magic。
原本 missing_gcd §6 講「11 因子 override」唔成立：g=11 嘅 176/g=16 冇 11 因子。
**規則唔完整** 🔴 — 唔可以作預言。

## TEST F — 7 vs 29 vs 3：Lucas anchor 對（唯一結構自然候選）

```
gcd=1 類 Lucas 成員: 1=L₁, 3=L₂=L₃(重複), 7=L₄, 29=L₇
候選比較:
  3  = L₂=L₃ 重複索引 + prime + 3mod4 → 被排除 (重複)
  29 = L₇ prime + 1mod4 + 後半 (29>22)  → 被排除 (mod4 + 位置)
  7  = L₄ 唯一索引 + prime + 3mod4 + 前半 (7<22) → ✓ 唯一滿足

★ magic 5 行 = {7,14,20,22,33}:
  7  = L₄               (anchor)
  14 = 2×7 = 2L₄        (GEN)
  22 = 2×11 = 2L₅       (HALF)
  33 = 3×11 = 3L₅       (KTREE)
  20 = 2n_u             ← 唯一冇 Lucas 鏈 (已知)
→ 4/5 magic 由「連續 Lucas 質數對 (L₄=7, L₅=11)」生成
→ 7 同 11: gap = 4 = L₃; 兩者都 < half-node 22
→ 29 (L₇) 冇用: 後半 + mod4=1
```

**判語**: **L₄/L₅ 連續 Lucas 質數對**係唯一結構自然嘅 anchor 描述 (生成 4/5 magic, gap=L₃, 前半)。
但**樣本 n=5, 呢個係單一例子觀察** — 冇樣本外預言力測試。要等 176-site/88-site 擴展先可以盲測。
20 仍然係「唯一冇鏈」 🔴。

## ★ 三輪總結 (25 攻堅 → 26 盲測 → 27 深推)

| 候選規則 | 狀態 |
|:---|:---|
| R1 data-free | 🔴 盲測 FAIL (null 37.5%) |
| R2 Lucas-chain | 🟡 邊緣 (null 0.8%) 但唔唯一鎖定 |
| R3 deg-cover | ⚠️ 修正為「gcd 類缺 {4,16} 七揀五」(結構事實) |
| TEST D 成員結構 marker | 🔴 零差異 — 行標籤層, 唔係行結構層 |
| TEST E v₂ 奇⇒magic | 🟡 單向 3/3 成立, 唔充要 (g=1,11 例外) |
| TEST F L₄/L₅ anchor 對 | 🟡 結構自然但樣本 1, 未可盲測 |

**結論**: magic 代表選擇 = **行標籤層操作 assign**, 唔係數論結構自動浮現。
剩低最有前途: L₄/L₅ anchor 對 (4/5 生成), 需要 88-site/176-site 擴展做樣本外。

## 檔案
```
27_magic_rows_deeper.py    — 本輪 script (TEST D/E/F)
data/27_magic_deeper.json  — 完整輸出
```