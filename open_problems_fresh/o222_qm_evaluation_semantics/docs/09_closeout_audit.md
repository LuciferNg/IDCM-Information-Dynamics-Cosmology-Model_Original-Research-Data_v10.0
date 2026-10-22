# O222 — 階段性 Closeout 審計（2026-09-29）

> **定位**：本檔 = **驗證記錄**，唔載新推導。目的：確認**本對話框（thread 93184）全部 session 鏈**嘅內容已入文檔／劇本，並且文檔**經獨立核對**。
> **權威判據**：`scripts/13_closeout_audit.py` → `logs/13_closeout_audit.out`、`data/13_closeout_audit.json`（**57/57 PASS**）。
> **獨立性聲明**：`scripts/13` **唔 import** `09`／`10`／`11`／`12`，只用 stdlib + 精確算術，並用**唔同算法**重算（域大小用**組合計數**＋**直接枚舉**雙路；CHSH 極值用**可分離分解**而非全枚舉／top-3 排序）。

---

## §0 一句話結論

**✅ 記錄完整、可獨立重現（57/57 PASS）**：8 條 session 鏈全部內容已入文檔／劇本；A2／B5／B2 全部 headline 值由獨立算法逐個重現（8/8 完全相同）；同時**捉到一個真記載錯誤**（§5-G3：A2 之兩個域計數無法重現，正確值 = 13,388,280／12,517,800；**不影響任何結果值**）。

---

## §1 驗證對象 = 本對話框整條 **session 鏈**（唔係單一 id）

判據：`~/.hermes/state.db`（**唯讀**）· `session_key = agent:main:telegram:dm:7500748185:93184` · 以 `parent_session_id` 串成壓縮鏈。

| # | session id | 開始 (HKT) | 結束 | end_reason | parent | msgs | tools |
|:-:|:---|:---|:---|:---|:---|:-:|:-:|
| 1 | `20260929_172254_1aa1852b` | 17:22:54 | 17:44:59 | compression | — | 117 | 65 |
| 2 | `20260929_174458_ed8ff7` | 17:44:58 | 18:57:02 | compression | 1 | 244 | 120 |
| 3 | `20260929_185702_e00f9b` | 18:57:02 | 19:29:48 | compression | 2 | 165 | 81 |
| 4 | `20260929_192948_999970` | 19:29:48 | 20:27:43 | compression | 3 | 230 | 112 |
| 5 | `20260929_202743_ba09e1` | 20:27:43 | 21:10:01 | compression | 4 | 228 | 109 |
| 6 | `20260929_211001_451052` | 21:10:01 | 22:14:22 | compression | 5 | 249 | 108 |
| 7 | `20260929_221422_e60c1a` | 22:14:22 | 23:09:46 | compression | 6 | 237 | 112 |
| 8 | `20260929_230946_6fca64` | 23:09:46 | live | — | 7 | (live) | (live) |

- **A1–A5 PASS**：鏈長 8；`parent[i] == id[i-1]` **全中**（壓縮鏈完整，無斷鏈）；時間單調；鏈訊息總數 **≥1488**（audit 時刻 1593，**鏈係活嘅，故此數係快照唔係凍結值**）。
- ⚠️ 教訓（skill §0.1 規則 1 之實證）：**本輪對話期間 session id 已換 8 次**（每次壓縮產生新 id）。只查「當前 id」會漏掉 7 條 session 嘅全部內容 ⟹ 必須用 `session_key` + `parent_session_id` 串鏈。

---

## §2 寫入 ledger 與範圍審計（零越界）

`scripts/13` §B 由全鏈 assistant `tool_calls` 抽 `write_file`／`patch` 目標，**並且**另掃 `terminal`／`execute_code` 之 shell／python 寫入通道（避免「只掃 write_file」嘅假範圍證據）：

