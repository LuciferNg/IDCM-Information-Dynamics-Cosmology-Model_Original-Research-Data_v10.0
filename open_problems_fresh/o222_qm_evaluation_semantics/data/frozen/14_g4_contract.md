# 14. G4 合約 — 讀取次序之結構導出與唯一性（`g4-contract-v1`，2026-09-30）

> 本文件在任何數字產生**之前**凍結。改動須走 §7 amendment（＋標明 tighten／loosen ＋重凍 ＋保留首跑 log）。

## §0 範圍與聲稱上限

**問**：B3R2 之五條 order 家族（`lex`／`diag`／`antidiag`／`block`／`stride`）係**人為**。讀取次序可否由**凍結結構**導出？

**改寫**：由 D6 之命中律（`docs/13` P2a/P2c：pair 之後 ledger 頂 = 該對之 b；成本 = 3 − [入頂 = a] − [b = a]）
把次序問題化為**有向圖之 Eulerian 問題**。

**聲稱上限（唔准超出）**：
1. 本輪**唔**引入任何新語義（全部輸入唯讀；次序係由圖結構**導出**，唔係選出）。
2. 本輪之唯一性結論**只可**關於「次序**類**」（Eulerian 類），**唔可以**講「唯一次序」——除非 §4 P4 之計數**等於 1**。
3. 本輪**唔**重推任何 CHSH 值（引 B3R2 `data/15_b3r2_results.json` 之判準與記錄）；P5 若可構成才計算，並須用**同一**統計量定義。

## §1 凍結輸入（全部唯讀，附所有者）

| id | 物件 | 所有者（可獨立重跑） | 用途 |
|:--|:--|:--|:--|
| I1 | 機器 `run_pair(a,b,s0,top,K,MUL,hx,budget,trail)` | `scripts/12_b5_budget.py`（impl `f2cb54fa…`） | 唯一之成本／值來源 |
| I2 | K 表、62 軸、h 表 | `scripts/12` `load_machine`／`load_inputs`（＝`scripts/09` impl `d8037bb1…`） | 點集與值 |
| I3 | 62 settings（id 序） | `data/04_b2_settings.json`（B2 凍結） | 點集之標籤 |
| I4 | 預算 `61.5 = 123/2`、`E_min = 123/176`、每讀成本 `123/88` | B5 `docs/07`（impl `f2cb54fa…`） | 終止條件 |
| I5 | 命中律（成本 = 3 − [入頂 = a] − [b = a]） | D6 `docs/13` §1 P2a/P2c（機器 impl `a681ae8c…`；審計 `scripts/19` A4 33/33） | P1 之閉式律 |
| I6 | B3R2 統計量 `feasible_chsh`／`simulate`／`order_list`／`build_anti`、可構成性判據（2×2 矩形）、`all4` 定義 | `scripts/15_b3r2_orderfair.py`（impl `14e17e7c…`） | P5／P6 之判據與定義 |
| I7 | E2 之 memo 命中有效表 `C2`（den = 3） | `data/09_a2_correlation.json`（A2 凍結） | P5 之值來源 |
| I8 | 對蹠表 `anti` | 由 I2 之軸向量精確重算（`build_anti`） | `all4` 之剔除 |

## §2 圖定義（凍結，唔准見數後改）

- **點集** `V`：62 個 settings，標籤取 I3 之原序。
- **邊集** `E`：有序對 `(a,b)`，`a ≠ b`；`|E| = 62·61 = 3782`。（**唔含 loop**——loop 屬 B3R2 之對角污染類，另立為診斷。）
- **成本律**（P1 之對象，須逐格驗；凍結形式 = `3 − [t = a] − [b = a]`）：第 `i` 條邊 `e_i = (a_i, b_i)` 之讀數
  `cost(e_i) = 3 − [t_i = a_i] − [b_i = a_i]`，其中 `t_i` = 入場 ledger 頂（`i = 1` 時 `t_1 = −1` 表空 ledger）；
  且 `t_{i+1} = b_i`（D6 命中律）。**例外須列出**（尤其 `t = a = b` 之「種子被 pop 吃掉」情形）。
- **Eulerian 電路**：一條遍歷每條邊**恰好一次**之閉路（有向）。
- **次序**：一條邊序列。**可行前綴**＝在 §1 I4 之預算與 per-read 終止條件下、由凍結機器實際接受之最長前綴。
- **公平度**（P6）：前綴內每點之 `(out, in)`；公平度量 = `max_v |out(v) − in(v)|`。

## §3 三條定理（本輪要驗；唔准只驗容易嘅一邊）

- **T1（存在）**：完全有向圖（無 loop）每個點 `in = out = n − 1 = 61` ⟹ 強連通且平衡 ⟹ Eulerian 電路存在。
- **T2（最優）**：
  (i) 每條邊之成本 `≥ 2`（除退化 `t = a = b` 之外；本輪邊集無 loop）；
  (ii) Eulerian 電路之每條**內部**邊成本 `= 2`（因 `t_i = b_{i−1} = a_i` ⟹ 首個 read 命中）⟹ 全電路讀數 `= 3 + 2·(3782 − 1) = 3 + 7562 = 7565`；
  (iii) 等號成立 ⟺ 次序 Eulerian（每一步皆命中 ⟺ 每一步 `t_i = a_i` ⟺ 連續邊首尾相接 ⟺ Eulerian）。
