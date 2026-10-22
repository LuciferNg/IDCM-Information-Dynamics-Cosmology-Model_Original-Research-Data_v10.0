# SESSION_START — O28 Planck gp10 mask 校正

> 交接日期: 2026-08-17
> 來源: O5 延伸 #2 (O5_OPEN_ISSUES.md)
> **關閉日期: 2026-08-21 — 🔴 gp10 冇節點對應 (NN_results.md)**

## 問題
Planck 第二冷斑 gp10 (32°,-8°) 最近節點 node21 距離 10.1° (唔命中)，但 gp10 區域部分被銀河面遮擋 — 需要 mask 校正。

> ⚠️ 時序標註: 本段「10.1°」係 **O5-era framing (2026-08-17 交接時)**；frame-corrected closure 值為 **10.05°** (2026-08-21, 見下「已確認」)。早期 framing 保留為合法歷史，唔以推導時序回溯污染。

## 已確認
- node21: 10.05° (+95.5 μK 熱!) — 距離確認, 熱確認
- node26: 20.25° (-48.3 μK)
- node22: 24.02° (-23.6 μK)
- **mask 校正後 centroid 移離節點 (18-20°)** — node26/22 唔喺 gp10 範圍

## 已完成 (2026-08-21)
- [x] gp10 flood-fill 實際範圍提取 (4 尺度 × 4 mask 門檻)
- [x] mask 校正後中心偏移 (bcut 5/10/15)
- [x] 校正後節點距離
- [x] node26/22 喺 gp10 範圍內? (唔喺)
- [x] 隨機對照 (同樣 mask 情況) — P(≤10.05°)=0.477 完全正常
- [x] Planck Nside=16 統計重現 (variance 0.75×, skew +0.12 — 失敗)
- [x] 0.5° 細尺度 peak cross-map (前景確認)
- [x] Verifier 20/20 PASS (05_verify.py)
- [x] Doc-vs-data verifier 32/32 PASS (06_doc_verify.py, close-out)
- [x] 全 scripts 重跑可重現
- [x] 覆蓋率 audit: 全部發現/計算/驗證已寫入記錄文檔
- [x] 衍生開放問題 audit: 冇新 O (O27/O29/O30 獨立)

## 資源
- Planck 2013: `../o5_catalog_compare/data/catalogs/planck2013.txt`
- SMICA cache: `../o5_catalog_compare/data/smooth_cache/` (4.17° 主用)
- NILC/Commander cache: 同目錄 (cross-map)

## 判定 (最終)
```
🟢 校正後中心 < 5° 某節點 → 第二冷斑命中   ❌ 唔成立
🔴 校正後仍然 10°+ → gp10 冇節點對應     ✅ 成立 (10.05° → 校正後 18-20°)
🟡 node26/22 喺邊緣 → 部分對應            ❌ 唔成立
```

**O28 判定: 🔴 gp10 冇節點對應 — 且「gp10 冷斑」本身喺 SMICA 中尺度存疑 (variance 低, skew 正, 唯一冷特徵係前景)**


---

## ★ 全樹路徑衛生審計註記（2026-10-02，append-only）

> 由 skill `script-chain-reproducibility` 全鏈核對器（`path_hygiene_scan.py`）全樹掃描建立——
> **2026-10-02 首次**。**本節唔改動上方任何內容。**
>
> ⚠️ 本節係**工具層審計**（產物路徑衛生），**唔屬本 O 推導**；亦冇對本 O 任何結論作出判定。
> 完整報告：`path_hygiene_audit_20261002/REPORT.md`

### 〇. 一句話

本目錄命中 **1 個 ghost-tree call site**。

### 一. 命中清單

#### ⚠️ ghost tree 依赖

| # | 檔案:行 | 讀取目標（ghost tree 內）|
|:--|:--|:--|
| 1 | `o28_gp10_mask/scripts/01_gp10_extract.py:26` | `open_problems_fresh/o28_gp10_mask/data` |

### 二. 處置（別 O 執行；本節只記移交）

```
⚠️ ghost tree 依赖：1 個 call site 讀 `/home/wsl/Projects/IDCM/IDCM-v10.0/`。
   ① 把所需檔搬入本 O `data/`（或記明「唯讀外部輸入」）
   ② `BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` ＋ 相對路徑
   ③ 風險（已量化）：ghost tree 係 2026-09-08 副本（全樹 288K）。全樹 301 個 call site 分類：
      ① 69 個目標仍存在（讀嘅係**陳舊副本**）；② 231 個目標已失踪但同相對路徑在 repo 存在
      （⟹ **改一行即可，零資料損失**）；③ 1 個 repo 內完全冇。逐 O 對照表 → 同報告目錄 `ghost_dispatch.md`
```

> ⚠️ 依據 `idcm-closeout` §8.1：跨 O 問題**只登記移交，唔准就地修**。本節由**外部審計**寫入，
> 本 O 之 session **有權刪去或改寫本節**（上方內容不受影響）——但如果決定保留，
> 請在 GATE / 下輪 round doc 裏明文記下「已接納 / 已處理」。