| 類別 | distinct 目標數 | 內容 |
|:---|:-:|:---|
| **O222 目錄** | 23 | 全部本目錄產物（docs／scripts／data／logs／根 md）|
| **problem_register** | 2 | `register.py`（**工具修正，用戶明示「先修正工具」**）＋ `README.md` |
| **master `open_problems_fresh/README.md`** | 2 次（python `open(...,'w')`） | O222 狀態行（live field）|
| **scratch 探針** | 18 | `~/.hermes/cache/scratch/*`（工作區，唔入 repo）|
| **skill** | 1 | `theory-self-falsification-harness`（#12–#18 教訓）|
| **其他（越界）** | **0** | — |
| 工具修正前備份 | 14 次 `cp ~/.hermes/backups/` | 依 `userskills-patch-backup` 紀律 |

**B1 PASS：0 越界** ✓（唯一「本目錄以外」寫入 = `problem_register`（工具修正＋註冊）＋ master README 狀態行＋scratch／skills —— 全部屬已明示或既有紀律範圍）。

---

## §3 數字覆蓋率（assistant 敘述 → 記錄）

- 由全鏈 **assistant 敘述**抽 4+ 有效位數字：**68 個 distinct**（C1 PASS）。
- **缺失 = 0**：audit 時刻「搵唔到」嘅全部屬**已申報噪音類**（session／proc id 碎片、工具輸出**字數**、2 個已被結果取代之 scratch 探針診斷值 `1440`／`24125`）⟹ **C2 PASS（真結果數字 0 缺失）**。
- **反方向**（docs → 記錄，§G）：三份結果文檔（`docs/04`／`06`／`08`）之 **全部** 4+ 有效位數字（34／15／11 個，剔除 hash 碎片）**全部**能在 `data/*.json`＋`logs/*.out` 找到（**0 missing**）⟹ **文檔冇任何未落地之孤立數字** ✓（G1–G3 PASS）。
- ⚠️ 覆蓋率答「**有冇記錄**」，**唔答**「對唔對」——「對唔對」由 §4 獨立重算負責。

---

## §4 獨立重算（headline 值，唔 import 原 script）

### §4.1 B5 資源身份（`scripts/13` §D，Fraction 零浮點）

| 量 | 獨立值 | 判據 |
|:---|:---|:---|
| 讀成本 | `123/88 = 2·E_min` EXACT | D1 PASS |
| 每 pass 可行讀數 | `(123/2)/(123/88) = **44 = N_d**` | D2 PASS |
| O41 自洽 | `44 × 123/88 = 123/2`（預算**恰好用盡**）| D3 PASS |
| pass 時長／`τ_deco` | 44 讀 = **1 tick**；`τ_deco` = **2 ticks = 2 pass** | D4 PASS |
| A2 超支 | `7688/44 = **1922/11** ≈ 174.7×` | D5 PASS |
| 預算可行前綴 | **15 對／43 讀**（由記錄之 per-pair 成本多重集 `{2,2,3×13}` 獨立累加；餘 1 讀 < 最平 pair 成本 2 ⟹ 第 16 對被結構性擋）| D6a–D6c、D7 PASS |
| 預算可行 CHSH | **恆等 0**（四統計量；隨機軸 null median = max = 0）| D9、D10 PASS |

### §4.2 A2 CHSH 極值（§E，**可分離分解**＋樣本對全掃自檢）

`S = M[a][i] − M[a][j] + M[a′][i] + M[a′][j] = V(i) + U(j)` ⟹ 精確可分離（`max S = max_i V + max_{j≠i} U`，top-2 技巧），零剪枝、零近似；並以 **150 對隨機 (a,a′) 之全 62² 掃描**自檢（8/8 PASS，E0）。

| 統計量 | E1 獨立 | E2 獨立 | 記錄 | 一致 |
|:---|:-:|:-:|:-:|:-:|
| `all4` | **2** | **3** | 2 / 3 | ✅ |
| `distinct` | 4 | 4 | 4 / 4 | ✅ |
| `distinct_anti` | 4 | 4 | 4 / 4 | ✅ |
| `raw` | 4 | 4 | 4 / 4 | ✅ |

