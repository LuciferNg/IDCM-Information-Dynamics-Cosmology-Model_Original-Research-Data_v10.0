# O224 — amplitude／複相位層之構造（Complex-Phase / Amplitude Layer）

> **★ Round 1 判決（並行 session，2026-09-30 → 10-01）**: `a=RED b=RED c=RED d=GREEN e=GREEN`｜contract `o224-r1-contract-v1`（P1–P16 預註冊）｜audit **12/12 PASS**｜產物：`docs/01_phase_layer_verdict.md`、`docs/02_findings_and_deltas.md`、`docs/03_escape_map.md`、`docs/04_residuals.md`、`scripts/00_contract.py`–`08_residuals.py`、`data/00`–`08`
> （machine block 之 state 已由 `verdict_issued (round 1 complete)` 正規化為 `partial` 以符合 register 列舉；原判決字串完整保留於本行與 register note。）

<!-- registry
pid:     O224
title:   amplitude／複相位層之構造（Complex-Phase / Amplitude Layer）
state:   partial
verdict: partial
flags:   contract=o224-r1-contract-v1 (P1-P16 pre-registered); audit 12/12 PASS; verdict round-1 by parallel session
owner:   O224
created: 2026-09-30
updated: 2026-09-30
prereq:  O222
dir:     open_problems_fresh/o224_amplitude_complex_phase_layer/
source:  O222 完整性 closeout 分流（調律者指令 2026-09-30：「開新o，把剩下開題分開幾個o解決，保留o222開放作為最終裁決及整合」）
-->

# O224 — amplitude／複相位層之構造（Complex-Phase / Amplitude Layer）

> **狀態**: 📄 **已註冊 — 目標已定（依 O222 no-go 邊界憲章 `docs/45`）**
> **建立/更新**: 2026-09-30｜**位置**: `open_problems_fresh/o224_amplitude_complex_phase_layer/`
> **前置**: **O222 保留開放作最終裁決及整合**；本 o 承接憲章判決項：**B1 · CHSH 封頂、B2 · 無連續複相位、B6 · 無多體關聯層**
> **目標權威來源**: `open_problems_fresh/o222_qm_evaluation_semantics/docs/45_no_go_boundary_charter.md`

---

## 一、問題陳述
**判定 B1／B2／B6 之終局性**：IDCM 現行協定（2I 左正則 120 態、±1 讀出 K、pair-local 因式表 ＋ memo、資源窗 all4）之關聯已證為**古典且構造性 Bell-local**。本 o 要裁決：可否在 IDCM 結構內（**唔加外部物件、零新參數**）長出 ① **複相位層**（越古典界至 Tsirelson 2√2 之前提）② **二分張量層**（`ℋ_A ⊗ ℋ_B`；現核 = 同一 2I 內 `ab⁻¹ ∈ 2I`）③ **多體（>2）關聯通道**（GHZ／Mermin）。
三者皆為**結構性 no-go 之候選終局**，唔係待辦清單；本 o 之交付 = 逐條給出 **✅（可構造，附顯式構造）** 或 **🔴（結構性不可能，附證明）** —— 唔接受「未明」。

## 二、已確立嘅結構（引用自 O222，逐項附出處）
```
🟢 B1 精確值：可行窗（all4）max|S| = 2 = **恰等古典界**；|S| = 3 存在（(59,60,1,61)）但 **0 個可行頂點**、需 174.7× 預算 ⟹ 唔可作物理解言
🟢 B1 更強形式：關聯**承認顯式 LHVM**（λ = 初始態 ＋ 帳本歷史；R26/G8 R_indep = 1 被決定性強迫）⟹ Bell-local 係**構造性**
🟢 B1 結構因：核 = 同一 2I 內（ab⁻¹ ∈ 2I）⟹ 無 ℋ_A ⊗ ℋ_B；sign_rank(K) = 3 ≪ rank_R = 6（缺口非 rank 現象）；角度離散（二十面體值集）
🟢 B2：無 φ ∈ [0,2π)；可見度值集量化 = {0, 1/15, 2/15, 1/5, 4/15, 1/3, 2/3, 1}（離散干涉存在，非連續）
🟢 B2 因果：D ≡ 0 之直接因 = 邊際恰 1/2（62/62），由 K 完全平衡 3720/3720 所致（**唔係**因缺相位）
🟢 B6 部分：關聯經 pair-local 因式表 ＋ memo ⟹ 結構性無信號（邊際 62/62、條件 3844/3844、ablation ≡ 0）
🔴 B6 未逐項驗證：GHZ／Mermin 型多方關聯未知（本 o 判項 c）
🔴 複相位擴張之存在性/不可能性本身（現僅兩層結構定位）
```

