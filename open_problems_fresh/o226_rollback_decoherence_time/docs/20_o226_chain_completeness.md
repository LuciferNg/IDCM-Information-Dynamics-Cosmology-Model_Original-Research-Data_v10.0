# O226 — 推導鏈腳本完整性輪（chain completeness）

> **日期**: 2026-10-02｜**性質**: 收尾後之**加性**完整性輪（零新推導、零數字改動）｜**觸發**: 用戶指示「確保 scripts/ 內有齊 o226 完整推導鏈的所有腳本」
> **方法**: **對磁碟做覆蓋**（唔對「輪次自稱之產物」做）＋ 交叉核 ＋ **機器強制**（兩處獨立，見 §4）

---

## §1 檢查方法（四路交叉）

1. **逐輪三元組**：鏈上每一輪（R1–R5 ＋ closeout）必須同時具備 {合約文檔、判決／交接文檔、data 檔、該輪全部腳本}；
2. **無未記錄腳本**：`scripts/*.py` 之**磁碟全集**必須**恰好等於**鏈記錄所列之集（差集兩邊都要空）；
3. **正典日誌覆蓋**：每個鏈腳本都要有其正典日誌（`logs/*.out` 帶 `RESULT:` 行；`_probe_*` 診斷腳本按設計無日誌）；
4. **產者覆蓋**：每個 `data/*.json` 至少要有一個腳本產它；另核**文檔內引用之腳本路徑**是否真存在。

## §2 磁碟實錄（19 個 `.py`，逐個列名）

| 輪 | 腳本（磁碟實名） | 合約文檔 | 判決／交接文檔 | data |
|:--|:--|:--|:--|:--|
| **R1** | `01_o226_contract_enforcer.py`、`02_o226_ledger_machine.py`、`03_o226_time_mapping.py`、`04_o226_budget_theorem.py`、`05_o226_multi_round.py`、`06_o226_staleness.py`、`07_o226_independent_audit.py`（＋診斷 `_probe_smoke.py`、`_probe_j4.py`） | `docs/01_o226_contract.md` | `docs/02_round1_verdicts.md`、`docs/05_independent_audit.md` | `data/02`–`06` |
| **R2** | `08_o226_class_machine.py`、`09_o226_class_audit.py` | `docs/06_o226_r2_contract.md` | `docs/07_o226_r2_verdicts.md`、`docs/08_o226_class_source.md` | `data/07_class_machine.json` |
| **R3** | `10_o226_value_closed_form.py`、`11_o226_value_audit.py` | `docs/09_o226_r3_contract.md` | `docs/10_o226_value_set_closed_form.md`、`docs/11_o226_r3_verdicts.md` | `data/08_value_closed_form.json` |
| **R4** | `12_o226_w_closed_form.py`、`13_o226_w_audit.py` | `docs/12_o226_r4_contract.md` | `docs/13_o226_w_closed_form.md`、`docs/14_o226_r4_verdicts.md` | `data/09_w_closed_form.json` |
| **R5** | `14_o226_orbit_factorisation.py`、`15_o226_orbit_audit.py` | `docs/15_o226_r5_contract.md` | `docs/16_o226_orbit_factorisation.md`、`docs/17_o226_r5_verdicts.md` | `data/10_orbit_factorisation.json` |
| **closeout** | `16_o226_closeout_audit.py`、`17_o226_closeout_verify.py` | `docs/18_o226_closeout_audit.md` | `docs/19_o226_uncleared_and_handoff.md` | `data/11_closeout_audit.json` |

**結論（`K1`）**：磁碟 19／19 ✓，**缺失 = 0、未記錄 = 0** ✓（鏈完整）。

## §3 本輪捉到嘅兩項**記錄缺口**（全屬登錄，非腳本缺失）

| # | 實錄 | 性質 | 處置 |
|:-:|:--|:--|:--|
| 1 | 全部 17 條 R1–R5 腳本之**完整檔名**，此前只出現喺 `MANIFEST.json`；文檔只以「`scripts/01–07`」「J1–J4」等**範圍／代號**指涉 | 記錄缺口（腳本本身在 ✓）| 本表 §2 **逐個列名**，並由 `C14`／`K1` 機器強制 |
| 2 | `_probe_smoke.py` 只喺 MANIFEST 出現（`_probe_j4.py` 有 `SESSION_START §八`／`01_problem_record §8` 記名）| 記錄缺口 | 本表 §2 ＋ §5 覆蓋宣告 |

**另兩項已澄清（非缺口）**：
- `logs/06_o226_staleness.out` 與正典 `logs/06_staleness.out` **md5 完全相同**（`cf97ad5a34d5e270f0c05cbe460fbdfe`，22 行、`RESULT: 11/16`）⟹ 前者係**早期命名之同一份副本**，保留作 provenance；**正典名以 R1 記錄為準 = `06_staleness.out`**（15/17 個正典日誌遵循 `NN_o226_*.out`，06 係唯一例外，已於 `C15` 清單內明文標註）。
- 文檔內引用之**上游（O222）腳本** `07_artifact_integrity.py`、`12_b5_budget.py`、`32_closeout3_audit.py` 均存在 ✓（唯讀引用、非本 O 產物）。