- **E5 PASS：8/8 值逐個相同**；**E7 PASS：記錄之 all4 argmax（`V00,V01,E00,F06`／`E27,E28,V01,E29`）在獨立實作下**逐字**達到同一極值** ✓
- **矩陣身份 pin 實**：`E1` 用 `C1_num`（閉式，den 120）；`E2` 用 `C2`（**memo 命中有效表**，den 3）。⚠️ 我自己第一版誤用 `C1rev_num`（`C1_rev` 係**序作用**診斷，唔係 E2 之表）⟹ 得 E2 all4 = 2 ✗，已即場查出並修正（見 §5 self-disclosure）。
- **E0 自檢**：樣本對上嘅可分離極值 ≤ 全域極值（且 min ≥ 全域 min）⟹ 可分離實作正確 ✓

### §4.3 B2 代數（§F，由**原始軸向量**獨立重算）

- **F3 PASS**：由 `data/04_b2_settings.json` 之 62 條軸向量（Q(√5) 精確算術）獨立算 `cos²θ = (u·v)²/(|u|²|v|²)` ⟹ **3844/3844 與記錄之 `cos2` 矩陣逐對相同**（0 mismatch）。
- **F1／F2 PASS**：`C²` 值集 `{0, 1/9, 4/9, 1}`、重數 `{960, 1660, 960, 264}` ✓
- **F4 PASS**：**精確命中 634/3844** ✓ · **F5 PASS**：`cos²θ` 無理（含 √5 分量）者 **1920/3844** ✓ · **F6 PASS**：`max|C² − cos²| = 8/9`（在 `E00/E29`）✓

### §4.4 完整性（§H）

- **H1 PASS**：不可變副本 MANIFEST **29 件**、`drift = 0`、`missing = 0`。
- **H2 PASS**：`data/*.json` **無孤兒**（`04_b2_freeze_r*.json` 屬 gate 歷史族，已由 `docs/04 §12.1` 列明）。

---

## §5 ★ FINDINGS（本輪審計捉到嘅真問題；全部**照報**）

### G3 — **A2 之兩個域計數無法重現**（記錄缺陷；唔影響任何結果值）

| 量 | A2 記錄（`docs/06 §5.1`／amend A8） | 獨立正確值 | 判據 |
|:---|:---|:---|:---|
| `distinct_anti` | ~~13,711,284~~ | **13,388,280** | 組合推導 ＝ `6228 pairs × 60 × 59` |
| `all4` | ~~12,838,884~~ | **12,517,800** | `62·60·59 + 3720·58·57`，**且直接 62⁴ 枚舉重現** |

- 兩者**均不整除 3782（=62·61）** ⟹ 數學上唔可能係「a≠a′」型域之計數 ⟹ 原值出自**過時／有缺陷之計數探針**。
- **反證正向**：**B5 輪**（`scripts/12`）獨立記錄 `tuples_visited` = 14,303,524／**12,517,800** ⟹ **B5 之計數正確**，兩輪互相打臉，以 B5 為準 ✓
- **影響評估**：**零**。CHSH 之 8 個值、argmax、null、前提檢查**全部獨立重現**（§4.2）⟹ 純記載錯誤。
- **處理**：`docs/06` 與 `docs/05`（A8／A10）**append 日期修正附註**（原文保留，禁追溯污染）＋ register 加注。

### 自我披露（我嘅審計器第一版亦有 3 個錯，全部由閘／自檢捉到）

1. **stale-index bug**：組合計數時內層 `nj` 用咗外層殘留變數 ⟹ 得 13,395,600／12,531,840（**與 A2 記錄同類錯誤**）；已改為 `nj = ni − 1` 並以**直接枚舉**交叉核對 ✓
2. **E2 矩陣誤用**：用 `C1rev_num`（序作用診斷）而非 `C2` ⟹ E2 all4 = 2 ✗；已 pin 矩陣身份 ✓
3. **核對器比較 bug**：字串排序期望寫錯（`'1/9'` vs `'1'`）⟹ 假 FAIL；已改 set 比較 ✓
（**方法論資產**：以上三類 + §G3 之「組合計數必須逐外層 index 重算內層數，且必須以直接枚舉交叉核對」已入 skill。）

---

## §6 檔案閉合水位（T0，本輪建立；規則：未變唔重驗）

