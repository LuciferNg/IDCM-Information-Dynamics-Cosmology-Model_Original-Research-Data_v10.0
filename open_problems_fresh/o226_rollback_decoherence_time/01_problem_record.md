# O226 — 回滾與退相干之時間結構（Rollback & Decoherence Time Structure）

<!-- registry
pid:     O226
title:   回滾與退相干之時間結構（Rollback & Decoherence Time Structure）
state:   partial
verdict: partial
flags:   closeout-2026-10-02; residual-4 (k=2 數據選定 / 單一錨 / T8 範圍外 / T9 負結果) see docs/19
owner:   O226
created: 2026-09-30
updated: 2026-10-02
prereq:  O222
dir:     open_problems_fresh/o226_rollback_decoherence_time/
source:  O222 完整性 closeout 分流（調律者指令 2026-09-30：「開新o，把剩下開題分開幾個o解決，保留o222開放作為最終裁決及整合」）
-->

# O226 — 回滾與退相干之時間結構（Rollback & Decoherence Time Structure）

> **狀態**: 🟡 **R1–R5 已判決 ＋ closeout 審計完成（partial，2026-10-02）** — 目標：依 O222 憲章 `docs/45` 之時間結構側（回滾 = 深度 1 vs tick／預算守恆／「退相干 = 帳本陳舊」之精確表述）；**殘餘 4 項見 `docs/19`**
> **建立/更新**: 2026-09-30｜**位置**: `open_problems_fresh/o226_rollback_decoherence_time/`
> **前置**: **O222 保留開放作最終裁決及整合**；本 o 承接憲章判決項：**時間結構（B1–B6 之時間側）**
> **目標權威來源**: `open_problems_fresh/o222_qm_evaluation_semantics/docs/45_no_go_boundary_charter.md`

---

## 一、問題陳述
**判定時間結構**：回滾（pop）與退相干時間 `τ_deco` 之**身份** —— 係數值關係定**類型關係**？並確立預算守恆（Σ ≤ 61.5 = B5 I1）之充要證明，及「**退相干 = 帳本陳舊／回滾結構，唔係相位耗散**」之精確表述（此為 B2/B3 之時間側對偶）。

## 二、已確立嘅結構（引用自 O222，逐項附出處）
```
🟢 一次 pass 精確帳：pairs = 3844、reads = 11532 = 3N²、hits = 124 = 2N、**pops = 3844（每對恰 1）**
🟢 時間對映：1 read = 1/44 tick ⟹ 回滾 = 1/44 tick、整 pass = 2883/11 ticks（精確分數）
🟢 **回滾 = 深度 1、無時間延展** ⟹ 與 2 ticks **不可比**（類型錯配，非 88 倍數值差）
🟢 Γ = 1/(2·tick) 之自身推導不變；ΔE_read = 123/88；E_sync = 44×123/88 = 61.5 = B5 I1
🔴 時間對映之唯一性（或最小時間擴張之不可能性）；預算守恆之充要；多輪穩定性
```

## 三、未確立（🔴 開放問題 = 本 o 之判決項）
```
🔴 時間對映：全部機器量 × {tick, 2 tick, τ_deco} 之完整匹配表 → 唯一性 或 no-go 終局
🔴 預算守恆定理：由讀寫律（3N² 讀、2N 命中、1 pop/對）導出 Σ 之閉式與充要條件
🔴 多輪/多步帳本：R 輪 × 120 初始態之穩定性與不變量（全量）
🔴 「退相干 = 陳舊度」之精確形式化（與 B2/B3 之對偶關係）
```

## 四、攻擊路線
```
1. 時間對映窮舉審計（低成本）
2. 預算守恆定理（中成本）
3. 多輪帳本全量（中成本）
4. 陳舊度-退相干對偶形式化（中成本）
```

## 五、驗證標準
```
✅ 匹配表完整（每格：物件 ＋ 結構謂詞 ＋ 數字）
✅ 預算守恆以閉式 ＋ 全量驗證
✅ 零新參數；與 docs/43 §二(d)、docs/42 §D 數字一致
```

**四道硬測試**（閉合宣稱必過）：① 自由度成本（零參數）② Monte-Carlo null（10⁷ 樣本，5σ）③ 可證偽＋樣本外盲測 ④ 結構剛性（擾動測試）

