# O70 — 155 Curves Facet 結構

> **開局**: 2026-08-31
> **狀態**: 🟢 **完滿閉合 v2 — 46 facets + 3732 exact extreme rays (2026-09-03 修正)**
> **來源**: O57 開放問題 #7 (docs/24)

## 完成

| 任務 | 狀態 | 詳情 |
|:-----|:----:|:------|
| 155 = 2×73+9 結構驗證 | ✅ | 73 = Nd+L₇ = 44+29, 9 = 3² |
| 52 nonzero = Nd+2B | ✅ | 44+8 |
| Rank 30 in 36D = 2L₅+2B | ✅ | 22+8 |
| Rank 29 in 32D = L₇ | ✅ | Loss of 1 via missing divisors |
| Q_ij rank 32 | ✅ | 185 curves full rank |
| Extra 3 = N_gen | ✅ | 30 extra curves add 3 dims |
| ★★ 155 curves ⊂ K 態 | ✅ | O57 docs/03 更正 |
| 6 null = 6 K states | ✅ | 精確對應 |
| 4 missing divisors [3,4,7,8] | ✅ | = N_gen, B, L₄, 2B |
| **★★ 46 facet-defining Mori rays** | ✅ **v2** | **185 入面只有 46 條真 facet-defining (139 redundant)** |
| **★★ 3732 exact extreme rays** | ✅ **v2** | **Sage PPL 24s 計算, 全部 rank-31 genuine 1-dim faces** |
| 舊 99 rays ⊂ 3732 | ✅ **v2** | 99/99 (舊集合只係 subset, 唔 complete) |

## ★★ v2 重大修正 (2026-09-03): 99 rays 唔 complete!

**舊結論** (08-31): "99 boundary rays (rank 32) = Kähler cone 充分必要包絡表徵"
**v2 發現**: 錯! 99 rays 只係 subset。

| 測試 | 結果 |
|:-----|:-----|
| C ⊆ K (99 rays ∈ cone) | ✅ PASS |
| **K ⊆ C (1000 random boundary points ∈ cone(99))** | **❌ FAIL** |
| Sage PPL (46 facets, 24s) | **3732 條 exact extreme rays** |
| 全部 3732 ∈ K (185 ieqs) | ✅ min −6.66e-16 |
| 全部 active rows rank = 31 | ✅ genuine 1-dim faces |
| 舊 99 ⊂ 3732 | ✅ 99/99 |

**卡死原因**: 185 條 Mori rays 有 **139 條 redundant** → 所有 DD 演算法 (CYTools/polymake/cddlib/PPL-185) 喺 32D 爆炸。移除 redundant 後剩 46 條, Sage PPL 24 秒完成。

## 46 條 facet-defining Mori rays 結構

```
indices: [15,16,20,23,26,27,29,34,37,40,42,47,53,54,62,63,68,70,71,76,79,80,87,
          97,100,101,106,112,113,116,135,136,143,148,154,157,158,160,165,168,169,
          172,174,175,178,183]
rank: 32 (full), 冇 collinear pairs
每條 sparse: 1-5 nonzero entries (median 4) — 典型 toric Mori generators
46/46 alignment 返 Q rows (= curve volume gradients)
```

## Extreme Rays 結構 (3732)

```
3732 = 2²×3×311 (冇直接 Lucas/Fib 結構)
active-facet 數分佈: 31:12, 32:24, 33:1240, 34:847, 35:654, 36:549, 37:180,
                     38:96, 39:54, 40:20, 41:16, 42:9, 43:22, 44:8, 45:1
全部 3732 條: active rows rank = 31 (genuine 1-dim faces)
facet size: 最少 950 (Mori 62), 最多 3731 (Mori 106)
```

## 檔存狀態 🟢 (v2)

**O70 完滿閉合 v2。** Kähler cone 完全表徵: 46 facet-defining inequalities → 3732 exact extreme rays (Sage PPL, exact rational)。

## 文檔
```
docs/01_155_structure_analysis.md  ✅ (結構)
docs/02_kahler_cone_embedding.md   ✅
docs/03_summary.md                 ✅
docs/04_cross_validation.md        ✅
docs/05_final_report.md            ✅ v2 更新
docs/06_extreme_rays_v2.md         ✅ NEW (2026-09-03)
01_problem_record.md               ✅ v2
SESSION_START.md                   ✅ v2
```


---

## ★★ O137 遺留攻堅輪交接註記（2026-09-25，append-only）

> 由 O137 `docs/36_gap_attack_round19.md` Round 19 之跨 O 審計建立。
> **本節唔改動上方任何內容。**

### 〇. 一句話

**O137 之「Mori cone 受阻」遺留（遺留 5）已被本 O（O70）閉合。**
O137 之阻塞係**方法問題**（`sc.rays()` 喺 C 擴展層阻塞），唔係根本不可得。

### 一. 閉合證據（本 O v2，2026-09-03）

```
★ 同一 polytope: o53_cy3_reality/data/polytopes/cy36_98_sage_export.json
   （O137 亦用此檔；md5 63536d17… 自 08-22 未改）
★ CYTools exact Mori cone: toric_mori_cone(in_basis=True) -> 185 exact integer rays
★ CYTools Kähler cone:     toric_kahler_cone() -> 185 hyperplanes
★ 46 facet-defining Mori rays（185 中 139 redundant）
★ 3732 exact extreme rays（SageMath 10.9 PPL，24s）
   全部 3732 ∈ K（185 ieqs，min −6.66e−16）；全部 active rows rank = 31
★ 舊 99 rays ⊂ 3732（99/99）— v1 結論「99 = 充分必要」已被本 O 自己推翻
```

### 二. 對 O137 之影響

```
🔴 O137 `docs/36` §十一「Mori rays 硬限時內未返回」之表述應理解為
   「cytools 之 sc.rays() / sc.extremal_rays() / ntfe_cones() 阻塞」，
   **唔等於**「Mori cone 不可得」。
   ⟹ O137 遺留 5 之 PF discriminant 路線應改由本 O 之 46 facet-defining rays 展開。
⚠️ O137 之 secondary cone 得 185 超平面（RR^37）— 與本 O 之 185 Kähler 超平面
   數字相同；**兩者是否同一物件待核**（維度約定唔同：O137 報 RR^37，本 O 報 32D）。
```

### 三. 相關 O（同輪建立）

```
O217 — 4-正則必要性（引用本 O 之 MaxCut / 阻挫結構？本 O 冇 MaxCut，見 O137 docs/32）
O221 — C_f 投影因子生成器（本 O 之 Q_ij 185×32 rank 32/32 為其輸入之一）
```

### 四. 狀態

```
[ ] 本節為交接註記，**唔代表本 O 有任何未完成工作**
     （本 O 狀態維持 🟢 完滿閉合 v2，見上方）
```
