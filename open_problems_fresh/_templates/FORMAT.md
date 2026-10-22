# FORMAT — IDCM 開放問題檔案格式合約

> **本檔係唯一規格來源。** 唔准憑記憶或習慣自由創作格式。
> 新檔一律由 `_templates/` 複製再填內容；要改格式 = 改本檔 + 改範本，唔准改單一檔案。

適用範圍：`open_problems_fresh/` 下所有 `o*_*/` 目錄及主題資料夾（`bbn/`、`cmb_cl/` …）。

---

## 一、五個檔各司其職

| 檔 | 角色 | 讀者 | 範本 |
|:---|:-----|:-----|:-----|
| `README.md` | **對外導引** — repo 上 GitHub 後嘅入口 | 外人 | `_templates/README_row.md` |
| `01_problem_record.md` | **推導鏈** — 問題陳述 + 已確立結構 + 攻堅路線 | 接手者 | `_templates/01_problem_record.md` |
| `SESSION_START.md` | **起手式** — 下個 session 由邊度開始 | 下一個 session | `_templates/SESSION_START.md` |
| `final_result.md` | **下載者 AI agent 快速理解**用嘅摘要 | 下載者 AI | `RESULT_TEMPLATE.md` |
| `problem_register/` | **只記編號 + 生命週期**（唔記內容） | 機器 | — |

⚠️ `README.md` **唔係賬本** — 唔好將狀態史塞入去。狀態史住喺 `problem_register/`。

---

## 二、機器塊（唯一可解析來源）

每個 `01_problem_record.md` 同 `SESSION_START.md` 開頭（第一行標題之後）必須有一個 HTML comment：

```markdown
<!-- registry
pid:     O213
title:   動力學層：世界演化方程
state:   partial
verdict: -
flags:   -
owner:   O213
created: 2026-09-19
updated: 2026-09-27
prereq:  O115, O208, O210
source:  O115 docs/02 §二 L7
-->
```

### 欄位定義

| 欄 | 必填 | 允許值 | 說明 |
|:---|:----:|:-------|:-----|
| `pid` | ✅ | `O<n>` 或 `<theme>/<item>` | 問題鍵；theme 例 `bbn/he3` |
| `title` | ✅ | ≤120 字，一行 | 問題名（**索引柄**，唔係內容） |
| `state` | ✅ | `registered` `open` `partial` `closed` `merged` `retracted` `tombstone` | 生命週期狀態 |
| `verdict` | ✅ | `-` `closed` `negative` `partial` `falsified` | `-` = 未有結論 |
| `flags` | ✅ | `-` 或逗號集（`posthoc`） | 標記，**永不覆蓋 verdict** |
| `owner` | ✅ | `O<n>` 或 theme 名 | 當前擁有者 |
| `created` | ✅ | `YYYY-MM-DD` | 註冊日 |
| `updated` | ✅ | `YYYY-MM-DD` | 最後更新日 |
| `prereq` | ✅ | `-` 或逗號分隔 pid | 前置；**冇就寫 `-`，唔准留空** |
| `source` | ✅ | 文字 ≤200 字 | 由邊度註冊（哪個 O 的哪份 doc） |

### 鐵律

1. **只加不改** — 機器塊係新增；舊 prose 一律保留喺下面，**唔准改寫**（歷史完整性）。
2. **缺席 ≠ 錯誤** — 未有機器塊 = 未遷移；`register.py check` 報 `NO-BLOCK`（資訊級）。
3. **一致性** — 機器塊同人讀 header 唔一致 → `check` 報 `BLOCK-DRIFT`（硬漂移）。
4. **README emoji 仍係狀態權威** — 機器塊同 README 唔一致 → `check` 報 `STATUS-DRIFT`。

---

## 三、狀態 emoji ↔ state 對映（唯一對映）

| emoji | state | 意思 |
|:-----:|:------|:-----|
| 📄 | `registered` | 已註冊，未開工 |
| 🔴 | `open` | 開放，攻堅中 |
| 🟡 | `partial` | 部分閉合 |
| 🟢 | `closed` | 已閉合 |
| 🔀 | `merged` | 已合併（行保留，唔刪） |
| ⬛ | `retracted` | 已撤銷 |
| 🪦 | `tombstone` | 編號墓碑，永不重用 |

⚠️ 唔准自創 emoji。舊檔有 🟠 等異體 → `register.py check` 歸為 `partial` 並列 `SEED-DISAGREE`。

---

## 四、各檔固定章節

### `01_problem_record.md`

```
# O{NNN} — {問題名}
<!-- registry ... -->

## 一、問題陳述
## 二、已確立嘅結構        （🟢 事實 + 驗證率；🔴 誠實標記）
## 三、未確立（🔴 開放問題）
## 四、攻擊路線
## 五、驗證標準
## 六、推導時序索引        （禁回溯污染：只可 append 新行）
## 七、相關文件
```

### `SESSION_START.md`

```
# O{NNN} SESSION_START — {問題名}
<!-- registry ... -->

## 一、接手起點          （狀態 + 上一個 session 停喺邊）
## 二、先做嘅第一步      （具體，可執行）
## 三、已知陷阱          （唔好重蹈嘅錯）
## 四、關鍵數字          （已確立值 + 出處）
## 五、交接 / 依賴
```

### `README.md` 行

```
| **O{NNN}** | **{名稱}** | {emoji} **{狀態一句}** | **{摘要：結論先行，含驗證率}** |
```

⚠️ **摘要內唔准用 `|` 字元**（會斷開表格）；需要時用 `\|` 或改寫。

---

## 五、紀律

1. **格式由範本定義** — agent 唔准自創欄位、章節、emoji。
2. **改格式 = 改範本** — 唔准只改一個檔令佢「特別」。
3. **歷史只可 append** — 舊結論唔准改寫；更正 = 新 section / 新 dated 檔。
4. **推導時序索引禁回溯污染** — 只可加新行，唔准改舊行。
5. **`data/` 與 stdout 不一致要修正** — 唔准留低矛盾數字。
6. **`ref` 只放路徑** — 內容唔入 `problem_register/`。
