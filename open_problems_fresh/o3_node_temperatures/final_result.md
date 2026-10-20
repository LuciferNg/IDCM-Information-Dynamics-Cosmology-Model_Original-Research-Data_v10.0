# O3 — 60 節點實際溫度統計

## 狀態: 🟡 部分閉合

## 結論
A₅ 60 節點網絡喺 Planck SMICA 4.17° 平滑圖嘅溫度統計完成：冷斑（節點 0, -134.19 μK）係唯一真正極端節點（98.2% 百分位）；「冷/熱」著色係 BFS parity 而非溫度預測；ΔE=0 零能量節點信號部分確認（高緯度 4 節點獨立支持 p=0.0074，但 8/12 節點喺銀河盤受前景污染，node 45 不可靠）；Fibonacci ladder 模型誠實負結果 🔴。

## 關鍵公式
- 著色規則: color[i] = 1 − (hop[i] mod 2)（BFS parity, 非溫度預測器）
- ΔE=0 12 節點: mean|T| = 19.05 μK vs 其他 48 = 36.18 μK, 比例 0.526, permutation p=0.038
- 高緯度剔除後: 4 節點 12.45 vs 34 節點 33.21, 比例 0.375, Welch p=0.0074（三地圖一致 0.375/0.416/0.372）
- 冷熱分離: 差 = -22.31 μK（p=0.06 邊緣, 銀河盤剔除後 p=0.24 消失）
- BFS ladder: Spearman ρ=-0.050（p=0.71）— 冇 ladder 🔴

## 依賴
cmb_cold_spot → O3 → O21 → O22 → O23 → O24 → O25 → O26

## 審計輪 (2026-09-09, 2026-09-11)
20_audit_independent.py 183/183 PASS（第一輪 157/157 + 第二輪 O/P 段覆核對徑對）；02_results 表格 42 cells 抄錄錯誤已修正（ground truth = data/node_temps.txt）；統計結論不變。推導時序索引見 01_problem_record.md。
對徑對後續 (22_antipodal_temp_check.py, 06_antipodal_temp_check.md, 04 待辦, 2026-09-11): 高緯 2 對對徑對三地圖溫度差穩定 (|ΔT|≈17-22μK) 但 30 對整體 vs 隨機 p≈0.08 邊緣；軸-冷斑方向旋轉對照 p=0.43 — 冇方向性。O3 條目內所有待辦已閉合。
