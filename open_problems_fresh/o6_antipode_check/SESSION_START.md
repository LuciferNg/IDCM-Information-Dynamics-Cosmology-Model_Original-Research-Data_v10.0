# O6 新 Session 啟動文件 — 對徑點檢驗

> 開新 session 時: 載入下面 skills, 然後將「啟動 prompt」複製做第一條訊息。

---

## 所需 Skills（載入順序）

### 1. `polyhedral-graph-analysis`（核心, 必須）
- §8 Anchor-control tests: 對徑點 = graph automorphism (60/60 著色一致)
- §7 SMICA 統計方法
- 群論背景 (A₅ 冇反演, 174.66°)

### 2. `camb-cmb-verification`（輔助）
- SMICA 平滑/座標鏈

### 3. `theoretical-physics-validation`（輔助）
- 符號分析: 相位 vs 幅度概念

## 前置資料（session 內需知）

```
節點 0 (冷斑): (209°,-57°) = ICRS (48.30,-20.44), -134.2μK, 冷色 anchor
節點 57 (對徑): ICRS (RA=233.7, Dec=22.2), +8.2μK, 冷色 (60/60 一致)
對徑角: 174.66° (180°-174.66° = 5.34° 差, A₅ 冇反演)
BFS: 節點 57 = 距離 8 (直徑唯一端點)
z 值: 兩個都 -3.24 (強制相同, 圖自同構)
60 節點: a5_nodes.txt
SMICA: /tmp/smica2.fits (2.01GB)
```

## 啟動 Prompt（複製做第一條訊息）

```
開 O6 對徑點檢驗專案: /home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o6_antipode_check/

任務: 解釋「節點 57 (對徑點) 冷色著色但 +8.2μK 正溫度」嘅矛盾

背景: 錨點對照測試顯示節點 0 (冷斑, -134μK) 同節點 57 (對徑, +8μK)
都係 z=-3.24 (冷色著色結構唯一有效)。但溫度符號相反!

步驟:
1. 節點 57 區域掃描: 附近 5° 溫度場 (熱斑結構? 定平?)
2. 節點 57 嘅 4 個最近鄰溫度 (著色交替應該熱/冷?)
3. 冷色 30 節點 vs 熱色 30 節點: 溫度正負分佈 (幾多冷色真係負?)
4. 平滑尺度測試: 2°/5°/10° FWHM 下節點 57 溫度變化
5. 理論: A₅ 冇反演 → 對徑點 = 相位對調? (冷色 = 干涉相位, 唔係溫度符號)

載入 skills: polyhedral-graph-analysis (§8 對徑 automorphism), camb-cmb-verification

關鍵概念: IDCM 冷熱 = 干涉相位 (唔係簡單溫度正負)
節點 57 z=-3.24 係「結構對稱」(圖自同構強制), 唔代表「又一個冷斑」
溫度 +8.2μK 可能反映「對徑相位」— 同冷斑相反

誠實: 如果解釋唔到 → 🟡 開放, 記錄矛盾
最後: 雙重驗證 + 更新 01_problem_record + README
```

## 檔案結構

```
o6_antipode_check/
├── 01_problem_record.md   # 問題 + 矛盾 (已建立)
├── SESSION_START.md       # 本文檔
├── scripts/
│   ├── 01_antipode_region.py
│   ├── 02_neighbors.py
│   ├── 03_sign_analysis.py
│   ├── 04_scale_test.py
│   └── 05_verify.py
└── data/
```

## 常見坑 (預先提醒)

1. **z=-3.24 係強制相同**: 節點 57 嘅 z 值 = 圖自同構結果, 唔係獨立證據
2. **+8.2μK 係平滑後值**: 可能受鄰近結構影響 — 掃描區域先落結論
3. **冷色 ≠ 負溫度**: 著色係「相位」, 溫度係「幅度×相位」— 兩者唔直接對應
4. A₅ 冇反演: 對徑點唔係「對稱點」, 唔應該自動同號
5. 如果發現節點 57 區域有熱斑 → 同 O2 熱斑掃描交叉驗證


---

## ★ 全樹路徑衛生審計註記（2026-10-02，append-only）

> 由 skill `script-chain-reproducibility` 全鏈核對器（`path_hygiene_scan.py`）全樹掃描建立——
> **2026-10-02 首次**。**本節唔改動上方任何內容。**
>
> ⚠️ 本節係**工具層審計**（產物路徑衛生），**唔屬本 O 推導**；亦冇對本 O 任何結論作出判定。
> 完整報告：`path_hygiene_audit_20261002/REPORT.md`

### 〇. 一句話

本目錄命中 **17 個 ghost-tree call site**。

### 一. 命中清單

#### ⚠️ ghost tree 依赖

| # | 檔案:行 | 讀取目標（ghost tree 內）|
|:--|:--|:--|
| 1 | `o6_antipode_check/scripts/01_antipode_region.py:160` | `open_problems_fresh/o6_antipode_check/data` |
| 2 | `o6_antipode_check/scripts/01_antipode_region.py:28` | `main_problems/p4_cmb_cold_spot/data/a5_nodes.txt` |
| 3 | `o6_antipode_check/scripts/01_antipode_region.py:161` | `open_problems_fresh/o6_antipode_check/data/antipode_region.txt` |
| 4 | `o6_antipode_check/scripts/02_neighbors.py:153` | `open_problems_fresh/o6_antipode_check/data` |
| 5 | `o6_antipode_check/scripts/02_neighbors.py:25` | `main_problems/p4_cmb_cold_spot/data/a5_nodes.txt` |
| … | （另有 12 處）| |

### 二. 處置（別 O 執行；本節只記移交）

```
⚠️ ghost tree 依赖：17 個 call site 讀 `/home/wsl/Projects/IDCM/IDCM-v10.0/`。
   ① 把所需檔搬入本 O `data/`（或記明「唯讀外部輸入」）
   ② `BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` ＋ 相對路徑
   ③ 風險（已量化）：ghost tree 係 2026-09-08 副本（全樹 288K）。全樹 301 個 call site 分類：
      ① 69 個目標仍存在（讀嘅係**陳舊副本**）；② 231 個目標已失踪但同相對路徑在 repo 存在
      （⟹ **改一行即可，零資料損失**）；③ 1 個 repo 內完全冇。逐 O 對照表 → 同報告目錄 `ghost_dispatch.md`
```

> ⚠️ 依據 `idcm-closeout` §8.1：跨 O 問題**只登記移交，唔准就地修**。本節由**外部審計**寫入，
> 本 O 之 session **有權刪去或改寫本節**（上方內容不受影響）——但如果決定保留，
> 請在 GATE / 下輪 round doc 裏明文記下「已接納 / 已處理」。
