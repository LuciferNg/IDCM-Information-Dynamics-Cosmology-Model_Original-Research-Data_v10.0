# O228 — 求值語義之資源幾何與最小性（Resource Geometry & Minimality）

<!-- registry
pid:     O228
title:   求值語義之資源幾何與最小性（Resource Geometry & Minimality）
state:   partial
verdict: partial
flags:   -
owner:   O228
created: 2026-09-30
updated: 2026-10-02
prereq:  O222
dir:     open_problems_fresh/o228_evaluation_resource_geometry/
source:  O222 完整性 closeout 分流（調律者指令 2026-09-30：「開新o，把剩下開題分開幾個o解決，保留o222開放作為最終裁決及整合」）
-->

# O228 — 求值語義之資源幾何與最小性（Resource Geometry & Minimality）

> **狀態**: 🟡 **部分閉合（partial）— R1–R14 已推；殘餘 5 項見 `final_result.md` §十五**（依 O222 no-go 邊界憲章 `docs/45`）
> **建立/更新**: 2026-09-30｜**狀態更新**: 2026-10-02｜**位置**: `open_problems_fresh/o228_evaluation_resource_geometry/`
> **前置**: **O222 保留開放作最終裁決及整合**；本 o 承接憲章判決項：**§3 資源幾何（正面清單）之完整刻畫與推廣**
> **目標權威來源**: `open_problems_fresh/o222_qm_evaluation_semantics/docs/45_no_go_boundary_charter.md`

---

## 一、問題陳述
**資源幾何之完整刻畫與一般 N 推廣**：把已精確化之資源量（最小分離幀 4／秩-6 最小 6／`reads = 3N²` 等）升級為**一般定理**，並求封閉形式；同時產出**資源側可證偽預言**（P4/P6 類），供未來協定做樣本外盲測。

## 二、已確立嘅結構（引用自 O222，逐項附出處）
```
🟢 最小分離幀 = **4**（全枚舉 12,645 個；隨機基準率 = 12645/557845 = 2.2668%；含單一家族 EEEE 625 個）
🟢 秩-6 最小規模 = **6**（維數論證 ＋ 顯式基 V00–V05，且同時分離 12 列型）
🟢 RT1 典範映射**單射 120/120**；字長分布 {0:1, 1:62, 2:57} ⟹ Cayley 直徑 = **2**
🟢 呈現冗餘 = **62 個長度-2 正關係**（EE 30／FF 20／VV 12）⟹ 生成集**反逆封閉**；態 0 最短字恰 62 條
🟢 成本律：reads = 3N² = 11532、hits = 2N = 124、overrides ∈ [52,80]（26 值）；**典範字 = 成本最小（120/120）**
🟢 軸集大量冗餘（58/62 可刪）；家族階譜 V↔5／F↔3／E↔4；機器原生 2I 雙重校準
🔴 一般 N 之幀計數閉式；一般機器定理；呈現理論之普遍性
```

## 三、未確立（🔴 開放問題 = 本 o 之判決項）
```
🔴 最小幀計數閉式：F(N) = ?（現僅 N = 62 之精確值 12,645）
🔴 一般機器定理：秩/幀/成本律對任意（群, 讀出表）之形式（承 R24/③ rz(n) 之 Zarankiewicz 類問題）
🔴 呈現理論：生成集反逆封閉之普遍性；最小關係長度之規律
🔴 資源側盲測預言：未見 N 之預測值須事先書面預言（P4/P6 類）
```

## 四、攻擊路線
```
1. 幀計數推廣：小 N 全枚舉 → 序列擬合/閉式猜測 → **盲測**驗證（中成本）
2. 一般機器定理：抽象化（群階、直徑、家族階譜）下之幀/基界（中成本）
3. 呈現理論：最小關係長度與生成集結構定理（中成本）
```

## 五、驗證標準
```
✅ 閉式 ＋ 全量驗證（小 N 全枚舉對照）
✅ 盲測預測（未見 N 之值須**事先書面**預言，後驗改動即失效）
✅ 零新參數；禁 φ-power／事後凑算子；與 docs/45 §3 數字一致
```

**四道硬測試**（閉合宣稱必過）：① 自由度成本（零參數）② Monte-Carlo null（10⁷ 樣本，5σ）③ 可證偽＋樣本外盲測 ④ 結構剛性（擾動測試）

