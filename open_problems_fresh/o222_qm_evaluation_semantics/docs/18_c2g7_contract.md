# 18. C2 + G7 合約 — 測度 ↔ 概率結構（Born 型）之對照（`c2g7-contract-v1`，2026-09-30）

## §0 範圍與聲稱上限（先寫死）

- 本輪**唔**宣稱導出 QM、唔宣稱導出 ħ／Hilbert 公理／Born 律。本輪只回答一件事：
  **凍結機器之測度結構係咩**，以及 QM 之 Born 結構（`p = |amp|^2`、干涉、non-commuting observables）
  在**邊一層**存在／缺席。
- **D6 P2d 之 🔴 判定維持不變**（原文謂詞：表值是否非負歸一權重；答案：否，C1/C2 係**帶號相關**）。
  本輪**唔改** `docs/12`／`docs/13` 任何一字；本輪只把 G7 之缺口**重新定位**（新檔另記）。
- 語言：精確算術（`Fraction`）為唯一權威；浮點只可作**資訊**，唔可作判據。

## §1 凍結輸入（唯讀，hash pin）

| 代號 | 對象 | 內容 |
|:--|:--|:--|
| **I1** | `scripts/09_a2_rollback.py`（`d8037bb1…`） | A2 機器語義：`read` 命中律、`rollback`、`C1 = (1/120) Σ_s K[s][a]·K[MUL[s][h(a)]][b]`、E2 之 exact DP、`EPOCHS = (0,961,1922,2883)`、62 軸、120 態 |
| **I2** | `data/09_a2_correlation.json` | `denominator = 120`、`C1_num`、`C1rev_num`、`C2`（Fraction 字串）、`axis_ids`、`axis_types` |
| **I3** | `scripts/12_b5_budget.py`（`f2cb54fa…`） | `load_a2()`、`load_machine()`、`run_pair(a,b,s0,top,K,MUL,hx,budget)` 回 `{s_final,x_a,x_b,top,misses}`；`PER_READ = 123/88`、`E_MIN = 123/176` |
| **I4** | `docs/13_d6_results.md` P4c | 結果邊際 = **1/2**（3844/3844）——**引，唔重推** |
| **I5** | `docs/17_g5_results.md` | G5 之 anti 完美匹配（31 對）與 62 setting 之列平衡（Σ_s K[s][a] = 0）——**引** |

**K/MUL/hx 之重建**：一律由 `scripts/12.load_machine()` 取得（佢自己 import `scripts/09`）；本輪**唔**自建群。

## §2 七格謂詞（見數前凍結；ASCII 形式為 doc↔impl 對齊字串）

| 格 | 謂詞 | 判據（ASCII） |
|:-:|:--|:--|
| **C1** | **態測度**：DP 之 `p_k` 是否**逐步 = uniform(1/120)**（非負、Σ = 1、pair map 保測） | ✅ ⟺ 全部 3844 步 `dev_L1 = 0` EXACT，且 `p_k = uniform`（值集 = {1/120}）；報 支持集大小、`max p`、`min p`；**另報**由群公理導出之保測性（`MUL` 為左平移 ⟹ 雙射） |
| **C2** | **結果測度**：每 setting 之 `P(+1) = 1/2` | ✅ ⟺ `sum_s K[s][a] = 0` ∀ a（62/62），並核 62 欄各 60 個 +1、60 個 −1；**引 I4** |
| **C3** | **乾淨四元組之 joint measure（LHV 憑證）** | ✅ ⟺ 存在 16-atom 有理非負歸一 `p`，`sum p = 1`、四邊際各 `1/2`、四相關值（由 `p` 重算）與**凍結表**逐項吻合；方法 = **精確頂點枚舉**（`vertex enumeration`：9 條等式 + 7 變量置零，`Fraction` 高斯消元） |
| **C4** | **`|S| > 2` 四元組之 joint 不可行** | 🔴/✅ 由精確可行性判定機械決定（同一頂點枚舉法）；**另附**原子級憑證：對全部 16 個 `±1` 原子，`x1*y1 - x1*y2 + x2*y1 + x2*y2 <= 2` ⟹ 任何 joint measure 皆有 `|S| <= 2`（無條件，唔需邊際條件） |
| **C5** | **amplitude／秩結構** | 報 `rank_R(K)`（`Fraction` 消元）、# 相異 row、**sign-rank = 1 之充要**（rows 兩兩相等或互補）之反例對數、greedy fooling-set 下界。🔴 ⟺ `sign_rank > 1`（即存在非「相等／互補」之 row 對）且秩 > 1 ⟹ 唔可由 `sqrt(p)sqrt(p)^T` 之 rank-1 疊加產生 |
| **C6** | **交換性分層** | 報 (i) 62 個觀察量 `diag(K)` 之對易數（全部 = 0 非對角 ⟹ 全對易）；(ii) `2I` 之換位子群大小（是否 = 120 = 完美群）；(iii) 平移對 `(a,b)` 中 `h(a)h(b) != h(b)h(a)` 之數目。✅ ⟺ 觀察量**全對易** |
| **C7** | **零判別力檢查（方法論）** | 🟡 ⟺ 機械證明「任何非負歸一 `p` 都係某 rank-1 PSD 之對角」（`sqrt(p)sqrt(p)^T`）⟹ 該類檢查對 Hilbert-origin **零判別力**，唔可當證據（沿用 `docs/20` α_s 之教訓） |

