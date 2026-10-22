# O222 — B3 第二輪合約（B3R2 v1）：資源界限**內**之公平讀取分配

> **規則版本**：`b3r2-contract-v1` · **凍結日**：2026-09-29 · **狀態**：本檔先於任何數字寫死（合約鐵律）
> **上游凍結**：`docs/07_b5_contract.md`（B5 v1 + A1–A6）· `docs/05_a2_contract.md`（A2 v1 + A1–A9）· `docs/03_b2_contract.md`（B2 v1）
> **register**：`O222/B3R2`（+ 子問題 Q1–Q4 之 note，**見數前**註冊）

---

## §0 範圍與聲稱上限（先寫死）

**問**：B5 已證：凍結字典序（`62a + b`）之下，44 讀預算之可行前綴**全屬 `a = 0`** ⟹ **冇任何 `a ≠ a′` 之 4-tuple** ⟹ Bell 型統計量**無法構成**，`|S| ≡ 0`；而 A2 之 `|S| = 3` 需 **174.7× 預算**。

**本輪問**：若把同一 **44 讀**預算改為**公平覆蓋之讀取分配**（order rule 家族，見 §2），Bell 型統計量**可否構成**？構成後之**精確值**為何？其**判定力**（null）與**前提完整性**如何？

**聲稱上限（不變，鐵律）**：
1. **唔**宣稱導出 QM／ħ／Hilbert 公理／Born 律。
2. **唔**稱「量子非局域」、**唔**稱「晶格導出 CHSH 違反」。
3. 若某 order 下預算可行 `|S| > 2`，**必須**同時通過 ① no-signalling ② ablation ≡ 0 ③ 歸因 三者，方可稱 **history-mediated contextuality（史誘發語境性）**；否則只能如實報 LHV-class。
4. **禁止**：見數後新增／刪除 order、改判據、只報部分家族、為救結果調次序。

---

## §1 凍結輸入（I1–I8，全部附所有者；**零參數可調**）

| # | 輸入 | 值／來源 | 所有者 |
|:-:|:---|:---|:---|
| I1 | 每 pass 能量預算 | `61.5 = 123/2` EXACT | O41 |
| I2 | Landauer 下限 | `E_min = 123/176` | O41 |
| I3 | **實際讀成本** | `ΔE_read = B(n) = 123/88 = 2·E_min` | O41 + O206（`ω_n = μ²`）|
| I4 | 每 pass 可行讀數 | `(123/2)/(123/88) = 44 = N_d`（`τ_deco = 2` 個此類 pass）| O126（讀 = 寫 = N_d）|
| I5 | **機器語義** | L-SEQ：`read(G, ctx)` + memo 命中律 + `rollback`／`reconcile` —— **以 `scripts/09_a2_rollback.py` 為唯一權威**（本輪 **import**，唔重寫）| 本 O（A2 凍結）|
| I6 | 每讀終止條件 | **per-read**：`B_rem ≥ E_min` 才可讀；唔足即停（B5 A5）| 本 O（B5）|
| I7 | 62 條晶格原生軸 ＋ `h` 表 ＋ 兩張估量器表 | `data/04_b2_settings.json`（軸向量，Q(√5)）· `data/08_a2_h_table.json` · `data/09_a2_correlation.json`：**E1 = `C1_num`（den 120，閉式）**、**E2 = `C2`（memo 命中有效表，den 3）** | 本 O（B2／A2）|
| I8 | 時期結構 | `p_k ≡ 均勻`（A3：max L1 dev = 0）⟹ 四時期讀取**塌縮**為單一表（E1／E2 之差 = memo 有效表 vs 閉式）；**此為引用既有凍結結論，非本輪新語義** | 本 O（A2 之 A3）|

⚠️ **I8 之誠實聲明**：本輪**唔**重推 `p_k`；`C2` 表直接取自已凍結之 A2 產物。若日後 A2 之 `C2` 表被修訂，本輪需重跑。

---

## §2 Order 家族（**見數前寫死；全部必須報告**）

