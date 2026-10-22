# O210 docs/13 — 推導鏈主表（**逐個列完整檔名**）

> 依 skill `idcm-closeout` §4.9：鏈表 doc **必須逐個列完整檔名**（只寫範圍／代號 ⟹ 一閉合就「看似冇腳本」）。
> 本表由 `scripts/10_audit_independent.py` §K①b **機械核對**（每支劇本名必須見於本檔或 `01_problem_record.md`）。
> 日期：2026-10-03（收尾輪）；全部路徑相對於本 O 目錄。

---

## 1. 劇本鏈（磁碟全集，13 支）

| # | 完整檔名 | 輪次 | 角色 | 產物 | 正典 log |
|:-:|:---------|:-----|:-----|:-----|:---------|
| 1 | `scripts/01_closure_verify.py` | R1 首輪 | 閉合性驗證 G1–G12（型別/運算/憲章/譜） | — | `logs/01_closure_verify.out` ✅ 129/129 |
| 2 | `scripts/02_type_registry.py` | R1 | 型別註冊表（90 條目）＋ T0 判準＋重寫率 | `data/02_type_registry.json` | `logs/02_type_registry.out` ✅ PASS |
| 3 | `scripts/03_inbound_recompute.py` | R1/更正 | 入站重算（O222 8/13 更正 + O88 身份） | — | `logs/03_inbound_recompute.out` ✅ 18/0 |
| 4 | `scripts/04_escape_period_derivation.py` | R2 續攻1 | 定理 T1（模 B 定則）＋ B-擾動 | — | `logs/04_escape_period_derivation.out` ✅ 27/27 |
| 5 | `scripts/05_operator_layer_selection.py` | R3 續攻2 | 定理 T2（no-go）＋ 七結構容許性 | — | `logs/05_operator_layer_selection.out` ✅ 23/23 |
| 6 | `scripts/06_branch_charge_definition.py` | R5 續攻4 | 定理 T3（分支荷 = 中心荷；1507 分量） | — | `logs/06_branch_charge_definition.out` ✅ 12/12 |
| 7 | `scripts/07_ktree_two_counts.py` | R5 續攻4 | C9 雙計數（34/33）＋ 標籤強制 | — | `logs/07_ktree_two_counts.out` ✅ 13/13 |
| 8 | `scripts/08_z4_bridge_definition.py` | R6 續攻5 | 定理 T4（ℤ₄ 扇區）＋ C10（站-模對偶） | — | `logs/08_z4_bridge_definition.out` ✅ 23/23 |
| 9 | `scripts/09_common_measure.py` | R7 續攻6 | T5/T6 ＋ 共同測度 no-go | — | `logs/09_common_measure.out` ✅ 19/19 |
| 10 | `scripts/10_audit_independent.py` | R8 收尾 | **全鏈獨立審計**（段 A–G ＋ §4.9 K 段獨立重做） | `data/audit/independent_recheck.json` | `logs/10_audit_independent.out` |
| 11 | `scripts/11_session_chain_provenance.py` | R8 收尾 | **全 session 鏈 provenance**（硬規則 1 ＋ §4.9⑤ inline 偵測） | `data/audit/session_chain_o210.json` | `logs/11_session_chain_provenance.out` |
| 12 | `scripts/12_register_coverage.py` | R8 收尾 | **登記面覆蓋核對**（§4.10 七項） | `data/audit/register_coverage.json` ＋ `data/audit/_check.txt` | `logs/12_register_coverage.out` |
| 13 | `scripts/13_manifest.py` | R8 收尾 | **MANIFEST 產生器**（收尾凍結；**必須最後跑**） | `data/MANIFEST.json` | `logs/13_manifest.out` |
| — | `scripts/run_chain.sh` | R8 收尾 | **driver of record**（預設 dry-run；`--execute` 才跑） | 全部 log（正典） | — |

**鏈次序**（§4.9 ⑥）：`run_chain.sh` → 01…**13**。磁碟劇本編號 **01–13 連續無缺號**（declared-gaps = 空）。
⚠️ **次序硬約束**：`13_manifest.py` 只能跑喺**全部寫入之後**（最後一支）；跑完之後任何寫入都會令 MANIFEST sha 失效（C4 FAIL）。

---

## 2. 文檔鏈（14 份）

| 檔 | 輪次 | 性質 |
|:---|:-----|:-----|
| `docs/01_type_system.md` | R1 | 型別系統（四型） |
| `docs/02_operations_closure.md` | R1 | 運算封閉集（七運算） |
| `docs/03_normalization_charter.md` | R1（＋§五–§九 append-only） | **歸一化憲章**（C1–C12、D1–D10、T4–T6） |
| `docs/04_rewrite_report.md` | R1 | 重寫率報告（88.9%） |
| `docs/05_inbound_handoff.md` | R1/更正 | 入站交接（O88/O222） |
| `docs/06_escape_period_theorem.md` | R2（＋§7 更正） | 定理 T1 |
| `docs/07_operator_layer_selection.md` | R3（＋§9、§10） | 定理 T2 ＋ ℤ₄ 狀態 |
| `docs/08_branch_charge_no_go.md` | R5 | 定理 T3 ＋ 條件 ③ |
| `docs/09_ktree_two_counts.md` | R5 | C9 雙計數（裁定修正） |
| `docs/10_z4_bridge.md` | R6 | 定理 T4 ＋ C10 |
| `docs/11_common_measure_no_go.md` | R7 | T5/T6 ＋ 共同測度 no-go |
| `docs/12_full_chain_closeout.md` | R8 | **全鏈收尾報告**（T0–T5 ＋ §4.9／§4.10） |
| `docs/13_script_chain.md` | R8 | 本檔（推導鏈主表） |
| `01_problem_record.md` / `final_result.md` / `SESSION_START.md` | 全輪 | 問題記錄（append-only）／活摘要／**不可變快照** |

---

## 3. 資料／日誌

- `data/02_type_registry.json`（產者：`scripts/02`）
- `data/audit/independent_recheck.json`（產者：`scripts/10`）
- `data/audit/session_chain_o210.json`（產者：`scripts/11`）
- `data/audit/register_coverage.json` ＋ `data/audit/_check.txt`（產者：`scripts/12`）
- `data/audit/hygiene_o210.json`（產者：外部核對器 `path_hygiene_scan.py`，報告見 `docs/12` §3）
- `data/audit/binding_o210.json`（產者：外部核對器 `numeric_producer_binding.py`）
- `data/MANIFEST.json`（收尾凍結：sha256 ＋ `untracked_by_design`；產者 = `scripts/13_manifest.py`）
- `logs/01…13_*.out`（13 支，全部帶 `RESULT:` 行）

> ⚠️ 本表由收尾輪建立；R1–R7 之劇本當時**未**寫正典 log（幽靈風險已由本輪補齊：全部 13 支重跑並落 log）。
> ⚠️ **`13_manifest.py` 係鏈上最後一支**：佢跑完之後任何寫入（含 docs／register 之外嘅檔案）都會令 MANIFEST sha 失效 ⟹ 要重新 `--execute` 全鏈。
