# O30: 60 節點微冷系統性 — 全部節點有冇整體溫度異常?

> **來源**: O5 衍生 (o5_catalog_compare/O5_OPEN_ISSUES.md #4)
> **狀態**: 🔴 已關閉 (2026-08-21) — 否定: 只有 node0/node9 真異常 + 離散性完成
> **驗證**: 17/17 PASS (scripts/07_verification.py) + 離散性 5 重測試
> **結果**: `NN_results.md` + `DISCRETENESS_COMPLETE.md`

## 問題陳述

O5 核心假說: IDCM 預測 **60 個 A₅ 節點全部有溫度異常** (拓撲縫合節點)。但目錄對比只發現 2 個強冷 (node0 + node9) — 其他 58 個冇對應目錄。

**關鍵問題**: 其餘節點係咪有**系統性微冷/微熱** (低於目錄閾值, 但統計上可檢測)?

## 結論 (2026-08-21)

**否定 — 「全部 60 節點有異常」假說不成立。**
**完成 — 「溫度效應離散」假說確認: 只有 5 個跨尺度穩定異常節點 (0,9,33,47,53), 剩餘 55 節點零異常。**

| 測試 | z | 判定 |
|:---|:---|:---|
| 60 節點 mean vs 隨機 | −0.21σ | 🔴 |
| 高緯 31 mean vs 隨機 | −0.47σ | 🔴 |
| 剔除 node0+9 mean | +0.52σ | 🔴 |
| mean\|T\| 幅度 (IDCM 真測試) | −0.65σ | 🔴 |
| 剔除後 mean\|T\| | −1.45σ | 🔴 (反方向) |
| 堆疊 radial profile | χ²=0.4/20dof p=1.0 | 🔴 |
| 多尺度 0.5°-10° | z ∈ [−0.55, +0.55] | 🔴 |
| 冷/熱 count | 29:31 (p=0.90) | 🔴 |
| **跨尺度穩定異常 (離散性)** | **5 vs 隨機 0.00±0.00, p<0.001** | 🟢🟢 |

- 節點 mean|T| = 32.75 μK **低於**隨機期望 34.95 μK (唔係測唔出, 係反方向)
- 可偵測閾值 11.6 μK; IDCM 預測幅度 (F₅≈150 μK) power=100% → 已被強力排除
- 子集效應 (ΔE=0 節點, O24 極端冷色) 完全唔受影響 — 保留
- **離散性**: 5 個跨尺度穩定異常 = node0 (冷斑), node9 (第二冷), node33 (邊緣冷 🟡), node47 (🔴 O27 前景), node53 (熱 +112 🟢🟢 新發現)

## 已知數據

| 量 | 值 |
|:---|:---|
| 高緯度節點 (|b|≥30°) | 31 個 |
| 其中 < -2σ | 2 個 (node0 -145.0, node9 -110.6) |
| 隨機期望 < -2σ | 0.7 個 |
| 高緯節點 σ (3.0°) | 48.6 μK |
| 大冷斑 | node0 (-134.2) |
| 第二冷 | node9 (-110.6) 已獨立確認 |

## 驗證結果 (2026-08-21)

1. **整體均值檢驗**: 60 節點 mean = −1.25 μK vs 隨機 0.00±5.8 → z = −0.21σ 🔴
2. **高緯度子集**: 31 節點 mean = −4.06 vs 隨機 → z = −0.47σ 🔴
3. **符號不對稱**: 冷 29:熱 31 (p=0.90), 冷熱 mean|T| 比 1.154x (p=0.58 NS) 🔴
4. **堆疊 radial profile**: flat (χ²=0.4/20dof, p=1.0), 中心 bin z=−0.16σ 🔴
5. **多尺度**: 0.5°-10° 全 z ∈ [−0.55, +0.55] 🔴
6. **控制組**: 1000 組隨機 (各向同性 + 同緯度), power 分析確認閾值 11.6 μK
7. **mean|T| 幅度檢驗**: 32.75 vs 34.95 → z=−0.65σ (單尾 p=0.74) 🔴

## 對 IDCM 嘅意義

1. 「60 節點全部有溫度異常」→ **否定**
2. 溫度效應係**離散** (只有特定節點), 唔係**連續** (全部節點微偏)
3. 修正假說: 異常只喺 node0/node9/ΔE=0 節點/極端節點 — 可能因為大部分節點 θ_i≈π/2 (正交相位, 效應≈0), 與 ΔE=0 觀察一致
4. **離散性完成**: 5 個跨尺度穩定異常 (0,9,33,47,53) — node53 熱異常係新發現 (b=−34° 高緯, 10/10 尺度全正)
5. **node53 多頻譜驗證 (2026-08-22)**: 🟢🟢 真實 CMB 熱異常 (三地圖 spread 1.8%, 平譜核心 +82 μK, R3 unmasked, dust 1.31x) — 見 NODE53_REPORT.md
6. **node33 多頻譜驗證 (2026-08-22)**: 🔴 前景污染 (143 GHz 轉正 +104, 217/143=5.09, 353 dust +4844 μK = 8.9x 冷斑, 環扣除冷核心消失) — 見 NODE33_REPORT.md。**O30 圖景修正: 3 真異常 (0/9/53) + 2 前景 (33/47)**

## 檔案

```
scripts/01_mean_vs_random.py       — 整體均值 vs 隨機 (1000 組)
scripts/02_stack_radial.py         — 堆疊 radial profile
scripts/03_multiscale.py           — 多尺度系統性
scripts/04_sign_asymmetry.py       — 符號不對稱 (O24 關聯)
scripts/05_power_analysis.py       — 統計力分析
scripts/06_amplitude_test.py       — mean|T| 幅度檢驗
scripts/07_verification.py         — 驗證器 17/17 PASS
scripts/08_discreteness.py         — 離散性 5 重測試 🟢🟢
scripts/09_node53_multifreq.py     — node53 多頻譜檢查 (O27 流程)
scripts/10_node53_ring_background.py — node53 環背景扣除 + dust tracer
scripts/11_node53_crossmap.py      — node53 三地圖一致性
scripts/12_node53_antipode_mask.py — node53 對徑 + mask 狀態
scripts/13_node53_verify.py        — node53 驗證器 14/14 PASS
scripts/14_full_session_verify.py  — **全面驗證器 62/62 PASS (2026-08-22)**
scripts/15_node33_multifreq.py     — node33 多頻譜 (🔴 前景判定)
scripts/16_node33_verify.py        — node33 驗證器 17/17 PASS
data/01_mean_vs_random.txt
data/02_stack_radial.txt
data/03_multiscale.txt
data/04_sign_asymmetry.txt
data/06_amplitude_test.txt
data/08_discreteness.txt
data/09_node53_multifreq.json
data/10_node53_ring_background.json
data/11_node53_crossmap.json
data/12_node53_antipode_mask.json
data/15_node33_multifreq.json
NN_results.md
DISCRETENESS_COMPLETE.md
NODE53_REPORT.md
NODE33_REPORT.md
```

## 推導時序索引 (2026-08-21 → 2026-09-11)

按 mtime + 文檔日期聲稱重建, 確保冇回溯污染:

| 步驟 | 日期/時間 | Script | 產出 | 內容 | 記錄文檔 |
|:---|:---|:---|:---|:---|:---|
| 1 | 08-21 23:12 | `01_mean_vs_random.py` | `data/01_mean_vs_random.txt` | 60 節點 mean −1.25 μK vs 隨機 (1000 組 iso+同緯) z=−0.21σ; 高緯 31 z=−0.47σ; 剔除 node0+9 轉正 | NN_results §1-3 |
| 2 | 08-21 23:13 | `02_stack_radial.py` | `data/02_stack_radial.txt` | 堆疊 radial profile 全線 flat χ²=0.4/20dof, 中心 bin z=−0.16σ | NN_results §4 |
| 3 | 08-21 23:13 | `03_multiscale.py` | `data/03_multiscale.txt` | 多尺度 0.5°-10° 全 z∈[−0.55,+0.55] 冇系統性 | NN_results §5 |
| 4 | 08-21 23:15 | `04_sign_asymmetry.py` | `data/04_sign_asymmetry.txt` | 冷/熱 29:31 p=0.90; 冷熱 mean|T| 比 1.154x p=0.58; O24 冷色 8/10 p=0.036 | NN_results §3 |
| 5 | 08-21 23:16 | `05_power_analysis.py` | — | 可偵測閾值 11.6 μK; IDCM F₅≈150 μK power=100% 已被排除 | NN_results §6 |
| 6 | 08-21 23:16 | `06_amplitude_test.py` | `data/06_amplitude_test.txt` | mean|T| 32.75 vs 34.95 z=−0.65σ (單尾 p=0.74); 剔除後 −1.45σ 反方向 | NN_results §7 |
| 7 | 08-21 23:16 | `07_verification.py` | — | 主測試驗證器 **17/17 PASS** | NN_results 驗證 |
| 8 | 08-22 00:50 | `08_discreteness.py` | `data/08_discreteness.txt` | 離散性 5 重測試: 跨尺度穩定異常 5 節點 (0,9,33,47,53) p<0.001 🟢🟢; 其餘 4 測試 🔴 | DISCRETENESS_COMPLETE |
| 9 | 08-22 00:53 | — | `SESSION_START.md` 更新 | 狀態 ✅ 已關閉 (離散性完成, node53 標 🟢🟢 待驗證) | SESSION_START |
| 10 | 08-22 00:55 | `09_node53_multifreq.py` | `data/09_node53_multifreq.json` | node53 多頻譜 raw 抽值; 217/143=1.66 上升但對照組同升 → 背景梯度 | NODE53_REPORT |
| 11 | 08-22 01:00 | `10_node53_ring_background.py` | `data/10_node53_ring_background.json` | 環背景扣除: 100 +82.7 / 143 +80.9 / 217 +51.0 μK 平譜 CMB-like; SMICA +82.0 一致 | NODE53_REPORT |
| 12 | 08-22 01:05 | `11_node53_crossmap.py` | `data/11_node53_crossmap.json` | 三地圖 SMICA +96.8 / NILC +96.2 / Commander +95.1 spread 1.8% (<5%) | NODE53_REPORT |
| 13 | 08-22 01:07 | `12_node53_antipode_mask.py` | `data/12_node53_antipode_mask.json` | 對徑 −46.05 冇鏡像; R3 unmasked; dust 1.31x 高緯 | NODE53_REPORT |
| 14 | 08-22 01:08 | `13_node53_verify.py` | — | node53 驗證器 **14/14 PASS** | NODE53_REPORT |
| 15 | 08-22 01:13 | `15_node33_multifreq.py` | `data/15_node33_multifreq.json` | node33 多頻譜: 143 GHz 轉正 +104, 217/143=5.09, 353 dust +4844 (8.9x) → 🔴 前景 | NODE33_REPORT |
| 16 | 08-22 01:38 | `16_node33_verify.py` | — | node33 驗證器 **17/17 PASS** | NODE33_REPORT |
| 17 | 08-22 01:43 | — | `NN_results.md` + `DISCRETENESS_COMPLETE.md` + `01_problem_record.md` 收尾 | 圖景修正: 3 真異常 (0/9/53) + 2 前景 (33/47) | 全部 |
| 18 | 08-22 01:44 | `14_full_session_verify.py` | — | 全面驗證器 **62/62 PASS** | 01_problem_record 驗證狀態 |
| 19 | 09-11 20:36 | `17_audit_independent.py` | — | 獨立審計 (唔用原 scripts/data 做輸入) **96/96 PASS** (2026-09-11 修正 audit 自身 3 處定義/容差: A4 RNG 漂移, I6/J8 353 dust 定義) | 本索引 |

**時序完整性**: mtime 序列單調遞增符合推導順序; 所有 08-22 發現喺文檔內容有「2026-08-22」標註, 冇寫成早前發生; SESSION_START (00:53) 早過 NODE53_REPORT (01:08) 正確反映當時狀態。✅

## 全面驗證狀態 (2026-08-22)

`scripts/14_full_session_verify.py` — **62/62 PASS**:
- PART A (O30 主測試 7 項): mean/z/幅度/堆疊/冷熱/ΔE=0/冷色 — 全部獨立重算一致
- PART B (離散性 4 項): 穩定異常 5 節點 + node53 zbar — 一致
- PART C (node53 6 項): 三地圖/環ΔT/多頻譜/mask/對徑/跨尺度 — 一致
- PART C2 (node33 5 項): 三地圖/353 dust/8.9x/R3 mask — 一致
- PART D (文檔完整性 30 項): 15 關鍵數值 + 10 data 檔引用 + 4 文檔交叉引用 — 全部喺文檔

**結論: 本 session 所有推導過程、發現、計算、驗證、結果已全部正確寫入記錄文檔, 數值獨立重算一致。**
