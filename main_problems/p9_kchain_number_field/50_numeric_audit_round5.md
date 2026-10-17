# 第五輪數字審計 — 50 號 (2026-10-17)

> **範圍**: 30_mirror_exclusion / 31_matrix_fixed_point / 32_column_isomorph_contact
> **Script**: `50_numeric_audit_round5.py` → `data/50_numeric_audit_round5.json`
> **紀律**: 零 import; 第一原理重算; mpmath 精確; §4.7 有罪推定 (審計員 check bug 優先)

---

## 結果: **35/36 PASS, 1 FAIL（真 script bug）**

```
A (30): A1 七類大小 / A2 鏡像流向 / A3 R4a 出走 / A4 R4c 鎖7 / A5 盲測 P=0.6999 / A6 33↔11+20↔24+22自鏡像
B (31): B1 8 operator 固定表 / B2 Galois {1,87} / B3 gcd_shift / B4 script 條件
C (32): C1 deg 分佈 / C1b 每層一 magic / C2 端點×magic / C3 7 位置 / C4 14 冇端點
```

### ✅ PASS (35)

| 項 | 內容 |
|:--|:--|
| A1 | gcd 七類 {1:20, 2:10, 4:5, 8:3, 11:2, 16:2, 22:1} ✅ |
| A2 | gcd4→{8:3,16:2}, gcd16→{4:2}, gcd8→{4:3} ✅ |
| A3 | 冇 magic 類=[4,16]; 全出走=[4,8,16]; 出走但有 magic=[8]（R4a 必要唔充要）✅ |
| A4 | 3/7/29 伴侶全 filler → R4c 分唔開 ✅ |
| A5 | 盲測 P=0.6999 (10⁶, seed 固定) ✅ |
| A6 | 33↔11, 20↔24, 22↔22, gcl(22)=22 ✅ |
| B1 | 8 op 全對: T1 trivial 43, T2/T3/T5/T6 唯一 magic=22, T4/T7 冇 ✅ |
| B2 | Galois d=3/7/29 → {1,87}; σ_87 固定全部奇數、唔固定任何偶數 ✅ |
| B3 | gcd_shift 保持 gcd1 嘅 k 只有 {43} (trivial) ✅ |
| C1 | deg 分佈 {40:20, 20:10, 10:5, 5:5, 4:2, 2:1, **0:1**} ✅ (含 n=44=ω₄₄ deg0) |
| C1b | 每 deg 層一 magic (deg10 缺, deg0=44 冇 magic) ✅ |
| C2 | data 格端點: (7,20)[7,20] / (8,22)[22] / (19,33)[33] / (1,22)[22] / (8,33)[33] ✅ |
| C3 | 7 = 第 4/20 位; 第一 Lucas 質數 = 3 ✅ |
| C4 | magic 只有 14 冇做 data 端點 ✅ |

### 🔴 FAIL (1) — 真 script bug: 31 號 Galois 條件

```
31 script galois_fixed() 用:  (a·d) mod 176 ∈ {d, 176−d}
    ⟺ σ_a(ω_d) = ±ω_d (鏡像條件, 唔係固定!)
    → 原 JSON sample = [1, 175]
正確固定條件:  a·d ≡ d (mod 176) 或 d(a+1) ≡ 88 (mod 176)
    → d=3/7/29 全 = {1, 87}  ← 31 md 正文啱
脚本值 vs md 值唔一致 = script bug; md 敘述正確
★ 結論不變: script 錯值 {1,175} 同正確值 {1,87} 都係 3/7/29 全同
   ⟹ 「σ_87 固定全部奇數, 唔係 7 特有」結論穩健
→ 31 md 已加 append-only 更正附註（script 要修正先可以重用）
```

### ★ 真 doc 錯 ×1（審計員自我檢查後確認方向）

```
32 md §T2/T3: 「6 格有 magic 端點，7 次命中」= 錯
實際: 5 格 6 次命中  ((7,20)=2hits + (8,22)+(19,33)+(1,22)+(8,33)=4×1hit)
→ 32 md 已加 append-only 更正附註（結論不變: (7,20) 仍唯一全 magic 端點格）
→ 數字修正: 6/9→5/9, 7→6
```

### ★ 審計員 check bug ×2（有罪推定程序）

```
C1 初始期望漏 deg0 (n=44, ω₄₄=2 有理點, gcl=176, om_deg=0)
   → 正確期望 = {40:20,20:10,10:5,5:5,4:2,2:1,0:1}
C2 初始期望「6/9 格有 magic 端點」照抄原 doc
   → 逐格重數 = 5/9 格 → 確認原 doc 錯 (唔係我會錯)
```

## 裁決

| 項 | 結果 |
|:--|:--|
| 30 號數字 | ✅ 全 PASS |
| 31 號數字 | ✅ 主體 PASS; **script Galois 條件 bug** (md 啱) |
| 32 號數字 | ✅ main PASS; **1 真 doc 錯** (6格7次→5格6次, 已更正) |
| 審計員 check bug | ✅ C1 期望修正 (deg0) |
| 推導結論穩健性 | ✅ 全部結論不受影響 |

## 審計員自查清單

```
▪ 39/36 初始 expect 漏洞: C1 漏 deg0 → 已修
▪ 發現「原 doc 6/9 7次」有問題時第一反應係自己會錯 → 逐格手數確認 = 真 doc 錯
   （§4.7 有罪推定: 審計員 bug 優先）
```

## 誠實標記

1. B4 係「script 執行值 vs md 敘述值」不一致 — 已確認 md 數學啱 (`d(a+1)≡88` 先係 σ(ω)=ω)
2. 31 script 唔可以重用直到修正 galois_fixed 條件 — 保持 ⚠️ 標記
3. 32 md 更正係數字層 (5/9, 6次) — 結構結論全部不變

## 檔案
```
50_numeric_audit_round5.py
data/50_numeric_audit_round5.json
31_matrix_fixed_point.md   — ⚠️ append-only 更正 (Galois 條件)
32_column_isomorph_contact.md — ⚠️ append-only 更正 (5格6次)
```