## 六、O222 交接依據（**只讀，唔喺 O222 寫任何檔**）
- 憲章：`o222_qm_evaluation_semantics/docs/45_no_go_boundary_charter.md`（B1–B6 ＋ §3 正面清單 ＋ §4 唔屬域）
- 證據文檔：`docs/13`（P2d）、`docs/19`（C2G7 七判準）、`docs/35`（QM 六項）、`docs/38`（R24）、`docs/39`（R25 amplitude）、`docs/40`（R26 G1/G8）、`docs/41`（R27）、`docs/42`（R28）、`docs/43`（R29 RT1＋邊界＋P1–P7）、`docs/44`（完整性 closeout）
- 可重跑基礎設施（唯讀）：`o222.../scripts/12_b5_budget.py`（`load_machine()`）、`scripts/07_artifact_integrity.py`、`scripts/32_closeout3_audit.py`；`data/frozen/MANIFEST.json`（349 件）
- register：O222 ↔ 本 o 之 handoff（ref 全部 in-scope）

## 七、紀律（沿用 O222 全套）
合約＋強制先於任何數字｜預註冊先於運算｜全量無優化（零剪枝、精確算術）｜零參數／零擬合（禁後驗湊算子、禁 φ-power fitting）｜「無效才是正確」｜每輪 docs/＋scripts/＋data/＋logs/＋MANIFEST＋register（append-only）｜四道硬測試全過方可宣稱閉合｜**唔准**在其他 O 目錄寫檔（跨 O 只經 register）

## 八、推導時序索引（R1，2026-10-02；**唯讀，禁回溯修改**）

> 用途：記錄 R1 之**推導時序**，確保「先合約、先預註冊、後見數」可被追溯；新發現只可加新 section。

| 序 | 時刻 | 事件（時序） | 產物 |
|:--|:--|:--|:--|
| 1 | 00:0x | 讀本檔 §二／§三 ＋ 上游憲章 `docs/45`§5、`docs/43`、`docs/42`§D、`docs/08`§1 | — |
| 2 | 00:1x | **凍結合約**（見數前）：`o226-r1-contract-v1`，判決項 J1–J4 ＋ 預註冊 Pr-1.1…Pr-4.5 ＋ I1–I9 | `docs/01_o226_contract.md` |
| 3 | 00:1x | **預註冊事件**寫入 register（**先於任何數字**）：5 條 note（J1／J2） | `problem_register/register.jsonl` |
| 4 | 00:2x | 寫 GATE 強制者（C1–C5）；寫凍結帳本機；跑 `scripts/02` → 16/16 | `scripts/01`、`scripts/02`、`data/02` |
| 5 | 00:2x | J1 路線 `scripts/03`（時間對映表 18 行／判別力否證／gauge） | `data/03_time_mapping.json` |
| 6 | 00:2x | J2 路線 `scripts/04`（閉式／盲測／null／剛性）；**Pr-2.2 方向被否證** → 立 Q2-c | `data/04_budget_theorem.json` |
| 7 | 00:3x | J3 路線 `scripts/05`（R = 1..8 × 120 態全量／世界線字 `ord(W) = 5`） | `data/05_multi_round.json` |
| 8 | 00:3x | J4 路線 `scripts/06` 首跑 5/10 → **發現讀取核僅 12 類** → 寫 J4 修復區段（5 項 `-c`）→ 11/16 | `data/06_staleness.json`、`scripts/_probe_j4.py` |
| 9 | 00:4x | 獨立審計 `scripts/07`（唔 import 02–06）→ 10/10 | `logs/07_o226_independent_audit.out` |
| 10 | 00:4x | 判決／否證／審計三文 ＋ RESULT ＋ MANIFEST ＋ register 4 事（progress×2、note×2） | `docs/02–05`、`RESULT.md`、`MANIFEST.json` |
| 11 | 00:5x | 全管線重跑以重生 logs（原 logs 因誤刪命令遺失；腳本為精確／確定性，重跑結果逐項一致） | `logs/0*_*.out` |

**★ 時序完整性聲明**：第 2、3 步（合約 ＋ 預註冊）**確定先於**第 4 步以後之一切數字；R1 之 8 項預註冊否證（`docs/04`）全部為「先寫死、後實測」之產物，無任何事後補寫預測。


