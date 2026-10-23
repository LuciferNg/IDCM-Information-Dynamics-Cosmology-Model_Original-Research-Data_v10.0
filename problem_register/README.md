# problem_register — IDCM 開放問題生命週期註冊冊

**記錄嘅只有編號 + 事件 + 時間**：註冊 / 歸屬 / 閉合 / 負結果 / 後驗 / 進度更新。
**永不記錄問題內容、永不記錄結論、永不記錄推導。** 內容住喺原本四處（見下），註冊冊只放**指針**（`ref` = 檔案路徑）。

## 分工（各檔案各司其職）

| 檔案 | 角色 |
|:-----|:-----|
| `README.md` | **對外導引** — repo 上 GitHub 後畀人睇嘅入口（**唔係賬本**） |
| `01_problem_record.md` | **推導鏈** — 問題陳述 + 已確立結構 + 攻堅路線 |
| `SESSION_START.md` | **起手式** — 下個 session 由邊度開始 |
| `final_result.md` | **下載者 AI agent 快速理解**用嘅摘要 |
| `problem_register/` | **只記編號 + 生命週期**（本目錄） |

註冊冊唔取代任何一個 — 佢係唯一可以「一個 query 答出邊個編號屬於邊個、而家咩狀態」嘅地方。

**格式由 `_templates/` 定義，agent 唔准自行創作規格**（見下節）。

## 兩種問題鍵（`pid`）

| pid 形式 | 例 | 說明 |
|:---------|:---|:-----|
| `O<n>` | `O213` | O 系列問題，有自己嘅 `o213_*` 目錄 |
| `<theme>/<item>` | `bbn/he3` | **主題資料夾內**嘅問題（無 O 編號）— theme ∈ `bbn` / `cmb_cl` / `h0_tension` / `ktree_structure` / … |
| `O<n>/<item>` | `O222/Q1` | ★ **某個 O 嘅子問題**（2026-09-29 新增）— 大 O 開工前先逐項註冊；`num` 保持 `NULL`（唔佔新 O 號、唔影響 README 漂移檢查）；前置 = 父 O 已註冊；`owner` = 父 O 名。查詢：`status --pid O222` / `log --pid O222` 會一併列子問題 |

`--num 213` 係 `--pid O213` 嘅簡寫；theme 問題一定要用 `--pid`。
`next-number` 只服務 O 系列（theme 問題唔佔 O 號）。

---

## 檔案格式範本（`_templates/`）— 唯一規格來源

**問題：** 214 個 O 目錄冇統一格式 —— 實測 `01_problem_record.md` 狀態行可解析率 **53%**、
`SESSION_START.md` **67%**、`前置` 欄只有 **44% / 17%**。同一件事有 5 種寫法，agent 每次自由創作。

**解法：** `open_problems_fresh/_templates/` 放三個範本，係**唯一**規格：

| 範本 | 對應檔 |
|:-----|:-------|
| `_templates/01_problem_record.md` | 每個 O / theme 目錄嘅問題記錄 |
| `_templates/SESSION_START.md` | 每個目錄嘅起手式 |
| `_templates/README_row.md` | `open_problems_fresh/README.md` 一行 |
| `_templates/FORMAT.md` | **格式合約**（欄位定義、允許值、紀律） |

**機器塊（唯一新機制）**：每個檔開頭一個 HTML comment，係**唯一**可解析嘅欄位來源：

```markdown
<!-- registry
pid:     O213
title:   動力學層：世界演化方程
state:   partial            # registered|open|partial|closed|merged|retracted
verdict: -                  # closed|negative|partial|falsified  (- = 無)
flags:   -                  # posthoc, ...
owner:   O213
created: 2026-09-19
updated: 2026-09-27
prereq:  O115, O208, O210   # 前置（逗號分隔，空 = 無）
source:  O115 docs/02 §二 L7
-->
```

- 機器塊**只加不改**：舊 prose 一律保留喺下面，唔准改寫（歷史完整性鐵律）。
- 機器塊缺席 = 未遷移，唔算錯；`check` 報 `NO-BLOCK` 作為**資訊級**。
- `state` 最終仍以 `open_problems_fresh/README.md` emoji 為權威。

---

## 編號衝突處理（`alias` / `collision`）