| 輪次 | 檔案家族 | 檔尾 mtime | 已驗範圍 | 狀態 |
|:---|:---|:---|:---|:---|
| W1 W-field/QM inventory | `docs/01`、`scripts/01`、`data/01`、`logs/01` | 17:47–18:19 | 全文（`scripts/01` 21/21）| ✅ 已驗 |
| W2 評估語義（R1 凍結）| `docs/02`、`scripts/02`、`data/02`、`logs/02` | 18:42–19:33 | 全文（8/8）| ✅ 已驗 |
| W3 群／穩定子 | `scripts/03`、`data/03`、`logs/03` | 19:02–19:33 | 全文（18/18）| ✅ 已驗 |
| W4 B2 合約 | `docs/03`、`scripts/04`、`data/04_*`、`logs/04_gate_*` | 19:30–21:01 | 全文（14/14、GATE OPEN、`frozen_at 21:01:03`）| ✅ 已驗 |
| W5 B2 執行（R11）| `scripts/05`、`data/05_*`、`logs/05_*` | 20:33–20:37 | 全文（impl `be946911…`；§4.3 F 段重算 cos² 3844/3844）| ✅ 已驗 |
| W6 B2 GPU 核對 | `scripts/06`、`data/06`、`logs/06` | 20:59–21:00 | 全文（4/4、`add870a6…`）| ✅ 已驗 |
| W7 完整性工具 | `scripts/07`、`data/frozen/MANIFEST.json` | 21:13–22:56 | 全文（29 件、drift 0）| ✅ 已驗 |
| W8 A2 合約＋機器 | `docs/05`、`scripts/08`、`scripts/09`、`data/08/09_*`、`logs/09_*` | 21:44–22:17 | 全文（17/17、20/20、impl `d8037bb1…`）| ✅ 已驗（§4.2 值獨立重現）|
| W9 A2 全量枚舉 | `scripts/10`、`data/10`、`logs/10` | 22:26–22:30 | 全文（8 值＋argmax 相同）| ✅ 已驗（§4.2）|
| W10 B5 合約＋機器 | `docs/07`、`scripts/11`、`scripts/12`、`data/11/12`、`logs/12_*` | 22:54–22:57 | 全文（10/10、8/8、impl `f2cb54fa…`）| ✅ 已驗（§4.1）|
| W11 結果文檔 | `docs/04`、`docs/06`、`docs/08` | 21:15–22:56 | 全文（§3 數字全落地；**扚到 G3**）| ✅ 已驗（＋修正附註）|
| W12 外圍記錄 | `01_problem_record.md`、`SESSION_START.md`、`final_result.md`、`README.md` 狀態行、register | 22:57–now | 全文 | ✅ 已驗 |
| W13 本審計 | `scripts/13`、`data/13`、`logs/13`、`docs/09` | now | — | ✅ 產物 |

**未變即唔重驗**：上述家族在本輪後若 mtime 未變，下輪只驗增量。

---

## §7 推導時序索引（本 session 鏈；**舊行唔改**）

