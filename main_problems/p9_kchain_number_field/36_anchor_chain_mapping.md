# Anchor 鏈→類映射 — 36 (2026-10-17)

> **目標**: 解 35 號殘留 — gcd2 (14 vs 10) 同 gcd16 (28 出局); 驗證「Lucas>Fib FAIL」
> **Script**: `36_anchor_chain_mapping.py` → `data/36_anchor_chain_mapping.json`

---

## R5 生成成員全特徵表

```
 d   rep    gcd  mir  mirg  m16  v2  half  data  Lch  Fch  magic
 5   1×F₅    1   39   1    5   0   前   F    F    T    —
 7   1×L₄    1   37   1    7   0   前   F    T    F    M
10   2×F₅    2   34   2   10   1   前   F    F    T    —
11   1×L₅   11   33  11   11   0   前   T    T    F    — (data)
14   2×L₄    2   30   2   14   1   前   F    T    F    M
15   3×F₅    1   29   1   15   0   前   F    F    T    —
20   4×F₅    8   24   4    4   2   前   F    F    T    M
21   3×L₄    1   23   1    5   0   前   T    T    F    — (data!)
22   2×L₅   22   22  22    6   1   軸   F    T    F    M
28   4×L₄   16   16   4   12   2   後   F    F    F    —  ← Lch=False?!
33   3×L₅   11   11  11    1   0   後   F    T    F    M
```

※ 注: 28 嘅 Lch=False 因為 L* 定義 m∈{1,2,3} (TEST F) 而 28=4×7 — **28 = 4L₄, m=4 Lucas 鏈超咗 TEST F 個 m≤3 窗口**!

## ★ 關鍵新發現 (更正 35 號結論)

### 1. 35 號「Lucas>Fib FAIL」係誤報

```
35 號話: 「20=4F₅ 被揀, 28=4L₄ 被捨 ⟹ Lucas 優先 FAIL」
實際: 20 ∈ gcd8, 28 ∈ gcd16 — 唔係同一 gcd 類!
      28 嘅排除機制 = S3 每 deg 層一代表 (gcd8/gcd16 都 deg5, 撞層)
      唔係「鏈比較」問題 — Lucas>Fib 喺 gcd2 (14 vs 10) 冇被違反!
```

**更正**: Lucas 優先規則冇死亡——gcd16 排除係另一層機制 (deg 層)。

### 2. data-free 自動排除 21 (新!)

```
R5 候選入面 data 成員: 11 (1×L₅) 同 21 (3×L₄) — 兩個都唔係 magic!
data-free 規則 (R1) 自動除 21, 唔使新判準
```

### 3. 剩餘決策樹收窄

```
S1 生成 11 候選
S4 data-free: 除 11, 21 → 剩 9
S2 每 gcd 類一代表: gcd1{5,7,15}, gcd2{10,14}, gcd8{20}, gcd11{33}, gcd16{28}, gcd22{22}
S3 每 deg 層一代表: deg5 撞 (20 vs 28) → 前半優先? 20<22 ✓ / 28>22 → 收 20 除 28
S5 gcd1 鎖: {5,7,15} 唯一 Lucas∧質數 = 7
判準: gcd2 内 Lucas 鏈 (14) vs Fib 鏈 (10) → 14
最終: {7, 14, 20, 22, 33} = magic 5/5 ✓ (但部分係後驗拼湊!)
```

## 一刀切規則測試 (A–F 全 False)

| 規則 | 揀咗 | =magic? |
|:--|:--|:--|
| A gcd類+L鏈優先 | [7,11,14,22] | ❌ |
| B gcd類+最細m | [7,11,14,20,22,28] | ❌ |
| C gcd類+最大m | [14,20,21,22,28,33] | ❌ |
| D gcd類+dmod8=4 | [20,28] | ❌ |
| E gcd類+前半優先 | [7,11,14,20,22,28] | ❌ |
| F gcd類+非data+最細m | [7,14,20,22,28,33] | ❌ |

**冇單一規則一刀切** — 剩餘決策要靠 S3 deg 層 + S5 質數層, 後驗成份高, **唔可以閉合**。

## 開放項 (36 號後)

```
① gcd16 (28) 排除: S3 deg5 撞層 + 前半優先 — 後驗, 要盲測
② gcd2 (14 vs 10): Lucas 鏈優先 — 冇被 35 號推翻, 仍係候選
③ 28 = 4L₄ m=4 超 TEST F m≤3 窗口 — 定義問題 (窗口擴充 = 後驗改規則, 禁)
④ 完整程序決定性: 係 reach 到 5/5 但 6 規則 stacking, 過度吻合風險
```

## 判定

| 輪 | 結果 |
|:--|:--|
| 35 號「Lucas>Fib FAIL」 | **❗更正為誤報** — 機制唔同層 (gcd vs deg) |
| data-free 自動除 21 | ✅ 新確定性 |
| 完整程序 = magic 5/5 | 🟡 後驗拼湊, 未盲測, 唔可以閉合 |

## 檔案
```
36_anchor_chain_mapping.py       — 本輪 script
data/36_anchor_chain_mapping.json
```