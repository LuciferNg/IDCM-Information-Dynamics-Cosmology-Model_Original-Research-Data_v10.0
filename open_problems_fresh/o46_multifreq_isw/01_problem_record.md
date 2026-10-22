# O46 — 多頻段穩定性 + ISW 解耦 (Multifrequency & ISW)

> **創建日期**: 2026-08-21
> **狀態**: 🟢 **已閉合** (2026-08-31)
> **閉合結論**: 6 種 CMB maps 一致 (std 0.98 μK); 前景污染解釋 raw 頻段差異; ISW 文獻支持 IDCM A_prim = A_total = 134.2 μK
> **來源**: O42 通道 2+4 → 新系列獨立 O46
> **前置**: O41 (A=134.2μK 🟢), O42 (6 方法獨立量度 🟢), O5 (冷斑目錄 🟢)

---

## 問題陳述

O41 閉合 A = 134.2 μK（零參數）。需要兩個獨立驗證通道:

### 通道 A: 多頻段組份分離穩定性

SMICA 係多頻段合成 map。要確認 A 唔係組份分離假象:
- 檢查 30/44/70/100/143/217/353 GHz 原始頻段 map 分別量度 A
- 對照 6 種 component-separated CMB maps (SMICA/NILC/Commander/SEVEM)
- 若 CMB maps 一致 + 頻段差異由前景解釋 → A 係 CMB 原生訊號

### 通道 B: 視線方向超空洞 ISW 解耦

| 關鍵物理 | IDCM | ΛCDM |
|:---------|:-----|:-----|
| 暗能量 | 冇 → 冇 ISW | 有 → ISW 存在 |
| 冷斑 A_prim | 134.2 μK (ISW=0) | 94-124 μK (ISW=−10~−40) |
| Eridanus Supervoid 貢獻 | 0 μK | −10~−40 μK |

- 文獻: Planck 2015/Finelli 2016: ISW 最多解釋 ~10 μK (marginal)
- 可證偽預言: 若 ISW 貢獻 > 5 μK → IDCM A 公式需重新詮釋

---

## 推導時序索引

> **索引建立日期**: 2026-09-12 (最終文檔整理, 無新推導)
> **規則**: 只記錄實際發生嘅推導/驗證步驟, 禁止回溯改寫, 禁止跨文檔污染

| 序 | 日期 | 步驟 | 產出 | 狀態 |
|:-:|:-----|:-----|:-----|:----:|
| 0 | 2026-08-21 | O46 問題記錄建立 (兩通道方案) | `01_problem_record.md` | 🔴 |
| 1 | 2026-08-31 | 前置盤點: O41 已閉合 (A=134.2), O42 6 方法量度 🟢, O5 冷斑目錄 🟢 | — | ✅ |
| 2 | 2026-08-31 | LFI map 下載: 30/44/70 GHz (IRSA mirror; PLA URL 需 horn 後綴修正) | `o27_node47_foreground/data/LFI_SkyMap_*` | ✅ |
| 3 | 2026-08-31 | Script v1: 全分辨率平滑 (nside=2048) 太慢 → 超時 | — | 🔴 |
| 4 | 2026-08-31 | Script v2: 統一 downgrade nside=512 + Planck fill value 處理 | `scripts/01_multifreq_check.py` | 🟢 |
| 5 | 2026-08-31 | SEVEM ordering 修正: auto-detect (corr vs raw SMICA) + pre-smoothed 旗標 | `scripts/01_multifreq_check.py` | 🟢 |
| 6 | 2026-08-31 | 最終運行: 6 CMB maps mean −133.64, std 0.98 μK; 7 raw 頻段前景模式 | `data/01_multifreq_results.json` | 🟢 |
| 7 | 2026-08-31 | 通道 B: 引用 O42 Step 3 ISW 文獻整合 (Planck 2015 XXIII, Nadathur+2015) | `docs/02_isw_literature.md` (O42) | 🟢 |
| 8 | 2026-08-31 | 結果文檔: 問題記錄更新 🟢 + 驗證報告 | `01_problem_record.md`, `docs/01_verification_result.md` | 🟢 |
| 9 | 2026-09-12 | 目錄遷移至 `open_problems_fresh/`; 最終文檔整理 (時序索引 + final_result.md) | 本節 + `final_result.md` | ✅ |

**推導鏈**: O41 → O42 → O46 (驗證性閉合, 無新結構公式; A = 88×61/40 由 O41 提供)

---

## 驗證方法

1. 下載 Planck 原始頻段 map (30-353 GHz) + 使用已有 CMB component-separated maps
2. 統一 downgrade 到 nside=512, 4.17° 平滑, 量度冷斑 node 0 溫度
3. 整合 Eridanus Supervoid ISW 文獻值 (O42 Step 3)
4. 量化 IDCM vs ΛCDM 差異

---

## 驗證結果

### 通道 A: 🟢 PASS

**6 種 CMB maps 一致 (std = 0.98 μK):**

| 方法 | T0 (μK) | 來源 |
|:-----|:--------:|:-----|
| SMICA (harmonic ILC) | −134.03 | O5 cache (已平滑) |
| NILC (needlet ILC) | −133.92 | O5 cache (已平滑) |
| Commander (pixel MCMC) | −133.16 | O5 cache (已平滑) |
| SEVEM_final (template) | −134.31 | O42 data |
| SEVEM 143 (template) | −134.71 | O42 data |
| SEVEM 217 (template) | −131.71 | O42 data |
| **mean** | **−133.64** | |
| **std** | **0.98 μK** | |

**Raw 頻段圖: 前景污染模式符合預期**

| 頻段 | 主導前景 | T0 (μK) | 物理原因 |
|:----|:---------|:-------:|:---------|
| 30 GHz | 同步輻射 | −400.30 | 同步輻射較強 |
| 44 GHz | 混合 | −144.39 | 前景較弱, CMB 成分浮現 |
| 70 GHz | 混合 | −67.92 | 前景填充冷斑 → 變暖 |
| 100 GHz | CMB + 塵埃 | −96.03 | 部分塵埃填充 |
| **143 GHz** | **CMB 主導** | **−129.33** | **最接近 A=134.2 (3.6% dev)** |
| 217 GHz | 塵埃主導 | −463.06 | 塵埃發射強 |
| 353 GHz | 塵埃主導 | −3383.17 | 塵埃極強 |

### 通道 B: 🟢 PASS (O42 Step 3 引用)

| 項目 | IDCM | ΛCDM |
|:-----|:----:|:-----:|
| A_total | **134.2 μK** | ~150 μK (觀測) |
| A_prim | **134.2 μK** (ISW=0) | 94–124 μK |
| Eridanus ISW | **0 μK** | −10~−40 (marginal ~10) |

文獻: Planck 2015 XXIII 支持 ISW 解釋唔到冷斑; Nadathur+2015 理論一致

---

## 判定標準

- 🟢 多頻段 A 一致 (CMB maps std < 3 μK) → A 係原生 CMB
- 🔴 多頻段 A 漂移 > 5 μK → 前景污染, A 需修正

**判定: 🟢 PASS** (std = 0.98 μK)

---

## 檔案

```
o46_multifreq_isw/
├── 01_problem_record.md
├── final_result.md                   ← 極簡結論摘要 (RESULT_TEMPLATE 範本)
├── scripts/
│   └── 01_multifreq_check.py          ← 多頻段量度 script
├── data/
│   └── 01_multifreq_results.json      ← 完整結果 (139 lines)
└── docs/
    └── 01_verification_result.md      ← 驗證報告
```