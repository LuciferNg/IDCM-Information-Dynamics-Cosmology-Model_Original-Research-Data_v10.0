# register 問題清單（按 O 系列順序）

生成：2026-10-23｜來源 `register.py check`（jsonl 2920 events）｜`chain: 已知歷史斷點 0（append-only 白名單）  新增斷點 0`

## 修復記錄（2026-10-23）

- hash mismatch 43 條 → 全鏈重簽（內容零改動，只重算 `prev_hash`/`hash`）
  - 來源：目錄改名改 ref/slug 17 條、ref 修補 9 條、cli 寫入 bug 16 條、手動 append 無 hash 1 條
- 鏈斷 3 處 → 修復（L2147 事件被刪、L2412 無 hash、L2420 後插分叉）
- 備份：`register.jsonl.pre_hashfix_20261023_213256`
- 驗證：`已知歷史斷點 0 / 新增斷點 0`

## 未解決問題（8 條，按 O 系列順序）

| 編號 | 類型 | 說明 |
|------|------|------|
| O198 | README-ONLY | O198 has README row but no register row |
| M1 | BLOCK-DRIFT | v11:main_problems/m1_mass_file_schema/SESSION_START.md: block=registered register=merged |
| M1 | BLOCK-DRIFT | v11:main_problems/m1_mass_file_schema/01_problem_record.md: block=registered register=merged |
| M2 | BLOCK-DRIFT | v11:main_problems/m2_sync_desync_exchange/SESSION_START.md: block=registered register=merged |
| M2 | BLOCK-DRIFT | v11:main_problems/m2_sync_desync_exchange/01_problem_record.md: block=registered register=merged |
| M3 | BLOCK-DRIFT | v11:main_problems/m3_omega_ratio_lock/SESSION_START.md: block=registered register=merged |
| M3 | BLOCK-DRIFT | v11:main_problems/m3_omega_ratio_lock/01_problem_record.md: block=registered register=merged |
| cmb_cold_spot/3d-chiral-shape | REF-MISSING | cmb_cold_spot/3d-chiral-shape ref -> O223 \| O185/IF4 \| O7 does not exist |

## 統計

- README-ONLY: 1
- REF-MISSING: 1
- BLOCK-DRIFT: 6

- 涉及 5 個 pid
- NO-BLOCK 646、SEED-DISAGREE 57（資訊性，不計入）