## §4 機器強制（雙重；此後鏈完整性唔靠人手核）

| 位置 | 標籤 | 內容 |
|:--|:--|:--|
| `scripts/01`（GATE）| **C14** | 逐輪 {合約、判決／交接、data、全部腳本} 存在，且**磁碟 `.py` 全集 = 記錄所列集**（兩邊差集空）|
| `scripts/01` | **C15** | 每個鏈腳本之正典日誌存在且帶 `RESULT:` 行（`_probe_*` 按設計豁免；正在寫入者按宣告 300 s 窗豁免）＋ 每個 `data/*.json` 有產者腳本 |
| `scripts/01` | **C4f／C5f** | closeout 兩支既受算術禁令（0 float literal／無被禁 import 名），亦唔可用 `../`；`subprocess` **只准 16**（鏈重跑者），17 保持唯讀；無非許可動態載入／`sys.path` 變更 |
| `scripts/16`（收尾審計）| **K1／K2** | **獨立**重做 C14／C15 之判準（唔引用 enforcer）|

**水位躍遷**：`scripts/01` = **21/21 → 25/25**（GATE OPEN）｜`scripts/16` = **20/20 → 22/22**（PASS）。
兩支既有檢查一字未改（R1–R5 之判準與數字不動）；新增全屬**加性**，且經 `scripts/16` 之 `R2`（逐 claim-tag 比對）確認為「新增 tag、無 verdict 改動」，`R3` 之 01 之 RESULT 由 `21/21` 更新為 `25/25` 亦作**宣告式 pin 更新**記錄（`R3b`）。

## §4b 本輪之儀器修正（誠實披露；全屬檢查式／儀器，非判準改動）

| # | 症狀 | 性質 | 處置 |
|:-:|:--|:--|:--|
| 1 | `01` 之 `C15` 首跑 24/25（`journals missing = ['01_o226_contract_enforcer.out']`）| **自我參照**：外層 shell 重定向令該日誌正在被寫入，檢查時尚無 `RESULT:` 行 | 加**宣告式 300 s 窗**：近期被觸碰之正典日誌視為「由祖先 pass 正在寫入」，由 `scripts/16`（R1/R3）＋`17`（M1）代驗 |
| 2 | `16` 之 `R1/R2/R3` 於加檢查後 FAIL（`01: got 24/25 want 25/25`）| ①pin 未更新（已改 `21/21 → 25/25`）；②「前後投影逐位元相同」遇**加性**檢查必然不合 | `R2` 改**逐 claim-tag** 比對（新增 tag 另列 INFO，明示「只加 tag、無 verdict 改動」）；`R3` 允許**宣告式 pin 更新**（印 `R3b: 01: 21/21 → 25/25`）|
| 3 | `16` 之 `S1` 於本輪連續 2 次 FAIL：先是 `README.md`（白名單寫成 `open_problems_fresh/README.md`，而 walk 根已係該目錄 ⟹ 永不命中），繼而係 **`o227_*/` 兩檔**（並行 session 於 60 s 內寫入）| ①檢查式路徑相對性錯誤；②**mtime 儀器在多 session 樹中無效**（同窗檔屬他人工作）| 白名單改 `('README.md',)`；`S1` 改**內容級**判準（新鮮 O226 標記掃描 ＋ README 帶本輪 token），mtime 足跡只作 INFO 歸因（與 `scripts/17` 同式）|

**註**：本輪所有修正只涉**檢查式／儀器**；受審對象（腳本清單、判決、數字）自始至終未改（`R2` 逐 tag 證實）✓

## §5 覆蓋宣告（本輪之後之定義）

- **「O226 推導鏈」= §2 表所列 19 個腳本**（17 條正式腳本 ＋ 2 條診斷探針）＋ 5 份凍結合約 ＋ 11 份 data ＋ 20 份文檔 ＋ 17 份正典日誌；
- **完整性 = 機器檢查**（`C14`／`C15`／`C4f`／`C5f` 於 GATE；`K1`／`K2` 於收尾審計），非一次性人工核；任何日後新增／刪除腳本都會令 **GATE 轉 CLOSED**（`C14` 兩側差集不再空）。

## §6 本輪產物

`docs/20_o226_chain_completeness.md`（本文）｜`scripts/01`（＋C14／C15／C4f／C5f）｜`scripts/16`（＋K1／K2、R2 逐 tag 比對、R3 宣告式 pin 更新、`exp`→`want` 變數改名、死碼清理、01 pin `21/21`→`25/25`）｜`SESSION_START.md §十三`｜`01_problem_record.md §十一`｜`README.md` O226 行（GATE 21/21→25/25）｜register note｜`MANIFEST.json` 重建。
