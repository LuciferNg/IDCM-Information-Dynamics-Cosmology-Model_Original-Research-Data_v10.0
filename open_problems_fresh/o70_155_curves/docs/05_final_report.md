# O70 — 155 Curves Facet 結構分析報告

> **日期**: 2026-08-31 (v1), 2026-09-03 (v2 修正)
> **狀態**: 🟢 **完滿閉合 v2 — 46 facets + 3732 exact extreme rays**
> **前置**: O57 docs/02-03 (155 curves), O57 docs/24 (開放問題 #7)
> **腳本**: scripts/01-39
> **歸檔**: 2026-08-31, **2026-09-03 v2 修正 (99 → 3732)**

---

## 一、核心結構：155 = 2×73+9 ✅

| 項 | 值 | 公式 | 驗證 |
|:---|:---|:-----|:----:|
| 155 | C(36,2) − 475 | 630 − 475 | ✅ 20/20 |
| 73 | Nd + L₇ | 44 + 29 | ✅ |
| 73 | L₆×4+1 | 18×4+1 | ✅ |
| 9 | 3² = N_gen² | 9 duplicate sr_ideal entries | ✅ |
| 5 | unique duplicate pairs | (1,6)×2, (6,15)×2, (6,17)×3, (10,12)×3, (12,14)×4 | ✅ |

## 二、58 條零體積 Curves = Nd + 2B ✅

- 52/155 nonzero volume vectors (Nd+2B = 44+8)
- 103 zero volume vectors (155−52)
- 4 missing divisors: [3, 4, 7, 8] = N_gen, B, L₄, 2B

## 三、Rank 結構 ✅

| 空間 | 維度 | 身份 | 公式 |
|:-----|:----:|:-----|:-----|
| 155 curves in 36D | **30** | 2L₅+2B | 22+8 |
| 155 curves in 32D | **29** | L₇ | 29 |
| 185 curves Q_ij | **32** | full rank | 32 |
| Extra (185-155) | **3** | N_gen | 3 |

Loss from 36D → 32D: **1** (due to 4 missing divisors [3,4,7,8])

## 四、★★ O57 更正：155 curves ⊂ K 態 ✅

**O57 docs/03 錯誤聲明：**「155 curves rank 30 = 2L₅+2B = C sector」
**實際：** 155 curves ⊂ **K 態空間**

| 測試 | 結果 | 含義 |
|:-----|:----:|:------|
| C 態投影到 155 curves | **0.0000** | 完全正交 |
| K 態投影到 155 curves | **0.961** mean | 強重疊 |
| 6 null directions ↔ K 態 | 6/6 overlap | 精確對應 |

## 五、Kähler Cone 表徵 ✅

**方法 A (LP min c·t, Σt=1):** 99 unique boundary rays, **full rank 32**
**方法 B (Active Set Refinement):** 75 unique rays, rank 30 (一致)

| 性質 | 值 |
|:-----|:----:|
| 維度 | 32 |
| 不等式 | 185 (Q @ t ≥ 0) |
| Boundary rays | 99 (rank 32) |
| Active constraints/ray | mean 106, range 76-174 |

## 六、Curve 數量對照

| 類型 | 數量 | 來源 |
|:-----|:----:|:------|
| Adjacency curves | 155 | sr_ideal complement |
| CYTools curve_basis | 32 | Mori cone generators |
| Total curves | 185 | compute_curve_volumes() |
| Extra curves | 30 | 185 − 155 |

## 七、★★ v2 修正 (2026-09-03): 99 → 3732 extreme rays

**v1 結論「99 boundary rays = 充分必要包絡表徵」係錯 — 99 只係 subset。**

| v2 發現 | 值 |
|:---|:---|
| 185 Mori rays 入面 facet-defining | **46 條** (139 redundant — DD 卡死元兇) |
| Sage PPL (46 ieqs, 24s) exact extreme rays | **3732 條** |
| 全部 ∈ K (185 ieqs) | min M·r = −6.66e-16 ✅ |
| 全部 active-rows rank | 31 ✅ (genuine 1-dim faces) |
| 舊 99 ⊂ 3732 | ✅ 99/99 |
| active-facet 分佈 | 31:12 ... 45:1 (詳見 docs/06) |

**方法論教訓**: 先做 facet-defining 篩選 (LP per constraint) 消除 redundant, DD 由「卡死」變「24 秒」。詳見 `docs/06_extreme_rays_v2.md`。

## 八、歸檔 🟢 (v2)

**O70 完滿閉合 v2!** Kähler cone 完全表徵: 46 facet-defining inequalities → **3732 exact extreme rays** (Sage PPL, exact rational, 24 秒)。

## 九、檔案

```
open_problems_fresh/o70_155_curves/
├── 01_problem_record.md        ✅ v2 (46 facets + 3732 rays)
├── SESSION_START.md            ✅ v2
├── scripts/
│   ├── 01-05: 結構驗證         ✅ 全部 PASS
│   ├── 06-11: Cone 方法探索    ✅ 比較完成
│   ├── 12-14: Extreme rays     ✅ LP 成功
│   ├── 15: 交叉驗證            ✅ 5 方法對比
│   ├── 16: 最終驗證            ✅ v1 20/20 PASS
│   ├── 22-31: Extreme ray walk 探索 (99→203→228, 唔 complete)
│   ├── 32: Facet-defining 檢查 ✅ 46/139
│   ├── 33: Sage PPL extreme rays ✅ 3732 (v2 核心)
│   ├── 34-38: 驗證 + 結構分析  ✅
│   └── 39: 獨立完整驗證        ✅ 21/21 PASS
├── data/
│   ├── 15_all_rays.npy         ✅ 99 boundary rays (v1, subset)
│   ├── 22_mori_cone_rays_32d.npy ✅ 185×32 exact int Mori generators
│   ├── 32_facet_defining_indices.npy ✅ 46 條
│   ├── 32_redundant_indices.npy      ✅ 139 條
│   └── 33_exact_extreme_rays_ppl.npy ✅ 3732×32 ← v2 最終答案
└── docs/
    ├── 01_155_structure_analysis.md  ✅
    ├── 02_kahler_cone_embedding.md   ✅
    ├── 03_summary.md                 ✅
    ├── 04_cross_validation.md        ✅
    ├── 05_final_report.md            ✅ v2
    └── 06_extreme_rays_v2.md         ✅ v2 (NEW, 完整報告)
```