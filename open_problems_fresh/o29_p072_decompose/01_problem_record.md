# O29: mean-nearest p=0.072 剩餘信號分解 — 有冇第二結構貢獻?

> **來源**: O5 衍生 (o5_catalog_compare/O5_OPEN_ISSUES.md #3)
> **狀態**: ✅ 已完成 (2026-08-21)
> **建立**: 2026-08-17
> **結論**: 🔴 冇第二結構 — p=0.072 殘餘 = 大冷斑家族 (6 斑) 尾巴。移除冷斑族 → p=0.385 (純噪聲)。node9/node47 排除。
> **驗證**: 47/47 file simulation verifier PASS (scripts/04_verify.py)

## 問題陳述

O5 顯著性測試: 全部 35 斑 (SMICA 15冷+14熱 + 文獻) mean-nearest **p=0.042** 🟢, 但**減大冷斑後 p=0.072** 🟡 唔再顯著。

**問題**: 剩餘 p=0.072 嘅弱信號係咪有第二結構 (node9/node47) 貢獻? 定係純粹噪聲?

## 已知數據

| 量 | 值 |
|:---|:---|
| 全部 35 斑 mean-nearest | p=0.042 (z=-1.77σ) |
| 減大冷斑後 | p=0.072 (z=-1.47σ) |
| 大冷斑距離 node0 | 0.00° |
| node9 已確認冷結構 | 三地圖 2.6% 一致 |
| node47 | -135.7 μK 但 b=-8.6° (前景風險) |

## 要驗證

1. **逐斑移除**: 每次移除一個斑, 重新計算 mean-nearest p — 邊個斑對 p 影響最大?
2. **node9 貢獻**: 移除 node9 對應嘅斑 (1.0° cold #?) 後 p 變化
3. **bootstrap 分解**: 對 35 斑做 leave-one-out bootstrap, 計算每個斑嘅 Δp
4. **方向檢驗**: 剩餘斑嘅最近節點距離係咪偏向近 (單尾)?
5. **同 O21 對接**: node9 嘅獨立確認 (NODE9_ANALYSIS) 同 p=0.072 有冇關聯

## 判定標準

- 🟢 移除特定斑後 p 大幅改變 (>0.05) → 該斑係信號來源
- 🔴 全部逐斑移除後 p 都係 ~0.07 → 純噪聲, 冇第二結構
- 🟡 部分斑貢獻但唔穩定 → 邊緣信號

## 推導時序索引 (2026-08-21)

**基於腳本依賴鏈同推導邏輯重建, 非檔案時間戳 (搬遷後不可靠)**

| 階段 | 腳本 | 數據/文檔 | 內容 |
|:---:|:---|:---|:---|
| 1. LOO 分解 | scripts/01_leave_one_out.py | decompose_results.json | 35 斑逐個移除 (1000-rot O5-aligned), 發現冷斑族 6 斑 (全部最近 node 0) |
| 2. 高旋轉數確認 | scripts/02_bootstrap_decompose.py | bootstrap_decompose.json + bootstrap_run.log | 10,000-rot 確認: 減冷斑族 p=0.385, 減 node9 p=0.042; bootstrap 2000 draws |
| 3. O21 對接 | scripts/03_o21_docking.py | o21_docking.json | node9 GRF z=-1.46σ/p=8.2%, node47 零貢獻 (23.18°), bootstrap 摘要 |
| 4. 檔案驗證 | scripts/04_verify.py | VERIFIER_RESULT.md | 47/47 file simulation verifier PASS |
| 5. 獨立重算 | scripts/05_independent_recheck.py | recheck_run.log | Fresh seed (777) 10k-rot 獨立確認: 所有關鍵 p 值喺 MC 範圍內一致 |
| 6. 熱斑幾何歸屬 (2026-09-11) | scripts/06_hotspot_attribution.py + 07_hotspot_verify.py | hotspot_attribution.json | 14 SMICA 熱斑 vs 節點/三角形/阻挫邊: 緯度修正後全部 \|z\|<1.8, 🔴 冇歸屬; 21/21 verifier |

**時序規則**: 階段 1-2 係主推導 (冷斑族發現 → 高旋轉數確認); 階段 3 係跨 O 對接; 階段 4-5 係驗證層, 冇引入新推導, 冇回溯污染前階段結論; 階段 6 係後續獨立問題 (熱斑幾何歸屬, O5 遺留), 冇回溯污染前階段「冇第二結構」結論。

## 檔案 (建立時)

```
scripts/01_leave_one_out.py
scripts/02_bootstrap_decompose.py
scripts/03_o21_docking.py
scripts/04_verify.py
scripts/05_independent_recheck.py
scripts/06_hotspot_attribution.py
scripts/07_hotspot_verify.py
data/decompose_results.json
data/bootstrap_decompose.json
data/bootstrap_run.log
data/o21_docking.json
data/recheck_run.log
data/hotspot_attribution.json
NN_results.md
VERIFIER_RESULT.md
FINAL_RECHECK.md
```