**核心判斷**：衝突唔係命名空間問題，所以**加 `theme/` 前綴解決唔到**。
真正嘅問題係「**同一標籤指向唔同／已漂移嘅對象**」— 要靠**別名表 + 碰撞註冊 + 永不重用**。

四類衝突（實測）：

| 類 | 例 | 機制 |
|:---|:---|:-----|
| **C1 主題內部編號各自為政** | `bbn/01` vs `cmb_cl/01` | `theme/item` 命名空間**已結構性解決**（扁平化先會撞） |
| **C2 主題文件引用漂移前嘅舊全域 O 號** | `cmb_cold_spot` 寫 O3，實指今 O4 | `alias` 表（**靜默、最危險**） |
| **C3 全域 O 號重複分配** | O1 / O17 / O143 各兩個目錄 | `collision` 表 + **原文贏**（唔自動揀） |
| **C4 退役 P 宇宙** | P2→O9, P3→O10, P4→O11, P5→O12 | `alias --scope global` |

```bash
# C2：記錄「某 scope 內某標籤」今日指向邊個 pid
python3 register.py alias --scope cmb_cold_spot --label O3 --pid O4 --note "O3 插入後 +1"
python3 register.py alias --list
python3 register.py resolve --scope cmb_cold_spot --label O3
python3 register.py find --scope cmb_cold_spot --pid O3      # 先解析，再搜

# C3：碰撞註冊（唔自動裁決，原文贏）
python3 register.py collision --scan
python3 register.py collision --list
```

⚠️ **別名唔改原文**：`alias` 只**記錄**舊標籤今日指向邊個；原文件永遠贏，
修正由該文件自己嘅擁有者做。`alias` 目標必須係已註冊 pid，否則拒收。

**鐵律**：編號只可**遞增**；墓碑號（`reserved_num`）**永不重用**；一個號兩個目錄
= 記入 `collision` 等人裁決，**唔准 DB 自行揀一個**。

---

## 檔案

| 檔案 | 角色 | git |
|:-----|:-----|:----|
| `register.jsonl` | **真源** — append-only 事件日誌，一行一事件，可 diff 可 merge | 追蹤 |
| `register.sqlite` | **投影** — 由 jsonl 重播生成，純查詢用，任何時候可 rebuild | ignore |
| `register.py` | CLI（唯一寫入途徑） | 追蹤 |
| `schema.sql` | DDL | 追蹤 |
| `clues.sqlite` | **衍生線索索引** — 由 docs 掃出，可隨時重建 | ignore |
| `REGISTER.md` | 人類可讀鏡像（生成，唯讀） | ignore |

**鐵律**：`register.jsonl` 係唯一真源；`register.sqlite` / `clues.sqlite` 係純投影（`rebuild` / `clues` 後一致，已驗證）。
兩個 sqlite 都唔可以手改，內容唔可以只存在 sqlite。

---

## 快速用法

```bash
cd problem_register

# 下一個可用編號（自動避開目錄 / 墓碑 / 已註冊）
python3 register.py next-number

# 註冊新問題（編號可省略 = 自動分配）
python3 register.py register --title "問題一句話" --keywords "關鍵詞; 關鍵詞" --owner O213

# 註冊主題資料夾內嘅問題（無 O 編號）
python3 register.py register --pid bbn/he3 --owner bbn --state open \
    --title "³He/H 結構預測" --ref main_problems/p1_bbn/01_problem_record.md#L103

# 記指針但唔改狀態（補 ref / 更正）
python3 register.py note --pid bbn/he3 --ref main_problems/p1_bbn/06_complete_record.md#L220

# 歸屬 / 移交 / 進度
python3 register.py assign   --num 224 --owner O169 --note "歸屬裁定"
python3 register.py handoff  --num 224 --target 213 --note "交回擁有者"
python3 register.py progress --num 224 --verdict partial --note "一半"

# 閉合（含負結果）
python3 register.py close --num 224 --verdict closed    --ref o224_x/docs/03.md
python3 register.py close --num 224 --verdict negative  --ref o224_x/docs/04.md --note "null test 失敗 = 結構巧合"

# 後驗標記（唔會覆蓋 verdict）
python3 register.py posthoc --num 224 --note "先見目標後揀算子"

# 合併 / 撤銷 / 墓碑
python3 register.py merge   --num 224 --target 213 --note "後來併入原先"
python3 register.py retract --num 224 --note "理由（硬事實）"
python3 register.py tombstone --num 224 --note "編號永久保留"

# 查詢
python3 register.py status            # 全部（或 --pid O213 / --pid bbn/he3）
python3 register.py log --pid bbn/he3 # 該問題完整事件時序
python3 register.py check             # 漂移檢查（有硬漂移 exit 1）
python3 register.py mirror            # 重生 REGISTER.md
```

