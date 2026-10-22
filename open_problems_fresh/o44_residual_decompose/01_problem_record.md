# O44 — p=0.072 剩餘信號分解 (Residual Signal Decomposition)

> **創建日期**: 2026-08-21
> **狀態**: ✅ 完成 (2026-08-21, 已由 O29 完成並 port 至 O44)
> **來源**: O5 衍生 (o5_catalog_compare/O5_OPEN_ISSUES.md #3)
> **原編號**: O29（舊系列）→ 新系列 O44
> **驗證**: 47/47 file simulation verifier + 獨立重算 (fresh seed) 雙重確認

---

## 問題陳述

O5 顯著性測試: 全部 35 斑 (SMICA 15冷+14熱 + 文獻) mean-nearest **p=0.042** 🟢,
但**減大冷斑後 p=0.072** 🟡 唔再顯著。

**問題**: 剩餘 p=0.072 嘅弱信號係咪有第二結構 (node9/node47) 貢獻? 定係純粹噪聲?

## 核心結論 🔴

**p=0.072 殘餘信號 = 大冷斑家族尾巴 (6 斑), 唔係第二結構 (node9/node47) 貢獻。**

移除成個冷斑族 (lit#1 + SMICA-c2 + 4 sub-spots = 6 斑全部最近 node 0) 後:

| 子集 | n | p (1000-rot) | p (10,000-rot) |
|:---|:---:|:---:|:---:|
| 全部 35 斑 | 35 | 0.042 | — |
| 減 lit#1 (O5 原本) | 34 | 0.072 | 0.066 |
| **減冷斑族 (6 斑)** | **29** | **0.365** | **0.385** |
| 減冷斑族 + node9 斑 | 27 | 0.324 | 0.340 |

O5 之前只減咗 lit#1 (1 斑), 但冷斑族其實有 **6 斑** — 全部移除後信號完全消失 (p→0.385)。

## 詳細結果

### Node 9 — 明確排除 🟡→🔴

| 檢驗 | 結果 | 判決 |
|:---|:---|:---:|
| node9 相關斑 (c3, c11) 平均距離 | 11.36° ± 1.02° vs 其餘 8.69° | 🔴 更遠 |
| permutation P(更近) | 0.788-0.792 | 🔴 冇更近傾向 |
| 移除 node9 斑後 p | 0.042 (1000-rot) / 0.041 (10k) | 🟡 反而**更顯著** |
| O21 GRF bootstrap (4.17°) | z=-1.46σ, p=8.2% | 🔴 高斯隨機 |

### Node 47 — 零貢獻 🔴

| 檢驗 | 結果 |
|:---|:---|
| 最近 node 47 嘅斑 | **冇** (0 斑) |
| 最近 catalogue 斑到 node 47 | SMICA-h10 @ 23.18° |
| O27 判定 | 前景污染 (b=-8.58°, R3 mask 遮住) |

### Leave-one-out Δp 排行

**信號載體 (移除後 p 升)** — 全部係近節點斑:

| 移除 | p | Δp | node | d |
|:---|:---:|:---:|:---:|:---:|
| CS sub-spot B (Cruz) | 0.101 | +0.029 | 0 | 1.14° |
| SMICA-h2 | 0.099 | +0.027 | 53 | 1.11° |
| CS sub-spot C (Cruz) | 0.093 | +0.021 | 0 | 3.21° |
| CS sub-spot D (Cruz) | 0.085 | +0.013 | 0 | 3.46° |
| SMICA-c2 | 0.082 | +0.010 | 0 | 0.75° |

**5 個最大 leverage 斑入面 3 個係冷斑族 (node 0)**。確定性 Δobs (無 MC 噪音) 確認同一排序。

### Bootstrap 分解

| 量 | 值 |
|:---|:---|
| bootstrap p 分佈 | mean 0.163 ± 0.148, median 0.116 |
| draws with p < 0.05 | **22.2%** |
| draws with p < 0.10 | 44.3% |

→ 只有 22% bootstrap resample 達到 p<0.05 — 同「單一族信號」圖像一致。

## 判定標準

| 判定標準 | 結果 | 判決 |
|:---|:---|:---:|
| 🟢 移除特定斑 p 大幅變 → 該斑係信號 | 移除冷斑族 6 斑 → p 0.072→0.385 | ✅ 冷斑族係信號 |
| 🔴 全部移除都 ~0.07 → 純噪聲 | 移除冷斑族後 ~0.37 | ✅ 冇第二結構 |
| 🟡 部分貢獻 → 邊緣信號 | node9 反信號, node47 零貢獻 | 🔴 排除 |

## 獨立重算確認 (2026-08-21, fresh seed 777)

| 量 | 記錄 | 獨立重算 | 一致 |
|:---|:---|:---|:---:|
| 冷斑族 6 斑 | lit#1+c2+sub-spots A-D | 完全相同 (deterministic) | ✅ |
| baseline-34 p | 0.072 (1000-rot) / 0.066 (10k) | 0.0641 (10k, seed 777) | ✅ MC 範圍 |
| 減冷斑族 p | 0.365 / 0.385 | 0.3805 (10k, seed 777) | ✅ |
| 減 node9 斑 p | 0.051 / 0.042 | 0.0411 (10k, seed 777) | ✅ |
| node9 距離差 | +2.66° | +2.66° | ✅ |
| P(node9 closer) | 0.7925 | 0.7882 | ✅ |
| node47 最近斑 | 23.18° | 23.18° | ✅ |
| bootstrap p<0.05 | 0.222 | 0.220 | ✅ |

## 陷阱記錄

⚠️ **MC rotation tests 係 rng-stream-order 依賴** — 要重現 O5 嘅 p=0.072 必須用 O5 嘅子集順序 consume rotations (all→lit→cold→hot→minus) 先做 LOO；唔同順序會俾 p=0.052。

⚠️ **match_results.json node 編號係 OLD a5_nodes 編號** (冷斑 = node 57)。scripts 已用新版 a5_nodes.txt (冷斑 = node 0) 重新計算 nearest-node 距離 — 幾何距離不變, 只係 node ID 移位。

## 推導時序索引 (Derivation Chronology Index)

> 依序記錄推導鏈每一步嘅時間、產出、驗證狀態。**只列已發生事件, 唔作回溯推導。**

| 序 | 日期 | 步驟 | 產出 | 驗證 |
|:-:|:---|:---|:---|:---:|
| 1 | 2026-08-21 | 讀取 SESSION_START + 01_problem_record + O5 數據 | 問題理解 | ✅ |
| 2 | 2026-08-21 | 發現 match_results node 編號係舊版 → 用新版 a5_nodes 重算 | 冷斑族 6 斑定義 (deterministic) | ✅ |
| 3 | 2026-08-21 | **scripts/01** LOO 分解 + O5-aligned 基線 | `data/decompose_results.json` | ✅ 重現 p=0.042/0.072 |
| 4 | 2026-08-21 | **scripts/02** 高旋轉數 + bootstrap + leverage + node9 | `data/bootstrap_decompose.json` | ✅ 1000/10000-rot 確認 |
| 5 | 2026-08-21 | 關鍵發現: O5 只減 lit#1, 冷斑族其實有 6 斑 | 減全族 → p=0.365 (決定性) | ✅ |
| 6 | 2026-08-21 | **scripts/03** O21 對接 | `data/o21_docking.json` | ✅ node9 z=-1.46σ 高斯隨機 |
| 7 | 2026-08-21 | **scripts/04** file simulation verifier | VERIFIER_RESULT.md | ✅ **47/47 PASS** |
| 8 | 2026-08-21 | **scripts/05** 獨立重算 (fresh seed 777) | `data/recheck_run.log` | ✅ 全部 MC 範圍內一致 |
| 9 | 2026-08-21 | 最終核對報告 | FINAL_RECHECK.md | ✅ 無幻覺, 無遺漏 |
| 10 | 2026-08-31 | O29 → O44 重編號 | 01_problem_record.md 更新 | ✅ 結果 port 至 O44 |
| 11 | 2026-09-12 | **全鏈重跑** (scripts 01→05, 路徑遷移後) | 重跑 JSON + audit_evidence.json | ✅ 47/47 PASS (見 NN_results.md 附錄) |

**關鍵時序規則**: 結論 (🔴 冇第二結構) 於步驟 5 (2026-08-21) 定案, 步驟 8/11 係獨立確認, 唔改變結論。所有驗證都係「確認」而非「新增推導」。

## 檔案

```
o44_residual_decompose/
├── 01_problem_record.md           # 本記錄 (已更新為 ✅ 完成)
├── scripts/
│   ├── 01_leave_one_out.py       # LOO + 冷斑族 + 定向移除 (O5-aligned rng)
│   ├── 02_bootstrap_decompose.py # 高旋轉數 + bootstrap + leverage + node9 檢驗
│   ├── 03_o21_docking.py         # O21 對接 + verdict table
│   ├── 04_verify.py              # file simulation verifier (47/47 PASS)
│   └── 05_independent_recheck.py # 獨立重算 (fresh seed, 2026-08-21)
├── data/
│   ├── decompose_results.json    # LOO + 子集結果
│   ├── bootstrap_decompose.json  # 高旋轉數 + bootstrap + leverage
│   ├── o21_docking.json          # O21 對接摘要
│   ├── recheck_run.log           # 獨立重算輸出
│   └── audit_evidence.json       # 2026-09-12 文檔-數據一致性審計
├── data_backup_orig/             # 原始 (2026-08-21) data 備份, 唔改動
├── NN_results.md                 # 完整結果報告 (+ 2026-09-12 重跑驗證附錄)
├── VERIFIER_RESULT.md            # 47/47 驗證記錄
└── FINAL_RECHECK.md              # 最終核對報告
```

## 後續

- ✅ O5 嘅「潛伏冷斑假說」已由 **O52 閉合** (2026-08-21): 🔴 冇潛伏冷斑 — 60 節點全部尺度 |z|<0.4σ, 只有 node0/node9 係真異常
- 🔴 熱斑幾何歸屬 (F₆/F₇ 距離節點 8-9°) 仍然開放 — 同本報告無關但係 O5 遺留問題
- 🟡 O52 帶出嘅新問題: 點解係「特定節點」(node0/node9/ΔE=0 子集) 而唔係「全部節點」有異常? 相位機制假說 (異常 ∝ cos θ_i, 大部分 θ_i≈π/2 正交) 值得開新 O 系列