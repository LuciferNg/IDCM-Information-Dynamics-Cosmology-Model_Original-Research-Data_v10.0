# O4 新 Session 啟動文件 — Fibonacci 等級物理動機

> 開新 session 時: 載入下面 skills, 然後將「啟動 prompt」複製做第一條訊息。

---

## 所需 Skills（載入順序）

### 1. `polyhedral-graph-analysis`（核心, 必須）
- Fibonacci ladder 重校準 (§7 ⚠️ simulation over-strength warning)
- 6level 模型細節 (χ²=1.31), 同色邊 pitfall
- 群論邊長 (§9), 旋轉不變 (§10)

### 2. `idcm-structural-derivation-workflow`（核心, 必須）
- IDCM 結構推導協議: 0,1 → φ → K_Chain 第一性原理
- 點樣分辨「結構推導」vs「數字遊戲」

### 3. `theoretical-physics-validation`（輔助）
- 驗證物理動機: 第一性原理 vs post-hoc

### 4. `idcm-phi-power-trap`（輔助, 提醒）
- φ-power 擬合陷阱警告 — 防止將數值分解成 φ-power

## 前置資料（session 內需知）

```
已知等級: F₅=150μK (冷斑), F₄=90μK, F₃=60μK
6level χ²=1.31 (最佳), 5level 1.68, 3level 較差
正常邊觀測 53.1μK, 阻挫邊 34.5μK
BFS 距離分佈: 1+4+8+11+12+11+8+4+1 (直徑8)
IDCM 結構: 0,1 → x²+x−1=0 → φ → K_Chain 44-site → K_Tree 33
已用 Fibonacci: F₅(冷斑), F₇=13(Ω_DM/Ω_b=13/2), F₅²=25(峰序列)
φ-power 規則: 結構公式必須由 CY₃(36,98)/K_Chain 譜/Z₃×Z₅ 電荷直接推導
```

## 啟動 Prompt（複製做第一條訊息）

```
開 O4 Fibonacci 等級動機專案: /home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o4_fib_motivation/

任務: 由 IDCM 第一性原理推導節點振幅等級嘅物理起源:
節點振幅 = Fibonacci ladder (F₃=60μK, F₄=90μK, F₅=150μK by BFS 距離)
點解係 Fibonacci? 點解按 BFS 距離? 點解 3 級?

候選機制 (全部要驗證):
1. BFS 距離衰減: A(d) = 30×F_{5−d}? 定 A(d) = 30×φ^(−d/2)?
2. 干涉級數: 節點 = m 階干涉 → F_m
3. K_Chain 模式: 振幅由 γ_n 組合 (γ₇=13.8MeV ↔ F₇=13?)
4. 拓撲位錯: 阻挫能量量子化 → 等級
5. ε 截斷: ε³ = 3 代 → 3 級

載入 skills: polyhedral-graph-analysis, idcm-structural-derivation-workflow, idcm-phi-power-trap

鐵律:
- 禁止數字遊戲 (唔可以「似 F₇ 所以係」)
- 必須由 0,1 → φ → K_Chain → CY₃ → 群論直接推導
- φ-power 公式必須有幾何/譜來源
- 推唔到就誠實記錄 🟡 開放, 唔好強推

最後: 雙重驗證 + 更新 01_problem_record + README
```

## 檔案結構

```
o4_fib_motivation/
├── 01_problem_record.md   # 問題 + 候選機制 (已建立)
├── SESSION_START.md       # 本文檔
├── scripts/
│   ├── 01_bfs_fit.py
│   ├── 02_group_word.py
│   ├── 03_kchain.py
│   ├── 04_frustration.py
│   └── 05_verify.py
└── data/
```

## 常見坑 (預先提醒)

1. **φ-power 陷阱**: 任何數值都可以分解成 φ-power — 必須有結構來源先算數
2. **BFS 距離 vs 等級**: 要證明「距離 d ↔ F_{5−d}」有機制, 唔好淨係相關
3. **6level 最佳但唔代表結構**: χ² 低可以係擬合優勢 — 需要獨立預測驗證
4. **同色邊 pitfall**: ladder 模型阻挫邊 |ΔT|=0 但觀測 34.5μK — 要解決
5. 如果 5 個機制全部失敗 → 誠實 🟡, 提議下步 (可能係 O2 熱斑數據幫手)


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
| 1 | `o4_fib_motivation/scripts/01_bfs_fit.py:151` | `open_problems_fresh/o4_fib_motivation/data/bfs_fit.txt` |
| 2 | `o4_fib_motivation/scripts/02_group_word.py:168` | `open_problems_fresh/o4_fib_motivation/data/group_word.txt` |
| 3 | `o4_fib_motivation/scripts/03_kchain.py:104` | `open_problems_fresh/o4_fib_motivation/data/kchain_spectrum.txt` |
| 4 | `o4_fib_motivation/scripts/04_frustration.py:146` | `open_problems_fresh/o4_fib_motivation/data/frustration_energy.txt` |
| 5 | `o4_fib_motivation/scripts/05_synthesis.py:178` | `open_problems_fresh/o4_fib_motivation/data/synthesis.txt` |
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
