# O27: 節點 47 前景污染分析 — 3.0° 第二冷係咪真實?

> **來源**: O5 衍生 (o5_catalog_compare/O5_OPEN_ISSUES.md #1)
> **狀態**: ✅ 完成 (2026-08-21) — 🔴 判定為前景污染, 見 NN_results.md
> **建立**: 2026-08-17

## 問題陳述

節點 47 (l=313.47°, **b=-8.58°**) 喺 3.0° SMICA 平滑下係**第二冷節點** (-135.7 μK, 僅次 node0 -145.0)。

但 |b| = 8.6° < 30° — **接近銀河面**, 溫度可能受銀河前景 (塵埃/同步輻射/自由-自由) 污染。

**問題**: 節點 47 嘅 -135.7 μK 係真實 CMB 冷結構, 定係銀河前景假象?

## 已知數據

| 量 | 值 |
|:---|:---|
| 位置 | l=313.47°, b=-8.58° |
| 3.0° SMICA | -135.7 μK (排名 2/60) |
| 5.0° SMICA (O2) | -123.4 μK |
| 距離大冷斑 | 90.5° |
| 距離 gp10 (32,-8) | 77.6° |
| 距離已知結構 | 冇 (唔近任何已知目錄冷斑) |

## 要驗證

1. **前景遮罩**: node47 喺 Planck 53% 或 70% mask 內定外?
2. **三地圖一致性**: SMICA/NILC/Commander 喺 node47 嘅溫度 (O3 有 4.17° cache)
3. **頻譜行為**: 用 Planck 多頻 (100/143/217/353 GHz) 檢查 node47 光譜係咪 CMB-like (平譜) 定 dust-like (上升)
4. **多尺度穩定性**: node47 喺 0.5°-10° 係咪穩定偏冷?
5. **熱點反查**: node47 對徑 (133.47°, +8.58°) 有冇對應結構?

## 判定標準

- 🟢 三地圖一致 (<5% spread) + 平譜 → 真實冷結構
- 🔴 三地圖分歧 或 光譜上升 → 前景污染
- 🟡 混合 → 部分污染

## 判定結果 (2026-08-21)

**🔴 前景污染** — 多頻譜測試決定性: node47 143 GHz = +18.3 μK (唔冷) + 217 GHz = +380.9 μK (急升), 217/143 = 20.8 vs 冷斑 0.36。SMICA 嘅 -136 μK 係銀河面塵埃殘留假象。R3 官方 CMB mask 亦遮住 node47 (0.5°-5° 盤 0% 保留, 60 節點 45/60 保留)。

**✅ close-out 驗證 (2026-08-21)**: `scripts/09_full_verification.py` 82 PASS / 0 FAIL — 所有數字由 raw FITS 獨立重算一致。判定穩固。

## 推導時序索引

| 序 | 日期 | 事件 | 產物 |
|:-:|:---|:---|:---|
| 1 | 2026-08-17 | O27 建立 (O5 延伸 #1 註冊) | `SESSION_START.md` |
| 2 | 2026-08-21 | 下載 Planck R3 頻率 map (100/143/217/353) + 3 個 mask | `data/HFI_SkyMap_*`, `data/COM_Mask_*` |
| 3 | 2026-08-21 | Script 01: 多尺度穩定性 (0.5°-10°) | `data/node47_multiscale.json` |
| 4 | 2026-08-21 | Script 02: 三地圖一致性 (SMICA/NILC/Commander @ 3.0/4.17/5.0) | `data/crossmap_node47.json` |
| 5 | 2026-08-21 | Script 03: 前景 mask 檢查 (R3/R2/GalPlane) | `data/mask_node47.json` |
| 6 | 2026-08-21 | Script 04: 對徑反查 + 週邊環境 | `data/antipode_node47.json` |
| 7 | 2026-08-21 | Script 05: Commander 低緯系統偏差 (t-test) | `data/commander_anomaly.json` |
| 8 | 2026-08-21 | Script 06/06b: 多頻譜 (3° 盤平均 + 3° FWHM 平滑) — **關鍵發現: 143 GHz 唔冷 + 217 GHz 急升** | `data/multifreq_node47.json`, `data/multifreq_smooth_node47.json` |
| 9 | 2026-08-21 | Script 07: 綜合判定 — 多頻譜 veto → **🔴 前景污染** | `NN_results.md` |
| 10 | 2026-08-21 | Script 08: 檔案驗證 (25/25 PASS) | — |
| 11 | 2026-08-21 | Script 09: close-out 全面驗證 (82/82 PASS) | — |
| 12 | 2026-09-11 | 搬遷至 IDCM-Original repo + scripts path 修復 (O3C /tmp 已清 → o5 4.17 cache) | scripts 01-09 |
| 13 | 2026-09-11 | 搬遷後重驗證: 08 (25/25) + 09 (82/82) = 107/107 PASS | — |

**推導鏈**: 問題定義 (SESSION_START) → 數據採集 (頻率 map + mask) → 六項獨立測試 (01-06) → 綜合判定 (07, 多頻譜 veto) → 雙重驗證 (08-09)。

## 衍生開放問題

1. **60-node 微冷系統學前景校正** (已註冊為 **O52**, 原 O30): 60 節點中 15/60 被 R3 CMB mask 遮住 (全部 |b|<20°)。O52 分析必須區分 masked/unmasked 節點 + 做多頻譜前景篩查, 否則前景污染會污染系統學結論。
2. **SMICA 銀河面殘留系統學**: node47 顯示 SMICA 喺 |b|<20° 有塵埃殘留假象 (-136 μK vs 143GHz +18 μK)。系統性量化 SMICA 低緯殘留 (對照 NILC/Commander) — 建議 O52 內一併處理 (未獨立註冊)。

## 檔案 (建立時)

```
scripts/01_foreground_mask.py
scripts/02_crossmap_node47.py
scripts/03_multifreq_node47.py
data/
NN_results.md
```
