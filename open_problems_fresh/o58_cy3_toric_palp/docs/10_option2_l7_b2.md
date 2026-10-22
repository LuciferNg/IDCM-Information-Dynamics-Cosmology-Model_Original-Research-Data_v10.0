# O58 — Option 2：45 = L₇ + B² 嘅鏡像對稱破缺機制

> **狀態**: 🟡 部分閉合 — 加性結構確認，機制待深挖
> **日期**: 2026-08-24

---

## 修正後嘅正確 picture（index-fix 後）

### 特殊 divisor 對 (0, 8)

| divisor | pts | K_{iii} | -K/8 | 身份 |
|:---|:---|:---|:---|:---|
| **0** | origin (ray 0, sum -742) | **-360** | **45** | 特殊 non-coordinate ray |
| **8** | (1,1,0,0) (ray 8, sum +733) | **-232** | **29** | 特殊 non-coordinate ray |
| 36 | (-1,-1,0,0) | +8 | — | 普通（唔係 -360！） |

### 加性閉合

```
45 = L₇ + B² = 29 + 16
-360 = -8×45 = -8×(L₇+B²) = -232 - 128 = -8L₇ - 8B²
128 = 8B² = 2⁷
```

**divisor 0 嘅 -K/8 = 45 係 divisor 8 嘅 -K/8 = 29 加上 B²！** 兩個特殊 ray 嘅 self-intersection 有精確嘅加性結構。

### Z₂ Mirror 嘅真正角色

**之前 docs/07 講嘅「(1,1,0,0) ↔ (-1,-1,0,0) mirror 對」係 index-shift artifact** — (-1,-1,0,0) 實際 K=+8，唔係 -360。

**真正嘅「mirror 對」係 ray 0 ↔ ray 8**（GLSM sum: -742 vs +733），佢哋嘅 K_{iii} 分別係 -360 同 -232，而 -K/8 = 45 = 29 + 16。

### 點解 45 = L₇ + B²？

45 = Σγ/2（K_Chain 44-site 全譜和的一半）
29 = L₇（Lucas）
16 = B²（K_Chain boundary × 2 嘅平方）

**即係 divisor 0 編碼「全譜」Σγ/2，divisor 8 編碼「Lucas 階梯」L₇，兩個加埋 B²。**

## 誠實評估

- ✅ 加性結構 45 = 29 + 16 精確成立（數值）
- ✅ (1,1,0,0) ↔ -232 普適（4/4 實例）
- 🟡 divisor 0 嘅 -360 喺其他實例係咪都係 -8×45？（未驗證）
- 🔴 點解 ray 0 同 ray 8 有呢種加性？機制未明

## 開放問題

- 🔴 divisor 0（ray 0）嘅 -360 喺其他 (36,98) 實例係咪都係 -8×45？
- 🔴 45 = L₇ + B² 嘅幾何根源（Z₂ 破缺？）
- 🟡 ray 0 / ray 8 喺 GLSM 嘅角色（q₃=6 對應？）

## 檔案

```
scripts/25_option2_asymmetry.py
scripts/28_mirror_points_universality.py
docs/09_index_fix_and_closure.md  # index 修正
```
