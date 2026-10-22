# O225 事故記錄：`01_problem_record.md` 被清空與重建（2026-10-01）

> 性質：**工具層事故（自傷）**，非推導錯誤；已完全重建並經獨立審計驗證。**未新增任何推導**。

## 一、事故

R25 收口時，以 `io.open(P,'w').write(io.open(P).read()+sec)` 更新狀態與 append §三十五。
Python 求值次序使 `open('w')` **先截斷**才執行內層 `read()` ⟹ 讀回空字串 ⟹ 全檔（自 03:21 之 75 行至 19:07 之 58,594 bytes）被覆寫為僅 §三十五。

- 觸發面：`execute_code` 直寫磁碟，**不受** `write_file` 之「先讀後寫」閘保護，亦**不入** Hermes checkpoints store（該 store 只記 `write_file`／`patch` 工具之編輯）。
- 因此 `~/.hermes/backups/`（無 o225 條目）、checkpoints（無 o225 檔名）、git（本目錄未追蹤）**三路皆無副本**。

## 二、重建來源（唯一可行路線：session DB `state.db`）

| 段 | 來源 | 說明 |
|---|---|---|
| §一–§八 ＋ registry 塊 | msg 284748（2026-10-01 03:21 之全文 `read_file` 工具結果） | 逐 byte 還原，去行號前綴 |
| §九–§三十五 | 各輪 append 之 **op-log**（`messages.tool_calls` 內嵌之節文） | verbatim；僅還原 JSON 轉義、`@@NOW@@`／`%s` 時間佔位符，並裁去其後接續之腳本碼 |
| §十六（R9） | msg 286528／286595（含判據字串「逐 (a,g) 鍵之 x-和消失」之真節） | 先前抽取誤取他節之引用，經字串判據重新定位 |

重組腳本：`~/.hermes/cache/scratch/o225_rebuild3.py`（先驗證後寫入：斷言章節不重複、無 `\n` 殘留、無行號、圍欄平衡、`R1–R23` 與 §十六判據字串在場）。重建腳本與抽取中間檔存於 scratch（按規則不入 MANIFEST）。

## 三、驗證與殘差

- 獨立審計：`scripts/82` = **8/8**、`scripts/36` = **32/32**、`scripts/37` = **10/10**、`scripts/47` = 8/8（MANIFEST 更新後）。
- 重建後 **608 行／48,387 bytes** vs 事故前 19:07 之 58,594 bytes：差約 17%，主因為 close-out 期之**逐行註記**（register/§六-c 接手表之現場注記）未落於 op-log 之節文內。
- 已知殘差：上述註記不復原；檔內以「事故重建說明」塊明示；sha 見 `data/MANIFEST.json`（v28）。

## 四、防止再犯（已寫入 skill）

1. 任何 append 一律 `p=''`：`txt = io.open(P, encoding='utf-8').read()` → `txt += sec` → `io.open(P,'w',encoding='utf-8').write(txt)`；**永不**在同一運算式內同時 `open('w')` 與 `read()`。
2. 對「歷史記錄檔」之寫入，優先改用 `patch` 工具（進 checkpoints）或 `write_file`（有讀寫閘）。
3. 事故當下**先凍結現場**（把殘檔另存 `.CORRUPT.bak`）再動手。
