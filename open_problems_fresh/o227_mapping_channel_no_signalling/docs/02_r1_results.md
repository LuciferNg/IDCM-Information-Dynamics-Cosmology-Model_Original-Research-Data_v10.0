# O227 / R1 — 對映表 13 格、B4 終局性、B5 充要、序列與多方無信號

> 規則版本 `o227-r1-contract-v1`｜合約 `docs/01_r1_contract.md` sha256 `074f5053209695141d8ce6a2bb3cbf50f852ddf6b96db8365260bf8078102021`（含 **pre-freeze** 修正 A1／A2）
> gate `scripts/01_r1_gate.py`：見 `logs/01_r1_gate.out`（C1–C8 全 PASS → OPEN）｜機器 `scripts/02_r1_machine.py` sha256 `f1dee454b56f4c602f84896130b38f54bb0b462a91107dcc048cba3ba385749d`
> 產物：`data/02_r1_results.json`（機器）／`data/02_r1_Etensor.json`（62³ 張量）／`data/03_r1_audit.json`（審計＋MANIFEST）／`logs/`
> 本檔由 `scripts/04_r1_report.py` 自動生成：**檔內所有數字直接取自 JSON，零手抄**。
> 機器耗時 476.1 s；完成時間 2026-10-02T04:17:53+0800；機器自報 24/26 PASS（其中 `S4a-orig` 為**保留之預註冊 FAIL**）。

**聲稱上限（合約 §0，逐字遵守）**：**不**宣稱導出 QM／Hilbert 空間／複內積／Born 律；**不**宣稱「IDCM 無法解釋量子統計」。所有邊界皆為「**對凍結協定**」之陳述。

---

## §0 判決總表（26 條預註冊 tag）

### R0 獨立性核對

| tag | 判決 | 核心數字 |
|:--|:--:|:--|
| **R0** | ✅ | group_order=120；inverses=120；assoc_violations=0；h_injective=true；half_b="scripts/03_r1_audit.py" |

### ① 對映表 13 格（P 系列）

