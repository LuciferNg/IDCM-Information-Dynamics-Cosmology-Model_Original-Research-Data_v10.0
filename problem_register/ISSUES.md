# register 問題清單（按 O 系列順序）

生成：2026-10-23｜來源 `register.py check`（jsonl 2883 events，hash chain 0 斷點）

## 修復記錄（2026-10-23）

- hash mismatch 43 條 → 全鏈重簽（內容零改動，只重算 `prev_hash`/`hash`）
  - 來源：目錄改名改 ref/slug 17 條、ref 修補 9 條、cli 寫入 bug 16 條、手動 append 無 hash 1 條
- 鏈斷 3 處 → 修復（L2147 事件被刪、L2412 無 hash、L2420 後插分叉）
- 備份：`register.jsonl.pre_hashfix_20261023_213256`
- 驗證：`register.py check` → `已知歷史斷點 0 / 新增斷點 0`

## 未解決問題（54 條，按 O 序）

| 編號 | 類型 | 說明 |
|------|------|------|
| O1 | STATUS-DRIFT | O1 register=merged README=closed |
| O4 | DUPLICATE-DIR | O4 has 2 directories: ['open_problems_fresh/o4_fib_motivation', 'open_problems_fresh/o4_renew'] |
| O17 | COLLISION-STALE | O17 registered as collision but now has 1 dir(s) |
| O38 | REF-MISSING | O38 ref -> scratch:o38_handoff_check_20261018.py does not exist |
| O38 | REF-MISSING | O38/m0-scale ref -> open_problems_fresh/o38_kappa_prediction/docs/29_lambda_scale_reconciliation.md does not exist |
| O124 | REF-MISSING | O124 ref -> register.jsonl does not exist |
| O142 | REF-MISSING | O142 ref -> open_problems_fresh/o142_boson_mass_derivation/docs/36_lambda_scale_adjudication.md ; \| open_problems_fresh/o38_kappa_prediction/docs/29_l |
| O142 | REF-MISSING | O142 ref -> open_problems_fresh/o142_boson_mass_derivation/docs/36_lambda_scale_adjudication.md ; does not exist |
| O143 | COLLISION-STALE | O143 registered as collision but now has 1 dir(s) |
| O185 | BLOCK-DRIFT | o185_string_theory_correspondence/SESSION_START.md: block=open register=closed |
| O198 | README-ONLY | O198 has README row but no register row |
| O225 | BLOCK-DRIFT | o225_mechanism_born_forcing/01_problem_record.md: block=registered register=partial |
| O227 | BLOCK-DRIFT | o227_mapping_channel_no_signalling/01_problem_record.md: block=closed register=partial |
| O228 | BLOCK-DRIFT | o228_evaluation_resource_geometry/01_problem_record.md: block=registered register=partial |
| O231 | BLOCK-DRIFT | o231_super_ym_idcm_qft/01_problem_record.md: block=open register=registered |
| O231 | BLOCK-DRIFT | o231_super_ym_idcm_qft/SESSION_START.md: block=open register=registered |
| O237 | BLOCK-DRIFT | o237_mass_roadmap_kchain_to_perception/01_problem_record.md: block=registered register=partial |
| O237 | BLOCK-DRIFT | o237_mass_roadmap_kchain_to_perception/SESSION_START.md: block=registered register=partial |
| O239 | BLOCK-DRIFT | o239_a5_tension_condensate/01_problem_record.md: block=registered register=partial |
| O240 | BLOCK-DRIFT | o240_vacuum_energy_full_closure/01_problem_record.md: block=registered register=closed |
| O240 | BLOCK-DRIFT | o240_vacuum_energy_full_closure/SESSION_START.md: block=registered register=closed |
| O241 | BLOCK-DRIFT | o241_vacuum_fluctuation_phenomenology/01_problem_record.md: block=registered register=partial |
| O241 | BLOCK-DRIFT | o241_vacuum_fluctuation_phenomenology/SESSION_START.md: block=registered register=partial |
| O247 | BLOCK-DRIFT | o247_natural_contamination_ladder/01_problem_record.md: block=registered register=partial |
| O247 | BLOCK-DRIFT | o247_natural_contamination_ladder/SESSION_START.md: block=registered register=partial |
| O250 | BLOCK-DRIFT | o250_k_tree_idcm_native_running/01_problem_record.md: block=registered register=partial |
| O250 | BLOCK-DRIFT | o250_k_tree_idcm_native_running/SESSION_START.md: block=registered register=partial |
| O252 | BLOCK-DRIFT | o252_los_obscuration_operator/01_problem_record.md: block=registered register=partial |
| O252 | BLOCK-DRIFT | o252_los_obscuration_operator/SESSION_START.md: block=registered register=partial |
| O256 | BLOCK-DRIFT | o256_cl_continuum_envelope/SESSION_START.md: block=registered register=partial |
| P14 | BLOCK-DRIFT | main_problems/p14_global_routing_table/SESSION_START.md: block=open register=partial |
| P14 | BLOCK-DRIFT | main_problems/p14_global_routing_table/01_problem_record.md: block=open register=partial |
| M1 | BLOCK-DRIFT | v11:main_problems/m1_mass_file_schema/SESSION_START.md: block=registered register=merged |
| M1 | BLOCK-DRIFT | v11:main_problems/m1_mass_file_schema/01_problem_record.md: block=registered register=merged |
| M2 | BLOCK-DRIFT | v11:main_problems/m2_sync_desync_exchange/SESSION_START.md: block=registered register=merged |
| M2 | BLOCK-DRIFT | v11:main_problems/m2_sync_desync_exchange/01_problem_record.md: block=registered register=merged |
| M3 | BLOCK-DRIFT | v11:main_problems/m3_omega_ratio_lock/SESSION_START.md: block=registered register=merged |
| M3 | BLOCK-DRIFT | v11:main_problems/m3_omega_ratio_lock/01_problem_record.md: block=registered register=merged |
| cmb_cold_spot/3d-chiral-shape | REF-MISSING | cmb_cold_spot/3d-chiral-shape ref -> O223 \| O185/IF4 \| O7 does not exist |

## 統計

- BLOCK-DRIFT: 28
- REF-MISSING: 6
- COLLISION-STALE: 2
- STATUS-DRIFT: 1
- DUPLICATE-DIR: 1
- README-ONLY: 1

- NO-BLOCK 646、SEED-DISAGREE 57（資訊性，不計入）