## 六、O222 交接依據（**只讀，唔喺 O222 寫任何檔**）
- 憲章：`o222_qm_evaluation_semantics/docs/45_no_go_boundary_charter.md`（B1–B6 ＋ §3 正面清單 ＋ §4 唔屬域）
- 證據文檔：`docs/13`（P2d）、`docs/19`（C2G7 七判準）、`docs/35`（QM 六項）、`docs/38`（R24）、`docs/39`（R25 amplitude）、`docs/40`（R26 G1/G8）、`docs/41`（R27）、`docs/42`（R28）、`docs/43`（R29 RT1＋邊界＋P1–P7）、`docs/44`（完整性 closeout）
- 可重跑基礎設施（唯讀）：`o222.../scripts/12_b5_budget.py`（`load_machine()`）、`scripts/07_artifact_integrity.py`、`scripts/32_closeout3_audit.py`；`data/frozen/MANIFEST.json`（349 件）
- register：O222 ↔ 本 o 之 handoff（ref 全部 in-scope）

## 七、紀律（沿用 O222 全套）
合約＋強制先於任何數字｜預註冊先於運算｜全量無優化（零剪枝、精確算術）｜零參數／零擬合（禁後驗湊算子、禁 φ-power fitting）｜「無效才是正確」｜每輪 docs/＋scripts/＋data/＋logs/＋MANIFEST＋register（append-only）｜四道硬測試全過方可宣稱閉合｜**唔准**在其他 O 目錄寫檔（跨 O 只經 register）

---

## 八、檔案閉合水位（close-out watermark；建立於 2026-10-02 14:07）

> 本欄為 **live field**：`上次檔案更新` = `stat` 實際 mtime；`上次 closed-out` = 完成驗證之時刻。
> 首次建立（本 O 自 R1 起從未 closed-out）⟹ **109 件全部全檔驗**，其後只驗水位之後新增／改動之內容。
> 唯一例外：`logs/24_closeout*`、`data/24_closeout*`（審計自產物，每次執行重寫）＝**宣告式 untracked-by-design**，
> 由每輪唯讀收尾核對（`logs/24_closeout_final_verify.out`）驗其完整性，不進 MANIFEST。

