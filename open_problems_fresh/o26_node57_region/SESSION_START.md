# SESSION_START — O26 節點 57 附近結構

> **開始**: 2026-08-17
> **來源**: O3 衍生問題 O3-6

## 任務

分析節點 57 (冷斑對徑, +8.21 μK) 附近大尺度結構, 同冷斑區對比。

## 交接點 (從 O3)

- 節點 57: T=+8.21 μK (4.17°), +5.5 μK (10°), hop=8, b=+22°
- 冷斑: -134.19 μK (4.17°), -68.8 μK (10°), b=-57°
- 已有: 三地圖多尺度 cache (/tmp/cache_o3/)
- 方法參考: scripts/18_node45_region.py

## 第一步

複製 node 45 區域分析到節點 57, 對比冷斑 30° 區域
---

# 2026-09-24 外部要求 — 宇微同構（Cosmos-Microcosm Isomorphism）檢定
> **append-only**：本段為新增，以上原文一字不刪。

> **來源**: 調律者要求檢討 Gemini「宇微同構」檢驗建議（4 路線 + A₅ chiral icosahedral 群論內核）。
> **裁決**: **唔開 O216** — 4 路線全部已有專屬 O；按「同一項目缺口唔開新 O」寫入各自 O 嘅 SESSION_START。
> **本 session 範圍**: 只加要求落本文件，**唔處理**呢啲分散問題；由本 O 下個 session 自行解決。
> **收口**: 待各 O 全數解決後，再由原 session 以**集合 + 證偽**統一裁決。

## 修正點（上游）

Gemini 主張「宏觀宇宙與微觀粒子共用同一套 A₅ chiral icosahedral 群論內核」，列 4 條檢驗路線：

| 路線 | Gemini 主張 | 已有專屬 O |
|:--|:--|:--|
| ① | 宇宙雙折射 β ↔ 微觀 δ_CP 群論代數映射 | O26-G1/O43-C（β）+ O123（δ_CP） |
| ② | 質量階層/混合角由 A₅ Molien 級數 + Casimir 特徵值生成 | O136/O137 + O65 |
| ③ | CMB 特定 ℓ 階（6,10,12…）非隨機相位鎖定 / f_NL | O143/O150 + O72 P5 |
| ④ | Σm_ν 絕對值（~0.06 eV 或理論下限） | O71 + O57 |

**Gemini 3 處硬傷（已核）**：
- **E1 範疇錯誤**：A₅ irrep 維數 = {1,3,3,4,5}，**唔係** {6,10,12}；ℓ=6,10,12 係 **invariant-harmonic degree**，且佢**漏咗 ℓ=15,16**（早於 18,20）。
- **E2 誤判判決點**：全球 β 非零唔區分 IDCM vs axion-like field（O26-G1 已明寫「唔係判決性」）。
- **E3 未收窄對稱性**：O143 已裁定幾何點集只係**手性 I（60 等距）**，唔係 I_h（120 自動同構）。

## 問題（本 O 專屬切片）

**本 O 切片 = 路線①（β 側：軸對齊）**。

- 上游狀態（本 O 已判，見 `12_bmode_verdict.md`）：isotropic β = 0.277°±0.057°（4.8σ，ACT+Planck joint）**非判決點**；方向依賴 dipole ❌ null（Planck PR4：no evidence of birefringence dipole）；Dec=18° 軸對齊 🔴 未直接測試。
- **要求（本 O 下個 session 處理）**：
  1. 取 Planck PR4 偏振 map → 直接測試 β-map 同 A₅ 對角軸（328.28°, +18.00°）對齊（即 **O26-G2**，見 `14_g3_plan.md:44` 全 map EB 交叉譜）。
  2. ★ **由本 O 幾何導出 β 值** — 目前 IDCM **完全冇 β 推導**（β 值從未導出）；冇推導就冇資格談「β ↔ δ_CP 代數映射」，Gemini 路線① 現階段係空中樓閣。
  3. 若 β 有結構值 → 再檢 β ↔ δ_CP 映射（δ_CP 側交 O123）。
- 判準：4 Hard Tests（dof cost / MC null 10⁷ / blind out-of-sample / rigidity）。

**狀態**: [ ] 未處理
> 只加註，未改本 O 結論檔（01_problem_record.md / docs/ / final_result.md）；處理後由本 O 自行寫入。
> 全鏈收口（集合 + 證偽）由 2026-09-24 session 統一裁決，本 O 只需完成自己嘅切片。


---

## ★ 全樹路徑衛生審計註記（2026-10-02，append-only）

> 由 skill `script-chain-reproducibility` 全鏈核對器（`path_hygiene_scan.py`）全樹掃描建立——
> **2026-10-02 首次**。**本節唔改動上方任何內容。**
>
> ⚠️ 本節係**工具層審計**（產物路徑衛生），**唔屬本 O 推導**；亦冇對本 O 任何結論作出判定。
> 完整報告：`path_hygiene_audit_20261002/REPORT.md`

### 〇. 一句話

本目錄命中 **14 個 ghost-tree call site**。

### 一. 命中清單

#### ⚠️ ghost tree 依赖

| # | 檔案:行 | 讀取目標（ghost tree 內）|
|:--|:--|:--|
| 1 | `o26_node57_region/scripts/01_node57_region.py:26` | `open_problems_fresh/o26_node57_region/data` |
| 2 | `o26_node57_region/scripts/01_node57_region.py:236` | `open_problems_fresh/o26_node57_region/data/node57_region_results.txt` |
| 3 | `o26_node57_region/scripts/03_node57_antipodal.py:148` | `open_problems_fresh/o26_node57_region/data/node57_antipodal_results.txt` |
| 4 | `o26_node57_region/scripts/04_node57_highlat.py:155` | `open_problems_fresh/o26_node57_region/data/node57_highlat_results.txt` |
| 5 | `o26_node57_region/scripts/05_node57_kstructure.py:224` | `open_problems_fresh/o26_node57_region/data/node57_kstructure_results.txt` |
| … | （另有 9 處）| |

### 二. 處置（別 O 執行；本節只記移交）

```
⚠️ ghost tree 依赖：14 個 call site 讀 `/home/wsl/Projects/IDCM/IDCM-v10.0/`。
   ① 把所需檔搬入本 O `data/`（或記明「唯讀外部輸入」）
   ② `BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` ＋ 相對路徑
   ③ 風險（已量化）：ghost tree 係 2026-09-08 副本（全樹 288K）。全樹 301 個 call site 分類：
      ① 69 個目標仍存在（讀嘅係**陳舊副本**）；② 231 個目標已失踪但同相對路徑在 repo 存在
      （⟹ **改一行即可，零資料損失**）；③ 1 個 repo 內完全冇。逐 O 對照表 → 同報告目錄 `ghost_dispatch.md`
```

> ⚠️ 依據 `idcm-closeout` §8.1：跨 O 問題**只登記移交，唔准就地修**。本節由**外部審計**寫入，
> 本 O 之 session **有權刪去或改寫本節**（上方內容不受影響）——但如果決定保留，
> 請在 GATE / 下輪 round doc 裏明文記下「已接納 / 已處理」。