`verdict` 值：`closed` / `negative` / `partial` / `falsified`。
`posthoc` 係 **flag**（獨立於 verdict），兩者並存。

---

## 線索索引（`clues` / `find`）— 內容唔入註冊冊，但可以搵返

註冊冊唔記內容，但推導時要**揾線索**（「呢個數以前邊度提過？」）。解法係一個**衍生索引**：
由 docs 掃出所有 O 編號提及 + 全文索引，**內容零改動**，索引可隨時重建。

```bash
python3 register.py clues                      # 建索引（~1.4s / 2051 docs / ~29k 提及）
python3 register.py find --num 169             # O169 喺邊啲 doc 被提及（731 處）
python3 register.py find --term "cold spot"    # 全文檢索（FTS5）
python3 register.py find --term "13/15" --limit 5
```

同 `idcm_rag_search`（語意檢索）互補：`find` 做**字面 / 編號**檢索，RAG 做**語意**檢索。
⚠️ `find` 係定位工具，唔係「有冇」嘅權威 — 判「存唔存在」仍要 `grep -rn`。

---

## 漂移檢查（`check`）

`check` 比對三個來源並回報：

| 級別 | 意思 | 性質 |
|:-----|:-----|:-----|
| `DUPLICATE-DIR` | 同一編號有兩個目錄（編號碰撞） | **硬漂移** |
| `UNREGISTERED-DIR` | 目錄存在但註冊冊無記錄 | **硬漂移** |
| `README-ONLY` | README 有行但無目錄、無註冊冊記錄（墓碑候選） | **硬漂移** |
| `STATUS-DRIFT` | 註冊冊狀態 vs README 狀態唔一致（README 係權威） | **硬漂移** |
| `PID-NO-FOLDER` | theme 問題嘅資料夾唔存在（如 `bbn/*` 但 `main_problems/p1_bbn/` 冇） | **硬漂移** |
| `REF-MISSING` / `REF-LINE-OOR` | `ref` 檔案／行號唔存在（ref 係唯一內容指針） | **硬漂移** |
| `COLLISION-STALE` | 已登記碰撞其實已解決（目錄剩返一個） | **硬漂移** |
| `ALIAS-DANGLING` | 別名指向未註冊 pid（會靜默錯誤路由） | **硬漂移** |
| `SEED-DISAGREE` | README 同 problem_record / SESSION_START 互相唔一致（= 舊 md 狀態行 stale） | 資訊 |
| `NO-BLOCK` | 檔案未有 `<!-- registry -->` 機器塊（未遷移） | 資訊 |
| `INFO-DB-ONLY` | 已註冊但資料夾未建（**設計允許**） | 資訊 |

`check` 有**硬漂移**時 exit 1 → 可掛入 session-end audit。另印 `seed state source`
（`readme` / `problem_record` / `session_start` / `inferred`）— `inferred` 即三個來源都冇狀態，屬**未確認**，唔係「無事」。

---

## 紀律

1. **註冊冊只記編號**：唔記問題內容、唔記結論、唔記推導。
2. **Append-only**：`event` 永不 UPDATE / DELETE；狀態改動 = 加新事件。
3. **缺席 ≠ 事實**：`check` 永遠列出未註冊目錄，唔會靜默當「無依賴」。
4. **原文贏**：註冊冊同原文衝突時，原文係權威，註冊冊報 stale（唔准自行揀一個）。
5. **編號唯一**：`register` 拒絕墓碑號（`reserved_num`）同已存在目錄號。
6. **指針唔係內容**：`ref` 只放路徑；推導一律寫入 O 目錄 `docs/`。
7. **格式唔准自創**：新檔一律由 `_templates/` 複製；改格式 = 改範本，唔係改單一檔。
8. **過渡期**：新問題「只入註冊冊、唔寫三處 md」嘅政策未正式切換 — 未切換前 md 照舊同步。

---

## 狀態

