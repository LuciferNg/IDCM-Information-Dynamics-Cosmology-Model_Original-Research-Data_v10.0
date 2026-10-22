# NN_results — O28: Planck gp10 冷斑 mask 校正

> **判定**: 🔴 **gp10 冇節點對應** — 校正後仍然 10°+ (實際更遠 19°+)
> **日期**: 2026-08-21
> **Verifier**: 20/20 PASS (scripts/05_verify.py) + 32/32 PASS (scripts/06_doc_verify.py)
> **覆蓋率 audit**: 2026-08-21 — 全部發現/計算/驗證已核對寫入 (詳見 §7)

## 核心發現

### 1. gp10 喺 SMICA 中尺度唔係冷斑 ❌

Flood-fill (spherical BFS, threshold ±1.5σ, search radius 25° around (32,-8), nside=1024):

| FWHM | 4.17° | 5.0° | 7.0° |
|:----:|:-----:|:----:|:----:|
| 冷 comps (bcut 5/10/15/20) | **0 / 0 / 0 / 0** | 0/0/0/0 | 0/0/0/0 |

- 只有 3.0° 搵到 comp，peak 喺 **(22.4,-25.0)** — 距離 gp10 中心 ~20°，係另一個結構 (唔係 gp10)
- gp10 中心 (32,-8) 喺 4.17° = **+10.4 μK 微熱**，radial profile 0-30° 全部偏熱 (+20~+27 μK)

### 2. Planck Nside=16 統計重現失敗 ❌

Planck 2013 用 Nside=16 分析 gp10 (fsky=7%) 話 high variance + negative skewness (cold spot)。SMICA 4.17° → Nside=16 重現:

| 統計量 | gp10 區域 (r=30°, 205 pix) | 其餘天空 (|b|≥25°) |
|:------|:--------------------------:|:------------------:|
| variance | 1081 | 1452 (**0.75×, 唔係高 variance**) |
| skewness | **+0.12** (正偏, 唔係負偏) | -0.15 |
| mean | +22.9 μK | +0.3 μK |

⚠️ 誠實註記: Planck 用嘅 gp10 區域形狀同 mask 唔完全等同 r=30° cap；呢個係近似重現。但喺 SMICA 中尺度完全搵唔到負偏/高 variance 嘅冷斑特徵。

### 3. 0.5° 細尺度 -215 μK peak = 前景/緊湊結構, 唔係 gp10 冷斑

- 0.5° smoothing: peak **(32.4,-5.5) = -215.0 μK** (距離 gp10 中心 2.5°)
- 但喺 4.17° 同一位置三地圖一致只有 -9 ~ -17 μK (SMICA -12.3 / NILC -9.0 / Commander -17.2)
- 振幅從 -215 → -12 μK 崩潰 = **緊湊小尺度結構** (前景或小 CMB 漲落)，唔係 Planck 講嘅大尺度冷斑
- 唔影響結論: 呢個位置距離任何節點 > 9.7°

### 4. Mask 校正後冷 centroid 移離節點 ❌

SMICA 4.17°, r≤15°, 冷像素 (T<0) centroid:

| |b| cut | centroid | 最近節點 |
|:------:|:--------:|:--------:|
| ≥5° | (38.9, -11.9) | node21 17.9° |
| ≥10° | (38.4, -16.1) | node21 19.7° |
| ≥15° | (37.5, -18.9) | node22 18.1° |

**Mask 校正唔係令 gp10 接近節點，而係推得更遠** (10° → 18-20°)。

### 5. 隨機對照: 10.05° 完全正常 ✅

| 對照 | 中位數 | P(nearest ≤ 10.05°) | P(nearest ≤ 5°) |
|:-----|:------:|:-------------------:|:---------------:|
| 銀河面條帶 |b|<20° | 10.32° | **0.477** | 0.117 |
| 全天 | 10.52° | 0.454 | 0.113 |
| gp10 30° 內 | 10.60° | 0.447 | 0.089 |

- gp10 最近節點 10.05° (node21) — **一半隨機位置都係咁**，冇任何異常
- P(nearest ≤ 5°) ≈ 0.09-0.12 — 節點網格喺銀河面附近稀疏係正常

## 節點角色最終表

| 節點 | 距離 gp10 | T (4.17°) | 角色 |
|:----:|:---------:|:---------:|:-----|
| node21 | 10.05° | **+95.5 μK 熱** | 最近但熱 — 唔係冷對應 |
| node26 | 20.25° | -48.3 μK | 微冷但距離遠, mask 校正後更遠 (23°) |
| node22 | 24.02° | -23.6 μK | 微冷但距離遠, 唔喺 gp10 範圍 |

