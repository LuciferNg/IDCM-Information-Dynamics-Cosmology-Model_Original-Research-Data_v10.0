# O8 新 Session 啟動文件 — 尺度半徑之謎

> 開新 session 時: 載入下面 skills, 然後將「啟動 prompt」複製做第一條訊息。

---

## 所需 Skills

### 1. `polyhedral-graph-analysis`（核心, 必須）
- 60 節點圖結構、群論邊長 (§9)、旋轉不變 (§10)
- SMICA 平滑尺度 (§7)

### 2. `camb-cmb-verification`（輔助）
- SMICA 平滑 workflow

## 前置資料

```
邊長: 26.0913° (已閉合, o1_edge_length)
冷斑 FWHM: 4.17° (R8, 5° 平滑)
節點: cmb_cold_spot/data/a5_nodes.txt
星系團真空: <4.5-5° (crystal_stress 發現)
比例: 4.17/26.09 = 0.16
候選: 26.09/2π = 4.15 (偏差 0.4%!)
```

## 啟動 Prompt

```
開 O8 尺度半徑專案: /home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o8_scale_radius/

任務: 解釋「節點影響範圍 ~5° 但間距 26.09°」嘅尺度之謎

背景: 冷斑 FWHM 4.17° (R8), 節點間距 26.0913° (已閉合)
比例 = 0.16。候選: 26.09/2π = 4.15 (0.4%)?

步驟:
1. 60 節點網絡幾何半徑 (inscribed/circumscribed)
2. 4.17 vs 26.09 比例搜索 (φ 冪/κ/π)
3. 尺度鏈: 26.09 → 4.17 → 冷斑 FWHM 一致性
4. 星系團真空 4.5-5° 交叉 (crystal_stress)
5. 可證偽預測: 其他節點影響範圍 = 4.17°

載入 skills: polyhedral-graph-analysis, camb-cmb-verification

重點: 4.17° = 26.09/2π 係咪真? (0.4% 偏差可能係平滑誤差)
      R8 幾何半徑 vs 觀測 FWHM 關係
誠實: 如果冇閉合 → 🟡 記錄, 唔好強推
最後: 雙重驗證 + 更新 01_problem_record + README
```

## 常見坑

1. FWHM 4.17° 係「平滑後」觀測 — 唔好當精確結構值
2. 26.09/2π = 4.153 偏差 0.4% — 要諗有冇平滑修正
3. 星系團真空 4.5-5° 係另一獨立量 — 交叉驗證用
4. 如果 4.17 同 26.09 冇簡單關係 → 可能係「觀測平滑效應」唔係結構


---

## ★ 全樹路徑衛生審計註記（2026-10-02，append-only）

> 由 skill `script-chain-reproducibility` 全鏈核對器（`path_hygiene_scan.py`）全樹掃描建立——
> **2026-10-02 首次**。**本節唔改動上方任何內容。**
>
> ⚠️ 本節係**工具層審計**（產物路徑衛生），**唔屬本 O 推導**；亦冇對本 O 任何結論作出判定。
> 完整報告：`path_hygiene_audit_20261002/REPORT.md`

### 〇. 一句話

本目錄命中 **23 個 ghost-tree call site**。

### 一. 命中清單

#### ⚠️ ghost tree 依赖

| # | 檔案:行 | 讀取目標（ghost tree 內）|
|:--|:--|:--|
| 1 | `o8_scale_radius/scripts/01_geometry_scale_search.py:24` | `main_problems/p4_cmb_cold_spot/data/a5_nodes.txt` |
| 2 | `o8_scale_radius/scripts/01_geometry_scale_search.py:164` | `open_problems_fresh/o8_scale_radius/data/geometry_scale.txt` |
| 3 | `o8_scale_radius/scripts/02_node_influence_radius.py:134` | `open_problems_fresh/o8_scale_radius/data/radial_profiles.npy` |
| 4 | `o8_scale_radius/scripts/02_node_influence_radius.py:135` | `open_problems_fresh/o8_scale_radius/data/half_radii.npy` |
| 5 | `o8_scale_radius/scripts/02_node_influence_radius.py:22` | `main_problems/p4_cmb_cold_spot/data/a5_nodes.txt` |
| … | （另有 18 處）| |

### 二. 處置（別 O 執行；本節只記移交）

```
⚠️ ghost tree 依赖：23 個 call site 讀 `/home/wsl/Projects/IDCM/IDCM-v10.0/`。
   ① 把所需檔搬入本 O `data/`（或記明「唯讀外部輸入」）
   ② `BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` ＋ 相對路徑
   ③ 風險（已量化）：ghost tree 係 2026-09-08 副本（全樹 288K）。全樹 301 個 call site 分類：
      ① 69 個目標仍存在（讀嘅係**陳舊副本**）；② 231 個目標已失踪但同相對路徑在 repo 存在
      （⟹ **改一行即可，零資料損失**）；③ 1 個 repo 內完全冇。逐 O 對照表 → 同報告目錄 `ghost_dispatch.md`
```

> ⚠️ 依據 `idcm-closeout` §8.1：跨 O 問題**只登記移交，唔准就地修**。本節由**外部審計**寫入，
> 本 O 之 session **有權刪去或改寫本節**（上方內容不受影響）——但如果決定保留，
> 請在 GATE / 下輪 round doc 裏明文記下「已接納 / 已處理」。