pair 索引 `(a, b)`，`a, b ∈ 0..61`。五條 order（各為 pair 集上之**全序** ⟹ 每個 k 之可行前綴唯一）：

| ID | 名 | 排序鍵 | 結構意圖 |
|:-:|:---|:---|:---|
| **O1** | `lex` | `(a, b)` | **凍結基線**（A2／B5 之字典序；預期前綴全 `a = 0`）|
| **O2** | `diag` | `((b − a) mod 62, a, b)` | 對角優先（`a = b` 先）|
| **O3** | `antidiag` | `((a + b) mod 62, a, b)` | 反對角優先 |
| **O4** | `block` | `(max(a,b), min(a,b), a)` | 塊狀（低 max 優先）|
| **O5** | `stride` | `((b − 13a) mod 62, b, a)` | 固定模步長 13（`gcd(13,62)=1` ⟹ 雙射）|

**結構判據（預先註冊，唔准事後改）**：對 order `O` 之可行前綴 `P`（由 I5+I6 之機器**實算**成本得）：
- `cov_a(P) = |{a : ∃b, (a,b) ∈ P}|`、`cov_b(P) = |{b : ∃a, (a,b) ∈ P}|`
- **可構成（constructible）** ⟺ `cov_a(P) ≥ 2` 且 `cov_b(P) ≥ 2` ⟺ ∃ 4-tuple 滿足 `a ≠ a′`、`b ≠ b′`。

⚠️ 判據係**組合／結構**條件（覆蓋度），**唔**含任何取自 CHSH 值之訊息 ⟹ 冇 cherry-picking 空間。

---

## §3 統計量（全部必須報告；精確有理；**全枚舉**）

1. 每個 order：**可行前綴** `P`（`k` 對、累計讀數、每對實算成本、`cov_a`／`cov_b`、終止 pair）。
2. **預算可行 CHSH**（權威數字，**全量枚舉**）：對 class ∈ {`raw`, `distinct`, `distinct_anti`, `all4`} 與估量器 ∈ {E1, E2}：
   - 域 = 四項之**四個 pair 全部落在 `P` 內**之 4-tuple（`a, a′, b, b′`），class 之約束與 A2 `scripts/10` **逐字相同**；
   - `S = M[a][b] − M[a][b′] + M[a′][b] + M[a′][b′]`；報 `max |S|` ＋ argmax（E1 用 `C1_num/120`、E2 用 `C2`）。
   - **若域為空** ⟹ 報「**無法構成**」（唔報 0 當作量度結果）—— 兩者必須分開標示。
3. **無限制基線**（交叉核對用）：同一 order 家族在**無預算限制**（全 3844 對）下之值，必須重現 A2／B5 之 8 個值 = `{raw 4, distinct 4, distinct_anti 4, all4 2(E1)/3(E2)}`。
4. **null（隨機軸標籤）**：每個 order `D = 100` draws，每 draw 抽一個 `π ∈ S_62`（文件化之 splitmix64，seed 註冊）**重跑整條管線**（成本 → 前綴 → CHSH），報 `median`／`max`／**達 ≥2 之比例**（`p` 值判據：`p ≤ 0.05` 才算顯著）。
5. **診斷**：`cov_a`／`cov_b` 對 `k` 之曲線；每對成本直方圖。

---

## §4 前提完整性與三檢查（Q4）

| 檢查 | 硬要求 |
|:---|:---|
| **marginal** | 每個 setting 之 marginal = **1/2 EXACT**（E1／E2 皆報）|
| **ablation** | 兩邊獨立抽樣 ⟹ `C ≡ 0` EXACT |
| **no-signalling** | 一邊之 marginal 與另一邊 setting 無關（精確檢查）|
| **歸因** | 若 `> 2`：必須指明貢獻之 pair／rank；歸因唔到 ⟹ 🔴 未閉合 |
| **Δ_order** | `max|C1[a][b] − C1_rev[a][b]|`（序作用診斷）照舊報 |

---

## §5 執行閘（唔可跳）

