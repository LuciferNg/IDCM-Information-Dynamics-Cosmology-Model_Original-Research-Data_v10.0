# 20. G1 + G8 合約 — ctx→s 映射與記錄冗餘（`g1g8-contract-v1`，2026-09-30）

## §0 範圍與聲稱上限（先寫死）

- **G1 之重述（唔改舊結論，只做本輪任務）**：舊判定 =「D5 觸發所需之 `ctx → s` 坐標映射**唔存在於凍結記錄**；
  合約明文**禁自創**」（`docs/07 §6`、`docs/08 §7`、`docs/09 §8`）。本輪**唯一**任務：
  **問「該映射可否由凍結記錄推導」**——若可，則**讀出**（唔係發明）並精確計算 D5 之觸發 `|N(s) - s| > 0`；
  若不可，則缺口**維持**並明寫原因。
- **G8 之重述**：D6 P3c 量得**可及深度 = 1**（只讀 ledger 頂）⟹ 單副本、無環境冗餘 🔴。本輪把「冗餘」**分層**
  並逐層精確量化（ledger 條目／衝突／一致性；K-row 簡併；orbit），判定邊一層（若有）滿足 QM 之 `R >= 2`。
- **戒律**：唔宣稱導出 QM／ħ／Hilbert／Born；唔宣稱「量子非局域」；**唔自創語義**（任何映射／度規必須
  逐項指出凍結出處）。

## §1 凍結輸入（唯讀，hash pin）

| 代號 | 對象 | 用途 |
|:--|:--|:--|
| **I1** | `scripts/09_a2_rollback.py`（`d8037bb1…`） | `load_inputs()`（62 軸 `U`、`ids`、`types`、`hvec`）、`build_group()`（`G`、`idx`、`MUL`）、`qkey`、Q(√5) 算術；**寫入規則**（`read` 未命中 ⟹ `s := MUL[s][h(ctx)]`） |
| **I2** | `scripts/12_b5_budget.py`（`f2cb54fa…`） | `load_machine()`、`load_a2()`、`run_pair(a,b,s0,top,K,MUL,hx,budget)`（回 `s_final/x_a/x_b/top/misses`；本輪 budget 取 `10^9` ⟹ 終止條件不觸發） |
| **I3** | `scripts/09` 之凍結次序 | `pairs = [(a,b) for a in range(62) for b in range(62)]`（字典序；B5／D6／G4 同一次序） |
| **I4** | `docs/13_d6_results.md` P3b／P3c | 記錄支配當前態（2 例）／可及深度 = 1（**引，不重推**） |
| **I5** | `docs/07 §6`、`docs/08 §7`、`docs/09 §8` | G1 之原文與「禁自創」條款 |
| **I6** | O210 `docs/01`／`docs/02`（**唯讀**） | 𝒯 = `K_chain ⊗ K_tree` 之 T0 純量像 `s = f(A)`（投影路線之 provenance） |

## §2 六格謂詞（見數前凍結；ASCII 形式為 doc↔impl 對齊字串）

| 格 | 謂詞 | 判據（ASCII） |
|:-:|:--|:--|
| **G1a** | **映射存在性**：讀出凍結寫入規則之 ctx 索引 —— `s_coord(ctx) = idx[h(ctx)]`（`h` 表 × 群 2I 之元素索引），並以凍結機器核對 `s := MUL[s][h(ctx)]` 逐 s 相符 | ✅ ⟺ 62/62 ctx 有 `h` 值、且對每 ctx 之 120 個 s，機器寫入後之態 = `MUL[s][h(ctx)]`（120/120 逐 s 相符）；另報 62 個 `h` 值之相異數（單射性） |
| **G1b** | **D5 觸發之精確計算**：`N(s) := MUL[s][h(ctx)]`（凍結寫入），觸發量 = 四元數坐標之**平方範數** `\|N(s) - s\|^2 ∈ Q(√5)`（精確） | 報 7440 = 62×120 對中 `> 0` 與 `= 0` 之數目、`= 0` 之 ctx 集合（`h(ctx) = e`）、平方範數之**精確值集**；判定觸發是否只依 ctx（唔依 s） |
| **G1c** | **候選路線比較**：① memo 一致性路線（D6 記錄 = trigger 為空）以計數重證；② O210 投影路線（唯讀）：`𝒯` 之 T0 純量像是否載有**顯式 f** 與維數 | 路線① ✅ ⟺ 重證結果與 D6 一致（trigger 空集之計數相符）；路線② 若上游**無顯式 f／無維數** ⟹ 只可報 **🟡 provenance**。兩者合併：本格取**較弱者** |
| **G8a** | **ledger 量化**：一 pass（3844 對 × 120 態、全量）內，逐 ctx 之**寫入條目數**（mean／min／max）、出現「同一 ctx 兩個值」之**衝突 ctx 數**、讀取總數 | ✅ ⟺ 計數自洽：`reads = 7688`、`writes = Σ([top != a] + [a != b])`、且 `misses` 逐對 = `[top != a] + [a != b]`（全量核對）；報衝突 ctx 數（> 0 即證明 ledger 內有 stale 副本） |
| **G8b** | **一致性冗餘**：`R_consistent` = 與某次讀取之返回值一致、且**可獨立讀取**之條目數 | ✅ ⟺ `R_consistent = 1`（只有頂可讀，引 I4）**且**存在 stale 副本（衝突數 > 0）⟹ 副本**唔一致** ⟹ 無冗餘；同時報 `R_naive`（同一 ctx 之總條目數最大值）作對照 |
| **G8c** | **多重性候選**：K-row 簡併度（120 態按 62 維 K 行分組之重數）＋ 2I orbit `{12,20,30}`＋ ledger 是否 ≥ 2 個**獨立 fragment** | 🔴 ⟺ 全部多重性**不可觀測**（同 K 行 ⟹ 對全部 62 setting 值相同）且 ledger fragment 數 = **1** ⟹ 唔滿足 `R >= 2`；✅ ⟺ 存在可觀測且獨立之 ≥ 2 fragment |