| # | 檔案 | 上次檔案更新 (mtime) | 上次 closed-out | 已驗範圍 | 狀態 |
|:-:|:-----|:---------------------|:----------------|:---------|:-----|
| 1 | `docs/00_r1_contract.md` | 2026-10-02 06:47 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 2 | `docs/01_r1_results.md` | 2026-10-02 08:13 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 3 | `docs/02_r2_contract.md` | 2026-10-02 07:26 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 4 | `docs/02_r2_results.md` | 2026-10-02 07:43 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 5 | `docs/03_r3_contract.md` | 2026-10-02 07:42 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 6 | `docs/04_r3_results.md` | 2026-10-02 08:18 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 7 | `docs/05_r5_contract.md` | 2026-10-02 10:35 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 8 | `docs/06_r5_results.md` | 2026-10-02 11:17 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 9 | `docs/07_r6_contract.md` | 2026-10-02 11:19 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 10 | `docs/08_r6_results.md` | 2026-10-02 11:20 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 11 | `docs/09_r7_contract.md` | 2026-10-02 11:32 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 12 | `docs/10_r7_results.md` | 2026-10-02 11:56 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 13 | `docs/11_r8_contract.md` | 2026-10-02 12:01 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 14 | `docs/12_r8_results.md` | 2026-10-02 12:19 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 15 | `docs/13_r9_contract.md` | 2026-10-02 12:29 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 16 | `docs/14_r9_results.md` | 2026-10-02 12:32 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 17 | `docs/15_r10_contract.md` | 2026-10-02 12:39 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 18 | `docs/16_r10_results.md` | 2026-10-02 13:15 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 19 | `docs/17_r11_contract.md` | 2026-10-02 13:20 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 20 | `docs/18_r11_results.md` | 2026-10-02 13:39 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 21 | `docs/19_r12_contract.md` | 2026-10-02 13:46 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 22 | `docs/20_r12_results.md` | 2026-10-02 13:48 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 23 | `scripts/01_r1_census.py` | 2026-10-02 06:48 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 24 | `scripts/02_r1_closed_form.py` | 2026-10-02 07:21 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 25 | `scripts/03_r1_audit.py` | 2026-10-02 07:27 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 26 | `scripts/04_r2_general_machine.py` | 2026-10-02 07:41 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 27 | `scripts/05_r2_protocol_cost.py` | 2026-10-02 07:32 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 28 | `scripts/06_r3_hard_tests.py` | 2026-10-02 08:07 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 29 | `scripts/07_null_scope_audit.py` | 2026-10-02 08:02 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 30 | `scripts/08_manifest.py` | 2026-10-02 14:03 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 31 | `scripts/09_r5_kmin_law.py` | 2026-10-02 11:05 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 32 | `scripts/10_r6_lp_certificate.py` | 2026-10-02 11:20 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 33 | `scripts/11_r7_pat_exact.py` | 2026-10-02 11:34 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 34 | `scripts/12_r7_lambda_profile.py` | 2026-10-02 11:41 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 35 | `scripts/13_r7_gap_law.py` | 2026-10-02 11:37 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 36 | `scripts/14_r7_pat_enum.py` | 2026-10-02 11:44 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 37 | `scripts/15_r7_pat_certificate.py` | 2026-10-02 11:47 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 38 | `scripts/16_r7_pat_decisive.py` | 2026-10-02 11:54 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 39 | `scripts/17_r8_critical_submachine.py` | 2026-10-02 12:02 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 40 | `scripts/18_r8_critical_submachine_dfs.py` | 2026-10-02 12:08 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 41 | `scripts/19_r8_delocalisation.py` | 2026-10-02 12:16 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 42 | `scripts/20_r9_closure.py` | 2026-10-02 12:31 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 43 | `scripts/21_r10_branch_certificate.py` | 2026-10-02 13:08 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 44 | `scripts/22_r11_opt_frame_census.py` | 2026-10-02 13:30 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 45 | `scripts/23_r12_cut_ladder.py` | 2026-10-02 13:46 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 46 | `scripts/24_closeout_audit.py` | 2026-10-02 14:03 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 47 | `data/00_o228_manifest.json` | 2026-10-02 14:03 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 48 | `data/01_r1_census.json` | 2026-10-02 06:48 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 49 | `data/02_r1_closed_form.json` | 2026-10-02 07:26 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 50 | `data/03_r1_audit.json` | 2026-10-02 07:27 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 51 | `data/04_r2_general_machine.json` | 2026-10-02 07:42 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 52 | `data/05_r2_protocol_cost.json` | 2026-10-02 07:33 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 53 | `data/06_r3_hard_tests.json` | 2026-10-02 08:07 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 54 | `data/07_null_scope_audit.json` | 2026-10-02 08:03 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 55 | `data/09_r5_kmin_law.json` | 2026-10-02 11:05 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 56 | `data/10_r6_lp_certificate.json` | 2026-10-02 11:20 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 57 | `data/12_r7_lambda_profile.json` | 2026-10-02 11:41 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 58 | `data/13_r7_gap_law.json` | 2026-10-02 11:41 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 59 | `data/15_r7_pat_certificate.json` | 2026-10-02 11:48 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 60 | `data/16_r7_pat_decisive.json` | 2026-10-02 11:56 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 61 | `data/19_r8_delocalisation.json` | 2026-10-02 12:18 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 62 | `data/20_r9_closure.json` | 2026-10-02 12:32 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 63 | `data/21_r10_branch_certificate.json` | 2026-10-02 13:12 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 64 | `data/22_r11_opt_frame_census.json` | 2026-10-02 13:32 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 65 | `data/23_r12_cut_ladder.json` | 2026-10-02 13:47 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 66 | `data/24_closeout_audit.json` | 2026-10-02 14:05 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 67 | `logs/01_r1_census.out` | 2026-10-02 06:48 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 68 | `logs/02_r1_closed_form.out` | 2026-10-02 07:26 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 69 | `logs/02_r1_firstrun_C17_FAIL_excerpt.out` | 2026-10-02 07:14 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 70 | `logs/03_chain.status` | 2026-10-02 07:26 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 71 | `logs/03_chain.status.NOTE` | 2026-10-02 08:13 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 72 | `logs/03_r1_audit.out` | 2026-10-02 07:27 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 73 | `logs/03_r1_audit_firstrun_B3_FAIL_excerpt.out` | 2026-10-02 07:27 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 74 | `logs/04_r2_firstrun_CRASH_excerpt.out` | 2026-10-02 08:13 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 75 | `logs/04_r2_general_machine.out` | 2026-10-02 07:42 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 76 | `logs/05_r2_protocol_cost.out` | 2026-10-02 07:33 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 77 | `logs/06_r3_firstrun_FAIL_excerpt.out` | 2026-10-02 07:49 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 78 | `logs/06_r3_hard_tests.out` | 2026-10-02 08:07 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 79 | `logs/07_null_scope_audit.out` | 2026-10-02 08:03 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 80 | `logs/08_manifest.out` | 2026-10-02 14:03 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 81 | `logs/09_r5_firstfullrun_4FAIL_excerpt.out` | 2026-10-02 10:54 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 82 | `logs/09_r5_firstrun_CRASH_excerpt.out` | 2026-10-02 10:41 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 83 | `logs/09_r5_kmin_law.out` | 2026-10-02 11:05 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 84 | `logs/09_r5_secondrun_CRASH_excerpt.out` | 2026-10-02 10:45 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 85 | `logs/09_r5_syntaxerror_excerpt.out` | 2026-10-02 11:16 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 86 | `logs/10_r6_lp_certificate.out` | 2026-10-02 11:20 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 87 | `logs/11_r7_pat_exact.out` | 2026-10-02 11:43 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 88 | `logs/12_r7_lambda_profile.out` | 2026-10-02 11:41 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 89 | `logs/13_r7_gap_law.out` | 2026-10-02 11:41 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 90 | `logs/14_r7_pat_enum.out` | 2026-10-02 11:45 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 91 | `logs/15_r7_pat_certificate.out` | 2026-10-02 11:48 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 92 | `logs/16_r7_pat_decisive.out` | 2026-10-02 11:56 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 93 | `logs/17_r8_critical_submachine.out` | 2026-10-02 12:07 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 94 | `logs/18_r8_critical_submachine_dfs.out` | 2026-10-02 12:14 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 95 | `logs/19_r8_delocalisation.out` | 2026-10-02 12:18 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 96 | `logs/20_r9_closure.out` | 2026-10-02 12:32 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 97 | `logs/21_r10_branch_certificate.out` | 2026-10-02 13:12 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 98 | `logs/21_r10_firstrun_BUG_indexings.out` | 2026-10-02 13:07 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 99 | `logs/21_r10_secondrun_small_budget.out` | 2026-10-02 13:08 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 100 | `logs/22_r11_firstrun_BUG_prune.out` | 2026-10-02 13:25 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 101 | `logs/22_r11_opt_frame_census.out` | 2026-10-02 13:32 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 102 | `logs/22_r11_secondrun_capped.out` | 2026-10-02 13:31 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 103 | `logs/23_r12_cut_ladder.out` | 2026-10-02 13:47 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 104 | `logs/24_closeout_audit.out` | 2026-10-02 14:05 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 105 | `logs/24_closeout_firstrun_expectation_bugs.out` | 2026-10-02 13:58 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 106 | `logs/24_closeout_secondrun_manifest_sync.out` | 2026-10-02 14:01 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 107 | `01_problem_record.md` | 2026-09-30 22:53 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 108 | `SESSION_START.md` | 2026-10-02 13:48 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |
| 109 | `final_result.md` | 2026-10-02 13:48 | 2026-10-02 14:06 | 全文 | ✅ 已驗 |

