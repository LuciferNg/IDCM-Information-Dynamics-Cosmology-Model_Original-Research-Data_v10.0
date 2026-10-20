# O3 新 Session 啟動文件 — 60 節點溫度統計

> 開新 session 時: 載入下面 skills, 然後將「啟動 prompt」複製做第一條訊息。

---

## 所需 Skills（載入順序）

### 1. `polyhedral-graph-analysis`（核心, 必須）
- §7 Real-data verification: SMICA 下載/平滑/統計方法（排列檢驗、隨機著色對照）
- §10 旋轉不變性: 分辨真結構 vs 座標系假象
- 60 節點圖結構 + 著色背景

### 2. `camb-cmb-verification`（輔助, 需要時）
- SMICA 真數據 workflow（下載 URL、平滑 sigma、座標鏈）

### 3. `theoretical-physics-validation`（輔助）
- 統計檢驗設計: null test 同 positive test 並重

## 前置資料（session 內需知）

```
SMICA 地圖: /tmp/smica2.fits (2.01GB, NSIDE 2048, 已下載)
60 節點: /home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt
著色結果: data/anchored_coloring.txt (冷30/熱30)
BFS 距離: 到冷斑距離分佈 1+4+8+11+12+11+8+4+1 (直徑8)
已知: 冷斑 -134.2μK, 節點47 -123.4μK, 節點57 +8.2μK
冷色平均 -12.4μK, 熱色平均 +9.9μK, 相關 r=-0.244
平滑: 4.17° FWHM (sigma = fwhm_rad/(2*sqrt(2*log(2))))
```

## 啟動 Prompt（複製做第一條訊息）

```
開 O3 節點溫度統計專案: /home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o3_node_temperatures/

任務: 完整測量 60 節點喺 Planck SMICA 5° 平滑圖嘅溫度, 建立統計:
1. 60 節點溫度分佈 (mean/std/min/max) + K-S 檢驗 vs 高斯
2. 冷色(30) vs 熱色(30) 分離顯著性 (bootstrap)
3. 節點極端值 vs 1000 組隨機 60 點對比
4. 溫度 vs BFS 距離相關 (Spearman, ladder 檢驗)
5. 節點 57 謎題: 冷色著色但 +8.2μK (解釋?)

載入 skills: polyhedral-graph-analysis (§7 SMICA 方法), camb-cmb-verification

方法: 讀 SMICA → 4.17° FWHM 平滑 → remove_dipole → 60 節點抽值
統計: model-free (bootstrap/排列/K-S), 唔好淨靠平均
誠實: 如果 60 節點溫度冇顯著特殊 → 🔴/🟡 負結果都要記錄
最後: 雙重驗證 (獨立重算) + 更新 01_problem_record + README
```

## 檔案結構

```
o3_node_temperatures/
├── 01_problem_record.md   # 問題 + 狀態表 (已建立)
├── SESSION_START.md       # 本文檔
├── scripts/
│   ├── 01_node_temps.py
│   ├── 02_stats_tests.py
│   ├── 03_extreme_test.py
│   ├── 04_ladder_corr.py
│   └── 05_verify.py
└── data/
```

## 常見坑 (預先提醒)

1. SMICA 讀取前確認檔案完整 (2.01GB)
2. 必須平滑到 4.17° (唔平滑冇信號, 0.07σ)
3. 冷熱分離要用 bootstrap CI, 唔好淨報 mean 差
4. 節點 57 謎題可能係「著色同溫度符號唔直接對應」— 思考但唔好強推
5. 隨機對照要 1000+ 次先穩


---

## ★ 全樹路徑衛生審計註記（2026-10-02，append-only）

> 由 skill `script-chain-reproducibility` 全鏈核對器（`path_hygiene_scan.py`）全樹掃描建立——
> **2026-10-02 首次**。**本節唔改動上方任何內容。**
>
> ⚠️ 本節係**工具層審計**（產物路徑衛生），**唔屬本 O 推導**；亦冇對本 O 任何結論作出判定。
> 完整報告：`path_hygiene_audit_20261002/REPORT.md`

### 〇. 一句話

本目錄命中 **2 處 WRITE**（推導產物寫出 repo 外）；**24 個 ghost-tree call site**。

### 一. 命中清單

#### 🔴 WRITE（違規）

| # | 檔案:行 | 寫去 |
|:--|:--|:--|
| 1 | `o3_node_temperatures/scripts/13_node45_multiscale.py:21` | `/tmp/cache_o3` |
| 2 | `o3_node_temperatures/scripts/15_high4_multiscale.py:18` | `/tmp/cache_o3` |

#### ⚠️ ghost tree 依赖

| # | 檔案:行 | 讀取目標（ghost tree 內）|
|:--|:--|:--|
| 1 | `o3_node_temperatures/scripts/01_node_temps.py:19` | `open_problems_fresh/o3_node_temperatures/data` |
| 2 | `o3_node_temperatures/scripts/01_node_temps.py:50` | `main_problems/p4_cmb_cold_spot/data/a5_nodes.txt` |
| 3 | `o3_node_temperatures/scripts/01_node_temps.py:99` | `main_problems/p4_cmb_cold_spot/data/anchored_coloring.txt` |
| 4 | `o3_node_temperatures/scripts/01_node_temps.py:114` | `open_problems_fresh/o3_node_temperatures/data/node_temps.txt` |
| 5 | `o3_node_temperatures/scripts/01_node_temps.py:119` | `open_problems_fresh/o3_node_temperatures/data/bfs_distances.txt` |
| … | （另有 19 處）| |

### 二. 處置（別 O 執行；本節只記移交）

```
🔴 WRITE 命中：2 處把推導產物寫出 repo。
   ① 改寫入 <O>/data/（BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
   ② 重跑該 script 生成產物，並更新所有引用該 /tmp 路徑嘅地方
   ③ 舊 /tmp 產物**搬入 data/**（唔係複製——避免兩份不一致）
   ④ 重跑 path_hygiene_scan --o-dir 確認 WRITE=0

⚠️ ghost tree 依赖：24 個 call site 讀 `/home/wsl/Projects/IDCM/IDCM-v10.0/`。
   ① 把所需檔搬入本 O `data/`（或記明「唯讀外部輸入」）
   ② `BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` ＋ 相對路徑
   ③ 風險（已量化）：ghost tree 係 2026-09-08 副本（全樹 288K）。全樹 301 個 call site 分類：
      ① 69 個目標仍存在（讀嘅係**陳舊副本**）；② 231 個目標已失踪但同相對路徑在 repo 存在
      （⟹ **改一行即可，零資料損失**）；③ 1 個 repo 內完全冇。逐 O 對照表 → 同報告目錄 `ghost_dispatch.md`
```

> ⚠️ 依據 `idcm-closeout` §8.1：跨 O 問題**只登記移交，唔准就地修**。本節由**外部審計**寫入，
> 本 O 之 session **有權刪去或改寫本節**（上方內容不受影響）——但如果決定保留，
> 請在 GATE / 下輪 round doc 裏明文記下「已接納 / 已處理」。
