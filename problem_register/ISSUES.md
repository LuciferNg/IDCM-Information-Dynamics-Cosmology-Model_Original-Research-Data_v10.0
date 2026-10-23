# register 問題清單（按 O 系列順序）

生成：2026-10-24｜來源 `register.py check`（jsonl 2921 events）
`chain: 已知歷史斷點 0（append-only 白名單）  新增斷點 0`

## 修復記錄

### 2026-10-23 — hash chain
- hash mismatch 43 條 → 全鏈重簽（內容零改動，只重算 `prev_hash`/`hash`）
  - 來源：目錄改名改 ref/slug 17、ref 修補 9、cli 寫入 bug 16、手動 append 無 hash 1
- 鏈斷 3 處 → 修復（L2147 事件被刪、L2412 無 hash、L2420 後插分叉）
- 備份：`register.jsonl.pre_hashfix_20261023_213256`

### 2026-10-24 — O198 刪除（用戶指示「直接刪除 O198 register 記錄」）
- 刪除 2 條 legacy tombstone 事件（09-27、10-03）
- 刪除 sqlite `event` 2 行 + `reserved_num` num=198
- 刪除 `open_problems_fresh/README.md` O198 row（合併歷史保留於 O197 row「★O198 合併」）
- 鏈重簽：0 mismatch / 0 break
- 備份：`register.jsonl.pre_delO198_20261024_014101`、`README.md.pre_delO198_*`

## 未解決問題（0 條）

`register.py check`：HARD DRIFT **0**
（NO-BLOCK 646、SEED-DISAGREE 54 屬資訊性，不計入）