## 三、未確立（🔴 開放問題 = 本 o 之判決項）
```
🔴 (a) 相位擴張：可否由 K_chain⊗K_tree 生成非平凡相位因子群（U(1) 化）？最小代價幾何？
🔴 (b) 二分張量層：K_tree 之二分性可否作張量因式分解之源？核之單系統性（2I ⊆ SU(2)）係偶然定結構必然？
🔴 (c) B6：GHZ／Mermin／Klyshko 型多方非古典關聯 → 逐項機器內全量枚舉（🔴→✅/🔴 二值）
🔴 (d) 離散值集 {0,1/15,…,1} 是否為 2I 表論之**必然**（連續角結構上是否不可得）
🔴 (e) F1/F2 判準（R25 提出）之操作化：可達深度 > 1 之構造能否在凍結架構內出現
```

## 四、攻擊路線
```
1. 相位擴張精確搜索：K 嵌入 ℂ 之相位擴張族枚舉 ＋ F1/F2 判準 → 存在性／最小代價（中成本）
2. 張量層結構審計：對 K_chain⊗K_tree 做張量因式分解審計，判「單系統核」係否必然（低成本）
3. 多方關聯全量：GHZ/Mermin/Klyshko 於機器內全量枚舉（零剪枝、精確算術）（中成本）
4. 表論必然性：由 2I 之不可約表示（dim {1,2,3,4,5,6}）推出可見度值集之量化來源（中成本）
5. 邊界定理：證「純實號 ±1 讀出 ⟹ 古典關聯」之充要條件（中成本）
```