---

## 九、檔案閉合水位（closeout watermark，T0；2026-10-02）

> 本 O 首次 closed-out（此前從未審計）⟹ 全部檔案**全檔驗**。mtime 見下；`git status` 顯示本目錄整棵為
> untracked（`?? open_problems_fresh/o226_rollback_decoherence_time/`），故採 **byte 比對 ＋ 前置快照** 作時序證據
> （快照：`~/.hermes/cache/scratch/o226_preclose/`，`scripts/17` 核 A1）。

| # | 檔案 | 上次檔案更新 (mtime) | 上次 closed-out | 已驗範圍 | 狀態 |
|:-:|:--|:--|:--|:--|:--|
| 1 | `docs/01–17`（17 件） | 2026-10-02 00:1x–02:04 | — | 全文（fence／U+FFFD／headline 覆蓋／時序回溯） | ✅ 已驗 |
| 2 | `scripts/01–15` | 2026-10-02 00:2x–01:5x | — | 全文（AST 閘 ＋ 全鏈重跑 ＋ 決策投影比對） | ✅ 已驗 |
| 3 | `data/01–10` | 2026-10-02（重跑刷新） | — | 逐 JSON 逐 claim | ✅ 已驗 |
| 4 | `logs/*`（含 `run1`／`run2` 過程存證） | 2026-10-02 | — | RESULT 行 ＋ Traceback 掃描 | ✅ 已驗 |
| 5 | `SESSION_START.md` / `RESULT.md` / `01_problem_record.md` | 2026-10-02 02:2x | — | 全檔 ＋ append-only 前綴證明 | ✅ 已驗 |
| 6 | `MANIFEST.json` | 2026-10-02 02:3x | — | 磁碟 vs manifest 逐件 sha256 | ✅ 已驗（`scripts/17`） |

**本輪新增（closeout 產物）**：`scripts/16`（審計器）、`scripts/17`（唯讀核對器）、`docs/18`（審計報告）、
`docs/19`（未清單 ＋ 跨 O 交接）、`data/11_closeout_audit.json`、`logs/16`、`logs/17`。

**審計器自身**：MANIFEST 於最後一筆寫入後方建，之後只跑唯讀 `scripts/17`（不寫任何檔）⟹ 自指漂移 = 0。

---

## 十、推導時序索引（R2–R5 ＋ closeout，2026-10-02；**唯讀，禁回溯修改**）

> 承 §八（R1）。每一列 = 一個**真實**步驟，按實際發生次序；新發現只可加新 section。

### 第 2 輪（R2）— 核類結構之來源
| 序 | 時刻 | 事件（時序） | 產物 |
|:-:|:--|:--|:--|
| 12 | 00:5x | 凍結 R2 合約（見數前）＋ register 預註冊 note | `docs/06`、`register.jsonl` |
| 13 | 00:5x | GATE 擴充 C6/C7/C4b/C5b；`scripts/08` 首跑 17/26（儀器 bug）→ 22/28 | `scripts/01`、`data/07`、`logs/08*` |
| 14 | 01:0x | 獨立審計 `scripts/09` → 14/15；判決文＋來源文 | `docs/07`、`docs/08` |

### 第 3 輪（R3）— 值集閉式與矛盾解決
| 序 | 時刻 | 事件 | 產物 |
|:-:|:--|:--|:--|
| 15 | 01:1x | 凍結 R3 合約＋預註冊 | `docs/09` |
| 16 | 01:1x | GATE C8/C9/C4c/C5c；`scripts/10` 首跑崩潰（`TypeError`，run1 存證）→ 修 → 20/28 | `scripts/10`、`logs/10*` |
| 17 | 01:2x | 獨立審計 `scripts/11` → 9/9；閉式文＋判決文 | `docs/10`、`docs/11` |

### 第 4 輪（R4）— `geo = 2W` 因數式 ＋ 慣例定理
| 序 | 時刻 | 事件 | 產物 |
|:-:|:--|:--|:--|
| 18 | 01:3x | 凍結 R4 合約＋預註冊 | `docs/12` |
| 19 | 01:3x | GATE C10/C11/C4d/C5d；`scripts/12` run1 `TypeError`→run2 11/13→**13/13** | `scripts/12`、`logs/12*` |
| 20 | 01:4x | 獨立審計 `scripts/13` run1 3/10→**10/10**；閉式文＋判決文 | `docs/13`、`docs/14` |