**R13 水位更新（2026-10-02 16:19）**：本輪新增 4 件 —— `docs/22_r13_contract.md`、`docs/23_r13_results.md`、
`scripts/25_r13_separation.py`、`data/25_r13_separation.json`、`data/25_r13_frames.json`、`logs/25_r13_separation.out`、
`logs/25_r13_firstrun_lp_role_mismatch.out` —— 全部**全檔驗**（`scripts/25` = 9/11 PASS ＋1 N/A；首跑已分檔），
`上次 closed-out = 2026-10-02 16:19`。

## 九、推導時序索引（append-only；按輪分組，實際產出次序）

### 第 1 輪（2026-10-02 06:47–08:18）— R1 資源幾何 / R2 一般機器 / R3 硬測試 / R4 null 口徑

| # | 日期 | 步驟 | 產物 | 結果 |
|:-:|:-----|:-----|:-----|:-----|
| 1 | 10-02 06:47 | R1 合約 | `docs/00_r1_contract.md`（`o228-r1-resource-geometry-v1`）| 契約先行 |
| 2 | 10-02 | R1 推導 | `scripts/01–03`、`data/01–03` | K 120×62、秩 6、F_1..F_4、閉式三路對帳 |
| 3 | 10-02 08:13 | R1 結果 | `docs/01_r1_results.md` | R1 closed |
| 4 | 10-02 07:26–07:43 | R2 合約＋推導 | `docs/02_r2_contract.md`、`scripts/04_r2_general_machine.py`、`scripts/05_r2_protocol_cost.py` | 六部機器 k_min 4/5/7/2/3/1、樣本外盲測 |
| 5 | 10-02 | R2 結果／校正 | `docs/02_r2_results.md`、`data/04–05` | T2/B1 FAIL ＋ `-c`；R2 closed |
| 6 | 10-02 07:42–08:18 | R3 硬測試 | `docs/03_r3_contract.md`、`docs/04_r3_results.md`、`scripts/06_r3_hard_tests.py`、`data/06` | 5/8 PASS（H1/H2a/H2b/H2v FAIL ＋ `-c`）|
| 7 | 10-02 | R4 null 口徑審計 | `scripts/07_null_scope_audit.py`、`data/07_null_scope_audit.json` | 5/5 PASS（J1–J4；with-replacement 差 5.7σ）|