- **T3（非唯一，BEST）**：Eulerian 電路數（固定起點）`= t_w · ∏_v (deg⁺(v) − 1)!`；完全有向圖（無 loop）`t_w = n^{n−2}` ⟹ `EC = n^{n−2}·((n − 2)!)^n`。
  `n = 62` 時以 **exact 大整數**報；並以 `n = 3, 4` 之**暴力枚舉**獨立驗 BEST 之適用性（含 arborescence 暴力計數）。

## §4 六格判據（每格報值 ＋ ✅／🟡／🔴）

- **P1 成本律**：對全部 `(t, a, b) ∈ {−1} ∪ V × V × V`（＝ 1 + 62³ = 238,329 格）以**凍結機器**實算 vs §2 律。
  判據：`matches / total`；例外逐條列出並歸類。
- **P2 Eulerian 構作**：以 **Hierholzer（canonical tie-break = 最小 index，寫死）**構作；驗 ①閉路 ②每邊恰好一次（3782/3782）③連續性 `b_i = a_{i+1}`。
- **P3 最優性**：(i) 由 P1 表取 `min`；(ii) 實算電路總讀；(iii) 以 `n = 3` 之**全排列枚舉**（6! = 720）驗「達最優 ⟺ Eulerian」。
- **P4 非唯一**：`EC(62)` exact；`n = 3, 4` 暴力 `EC` 與 BEST 對比；`t_w` 以矩陣樹（有向）暴力驗 `n = 3, 4`。
- **P5 可構成性**：(a) canonical 前綴之矩形判據 ＋（若可構成）`all4` 值；(b) **存在性**：構作一條 Eulerian 電路，其前綴含 2×2 矩形（含殘圖仍 Eulerian 之證明），並計其 `all4` 值。兩者皆報。
- **P6 公平性**：canonical 前綴之 `max_v |out − in|`（定理：Eulerian 前綴必 `≤ 1`），並與 B3R2 五家族前綴**同一定義**並列。

## §5 盲測窗與預註冊

1. **未見數前唔准填**：P1 之例外清單、P3 之 `min`、P4 之 `EC(62)` 數值、P5(a)/(b) 之可構成性與值、P6 之公平度。
2. **寫死之選擇**（見數前）：邊集無 loop；tie-break = 最小 index；起點 = 最小 index 且在電路中取「以 (0,1) 為首邊」之旋轉；公平度定義如 §2。
3. **統計量**：若 P5 可構成，用 I6 之 `feasible_chsh(M=C2 num, den=3, mode='all4', pref, anti, ids)`——**逐字**沿用，唔准改判準。
4. 見數後任何改動 ⟹ §7 amendment ＋ 重凍 ＋ 首跑 log 保留。

## §6 禁區

- 唔准自創語義、唔准改邊集／tie-break／判據／統計量（見數後）。
- 唔准重寫凍結機器：**只可 import**（`scripts/12` 之 `run_pair`／`load_machine`／`load_a2`；`scripts/15` 之統計量）。
- 唔准把「Eulerian 類」之結論講成「唯一次序」。
- 唔准在本輪重推 CHSH：P5 之值必須與 I6 之定義**逐字一致**。
- 唔准寫入本目錄以外之任何檔案（register／README 之狀態行除外）。

## §7 Amendment 記錄

| # | 日期 | 內容 | tighten／loosen | 值有無變 |
|:--|:--|:--|:--|:--|
| A1 | 2026-09-30 | **impl-only**：① `sys.set_int_max_str_digits`（`EC(62)` 有 5187 位，Python 預設上限 4300）② P4 之 BEST↔暴力**約定**修正（BEST 固定首邊；由 w 出發之邊序列 = BEST × outdeg(w)）。兩者皆屬實作，**謂詞與判據不變**、值不變；重凍（impl `b8dbc594…` → `efa6aade…`）；首跑 log 保留 2 份（`logs/21_g4_firstrun_int_str_limit.out`、`logs/21_g4_firstrun_convention_mismatch.out`）；前次 freeze 記錄保存為 `data/20_g4_freeze_pre_amendment_a1.json` | — | 無 |

## §8 預期失敗模式（見數前寫低，防止事後合理化）

1. 成本律若有例外（如 `t = a = b`），**唔准**改律去遷就 —— 例外即結果（並須說明該情形喺本輪邊集可否出現）。
2. 若 canonical 前綴**唔**可構成，**唔准**換 tie-break／換旋轉去救 —— 換法即 §5 之見數後改動，須 amendment。
3. 若 `EC(62) = 1`（不可能但須驗）⟹ 才可講唯一；否則只可報類。
4. 若 T2(iii) 之小例子（`n = 3`）出現**非** Eulerian 之最優者 ⟹ T2(iii) 被否證，如實報。
