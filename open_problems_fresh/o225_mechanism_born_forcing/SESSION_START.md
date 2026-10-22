# SESSION_START — O225 機制層 Born 權重／概率結構之強制（Mechanism-Level Born Forcing）



# SESSION_START — O225 機制層 Born 權重／概率結構之強制（Mechanism-Level Born Forcing）

> **狀態**: R1–R23 全判定（close-out 第二輪完成，餘下 🔴 見 `docs/49` §六）（★★R23 **判準已導出**：單項族 ⟹ `sgn(A_0)·sgn(x_j) = −sgn(u_0u_1u_2)` 型、二對相同 ⟺ `sgn(u_0u_1)=+1`；非單項族 `A_0 = −(u_0u_1x_0+(u_1²+u_2²)x_1)/u_2`；非承載 = 單項族∧同號 ∪ 41/42｜★凍結路線 `f_tf+f_ft ≡ Σ_a Λ_a`、零集 = Z10（10 態）｜❌ Y3；待審 Z2/Z4（`Tterm/keys` 定向）｜79 10/13、80 4/4｜閘 78=5/5｜MANIFEST v25
> **目標權威來源**: `o222_qm_evaluation_semantics/docs/45_no_go_boundary_charter.md`

---

## 一、接手起點

### 0. 調律者指令（原文，2026-09-30）
> 「把你修正後的目標寫入新開o的指示，這些正是新開o要解決的目標」

### 1. 修正後目標（權威 = O222 no-go 邊界憲章 `docs/45`）
本 o 承接之判決項：****B3 · 機制層 Born 權重缺席****
（憲章全文：`open_problems_fresh/o222_qm_evaluation_semantics/docs/45_no_go_boundary_charter.md`）
★ 憲章要點：所有邊界皆為「**對凍結協定**」之陳述；精確講法唔係「IDCM 無法解釋量子統計」，而係「**喺此協定下其可觀測關聯係古典（Bell-local），且係構造性**」；其**終局性** = 本 o 之判決對象。

### 2. 本 session 之交付定義
1. 讀 `01_problem_record.md` §二（已確立）與 §三（🔴 判決項）
2. **先立合約**（操作空間封死）＋ **先預註冊**（每輪預測先寫低），才跑數
3. 逐判決項給 **✅（附顯式構造）** 或 **🔴（附不可能性證明）** —— 唔接受「未明」
4. 每輪：`docs/` 新檔 ＋ `scripts/` ＋ `data/` ＋ `logs/`；四道硬測試全過方可宣稱閉合

### 3. 唯讀前置資產
- 凍結機器：`o222.../scripts/12_b5_budget.py`（`load_machine()`）
- 最近一輪精確值：`o222.../docs/43_r29_rt1_boundary.md`、`docs/45_no_go_boundary_charter.md`

### 4. 交接限制
**禁止**在 O222 或任何其他 O 目錄寫入檔案；跨 O 只可經 register（handoff／note／mirror）。


---

## ★ 全樹路徑衛生審計註記（2026-10-02，append-only）

> 由 skill `script-chain-reproducibility` 全鏈核對器（`path_hygiene_scan.py`）全樹掃描建立——
> **2026-10-02 首次**。**本節唔改動上方任何內容。**
>
> ⚠️ 本節係**工具層審計**（產物路徑衛生），**唔屬本 O 推導**；亦冇對本 O 任何結論作出判定。
> 完整報告：`path_hygiene_audit_20261002/REPORT.md`

### 〇. 一句話

本目錄命中 **1 處 READ 自 agent scratch**（輸入 provenance 缺口）。

### 一. 命中清單

#### 🟡 READ（由 agent scratch / cache 讀入）

| # | 檔案:行 | 讀自 |
|:--|:--|:--|
| 1 | `o225_mechanism_born_forcing/scripts/81_o225_closeout2_audit.py:87` | `/home/wsl/.hermes/cache/scratch/o225_closeout_before.json` |

### 二. 處置（別 O 執行；本節只記移交）

```
🟡 READ 命中：1 處由 **agent scratch / cache** 讀入（唔係 repo 內絕）。（append 2026-10-09：本行歷史標記已收尾 —— O225 結構層五項閉合見 docs/71_r33_results.md §三；PHYS-1 跨 O 待下游裁決。原文不刪。）
   scratch 係 24h 閒置即清嘅位置 ⟹ 該輪推導**事後無法重建輸入**。
   ① 把輸入快照搬入 <O>/data/（標明下載日期 + 來源 URL / 本地路徑）
   ② 改 script 讀 repo 內相對路徑
   ③ 若真係不可搬（大數據）⟹ 寫 <O>/data/README_input.md 記下重獲取步驟 + 在同行加
      `# path-hygiene: exempt <理由>`
```

> ⚠️ 依據 `idcm-closeout` §8.1：跨 O 問題**只登記移交，唔准就地修**。本節由**外部審計**寫入，
> 本 O 之 session **有權刪去或改寫本節**（上方內容不受影響）——但如果決定保留，
> 請在 GATE / 下輪 round doc 裏明文記下「已接納 / 已處理」。