### 第 2 輪（10:35–11:20）— R5 `k_min` 律 / R6 LP 憑證

| # | 日期 | 步驟 | 產物 | 結果 |
|:-:|:-----|:-----|:-----|:-----|
| 8 | 10-02 10:35 | R5 合約＋推導 | `docs/05_r5_contract.md`、`scripts/09_r5_kmin_law.py`、`data/09` | `cap(k)=min(2^k,k²−k+2)`；15/21 PASS |
| 9 | 10-02 11:17 | R5 結果 | `docs/06_r5_results.md` | 排列界勝資訊界；`F_5=F_6=0`；ν = {2,3,5,1,2,1} |
| 10 | 10-02 11:19 | R6 合約＋憑證 | `docs/07_r6_contract.md`、`scripts/10_r6_lp_certificate.py`、`data/10` | `LP*(edge)=5<7` ⟹ 線性鬆弛全死（6/6，negative）|
| 11 | 10-02 11:20 | R6 結果 | `docs/08_r6_results.md` | 弱對偶 `ν ≤ LP* ≤ k_min`；LP 之用途係否定 |

### 第 3 輪（11:32–12:32）— R7 三線 / R8 臨界子機器 / R9 精確 IP

| # | 日期 | 步驟 | 產物 | 結果 |
|:-:|:-----|:-----|:-----|:-----|
| 12 | 10-02 11:32–11:56 | R7 三線攻堅 | `docs/09–10`、`scripts/11–16`、`data/12,13,15,16` | ①6/7 ②5/7 ③4/4；`pat(k=6)=26` 精確 |
| 13 | 10-02 12:01–12:19 | R8 臨界子機器 | `docs/11–12`、`scripts/17–19`、`data/19` | 5/7（negative）；五類憑證空間窮盡、障礙非局部化 |
| 14 | 10-02 12:29–12:32 | R9 精確 IP ＋ 成本 | `docs/13–14`、`scripts/20`、`data/20` | 5/7；首例真整數間隙 `ν=3<LP*=4`；憑證成本 31.48% |

### 第 4 輪（12:39–13:48）— R10 B&B / R11 8584 普查 / R12 支撐切平面

| # | 日期 | 步驟 | 產物 | 結果 |
|:-:|:-----|:-----|:-----|:-----|
| 15 | 10-02 12:39–13:15 | R10 非凸憑證 | `docs/15–16`、`scripts/21`、`data/21` | 3/6；顯式 7-覆蓋 ＋ B&B 閉合引理 0；首版 indexing bug 留檔 |
| 16 | 10-02 13:20–13:39 | R11 幀普查 | `docs/17–18`、`scripts/22`、`data/22` | 5/6；**8584 幀**（三重驗證）；首版剪枝 bug 留檔 |
| 17 | 10-02 13:46–13:48 | R12 支撐切平面 | `docs/19–20`、`scripts/23`、`data/23` | 2/5（negative）；方向定理 ＋ 虛擬 pair 編碼；支撐 9-冗餘 |

### 第 5 輪（本輪，2026-10-02 14:07）— CLOSEOUT 審計

