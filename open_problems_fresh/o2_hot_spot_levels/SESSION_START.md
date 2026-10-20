# O2 新 Session 啟動文件 — 熱斑等級驗證

> 開新 session 時: 載入下面 skills, 然後將「啟動 prompt」複製做第一條訊息。

---

## 所需 Skills（載入順序）

### 1. `polyhedral-graph-analysis`（核心, 必須）
- 60 節點 A₅ 軌道圖結構、阻挫著色、SMICA 驗證完整 pipeline
- **§7 Real-data verification**: SMICA 下載/平滑/統計方法（排列檢驗、隨機著色對照）
- **§9 群論邊長**: 26.09° = arccos(cos²δ−sin²δ/2) 閉合
- **§10 旋轉不變性**: 分辨真結構 vs 座標系假象
- 重點: 節點振幅可能係 Fibonacci ladder (F₃/F₄/F₅ by BFS 距離), 唔係 uniform

### 2. `camb-cmb-verification`（輔助, 需要時）
- CAMB 2.0 API 坑（raw_cl, unlensed_scalar, 單位轉換）
- SMICA 真數據 workflow（下載 URL、平滑 sigma、座標鏈）
- 冷斑振幅閉合背景

### 3. `web-access-protocol`（需要時）
- 下載額外數據（Vielva 2007 熱斑目錄、Planck 冷斑目錄）時用

## 前置資料（session 內需知）

```
SMICA 地圖: /tmp/smica2.fits (2.01GB, NSIDE 2048, 已下載)
60 節點: /home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt
著色結果: data/anchored_coloring.txt (冷30/熱30)
阻挫邊: data/frustration_edges.txt (32條)
冷斑: (l,b)=(209°,-57°), ICRS (48.30,-20.44), SMICA 5°平滑 = -134.2μK
對徑點: (29°,+57°), 最近節點 5.34°
斐波等級: F₅=150μK(冷斑✅), F₆=240μK, F₇=390μK, F₈=631μK
```

## 啟動 Prompt（複製做第一條訊息）

```
開 O2 熱斑等級驗證專案: /home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o2_hot_spot_levels/

任務: 用 Planck SMICA 真數據驗證 IDCM Fibonacci 熱斑等級結構
(冷斑=5×RMS=F₅ 已閉合; 預測 F₆=240μK, F₇=390μK, F₈=631μK 熱斑)

載入 skills: polyhedral-graph-analysis (SMICA 驗證 §7, 群論 §9, 旋轉不變 §10), camb-cmb-verification (如需)

執行步驟:
1. 熱節點平均: 60 節點中 30 個「熱色」節點 (anchored_coloring.txt) 喺 SMICA 5° 平滑圖嘅平均溫度 (應 > 0)
2. 對徑點掃描: (29°,+57°) 附近 5° 內最大正溫度
3. 全天最熱點: SMICA 5° 平滑後全天最大值, 對比 F₆/F₇/F₈ 預測
4. 等級擬合: 最熱 N 點 vs Fibonacci 等級表
5. 文獻對比: Vielva 2007 熱斑目錄 (如可取得)

每步: 寫 scripts/NN_*.py + 驗證 + 記錄 (01_problem_record.md 狀態表更新)
誠實記錄: 熱斑等級存在 (🟢) 定唔存在 (🔴/🟡)
最後: 雙重驗證 (獨立重算所有數字) + 更新 01_problem_record + README
```

## 檔案結構

```
o2_hot_spot_levels/
├── 01_problem_record.md   # 問題 + 狀態表 (已建立)
├── scripts/
│   ├── 01_hot_node_mean.py      # 熱節點平均溫度
│   ├── 02_antipode_scan.py      # 對徑點掃描
│   ├── 03_allsky_hotspots.py    # 全天熱點
│   ├── 04_fib_ladder_fit.py     # 等級擬合
│   └── 05_verify.py             # 雙重驗證
├── data/
└── NN_results.md
```

## 常見坑 (預先提醒)

1. SMICA 讀取前確認檔案完整 (2.01GB, 唔好 1.95GB 截斷版)
2. 必須平滑到結構尺度 (冷斑 4.17° FWHM), 唔平滑冇信號
3. 統計用 model-free 檢驗 (排列/隨機對照), 唔好淨靠平均
4. 熱斑等級係「結構預測」— 如果 60 節點熱色平均係正但唔達 F₆, 記錄 🟡 並分析 (可能係 ladder)
5. 負結果都係數據 — 唔好假裝閉合


---

## ★ 全樹路徑衛生審計註記（2026-10-02，append-only）

> 由 skill `script-chain-reproducibility` 全鏈核對器（`path_hygiene_scan.py`）全樹掃描建立——
> **2026-10-02 首次**。**本節唔改動上方任何內容。**
>
> ⚠️ 本節係**工具層審計**（產物路徑衛生），**唔屬本 O 推導**；亦冇對本 O 任何結論作出判定。
> 完整報告：`path_hygiene_audit_20261002/REPORT.md`

### 〇. 一句話

本目錄命中 **20 個 ghost-tree call site**。

### 一. 命中清單

#### ⚠️ ghost tree 依赖

| # | 檔案:行 | 讀取目標（ghost tree 內）|
|:--|:--|:--|
| 1 | `o2_hot_spot_levels/scripts/01_hot_node_mean.py:23` | `open_problems_fresh/o2_hot_spot_levels/data` |
| 2 | `o2_hot_spot_levels/scripts/01_hot_node_mean.py:153` | `open_problems_fresh/o2_hot_spot_levels/data/hot_node_temps.txt` |
| 3 | `o2_hot_spot_levels/scripts/01_hot_node_mean.py:159` | `open_problems_fresh/o2_hot_spot_levels/data/all_node_temps_smoothed.txt` |
| 4 | `o2_hot_spot_levels/scripts/02_antipode_scan.py:19` | `open_problems_fresh/o2_hot_spot_levels/data` |
| 5 | `o2_hot_spot_levels/scripts/02_antipode_scan.py:160` | `open_problems_fresh/o2_hot_spot_levels/data/antipode_scan.txt` |
| … | （另有 15 處）| |

### 二. 處置（別 O 執行；本節只記移交）

```
⚠️ ghost tree 依赖：20 個 call site 讀 `/home/wsl/Projects/IDCM/IDCM-v10.0/`。
   ① 把所需檔搬入本 O `data/`（或記明「唯讀外部輸入」）
   ② `BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` ＋ 相對路徑
   ③ 風險（已量化）：ghost tree 係 2026-09-08 副本（全樹 288K）。全樹 301 個 call site 分類：
      ① 69 個目標仍存在（讀嘅係**陳舊副本**）；② 231 個目標已失踪但同相對路徑在 repo 存在
      （⟹ **改一行即可，零資料損失**）；③ 1 個 repo 內完全冇。逐 O 對照表 → 同報告目錄 `ghost_dispatch.md`
```

> ⚠️ 依據 `idcm-closeout` §8.1：跨 O 問題**只登記移交，唔准就地修**。本節由**外部審計**寫入，
> 本 O 之 session **有權刪去或改寫本節**（上方內容不受影響）——但如果決定保留，
> 請在 GATE / 下輪 round doc 裏明文記下「已接納 / 已處理」。
