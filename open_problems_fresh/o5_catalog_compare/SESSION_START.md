# O5 新 Session 啟動文件 — 冷斑 Catalogue 對比

> 開新 session 時: 載入下面 skills, 然後將「啟動 prompt」複製做第一條訊息。

---

## 所需 Skills（載入順序）

### 1. `polyhedral-graph-analysis`（核心, 必須）
- 60 節點位置 + 著色 + SMICA 驗證背景
- §7 統計方法 (排列檢驗, 隨機對照)

### 2. `web-access-protocol`（核心, 必須）
- 下載 arXiv 論文 (Vielva 2004, Cruz 2005, Planck 2013)
- Anti-bot retry chain (UA → headers → API/mobile → Wayback → Jina)
- PDF 轉文字 (pdftotext)

### 3. `camb-cmb-verification`（輔助）
- 冷斑背景 (振幅/位置閉合)

### 4. `astrophysical-sed-fitting`（唔需要）
- 唔使 (純位置統計, 無 SED)

## 前置資料（session 內需知）

```
60 節點: /home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt
節點 0 = 大冷斑 (209°,-57°) = ICRS (48.30,-20.44)
節點 57 = 對徑點 (174.66° 對面)
天球覆蓋: 60 節點, 邊長 26.09° (每節點 4 鄰)
冷斑尺度: 4.17° FWHM (R8)
已知命中: 大冷斑 = 節點 0 (官方確認)
```

## 啟動 Prompt（複製做第一條訊息）

```
開 O5 冷斑目錄對比專案: /home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare/

任務: 對比公開冷斑目錄 vs 60 A₅ 節點, 計算命中率同顯著性

步驟:
1. 下載目錄數據:
   - Vielva et al. 2004 (astro-ph/0310273) — 大冷斑官方
   - Cruz et al. 2005 (astro-ph/0505341) — WMAP cold spots catalogue (~10+ 冷斑)
   - Planck 2013 (1303.5083) — 冷斑統計
   - 文獻熱斑 (Vielva 2007, 如有)
2. 提取目錄冷斑座標 (RA/Dec 或 l/b)
3. 對比: 每個目錄冷斑 → 最近 A₅ 節點距離
4. 命中率: < 5° 內有節點嘅比例 (vs 隨機期望)
5. 顯著性: 1000 次隨機旋轉 60 節點 → 命中率分佈 → p-value

載入 skills: polyhedral-graph-analysis, web-access-protocol
下載方法: curl + UA + pdftotext (web-access-protocol 反 bot 鏈)

預期: 如果命中率顯著 > 隨機 → 🟢 節點係真結構
      如果得大冷斑一個命中 → 🟡 其他節點係潛伏冷斑
誠實記錄 p-value, 唔好誇大
最後: 雙重驗證 + 更新 01_problem_record + README
```

## 檔案結構

```
o5_catalog_compare/
├── 01_problem_record.md   # 問題 + 目錄候選 (已建立)
├── SESSION_START.md       # 本文檔
├── scripts/
│   ├── 01_fetch_catalogs.py
│   ├── 02_match_nodes.py
│   ├── 03_significance.py
│   ├── 04_scale_check.py
│   └── 05_verify.py
├── data/
│   └── catalogs/          # 下載嘅目錄數據
└── NN_results.md
```

## 常見坑 (預先提醒)

1. **arXiv PDF 下載**: 用 arxiv.org/abs/astro-ph/0505341 → PDF → pdftotext; 如果 bot 擋, 用 export.arxiv.org mirror
2. **Cruz 2005 目錄**: 冷斑數量 (~10-15 個), 座標喺論文表入面 — 要人手/腳本提取
3. **命中率期望值**: 60 節點覆蓋 — 唔係 26%! 要計實際覆蓋率 (節點 5° 內面積)
4. **隨機對照要旋轉節點集**: 唔係隨機生成點 (保留網絡結構)
5. 目錄可能有尺度差異: 冷斑 catalogue 通常用 SMHW R 尺度 — 唔同 R 有唔同冷斑


---

## ★ 全樹路徑衛生審計註記（2026-10-02，append-only）

> 由 skill `script-chain-reproducibility` 全鏈核對器（`path_hygiene_scan.py`）全樹掃描建立——
> **2026-10-02 首次**。**本節唔改動上方任何內容。**
>
> ⚠️ 本節係**工具層審計**（產物路徑衛生），**唔屬本 O 推導**；亦冇對本 O 任何結論作出判定。
> 完整報告：`path_hygiene_audit_20261002/REPORT.md`

### 〇. 一句話

本目錄命中 **1 處 READ 自 agent scratch**（輸入 provenance 缺口）；**4 個 ghost-tree call site**。

### 一. 命中清單

#### 🟡 READ（由 agent scratch / cache 讀入）

| # | 檔案:行 | 讀自 |
|:--|:--|:--|
| 1 | `o5_catalog_compare/scripts/master_full_rerun.sh:46` | `/tmp/smica2_smooth` |

#### ⚠️ ghost tree 依赖

| # | 檔案:行 | 讀取目標（ghost tree 內）|
|:--|:--|:--|
| 1 | `o5_catalog_compare/scripts/01_fetch_catalogs.py:21` | `open_problems_fresh/o5_catalog_compare/data` |
| 2 | `o5_catalog_compare/scripts/01_fetch_catalogs.py:81` | `open_problems_fresh/o5_catalog_compare/data/literature_catalog.json` |
| 3 | `o5_catalog_compare/scripts/02_smica_catalog.py:30` | `open_problems_fresh/o5_catalog_compare/data` |
| 4 | `o5_catalog_compare/scripts/02_smica_catalog.py:158` | `open_problems_fresh/o5_catalog_compare/data/smica_catalog.json` |

### 二. 處置（別 O 執行；本節只記移交）

```
🟡 READ 命中：1 處由 **agent scratch / cache** 讀入（唔係 repo 內絕）。
   scratch 係 24h 閒置即清嘅位置 ⟹ 該輪推導**事後無法重建輸入**。
   ① 把輸入快照搬入 <O>/data/（標明下載日期 + 來源 URL / 本地路徑）
   ② 改 script 讀 repo 內相對路徑
   ③ 若真係不可搬（大數據）⟹ 寫 <O>/data/README_input.md 記下重獲取步驟 + 在同行加
      `# path-hygiene: exempt <理由>`

⚠️ ghost tree 依赖：4 個 call site 讀 `/home/wsl/Projects/IDCM/IDCM-v10.0/`。
   ① 把所需檔搬入本 O `data/`（或記明「唯讀外部輸入」）
   ② `BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` ＋ 相對路徑
   ③ 風險（已量化）：ghost tree 係 2026-09-08 副本（全樹 288K）。全樹 301 個 call site 分類：
      ① 69 個目標仍存在（讀嘅係**陳舊副本**）；② 231 個目標已失踪但同相對路徑在 repo 存在
      （⟹ **改一行即可，零資料損失**）；③ 1 個 repo 內完全冇。逐 O 對照表 → 同報告目錄 `ghost_dispatch.md`
```

> ⚠️ 依據 `idcm-closeout` §8.1：跨 O 問題**只登記移交，唔准就地修**。本節由**外部審計**寫入，
> 本 O 之 session **有權刪去或改寫本節**（上方內容不受影響）——但如果決定保留，
> 請在 GATE / 下輪 round doc 裏明文記下「已接納 / 已處理」。
