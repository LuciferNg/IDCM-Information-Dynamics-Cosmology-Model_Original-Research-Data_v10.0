# SESSION_START — O30 60 節點微冷系統性

> 交接日期: 2026-08-17
> 來源: O5 延伸 #4 (O5_OPEN_ISSUES.md) — **最高價值**
> **狀態: ✅ 已關閉 (2026-08-21) — 否定 + 離散性完成**

## 問題
60 個 A₅ 節點全部有溫度異常 (IDCM 假說)? 目錄只發現 node0 + node9 兩個強冷 — 其他節點有冇系統性微冷/微熱?

## 結論 (2026-08-21)
**🔴 否定 — 「全部 60 節點有異常」假說不成立。只有 node0/node9 真異常。**
**✅ 離散性完成 — 溫度效應離散: 只有 5 個跨尺度穩定異常節點, 剩餘 55 節點零異常。**

- 60 節點 mean = −1.25 μK vs 隨機 0.00±5.8 → z = −0.21σ
- mean|T| 幅度 = 32.75 vs 隨機 34.95 → z = −0.65σ (單尾 p=0.74) — 反方向
- 剔除 node0+9 後 mean|T| z = −1.45σ (更低)
- 堆疊 radial flat (χ²=0.4/20dof p=1.0), 多尺度全 z∈[−0.55,+0.55]
- 冷/熱 29:31 (p=0.90), power 閾值 11.6 μK, IDCM F₅≈150 μK 幅度已被排除
- 子集效應 (ΔE=0 12節點 19.05 μK, O24 8/10) 保留
- **離散性**: 跨尺度穩定異常 5 節點 (0,9,33,47,53) vs 隨機 0.00±0.00 → p<0.001 🟢🟢
  - node0 冷斑 −134 ✅ | node9 第二冷 −107 ✅ | node33 −83 🟡 (b=−16°)
  - node47 −123 🔴 (O27 銀河面前景) | **node53 +112 🟢🟢 新發現熱異常 (b=−34°, 10/10 尺度全正)**
  - 剩餘 46 節點零異常 (上限 5.3 μK)
- 驗證: 17/17 PASS (scripts/07_verification.py)

## 已確認
- 高緯 31 節點: 2 個 < -2σ (node0 -145.0, node9 -110.6) — 期望 0.7
- 超出隨機嘅冷節點全部係已知結構
- 高緯節點 σ (3.0°) = 48.6 μK

## 未做 (已完成)
- ~~60 節點 mean vs 隨機位置 mean (Welch t-test)~~ ✅ 01
- ~~高緯度子集 (31) mean vs 隨機~~ ✅ 01
- ~~符號不對稱 (冷端 vs 熱端, 相關 O24)~~ ✅ 04
- ~~堆疊 radial profile vs 隨機~~ ✅ 02
- ~~多尺度 (0.5°-10°) 系統性~~ ✅ 03
- ~~1000 隨機控制組~~ ✅ 01-06
- ~~溫度效應離散性 (修正假說)~~ ✅ 08

## 資源
- O5 smooth cache: `../o5_catalog_compare/data/smooth_cache/` (0.5-10° 全尺度)
- a5_nodes: `../cmb_cold_spot/data/a5_nodes.txt` (ICRS! 要轉 Galactic)
- O24: `../o24_extreme_side_asym/` (8/10 冷色重現)
- O3 節點溫度: `../o3_node_temperatures/` (node_temps.txt)

## 判定
~~🟢🟢 >3σ 偏離 → **全部節點有異常** 假說成立~~
~~🟢 2-3σ → 邊緣~~
~~🔴 <2σ → 只有 node0/node9 真異常~~ → **✅ 確認 🔴 <2σ: 只有 node0/node9 真異常 + 離散性 🟢🟢**


---

## ★ 全樹路徑衛生審計註記（2026-10-02，append-only）

> 由 skill `script-chain-reproducibility` 全鏈核對器（`path_hygiene_scan.py`）全樹掃描建立——
> **2026-10-02 首次**。**本節唔改動上方任何內容。**
>
> ⚠️ 本節係**工具層審計**（產物路徑衛生），**唔屬本 O 推導**；亦冇對本 O 任何結論作出判定。
> 完整報告：`path_hygiene_audit_20261002/REPORT.md`

### 〇. 一句話

本目錄命中 **16 個 ghost-tree call site**。

### 一. 命中清單

#### ⚠️ ghost tree 依赖

| # | 檔案:行 | 讀取目標（ghost tree 內）|
|:--|:--|:--|
| 1 | `o30_node_systematics/scripts/01_mean_vs_random.py:27` | `open_problems_fresh/o30_node_systematics/data` |
| 2 | `o30_node_systematics/scripts/01_mean_vs_random.py:109` | `open_problems_fresh/o30_node_systematics/data/01_mean_vs_random.txt` |
| 3 | `o30_node_systematics/scripts/02_stack_radial.py:131` | `open_problems_fresh/o30_node_systematics/data/02_stack_radial.txt` |
| 4 | `o30_node_systematics/scripts/03_multiscale.py:87` | `open_problems_fresh/o30_node_systematics/data/03_multiscale.txt` |
| 5 | `o30_node_systematics/scripts/04_sign_asymmetry.py:51` | `open_problems_fresh/cmb_cold_spot/data/anchored_coloring.txt` |
| … | （另有 11 處）| |

### 二. 處置（別 O 執行；本節只記移交）

```
⚠️ ghost tree 依赖：16 個 call site 讀 `/home/wsl/Projects/IDCM/IDCM-v10.0/`。
   ① 把所需檔搬入本 O `data/`（或記明「唯讀外部輸入」）
   ② `BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` ＋ 相對路徑
   ③ 風險（已量化）：ghost tree 係 2026-09-08 副本（全樹 288K）。全樹 301 個 call site 分類：
      ① 69 個目標仍存在（讀嘅係**陳舊副本**）；② 231 個目標已失踪但同相對路徑在 repo 存在
      （⟹ **改一行即可，零資料損失**）；③ 1 個 repo 內完全冇。逐 O 對照表 → 同報告目錄 `ghost_dispatch.md`
```

> ⚠️ 依據 `idcm-closeout` §8.1：跨 O 問題**只登記移交，唔准就地修**。本節由**外部審計**寫入，
> 本 O 之 session **有權刪去或改寫本節**（上方內容不受影響）——但如果決定保留，
> 請在 GATE / 下輪 round doc 裏明文記下「已接納 / 已處理」。
