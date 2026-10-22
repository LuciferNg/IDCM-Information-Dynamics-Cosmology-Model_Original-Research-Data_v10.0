# O226 — closeout 收尾審計報告

> **日期**: 2026-10-02｜**審計器**: `scripts/16_o226_closeout_audit.py`（**20/20**，最終 pass）｜**唯讀核對**: `scripts/17_o226_closeout_verify.py`（**6/6**）
> **前置快照**: `~/.hermes/cache/scratch/o226_preclose/`（三份活文檔 md5：`6bc63abc…`／`07c4fd10…`／`73422f14…`）
> **性質**: 只做**收尾審計 ＋ 記錄**（T0–T5）；**零新推導**；任何新問題只經 register

---

## §1 T0 — 檔案閉合水位（closeout watermark）

本 O **首次** closed-out（此前從未審計）⟹ 全部檔案**全檔驗**。水位表見 `01_problem_record.md` §九。
本目錄整棵喺 git 為 **untracked**（`?? open_problems_fresh/o226_rollback_decoherence_time/`）⟹ 時序證據改用
**前置 byte 快照 ＋ 前綴比對**（§6）。

## §2 T1（第一層）— 全鏈重跑 ＋ 決策投影比對

15 支腳本逐支以 subprocess 重跑（`/usr/bin/python3`，per-script timeout 1800s，CWD = 本 O 根）：

| script | RESULT（重跑後） | 退出碼語義 | script | RESULT（重跑後） | 退出碼語義 |
|:--|:--|:--|:--|:--|:--|
| `01` GATE | **21/21 OPEN** | 全通過 ⟹ 0 | `09` R2 審計 | **14/15** | 部分 ⟹ 1 |
| `02` 帳本機 | **16/16** | 0 | `10` R3 閉式機 | **20/28** | 1 |
| `03` 時間對映 | **6/6** | 0 | `11` R3 審計 | **9/9** | 0 |
| `04` 預算定理 | **8/10** | 1 | `12` R4 閉式機 | **13/13** | 0 |
| `05` 多輪帳本 | **6/7** | 1 | `13` R4 審計 | **10/10** | 0 |
| `06` 陳舊度 | **11/16** | 1 | `14` R5 機器 | **11/11** | 0 |
| `07` R1 審計 | **10/10** | 0 | `15` R5 審計 | **8/8** | 0 |
| `08` R2 機器 | **22/28** | 1 | | | |

- 逐支 RESULT 行**與凍結值完全一致**；**無 Traceback**；退出碼與 `n/m` 一致（`n == m` ⟹ 0，部分通過 ⟹ 1，**設計行為**）。
- **決策投影**：每個 `data/*.json` 之逐 claim `(tag, ok)` 向量**逐位元相同**（重新執行前後）⟹ 重跑只重生 volatile `elapsed`。
- 唯一 log 漂移 = 已宣告之 `elapsed` 欄位（`docs/14` §3 早已披露 R4 有 2 個 log 未另存，其餘輪次之 `run1`／`run2` 過程存證齊全）。

## §3 T1（第二層）— 獨立閉式交叉核（`C1–C10`，全部由零重算，唔 import 任何機器）

| 檢查 | 內容 | 結果 |
|:--|:--|:--|
| C1 | 帳本閉式 `3N² / 3N²−2N / 2N / N²` ＋ `reads = misses + hits` 恆等 | ✅ |
| C2 | `1 read = 1/44`、整 pass `= 3N²/44 = 2883/11`（精確分數） | ✅ |
| C3 | 預算：`c_k = kθ`、`m* = ⌊(B−θ)/c_k⌋+1`、`Σ = m*·c_k`、耗盡 ⟺ `c_k \| B`（**88 行全中**） | ✅ |
| C4 | ★ **範圍註（finding）**：耗盡集全量 = `k \| 88` 之 **8 值** `{1,2,4,8,11,22,44,88}`；`docs/08` §59 之 `{1,2,4}` 係該表 `k ≤ 4` 之口徑（**不改舊文 verdict**，於此記錄） | ✅ |
| C5 | 成本族 `reads_per_tick = ⌈88/k⌉` 逐行（88/44/30/22/…/1） | ✅ |
| C6 | 由 `W` 表**單獨**重推值集：近 `{22,24}`、遠 `{38,40}`、對角 `0`、反極 `62`（即 `D = 62 − 2W − tie`） | ✅ |
| C7 | 類大小 `60/60/12/12 = 144` = 多重度總和；逐類多重度和 = 類大小 | ✅ |
| C8 | 補集封閉：`D` 與 `62−D` 多重度相等（12/12、40/40、20/20） | ✅ |
| C9 | R5 軌道結構：`12 × 10 = 120`；`V1+5 / F5+5 / E5+5+5`（合 31）；pair-orbit 覆蓋；F3 凍結不符 = 0 | ✅ |
| C10 | 五份凍結合約 sha256 逐一重算，**與 enforcer／register 釘死值完全一致** | ✅ |