## §3 四元組之凍結選取規則（寫死，唔准見數後改）

- CHSH 形式：`S(a,a2,b,bp) = C[a][b] - C[a][bp] + C[a2][b] + C[a2][bp]`（與 `scripts/09.chsh_max` 之 `P[i] - Q[j]` 一致）。
- 域 `D_all4`：`a != a2`、`b != bp`、`b` 與 `bp` 皆 ∉ `{a, a2}`，且四對 `(a,b)/(a,bp)/(a2,b)/(a2,bp)` **皆非對蹠**（`anti` 表），與 G5/B3R2 之 `all4` 一致。
- `M = max{|S| : tuple in D_all4}`（精確）。
  - 若 `M <= 2`：C3 之四元組 = argmax（tie-break：字典序最小 `(a,a2,b,bp)`），亦報之為 C4 之對象（並標「無 `|S| > 2` 情形」）。
  - 若 `M > 2`：C4 之四元組 = 該 argmax；C3 之四元組 = `D_all4` 內 **`|S| <= 2` 之子域**之 argmax（tie-break 同上），兩者**皆須報**。
- 對 `C1` 與 `C2` 兩張表**各做一次**（共 4 個對象：C1 之 C3/C4、C2 之 C3/C4）。
- 可行性判定之維度：`p` 為 16 個 atom 之有理權重；等式 = 1（歸一）＋ 4（四邊際 = 1/2）＋ 4（四相關值）= **9**；非負 = 16。頂點枚舉 = 選 7 個變量置零解 9×9 系統（`Fraction`），檢查全部等式與非負。

## §4 抽樣與全量

- 本輪**全部格皆全量／精確**，**零抽樣**（DP 全 3844 步、62 欄全查、四元組域精確最大化、頂點枚舉完備）。
- 若任何格因資源界限未能完備 ⟹ 該格必須明文標 🟡 ＋ 報樣本數 ＋ 用**預先寫死**之 LCG（`a = 1103515245, c = 12345, m = 2^31, seed = 20260930`）；**唔准**把抽樣當精確。
- 節點上限 `30000000`；時間上限 600 s；觸限即降 🟡 並如實報。

## §5 執行與閘

```
1. scripts/26_c2g7_contract.py --freeze-impl scripts/27_c2g7_measure.py     (強制者；須 GATE = OPEN)
2. scripts/27_c2g7_measure.py                                               (機器；7 格)
3. scripts/28_c2g7_audit.py                                                 (獨立審計；唔准 import 27)
```
- 閘必查：I1–I3 之 hash pin、上游 GATE（`logs/23_g5_contract.out` 須含 `GATE = OPEN`）、impl AST（禁 `numpy/scipy/math/random`、禁非整數浮點字面值、禁變數名 `pi/log/cos/sin/tan/exp/sqrt`）、doc↔impl 之 7 條 ASCII 對齊字串、`C1`–`C7` 全在、`vertex enumeration` 與 `30000000` 出現於兩邊。
- 機器必須 **append-only** 寫 `data/27_c2g7_results.json`（連 `cell_order`）＋ 每個格自報 verdict。

## §6 咩算「改判準」（禁）

見數後改：① 七格之判據；② 四元組選取規則；③ 可行性判定維度（等式／非負集）；④ 秩／sign-rank 之定義；
⑤ 把「觀察量對易」放寬為「狀態對易」等偷換。以上任何一項改動 ⟹ 開 amendment ＋ 重凍 ＋ 保留首跑 log；
**唔准**只改一行而唔記。

## §7 Amendment 表

| # | 日期 | 內容 | tighten／loosen | 值有無變 |
|:--|:--|:--|:--|:--|
| A1 | 2026-09-30 | **impl-only**：可行性子程序之**邊際方程編碼**修正 —— 首版寫成 `2·Σ p'·x_w = D`，正確為 `Σ p'·x_w = 0`（因 `P(+1) = 1/2 ⟺ E[x_w] = 0`）；首版令 LP **恆不可行**（sanity case 亦 0 頂點）。**謂詞、判據、維度、四元組選取規則全部不變**；重凍；首跑 log 保留（`logs/27_c2g7_firstrun_c3_infeasible.out`） | — | C3 由 🟡 → ✅（其餘六格不變） |
