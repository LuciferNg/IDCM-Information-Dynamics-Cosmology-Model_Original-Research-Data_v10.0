# O225 全鏈盲測審計報告（`o225-blind-audit-v1`）

> **生成**：`scripts/96_audit_report.py`（可重跑；本檔由 `data/92–95` 之 JSON 生成，時間 2026-10-09 13:11）
> **對象**：`scripts/`（全部有編號腳本＋審計引擎 92–96）、`docs/00–57`、`01_problem_record.md`（逐步重建版）
> **唯讀聲明**：本輪審計不修改任何輪次之推導腳本與 docs；重建僅動 `01_problem_record.md`（已備份 `.bak`）。

## 一、方法（四層，互不替代）

| 層 | 內容 | 引擎 | 產物 |
|---|---|---|---|
| **A 重現** | 逐支重跑 `scripts/01–91`（含合約閘／機器／審計），記錄 exit／RESULT／FAIL／Traceback／耗時 | `92_audit_sweep.py` | `data/92_audit_sweep.json`、`logs/92_<script>.out` |
| **B 綁定** | 每個有日誌之腳本判決 `n/m` 必須在某 doc 有記載（宣稱↔證據） | `95_doc_binding.py` | `data/95_doc_binding.json` |
| **C 盲測重算** | 由**定義**自行實作（不 import 本 o 推導腳本、不讀輪次答案），另路重算關鍵量 | `93_audit_blind.py` | `data/93_audit_blind.json` |
| **D 精確 null** | 以**精確組合計數**（非抽樣）評估結構之顯著性 | `93_audit_blind.py` | 同上 || **A2 漂移** | 凍結 `data/*.json` ↔ 當日重跑 ↔ 歷史日誌三方對帳 | `97_drift_audit.py` | `data/97_drift_audit.json` |

## 二、A 段：重現（完成 88 支）

- 完成支數 = **88**；逾時 = 0；含 Traceback = 1
- 逾時清單 = 無
- Traceback 清單 = ['37_closeout_docs']（**誤報**：該支輸出本身含「Traceback 日誌…」清單字樣，非崩潰）
- 含 FAIL 之支 = 39 支；**其 FAIL tag 集與歷史日誌逐支相同者 = 83 支**（見 A2 段）
- 說明：本項目採「被否證之預註冊原樣保留 FAIL」制度，故 FAIL 存在 ≠ 缺陷；判別標準 = **重跑是否復現同一組 FAIL tag**。
  - `05_r1_null_analysis`：FAIL = Q1,Q4
  - `06_r1_axis_sign_structure`：FAIL = S1,S2
  - `11_r2_g1_table`：FAIL = P5pre,P7
  - `12_r2_dyn17`：FAIL = P11,P14
  - `21_r5_tie_global`：FAIL = Q1,Q3
  - `23_r6_contract`：FAIL = C8
  - `24_r6_mechanism`：FAIL = A6
  - `25_r6_geometry`：FAIL = C3
  - `27_r7_contract`：FAIL = C8
  - `28_r7_mechanism2`：FAIL = A3,A5,A4b,A6,A7
  - `29_r7_audit`：FAIL = D3,D4
  - `30_r8_contract`：FAIL = C8
  - `31_r8_group`：FAIL = A1,A3,B1,D1
  - `32_r8_audit`：FAIL = E3a
  - `33_r9_contract`：FAIL = C2,C8,C8c
  - `34_r9_pairing`：FAIL = A2,A5a,A5b,A5c,A5d,B1a,B1b,B2a
  - `35_r9_audit`：FAIL = E2,E6
  - `37_closeout_docs`：FAIL = CO1
  - `39_r10_universal`：FAIL = D3,E1
  - `40_r10_audit`：FAIL = E1
  - `42_r11_machine`：FAIL = T3,U1,V1,V3,V4,W1,W2,W3
  - `45_r12_machine`：FAIL = Y2,Y3,Y5,Q1,Q3,X7-c（量測律）,Z2g（預註冊子猜測）
  - `47_chain_index`：FAIL = C2,C5
  - `49_r13_machine`：FAIL = A3,B1,B2,B3,B4,C2,C3,C4
  - `52_r14_machine`：FAIL = E1,E2,F2,F3,G3,E4,E5,E6
  - `55_r15_machine`：FAIL = G1,G2,G3,E5,E6
  - `58_r16_machine`：FAIL = F4,G3,G4
  - `61_r17_machine`：FAIL = K3b,K1,K2,K4,L2,L3,K6
  - `64_r18_machine`：FAIL = N2,N3,N5,O2,O6-c
  - `67_r19_machine`：FAIL = Q6,P5-c
  - `70_r20_machine`：FAIL = S1,T1,T2
  - `73_r21_machine`：FAIL = U1,U3,U4,U5,U6,U3-a,V1,V2
  - `74_r21_audit`：FAIL = B4
  - `76_r22_machine`：FAIL = W3,W3-c,X2
  - `77_r22_audit`：FAIL = A1
  - `79_r23_machine`：FAIL = Y3,Z2,Z4
  - `84_r24_machine`：FAIL = Q2
  - `87_r25_machine`：FAIL = R1,R2,R3,R4
  - `90_r26_machine`：FAIL = T2,T2-c,T3,T3-c,U1,V4