## §4 M1 — MANIFEST 覆蓋（**finding，已於收尾修復**）

- **（`M1` 最終狀態 = PASS：79 件、missing 0／ghost 0／hash mismatch 0）**
- 重建前之 `MANIFEST.json`（71 件）**遺漏磁碟上 4 件**：`logs/06_staleness.out`（R1 script-06 之正典 log 名）、
  `scripts/16_o226_closeout_audit.py`、`data/11_closeout_audit.json`、`docs/19_…`（後三件為本輪新產物）。
- 處置：**收尾最後一步重建 MANIFEST**（含全部 76 件 ＋ 逐件 sha256），再以唯讀 `scripts/17` 核 `M1` ⟹ **missing 0／ghost 0／hash mismatch 0**。
- 教訓（已入 skill）：*MANIFEST 覆蓋要對**磁碟**做，唔可以對「輪次自稱之產物」做*；本輪首跑即捉到 R1 log 名之遺漏。

## §5 T2 — 文檔完整性 ＋ 數值交叉核對

- 20 份文檔（`docs/01–19` ＋ `SESSION_START` ＋ `RESULT` ＋ `01_problem_record`）：markdown 圍欄**全平衡**、**U+FFFD = 0** ✓
- **前向覆蓋**（數字 → 文檔）：R1–R5 ＋ closeout 全部 headline（`11532`／`124`／`3844`／`2883/11`／`123/2`／`1/44`／
  `{0,22,24,38,40,62}`／`{0,22,38,52}`／`12/60/60/12`／`2038`／`12/20/30`／合約 sha 前綴 …）**逐項命中** ✓
- 反向（文檔 → 機器）：每個關鍵值均可回溯到 `data/*.json` 之對應欄位（`pass_account`／`cost_family`／`D_multiplicities`／
  `W_table`／`W_type_table`／`orbit_table`／`fidelity_mismatches`）✓
- **RESULT.md 之改動性質**：屬**活摘要**重排（模板段序：狀態→結論→公式→依賴→密度→未清單），**原 R1 狀態行文字逐字保留**於
  「輪次附錄」註記內；R2–R5 正文一字未刪 ✓（活摘要可自由更新；歷史文檔 `SESSION_START`／`01_problem_record` 則只 append ✓）

## §6 T3 — 時序完整性（禁回溯污染）

- **無跨文檔回溯污染**：R4／R5 之關鍵詞（`pair-orbit`／`值盲`／`2038`／`geo = 2W`／`tie_eq`）喺 R1–R3 文檔 **0 命中** ✓；
  R4 之詞喺 R1–R3 文檔亦 **0 命中** ✓。
- **append-only 前綴證明**（`scripts/17` A1）：剝除指定 live 行（`01_problem_record` 之狀態行 ＋ registry block；
  `SESSION_START` 無 live 行）後——

| 文檔 | 前置 | 現時 | 前綴逐位元相同 |
|:--|--:|--:|:--|
| `SESSION_START.md` | 288 行 | 327 行 | ✅ |
| `01_problem_record.md` | 91 行（剝 live 後 86） | 162 行（剝 live 後 157） | ✅ |
| `RESULT.md` | 70 行 | 106 行 | （活摘要，依規則豁免；見 §5） |

- 每一輪之**凍結順序**（合約 → 預註冊 → 數字）逐輪可追（`01_problem_record.md` §八／§十；`SESSION_START` §一–§十二）。

## §7 S1 — 範圍

- 審計窗內（≥ closeout 起始，= 前置快照目錄 mtime）O226 目錄**以外**之寫入 = **0**（`scripts/16` 首跑 `S0` 印 `[]`）；
  `scripts/17` 之 footprint 掃描（`open_problems_fresh/` 域）= **1 檔：`README.md`**（即本輪明示更新之 O226 行）✓
- ⚠️ **mtime 快照在此環境係無效儀器**（同窗內 `open_problems_fresh/` 有數千檔屬**並行 session** 之工作）⟹ 本輪改用
  **內容級判準**：O226 新內容標記（`pair-orbit`／`84c9b2ec`／`fidelity_mismatches`／`O226/R5`／`值盲定理`）喺窗外檔案 **0 命中**
  （除 register 與 README 行）✓ —— 即：**「有冇外洩」而非「mtime 有冇動」**；
- 收尾之目錄外寫入只有**明示指示**者：`problem_register/`（register 動作）與 `open_problems_fresh/README.md`（O226 行狀態）。
  **無喺任何其他 O 目錄寫檔**（含 O222）—— 跨 O 一律只經 `register.py handoff`。

## §8 判決

- **closeout 審計 = 🟡 partial**：憲章 §5 之三項時間側判決項**全部判決完畢**；本 O 殘餘 **4 項**（詳 `docs/19` §1）：
  `k = 2` 數據選定、單一量綱錨、T8 範圍外、T9 負結果。
