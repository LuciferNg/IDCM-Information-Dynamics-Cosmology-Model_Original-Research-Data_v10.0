# R5 缺類必然性 + 88-site 前向預測 — 37 (2026-10-17)

> **目標**: 將「缺 {4,16}」昇做結構必然; 完整程序正式化; 88-site 前向
> **Script**: `37_r5_necessity_and_extension.py` → `data/37_r5_necessity_extension.json`
> **結果**: T1/T2 必然性 ✅; T3 程序唯一鎖 magic 5/5 EXACT ✅; **T4 88-site 前向部分 FAIL 🟡**

---

## T1 — 缺 gcd4 = 代數必然（唔係巧合）

```
anchor {5,7,11} × m ∈ {1,2,3,4} mod 8 = {1,2,3,4,5,6,7}  ← 永不出 0!
gcd4 候選 {8,16,24,32,40} 全部 ≡ 0 mod 8
⟹ R5 生成集 ∩ gcd4 = ∅  — 必要, 唔係揀出嚟
```

## T2 — 缺 gcd16 = 撞層機制

```
gcd16 = {12, 28}
12 唔喺 R5 生成集 (唔係 anchor×m≤4)
28 = 4×7 喺生成集, 但 deg(28)=5 = deg(20)
⟹ gcd8 20 / gcd16 28 撞 deg5 層 → S3 每 deg 層一代表 → 球半優先 → 20
```

## T3 — 完整程序 (兩階段) 唯一鎖定 magic 5/5 EXACT ✅

```
Phase A (類内): 生成 → data-free(44) → 每 gcd 類一代表
  S5 唯一 Lucas∧質數 (gcd1: {5,7,15} → 7)
  否則 Lucas 鏈優先 (gcd2: {10,14} → 14)
  單一候選直接收 (gcd8: {20}, gcd11: {33}, gcd16: {28}, gcd22: {22})
Phase B (跨類): 每 deg 層一代表, 撞層球半優先 (gcd8 20 vs gcd16 28 → 20)

輸出: [7, 14, 20, 22, 33] = magic 5/5 EXACT 一致 True
```

## T4 — 88-site 前向預測 = 樣本外部分 FAIL 🟡（誠實記錄）

```
88-site 程序輸出 = [7, 11, 14, 22, 28, 44] (6 代表)
gcd 類: gcd1{5,7,15,21}, gcd2{10,14}, gcd4{20,28}, gcd11{11,33}, gcd22{22}, gcd44{44}

magic↑88 = 7(gcd1), 14(gcd2), 20(gcd4), 22(gcd22), 33(gcd11)
程序喺 88-site 保留: 7, 14, 22 (3/5)
20 → 被 28 取代 (88-site 兩個都 gcd4! 撞層)
33 → 被 11 取代 (88-site 冇 data label, 11 未被排除)

★ 深入觀察: 
  44-site 缺類 gcd4 嘅「身份」喺 88-site 變成 magic 20 嘅歸屬類!
  (20 喺 44-site: gcd8; 喺 88-site: gcd4 — 缺類重組, 同 30 號「20↔24 補償」呼應)
```

## 裁決

| 項 | 結果 |
|:--|:--|
| T1 gcd4 缺 = 代數必然 (mod 8 指紋) | ✅ 閉合 |
| T2 gcd16 缺 = deg5 撞層 | ✅ 閉合 |
| T3 完整程序鎖 magic 5/5 | ✅ 44-site 唯一 (但規則由 magic 反推 — 後驗) |
| T4 88-site 前向 | 🟡 **部分 FAIL** — magic 3/5 保留, 20→28, 33→11 |
| 程序 scale-invariant? | ❌ 唔係 — R5 程序唔係 44-site 唔變量 |

## ★ 誠實標記

1. **T4 係樣本外盲測（部分）FAIL** — 唔可以因為 T3 靚就淨係講好消息
2. 解釋 T4 有兩條路: (a) magic rows 只屬 44-site 結構, 唔應推廣 (b) 88-site 欠 data label, 11 若係 data 則 33 保留 — **需要 88-site 自己 label 先知**
3. T3 程序 100% fit 44-site = 後驗 fit — 用戶批「後驗後補盲測」, T4 就係第一份樣本外報告, 結果係部分 FAIL
4. 「20 喺 88-site 屬 gcd4」同 30 號「20↔24 gcd8↔gcd4 補償」兩個觀察point去同一方向: **gcd4 嘅角色喺擴展下被重組**

## 檔案
```
37_r5_necessity_and_extension.py       — 本輪 script
data/37_r5_necessity_extension.json
```