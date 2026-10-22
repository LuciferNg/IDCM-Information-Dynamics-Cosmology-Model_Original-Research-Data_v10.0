# O227 — 連接通道：對映表、無信號與糾纏熵（Mapping Channel / No-Signalling）

<!-- registry
pid:     O227
title:   連接通道：對映表、無信號與糾纏熵（Mapping Channel / No-Signalling）
state:   closed
verdict: closed
flags:   -
owner:   O227
created: 2026-09-30
updated: 2026-10-02
prereq:  O222
dir:     open_problems_fresh/o227_mapping_channel_no_signalling/
source:  O222 完整性 closeout 分流（調律者指令 2026-09-30：「開新o，把剩下開題分開幾個o解決，保留o222開放作為最終裁決及整合」）
-->

# O227 — 連接通道：對映表、無信號與糾纏熵（Mapping Channel / No-Signalling）

> **狀態**: 🟡 **部分閉合（R1 一輪；26 條 tag：✅ 19／🟡 1／🔴 6）** —— 🔴 之中 `S4a-orig` 為保留之原形式、`B5c` 為否證並更正之預註冊命題、`P2d` 為憲章繼承
> **建立/更新**: 2026-09-30｜**位置**: `open_problems_fresh/o227_mapping_channel_no_signalling/`
> **前置**: **O222 保留開放作最終裁決及整合**；本 o 承接憲章判決項：**B4 · 無複本⟹無熵、B5 · 隨機性上限**
> **目標權威來源**: `open_problems_fresh/o222_qm_evaluation_semantics/docs/45_no_go_boundary_charter.md`

---

## 一、問題陳述
**判定通道層**：① 對映表 13 格之逐格材料化（每格：已凍結物件 ＋ 可計算結構謂詞 ＋ 量到數字，機械可判）；② **B4**：無獨立複本（`R_indep = 1`）⟹ 無糾纏熵／無 Schmidt 分解之**終局性**，及**替代熵量**（帳本熵／陳舊度律）之判準；③ **B5**：隨機性上限 `log₂60 = 5.9069 bits` ⟹ **隨機性擴張不可能**之充要陳述；④ 無信號之序列（多輪）與多方推廣。

## 二、已確立嘅結構（引用自 O222，逐項附出處）
```
🟢 無信號：邊際 62/62 恰 1/2 ⟹ D ≡ 0；條件 3844/3844；ablation ≡ 0；3700 對 0 違反（V²+D² ≤ 1 恆真但空洞）
🟢 B4：R_indep = 1（G8 決定性強迫）；可及深度 = 1；單副本 ⟹ 熵量空缺
🟢 B5：120 初始態 → **恰 60 個相異行為**（類大小全 2；中心 Z₂ 之 2:1；60 = |I|）⟹ log₂60 = 5.9069 bits
🟢 跨運行全量：7140 對一致率 min = 3577/11532、mean = 59/119、**max = 1**（存在完全相同之相異初始態運行）
🟢 帳本律（替代熵量之素材）：hits = 2N = 124（全 120 態恆定）；override ∈ [52,80]（26 值）
🔴 對映表逐格材料化之完整性；替代熵量之判準；序列/多方無信號
```

## 三、未確立（🔴 開放問題 = 本 o 之判決項）
```
🔴 對映表 13/13 格機械可判（物件/謂詞/數字三件齊備）
🔴 替代熵量：帳本熵／陳舊度可否承擔糾纏熵之角色？（須給可證偽判準，含單調性/次可加性檢驗）
🔴 B4 終局性：任何「第二副本」之不可能性是否可一般證明（非僅決定性論證）
🔴 B5 充要陳述：隨機性上限之精確來源（Z₂ 2:1 是否唯一機制）
🔴 序列（多輪）與多方無信號定理
```

## 四、攻擊路線
```
1. 對映表逐格材料化（低成本）
2. 替代熵量構造 ＋ 判準（中成本）
3. B4/B5 之一般定理（中成本）
4. 序列/多方無信號（中成本）
```