## 三、A2 段：漂移對帳（凍結 JSON ↔ 當日重跑 ↔ 歷史日誌）

- 分類統計 = `{"match_log": 83, "match_gate": 3, "drift_vs_log": 1, "no_result": 1}`
- **非預期漂移（1 支）**：
  - `47_chain_index`：重跑 [6, 8]；凍結 None
- 已知**時間序敏感**之審計器（非缺陷，屬設計）：
  - `37_closeout_docs`：CO1 要求 MANIFEST 為最後寫入（§28.5 唯讀收口）；掃描期間 MANIFEST 尚未刷新故 FAIL （**MANIFEST 刷新後複驗 = 10/10**）
  - `47_chain_index`：C2 要求每支劇本皆有日誌、C5 要求 MANIFEST 覆蓋且 sha 當前；掃描期間新引擎尚未有日誌／MANIFEST 未刷新故 FAIL （**MANIFEST 刷新後複驗 = 8/8**）
- 無凍結 JSON 可對（僅日誌承載）= 0 支。

## 四、B 段：宣稱 ↔ 證據綁定

- 有日誌之腳本判決數 = **128**；已綁定 = **128**；未綁定 = **0**
- 未綁定清單 = 無 🔴

## 四-b、Q1 段：逐輪文檔聲稱 ↔ 重跑（`98`）

- 分類 = `{"gate_ok": 3, "match": 77, "diverge": 5, "no_claim": 1, "no_script": 2}`（29 輪 / 88 支）
- flagged = 5 支：
  - `R6`／`23_r6_contract`：重跑 [7, 8]；doc 窗內候選 [[6, 6], [8, 8], [9, 10], [11, 12]]
  - `R7`／`27_r7_contract`：重跑 [7, 8]；doc 窗內候選 [[5, 7], [6, 11], [8, 8]]
  - `R8`／`30_r8_contract`：重跑 [7, 8]；doc 窗內候選 [[7, 11], [8, 8]]
  - `R9`／`33_r9_contract`：重跑 [7, 10]；doc 窗內候選 [[0, 0], [1, 1], [2, 62], [4, 6], [6, 8], [7, 8], [7, 9], [8, 10], [10, 23], [11, 23], [12, 23], [34, 35]]
  - `CLOSEOUT-1`／`37_closeout_docs`：重跑 [9, 10]；doc 窗內候選 [[6, 8], [8, 10], [10, 10], [12, 23], [32, 32], [36, 37]]
- **定讞**：上述全部屬「一次性判據」或「時序敏感」型，非推導漂移 —— 4 支 C8「見數前註冊」閘（`23`/`27`/`30`/`33`，見 `docs/49` 行 40 逐字記載）＋ `37` 之 MANIFEST 時序（刷新後複驗 10/10）。

## 四-c、Q3 段：審計缺口補完（`99`）與 register 同步（`100`）

- `99_gap_blind`：**11/11 PASS**（缺口：Λ_a(s) 逐欄貢獻、f_tf/f_ft/f_tt 事件三元配對）
  - [PASS] G0 事件協議重現：自寫事件集 sha256 符 data/34（124 條）
  - [PASS] G1 Λ_a(s) 奇偶律：奇異 (欄,態) = 64 且全屬第 61 欄（R20 T1／T1-c）
  - [PASS] G2 Λ 支撐 = 16 欄，且與凍結 data/70 之 support 逐字相同
  - [PASS] G3 ★ Z10 選擇律（Λ-判據；C2 = Σ_a Λ_a = 0 ∧ max|Λ| ≤ 2）：120 態解集恰 10 態，且 = 凍結 Z10
  - [PASS] G4 f_tf／f_ft／f_tt 獨立重算：與凍結 data/31 之三陣列**逐態全同**（120×3）
  - [PASS] G5 ★ 兩路線互證：{f_tf + f_ft = 0} = {f_tf = −f_ft ≠ 0} = Z10（Λ-判據）—— 同一 10 態
  - [PASS] G6 Σ_{s0} f_tf = Σ f_ft = 0、Σ f_tt = 64（R9 A2／A2c 之值）
  - [PASS] G7 ★ A5ac：S_TF ≡ 0 且 S_FT ≡ 0（逐鍵局部消失；62 鍵全檢）
  - [PASS] G8 ★ A5bc：S_TT 值集 = {−8,0,8}、非零鍵 12、Σ n·S_TT = 64
  - [PASS] G9 ★ A2c 恆等式：Σ n·S_TF = Σ_{s0} f_tf、Σ n·S_FT = Σ f_ft、Σ n·S_TT = Σ f_tt（= 0／0／64）
  - [PASS] G10 ★ R25 R4／R4-c：support 16 欄之（正項數 = 負項數 ∧ 非零）解集 = 24 ⊋ Z10（10）
