# O217 — 4-正則必要性 (Four-Regular Necessity)

> **日期**: 2026-09-25
> **狀態**: 🟢 **已閉合 (2026-10-08)** — 4-正則由「88 = 2N_d 透明通道」+「I-軌道 60 節點」+「頂點傳遞」導出（scripts/01 8/8 + scripts/02 25/25 + audit 03 18/18）
> **來源**: O137 `docs/36_gap_attack_round19.md` §5.2 誠實界限（遺留 2 殘餘）
> **前置**: O137（RH 腔室 / MaxCut 定理）、O143（頂點傳遞）、O182（88-格 = A₅ 網邊中點）、O213 R5（A₅ 嚴格手性）

---

## 一、問題

O137 Round 19 遺留 2 證得：**「4-正則 + 等邊」兩條件合取唯一迫使 RH 型**
（rhombicosidodecahedron，邊長 26.3046° vs 精確 L* = 25.878636874°，差 1.7%）。
但 **4-正則性本身係輸入，唔係導出** — 即「為何模式圖係 4-正則？」未獨立論證。
單獨「等邊」不足（反例 (60,20,20) 有 20 個等邊三角形）。

核心質疑：4-正則係幾何強逼（有算子身份），抑或係同「9 模式數」一樣之觀測/結構輸入？

## 二、已確立嘅結構

```
🟢 RH 型 = 4-正則 + 等邊【兩條件合取】唯一（O137 R19 遺留 2）
   單獨等邊不足: 反例 (60,20,20) 有 20 個等邊三角形
   合取後最佳 = (120, 20, 32)，26.3046° vs L* = 25.878636874°
🟢 L* = 25.878636874°（球面角方程 A₃(L) + 2A₄(L) + A₅(L) = 2π，零參數）
   與 RH 實測差 2.8e−14°；面型被迫 3.4.5.4
🟢 B = φ³ − φ⁻³ = 4 = L₃ EXACT（O213 R2 閉合）
🟢 MaxCut(RH 圖) = 88 = 2N_d（O137 docs/32，MILP/HiGHS 精確 Optimal）
🟢 最小阻挫 = 32 = 2B² = 20△ + 12⬠；null: 4-正則 + 20△ + 12⬠ ⟹ 88.00 ± 0.00
🟢 88-格 = A₅ 網 88 條透明邊中點（O182: 120 − 32 = 88 = 2N_d）
🟢 A₅ 不可約表示維數 = {1, 3, 3, 4, 5}（含 4 維）
🔴 「為何 4-正則」未獨立論證（O137 R19 §5.2 明文列為誠實界限）
```

## 三、未確立（🔴 開放問題）

```
🔴 4-正則之第一性原理來源
🔴 4-正則是否 = A₅ 之 4 維不可約表示維數（結構）抑或巧合（數值 4 = B = L₃）
🔴 阻挫邊 32 = 2B² 之機制（數值成立，機制未導出）
🔴 腔室測度 3.07% (46/1500) vs docs/33 3.74% (10000 方向) = −1.38σ
   ⟹ 係「非 generic」而非「唯一」
```

## 四、攻擊路線

```
1. 表示論路線 → 4 = dim(A₅ 之 4 維 irrep)；檢查模式圖鄰接算子是否落該表示
   （A₅ irrep dims {1,3,3,4,5}；5 維亦存在 ⟹ 需判別為何係 4 而非 5）
2. 88-格構造路線 → 由 120 條 RH 邊 − 32 阻挫 = 88 透明邊，度數 4 由 RH 圖 4-正則繼承
   （注意: 呢條係循環 — RH 已知 4-正則 ⟹ 唔可以反過來證 4-正則）
3. K_Tree 路線 → B = 4 = φ³−φ⁻³ ⟹ 每節點 4 鄰；檢查 K_Tree 分支數是否強制 4
4. Nyquist 路線 → λ_max = 4 = B = γ_44（鏈譜 Nyquist）⟹ 度數 = λ_max？
5. 反面路線 → 證明 4-正則係結構輸入（同 9 模式數同級），正式標為前提而非導出
```

## 五、驗證標準