## 五、驗證標準
```
✅ B1/B2/B6 各得 **✅ 或 🔴** 二值結論（附顯式構造或不可能性證明）；禁「未明」
✅ 零新參數；禁後驗湊算子；禁 φ-power fitting
✅ F1/F2 至少一項機械判別（通過或否證）
✅ 與 docs/45 §2 之數字完全一致（2、2√2、3、174.7×、3 vs 6、8 值集、3720/3720、62/62）
✅ 若結論為「可構造」：須附顯式零參數構造 ＋ 通過四道硬測試
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

## 八、推導時序索引（round 1，2026-09-30；append-only，禁止回溯改寫）

> 依「先合約後數字、先預註冊後運算」之時序排列。所有算術 = `Fraction`／Q(√5)（numpy 僅作整數/布林加速器，唔入判決算術）。

| 次序 | 產物 | 內容 | 出處 |
|---|---|---|---|
| 1 | `data/frozen/`（3 件）＋ `data/frozen/o222_snapshot.sha256` | 凍結輸入逐字複本 ＋ O222 size+mtime 快照雜湊 | `scripts/00` A1 |
| 2 | `data/00_contract.json` | 合約＋預註冊：操作空間 S0–S5、判項 (a)–(e) 定義、預測 P1–P16、自我指紋 | `scripts/00_contract.py` |
| 3 | `data/01_relock.json` | 機器重鎖：\|2I\| = 120、K 120×62、62 列全和 0、C1 對凍結 3844 對逐項相同、max\|S\|（2／3／4）、rank_R = 6、120→60 坍縮 | `scripts/01_relock.py`（14 claims） |
| 4 | `data/02_phase.json` | (a)：階譜 {1:1,2:1,3:20,4:30,5:24,6:20,10:24}、[2I,2I] = 2I、全 120 元素與逆共軛、Σχ² = 120、Σχ = 0、FS = −1（ν₂ 交叉核對） | `scripts/02_phase.py` |
| 5 | `data/03_tensor.json` | (b)：0/1891 非交換對、12 相異讀出列／纖維 10、乘積封閉 ≤ 2¹²、類型二分 | `scripts/03_tensor.py` |
| 6 | `data/04_multiparty.json` | (c) M1 校準（2√2／4）、M2 顯式 LHVM 憑證（3782/3782）、M3 無信號、M4 修正註記、M5／M7 範圍 | `scripts/04_multiparty.py` |
| 7 | `data/04b_window.json` | (c) 真 E3/E4：全量 62⁶ 最大 = **22/15**、argmax 合法（六設定相異、無對極）、12 軸池暴力三窗 22/15、n = 4（6 軸池）38/15 | `scripts/04b_window.py` |
| 8 | `data/05_valueset.json` | (d)：15 帶號值／8 大小值、全部 3844 分子 ≡ 0 (mod 8)、左不變核階 2、300 抽樣 300/300 ＋ null ~50%、連續對照 11 值、計數層 123/2／123/88／44／174.73× | `scripts/05_valueset.py` |
| 9 | `data/06_escape.json` | (e)：F1 五物件校準 (T,T)/(T,T)/(F,F)/(F,F)/(F,F)、F2 判兩個超界值為偽、深度 = 1、逃生圖成本 | `scripts/06_escape.py` |
| 10 | `data/07_audit.json` | 審計：A1 完整性／A2 清單／A3 預測帳（16/16）／A4 剛性電池／A5 四道硬測試／A6 判決總表／A7 憲章一致性 12/12 | `scripts/07_audit.py` |

### 本輪裁決（對照 §三 之判項）
```
(a) 相位擴張   🔴  見 docs/01 §二
(b) 二分張量層 🔴  見 docs/01 §三
(c) B6 多體界  🔴  見 docs/01 §四（含憲章推論步驟之邏輯更正）
(d) 離散值集   ✅  見 docs/01 §五
(e) F1/F2      ✅  見 docs/01 §六
```

### 未閉合殘項（**明確標示，唔掩蓋**）
```
🟡 sign_rank(K) = 3：本輪**繼承** O222 R20 之精確結果（600/600 候選），未在本輪重推
🟡 n = 4 之全 62 設定枚舉：不可行（8 槽）；本輪以聲明之 6 軸頂點池為界
🟡 F1 校準集「product state」之措辭邊界：取古典乘積詮釋（已在 claim 明示披露）
🟡 時間反演相關 C1rev_num（凍結檔含此表）：本輪未逐項納入（唔影響 (a)–(e) 之判決）
```

### 方法學發現
10 條見 `docs/02_findings_and_deltas.md`（★ 最重要：憲章 B6 之「無信號 ⟹ 無多體通道」推論一般不成立，界須枚舉——本輪已枚舉並維持原結論，但**推論依據**已更正）。

---

## 九、第二輪：殘留攻堅（2026-10-01；append-only，上文第一輪記述一字不改）

**腳本**：`scripts/08_residuals.py`（預註冊在 docstring）；**結果**：`RESULT: 6/6 PASS (0 FAIL)`、`exit=0`；
**審計**：`scripts/07_audit.py` → **13/13 PASS**（新增 A8）；`round_totals = 68 / 0`；integrity 三 True（O222 734 檔未變）。

| 第一輪殘項 | 第二輪狀態 | 證據 |
|---|---|---|
| 🟡 `sign_rank(K) = 3`（繼承 O222 R20） | **✅ 已在本 o 內精確推得** | R1 構造性上界（30/62 軸有 tie 1200 項；逐軸 perceptron 修正、ε=1/10、精確覆檢 7440 項零值 0／錯配 0）＋ R2 精確下界（rank-2 ⟹ circular-ones 必要條件；窮盡搜索 362 節點無解）。判準校準：rank-2 生成 200/200 通過、隨機型 0/12 可容 ⟹ `sign_rank(K) = 3` EXACT |
| 🟡 n = 4 全 62 枚舉不可行 | 🟡 **範圍收窄，仍 OPEN**（唔假稱證明） | 逐 tuple 精確可算（樣本 −1/15、−1/15、1/3）；代數界 16 > LHV 界 4（無資訊）；全局 62⁸ 最大未算 |
| 🟡 F1「product state」措辭邊界 | **✅ 已封** | F1 v2 加「態相干」子句 ⟹ 六物件 **6/6** 精確分離（含單 qubit \|0⟩＋Pauli 讀法）；凍結機器非交換讀出對 = 0 |
| 🟡 `C1rev_num` 未納入 | **✅ 已閉合（新關係）** | `C1rev_num ≡ C1_numᵗ`（3844 項 0 不符）；`C1 ≠ C1ᵗ`（2388 項）⟹ 世界線非交換性全含於 C1 |

**新增方法學（續 docs/02，編號 12–15）**：① tie ≠ 約定（tie 亦可由 rank-3 幾何精確分開）；② 必要條件否證法（比候選搜索強）；③ 判準必先校準（正對照＋判別力）；④ 反演表即轉置。
**第三輪候選**：n = 4／一般 n 之全局多體最大（需結構性歸約）；E4 值集是否全落 `1/15` 網格。
**紀律**：第二輪同樣只寫入本 O 目錄；第一輪已閉合記錄（§一–§八、`docs/01–03`）未被改寫。

---

## 十、第三輪：E4/E5 全量與 n = 4 界結構（2026-10-01；append-only，上文一字不改）

**腳本**：`scripts/09_global_n.py`（R6–R9，預註冊於 docstring）、`scripts/10_e5.py`（E1–E2）、`scripts/11_determinism.py`（D1–D2）；
**結果**：`09` → `8/8 PASS`、`exit=0`；`10` → `2/2 PASS`；`11` → `2/2 PASS`；
**審計**：`07_audit.py` → **16/17 PASS（1 FAIL = A1）**；`round_totals = 80 / 0`；全文 `docs/05_global_n.md`。

| 第二輪殘項 | 第三輪狀態 | 證據 |
|---|---|---|
| 🟡 n = 4 全 62 枚舉不可行（全局 62⁸ 最大未算）| 🟡 **仍未閉合，但由無界收窄為有限區間 [4.0, 6.4]** | R6 E4 全量（14.8M，off-grid 0）→ R7a 精確 (d,d′) 分離 → R7b raw 退化（480/120 = 界）→ R7c 三角界否證（8 > 4，遮罩亦 120）→ R7d 三窗口池內極值（480／320／224）→ R7f 無條件放鬆憑證（sup ≤ 768/120 = 6.4，支配性＋校準＋一致性三驗）|
| （新）E4 值集是否落 1/15 網格 | **✅ 是（全量）** | 14,776,336 項全 ≡ 0 (mod 8)；19 個相異值；`max|E4| = 1` 於四軸全同 |
| （新）E5 層 | **✅ grid 閉合；n = 5 未決** | 全 62⁵ = 916,132,832 項 off-grid 0；`max|E5| = 48/120`；`16·max = 6.4 > 4` ⟹ OPEN |
| （新）決定性 | **✅** | 09／10 決策投影重跑前後逐位元相同（宣告式時序正規化；`docs/05` §13.2）|

**新增方法學（續，編號 16–24）**：見 `docs/05` §11 與 §13.4（顯式索引防假 PASS、兩極值鐵律、raw 窗退化識別、遮罩極值、放鬆憑證自我驗證三件套、精確化約 vs 放鬆、並行 session 環境之唯讀證明、決定性正規化）。
**環境發現**：預註冊 mtime 快照儀器（A1）在並行 session 環境下**不足**（如實 FAIL）；改以內容雜湊（O222 MANIFEST 350/350）＋足跡歸因＋原始碼掃描重建結論（A11 PASS）；儀器修正（滾動讀集快照）記入下一輪。
**紀律**：第三輪只寫入本 O 目錄；第一、二輪已閉合記錄未被改寫；第三輪修訂（R7b/R7c 由「期望閉合」改記為 finding）發生於本輪尚未閉合期間，已於 `docs/05` §0 明示。

---

## 十一、第四輪（2026-10-01）— n = 4 全域精確閉合（路線 (1) 履行）

| 項 | 結果 |
|---|---|
| 🟡 第三輪遺留「n = 4 全 62⁸ 最大 ∈ [480, 768]/120」| **✅ 閉合：精確 512/120 = 4.266667**（62⁶ 外層分片精確枚舉；覆蓋 = 56,800,235,584 = 62⁶；四路獨立驗證）|
| （新）參考值 | 全域 min = −512/120；argmax = (V00,E28,V00,E21,E11,F10,F01,F16)；LHV 界 = 480/120 |
| ★★（新）合法性與超越 | argmax 之四對設定全相異 ⟹ 在**合法（每對內相異）Bell 窗**內；合法窗 ⊆ 原始窗 ⟹ party 窗全域 = 512 **恰等** ⟹ **在合法窗內超越 n = 4 Mermin 不等式，超額 32/480 = 6.667%** |
| （新）預註冊 P9 | n = 3 子句不變（22/15 < 2）；**n = 4 子句證偽**（原「6 軸頂點池」範圍被越過）⟹ 須改記為「n = 3 confirmed ／ n = 4 REFUTED」|
| （新）第三輪 `eight_anti` 語意 | finding（如實）：v3 語意允許 `(d,d′)` 對極；池內 880/46,080 = 1.910% 之最大值必用對極 |
| 🟡 八者相異窗全域 | **仍未閉合**：eight ∈ [320, 512]、eight_anti ∈ [224, 512]（專用加窗趟次未執行，明示）|

**新增方法學（續，編號 25–29）**：見 `docs/06` §4（「池」是遮蔽物；子集+達成者=等式夾；分片覆蓋即證據；
多窗耦合之精確 top-K；同輪內實作修訂留痕 + 決定性重跑證明路徑穩定）。
**跨文檔標註**：`docs/01` §四 加 dated cross-reference（原文與標籤不動；(c) 之 n = 4 依據待判決層裁定）。
**紀律**：第四輪只寫入本 O 目錄；判決算術全整數（numpy 僅整數加速器）；零新參數；第一、二、三輪已閉合
記錄未改寫。

**Close-out 鏈結果（2026-10-01 03:03）**：`11_determinism` **3/3**（D1/D2 + **D3 同片重跑**）、
`12 --aggregate` **6/6**、`13_party_window` **5/5**、`07_audit` **17/18**（唯一 FAIL = A1 環境儀器；
A11 PASS 350/350）。**ledger 92 claims / 0 FAIL**。產物雜湊 21 檔 = `scratch/o224_r4.sha256`。
→ **本輪唯一殘留**：八者相異 / v3 嚴格窗之全域精確值（界於 [320, 512] / [224, 512]），記為 register
之遺留項（非新 O）。

### 十一.1 加值審計（addenda 14/15，同日 03:2x）

| 項 | 結果 |
|---|---|
| 觸發 | 遲到通知（`probe_r4.py`）報 v3 `eight_anti` 對極實現 **392** vs 本輪普查 **880** ⟹ 先核污染：21/21 雜湊 OK、活躍判決進程 0 ⟹ **零污染** |
| `scripts/14_census_exact.py` | 存在計數（規則無關）= **11,318 / 46,080 = 24.5616%**；Q1/Q2/Q4 PASS、**Q3 如實 FAIL（失敗即發現：重建規則得 1,734／1,794，正係 tie 退化之證）** |
| `scripts/15_anti_convention.py` | **4/4 PASS**：T1 逐字重現兩慣例（880／392）、T2 以另一算法（62×62 外和）重現 11,318、T3 關係、T4 混合達成見證（mixed = 11,318）|
| 量化更正 | v3 精度發現之發生率 **1.91%（census 慣例）→ 24.56%（存在計數）**（低估 ≈ 12.9 倍）|
| 審計 | **A14** 新增 ⟹ **18/19 PASS**（唯一 FAIL 仍 A1）；ledger 92/0 不變 |
| 方法學 | 新增 30–32（存在式計數／逐字重現他碼慣例／預註冊 FAIL 即發現）|


---

## 十二、第五輪（2026-10-01）— 五窗全域極值精確閉合（append-only，上文一字不改）

| 項 | 結果 |
|---|---|
| 🟡 第三輪／第四輪遺留「`eight ∈ [320, 512]`、`eight_anti ∈ [224, 512]`」| **✅ 閉合：兩者皆為單一精確數 `512/120 = 4.266667 = 64/15`**（全 62⁸ 分片精確枚舉，覆蓋 = 62⁶ = 56,800,235,584）|
| （新）五窗全域極值 | `raw_full` = `party` = `eight` = `anti_v3` = `anti_str` = **±512/120**（四個窗之 max 全等、min 全等）|
| （新）最嚴窗得勝配置 | `eight`／`anti_v3`／`anti_str`：max `[0, 60, 32, 59, 23, 44, 14, 31]`；min `[0, 60, 32, 59, 23, 44, 29, 12]` |
| ★★（新）結構意義 | LHV 古典界 = 480/120 = 4；超越 = **32/480 = 6.667%**，且在最嚴窗（八者相異 ∧ 八者兩兩非對極）**同樣成立** ⟹ 第四輪「合法窗內超越」升級為「**最嚴窗內超越**」；超越非放寬約束之產物 |
| ★（新）閉合之雙錨 | 上界 = 第四輪已閉合之全域 raw max 512（窗 ⊆ raw，來源獨立）；下界 = **一個**見證，經 C8 四路獨立驗證（直接 8 項／成員檢查／未因式化四項／該群全 62⁴ 材化）⟹ **結論不依賴窮舉本身之正確性** |
| （新）引擎量測（答用戶「必須 CPU 嗎」）| numpy CPU 21.5 ms/group/核（5–7 h）／CuPy GPU **2.87 ms**（**11.8 h**，最慢）／Numba JIT 12 線程 **1.30 ms**（**5.3 h**）⟹ **GPU 可用但更慢**（小軸歸約 × 網格選取係 memory/latency-bound，唔食 tensor core）|

**新增方法學（續，編號 33–35）**：見 `docs/06` §7 —— 「雙錨閉合」（上界取自已閉合之更大域，新引擎只負責
找見證）、「三引擎交叉驗證且逐群／累加分開驗」（兩路比對會把共通盲點變假綠）、「互斥分片 checkpoint ＋
共同受限域驗累加」（長跑 8 段、端點取 n_shards 倍數以保持 `p % ns == k` 分片指派精確）。

**跨文檔標註**：`docs/01` §四 於既有 2026-10-01 cross-reference 之下加第二筆 dated 註記（原文與標籤不動）：
(c) 之 n = 4 依據在**最嚴窗內**仍超越古典界（512 vs 480），惟 (c) 標籤之語意層裁定仍留判決層。

**紀律**：第五輪只寫入本 O 目錄；判決算術全整數（無 float／fastmath／近似）；零新參數；第一至四輪已閉合
記錄一字未改；同輪實作修訂（`16` 之 `outer_tuples` 欄位定義與 C9 呼叫簽名、`18` 之 merge 同欄位）**僅及
驗證管線／欄位、判定值零改動**，並以「12 分片 `windows` 逐位元相同、僅 `outer_tuples` 變」之欄位級比對為證。

**Close-out 結果（2026-10-01 09:37）**：`18 --check`（J1，136 宣告群，三路）**ALL OK**；`18 --check-range`
（J6，共同受限域）**ALL OK**；`17 --check`（G1）**ALL OK**；`18 --run-range` ×8 → `--merge` → `16 --aggregate`
= **C1–C9 9/9 PASS（0 FAIL）**。產物雜湊 31 檔 = `scratch/o224_r5.sha256`；預註冊 = `scratch/o224_r5_prereg.sha256`。
→ **本輪無殘留**：第三輪起之兩個殘界全數消滅；(a)(b)(d)(e) 四判項不變，(c) 之語意層裁定仍在判決層。

### 十二.1 收尾補記（同日 09:4x–10:0x）：A15、一項更正、環境 FAIL（append-only）

| 項 | 結果 |
|---|---|
| ★ 更正（如實） | 分片層極值**非每片 512**：**分片 05／06** 之 `anti_v3`／`anti_str` = **480/−480（恰等古典界）**，其餘 10 片 = 512/−512 ⟹ **最嚴窗之超越非泛用**（由 A15 首跑如實 FAIL 抓出）|
| 儀器根因 | `18 --merge` 摘要 print 洩漏迴圈變數，重複印最後一片之值 ⟹ 首跑 run log 尾 12 行全部 512（**數據檔一直正確**）；已修 print ＋ 重跑 merge（內容逐位元不變，manifest 覆核）|
| 新增審計項 | **A15**（唯讀核 16/17/18 全鏈：9/9 claims、五窗 ±512、覆蓋 3844 對、`outer_tuples` = 62⁶、各片 ∈ [480,512]、**in-O 雜湊清單 32/32**、J1/J6 ALL OK、8 range 起點、smoke 移位未刪、SIGTERM 舊 log 標 SUPERSEDED）⟹ **PASS** |
| 審計現狀 | **18/20 PASS**；兩個 FAIL 皆環境儀器：**A1**（第三輪起已知之 mtime 儀器）、**A11**（本輪新：內容檢查仍 **350/350 PASS**、目錄外路徑字面量 = []，僅因並行 session 漂移跨越 ±60 s 簇）|
| 修訂留痕 | `scripts/18`（print）、`scripts/07_audit.py`（A15）、`data/16_r5_manifest.sha256`（in-O 清單）——**判定值全輪未曾改動** |

### 十二.2 引擎成本表更正（同日 10:1x，append-only；實測取代推算）

| 項 | 結果 |
|---|---|
| 更正 | §十二 表內「numpy CPU 21.5 ms/group/核」為 **profiling 推算**；**實測 = 14.3–15.0 ms／group／核**（`logs/18_engine_measure.out`），即 12 進程 ≈ **5.0 h**，與 JIT（1.280 ms／group 12 線程 ⟹ 5.3 h）**實質等效** |
| 更正 | GPU 2.84–2.90 ms／group（chunk 64 與 128 **同速**）⟹ **「3 GB VRAM 逼細 chunk」之歸因撤回**（顯卡確為 GTX 1060 3 GB：`nvidia-smi` 3072 MiB ✓，但 VRAM 唔係瓶頸）；可支持歸因 = 小軸歸約＋多次 kernel launch＋算術強度低 |
| 影響 | **零** —— 三引擎之判定值（五窗極值、覆蓋、得勝配置）與成本表無關；本輪生產路徑為已三層驗證之 JIT，`16` 全 62⁴ 作獨立覆核（C8）|
| 登錄檔 | `scratch/measure_engines.py` → `logs/18_engine_measure.out`；首跑 VRAM 行印錯之檔保留為 `logs/18_engine_measure_firstrun_vram_mislabel.out`（已加註無被引用）|

### 十二.3 劇本鏈完整性審計（同日 10:3x，append-only）

| 項 | 結果 |
|---|---|
| 問題 | 整個 O224 推導過程是否完整留下 python 劇本檔案鏈？**答：現時係「是」** |
| 機械證據 | `scratch/chain_audit.py` → `logs/19_chain_audit.out`：**VERDICT: CHAIN COMPLETE（0 failed checks）**；`scripts/07_audit.py` **A16 PASS**；審計總計 **19/21**（A1／A11 環境儀器）|
| ★ 真缺口（已補） | R2–R5 探針、R4/R5 啟動器、round manifests 原只在 **Hermes scratch（24 h 會清）** ⟹ 逐位元鏡射入 `scratch/probes/`（16）＋`scratch/manifests/`（11＋revA 12），附 `PROVENANCE.md`（**27/27 雜湊一致**）|
| ★ 命令列缺口（已補） | R1–R5 調用命令列原只在對話 ⟹ 新增 driver of record **`scripts/run_chain.sh`**（**49 條調用／31 個 run 語句**，預設 dry-run、`--execute` 才真跑；R1–R3 重建＝語意正確非逐字回溯，如實註明）|
| 依賴 | 唯一外部依賴 = `data/frozen/*`（O222 快照）；其餘全鏈自足 |
| 產物 | in-O manifest **81 條**（含鏡射全件）；新文檔 `docs/07_script_chain.md`；新 log `19_chain_audit.out`、`19_chain_dryrun.out` |

### 十二.4 劇本鏈合併入 `scripts/`（同日 10:5x，append-only）

| 項 | 結果 |
|---|---|
| 問 | 是否在 **`scripts/`** 資料夾完整留下 python 劇本檔案鏈？**答：係（現時）** —— 42 支劇本／啟動器／工具**全部在 `scripts/`**（44 件含 2 份說明）|
| 組成 | 判定鏈 20（00–18＋`lib2i`）／driver 4（`run_chain.sh`＋3 支輪次啟動器）／探針 14（`probe_*`×12＋`bench_r5`＋`prof_r5`）／收尾工具 3（`measure_engines`、`chain_audit`、`chain_audit_v1`）|
| provenance | `scripts/MIRROR_PROVENANCE.md` 逐檔 sha256；A 組 16 件鏡射檔 **16/16 與來源一致**；`scratch/probes/` 已移除（搬移非刪除）；round manifests 等證據留 `scratch/manifests/`（11＋revA 12）|
| 防再散 | **A16 加 `SCRIPT CONSOLIDATION` 斷言**（`scratch/probes` 不存在＋probe ≥14＋tool ≥2＋launcher ≥4）|
| 現況 | `chain_audit` **CHAIN COMPLETE（0 failed）**；`07_audit` **19/21 PASS**（A1／A11 環境）；manifest **80 條 OK**；driver dry-run **49 條**|
| tripwire | 改審計/工具或 provenance 表列檔後：①重生成表 ②刷新 manifest 行 ③才跑審計（本輪撞 3 次並修好，已寫入 docs/07）|
