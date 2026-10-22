# O114 — SU(12)→SM 完整粒子物理現象學鏈

> **Session**: 2026-08-29
> **狀態**: 🔴 **攻堅中 — 5 關卡逐步推進**
> **來源**: O107 剩餘誠實限制 #1-#4 + O108 前置
> **前置**: O107 (6 extra U(1) 物理意義, 13/13 PASS), O85 (breaking chain, 18/18 PASS), O88 (anomaly, 46/46 PASS), O89 (gauge coupling, 46/46 PASS), O54 (lepton masses), O90 (V_Λ)
> **定位**: 從代數分類 (Cartan 5+6 分解) 跨越到真實粒子物理現象學，一次過解決 5 個 🔴 缺口

---

## 攻堅目標

建構 SU(12) → SM 粒子物理現象學鏈條，順序通過 5 個關卡：

```
[關卡 1: 費米子嵌入] ──> [關卡 2: Anomaly 檢驗] ──> [關卡 3: Adjoint VEV 破缺]
                                                          │
[關卡 5: Z' 質量譜] <── [關卡 4: 質量矩陣與 Kinetic Mixing]
```

### 重要前置修正 (O107 更正)
O114-1 已發現：
- **6 extra U(1) = 純水平對稱性** — 唔帶任何 SM 量子數 (B-L/Y/T₃=0)
- B-L, Hypercharge, Weak Isospin 全部喺 **tensor Cartan subspace** (5 個方向)
- 6 extra U(1) 只區分 generation indices
- 因此關卡 1 嘅焦點從「extra U(1) charge 分配」轉為「extra U(1) 同 fermion 嘅 generation-separating 耦合」

### 5 大關卡 (修正版)

| 關卡 | 內容 | 腳本 | 狀態 |
|:----:|:-----|:----|:----:|
| 1 | 三代 SM 費米子嵌入 — 12 維向量劃分 + 6 extra U(1) generation charge 矩陣 | 01 + 01b | ✅ **完成** |
| 2 | 規範反常相消 — 6×6×6 三角反常 + 重力反常 | 02_anomaly_check.py | ✅ **完成** |
| 3 | Adjoint Higgs VEV — 143 標量場 VEV 展開 + 6×6 M² 矩陣 | 03_higgs_vev_breaking.py | ✅ **完成** |
| 4 | 質量矩陣 + Kinetic Mixing 同時對角化 → 物理 Z' 本徵態 | 04_kinetic_mixing_diag.py | ✅ **完成** |
| 5 | 6 extra U(1) Z' 質量譜 + 同 tensor Cartan Z' 嘅 mixing | 05_zprime_spectrum.py | ✅ **完成** |

---

## 檔案結構

```
o114_sm_phenomenology/
├── SESSION_START.md              ← 本文件
├── docs/
│   └── 01_sm_full_phenomenology.md  ✅ 閉合報告 (172 行)
├── scripts/
│   ├── 01_fermion_embedding.py     ✅ 費米子嵌入 + charge 矩陣
│   ├── 01b_sm_quantum_numbers.py   ✅ SM 量子數分配 (Y, T₃, Q, B-L)
│   ├── 02_anomaly_check.py         ✅ 6×6×6 反常檢查 (全 PASS)
│   ├── 03_higgs_vev_breaking.py    ✅ Adj. Higgs VEV + 6×6 質量框架
│   ├── 04_kinetic_mixing_diag.py   ✅ 1-loop kinetic mixing + 對角化
│   └── 05_zprime_spectrum.py       ✅ 綜合閉合報告 + 最終結論
└── data/
    ├── 01_fermion_embedding.json   ✅
    ├── 01b_sm_quantum_numbers.json ✅
    ├── 02_anomaly_check.json       ✅
    ├── 03_mass_matrix.json         ✅
    ├── 04_mass_diagonalization.json ✅
    └── 05_final_report.json        ✅
```

---

*🚀 O114 已註冊 — SU(12)→SM 完整粒子物理現象學鏈 — 2026-08-29*

---

## ★ 全樹路徑衛生審計註記（2026-10-02，append-only）

> 由 skill `script-chain-reproducibility` 全鏈核對器（`path_hygiene_scan.py`）全樹掃描建立——
> **2026-10-02 首次**。**本節唔改動上方任何內容。**
>
> ⚠️ 本節係**工具層審計**（產物路徑衛生），**唔屬本 O 推導**；亦冇對本 O 任何結論作出判定。
> 完整報告：`path_hygiene_audit_20261002/REPORT.md`

### 〇. 一句話

本目錄命中 **13 個 ghost-tree call site**。

### 一. 命中清單

#### ⚠️ ghost tree 依赖

| # | 檔案:行 | 讀取目標（ghost tree 內）|
|:--|:--|:--|
| 1 | `o114_sm_phenomenology/scripts/01_fermion_embedding.py:18` | `open_problems_fresh/o114_sm_phenomenology/data` |
| 2 | `o114_sm_phenomenology/scripts/01_fermion_embedding.py:976` | `open_problems_fresh/o114_sm_phenomenology/data/01_fermion_embedding.json` |
| 3 | `o114_sm_phenomenology/scripts/01b_sm_quantum_numbers.py:12` | `open_problems_fresh/o114_sm_phenomenology/data` |
| 4 | `o114_sm_phenomenology/scripts/01b_sm_quantum_numbers.py:575` | `open_problems_fresh/o114_sm_phenomenology/data/01b_sm_quantum_numbers.json` |
| 5 | `o114_sm_phenomenology/scripts/02_anomaly_check.py:17` | `open_problems_fresh/o114_sm_phenomenology/data` |
| … | （另有 8 處）| |

### 二. 處置（別 O 執行；本節只記移交）

```
⚠️ ghost tree 依赖：13 個 call site 讀 `/home/wsl/Projects/IDCM/IDCM-v10.0/`。
   ① 把所需檔搬入本 O `data/`（或記明「唯讀外部輸入」）
   ② `BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` ＋ 相對路徑
   ③ 風險（已量化）：ghost tree 係 2026-09-08 副本（全樹 288K）。全樹 301 個 call site 分類：
      ① 69 個目標仍存在（讀嘅係**陳舊副本**）；② 231 個目標已失踪但同相對路徑在 repo 存在
      （⟹ **改一行即可，零資料損失**）；③ 1 個 repo 內完全冇。逐 O 對照表 → 同報告目錄 `ghost_dispatch.md`
```

> ⚠️ 依據 `idcm-closeout` §8.1：跨 O 問題**只登記移交，唔准就地修**。本節由**外部審計**寫入，
> 本 O 之 session **有權刪去或改寫本節**（上方內容不受影響）——但如果決定保留，
> 請在 GATE / 下輪 round doc 裏明文記下「已接納 / 已處理」。
