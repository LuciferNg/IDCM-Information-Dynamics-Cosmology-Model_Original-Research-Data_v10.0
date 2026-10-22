# O52 — 60 節點系統性微冷/微熱檢驗 (Node Systematics)

> **創建日期**: 2026-08-21
> **狀態**: ✅ 主體已完成 (2026-08-21) + 🟡 剩餘開放 (2026-08-31) → 🔴 ΔE=0 判死, **O52 完全閉合** (2026-09-11)
> **來源**: O5 衍生 (o5_catalog_compare/O5_OPEN_ISSUES.md #4)
> **前置**: O5 (冷斑目錄 🟢), O7 (阻挫邊 🟢), O21 (node9 🟢), O25 (尺度譜 🟢), O28 (gp10 ❌)
> **原編號**: O30（舊系列）→ 新系列 O52
> **主體結論**: 🔴 冇系統性微冷/微熱 — 全部尺度 |z|<0.4σ, 堆疊 profile 全部 |z|<0.6σ。只有 node0/node9 係真異常。IDCM「全部 60 節點有異常」假說需修正。
> **驗證**: 54/54 file simulation verifier PASS (scripts/03_verify.py)
> **⚠️ 2026-09-11 追擊註**: ΔE=0 12節點抑制經多頻譜最後裁決 → 🔴 判死 (docs/02_deltaE0_verdict_20260911.md)。O52 無剩餘開放問題。
> 
> ## 🟡 剩餘開放問題 (2026-08-31, 全部已處理 2026-09-11)
> 
> | # | 問題 | 狀態 | 最新結果 |
> |:--:|:-----|:----:|:---------|
> | 1 | **ΔE=0 12節點抑制 — 跨地圖驗證** | 🔴 判死 (2026-09-11) | 4.17° 抑制只存在於組件分離地圖 (SMICA/NILC/Commander p=0.036-0.055); HFI 100/143/217 GHz 完全冇重現 (方向相反 p≥0.99); 高緯子集 0/6 地圖達 p<0.05。多頻譜否證 → 組件分離/前景假象。docs/02_deltaE0_verdict_20260911.md, scripts/06_deltaE0_verdict.py |
> | 2 | **相位機制假說 — 點解係特定節點？** | 🟡 已移交 O143 | 4 步算子化框架已建立, Step 1 (𝒫) 🟢, Step 2 (T_pipe) 🟢, Step 3/4 (θ_i^ind) 🟡 見 o143/ |
> | 3 | **熱節點系統性 (O24 相關)** | 🟡 已部分處理 | O52 已顯示冇整體熱系統性, 但 node53 熱異常 (+112 μK) 已獨立確認

---

## 問題陳述

IDCM 核心假說: **60 個 A₅ 節點全部有溫度異常**（拓撲縫合節點）。
O5 目錄對比只發現 2 個強冷 (node0 + node9) — 其他 58 個冇對應目錄。

**關鍵問題**: 其餘節點係咪有**系統性微冷/微熱**（低於目錄閾值, 但統計上可檢測）?

## 已知數據

| 量 | 值 |
|:---|:---|
| 高緯度節點 (|b|≥30°) | 31 個 |
| 其中 < -2σ | 2 個 (node0 -145.0, node9 -110.6) |
| 隨機期望 < -2σ | 0.7 個 |
| 高緯節點 σ (3.0°) | 48.6 μK |
| 大冷斑 | node0 (-145.0) |
| 第二冷 | node9 (-110.6) 已獨立確認 |

## 要驗證

1. **整體均值檢驗**: 60 節點 mean vs 隨機位置 mean (t-test / Welch) — 係咪整體偏冷/偏熱?
2. **高緯度子集**: 31 個高緯節點 mean vs 隨機 (避開銀河面污染)
3. **符號不對稱**: 冷端 vs 熱端 (O24 相關: 冷端 8/10 vs 熱端 6/10)
4. **堆疊法**: 60 節點溫度堆疊 (平均 radial profile) vs 隨機位置堆疊
5. **多尺度**: 0.5°-10° 每尺度重複 — 系統性隨尺度點變?
6. **控制組**: 隨機 60 點 (同緯度分佈) 重複 1000 次 → 零假設分佈

## 判定標準

- 🟢🟢 60 節點 mean 偏離隨機 >3σ → **全部節點有異常** 假說成立
- 🟢 偏離 2-3σ → 邊緣, 需要更大樣本
- 🔴 偏離 <2σ → 只有 node0/node9 係真異常, 其他節點冇系統性

## ⚠️ O27 前置發現 (2026-08-21) — 必須納入

O27 (node47 前景分析) 確認:
1. **60 節點中 15/60 被 R3 CMB common mask 遮住** (全部 |b|<20°, 銀河面)
2. node47 案例: SMICA 喺 |b|<20° 有塵埃殘留假象 (SMICA -136 μK vs 143 GHz +18 μK)
3. **本分析必須分層執行**: masked (15) vs unmasked (45) 節點分開統計
4. **新增測試 7**: 只睇 unmasked 45 節點 (R3 CMB mask 內) 嘅系統性 — 排除前景污染
5. **新增測試 8**: 對任何顯著異常節點做多頻譜篩查 (143/217 GHz, O27 方法)
6. 高緯度子集 (|b|≥30°) 由 31 個更新: R3 mask 後實際 unmasked 高緯節點數要重新數

## 對 IDCM 嘅意義

呢個係 O5 假說嘅**最終考驗**:
- 如果成立 → 60 節點全部係拓撲縫合點, 溫度異常係普遍現象
- 如果唔成立 → 只有少數節點有異常, 需要修正「全部節點有異常」假說

## 檔案

```
o52_node_systematics/
├── 01_problem_record.md      ← 本文件
├── scripts/
│   ├── 01_node_vs_random_mean.py  60節點 vs 隨機控制組 (多尺度)
│   ├── 02_stacking_profile.py     堆疊 radial profile
│   ├── 03_verify.py               file simulation verifier (54/54)
│   ├── 04_independent_recheck.py  獨立重算 (fresh fits sampling)
│   ├── 05_deltaE0_crossmap.py     ΔE=0 跨地圖驗證 (2026-08-31)
│   └── 06_deltaE0_verdict.py      ΔE=0 最後裁決 — 多頻譜 + 尺度掃描 (2026-09-11)
├── data/
│   └── o52_deltaE0_verdict.json   # 06 裁決結果 (20k perms × 5 seeds + per-node 4.17° 值)
├── docs/
│   └── 02_deltaE0_verdict_20260911.md   # 🔴 ΔE=0 判死裁決
├── NN_results.md
└── VERIFIER_RESULT.md
```

## 推導時序索引 (2026-08-21 + 2026-08-31 後續)

**基於腳本依賴鏈同推導邏輯重建, 非檔案時間戳 (搬遷後不可靠)**

| 階段 | 腳本 | 數據/文檔 | 內容 |
|:---:|:---|:---|:---|
| 1. 多尺度均值 | scripts/01_node_vs_random_mean.py | o52_systematics.json | 8 尺度 × 7 統計; 🚨 frame bug (ICRS 直接採樣) → 修正為 Galactic lonlat, R3 mask 45/60 同 O27 一致 |
| 2. 堆疊 profile | scripts/02_stacking_profile.py | o52_stacking.json + stacking_run.log | 7 annulus (0-14°) × 1000 random stacks, 全部 \|z\|<0.6 |
| 3. 檔案驗證 | scripts/03_verify.py | VERIFIER_RESULT.md | 54/54 file simulation verifier PASS |
| 4. 獨立重算 | scripts/04_independent_recheck.py | recheck2_run.log | Fresh fits sampling (seed 888, 500 stacks): 全部數值一致 |
| 5. ΔE=0 跨地圖 (2026-08-31) | scripts/05_deltaE0_crossmap.py | o52_deltaE0_crossmap.json | Raw/0.3°/4.17° × SMICA/NILC/Commander: ΔE=0 抑制係平滑尺度依賴, raw SMICA 冇抑制 → 🟡 非穩健 |
| 6. ΔE=0 最後裁決 (2026-09-11) | scripts/06_deltaE0_verdict.py | o52_deltaE0_verdict.json + docs/02_deltaE0_verdict_20260911.md | 20k perms × 5 seeds; HFI 100/143/217 GHz 多頻譜 + 平滑尺度掃描: 抑制只存在於組件分離地圖, 多頻譜冇重現 + 高緯 0/6 達 p<0.05 → 🔴 判死, O52 完全閉合 |

**時序規則**: 階段 1-2 係主推導 (frame 修正 → 堆疊確認); 階段 3-4 係驗證層, 冇引入新推導; 階段 5 係後續獨立問題 (ΔE=0 跨地圖), 冇回溯污染前階段「60 節點無系統性」結論; 階段 6 (2026-09-11) 為最終裁決, 判死階段 5 嘅 🟡 開放問題, 主體結論 (階段 1-4) 不變。