### Radial profile 補充 (SMICA 4.17°, gp10 中心向外)

| 環帶 | mean ± std (μK) | n |
|:----:|:---------------:|:--:|
| 0-5° | +24.7 ± 24.5 | 95,769 |
| 5-10° | +25.5 ± 36.4 | 286,556 |
| 10-15° | +25.4 ± 40.7 | 475,178 |
| 15-20° | +26.9 ± 39.7 | 660,185 |
| 20-25° | +20.6 ± 33.0 | 840,146 |
| 25-30° | +20.9 ± 30.3 | 1,013,757 |
| 30-35° | +3.0 ± 35.8 | 1,179,581 |

→ gp10 中心 0-30° 全部偏熱 (+20~+27 μK)，冇任何冷結構信號。

## 判定

```
🟢 校正後中心 < 5° 某節點 → 第二冷斑命中   ❌ 唔成立
🔴 校正後仍然 10°+ → gp10 冇節點對應     ✅ 成立 (10.05° → 校正後 18-20°)
🟡 node26/22 喺邊緣 → 部分對應            ❌ 唔成立 (校正後 centroid 移離佢哋)
```

**O28 判定: 🔴 gp10 冇節點對應**

## 驗證紀錄 (2026-08-21 close-out audit)

| Verifier | 結果 | 內容 |
|:---------|:----:|:-----|
| scripts/05_verify.py | **20/20 PASS** | JSON 值 assert (flood-fill 0 comps, Nside16 stats, 隨機對照 p, 節點距離) |
| scripts/06_doc_verify.py | **32/32 PASS** | NN_results.md 每個數字 vs data JSON + 由 raw map 獨立重算 (gp10 中心 +10.4, node21/26/22 距離+溫度, Nside16 var ratio 0.745, 0.5° peak, NILC/Commander cross-map) |
| 全 scripts 重跑 (00-05) | ✅ 可重現 | 重跑後數字一致, 05 verifier 仍 20/20 |

**覆蓋率 audit**: session 全部推導/發現/計算/驗證 vs 記錄文檔 — 32 claims 檢查, 全部覆蓋 (補齊 radial 精確表 + P(≤5°) + 32/32 記錄後無遺漏)。

## 更深一層: gp10「冷斑」本身存疑

Planck 2013 引用 Cruz 2011 嘅 gp10 high-variance 區域 + 「prominent cold spot at b=-8°, l=32°, partially masked」。但:
1. SMICA 中尺度 (4.17-7°) 喺 gp10 完全搵唔到冷結構
2. Nside=16 重現: 區域 variance 反而低 (0.75×), skewness 正
3. 唯一細尺度冷特徵 (-215 μK @ 0.5°) 係緊湊前景

→ **gp10「第二冷斑」好可能係 Cruz 2011 低解析度 (Nside=16) variance/skewness 統計嘅偽影或前景驅動**, 唔係真實 CMB 冷結構。O5 結論 (第二冷斑冇節點對應) 因此更穩固。

## 檔案

```
scripts/00_probe.py         節點距離 + 溫度探針 (frame-corrected)
scripts/01_gp10_extract.py  多尺度 flood-fill 提取
scripts/02_planck_nside16.py Planck Nside=16 統計重現 + 細尺度掃描
scripts/03_crossmap_nodes.py 三地圖 cross-map + mask 校正 centroid
scripts/04_random_control.py 隨機對照 (銀河面條帶/全天/gp10 附近)
scripts/05_verify.py         20/20 verifier
scripts/06_doc_verify.py     32/32 doc-vs-data verifier (close-out)
data/gp10_extract.json
data/gp10_planck_style.json
data/random_control.json
```

## 衍生開放問題 audit (2026-08-21)

| 候選衍生問題 | 狀態 |
|:------------|:----:|
| gp10「冷斑」本身存疑 (variance 低/skew 正/前景) | 已納入 O28 結論 — 唔開新 O |
| O5 #1 node47 前景污染 | 獨立 O27 (已存在) |
| O5 #3 p=0.072 分解 | 獨立 O29 (未開始, 不受 O28 影響) |
| O5 #4 60 節點系統性 | 獨立 O30 (未開始, 不受 O28 影響) |

**O28 冇衍生新開放問題 — 可以 close ✅**