## 五、驗證標準
```
✅ 13/13 格機械可判（✅/🟡/🔴）
✅ 替代熵量附可證偽條件；B4/B5 各得二值結論
✅ 零新參數；與 docs/45 §2 B4/B5、docs/43 §二(b) 一致
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

## 推導時序索引（R1，2026-10-02 04:49:48+0800）

> 規則：**禁回溯污染** —— 本索引只記錄時序與指針，唔改寫任何已閉合之結論。

| # | 工件 | 性質 | sha256／結果 |
|:-:|:--|:--|:--|
| 1 | `docs/01_r1_contract.md` | 合約（先於數字；含 A1／A2 pre-freeze 校正） | `074f505320969514` |
| 2 | `scripts/01_r1_gate.py` | 閘（C1–C8） | GATE: 10/10 PASS -> OPEN |
| 3 | `scripts/02_r1_machine.py` | 機器（import 凍結讀出語義） | `f1dee454b56f4c60`；24/26 PASS |
| 4 | `data/02_r1_results.json` | 機器輸出（26 格） | `9089a1d07ba4dba0` |
| 5 | `data/02_r1_Etensor.json` | 62³ 三方張量（Ｅ 之精確分子） | `8b66e68a21fc3fed` |
| 6 | `scripts/03_r1_audit.py` ＋ `data/03_r1_audit.json` | 審計（由零自寫；唔 import 機器） | 5/5 PASS；K 0/7440 mismatch |
| 7 | `scripts/04_r1_report.py` ＋ `docs/02_r1_results.md` | 報告（自動生成） | — |
| 8 | `MANIFEST.json` | 全件 sha256 ＋ 上游 pins ＋ O222 零寫入證明 | — |

### 逐格判決

| tag | 判決 | 核心數字 |
|:--|:--:|:--|
| R0 | ✅ | {"group_order": 120, "inverses": 120, "assoc_violations": 0, "h_injective": true, "half_b": "scripts/03_r1_aud |
| P1a | ✅ | {"orbit_sizes": [12, 20, 30], "type_invariant": true, "permutations": 120, "distinct_lines": 31, "antipodal_pa |
| P1b | ✅ | {"bijective_axes": 62, "of": 62} |
| P1c | 🟡 | {"provenance_law_text": true, "dimensions_available": false, "source": "o210_causal_tensor_algebra/{final_resu |
| P2a | ✅ | {"reproducible_pairs": 3844, "of": 3844, "replay_miss_pattern_matches": true, "lex_pairs": 15, "block_pairs":  |
| P2b | ✅ | {"history_sensitive_settings": 62, "of": 62, "example": ["V00", [-1, 1]]} |
| P2c | ✅ | {"lex": {"pairs": 15, "reads_per_pair": [2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3], "ledger_growth_per_pair |
| P2d | 🔴 | {"C1_values": ["-1", "-2/3", "-1/3", "-4/15", "-1/5", "-2/15", "-1/15", "0", "1/15", "2/15", "1/5", "4/15", "1 |
| P3a | ✅ | {"memo_hit_pairs": 14, "pushes": 85, "read_attempts": 99, "static_rule_ok": true} |
| P3b | ✅ | {"overrides": 2, "example": {"pair": ["V02", "V00"], "stored": 1, "current_state_would_give": -1}} |
| P3c | 🔴 | {"accessible_depth": 1, "redundancy": 1} |
| P4a | ✅ | {"rank_C1": 61, "rank_C2": 62, "rank_C1rev": 61, "rank1_means": "C = u (x) v factorisable"} |
| P4b | 🔴 | {"own_sweep": {"lex": {"E1_all4": "0", "E2_all4": "0", "argmax_E1": null, "argmax_E2": null, "window_pairs": 1 |
| P4c | ✅ | {"balanced_axes": 62, "of": 62, "column_sums": [0], "conditional_marginal_violations": 0, "of_conditional": 38 |
| B4a | ✅ | {"pair_histogram_mismatches": 0, "of_pairs": 3844, "diagonal_pairs": 62, "four_read_joints_exhibited": 60, "of |
| B4b | ✅ | {"commutator_subgroup_order": 120, "perfect": true, "nontrivial_normal_subgroup_orders": [1, 2, 120], "direct_ |
| B4c | ✅ | {"pairs_with_explicit_separable_decomposition": 3844, "of": 3844, "product_components_per_pair": 120, "S_ent": |
| B4d | 🔴 | {"class_counts_k": [1, 2, 4, 16, 26, 34, 48, 52, 54, 57, 58, 58, 58, 59, 59, 59], "entropy_bits_k": [0.0, 1.0, |
| B4e | ✅ | {"E1_single_state_function_read": true, "E2_pair_local_memo": true, "E3_no_second_randomness_source": true, "r |
| B5a | ✅ | {"rows_with_K_s_equals_K_neg": 120, "of_rows": 120, "distinct_behaviours": 60, "class_sizes": [2], "every_clas |
| B5b | ✅ | {"schedule_negation_equivariant": true, "sign_blind_draws_covered_by_the_theorem": 200, "of_draws": 200, "draw |
| B5c | 🔴 | {"common_stabiliser": [0, 21, 30, 36, 43, 75, 99, 106, 108, 117], "common_stabiliser_order": 10, "elements_are |
| S4a | ✅ | {"read_steps_checked": 99, "unconditional_marginal_violations": 0, "remote_setting_independence_violations": 0 |
| S4a-orig | 🔴 | {"history_classes": 644, "unbalanced": 634, "of_classes": 644} |
| S4b | ✅ | {"three_party_tensor_entries": 238328, "tensor_denominator": 120, "marginal_zero_triples": 3844, "of_triples": |
| S4c | ✅ | {"claim": "no channel for multipartite non-classical correlations", "boundary": "within this protocol every mu |
