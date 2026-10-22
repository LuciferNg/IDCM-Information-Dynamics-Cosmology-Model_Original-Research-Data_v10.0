# O58 — Index 修正 + 真正普適閉合：(1,1,0,0) ↔ -232 = -8×L₇

> **狀態**: 🟢 修正完成
> **日期**: 2026-08-24
> **嚴重性**: 🔴 修正 docs/01-08 嘅 index 錯誤

---

## CYTools intersection_numbers() Index Convention（重要！）

**CYTools `cy.intersection_numbers()` 返回 0-based divisor index（0..36），divisor d ↔ pts[d]**（pts[0] = origin，pts[1..37] = rays + interior points）。

```
intersection (8,8,8) = -232  → divisor 8 = pts[8] = (1,1,0,0)
intersection (0,0,0) = -360  → divisor 0 = pts[0] = origin (特殊 convention)
intersection (36,36,36) = 8  → divisor 36 = pts[36] = (-1,-1,0,0)
intersection (1,1,1) = 4     → divisor 1 = pts[1] = (1,0,0,0)
```

**之前 docs/01-08 錯咗**：用 `K[i-1,j-1,k-1]`（假設 1-based + 再 shift）— 錯 mapping。

## 修正後嘅真確結果

### 真正普適閉合（Option 1 ✅）

**lattice point (1,1,0,0) ↔ K = -232 = -8×L₇（L₇=29）— 4/4 實例確認！**

| inst | (1,1,0,0) 位置 | K | star |
|:---|:---|:---|:---|
| 0 | pts[8] | **-232** | 8 |
| 1 | pts[8] | **-232** | 18 |
| 3 | pts[8] | **-232** | 20 |
| 50 | pts[5] | **-232** | 14 |

**冇 (1,1,0,0) 嘅實例（2,5,10,20,89）都冇 -232** — 完美對應！

### 撤回（index-shift artifacts）

- ❌ **「divisor 36 = (-1,-1,0,0) 有 K=-360」** — 實際 +8
- ❌ **「K[0,0,35] = -44」** — 實際係 (0,1,1) = -44（divisor 0 × divisor 1²）
- ❌ **「Z₂ mirror 對 29/45」** — (-1,-1,0,0) 唔係 -360
- ❌ **「star=8 ↔ 負 K」** — 只係 canonical 巧合

### 真正負對角 divisor（0-based）

| divisor | pts | K | 值 |
|:---|:---|:---|:---|
| 8 | (1,1,0,0) | **-232** | **-8×L₇** ✅ |
| 12 | (-23,-15,-6,-2) | -5 | — |
| 17 | (-11,-6,-3,-1) | -5 | — |
| 0 | origin (特殊) | -360 | -8×45（但係 divisor 0 特殊，唔係 Z₂ mirror） |

## 修正後嘅完整 picture

1. **(1,1,0,0) ↔ -232 = -8×L₇：真實普適閉合**（4/4 實例，幾何載體 = lattice point）
2. **-360 = -8×45 係 divisor 0**（origin 特殊 divisor）— 意義待查，唔係 mirror 對
3. **star size 唔普適**（triangulation-dependent）— 只係 canonical 巧合
4. **HF swap 發現完全獨立，仍然成立** ✅（docs/04, 06 不受影響）

## 開放問題

- 🔴 divisor 0（origin）嘅 -360 = -8×45 幾何意義？（45 = Σγ/2 = N_d+1）
- 🔴 點解 (1,1,0,0) 出現即 -232？norm²=2 / sum=2 嘅角色
- 🟡 (-1,-1,0,0) mirror 點 K=+8 嘅意義

## 檔案

```
scripts/21-23             # 舊（index 錯）
scripts/24-28             # Option 1+2（v2 修正後正確）
docs/07_star_k_closure.md # ⚠️ 部分撤回（star=8 部分）
docs/08_point_1100_closure.md # ✅ 正確（(1,1,0,0) 閉合）
```
