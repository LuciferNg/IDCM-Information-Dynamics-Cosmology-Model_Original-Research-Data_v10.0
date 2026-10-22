# O70 — 02: 155 Curves Kähler Cone 嵌入結構

> ⚠️ **歷史文件 (v1, 2026-08-31)** — §二「32 facets / 32 extreme rays」推論**已被 v2 推翻**。
> v2 正確結果: **46 條 facet-defining** (唔係 32), **3732 條 extreme rays** (唔係 32)。
> 詳細見 `docs/06_extreme_rays_v2.md`。§一核心發現 (155 ⊂ K 態) 仍然有效。

> **日期**: 2026-08-31
> **狀態**: 🟢 **Kähler cone 維度結構閉合** (v2 修正: 46 facets / 3732 rays)

---

## 一、核心發現

### Rank 結構

| 空間 | 維度 | 身份 |
|:-----|:----:|:------|
| 155 curves in 36D | **30** | 2L₅+2B = 22+8 |
| 155 curves in 32D | **29** | L₇ = 29 |
| 185 curves Q_ij in 32D | **32** | Full cone rank |
| 155 curves 嘅 32D 補集 | **3** | N_gen = 3 |

### 維度分析

```
36D (full Kähler moduli)
  ├── 32D divisor basis (present divisors [1,2,5,6,9..36])
  │    ├── 155 curves span 29D = L₇
  │    └── 30 extra curves add 3D = N_gen
  │         → 29 + 3 = 32 = full cone rank
  └── 4D missing divisors [3,4,7,8] = N_gen, B, L₄, 2B
       └── 155 curves span 4D there (full rank in missing)
            → 30 (36D) = 29 (32D) + 1 (from missing divisors)
```

### 29 = L₇

```
L₇ = φ⁷+φ⁻⁷ = 29
29 = 2L₅+2B-1 = 30-1
```

The 1 dimension lost when projecting from 36D to 32D is carried by the 4 missing divisors [3,4,7,8] = N_gen, B, L₄, 2B.

### 3 = N_gen

The 30 extra curves (185-155) add 3 = N_gen dimensions to reach full 32D rank.

---

## 二、Kähler Cone 結構推論

```
Kähler cone (32D) = 32 facets
  ├── 29 facets from 155 adjacency curves (sr_ideal complement)
  │    └── rank 29 = L₇
  └── 3 facets from 30 extra curves
       └── add 3 = N_gen dimensions
```

每個 facet 對應一條 curve 嘅 volume = 0 嘅 hyperplane。
Cone 嘅 32 個 extreme rays 係呢 32 個 facet 嘅交集。

---

## 三、意義

1. **155 條 curves 唔係 cone 嘅完整定義者** — 只貢獻 29/32 個 facets
2. **30 條額外 curves 貢獻 3 個 facets** — 對應 3 代 (N_gen=3)
3. **完整 Kähler cone 需要 185 條 curves 先定義到**
4. **155 = 2×73+9 係 sr_ideal 嘅圖結構**，唔係 cone 嘅 facet 結構

---

## 四、檔案

```
scripts/07_185_curves_analysis.py  ✅ 185 curves Q_ij rank 32
data/07_185_curves.json            ✅
```