- `101_register_sync`：**5/5 PASS**（register ↔ `01_problem_record.md` 雙向同步）

## 五、C／D 段：盲測重算與精確 null

- [PASS] **B01** K 表：值集 {±1}、+1/−1 平衡、120/120 列之列和 ≠ 1  
  `值集 = [-1, 1]；+1/−1 = 3720/3720；列和 ≠ 1 之列 = 120/120`
- [PASS] **B02** 協議重現：事件 124、鍵 62（多重度全 2）、事件 sha 符 data/34  
  `事件 = 124；鍵 = 62；多重度全 2 = True；sha 相符 = True`
- [PASS] **B03** tie 表型別欄計數（報值；供 docs 綁定）  
  `型別計數 = {'vertex': 12, 'face': 20, 'edge': 30}`
- [PASS] **B04** dind 雙路線等價：γ≠ε vs R22 (lidx 叉積, lidx KV) 判準，逐 (態,欄)  
  `不符 = 0（樣本 []）`
- [PASS] **B05** S_TT（y-索引，獨立路線）：值集 {−8,0,8}、非零鍵 12、Σ n·S_TT = 64、±8 欄集  
  `值集 = [-8, 0, 8]；非零鍵 = 12；Σ = 64；+8 = [32, 35, 36, 45, 48, 57, 58, 61]；−8 = [37, 38, 55, 56]`
- [PASS] **B06** −8 欄集 [37,38,55,56] = 自身 partner 對合之閉合  
  `partner 對：[(37, 56), (38, 55), (55, 38), (56, 37)]`
- [PASS] **B07** 補集 20：群公理全檢（封閉／單位／逆／結合律 8000 三元組）＋階譜＋唯一對合居中心  
  `封閉 = True；單位 ∈ = True；逆 ∈ = True；結合律 = True；階譜 = {1: 1, 2: 1, 4: 10, 5: 4, 10: 4}；對合 = 1；居中 = True`
- [PASS] **B08** R24 恆等式：T_0 + T_1 = −u_2·A_0（A_0 = (u×x)_0 自算；Z[√5] 逐值）  
  `檢查 80 個 (欄,態)；反例 = 0 []`
- [PASS] **B09** R25 S4：8 非承載欄之 dind 共同值 = 0 ⟺ sgn(u_2) = −1；= 1 ⟺ +1  
  `逐欄 (欄, {dind}, sgn u_2) = [(39, [0], -1), (40, [1], 1), (41, [0], -1), (42, [1], 1), (51, [0], -1), (52, [1], 1), (53, [0], -1), (54, [1], 1)]`
- [PASS] **B10** R26：零鍵項數分佈 = {0,8,40}；非零鍵 8 項全同號  
  `零鍵項數集 = [0, 8, 40]；非零鍵同號 = True`
- [PASS] **B11** 精確 null：G 內階 20 子群之數目 / C(120,20) = 補集為子群之機率  
  `階 20 子群 = 6 個；C(120,20) = 29462227291176635718126；P(隨機 20-子集為子群) ≤ 2.037e-22`
- [PASS] **B12** 精確 null：30 edge 欄中隨機 4-子集為 partner-閉合之機率（vs 實測 −8 欄集）  
  `partner-閉合 4-子集 = 105/27405（P ≈ 0.0038）；實測 −8 欄閉合 = 1`

**C／D 段小結：12/12 PASS**。

重點：
- `B04` 兩條 dind 路線（機器之 `γ≠ε` 與 R22 之 leading-index 判準）在全部 120×62 格**零不符** ⟹ 判準式可換算。
- `B08` R24 恆等式 `T_0 + T_1 = −u_2·A_0` 於 41／42 線全部 tie 態（80 格）**零反例**（`A_0` 由叉積自算）。
- `B11`（精確 null）群 `G` 內**階 20 子群僅 6 個**，而 C(120,20) ≈ 2.95×10²² ⟹ 隨機 20-子集為子群之機率 ≤ 2.0×10⁻²² ⟹ 補集 = `Dic₅` 非巧合。
- `B12`（精確 null）30 個 edge 欄中隨機 4-子集為 partner-閉合者 105/27405（P ≈ 0.38%）⟹ `−8` 欄集之閉合具結構性。

## 六、限制與未覆蓋（誠實界線）

- 本報告之 C 段只覆蓋**可由凍結機器與定義直接重算**之量；凡其定義僅存在於某輪機器碼內者（如 `Λ_a(s)` 之逐欄貢獻、`f_tf/f_ft/f_tt` 之「事件三元」配對），僅有 A 段重現＋B 段綁定，**未作獨立重算** ⟹ 標為待補。
- `data/34_r9_pairing.json` 之 `events_sha` 作為 R9 期協議之凍結錨；B02 已獨立重算該 sha（自寫 stack 協議）並相符。
- 事故層（`01_problem_record.md` 曾清空）另見 `docs/54`；本重建版第二版由 `scripts/94_record_rebuild.py` 生成（§一–§七 逐字保留，§八–§三十六 由重跑判決＋docs 原文摘錄組裝）。
