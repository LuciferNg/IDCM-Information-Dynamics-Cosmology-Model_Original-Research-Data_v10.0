# O3: 60 節點實際溫度統計 — SMICA 全節點掃描

## 問題陳述

冷斑項目確認節點 0 (冷斑) = -134.2μK, 對徑點 (節點 57) z=-3.24。但其他 58 個節點嘅實際溫度未系統統計。

**O3 目標: 完整測量 60 節點喺 SMICA 5° 平滑圖嘅溫度, 建立完整統計:**

1. 60 節點溫度分佈 (mean, std, min, max)
2. 冷色 (30) vs 熱色 (30) 節點平均溫度差異
3. 節點溫度 vs 隨機天空位置溫度嘅顯著性
4. 溫度極端節點 ranking (最冷/最熱)
5. 同 ΛCDM 高斯場對比 (60 隨機點嘅期望分佈)

## 狀態表

| # | 任務 | 狀態 | 結果摘要 |
|:-:|:-----|:----:|:---------|
| 1 | 60 節點溫度分佈 | ✅ | mean=-1.25, std=46.19, min=-134.2 (節點0), max=+112.0 (節點53); K-S 高斯符合 (p=0.51-0.74) |
| 2 | 冷色 vs 熱色分離 | 🟡 | 冷=-12.41, 熱=+9.91, 差=-22.31 μK; Welch p=0.061, 排列 p=0.061 — 邊緣 |
| 3 | 極端值 vs 隨機 | 🟢/🟡 | 冷斑 98.2% 更冷 (z=-1.98σ) 🟢; 冷熱差排列 p=3.4% 🟢; 整體 std 91.8% 🔴 |
| 4 | BFS ladder | 🔴 | Spearman ρ=-0.05 (p=0.71); Fibonacci ladder ρ=0.20 (p=0.12) — 冇 ladder |
| 5 | 節點 57 謎題 | ✅ | 著色=BFS parity 唔係溫度預測; 23/60 符號唔匹配; 12 冷色正溫之一 |
| 6 | ΔE=0 節點檢驗 | 🟡🚨 | mean\|T\|=19.05 vs 36.18 (比例 0.526), permutation p=0.038; **但 8/12 喺銀河盤 (p=0.038)**; 高緯度剔除後仍顯著 (4 vs 34, p=0.0074) |

## 關鍵發現

1. **冷斑係唯一真正極端節點** — 98.2% 百分位, 其他節點接近隨機
2. **著色 = BFS parity (hop 奇偶), 唔係溫度預測** — 解決節點 57 謎題
3. **ΔE=0 零能量節點信號再確認** (p=0.038) — 與 §21 一致
4. **Fibonacci ladder 唔被支持** 🔴 誠實負結果
5. **冷熱分離係邊緣信號** (p=0.06), 銀河盤剔除後消失 — 唔穩健

## 已知事實

| 量 | 值 | 來源 |
|:---|:---|:-----|
| 冷斑 (節點 0) | -134.19 μK | 本專案 01_node_temps.py |
| 節點 47 (次冷) | -123.40 μK | 本專案 |
| 節點 53 (最熱) | +112.00 μK | 本專案 |
| 節點 57 (對徑) | +8.21 μK | 本專案 |
| 冷色平均 | -12.41 μK | 本專案 |
| 熱色平均 | +9.91 μK | 本專案 |
| 冷熱差 | -22.31 μK (p=0.06) | 本專案 |
| 相關 r (著色-溫度) | -0.244 | 22_smica_smoothed.py (舊) |
| ΔE=0 mean\|T\| | 19.05 μK (p=0.038) | 本專案 08 |

## 驗證路徑

