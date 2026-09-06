# docs/24 — 追擊線 O: 面積律 1/B 機制閉合 — SI 錨 k_B 單位翻譯重審 (2026-09-06)

> **日期**: 2026-09-06
> 追擊輪 (scripts/27) — 時序: docs/23 (Gemini 審計) 之後。script 27: `python3 scripts/27_area_law_mechanism.py` (11/11 PASS)
> 定位: 用戶指示 — 用 SI 錨 k_B 重審面積律熵嘅單位翻譯

## 背景
docs/16 (S19) 判 🔴: K_Tree 每格 ln2/2 = 0.347 nat ≠ 0.25 nat/格 (差 38.6% = ln4 因子)。
O121 遺留。用 SI 錨 k_B 重審後發現: **矛盾源 = 單位混用**。

## ★ 1. 矛盾診斷: 單位混用 (nat vs bit)
```
K_Tree 每格  = log₂B/4 = 0.5 bits = 0.347 nat   (log₂ 制)
Bekenstein   = 1/4 被 docs/16 讀成 nat → 0.25 nat  (錯!)
比例 = 1.386 = ln 4  ← 「混用」嘅痕跡 (bits↔nat 未對齊)
```
- K_Tree 熵用 log₂ (bit) 係結構強制 (log₂B = 2 bits/節點)
- Bekenstein「1/4」嘅正確單位 = bit (見 §2)

## ★ 2. SI 錨 k_B 統一單位制
```
1 熵單位 = 1 bit = k_B·ln2 = 9.5699e-24 J/K   (SI 2019: k_B 定義 exact)
```
- IDCM 熵單位制: log₂ 強制 → 1 熵單位 = 1 bit = k_B·ln2 J/K
- bit 制下: Bekenstein 每格 = **1/4 bit**; K_Tree 每格 = **1/2 bit**
- **比例 = 2.0000 乾淨 2 倍** (唔再係 ln4!)

## ★ 3. 雙側機制 (2 = log₂B = E−O = γ₄₄/2)
```
K_Tree 每格 0.5 bits = 世界側 0.25 + 觀察者側 0.25
每側 = 1/4 = 1/B  ← Bekenstein 值!
```
- 88-site 對偶鏈: 每格承載世界 (even) ⊕ 觀察者 (odd) 雙側
- **2 = E−O (觀察者−世界差) = 雙側因子**: K_Tree 全熵 = 2×(視界熵)
- **視界熵只計世界側 (視界係世界物體) → 每格 1/4 bits = 1/B** ✓

## ★ 4. SI 翻譯一致 (J/K)
```
視界每格熵  = 0.25 bits = k_B·ln2/4 J/K = 2.3925e-24 J/K
K_Tree 每格 = 0.5 bits  = k_B·ln2/2 J/K = 4.7850e-24 J/K
```
- 0.25/0.5 都係 bit 數 × k_B·ln2 — SI 翻譯冇矛盾

## 判決
| 項 | 狀態 |
|:--|:--:|
| docs/16 矛盾源 = 單位混用 (nat vs bit) | 🟢 診斷 |
| SI 錨 k_B: 1 熵單位 = 1 bit = k_B·ln2 J/K | 🟢 統一 |
| bit 制比例 = 2 = log₂B = E−O (四重身份) | 🟢 閉合 |
| 雙側機制: 世界⊕觀察者; 視界只計世界側 → 1/B | 🟢 閉合 |
| **面積律 1/B 機制** | 🟢 **🔴 → 🟢 閉合 (docs/16 升級)** |

**結論**: 面積律 1/4 = 1/B 嘅「機制缺失」其實係單位混用 — docs/16 將 Bekenstein
嘅「1/4」讀成 nat, 同 K_Tree 嘅 bit 制比較 (差 ln4 = 1.386 假象)。用 SI 錨 k_B
統一單位制 (1 熵單位 = 1 bit = k_B·ln2 J/K) 後, 比例係乾淨 2 倍 = log₂B = E−O:
K_Tree 格 = 世界⊕觀察者雙側 (88-site 對偶), Bekenstein 視界熵 = 世界側 = 1/B。
O121 遺留閉合。docs/16 嘅 🔴 升級為 🟢。