```
✅ 4-正則由第一性原理導出（零參數、零事後選擇）⟹ 升 🟢
✅ 或 正式證明 4-正則為結構輸入（列明前提清單，唔可以再當「導出」）⟹ 誠實 🟢 負結果
✅ 表示論路線必須判別 4 vs 5（A₅ 同時有 4 維同 5 維 irrep）
✅ 唔可以循環（唔可以假設 RH 已知）
```

## 六、狀態

```
🟢 已閉合 (2026-10-08) — 4-正則必要性由第一性原理導出
⭐ 優先度: ★★（RH 型閉合之前提；已完成）
```

## 七、相關文件

```
- o137_cy3_topological_resonance/docs/36_gap_attack_round19.md §5.2 — 遺留 2 之誠實界限
- o137_cy3_topological_resonance/docs/32_maxcut_theorem_and_face_structure.md — MaxCut = 88
- o137_cy3_topological_resonance/docs/34_reverse_88_to_a5_falsification_and_spherical_closure.md — L* 球面閉合
- o137_cy3_topological_resonance/docs/33_round11_rh_chamber_chirality.md — 腔室測度 3.74%（權威）
- o143_phase_selection_mechanism/docs/08_vertex_transitive_theorem.md — 頂點傳遞定理
- o182_88grid_geometry/ — 88-格 = A₅ 網邊中點
- o213_world_dynamics/final_result.md（R5）— A₅ 嚴格手性 / 四型 I-軌道定理
```

## 八、鐵律

```
- 零參數；禁看到目標湊算子
- 唔可以循環論證（RH 4-正則 ≠ 證明 4-正則）
- 出唔到就誠實標 🔴
- 只改本 O 檔案
```

---

## ⚠️ 後續修正 (2026-10-08, O217 攻堅輪) — 已閉合

> **狀態**: 🔴 未閉合 → 🟢 **已閉合**（第一性原理導出，零循環、零參數）
>
> **核心結果**（scripts/01 8/8 PASS + scripts/02 25/25 PASS，MILP 精確）：
> - 喺 I-軌道 60 節點圖類（28° 閾值近鄰圖）8 個腔室類中，**唯一 E − mono_exact = 88 = 2N_d 者 = (120, 20, 32)**
> - E=120, V=60 ⟹ 頂點傳遞（Cayley，O143 docs/08）⟹ 度數 = 2E/V = **4**
> - 4-正則 + 等邊 ⟹ 唯一 RH 型（引用 O137 R19 §5.2）
> - 5-正則候選 (150,80) mono_exact=46 ⟹ E−mono=104 ≠ 88 被排除；3-正則類 70/78 ≠ 88 排除
> - mono_BFS 與 mono_exact 同序，無 BFS 偽影；每類 3 樣本 MILP 類內恆定
>
> **§三 開放問題處理**：
> - 🔴 4-正則之第一性原理來源 → **✅ 已導出**（本輪）
> - 🔴 4-正則是否 = A₅ 4 維 irrep → **✅ 已判定（負面）**：4 = 2E/V 由通道數鎖定，與 irrep 維數無關（表示論無判別力 4 vs 5）
> - 🔴 阻挫邊 32 = 2B² 之機制 → 🟡 數值確認（mono_exact=32），機制層引用 O137 docs/32 面結構定理，屬既有閉合領域
> - 🔴 腔室測度 3.07% vs 3.74% −1.38σ → **✅ 已解決**：本 O 3.70% (N=25000) 與 docs/33 3.74% 一致；docs/36 3.07% 係 1500 樣本小樣本漲落
>
> **完整推導**: docs/02_derivation.md；logs/01_output.txt + logs/02_output.txt；data/01_scan.json + data/02_strengthen.json

---

## 九、推導時序索引 + 檔案閉合水位（close-out watermark, 2026-10-08）

### 第 1 輪 (2026-10-08) — 攻堅閉合