| # | 時間 (HKT) | 步驟 | 產物 | 結果 |
|:-:|:---|:---|:---|:---|
| 1 | 17:46 | W-field／QM inventory 建立 | `docs/01`、`scripts/01` | 21/21 PASS |
| 2 | 18:42 | R1 評估語義凍結（thunk／force／rollback）| `docs/02`、`scripts/02` | 8/8 PASS |
| 3 | 19:02 | Aut／穩定子分析 | `scripts/03` | 18/18 PASS |
| 4 | 19:30 | B2 合約 v1（C(θ) 晶格導出）| `docs/03`、`scripts/04` | 14/14、GATE OPEN |
| 5 | 20:33 | B2 執行輪 R11 凍結 | `scripts/05`、`data/05_*` | impl `be946911…`；C² 值集 {0,1/9,4/9,1} |
| 6 | 20:59 | B2 GPU 獨立核對（500 draws）| `scripts/06` | 4/4 PASS、`add870a6…` |
| 7 | 21:01 | B2 最終閘（`frozen_at`）| `data/04_b2_freeze.json` | `frozen_at 21:01:03` |
| 8 | 21:13 | 不可變副本工具 | `scripts/07`＋`data/frozen/` | 21 件 → 29 件、drift 0 |
| 9 | 21:44 | A2 合約（L-SEQ 機器；17 條 H 檢查）| `docs/05`、`scripts/08` | 17/17、GATE OPEN |
| 10 | 22:06 | A2 機器凍結 | `scripts/09` | impl `d8037bb1…` |
| 11 | 22:14 | A2 凍結輪 | `logs/09_a2_rollback.out` | 20/20 PASS、478.6 s |
| 12 | 22:26 | A2 全量無優化枚舉（**用戶硬指令**）| `scripts/10`、`data/10` | 8 值＋argmax 與加速器逐個相同 |
| 13 | 22:24–22:30 | A2 結果文檔＋null 全枚舉 | `docs/06` | E1 all4 = 2、E2 all4 = 3、null p ≈ 0.42（**無顯著性**）|
| 14 | 22:54 | B5 合約（資源界限；amend A1–A6）| `docs/07`、`scripts/11` | 10/10 PASS、GATE OPEN |
| 15 | 22:55 | B5 機器（首跑閘捉到我 factor-2 錯）| `scripts/12`、`logs/12_*_firstrun_FAILS.out` | 修正後 8/8 PASS、impl `f2cb54fa…` |
| 16 | 22:56 | B5 結果文檔 | `docs/08` | 44 讀/pass = N_d；可行 15 對；**可行 CHSH ≡ 0** |
| 17 | 23:14–23:5x | **本 closeout**（session 鏈＋ledger＋覆蓋率＋獨立重算）| `scripts/13`、`docs/09`、`data/13` | **57/57 PASS**；捉到 **G3** |

**時序完整性確認**：全部產物 mtime 單調（17:46 → now，見 §6）；docs 一律遲於其 script 結果；**無任何舊文檔被新推導 backfill**（本輪只 append 日期修正附註）✓
**時序完整性規則**：① 新發現只可 append；② 已閉合輪次之值唔改（只加附註）；③ 註記日期用 `date` 實際值；④ 跨 O 交接只經 register。

---

## §8 未閉合 inventory（交付物 = 每項都有書面判定）

| 項 | 判定 | 位置 |
|:---|:---|:---|
| `G1`：D5 觸發所需 ctx → s 映射唔存在於凍結記錄 | 🟡 已判定（結構缺口；**禁自創**）| `docs/07 §6`、`01_problem_record §9.5` |
| `G2`：逐模頻率 `f(n)` 🔴（O206）| 🟡 已判定（上游未閉合；`f(n)` 出後需重算）| `docs/07 §6.5` |
| `G3`：A2 域計數記載錯誤（本輪新）| 🟢 **已判定（記載層；已附註修正）** | 本檔 §5、`docs/06 §5.1` 附註 |
| A2 超額無顯著性（p ≈ 0.42）| 🟢 已判定（負面結果）| `docs/06 §0/§5.4` |
| A2 `\|S\| = 3` 需 174.7× 預算 ⟹ 反事實 | 🟢 已判定（唔可作物理預言）| `docs/08 §5` |
| D3–D6、Q3 剩餘、Q4、C2、`F_proj = 17` 身份統一 | 🔴 未開始（非本輪範圍）| `01_problem_record §9` |
| B3 第二輪（資源界限**內**重新定義統計量）| 🔴 建議下一輪 | `docs/08 §7` |

**未閉合掃描**：`01_problem_record` 16 個、`SESSION_START` 12 個、`final_result` 13 個 🔴/🟡 標記 —— 全部有書面判定（I1 PASS）✓

---

## §9 重跑指令

```bash
cd open_problems_fresh/o222_qm_evaluation_semantics
/usr/bin/python3 -u scripts/13_closeout_audit.py > logs/13_closeout_audit.out 2>&1   # 約 3 分鐘；期望 RESULT: 57/57 PASS
/usr/bin/python3 -u scripts/07_artifact_integrity.py                                 # MANIFEST drift 0
/usr/bin/python3 ../problem_register/register.py check                               # register 漂移掃描
```
**閘之否決規則**：`scripts/13` 任何 `[FAIL]`（除已登記之 G3 類 discrepancy check）⟹ **禁止推進下一階段**。
