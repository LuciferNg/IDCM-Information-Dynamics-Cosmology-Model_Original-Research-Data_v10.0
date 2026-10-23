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

### 2026-10-24c — M1/M2/M3 假 BLOCK-DRIFT 之放大器（`iter_docs` 重複掃描）
- **現象**：同一 6 條假漂移（M1/M2/M3 × 2 檔）在 check 報告出現 **3 次**（18 條）。
- **根因**：`iter_docs()` 同一物理檔可由多個 theme 名抵達（`M1`/`m1`/`v11.0`、`P10`/`kchain_number_field`…）
  ⟹ 全庫 **43 檔重掃 2–3×（+51 yield）**，任何 BLOCK-DRIFT／NO-BLOCK 被放大。
- **修法**：`iter_docs()` 以 `realpath` 去重（首次 sorted 命中為準）；不影響任何判斷邏輯。
- **驗證**：yields 757→706（dups 0）；`check` HARD DRIFT 0、chain 0 斷點；
  NO-BLOCK 646→**616**（去重後真實數）。
- **負控制**：M3 block=merged 照報 BLOCK-DRIFT；`M9` 照報 BLOCK-UNREGISTERED；
  legacy 只有細寫 row 時 fallback 仍生效。
- 備份：`register.py.pre_m3statededup_20261024_014030`