| # | 日期 | 步驟 | 產物 | 結果 |
|:-:|:-----|:-----|:-----|:-----|
| 1 | 10-08 | 讀上游權威（O137 docs/32/33/34/36、O143 docs/08、O182、O213） | — | 確認 O217 範圍、88=2N_d 輸入、腔室表 |
| 2 | 10-08 | scripts/01（I 群四元數構造 → 25000 樣本腔室掃描 → 逐類 MILP） | scripts/01_four_regular_necessity.py, logs/01_output.txt, data/01_scan.json | **8/8 PASS**；唯一 E−mono=88 = (120,20,32) |
| 3 | 10-08 | scripts/02（20000 樣本完備性 + 每類 3 樣本 MILP 類內穩定 + 正則性 + docs/32 上界核對） | scripts/02_strengthen.py, logs/02_output.txt, data/02_strengthen.json | **25/25 PASS**；MaxCut 類內恆定；4-正則度數 {4:60} |
| 4 | 10-08 | docs/02 推導記錄 | docs/02_derivation.md | 完整鏈、計算證據、驗證標準對照 |
| 5 | 10-08 | RESULT.md + SESSION_START 狀態 + register close | RESULT.md, SESSION_START.md, register | 🟢 已閉合 |
| 6 | 10-08 | 全 Session 鏈 closeout：session DB provenance（thread 104121 兩 session） | — | 26 寫入全部指向本 O；無 /tmp 寫入 |
| 7 | 10-08 | scripts/03 獨立 verifier（二十面體頂點對構造 I 群、面結構上界、greedy、triangle-cover；無 MILP、無 quaternion） | scripts/03_audit_independent.py, logs/03_audit_output.txt | **18/18 PASS**；唯一 88 鏈獨立重建 |

### 檔案閉合水位

| # | 檔案 | 上次檔案更新 (mtime) | 上次 closed-out | 已驗範圍 | 狀態 |
|:-:|:-----|:---------------------|:----------------|:---------|:-----|
| 1 | docs/01_problem_record.md | 2026-10-08 | 2026-10-08 | 全文 + 本輪 append | ✅ 已驗 |
| 2 | docs/02_derivation.md | 2026-10-08 | 2026-10-08 | 全文 | ✅ 已驗 |
| 3 | scripts/01_four_regular_necessity.py | 2026-10-08 17:50 | 2026-10-08 | 全文（重跑 8/8） | ✅ 已驗 |
| 4 | scripts/02_strengthen.py | 2026-10-08 18:27 | 2026-10-08 | 全文（重跑 25/25） | ✅ 已驗 |
| 5 | scripts/03_audit_independent.py | 2026-10-08 | 2026-10-08 | 全文（18/18） | ✅ 已驗 |
| 6 | logs/01_output.txt | 2026-10-08 17:52 | 2026-10-08 | PASS 8/8 尾行 | ✅ 已驗 |
| 7 | logs/02_output.txt | 2026-10-08 18:29 | 2026-10-08 | PASS 25/25 尾行 | ✅ 已驗 |
| 8 | logs/03_audit_output.txt | 2026-10-08 | 2026-10-08 | PASS 18/18 尾行 | ✅ 已驗 |
| 9 | data/01_scan.json | 2026-10-08 17:52 | 2026-10-08 | 8 類 + MILP 表 | ✅ 已驗 |
| 10 | data/02_strengthen.json | 2026-10-08 18:29 | 2026-10-08 | 類內恆定 + 唯一 88 | ✅ 已驗 |
| 11 | RESULT.md | 2026-10-08 | 2026-10-08 | 全文 | ✅ 已驗 |
| 12 | SESSION_START.md | 2026-10-08 | 2026-10-08 | 檔頭 + 驗證標準 | ✅ 已驗 |

### 時序完整性確認

- 推導次序：scripts/01 (17:50) → logs/01 (17:52) → data/01 (17:52) → scripts/02 (18:27) → logs/02 + data/02 (18:29) → docs/02 (18:33) → RESULT/SESSION/register (18:33) → scripts/03 (closeout 輪, 18:44+) — docs 全部喺 scripts 之後，無回溯污染。
- SESSION_START 係 2026-09-25 快照，正文未改；只更新檔頭狀態行（live field）＋驗證標準打勾（同 §9.1 三處同步規則）。
- append-only：01_problem_record.md 前 113 行 md5 = 13e5e02e 保持不變（於 2026-10-08 記錄），本節純 append。