| # | 路徑 | 方法 | 狀態 |
|:-:|:----|:-----|:----:|
| 1 | 溫度分佈 | 60 節點 SMICA 值, 直方圖 + 統計檢驗 | ✅ |
| 2 | 冷熱分離 | 30/30 分組, bootstrap 顯著性 | ✅ |
| 3 | 極端檢驗 | 節點 min/max vs 2000 組隨機 60 點 | ✅ |
| 4 | ladder 檢驗 | 溫度 vs BFS 距離相關 (Spearman) | ✅ |
| 5 | 對徑點謎題 | 節點 57 正溫度但冷色著色嘅解釋 | ✅ |
| 6 | 雙重驗證 | 獨立重讀重平滑重抽值, max\|Δ\|=0.000049 μK | ✅ |

## 檔案

```
scripts/01_node_temps.py       # 60 節點溫度提取 ✅
scripts/02_stats_tests.py      # 統計檢驗 (KS/bootstrap) ✅
scripts/03_extreme_test.py     # 極端值 vs 隨機 ✅
scripts/04_ladder_corr.py      # BFS 距離相關 ✅
scripts/05_verify.py           # 雙重驗證 ✅
scripts/06_node57_puzzle.py    # 節點 57 謎題 ✅
scripts/07_plots.py            # 圖表 ✅
scripts/08_zero_energy_nodes.py # ΔE=0 檢驗 ✅
scripts/09_hallucination_check.py  # 幻覺檢查 ✅
scripts/10_red_flag_check.py   # 紅燈驗證 ✅
scripts/11_cross_map_zeroE.py  # 三地圖交叉 ✅
scripts/12_midlayer_rotation_test.py  # 中間層旋轉對照 ✅
scripts/13_node45_multiscale.py  # node 45 多尺度 ✅
scripts/14_high4_positions.py    # 高緯 4 節點位置 ✅
scripts/15_high4_multiscale.py   # 高緯 4 三地圖多尺度 ✅
scripts/16_high4_vs_node45.py    # 高緯 4 vs node 45 對比 ✅
scripts/17_antipodal_pairs.py    # 對徑對分析 ✅
scripts/18_node45_region.py      # node 45 附近區域結構 ✅
scripts/19_full_hallucination_check.py  # 完整幻覺檢查 (88/88) ✅
scripts/20_audit_independent.py   # 🆕 2026-09-09 獨立審計 (157/157 PASS)
scripts/21_fix_02_results_table.py  # 🆕 2026-09-09 表格修正 (42 cells)
scripts/22_antipodal_temp_check.py  # 🆕 2026-09-11 對徑對三地圖溫度差+方向性
data/node_temps.txt            # 完整數據 ✅ (ground truth)
data/bfs_distances.txt         # BFS 分佈 ✅
figs/01_temp_hist.png          # 直方圖
figs/02_coldhot_box.png        # 盒鬚圖
figs/03_temp_vs_bfs.png        # BFS 散點
02_results.md                  # 完整結果報告 ✅
```

## 推導時序索引

> 全部 O3 推導鏈按時序排列。**日期為實際完成日，禁止以推導時序回溯改動舊記錄。**

