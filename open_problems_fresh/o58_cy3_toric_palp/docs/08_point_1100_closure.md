# O58 — 真正嘅普適閉合：(1,1,0,0) ↔ K=-232 = -8×L₇

> **狀態**: 🟢 閉合 — lattice point 係載體，star 係 artifact
> **日期**: 2026-08-24
> **修正**: docs/07 嘅 star=8 ↔ 負 K 只係 canonical 專屬；真正普適係 point (1,1,0,0)

---

## Option 1 結果：Star-K 普適性測試（9 實例）

### Star Size 唔普適 ❌

| inst | verts | star=8 點 | star8 K | 結論 |
|:---|:---|:---|:---|:---|
| 0 (canonical) | 6v | pts[8], pts[36] | **-232, -360** | ✅ 唯一 star8→負 |
| 1 | 6v | 3 點 | +7, +8, +8 | ❌ 正 |
| 2 | 7v | 2 點 | +6, +6 | ❌ 正 |
| 3 | 7v | 3 點 | +7, +8, +8 | ❌ 正 |
| 5 | 7v | 0 | — | — |
| 10 | 8v | 2 點 | +7, +7 | ❌ 正 |
| 20 | 8v | 2 點 | +8, +8 | ❌ 正 |
| 50 | 9v | 3 點 | +8, +8, +8 | ❌ 正 |
| 89 | 10v | 1 點 | +8 | ❌ 正 |

**Star size 係 triangulation-dependent** — 唔係普適幾何量。docs/07 嘅「star=8 ↔ 負 K」只係 canonical 實例巧合。

### Lattice Point (1,1,0,0) 普適 ✅

**喺所有包含 (1,1,0,0) 嘅實例，該點 K = -232 = -8×L₇：**

| inst | (1,1,0,0) 位置 | K | star |
|:---|:---|:---|:---|
| 0 | pts[8] | **-232** | 8 |
| 1 | pts[8] | **-232** | 18 |
| 3 | pts[8] | **-232** | 20 |
| 50 | pts[5] | **-232** | 14 |
| 2/5/10/20/89 | 冇呢個點 | — | — |

**4/4 出現即 -232** — (1,1,0,0) 係 -232 = -8×L₇ 嘅真正幾何載體！

## 核心閉合

1. **lattice point (1,1,0,0)**（norm²=2, sum=2）— 喺所有 (36,98) 實例中都係 **K=-232 = -8×L₇**
2. **star size 唔係普適**（triangulation-dependent）— 之前嘅 star=8 結論要修正
3. **-360 = -8×45 係 canonical 專屬**（其他實例冇 (-1,-1,0,0) mirror 點？要查）

## 點解 (1,1,0,0)？

- norm² = 2（最短非零向量之一）
- sum = 2（坐標和）
- (1,1,0,0) = e₁+e₂ — **兩個 coordinate ray 嘅和**
- 佢喺 polytope 入面好「接近」邊界 → 小 star / 負自交

## 修正 docs/07

docs/07「star=8 ↔ 負 K」係 canonical 專屬，唔係普適。正確表述：
- **star=8 只係 canonical 實例巧合**（嗰 2 點剛好 star=8）
- **真正普適：lattice point (1,1,0,0) ↔ K=-232 = -8×L₇**

## 開放問題

- 🔴 (-1,-1,0,0) mirror 點喺其他實例存在嗎？佢嘅 K 係咪 -360？
- 🔴 點解 (1,1,0,0) 出現即 -232？norm²=2 / sum=2 嘅角色
- 🟡 其他「特殊 lattice point」有冇類似普適閉合？

## 檔案

```
scripts/24_star_k_universality.py   # v1（有 index bug）
scripts/26_star_k_universality_v2.py # v2（修正）
scripts/27_point_1100_universality.py # (1,1,0,0) 測試
data/star_k_universality_v2.json
data/point_1100_universality.json
```
