# O70 v2 — Kähler Cone: 46 Facets + 3732 Exact Extreme Rays

> **日期**: 2026-09-03
> **狀態**: 🟢 v2 修正完成
> **觸發**: 用戶「繼續 O70 原本任務」→ 裝好 SageMath 10.9 後重跑 O57 #7 開放問題

---

## 一、背景

O70 v1 (08-31) 用 float LP 攞到 **99 boundary rays** (rank 32), 宣稱「充分必要包絡表徵」並歸檔。但驗證標準留低 🟡「36-dim cone extremal rays 需 convex hull (工具鏈問題)」。

用戶安裝 SageMath 10.9 就係為咗完成呢步。

## 二、v1 結論推翻過程

### 2.1 CYTools exact Mori cone (新 env 裝好全套依賴)

```
toric_mori_cone(in_basis=True) → 185 exact integer rays (32D)
toric_kahler_cone() → 185 hyperplanes
```

### 2.2 99 rays 完整性檢查 (script 24)

| 測試 | 方法 | 結果 |
|:-----|:-----|:-----|
| C ⊆ K | M·R ≥ 0 (185×99) | ✅ min −2.5e-11 |
| 全部 extreme | LP in_cone | ✅ 0 non-extreme |
| **K ⊆ C** | **300 random LP boundary points ∈ cone(99)?** | **❌ 4/300 FAIL** |

→ 99 rays **唔 complete**。有 Kähler cone 嘅點寫唔成 99 rays 嘅正組合。

### 2.3 Iterative walk (script 29, 31)

Fail points 嘅 active-set null space 迭代補漏:
- 23 rounds: 99 → **203** (script 29)
- 再補 8 rounds: 203 → **228** (script 31)
- 5000 random test 仍然 21 fail → **收斂極慢, 每次只搵到 2-5 條**

→ 呢個 cone 嘅 extreme rays 數目遠超 99/228, random walk 本質上唔 practical。

## 三、突破: Facet-defining 篩選 (script 32)

一條 Mori ray m_i 係 facet-defining iff:
```
∃ t: m_i·t = 0, m_j·t > 0 ∀ j≠i
= LP: max s s.t. M_{-i}·t ≥ s, m_i·t = 0, −1 ≤ t ≤ 1
```

**結果: 185 條 Mori rays 只有 46 條 facet-defining, 139 條 redundant!**

```
facet-defining indices:
[15,16,20,23,26,27,29,34,37,40,42,47,53,54,62,63,68,70,71,76,79,80,87,
 97,100,101,106,112,113,116,135,136,143,148,154,157,158,160,165,168,169,
 172,174,175,178,183]
```

46 條性質:
- rank 32 (full), 冇 collinear pairs
- 每條 1-5 nonzero entries (median 4) — 極 sparse toric generators
- 46/46 alignment 返 Q rows (curve volume gradients)

## 四、Sage PPL Exact Extreme Rays (script 33)

```python
Polyhedron(ieqs=[(0, *m) for m in Mf_46rows], backend='ppl')
→ 3732 rays, 24 秒完成
```

185 條 (139 redundant) → 跑 300-1000s 冇進展 (script 22/23 被 kill)
46 條 (乾淨) → **24 秒** ✅

## 五、完整驗證 (script 34, 38)

| 檢查 | 結果 |
|:-----|:-----|
| 全部 3732 ∈ K (185 ieqs) | ✅ min −6.66e-16 |
| Active rows rank | **全部 3732 條 = 31** ✅ (genuine 1-dim faces) |
| Extreme (抽樣 200) | ✅ 0 non-extreme |
| 舊 99 ⊂ 3732 | ✅ 99/99 |
| Active rows null space = ray | ✅ 38/38 抽樣 |

### Active-facet 數分佈

```
31:12, 32:24, 33:1240, 34:847, 35:654, 36:549, 37:180, 38:96, 39:54,
40:20, 41:16, 42:9, 43:22, 44:8, 45:1
```

(註: script 34 用「≥32」threshold 係錯 — 1-dim face 只需 rank 31, 即 ≥31 條 active rows 其中 31 條 independent。script 38 確認全部 rank=31。)

### Facet size (每條 facet 有幾多 extreme rays)

```
最少: Mori 62 → 950 rays
最多: Mori 106 → 3731 rays (即幾乎所有 extreme rays 都 active 喺呢條 facet)
```

## 六、方法論教訓 (可重用)

1. **Redundant constraints 係 DD 演算法殺手** — 先做 facet-defining 篩選 (LP per constraint), 可以將「卡死」變「24 秒」
2. **Random LP boundary 抽樣唔保證 complete** — 99 條 subset 被當成全集
3. **K ⊆ C containment 檢查** (random boundary ∈ cone) 先係完整性嘅判準
4. **CYTools Cone.extremal_rays() 警告** d>18 impossible — 但經 facet-reduction 後 Sage PPL 可行

## 七、檔案

```
data/22_mori_cone_rays_32d.npy         185×32 exact int (Mori generators)
data/22_Q_matrix_185x32.npy            185×32 (float gradient)
data/32_facet_defining_indices.npy     46 條
data/32_redundant_indices.npy          139 條
data/33_exact_extreme_rays_ppl.npy     3732×32 ← 最終答案
scripts/22-38                          全部探索 scripts
```

## 八、結構意義 (未解)

- 46 = Nd + 2 = 44 + 2? (自然但未證)
- 3732 = 2²×3×311 — 冇直接 Lucas/Fib 分解
- Extreme rays 嘅 IDCM 意義 (155 curves ⊂ K 態) 待後續
