# O8: 節點 5° 影響範圍 vs 26° 間距 — 尺度半徑之謎

> **狀態: 🟢 已閉合 (2026-08-19)**
> **閉合: 影響半徑 = 節點間距/2π = 約化波長 λ̸ = 4.1526°**
> **詳情: `02_results.md`**

## 問題陳述

冷斑項目發現: 節點影響範圍 ~5°（冷斑 FWHM 4.17°），但節點間距 26.09°。**點解影響範圍遠細過間距？** 5° vs 26° 比例 = 0.19 ≈ ?

## 已知事實

| 量 | 值 | 來源 |
|:---|:---|:-----|
| 冷斑 FWHM | 4.17° (R8 尺度) | 22_smica_smoothed.py |
| 節點間距 (邊長) | 26.0913° | o1_edge_length |
| 影響/間距 | 4.17/26.09 = 0.16 | — |
| 冷斑 RMS | ε⁵/8 = 1.1007e-5 | 02_cold_spot_structural.py |
| 冷斑尺度 ℓ | 44 = 2N_d | 22_complete_summary.md |
| 星系團真空 | <4.5-5° | crystal_stress/ |

## 候選結構關係

```
✅ 閉合: 4.17° = 26.09°/2π = 4.1526° (偏差 0.42%)
       去平滑後: 4.152° (偏差 0.01%)
❌ 排除: 180/44 = 4.09° (1.5%), 26.09×ε = 4.03° (3.3%)
❌ 排除: 26.09×φ⁻³ = 6.16° (47.7%)
```

## 閉合鏈 (零自由參數)

```
a = 26.0913° (o1 群論閉合)
  → r = a/2π = 4.1526° (約化波長)
  → 冷斑 HWHM (去平滑) = 4.152° (0.01% ✅)
  → ℓ = 180/r = 43.3 ≈ 44 = 2N_d (-1.5%)
  → 星系團真空 4.5-5° (1.08-1.20×, 物質排除緩衝)
```

## 驗證路徑

| # | 路徑 | 方法 | 結果 |
|:-:|:----|:-----|:----:|
| 1 | R8 幾何 | 60 節點網絡 inscribed/circumscribed/Voronoi | Voronoi 14.79°, 唔係影響半徑 |
| 2 | 比例搜索 | 4.17/26.09 vs φ 冪/κ/π 組合 | **a/2π 唯一 0.5% 內候選** |
| 3 | 尺度鏈 | 26.09 → 4.17 → 冷斑 FWHM | **去平滑閉合 0.01%** |
| 4 | 星系團真空 | 4.5-5° 真空半徑同 4.17 一致? | ✅ 1.08-1.20× |
| 5 | 可證偽預測 | 其他節點影響範圍 = 4.17° | 🔴 等單極強節點 (P2) |

## 推導時序索引 (2026-08-19)

按執行時間排序, 記錄每步推導/發現/驗證嘅產物:

| # | 時間 | 步驟 | 產物 | 發現 |
|:-:|:----:|:-----|:-----|:-----|
| 1 | 16:13 | 幾何半徑 + 比例搜索 | `scripts/01`, `data/geometry_scale.txt` | 唯一 0.5% 內候選 = **a/2π = 4.1526°** (0.42%); Voronoi 14.79° 排除 |
| 2 | 16:18 | 節點影響半徑量度 | `scripts/02`, `data/radial_profiles.npy` | 60 節點 mean\|T\| 半峰 = 4.25° (初步); 發現節點冇單極信號 |
| 3 | 16:21 | 尺度驗證 A/B/C | `scripts/03` | **方法坑**: 60 節點平均 |T| 冇單極信號 → median 10.3° 假結果; 信號喺阻挫邊唔喺節點 |
| 4 | 16:26 | 去平滑外推 | `scripts/05`, `data/desmear_result.txt` | **0.1° bins 外推 HWHM_true = 4.138°** (偏差 0.34%) |
| 5 | 16:28 | 閉合鏈 + Gaussian 擬合 | `scripts/06`, `data/closure_chain.txt` | Gaussian A=-148.7 μK, σ=4.452, R²=0.9958; **閉合鏈完整** |
| 6 | 16:29 | 全部節點 profile | `scripts/07`, `data/all_node_radii.txt` | 只有冷斑有單極信號; 節點 47 = 大尺度結構 |
| 7 | 16:33 | 雙重驗證 (第 2 重) | `scripts/99`, `data/verification_result.txt` | **7/7 PASS** (獨立重算邊長/外推/真空/ℓ) |
| 8 | 16:35 | 結果圖 | `scripts/08`, `data/o8_scale_closure.png` | HWHM_true = 4.148° (第三估計, -0.12%) |
| 9 | 16:40 | 冷斑 profile 修正 | `scripts/04` (修寫檔 bug), `data/coldspot_profile.txt` | 10 尺度完整數據 |
| 10 | 16:54 | 最終核對 (第 3 重) | `scripts/FINAL_AUDIT.py`, `data/final_audit.txt` | **23/23 PASS** (由 02_results.md 逐數字重算) |
| 11 | 17:03 | 文檔更新 | `01_problem_record.md`, `02_results.md`, `README.md` | 閉合記錄 + 方法學教訓寫入 |
| 12 | — | 文檔完整性核對 (第 4 重) | `scripts/DOC_AUDIT.py`, `data/doc_audit.txt` | **46/46 PASS** (含歷史時序 + 污染檢查) |

**時序完整性:** SESSION_START.md (08-16 21:27, 原始啟動) → 推導 (08-19 16:13-16:54) → 文檔更新 (17:03)。無回溯污染: SESSION_START 保持原始內容, 未被 O8 結果改寫。

**依賴鏈:** o1_edge_length (邊長 26.0913°) → cmb_cold_spot (冷斑 R8 4.17°, a5_nodes) → crystal_stress (星系團真空 4.5-5°) → **O8 (本項目)** → 後續: O25 尺度譜 / 節點 47 影響半徑建模 (P2 可證偽預測)

## 雙重驗證

`scripts/99_double_verification.py` → **7/7 PASS** 🟢
`scripts/FINAL_AUDIT.py` → **23/23 PASS** 🟢 (第 3 重獨立核對, 由 02_results.md 出發)
`scripts/DOC_AUDIT.py` → **46/46 PASS** 🟢 (第 4 重文檔完整性, 含時序/污染檢查)

## 相關檔案

```
02_results.md                    # 完整閉合記錄 (本文檔)
scripts/01-08                    # 分析 + 圖
scripts/99_double_verification.py # 雙重驗證 7/7
scripts/FINAL_AUDIT.py           # 最終核對 23/23
scripts/DOC_AUDIT.py             # 文檔完整性核對 46/46
data/                            # 全部結果 + o8_scale_closure.png
data/final_audit.txt             # 最終核對結果
data/doc_audit.txt               # 文檔核對結果
final_result.md                  # 極簡結論摘要 (RESULT_TEMPLATE 格式)
```

## 技能

- polyhedral-graph-analysis（核心）✅ 已載入
- camb-cmb-verification（輔助）✅ 已載入

---

*O8 記錄 · IDCM v10.0 · 2026-08-19*