- **P0（已完成）**：schema + CLI + 由 211 個既有 O 目錄 backfill（`source=backfill:*`，唯讀，零改動舊檔）
  + `check` 漂移審計 + `clues`/`find` 衍生線索索引。
- **P1（試點，2026-09-27）**：**`bbn/` 主題資料夾** 6 個既有開放問題已改由註冊冊註冊
  （`bbn/he3` `bbn/li7-obs` `bbn/2eps` `bbn/summary` `bbn/recheck-o169` `bbn/recheck-o214`）
  — 舊 md **零改動**，註冊冊只記編號 + 狀態 + 指針。試點發現 1 個**真狀態衝突**（見下）。
- **P2（2026-09-27）**：改名 `problem_ledger` → `problem_register`；`_templates/` 格式範本；
  Hermes tool（`idcm_problem_register` / `idcm_problem_find`）+ skill。
- **P3（2026-09-29，O222 開工前）**：三項工具修正 ——
  1. **子問題鍵 `O<n>/<item>`**（`register --pid O222/Q1`）：父 O 必須已註冊、`num` 保持 `NULL`、
     `slug` 預設 = pid、`owner` = 父 O 名；`check` 對子問題改驗「父已註冊 + 父目錄存在」（`PID-ORPHAN` /
     `PID-NO-FOLDER`）。
  2. **incoming handoff 可見**：`log --pid <DST>` 兼列 `target_pid = <DST>` 之事件（prefix `<<`）；
     `status --pid <DST>` 加 `incoming (n addressed to <DST>)` 區塊。舊缺口 = 跨 O 交接只記在 SRC 側，
     目標 O 開檔時睇唔到。
  3. **handed_off 唔再覆寫來源 `owner`**：該事件之 `owner` 欄 = 接收方（純顯示），
     replay 唔再將來源問題標為「由目標 O 擁有」。（修正前 O222 被錯標 `owner=O138`；已 `rebuild` 復原。）
  驗證：`rebuild` 316 事件；`total=233`；`check` 之 HARD DRIFT 仍 6（全為既有，O222 零漂移）；
  `PID-NO-FOLDER`/`PID-ORPHAN`/`REF-MISSING`(新增) 皆 0。備份：`~/.hermes/backups/problem_register__register.py.v22pre.*`。
- **待定**：政策切換點；`register.jsonl` 是否 commit；4 個編號碰撞裁決（O1/O4/O17/O143）。

- **P25（2026-10-16，ledger 鏈斷根因修復）**：`hash`/`prev_hash` 鏈斷——症狀 L2147（prev 指
  不存在 hash `0a3ae40cfab2`）、L2412（無 hash 之外來行）、L2413（跳 L2412）、L2420（跳
  L2416–L2419）。**根因兩處**：①`record()` 由 **sqlite 投影**取 prev（
  `SELECT hash FROM event ORDER BY id DESC`），並行 session 之投影滯後 ⟹ prev 指住舊尾；
  ②`append_jsonl()` 無 file lock ⟹ 兩流可同時寫分叉鏈。
  **修法**：新 `append_chained(rec)`——`fcntl.flock` 臨界區內由 **JSONL 真源**讀尾、
  計 `prev_hash`/`hash`、append、`fsync`；`record()` 改為只填欄位後交 `append_chained`
  決定鏈接（唔再讀 sqlite）。
  **驗證**：單寫入接尾（L2878 prev = L2877 hash）；並行雙流測試（L2879/L2880）零分叉、
  鏈接正確；`rebuild` 2880/2880 一致。
  **歷史斷點**：append-only 鐵律 ⟹ 不改舊行，只留診斷事件（L2878）。
  備份：`~/.hermes/backups/problem_register__register.py.v24pre.20261023_205003`。

### 試點發現（bbn）

`bbn/he3`（³He/H 結構預測）**三個來源互相矛盾**：

| 來源 | 判定 |
|:-----|:-----|
| `01_problem_record.md#L103` | 🟡 partial |
| `08_omegab_direct.md` | 🟡 partial |
| `06_complete_record.md#L220` | 🟢 已閉合 (O13) |

註冊冊記 `state=partial state_source=problem_record`，衝突寫入 `note` + `log` 事件（**唔自行揀一個**）。
裁決要由本 O 自己喺原文改，註冊冊跟隨。
