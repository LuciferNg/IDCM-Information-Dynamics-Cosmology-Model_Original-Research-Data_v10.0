# O28: Planck gp10 冷斑 mask 校正 — 第二官方冷斑有冇節點對應?

> **來源**: O5 衍生 (o5_catalog_compare/O5_OPEN_ISSUES.md #2)
> **狀態**: ✅ 已關閉 (2026-08-21) — 🔴 gp10 冇節點對應
> **建立**: 2026-08-17

## 問題陳述

Planck 2013 確認第二冷斑 **gp10 (l=32°, b=-8°)** — 但 O5 顯示最近節點 node21 距離 **10.1°** (唔命中, 且係熱 +93.3 μK), node26 距離 20.2° (-49.0 μK)。

Planck 2013 原文註明 gp10 區域**部分被銀河面遮擋** — mask 校正未做。

**問題**: gp10 冷斑區域喺 mask 校正後, 有冇 A₅ 節點對應? 定係純粹銀河面內結構?

## 已知數據

| 量 | 值 |
|:---|:---|
| gp10 位置 | l=32°, b=-8° |
| 最近節點 | node21: 10.05° (+95.5 μK 熱!) — frame-corrected closure 值 |
| 第二近 | node26: 20.25° (-48.3 μK) |
| 第三近 | node22: 24.02° (-23.6 μK) |
| node26/22 | 都係微冷 (-48/-24) — 潛在對應? |

> ⚠️ 時序標註: 問題陳述段嘅距離/溫度值係 **O5-era framing (2026-08-17 交接時)**；
> 本表係 frame-corrected **closure 值 (2026-08-21)**。兩者都係合法歷史，
> 分別代表 O5 量度同 O28 frame 校正後量度 (差異來源: ICRS→Galactic frame 轉換)。

## 結論 (2026-08-21)

### 🔴 gp10 冇節點對應 — 且「gp10 冷斑」本身存疑

1. **SMICA 中尺度冇冷結構**: 4.17°/5.0°/7.0° flood-fill 喺 gp10 附近 (r=25°) 搵到 **0 個冷 comp**; gp10 中心 (32,-8) = +10.4 μK 微熱, radial 0-30° 全偏熱 (+20~+27 μK)
2. **Planck Nside=16 統計重現失敗**: gp10 區域 variance = 0.75× 其餘天空 (唔係 high variance), skewness = **+0.12 正偏** (唔係負偏)
3. **0.5° peak (-215 μK) = 前景**: 4.17° 三地圖一致只有 -9~-17 μK, 振幅崩潰 = 緊湊小尺度結構
4. **Mask 校正後 centroid 移離節點**: (38,-16) 一帶, 距離任何節點 > 17°
5. **隨機對照**: 銀河面條帶隨機位置 P(nearest ≤ 10.05°) = **0.477** — 10.05° 完全正常, 唔係異常空洞

**更深結論**: gp10「第二冷斑」好可能係 Cruz 2011 低解析度 (Nside=16) variance/skewness 統計嘅偽影或前景驅動, 唔係真實 CMB 冷結構。O5 結論 (第二冷斑冇節點對應) 更穩固。

### Flood-fill 結果表

| FWHM | 4.17° | 5.0° | 7.0° |
|:----:|:-----:|:----:|:----:|
| 冷 comps (bcut 5/10/15/20) | **0 / 0 / 0 / 0** | 0/0/0/0 | 0/0/0/0 |

(3.0° 唯一 comp peak (22.4,-25.0), 距 gp10 ~20°, 係另一結構)

### Radial profile (SMICA 4.17°, gp10 中心向外)

| 環帶 | mean ± std (μK) |
|:----:|:---------------:|
| 0-5° | +24.7 ± 24.5 |
| 5-10° | +25.5 ± 36.4 |
| 10-15° | +25.4 ± 40.7 |
| 15-20° | +26.9 ± 39.7 |
| 20-25° | +20.6 ± 33.0 |
| 25-30° | +20.9 ± 30.3 |
| 30-35° | +3.0 ± 35.8 |

### Mask 校正 centroid (SMICA 4.17°, r≤15°, 冷像素 T<0)

| \|b\| cut | centroid | 最近節點 | 距離 |
|:------:|:--------:|:--------:|:----:|
| ≥5° | (38.9, -11.9) | node21 | 17.9° |
| ≥10° | (38.4, -16.1) | node21 | 19.7° |
| ≥15° | (37.5, -18.9) | node22 | 18.1° |

→ Mask 校正唔係令 gp10 接近節點，而係推得更遠 (10° → 18-20°)。

## 推導時序索引 (Derivation Timeline)

| # | 日期 | 步驟 | Script | 產出 | 狀態 |
|:-:|:----:|:-----|:-------|:-----|:----:|
| 1 | 2026-08-17 | O5 close audit → 註冊 O28 (gp10 mask 校正問題) | — | 01_problem_record.md 初版 | ✅ |
| 2 | 2026-08-21 | node 距離/溫度探針 (ICRS→Galactic frame 校正) | 00_probe.py | node21=10.05°(+95.5), node26=20.25°(-48.3), node22=24.02°(-23.6) | ✅ |
| 3 | 2026-08-21 | 多尺度 flood-fill (4.17/5.0/7.0° = 0 冷 comp; 3.0° 唯一 comp) | 01_gp10_extract.py | gp10_extract.json | ✅ |
| 4 | 2026-08-21 | Planck Nside=16 統計重現 (var 0.75×, skew +0.12 — 失敗) + 細尺度掃描 | 02_planck_nside16.py | gp10_planck_style.json (0.5° peak -215) | ✅ |
| 5 | 2026-08-21 | 三地圖 cross-map + mask 校正 centroid (移離節點) | 03_crossmap_nodes.py | centroid 17.9-19.7° | ✅ |
| 6 | 2026-08-21 | 隨機對照 (銀河面條帶/全天/gp10 附近) | 04_random_control.py | random_control.json (P=0.477) | ✅ |
| 7 | 2026-08-21 | JSON verifier | 05_verify.py | **20/20 PASS** | ✅ |
| 8 | 2026-08-21 | doc-vs-data verifier + 覆蓋率 audit | 06_doc_verify.py | **32/32 PASS**, 覆蓋率 21/21 | ✅ |
| 9 | 2026-08-21 | 閉合判定 + 文檔更新 (NN_results/record/SESSION_START) | — | 🔴 gp10 冇節點對應 | ✅ |
| 10 | 2026-09-11 | **獨立 audit** (唔 import 原始 script; tangent-plane grid + ndimage 獨立 flood-fill; 多 seed MC) | 07_audit_independent.py | **78/78 PASS** (初跑 75/78 → 3 個 doc gap 修復) | ✅ |
| 11 | 2026-09-11 | doc gap 修復: record 補 centroid 表 + 時序標註; SESSION_START 標註 O5-era | — | 本文件 + SESSION_START | ✅ |
| 12 | 2026-09-11 | final_result.md (RESULT_TEMPLATE 格式) | — | final_result.md | ✅ |

**時序完整性原則**: 早期 framing 值 (O5-era 距離/溫度) 保留喺問題陳述段作為合法歷史，
唔以推導時序回溯污染; closure 值 (10.05°/95.5 μK) 只寫入後續段落。

## Verifier

- **20/20 PASS** (scripts/05_verify.py) — 所有數字由 data/ JSON 直接讀取核實
- **32/32 PASS** (scripts/06_doc_verify.py) — NN_results.md 每個數字 vs data JSON + raw map 獨立重算
- **全 scripts 重跑 (00-05) 可重現** — 數字一致
- **覆蓋率 audit**: session 全部發現/計算/驗證已寫入記錄文檔, 無遺漏

## 衍生開放問題 audit

- O28 冇衍生新開放問題
- O27 (node47) / O29 (p=0.072) / O30 (60 節點系統性) = O5 其他延伸, 獨立存在, 不受 O28 影響

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
NN_results.md                完整結果
```