## §3 精確算術與度規出處

- 態坐標 = 凍結四元數 `q_s ∈ Q(√5)^4`（I1 之 `G` 元素，單位範數 ✓）；距離用**平方範數**
  `\|q_{N(s)} - q_s\|^2 = Σ_i (Δq_i)^2`（每個分量 ∈ Q(√5) ⟹ 平方和 ∈ Q(√5)·… **注意**：Q(√5) 對乘法封閉 ✓
  ⟹ 平方範數 ∈ Q(√5) ✓ 精確可比）。
- 零距判定：`\|Δ\|^2 = 0 ⟺ q_{N(s)} = q_s`（正定）⟹ 與 `N(s) = s`（索引相等）**必須一致**（兩路互核）。
- 一律 `Fraction`；禁浮點字面值、禁 `math/numpy/random`（抽樣若有須手寫 LCG，見 §4）。

## §4 抽樣與全量

- G1a：62 ctx × 120 s = **7440** 全查。G1b：**7440** 全查，值集全收。
- G8a：**120 × 3844 = 461,280** 對-step 全量（無抽樣、無剪枝）；由凍結 `run_pair` 之輸出（`top`、`x_a`、`x_b`、`misses`）
  **重建** ledger，唔另寫機器語義（寫入位置 = 首讀未命中則寫 `a`；`a != b` 則第二讀必寫 `b`）。
- 若任何格未達全量 ⟹ 該格明文標 🟡 ＋ 樣本數 ＋ 預先寫死之 LCG（`a = 1103515245, c = 12345, m = 2^31, seed = 20260930`）。
- 節點上限 `30000000`；時間上限 600 s；觸限即降 🟡。

## §5 執行與閘

```
1. scripts/29_g1g8_contract.py --freeze-impl scripts/30_g1g8_gaps.py     (強制者；須 GATE = OPEN)
2. scripts/30_g1g8_gaps.py                                              (機器；6 格)
3. scripts/31_g1g8_audit.py                                             (獨立審計；唔准 import 30)
```
- 閘必查：I1／I2 hash pin、上游 GATE（`logs/26_c2g7_contract.out` 須含 `GATE = OPEN`）、impl AST（禁
  `numpy/scipy/math/random`、禁非整數浮點字面值、禁變數名 `pi/log/cos/sin/tan/exp/sqrt`）、
  6 條 doc↔impl ASCII 對齊（`s_coord(ctx) = idx[h(ctx)]`、`|N(s) - s|^2 > 0`、`value-level consistency`、
  `ledger entries per ctx`、`R_consistent = 1`、`R >= 2`）、`30000000` 兩邊出現。

## §6 咩算「改判準」（禁）

見數後改：① 六格判據；② `s_coord` 之定義（**禁**改為見數後之替代映射）；③ 距離度規；④ ledger 重建規則；
⑤ 「冗餘」之定義（禁把「不可觀測簡併」講成環境冗餘）。任何改動 ⟹ amendment ＋ 重凍 ＋ 保留首跑 log。

## §7 Amendment 表

| # | 日期 | 內容 | tighten／loosen | 值有無變 |
|:--|:--|:--|:--|:--|
| **A1** | 2026-09-30 | **impl-only（來源更正）**：§1 加 **I7 = `scripts/18_d6_mapping.py`**（`a681ae8cf6bc…`，即量得「可及深度 = 1」之凍結 D6 機器）；§4 之 ledger 來源由 `scripts/12.run_pair` 改為 **I7 之 `replay_protocol`**（**真 ledger**）＋本機以**同一協定**之顯式重播（逐對與 I7 之 `misses／top／ledger_len` 全量比對，0 mismatch 才採用）。原因：**首跑揭露 `scripts/12.run_pair` 之 `L` 只是一元「頂標記」**（`L = [(top, 0, s0)]`，值為偽 `0`），**唔係 ledger** ⟹ G8a／G8b 之逐 ctx 統計在該對象上**無定義**（首跑 log `logs/30_g1g8_firstrun_runpair_ledger_wrong.out` 保留）。**六格謂詞、判據、門檻全部不變**；G1a 之行為核對改以**對角對 `(a,a)`** 隔離單次寫入（`s_final == MUL[s0][h(a)]`，62×120 全查），與 §2 原文「機器寫入後之態 = `MUL[s][h(ctx)]`」逐字相符。§5 之閘條件 C6 同步改為：**只准**申報之顯式重播（`ledger_replay`），且**必須**逐對與 I7 之 `replay_protocol` 全量比對（新閘條件 C7 檢查 I7 檔名與驗證欄位）。 | 無（來源更正） | 無（首跑全部 FAIL 係假設錯，未產生有效值） |