| # | 日期 | 步驟 | 產物 | 結果 |
|:-:|:-----|:-----|:-----|:-----|
| 18 | 10-02 | closeout 審計器 | `scripts/24_closeout_audit.py`、`data/24`、`logs/24_closeout_audit.out` | **32/32 PASS**（首輪 28/32 之 4 FAIL 全屬審計器自身）|
| 19 | 10-02 | 審計報告＋文檔 | `docs/21_closeout_audit.md`、本檔 §八／§九、`final_result.md` §十三、`SESSION_START.md` ★CLOSEOUT | 記錄完整性發現 5 條（含 LP 對偶憑證未落碟）|
| 20 | 10-02 | `scripts/08` amendment | `scripts/08_manifest.py`（impl-only 排除清單） | 判定謂詞不變；MANIFEST 刷新為本輪最後寫入 |
| 21 | 10-02 | register 收束 | `problem_register/register.jsonl` | O228 closeout note；母項維持 partial |

**時序完整性確認**：本索引依**實際產出次序**記錄（mtime 證據見 §八）；docs 一律**後於**其 scripts 結果；
本輪新增者只 append，**舊行零改動**（append 前取 md5，append 後舊段 byte-identical）。
**時序完整性規則**：①禁跨文檔以新推導污染舊記錄（舊 doc 只可加 dated 附註）②禁以推導時序回溯污染
（早期輪次列不准寫入後期結論）③`final_result.md` 為**活摘要**（可更新），`docs/00–20` 為**歷史**（只可 append 附註）。

---

## 十、第 6 輪推導時序（append-only；R13）

| # | 日期 | 步驟 | 產物 | 結果 |
|:-:|:-----|:-----|:-----|:-----|
| 22 | 10-02 | R13 合約 | `docs/22_r13_contract.md`（`o228-r13-separation-and-certificate-v1`）| 契約先行（含有效域限制之先聲明）|
| 23 | 10-02 | R13 推導 | `scripts/25_r13_separation.py`、`data/25_r13_separation.json`、`data/25_r13_frames.json` | **9/11 PASS（+1 N/A）** |
| 24 | 10-02 | R13 結果 | `docs/23_r13_results.md`、`final_result.md` §十四、`SESSION_START.md` ★R13 | `M = 9/5`（家族死）＋ 極小覆蓋族 ≥ 130,969 個 size ≥ 8 成員（新發現）|

**時序註**：R13 之首跑（LP 角色 mismatch，`ValueError`/`KeyError`）已分檔保留
（`logs/25_r13_firstrun_lp_role_mismatch.out`）；全量 8584 普查之**從頭 DFS** 見該檔（52.0 s／304,315,585 節點），
另 `scripts/24` 之獨立審計亦重算同一普查（66.2 s／304,315,585 節點）⟹ 兩支獨立實作同值。

---

## 十一、第 7 輪推導時序（append-only；R14）

| # | 日期 | 步驟 | 產物 | 結果 |
|:-:|:-----|:-----|:-----|:-----|
| 25 | 10-02 | R14 合約 | `docs/24_r14_contract.md`（`o228-r14-cover-family-v1`）| 契約先行（含誠實分級條款）|
| 26 | 10-02 | R14 推導 | `scripts/26_r14_cover_family.py`、`data/26_r14_cover_family.json` | **11/14 PASS**（3 FAIL ＋ 3 `-c`）|
| 27 | 10-02 | R14 結果 | `docs/25_r14_results.md`、`final_result.md` §十五、`SESSION_START.md` ★R14 | `M_all = 1` 無條件；`F'_8 ≈ 3.07e6` |

**時序註**：`scripts/26` 有兩次實作錯誤（首跑：`ph` 未定義之插入位置錯；二跑：`two` 計數誤寫成 O(4e9)）—— 首跑 log 分檔
`logs/26_r14_firstrun_prereg_errors.out`；定案跑 = 127.4 s、`data/26` 齊。

---

## 十二、第 8 輪推導時序（append-only；closeout-2）

| # | 日期 | 步驟 | 產物 | 結果 |
|:-:|:-----|:-----|:-----|:-----|
| 28 | 10-02 | drift 修復 | `01_problem_record.md` 塊／`SESSION_START.md` 狀態行；R1–R5 backfill close | HARD DRIFT 32→31；O228 清零 |
| 29 | 10-02 | closeout-2 審計 | `scripts/27`、`logs/27`、`data/27`、`docs/00_closeout_audit.md` | **24/24 PASS** |
| 30 | 10-02 | 事故與還原 | `data/25_r13_separation.json`（git restore） | sha256 ≡ MANIFEST ✓ |
