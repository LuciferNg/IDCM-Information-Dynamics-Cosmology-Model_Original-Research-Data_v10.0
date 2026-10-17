# 88-site 物理 label 攻堅 — 46 號 (2026-10-17)

> **問題**: 37 T4 樣本外「88-site 冇 data label → DATA_N=∅ → 3/5 保留」
> **攻法**: 44-site 25 個 label 格全部 (i,j) ≤ 44 < 88 → 同座標存在於 88-site
> **Script**: `46_88site_labels.py` → `data/46_88site_labels.json`

---

## ★ T1 — label 格存在性（核心論證）

```
44-site 已知 25 格 (9 known + 9 dual + 7 near): 全部 (i,j) ≤ 44 < 88
⟹ 88-site 格空間包含全部 44-site label 格 — 同座標存在!
⟹ 「88-site 冇 data label」= 37 T4 嘅錯誤判斷
```

## T2 — data 6 行喺 88-site

```
d=11: (30,41) m_W/m_Z   → 88-site gcd=11
d=13: (7,20) n/p        → 88-site gcd=1
d=17: (1,18) m_μ/m_τ    → 88-site gcd=1
d=19: (19,38) m_H/m_W   → 88-site gcd=1
d=21: (1,22) m_s/m_d    → 88-site gcd=1
d=25: (8,33) m_c/m_b    → 88-site gcd=1
data-free 適用: 88-site 應照排 {11,13,17,19,21,25}
```

## ★★ T3 — 修正後 88-site 前向: **4/5**（唔係 3/5）

```
修正版 (data-free 適用): [7, 14, 22, 28, 33, 44]
  保留 magic = [7, 14, 22, 33] → 4/5 ✓
37 T4 原版 (DATA_N=∅):   [7, 11, 14, 22, 28, 44]
  保留 magic = [7, 14, 22] → 3/5
```

## T4/T5 — 取代機制修正

```
20→28 取代: 仍然 (Lucas 鏈優先 — gcd4 候選含 20=4F₅ Fib, 28=4L₄ Lucas → 28)
★ 33→11 取代: 撤銷 — 11 係 DATA row (m_W/m_Z label 格存在) → data-free 排 11 → 33 保留
  ⟹ 37 T4「33→11 取代」= DATA_N=∅ 嘅 artefact, 唔係結構
```

## T6 — 樣本外統計（保守）

```
44-site (in-sample): 5/5 保留
88-site (out-of-sample): 4/5 保留 (7,14,22,33) — 20 仍然失去
隨機期望: 6/87 ≈ 6.9% / magic — 4/5 遠高於隨機 🟡
保守標記: 樣本外預測改善, 唔當閉合
```

## T7 — 誠實缺口

```
1. label 格存在 ≠ label 完整: 88-site 可能仲有 d>44 額外物理格 (未掃, 禁止看目標凑算子)
2. data-free 適用性 = 座標存在性論證 — 冇 88-site 獨立 label 驗證
3. 4/5 vs 3/5 差異只影響「33 vs 11」— 11 本身就係 L₅ anchor
4. 最終裁決 = 等 88-site 獨立 label (P13/外部) 一致確認
```

## 裁決

| 項 | 結果 |
|:--|:--|
| 88-site label 資格 | ✅ 25 格同座標存在 — data-free 適用 |
| 樣本外 magic 保留 | ✅ **4/5** (7,14,22,33) — 修正 37 T4 嘅 3/5 |
| 20→28 取代 | ✅ 仍然 (Lucas 鏈優先, 結構) |
| 33→11 取代 | ✅ 撤銷 (artefact) |
| 樣本外統計 | 🟡 4/5 保守 — 唔閉合 |
| R5 程序 scale 穩健性 | 🟡 提升: 5/5 → 4/5 (唯一失去 = 20, 因為 88-site gcd4 撞層) |

## 誠實標記

1. 呢個係**修正**（37 T4 嘅 DATA_N=∅ 決定被推翻），唔係新推導——37 T4 記錄保持原樣, 以本輪附註為準
2. 4/5 樣本外仍唔係閉合——R5 程序喺 88-site 失去 20（gcd4 由 20 變 28），唔係 perfect
3. 「同座標 label 遷移」係一個假設（label 跟格座標走, 唔跟 d 類走）——有 25 格支持, 冇獨立驗證

## 檔案
```
46_88site_labels.py       — 本輪 script
data/46_88site_labels.json
(R5 程序 88-site 樣本外: 3/5 → 4/5 更新)
```