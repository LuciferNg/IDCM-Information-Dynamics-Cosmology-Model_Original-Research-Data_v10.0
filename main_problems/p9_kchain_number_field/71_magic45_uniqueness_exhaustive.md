# Magic「唯一性 vs 方便性」終極判決 — 71 號 (2026-10-17)

> **背景**: 70 號留 gap——magic 係咪「唯一」同時過全部約束嘅 5-collection?
> **Script**: `71_magic45_uniqueness_exhaustive.py` → `data/71_magic45_uniqueness_exhaustive.json`
> **方法**: 窮舉全部 C(43,5)=962,598 個 5-collection, 過 4 閘

---

## 結果: **7/8 PASS (D3 判決 = magic 唔唯一, 誠實 FAIL)**

## ★★ 核心裁決

### Magic 唔係唯一 — 37 個 5-collection 都過晒 G1-G4 🔴

```
約束閘 (R5 程序各閘抽象):
  G1 gcd 類互斥: 5 個 gcd(|44−d|,176) 全部唔同
  G2 deg 層互斥: 5 個 deg(ω_d) 全部唔同
  G3 data-free: 唔含 DATA = {11,13,17,19,21,25}
  G4 3-anchor 可生成: ∃ 3-anchor (a,b,c) 使 G({a,b,c}; m∈{1,2,3,4}) ⊇ 呢 5 個

結果:
  過 G1+G2+G3: 9,625 個 (1.0% of 962,598)
  過 G1+G2+G3+G4: 37 個
  ★ magic {7,14,20,22,33} 只係 37 個之中一個 — 唔係唯一!
```

### 37 個過閘集合成員頻率 (揭示結構核心)

```
22: 31/37 (84%)   ← gcd22 唯一 gcd 類成員 (22 = μ² = 2)
33: 31/37 (84%)   ← gcd11 唯一 data-free 代表
 7: 23/37 (62%)   ← gcd1 Lucas 質數
40: 23/37 (62%)   ← gcd4 外圍
20: 17/37 (46%)   ← gcd8
28: 17/37 (46%)   ← gcd16
10: 13/37 (35%)   ← gcd2 Fib
14: 13/37 (35%)   ← gcd2 Lucas
30:  9/37 (24%)
 5:  4/37 (11%)
15:  4/37 (11%)
```

→ **結構強制嘅只有 22 (gcd22 類唯一) + 33 (gcd11 data-free 唯一)**；
其餘 3 個位置由 {gcd1,gcd2,gcd8/16/4} 類自由組合 —— 37 個變體。

## ★ 三層裁決總結 (70+71 合併)

```
「Magic 由結構唯一鎖定」claim — 🔴 撤回 (三判準全 FAIL):
  ① anchor 唔唯一: 3 個 cover triples (70 號)
  ② 5-collection 唔唯一: 37 個過晒 G1-G4 (71 號)
  ③ O-series 身份唔特別: 領域 91% 都有身份 (70 號)

仍企穩:
  ✅ 44-site R5 5/5 EXACT 程序 consistency (26 盲測預註冊 5/5)
  ✅ magic 結構 (5 gcd 類 + 5 deg 層) 比隨機稀有 47 倍 (p=2.1%)
  ✅ 22 + 33 喺 gcd 類結構上近乎強制 (84% 過閘集都含)
```

## 對「44 magic 獨特性支撐物理世界」嘅終極回應

```
如果「獨特性」指「magic 係唯一結構解」→ 🔴 唔成立 (37 個解)
如果「獨特性」指「magic 有完整 O-series identity」→ 🔴 領域 91% 都有
如果「獨特性」指「gcd/deg 層 cover 稀有」→ ✅ 成立 (2.1%, 但純結構,
  唔關物理/O-series)
唯一未被擊穿嘅: 「magic 5 個 = 完整程序 (S1-S5 含 Lucas/質數規則)
  嘅輸出」— 程序 consistency 真, 但程序規則本身後驗 (35 號 Q5 已審計:
  anchor 集後驗、乘數後驗、S2/S5 新規則)
```

## 誠實判讀

- 71 號唔係審計 35 號「錯」——35 號已自己標記 Q5 自由參數；
  71 號係補「唯一性 vs 方便性」gap, 結論 = 方便性 (37 個其中一個)
- R5 程序 (完整定義) 仍然 deterministic 輸出 magic;
  問題係「完整定義」有幾多後驗選擇 (anchor 3 解 + gcd2 14 vs 10 Lucas/Fib 優先)
- 唔推新結論; 只記錄 37 個事實

## Gap 剩餘

```
★ 37 個替代集合入面, 有冇其他都含有完整 O-series label 嘅 (9 個已知)?
  領域 91% ⟹ 幾乎肯定有 — 若確認, 「magic 身份完整性」都唔特別
  (未驗, 因領域率已 91% 斷定冇信息量)
```

## 檔案
```
71_magic45_uniqueness_exhaustive.py
data/71_magic45_uniqueness_exhaustive.json
```