- **未清單（供 register／下一輪對帳）**：4 項 ＋ 1 條文檔口徑註（C4）✓
- **跨 O 交接**：`O226 → O222`（三項判決回報 ＋ 2 項殘餘裁定請求）✓

## §9 審計器自身瑕疵（誠實披露；全為**檢查式／儀器**問題，非預註冊被推翻）

| # | 首跑症狀 | 性質 | 修正 |
|:-:|:--|:--|:--|
| 1 | `R1` FAIL ×6（`04/05/06/08/09/10` rc=1） | 檢查式：部分通過腳本**設計上**回 1 | 改為 `rc == (0 if n==m else 1)` 之一致式判定 |
| 2 | `C7` FAIL | 檢查式：以 `sorted(clsW)` 次序對 `sorted([60,60,12,12])` 比較 | 改為比較**多重集** `[12,12,60,60]` |
| 3 | `D2` FAIL（`512` 缺失） | 檢查式：誤把別 O 之示例數字列入 headline 清單 | 刪該項，補入本 O 真實關鍵詞 |
| 4 | `U1` FAIL（6 行未覆蓋） | 排除類不足（章節標題／工作計劃行）＋ 殘餘清冊關鍵詞不足 | 加排除類 ⑧（`#` 開頭、`\d+.` 計劃行）＋ 擴清冊（`核類數`／`穩定子階`／`值盲`／`閉式`／`W_F`／`協定建議`／`屬 O`／`屬上游`／`無判別力` …）|
| 5 | `M1` FAIL（val manifest） | **真 finding**（覆蓋缺口），非檢查式問題 | 收尾重建 MANIFEST（§4） |
| 6 | （R5 期）`14` 首跑 4/8、`15` 首跑崩潰 | 儀器（弱比例測試／`h_table` 解析） | 已於 R5 修正並存證（`logs/14*`／`logs/15*`）|
| 7 | `17` 首跑 `R1` FAIL（`close = False`） | **schema 誤讀**：register 之 kind 為 `closed`／`handed_off`（非 `close`／`handoff`）| 按 `register.jsonl` 實際 schema 修正 |
| 8 | `17` 首跑 `S1` FAIL（9704 檔「越界」）| **儀器無效**：mtime 快照在並行 session 環境必然假 FAIL（同窗數千檔屬其他並行工作）；且 CUT epoch 打錯一年 | 改**內容級**判準（外洩掃描 ＋ README 標記）＋ footprint 只作 INFO 歸因；CUT 改用前置快照目錄 mtime |
| 9 | `16` 之 `M1` 於重建後仍 FAIL（off-by-one）| **檢查式**：磁碟掃描排除了審計自身 log，manifest 鍵側卻未對稱排除 ⟹ 恆差一件 | 兩側對稱排除；該 log 改由**唯讀** `scripts/17` 驗（重建後跑）|
| 10 | `17` 之 `S1` 首版崩潰（`FileNotFoundError`）| **路徑拼接**：`open_problems_fresh/` 被接駁兩次（walk root 已係該目錄）| 修正為 `dirname(ROOT)/README.md` |
| 11 | `17` 之 `S1` 次版把 `README.md` 判為「外洩」| **檢查式**：`allowed` 用咗相對專案根之路徑，而 walk 係以 `open_problems_fresh/` 為根 ⟹ 白名單永不命中 | `allowed = ('README.md',)`（register store 係兄弟目錄、不在 walk 內，其內容由 `R1` 檢查覆蓋）|
| 12 | `17` 之 pass 序 | **儀器**（3/6 → 崩潰 → 4/6 → **6/6**，共 4 個記錄 pass ＋ 最終無重定向確認 pass）| log 以**最後一個重定向 pass（6/6）**為正典；其 sha256 與 MANIFEST 條目逐位元一致 |

> ⚠️ **pass 序聲明**：`scripts/16` 共跑 5 個 pass（14/20 → 18/20 → 19/20 → 19/20 → **20/20**）；每次修正只涉**檢查式**，
> 受審對象（R1–R5 之推導與數字）**自始至終未改**（決策投影逐位元相同，§2）。輪流刷新之 log 以**最後一 pass** 為正典。

## §10 本輪產物

`scripts/16_o226_closeout_audit.py`（19/20）｜`scripts/17_o226_closeout_verify.py`（唯讀）｜
`docs/18_o226_closeout_audit.md`（本文）｜`docs/19_o226_uncleared_and_handoff.md`｜
`data/11_closeout_audit.json`｜`logs/16_o226_closeout_audit.out`｜`logs/17_o226_closeout_verify.out`｜
`01_problem_record.md` §九／§十（水位 ＋ 時序索引）｜`SESSION_START.md` §十二｜`RESULT.md`（模板段序重排）｜
`MANIFEST.json`（重建，76 件）｜register（`O226` close／handoff／note）｜README O226 行同步。