| # | 日期 | 位置 | 推導鏈步驟 | 下游 |
|:-:|:-----|:-----|:----------|:-----|
| 1 | 08-16 | SESSION_START.md | 方法設定: SMICA 4.17° FWHM 平滑 → remove_dipole → 60 節點抽值 | → #2 |
| 2 | 08-17 | 01_problem_record | 問題陳述: 冷斑 -134.2μK 已知, 其餘 58 節點未統計 | → #3 |
| 3 | 08-17 | 02_results §1 | 60 節點溫度分佈: mean=-1.25, std=46.19, K-S 高斯符合 | → #4/#7 |
| 4 | 08-17 | 02_results §2 | 冷熱分離: 差=-22.31μK, p=0.06 邊緣; 銀河盤剔除後 p=0.24 消失 | → #9 |
| 5 | 08-17 | 02_results §3 | 極端檢驗: 冷斑 98.2% 更冷 (z=-1.98σ); 無整體效應 | → #6 |
| 6 | 08-17 | 02_results §4-5 | BFS ladder 冇相關 (ρ=-0.05); 節點 57 謎題 = 著色係 BFS parity | 閉合 |
| 7 | 08-17 | 02_results §6 | ΔE=0 檢驗: 12 節點比例 0.526, perm p=0.038 🟢 | → #8 |
| 8 | 08-17 | 03_red_flag | 🚨 紅燈: 8/12 ΔE=0 喺銀河盤 (p=0.038) | → #9 |
| 9 | 08-17 | 03_red_flag | 中間層效應破解: k=2 必須喺 d3-d5; 旋轉對照 p=0.17, 條件 p=0.40 🟢 紅燈 1 破解 | → #10 |
| 10 | 08-17 | 03_red_flag | 2×2 表: 銀河盤 (0.515, p=0.105) / 高緯 (0.375, p=0.0074); 紅燈 4: 銀河盤唔天然偏低 | → #11 |
| 11 | 08-17 | 04_high4_node45 §1 | node 45 裁決: 三地圖一致 (spread 1.6μK) 但細尺度前景特徵 🟡 部分降級 | → #12 |
| 12 | 08-17 | 04_high4_node45 §2 | 高緯 4 節點 (10,22,25,32): |b|≥30° 乾淨; Welch p=0.0074 🟢🟢 最強證據 | → #13 |
| 13 | 08-17 | 04_high4_node45 §2.2 | 對稱結構: 2 對近對徑同色對 (174.66°, hop 和=8) = A₅ 30 對強制 | 閉合 |
| 14 | 08-17 | 04_high4_node45 §2.5-2.6 | 多尺度 3°-7° 穩定 + 三地圖一致 (0.375/0.416/0.372) | 閉合 |
| 15 | 08-17 | 05_hallucination_check | 幻覺檢查: 88/88 統計數字獨立重算一致 | → #16 |
| 16 | 08-17 | README | 總結 + 衍生 O21-O26 | → O21-O26 |
| 17 | 09-09 | 02_results 表格 | **審計輪**: 15 T + 27 hop 抄錄錯誤, 按 node_temps.txt 修正 (21_fix) | 閉合 |
| 18 | 09-09 | 20_audit_independent.py | **審計輪**: 157/157 PASS 覆核全部文檔數字; 04 MW p=0.0995 補註 one-sided; 05 註記表格盲點 | 閉合 |
| 19 | 09-11 | 22_antipodal_temp_check.py | 對徑對三地圖溫度差 (04 待辦 1): (10,25)\|ΔT\|≈22μK、(22,32)≈17-19μK 三地圖穩定; 30 對 vs 隨機 p≈0.07-0.10 邊緣 | 閉合 |
| 20 | 09-11 | 04 §待辦 | 對徑對方向性 (04 待辦 2): 軸-冷斑角 mean=57.0°, 旋轉對照 p=0.427 — **冇方向性** | 閉合 |
| 21 | 09-11 | 06_antipodal_temp_check.md | 對徑對分析完整報告: 三地圖穩定 + 30 對 p≈0.08 邊緣 + 方向性 p=0.43 負結果; 影響評估 | 閉合 |

**時序完整性**: 文件 mtime 單調 (08-16 → 08-17 03:56 → 10:16 → 12:14 → 12:34 → 15:58), 無回溯; 09-09 審計輪修正一律以 ⚠️/ℹ️ 註記標明日期, 不改動原記錄內容；09-11 對徑對後續 (22/06/索引#19-21) 以 📜 註記標明。

## 坑 (記錄俾將來)

1. scipy 新版本 `kstest` 唔接受 `args=` — 要用 `stats.norm(loc,scale).cdf` 傳入
2. matplotlib 新版 `boxplot` 用 `tick_labels=` 唔係 `labels=`
3. 平滑地圖要 cache (`/tmp/smica2_smooth417.fits`) 避免重複 2 分鐘平滑
4. 隨機對照中 shuffle 同 choice 要分開 RNG 操作, 唔好誤用像素索引做 permutation
5. 銀河盤 (|b|<20°) 有 22/60 節點 — 統計要報告剔除前後
