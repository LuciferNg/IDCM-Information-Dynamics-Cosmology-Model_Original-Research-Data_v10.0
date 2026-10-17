# Magic Rows 規則盲測 — 26 (2026-10-17)

> **測試目標**: 25_magic_rows_open 嘅「結構閉合」有冇樣本外預言力?
> **方法**: zero-import, 預註冊規則 R1/R2/R3, closed-form + MC 10⁶ 雙軌, P13 交叉
> **Script**: `26_blind_test_magic_rows_rules.py` → `data/26_blind_test.json`

---

## 預註冊規則 (locked, 唔准事後改)

```
R1 data-free:  magic 代表 ∉ data rows {11,13,17,19,21,25}
R2 Lucas-chain: magic 代表 ∈ L* = {m·Lₖ : m∈{1,2,3}, Lₖ∈{1,2,3,4,7,11,18,29}}
R3 deg-cover:   magic 覆蓋 deg {40,20,5,2,4}, 缺 deg=10
```

## TEST A — Null 概率 (隨機每 gcd 類揀 1 代表)

| 測試 | closed-form | MC 10⁶ | 判定 |
|:-----|:-----------:|:------:|:----:|
| **A1 P(5/5 非 data)** | **0.375** | 0.375039 | 🔴 **FAIL** — data 只塞喺 gcd=1 (5/20) 同 gcd=11 (1/2) 類, 其它類 100% 非 data; 純巧合概率 37.5% |
| **A2 P(5/5 ∈ L*)** | **0.008** | 0.008288 | 🟡 **邊緣** — 0.8% 有訊號, 但未到 5σ (需 <3e-7); 每類獨立: gcd1=0.3, gcd2=0.4, gcd8=0.67, gcd11=1.0, gcd22=1.0 |
| **A3 deg-cover** | — | 0.0 | ⚠️ **表述修正** — gcd→deg 唔係單射 (gcd=8/16 都 deg5), deg_hist {40:1,20:1,10:1,5:2,4:1,2:1}; 「缺 deg10」啱一半: gcd=4 係 deg10 唯一來源 (全缺), gcd=16 係 deg5 第二來源冇代表 (唔係 deg 缺) |

## TEST B — P13 master_atlas 交叉

```
P13 Row label d (正側) = {7,14,20,22,33} = P9 magic 全同 ✅
physics label: -25 m_c/m_b, -21 m_s/m_d, -19 m_H/m_W, -17 m_mu/m_tau,
               14 c/s, 13 n/p, 11 m_W/m_Z (正負同號) — 全部對應 p9 data rows ✅
```
**注意**: P13 同 p9 分類**同源** (P13 就係最初 label 源頭) → 一致性成立, 但**唔算獨立盲測證據**。唔可以當 PASS 證據用。

## TEST C — 辨識力 (規則唯唔唯一鎖定 magic?)

```
R1+R2 篩完, 每 gcd 類 survivors:
  gcd=1: {1,3,7,9,29}  (5 個!)  ← 7 唔唯一
  gcd=2: {2,6,14,18}   (4 個)
  gcd=8: {4,36}        (2 個)
  gcd=11: {33}         ✓ 唯一
  gcd=22: {22}         ✓ 唯一
  total = 15 個候選 → 唔唯一鎖定 {7,14,20,22,33} ❌
```
**R1+R2 只係必要條件, 唔係充分預言規則**。gcd=1 類真 magic=7 喺 5 個 survivors 入面, 需要額外未預註冊判準 (質數? 3mod4? 最小>1?) 先鎖到——任何後驗加入都算 overfitting, 唔可以。

## ★ 結論 — 誠實標記

| 25 號主張 | 盲測裁決 |
|:---|:---|
| 「data-free 代表規則」閉合 | 🔴 **降級 FAIL** — null 37.5%, 冇統計強度; 保留做「觀察」唔係「規則」 |
| 「Lucas 鏈」閉合 | 🟡 **降級邊緣** — null 0.8%, 有訊號未到 5σ; 保留做「候選模式」 |
| 「缺 {4,16} = deg10 唯一缺類」 | ⚠️ **表述修正** — 「gcd 類缺 {4,16}」先啱 (deg5 唔缺: gcd=8 有代表) |
| "缺 gcd 類 {4,16} (七揀五)" | ✅ 維持 — 純結構事實, 唔係預言 |
| magic rows 本身 = {7,14,20,22,33} | ✅ 維持 (P13 一致) |

**判語**: magic rows 內部代表選擇規則**未閉合** — 現有 R1/R2 唔足以唯一鎖定, 需要新結構判準 (例如「7 = 唯一 Lₖ 質數且 3mod4」要等獨立盲測設計, 唔可以事後補)。25 號兩個「閉合」標記降級。

## 檔案
```
26_blind_test_magic_rows_rules.py   — 盲測 script (MC seed 固定可重現)
data/26_blind_test.json             — 完整輸出
```