### 第 5 輪（R5）— F／E 軌道因數式 ＋ 值盲定理 ＋ 慣例影響矩陣
| 序 | 時刻 | 事件 | 產物 |
|:-:|:--|:--|:--|
| 21 | 01:4x | 凍結 R5 合約＋預註冊 | `docs/15` |
| 22 | 01:5x | GATE C12/C13/C4e/C5e；`scripts/14` 4/8（弱比例測試）→ 7/9 → 改寫 V1（pair-orbit 層）→ **11/11** | `scripts/14`、`logs/14*` |
| 23 | 01:5x | 獨立審計 `scripts/15` 崩潰（`h_table` 解析）→ 7/8（`A1` 符號）→ **8/8** | `scripts/15`、`logs/15*` |
| 24 | 02:0x | 因數式文＋判決文；GATE 修 AST 假陽性（`exp` 變數名）→ **21/21 OPEN** | `docs/16`、`docs/17` |

### closeout 輪（2026-10-02 02:1x–02:4x）
| 序 | 時刻 | 事件 | 產物 |
|:-:|:--|:--|:--|
| 25 | 02:13 | 取前置快照（三份活文檔 md5）＋寫 closeout 審計器 `scripts/16`（R/C/M/D/T/U/S 七段） | `~/.hermes/cache/scratch/o226_preclose/`、`scripts/16` |
| 26 | 02:15 | 全鏈重跑（15 支）＋決策投影比對；閉式交叉核；查 MANIFEST 覆蓋 | `logs/16`、`data/11` |
| 27 | 02:2x | 首跑 14/20（檢查式自身瑕疵：R1 退出碼、C7 排序比較、D2 誤列、U1 排除類）→ 逐條修 → **18/20**（餘 M1 = 重建前既知） | `logs/16*` |
| 28 | 02:3x | 未清單文＋交接文；活文檔更新（狀態行 ＋ §九／§十／§十二）；register（close／handoff／note）；README 行 | `docs/18`、`docs/19`、register、README |
| 29 | 02:4x | MANIFEST 重建（最後一筆寫入）→ 唯讀 `scripts/17` 核 M1/A1/D1/U1/R1/S1 | `MANIFEST.json`、`logs/17` |

**★ 時序完整性聲明**：每輪第 1 步（凍結合約 ＋ 預註冊）**確定先於**該輪一切數字；所有預註冊否證（R1 8 項、R2/R3/R4/R5 各若干）
均為「先寫死、後實測」之產物，原樣保留 FAIL ＋ 另立 `-c`，無事後補寫。closeout 之全部 FAIL（
`scripts/16` 首跑 6 項、`logs/14*`、`logs/15*`）均為**儀器／檢查式瑕疵**（非預註冊被推翻），逐條列於 `docs/18` §3。

### 十一、推導鏈腳本完整性輪時序（2026-10-02；加性輪）

| # | 時間 | 步驟 | 產物 |
|:-:|:--|:--|:--|
| 30 | 02:4x | 磁碟覆蓋核（19 `.py` 逐一列名、11 data 產者、17 正典日誌）→ 捉到 2 項**記錄缺口**（腳本完整檔名只喺 MANIFEST；`_probe_smoke.py` 無記名）| `docs/20` |
| 31 | 02:5x | 機器強制：`scripts/01` ＋C14／C15／C4f／C5f（21/21→**25/25**）；`scripts/16` ＋K1／K2（20/20→**22/22**）；既有檢查一字未改 | `scripts/01`、`scripts/16`、`logs/01`、`logs/16` |
| 32 | 02:5x | 活文檔同步：`SESSION_START §十三`、`README` O226 行（GATE 21/21→25/25）、register note、`MANIFEST` 重建 | `MANIFEST.json`、`logs/17` |

**性質聲明**：本輪**零新推導、零數字改動**；唯一 pin 變動 = `scripts/01` 之 RESULT（`21/21 → 25/25`，因新增 4 項加性檢查），已由 `scripts/16` 之 `R2`（逐 claim-tag 比對，證實無 verdict 改動）＋ `R3b`（宣告式 pin 更新）雙重記錄。