```
1. 跑 scripts/14_b3r2_contract.py            → 輸入 hash pin + order 家族雙射檢查 + 判據自檢 + AST 封鎖（禁 cos/sin/tan/pi/sqrt/exp/log、numpy/scipy/math/random、非整數浮點字面值、變數名 pi/log）
                                             → 寫 data/14_b3r2_freeze.json
2. 跑 scripts/14 ... --freeze-impl scripts/15_b3r2_orderfair.py
                                             → AST 硬檢查 + impl hash 寫入 freeze
   ★ 此刻起 scripts/15 任何一個 byte 改動 = 整輪作廢
3. 跑 scripts/15                             → 出數（權威）＋ null ＋ 三檢查 → data/15_b3r2_results.json、logs/15_b3r2.out
4. 記 register（O222/B3R2）
```
**閘之否決規則**：`scripts/14` 任何 `[FAIL]` ⟹ 禁止跑 `scripts/15`；impl hash 遺失／被改 ⟹ 整輪作廢。

---

## §6 禁區（合約鐵律）

1. **唔准**見數後新增／刪除 order、改判據、改 class 定義。
2. **唔准**只報「靚」嘅 order；**五個全報**，包括基線（預期全部「無法構成」亦要報）。
3. **唔准**把「域為空」寫成 `|S| = 0`（兩者必須分開）。
4. **唔准**用加速器取代全枚舉作權威值；加速（若有）只作交叉核對，且要求逐值相同。
5. **唔准**由本輪結果反推 I1–I8（輸入全部來自已凍結之上游）。
6. 一切 `> 2` 之主張須附三檢查；否則如實報 LHV-class。

---

## §7 結構缺口（登記，唔自創）

| # | 缺口 | 狀態 |
|:-:|:---|:---|
| G1 | D5 觸發所需 `ctx → s` 映射唔存在於凍結記錄 | 🔴 仍開（**禁自創**）|
| G2 | 逐模頻率 `f(n)`（O206）⟹ 讀成本均勻 | 🔴 上游 |
| **G4（本輪新）** | 「公平分配」在 IDCM 結構上有冇**唯一**之 order（例如由 `h` 表／群結構導出）？本輪之五條 order 係**人為家族**，只證「存在性／可行性」，**唔**證唯一 | 🔴 登記（本輪**唔**解）|

---

## §8 檔案清單

| 檔案 | 角色 |
|:---|:---|
| `docs/10_b3r2_contract.md`（本檔） | B3R2 合約正文（凍結）|
| `scripts/14_b3r2_contract.py` | 合約強制者（hash pin + 雙射檢查 + AST 封鎖）|
| `scripts/15_b3r2_orderfair.py` | 機器（成本 → 前綴 → 全枚舉 CHSH → null → 三檢查）|
| `data/14_b3r2_freeze.json`、`data/15_b3r2_results.json` | 凍結附證／結果 |
| `logs/15_b3r2.out` | 執行日誌（權威）|
| `docs/11_b3r2_results.md` | 結果報告 |

---

## §9 修正記錄（amendments）

| # | 時間 | 內容 | 是否改動 §2–§4 | 重凍 |
|:-:|:---|:---|:---|:---|
| A1 | 2026-09-29 | **缺陷修正**：§2 原寫「`cov_a ≥ 2` 且 `cov_b ≥ 2` ⟺ 存在 4-tuple」。**此等價為假**（機器首跑否證：`stride` 前綴 `cov_a = cov_b = 15` 但**無**任何合法 4-tuple —— 該前綴係 `a ↦ b` 之雙射，任何 `(a,i),(a₂,i)` 同在前綴即逼 `a = a₂`）。修正後判據 = **直接計算存在性**（枚舉即得），`cov_a`／`cov_b` 降為**診斷量**（照報）。**class 定義、order 家族、統計量、null 參數（D = 100）全部不變**；**任何已報數值不受影響**；修正方向為**收緊**（承認可構成之 order 更少），非放寬。 | 否（僅 §2 判據陳述） | **是**（impl 需重凍；首跑 log 保留為 `logs/15_b3r2_firstrun_contract_defect.out`）|