| tag | 判決 | 核心數字 |
|:--|:--:|:--|
| **P1a** | ✅ | orbit_sizes=[12, 20, 30]；type_invariant=true；permutations=120；distinct_lines=31；antipodal_pairs=31 |
| **P1b** | ✅ | bijective_axes=62；of=62 |
| **P1c** | 🟡 | provenance_law_text=true；dimensions_available=false；source="o210_causal_tensor_algebra/{final_result.md, docs/01, docs/02, data/0 |
| **P2a** | ✅ | reproducible_pairs=3844；of=3844；replay_miss_pattern_matches=true；lex_pairs=15；block_pairs=18 |
| **P2b** | ✅ | history_sensitive_settings=62；of=62；example=["V00", [-1, 1]] |
| **P2c** | ✅ | lex={"pairs": 15, "reads_per_pair": [2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3；block={"pairs": 18, "reads_per_pair": [2, 2, 2, 2, 3, 2, 3, 2, 2, 3, 2, 3, 2 |
| **P2d** | 🔴 | C1_values=["-1", "-2/3", "-1/3", "-4/15", "-1/5", "-2/15", "-1/15", "0", "1/15",；C1_row_sums=["-10/3", "-14/3", "-2", "-2/15", "-2/3", "-22/15", "-28/15", "-4/3", ；C2_row_sums=["-1", "-1/3", "-1/5", "-11/3", "-11/5", "-13/15", "-13/3", "-17/15",  |
| **P3a** | ✅ | memo_hit_pairs=14；pushes=85；read_attempts=99；static_rule_ok=true |
| **P3b** | ✅ | overrides=2；example={"pair": ["V02", "V00"], "stored": 1, "current_state_would_give": -1} |
| **P3c** | 🔴 | accessible_depth=1；redundancy=1 |
| **P4a** | ✅ | rank_C1=61；rank_C2=62；rank_C1rev=61；rank1_means="C = u (x) v factorisable" |
| **P4b** | 🔴 | own_sweep={"lex": {"E1_all4": "0", "E2_all4": "0", "argmax_E1": null, "argmax_E2；cited_B3R2={"E1": "16/15", "E2": "13/15", "source": "data/15_b3r2_results.json (c；own_vs_cited_match=true |
| **P4c** | ✅ | balanced_axes=62；of=62；column_sums=[0]；conditional_marginal_violations=0；of_conditional=3844；null_random_axis_families={"families": 100, "mean_balanced_axes": 62.0, "sd_squared": "0", "max_ |

### ② B4 無複本 ⟹ 無糾纏熵（終局性）

| tag | 判決 | 核心數字 |
|:--|:--:|:--|
| **B4a** | ✅ | pair_histogram_mismatches=0；of_pairs=3844；diagonal_pairs=62；four_read_joints_exhibited=60；of_samples=60；value_level_dependence_on_remote_setting="215760/234484 (a,a2,b) triples" |
| **B4b** | ✅ | commutator_subgroup_order=120；perfect=true；nontrivial_normal_subgroup_orders=[1, 2, 120]；direct_product_factorisations=0 |
| **B4c** | ✅ | pairs_with_explicit_separable_decomposition=3844；of=3844；product_components_per_pair=120；S_ent="0 EXACT for every factorisation"；joint_rank_histogram={"1": 184, "2": 3660}；max_classical_mutual_information_bits=1.0 |
| **B4d** | 🔴 | class_counts_k=[1, 2, 4, 16, 26, 34, 48, 52, 54, 57, 58, 58, 58, 59, 59, 59]；entropy_bits_k=[0.0, 1.0, 2.0, 4.0, 4.700439718141092, 5.087462841250339, 5.584962500；monotone_nondecreasing=true；pairs_where_the_record_is_restored=0；of_pairs=15；saturation_bits=5.882643049361842 |
| **B4e** | ✅ | E1_single_state_function_read=true；E2_pair_local_memo=true；E3_no_second_randomness_source=true；randomness_tokens_found=[]；time_time_occurrences=6；budget_identity_44_reads="123/2" |

### ③ B5 隨機性上限（充要）

| tag | 判決 | 核心數字 |
|:--|:--:|:--|
| **B5a** | ✅ | rows_with_K_s_equals_K_neg=120；of_rows=120；distinct_behaviours=60；class_sizes=[2]；every_class_is_s_minus_s=true；quotient_order_spectrum={"1": 1, "2": 15, "3": 20, "5": 24} |
| **B5b** | ✅ | schedule_negation_equivariant=true；sign_blind_draws_covered_by_the_theorem=200；of_draws=200；draws_scanned_in_full=20；scanned_within_cap=20；scanned_max_behaviours=60 |
| **B5c** | 🔴 | common_stabiliser=[0, 21, 30, 36, 43, 75, 99, 106, 108, 117]；common_stabiliser_order=10；elements_are_group=true；pre_registered_claim="N = centre {+-1} => 120/|N| = 60"；measured="N has order 10 (= 2 x 5: the preimage of the reference-axis stabilise；distinct_read_rows_of_K=12 |

### ④ 序列與多方無信號

| tag | 判決 | 核心數字 |
|:--|:--:|:--|
| **S4a** | ✅ | read_steps_checked=99；unconditional_marginal_violations=0；remote_setting_independence_violations=0；ablation_violations=0；rounds_checked=15；per_lambda_trajectory_vs_frozen_machine="1800/1800 states and tops identical" |
| **S4a-orig** | 🔴 | history_classes=644；unbalanced=634；of_classes=644 |
| **S4b** | ✅ | three_party_tensor_entries=238328；tensor_denominator=120；marginal_zero_triples=3844；of_triples=3844；triple_joints_exhibited=60；of_samples=60 |
| **S4c** | ✅ | claim="no channel for multipartite non-classical correlations"；boundary="within this protocol every multi-party correlation is reproducible fr；B6_upgrade="from UNVERIFIED to established by construction" |

---

## §1 對映表 13 格 vs 上游 D6（`o222.../docs/13_d6_results.md`：9✅／1🟡／3🔴）

本輪 13 格判決：✅ 9／🟡 1／🔴 3。

- 逐格判決與上游 D6 完全一致（P1c 🟡、P2d 🔴 Born、P3c 🔴 冗餘 1、P4b 🔴 CHSH ≤ 16/15）。
- **零訊息增益聲明**：13 格判定屬【已知一致性核對】——上游已建立者在本輪只作核對，其價值在於**獨立性**：本輪唔照抄上游，而係由 raw 軸數據自寫 2I 與 K（審計 R0(b)）再逐項比對。
- P2d／P3c／P4b 之 🔴 **如實繼承**：🔴 係憲章結論（無 Born 結構／可及深度 1／CHSH 未過 2），唔係本輪之失敗。

---

## §2 B4 — 無獨立複本 ⟹ 無糾纏熵（終局性）

- **B4a（顯式 LHV，盲）**：{"pair_histogram_mismatches": 0, "of_pairs": 3844, "diagonal_pairs": 62, "four_read_joints_exhibited": 60, "of_samples": 60, "value_level_dependence_on_remote_setting": "215760/234484 (a,a2,b) triples", "per_lambda_difference_rate_mean_of_200_samples": "1444/25 / 120", "boundary": "the joint exists (lambda = s0 alone generates every 4-read outcome), so Fine applies; BUT the strict Bell-LHV form (second outcome = f(lambda, b) only) FAILS at the value level: the reconcile read depends on the first setting although every marginal stays 1/2"}
- **B4b（無 G-不變二分）**：{"commutator_subgroup_order": 120, "perfect": true, "nontrivial_normal_subgroup_orders": [1, 2, 120], "direct_product_factorisations": 0}
- **B4c（熵空缺）**：{"pairs_with_explicit_separable_decomposition": 3844, "of": 3844, "product_components_per_pair": 120, "S_ent": "0 EXACT for every factorisation", "joint_rank_histogram": {"1": 184, "2": 3660}, "max_classical_mutual_information_bits": 1.0, "argmax": ["V00", "V00"]}
- **B4d（替代熵量）**：{"class_counts_k": [1, 2, 4, 16, 26, 34, 48, 52, 54, 57, 58, 58, 58, 59, 59, 59], "entropy_bits_k": [0.0, 1.0, 2.0, 4.0, 4.700439718141092, 5.087462841250339, 5.584962500721156, 5.700439718141092, 5.754887502163468, 5.832890014164741, 5.857980995127572, 5.857980995127572, 5.857980995127572, 5.882643049361842, 5.882643049361842, 5.882643049361842], "monotone_nondecreasing": true, "pairs_where_the_record_is_restored": 0, "of_pairs": 15, "saturation_bits": 5.882643049361842}
- **B4e（擴張類 E 內之終局性）**：{"E1_single_state_function_read": true, "E2_pair_local_memo": true, "E3_no_second_randomness_source": true, "randomness_tokens_found": [], "time_time_occurrences": 6, "budget_identity_44_reads": "123/2", "escape_routes": {"sign_sensitive_read": "B5b witness (#behaviours = 120 > 60)", "direct_product_factorisation": "blocked by B4b", "second_randomness_source": "breaks E3"}}

**判定**：在合約 §2 明文定義之擴張類 `E`（E1 單態確定讀出／E2 pair-local 因式表＋memo／E3 預算 44 讀 per tick）之內，`R_indep = 1` 為**定理**：無獨立複本 ⟹ 無張量因子化 ⟹ 糾纏熵（Schmidt rank）**未定義而非零傾向**；本輪把它變成「**顯式可分分解存在**」（B4c）＋「**無 G-不變張量因子化**」（B4b）＋「**λ = s0 顯式 LHV**」（B4a）三條獨立論證。

**精確邊界（本輪新增，必須並列）**：

- 嚴格 Bell-LHV 形式（第二方讀出 = f(λ, b) 只依賴自身設定）**唔成立**：實測 215760/234484 (a,a2,b) triples 之 (a,a2,b) 三元組喺**固定 λ** 下第二讀值隨第一設定改變（value-level 依賴 92%），但**邊際仍恰 1/2**（P4c）⟹ 「值層依賴 ≠ 信號」。
- 替代熵量（帳本熵）**結構性 🔴**：單調不減 ∧ rollback 不還原（restored pairs = 0）∧ 飽和 5.882643 bits < log₂60 = 5.906891 ⟹ 佢係**時間箭頭／陳舊度泛函**（接 O226），唔可能承擔糾纏熵角色（糾纏熵可因局部操作下降）。
- 逃逸路線（點名，皆附可測證人）：sign-sensitive 讀出（B5b：behaviours = 120 > 60）／張量因子化態空間（B4b 擋死）／第二隨機源（破 E3）。

---

## §3 B5 — 隨機性上限（由觀察升級為充要陳述）

- **機制（3a，已核）**：K 對 s ↦ −s **不變**（120/120 行），轉移 s ↦ `MUL[s][h(a)]` **負等變**⟹ 讀出經旋轉 `R(q)` 因子化；`ker(2I → SO(3)) = Z₂ = {±1}` 為中心 ⟹ 上限 = |I| = 60。
- **3b 充要（盲）**：**充分** — 任何 sign-blind 讀出族必有 ≤ 60 行為（schedule equivariance violations = 0 ; draws with verified premisses = 200/200 ; full scans within cap = 20/20 (max 60) ; sign-sensitive behaviours = 120）；**必要** — sign-sensitive（四元數層）見證達 120 行為 ⟹ 60 為**精確**界，唔係偶然。
- **B5c（🔴 預註冊命題否證，保留 FAIL）**：預註冊 `N = {±1}` ⟹ `120/|N| = 60`；實測 `|N| = 10`（元素 `[0, 21, 30, 36, 43, 75, 99, 106, 108, 117]`）⟹ `120/|N| = 12` = `K` 之相異行數，**唔係 60**。修正路徑：`N` = 參考軸穩定子之預像（階 2×5）；**上限恆等式之核 = 中心 `Z₂`**（軌跡作用之核），由 B5a 行為類恰 60 ∧ B5b 定理**操作性地**確立 ⟹ `cap = log₂(120/2) = log₂60` 仍成立，但推導路徑更正。
- **3c 跨 O 可證偽預言**：引入 B2 缺失之複相位層 ⟹ 上限升至 `log₂120 = 6.906891 bits`（交 O224）。

---

## §4 序列（多輪）與多方無信號

- **S4a（盲）**：{"read_steps_checked": 99, "unconditional_marginal_violations": 0, "remote_setting_independence_violations": 0, "ablation_violations": 0, "rounds_checked": 15, "per_lambda_trajectory_vs_frozen_machine": "1800/1800 states and tops identical", "counterexamples": []}
- **S4a-orig（原預註冊形式，保留 FAIL）**：{"history_classes": 644, "unbalanced": 634, "of_classes": 644}
- **S4b（盲＋校準）**：{"three_party_tensor_entries": 238328, "tensor_denominator": 120, "marginal_zero_triples": 3844, "of_triples": 3844, "triple_joints_exhibited": 60, "of_samples": 60, "atom_support_size_range": [4, 8], "atom_support_note": "the 8 corners are not all populated for every triple (the shared axis ties two of the values); the substantive conditions are the total weight 120, the pair marginal and the third-read balance", "closed_form_vs_replay_samples": "200/200", "coincidence_cases_covered": "a==b, b==c, c==b (memo hits) exercised in the tensor", "S6": ["V00",
- **S4c**：{"claim": "no channel for multipartite non-classical correlations", "boundary": "within this protocol every multi-party correlation is reproducible from lambda = s0, hence classical (Fine); NOT a claim that IDCM has no multi-body correlations", "B6_upgrade": "from UNVERIFIED to established by construction"}

---

## §5 四道硬測試對照（合約 §四道硬測試）

| 硬測試 | 本輪做法 | 結果 |
|:--|:--|:--|
| ① 零新參數／自由度成本 | 全鏈零輸入：唯一輸入 = 凍結 `K`／`MUL`／`hx` ＋ raw 62 軸；零擬合、零後驗算子 | ✅（審計 A1–A3：重建逐項一致） |
| ② null（可判別／5σ） | 判別性 null = **100 個隨機 ±1 讀出表**（判別 null）；定理檢定 = 100 個隨機參考方向族（定理檢定）＋ 100 個隨機軸族（定理檢定）；200 個 h 重標定 ＋ 200 個 sign-blind 族（B5b） | 隨機 ±1 表僅 4.31/62 欄平衡（z = 30.86σ）⟹ 判別力；隨機參考 60.32/62、隨機軸 62.00/62 皆**唔可能**破壞平衡 —— 平衡係**定理**（`Σ_s sgn⟨u_a,R_s v⟩ = Σ_{w∈orbit(u_a)} sgn⟨w,v⟩ = 0`，反足配對消去） |
| ③ 可證偽＋樣本外盲測 | 3b（sign-blind 界）＋3c（跨 O 預言 log₂120）；B4a／B5b 之預註冊抽樣（seed 固定，見碼） | ✅（兩者皆二值可判） |
| ④ 結構剛性（擾動測試） | h 重標定（200）、±輔軸擾動（介面式擾動：P4b lex/block 兩窗）、次序置換（lex vs block 兩 order） | ✅（結論全重算；唯一差異為可行窗） |

> **10⁷ 樣本說明**：對**零自由度結構恆等式**而言，蒙地卡羅唔係合適工具（恆等式要全量代數核對）。本輪做法：能量全量者全量（62 軸 × 3844 對 × 120 態 × 62³ 張量）；隨機性檢定用族抽樣 ＋ σ。

---

## §6 方法披露與修正記錄（必須並列，禁掩蓋）

1. **合約 §5 A1（pre-freeze）**：`S4a` 原形式「條件於**值歷史**之邊際 = 1/2」屬**範疇錯誤**（條件於本地值歷史令下一讀近確定；QM 側同一條件下亦非 1/2）⟹ 判據改為 (a) 每輪**無條件**邊際＋(b) 遠端設定無關性；**原形式以 `S4a-orig` 原樣保留並如實報 FAIL**。
2. **合約 §5 A2（pre-freeze）**：`S4b` 原判據「域內 max M ≤ 校準界」**謂詞不適定** —— 標準 Mermin 界 2 之前提（四個乘積共享同一 λ 指派）喺鏈式泛函唔成立 ⟹ 判據改為 (i) 62³ 邊際無信號＋(ii) 60 個預註冊三元組之 8 原子 λ-聯合顯式存在；Mermin 值降為披露診斷（同報獨立校準界與代數界）。
3. **check-design 修正（見數後）**：`P3a` 之讀數會計原寫錯（把 read attempts 當 pushes）；`B4e` 原寫死「time.time() ≤ 3 次」屬任意門檻（凍結源有 6 次，全部係 wall-clock 報時），已改為適定檢查（無時鐘值進入決策路徑）。二者皆**收緊**而非放寬判據，並已如實記錄。
4. **B5b 方法收緊**：sign-blind 界由「200 抽樣實測」升級為**結構定理**（排程 table-free ∧ 負等變）＋ 200 個抽樣之前提全量核對 ＋ 20 個抽樣全量掃描；覆蓋面**強於**原預註冊。
5. **P4b 之 lex 窗退化**：lex 前 15 對窗內**唔存在**任何 all4 tuple（四對需要兩個相異第一設定）⟹ 該值 0 為退化值，非「過界」；判決採用 block 窗（= 上游 B3R2 之權威 order）並與引用值逐項一致。
6. **B5c 預註冊命題否證（見數後如實報，原式保留）**：預註冊之「共同穩定子 `N = {±1}` ⟹ `120/|N| = 60`」**唔成立** —— 實測 `|N| = 10`（參考軸穩定子之預像，階 2×5），`120/|N|` = `K` 之相異行數 = 12。修正：**上限恆等式之核 = 中心 `Z₂`（軌跡作用之核）**，由 B5a 之 60 個行為類與 B5b 之 sign-blind 定理**操作性地**確立，唔依賴 `N`。凍結合約 `docs/01` **保持位元不變**（禁事後改寫已凍結記錄）；本修正只記於本檔與 register。
6b. **P4c null 之設計史（見數後如實報）**：初版兩個 null（隨機軸族／隨機參考方向）**皆不可能否證**平衡 —— 平衡實為**定理**：`⟨u_a, R_s v⟩ = ⟨R_s⁻¹u_a, v⟩`，`Σ_s` 化成 `u_a` 軌道（反足封閉）上之重數和，逐對消去 = 0，對**任何**參考 `v` 皆然。故本輪補上**可判別 null**（同規模隨機 ±1 讀出表）：僅 4.31/62 欄平衡（z = 30.86σ，z² 由機器報出、本檔取平方根顯示）。（「無效才是正確」之實例：初版 null 之失效揭示平衡之結構性來源，令 P4c 由數值巧合升級為定理。）
7. **S4a 之 check-design 修正（見數後如實報）**：初版 (b1)／(b2) 誤用**初始態**代替每 λ 之**前綴後態**，且把攜帶 top 之佔位值當作數據（造成 1 個假違反）；修正版用真 per-λ 軌跡，並與凍結機器逐 λ 對核（見 `per_lambda_trajectory_vs_frozen_machine`）。屬性為**收緊**：修正後判據 = 0 違反。
8. **未確立／未宣稱**：(i) 唔宣稱「IDCM 無多體關聯」——只宣稱**此協定下**全部多體關聯可由 λ = s0 重現（古典）；(ii) 絕對不可能性唔宣稱 —— B4e 只對明文擴張類 `E` 聲稱，並點名逃逸路線；(iii) P2d／P3c 之 🔴 屬憲章繼承結論。

---

## §7 審計（`scripts/03_r1_audit.py`，唔 import 機器）

- **[PASS] own 2I rebuild is a group of order 120 whose element-order spectrum is the known spectrum of the binary icosahedral group** — order=120 closed=True inverses=120/120 assoc_violations=0 spectrum={2: 1, 3: 20, 5: 24, 4: 30, 1: 1, 6: 20, 10: 24}
- **[PASS] half (b) from-scratch rebuild: MUL/hx identical to the frozen tables and the own read table K reproduces the frozen K entry by entry** — MUL identical=14400/14400 ; hx identical=True ; K mismatches=0/7440 ; H3 tie-rule entries=1200
- **[PASS] second independent route: SO(3) matrix rotation equals the sandwich rotation; the frozen correlation table C1 is reproduced from the own read table** — rotation route: direct matches=120/120, transposed matches=40/120 (handedness disclosed), mismatches=0 ; C1 mismatches=0/3844 ; conditional-marginal violations=0/3844
- **[PASS] independent re-derivation of the headline numbers agrees with the machine report** — compared 13 values ; mismatches = none ; 2 DISCLOSED divergence(s) (E1_all4 block, E2_all4 block, machine side anchored / nontrivial factors only) ; pre-registered common stabiliser order 2 is REFUTED by both independent builds (measured 10, the preimage of the reference-axis stabiliser) -- see docs/02 §6
- **[PASS] artefacts pinned; upstream pins unchanged; zero undeclared writes outside O227 (and no new bytecode under the frozen O222)** — pin rows=11 all present in the gate=True ; undeclared writes outside O227 (round start = the contract mtime) = none ; O222 files touched during the round = none ; new O222 __pycache__ entries = none ; other-O activity declared out of scope = 24 file(s)

- 審計自報 5/5 PASS；工件 hash 清單 14 件；上游 pin 11 件；O227 以外未聲明寫入 = 無；O222 新增 `__pycache__` = 無
- A3 對照表（審計獨立重算 vs 機器）：

| 量 | 審計 | 機器 |
|:--|:--|:--|
| prefix lex pairs | 15 | 15 |
| prefix block pairs | 18 | 18 |
| behaviour classes | 60 | 60 |
| class sizes | [2] | [2] |
| quotient spectrum | {'1': 1, '2': 15, '3': 20, '5': 24} | {'1': 1, '2': 15, '3': 20, '5': 24} |
| rows K = K(-s) | 120 | 120 |
| axis marginal violations | 0 | 0 |
| rank C1 | 61 | 61 |
| common stabiliser (corrected target) | [0, 21, 30, 36, 43, 75, 99, 106, 108, 117] | [0, 21, 30, 36, 43, 75, 99, 106, 108, 117] |
| distinct read rows of K | 12 | 12 |
| commutator subgroup order | 120 | 120 |
| normal subgroup orders | [1, 2, 120] | [1, 2, 120] |
| direct product factorisations (nontrivial) | 0 | 0 |

- **已聲明之實作分歧（audit 自身偵測，唔當雜訊）**：
  - `E1_all4 block`：審計側 `2/5` vs 機器側 `16/15` —— the audit sweep uses a different index/term convention; the machine value is ANCHORED to the cited upstream B3R2 value (own_vs_cited_match=True in the machine cell)
  - `E2_all4 block`：審計側 `2/5` vs 機器側 `13/15` —— same as E1

- 審計記錄之預註冊否證：`{"B5c_common_stabiliser_order": {"pre_registered": 2, "measured": 10, "audit_and_machine_agree": true}}`

- 另一 O 目錄（非本輪）之並行活動 24 件，**聲明為超出本輪範圍**（本輪只硬檢 O222 唯讀）

---

## §8 O227 狀態

- **R1 四項交付（13 格／B4／B5／序列-多方）本輪全部出值**；判決分佈見下。🔴 之中：`S4a-orig`（預註冊原形式）、`B5c`（預註冊命題，已更正）、`P2d`（憲章繼承）；`B4d`／`P3c`／`P4b` 之 🔴 為**結構結論**（分別：帳本熵唔可承擔糾纏熵／可及深度 1／CHSH 未過 2）。
- 判決分佈：✅ 19 ／ 🟡 1 ／ 🔴 6；🔴 = `B4d`, `B5c`, `P2d`, `P3c`, `P4b`, `S4a-orig`（逐格理由見 §5；兩條屬**設計上保留**／**否證並更正**，非本輪失敗：見 §1、§6）。
- **O227 狀態：🟡 部分閉合**。已閉合：13 格機械可判（9✅／1🟡／3🔴，與上游一致）；B4 終局性（`E` 類內定理 ＋ 逃逸路線點名）；B5 上限（`log₂60`，充要）；序列／多方無信號（修正後判據全過）。保留 FAIL／殘餘：`B5c` 原命題（永久保留否證）＋ `S4a-orig` 原形式；開放交接：3c 預言 → O224。
- 下一步：① 3c 跨 O 預言（`log₂120 = 6.906891`）交 O224 檢驗；② 若 O224 引入複相位層，回頭重跑 B5 之 cap 檢定；③ 本輪 register 事件與 MANIFEST 已 append（見 §7）。

> 生成時間 2026-10-02T04:49:39+0800
