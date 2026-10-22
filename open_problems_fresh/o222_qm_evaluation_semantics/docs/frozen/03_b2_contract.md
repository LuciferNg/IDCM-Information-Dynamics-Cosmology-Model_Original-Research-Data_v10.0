# O222 docs/03 — B2 / B1 / B4 合約（Contract v1，凍結）

> **狀態**：🔒 **凍結（frozen）** — 於任何 C(θ) 數字被計算之前寫定
> **凍結附證**：`data/04_b2_freeze.json`（內含 settings 表 hash、本檔 hash、enforcer hash、時間戳）
> **強制者**：`scripts/04_b2_contract.py`（可執行；跑得到 = 合約有效，跑唔到 = 唔准跑 B2）
> **適用判準**：R1 凍結語義（`docs/02`：force 單值 + memo；C1 = Aut 破缺／穩定子）

---

## §0 為何要有合約（三個鎖，對應調律者三點）

| 鎖 | 對應裁定 | 機械保證 |
|---|---|---|
| **L-SET** | ① Setting 表 + 盲測窗強制凍結 | 62 個**精確晶格軸**枚舉 + 全 3844 有序對全掃（**無選點**）；分割 DEV 144 / BLIND 3700 + hash 承諾 |
| **L-ZERO** | ② 零參數硬約束 | C 之唯一定義 = 群元素重疊分佈；AST 掃描禁 `cos/sin/tan/π/numpy/scipy` 入 kernel；**對 −cos θ 之比較用精確代數平方關係**（連比較都唔用三角） |
| **L-CAUSAL** | ③ B1 前提判別 + B4 無信號先決鎖定 | 因子表局部性（remote setting 唔准入 local kernel）+ 聯合分佈可行性嘗試 + ablation（獨立抽樣 ⟹ C = 0）+ marginal = 1/2 **結構推導**（非假設） |

★ **核心紀律**：**曲線吻合 = 群論／幾何嘅勝利；唔吻合 = 底層拓撲映射要修** —— 兩者都唔准回頭調參。
**任何**超參數／定義／grid 改動 ⟹ 合約 version +1、新 hash、新 doc、並在 register 明寫「moving goalposts」。

---

## §1 L-SET：操作空間封死（Setting 表）

### 1.1 Setting = 晶格原生軸（精確，零三角）

Setting 集合 **唔係** 人選角度，而係 **R1 導出嘅 62 條晶格原生軸**（`scripts/03` 規則：群元素階 5 → 頂點線，階 3 → 面心線，階 2 → 邊中點線）：

| 類 | 線 | 定向 | ID 規則 | 枚舉次序（凍結） |
|---|---|---|---|---|
| 頂點 5 重軸 | 6 | 12 | `V00`–`V11` | 定向提升後 sorted |
| 面心 3 重軸 | 10 | 20 | `F00`–`F19` | 同上 |
| 邊中點 2 重軸 | 15 | 30 | `E00`–`E29` | 同上 |

- **θ 唔係輸入**：setting 係軸本身；軸間角嘅 cosine 由精確內積得出（`cos θ = u·v / (|u||v|)`）。
- **掃描範圍（凍結）**：**全部 62 × 62 = 3844 有序對**（`a`, `b`）。**無子集選擇、無「代表性角度」**。
- **相關函數取三種 type 分解全報**：V×V（144）、V×F、V×E、F×F、F×E、E×E —— 每個 class 之統計（mean、max|C|、與 cos² 之代數差）逐類報，唔准只報最好嗰類。

### 1.2 凍結之枚舉次序（防止「換個排序就換個 max」）

軸清單 = `V` 全集（sorted 12）+ `F` 全集（sorted 20）+ `E` 全集（sorted 30）；索引 = 清單位置（0..61）。
CHSH 之 4-tuple 掃描 = **枚舉次序下全部 4-tuple**（報告 max 及 argmax），唔准事後換次序。

---

## §2 L-SET：盲測窗 + 分割 + 超參數凍結表

### 2.1 分割（凍結）

| 集 | 內容 | 對數 | 用途 |
|---|---|---|---|
| **DEV** | `V×V` 全 144 對 | 144 | 開發／單元測試機制（**唯一可見集**） |
| **BLIND** | 其餘 3700 對（V×F、V×E、F×F、F×E、E×E、以及反向序） | 3700 | 凍結後才揭示；**值唔准在 freeze 前打印** |

### 2.2 誠實界定「盲」（唔虛報）

同一 session 內部冇真正資訊隔離 ⟹ 盲測靠**三重替代保證**，逐項可核：
1. **Code-hash 承諾**：`scripts/05`（實作）之 SHA-256 在跑任何 C 值**之前**寫入 `data/04_b2_freeze.json`；跑完後 hash 一變 = 整輪作廢。
2. **零參數**：定義內**冇**任何可調參（見 §3）⟹ 冇「調」嘅空間，得「改定義」——後者要 version bump + 宣告。
3. **全報告**：3844 對全數入文檔／JSON（`data/05_b2_correlation.json`），**唔准只報一部分**；盲集值另存 `data/05_b2_blind_values.json`，只需與 DEV 集一齊報。

### 2.3 超參數凍結表（**寫死值，跑前定**）

| # | 超參數 | 凍結值 | 備註 |
|---|---|---|---|
| H1 | 群測度 w(g) | **uniform on 2I（120）為主**；uniform on I（60）為對照 | 兩者皆報；主對照分歧 = 訊號 |
| H2 | 二值化規則 | `O = sign(u·(g n̂))`，精確代數比較 | 無浮點 |
| H3 | 平局規則（`u·(g n̂) = 0`） | `O = sign(首個非零分量 of (g n̂))`；平局數獨立報 | 平局係 diagnostic，唔入分子 |
| H4 | 參考軸 `n̂` | 軸清單索引 0（`V00`） | 凍結；另報全 12 頂點作 robustness |
| H5 | C 之定義 | `C[a][b] = Σ_g w(g) K(g,a) K(g,b)` | 見 §3 |
| H6 | QM 比較量 | **精確平方關係**：`C[a][b]²` ≟ `cos²θ(a,b)`（∈ Q(√5)） | 連比較都唔用三角 |
| H7 | 符號約定 | 報 \|C\| vs \|cos θ\|；符號圖另報 | singlet 全域負號係約定，非內容 |
| H8 | CHSH 視窗 | `S ≤ 2 + 1e−12` = LHW-class；`\|S − 2√2\| ≤ 1e−9` = QM-like；否則 = 第三結構值 | 三值皆報精確值 |
| H9 | Null（隨機軸） | 10⁴ draws，**seed = 222** | 取代 2I 為同基數隨機單位四元數集 |
| H10 | Null（獨立抽樣） | `g_a ⟂ g_b` → 期望 `C = 0` EXACT | 通訊歸因測試（§5） |
| H11 | 聯合分佈可行性 | 精確線性可行性（Fraction / 整數 LP），枚舉 setting 子集由小到大 | B1 之機械內容（§4） |
| H12 | 最小不可行子集 | 報**最小基數**之 infeasible 子集 + 全部同基數者 | 唔准只報一個例子 |

**改動 H1–H12 任何一項 = 合約 v2**（require: 新 doc、新 hash、register 記 moving-goalposts）。

---

## §3 L-ZERO：零參數硬約束（C 之唯一定義）

### 3.1 定義（唯一，寫死）

```
K(g, a) = sign( u_a · (g n̂) )                      # ±1，精確代數；g ∈ 2I；u_a = setting a 之軸
C[a][b] = Σ_{g ∈ G} w(g) · K(g, a) · K(g, b)        # G = 2I（主）/ I（對照）
```

- 全部輸入 = **群元素 + 軸內積**，冇三角、冇擬合補丁、冇自由參數。
- 軸間角**只**在比較階段以代數方式出現：`cos²θ(a,b) = (u_a·u_b)² / (|u_a|² |u_b|²) ∈ Q(√5)` —— **精確**，唔經浮點。
- **Hard ban（AST 強制，見 §7）**：kernel 函數內出現 `cos/sin/tan/acos/atan/pi`、`numpy/scipy`、或 `0.7071067811865476 / 1.4142135623730951` 等常數 ⟹ 合約 FAIL，禁止出數。

### 3.2 唔准嘅三件事（明文）

1. **禁** 在任何地方寫死 `-cos θ`、`2√2`、`0.7071…` 作為輸出或中間量。
2. **禁** 為匹配 −cos θ 而改 kernel 形式（改 = 新 contract version + 宣告）。
3. **禁** 事後揀 setting／子集／type class 令曲線好睇（§1.1 全掃 + 全報）。

---

## §4 L-CAUSAL (B1)：CF-definiteness 之違背必須純由 ledger 造成

三項機械檢查（`scripts/05` 必須全部通過，`scripts/04 --freeze-impl` 先驗前兩項之靜態形式）：

1. **因子表局部性（靜態，AST）**：C 必須由**單 setting 因子表**組裝 —— `K` 表逐 setting 一次算好（函數參數**只准一個 setting**，函數體內**唔准**出現第二 setting 之名）；配對階段只可乘兩個單 setting 表。remote setting 出現喺 local 分支 ⟹ FAIL（= 隱含通訊）。
2. **聯合分佈可行性嘗試（動態，精確 LP）**：對 setting 子集 S，嘗試構造 joint signed measure over outcome assignments；由 |S| = 2 起逐級增大，報**最小 infeasible 子集**（基數 + 全部同基數者）。**必須真跑**，唔准以「Bell 定理話唔可能」代替。
3. **歸因**：若採 sequential（rollback）級 C 並出現 CHSH > 2，超額**必須**歸因到 R1 之 ℓ ≥ 3 Aut-破缺 sector（rank-3 octupole ctx，`|Stab_I| = 1`），並附該 sector 之貢獻分解；唔可以只講「因為量子」。

★ B1 之實質命題（凍結表述）：**反事實確定性喺 lazy 語言中類型級不成立**（未強制之 thunk 冇值；換 ctx = 換 thunk，R1 A3）；
但「唔成立」本身唔會給出 > 2 —— 要 > 2 需要**相異 setting 之讀取算子不能共存**（同一 thunk 只能有一個 memo 值）。

---

## §5 L-CAUSAL (B4)：無信號（需推導，唔准假設）

1. **marginal 結構推導（已於 contract 執行時驗證）**：單翼 marginal `P(O_a = +1) = 1/2` **EXACT** ∀ 62 軸。機制：二十面體**中心對稱**（`v ∈ V ⟹ −v ∈ V`）⟹ 任一方向 6 正 / 6 負；乘 I-軌道重數（12 方向 × 重數 5 = 60）⟹ 30 / 30 精確。
   - **平局唔准當無事**（H3 實測）：三類軸之 `Σ_v sign(u·v)` = **0 / 0 / 0**；edge 軸恰 **⊥ 4 個 vertex 方向**（vertex／face 軸 = 0 個）⟹ 平局數 = 4 × 5 = **20 / 軸**。
   - 用 H3 規則**指派**平局符號（唔係排除）後，12 refs × 62 軸 × 60 rotations：**7200 平局事件、0 軸不平衡** ✓ ⟹ `P = 1/2` 包含平局仍然 EXACT。
   ⟹ **marginal 與對手 setting 無關**係結構後果，唔係加設條件。
2. **ablation（通訊歸因）**：將共享群元素改成兩翼獨立抽樣（H10）⟹ `C ≡ 0` EXACT。若 C 仍顯著 ⟹ 相關性來自隱含通訊 ⟹ **路線死**（記錄為負結果，唔准救）。
3. **禁循環**：引用 QM 之 no-signalling、Tsirelson bound、Born 律作輸入 ⟹ FAIL；所有輸入只准 R1 凍結語義 + 群結構 + §1 之 setting。

---

## §6 預先註冊之結構預期（**跑之前寫死**）

| # | 量 | 結構預期（現時凍結） | 由何結構推得 | 判別 |
|---|---|---|---|---|
| P1 | `P(O_a=+1)` | **= 1/2 EXACT** ∀ a（62 全掃；**含 H3 平局指派**：7200 tie events、0 不平衡） | 二十面體中心對稱 6/6 × 軌道重數 5；edge 軸 ⊥ 4 vertex 方向 ⟹ 20 平局／軸 | 全 grid；任何偏離 = 結構錯 |
| P2 | `C`（coexistence 級） | 確定性函數 of 單一共享 g ⟹ **CHSH ≤ 2 EXACT** | Bell 不等式對 LHV 之定理（此處 g = 共享隱變量） | 若 > 2 ⟹ factor 結構被破（= 實作 bug），唔係物理 |
| P3 | `C`（sequential／rollback 級） | 容許 > 2；**超額須歸因 ℓ≥3 sector**；數值本身由群結構決定 | 相異 setting 之讀不可共存（memo 單值） | 歸因測驗（§4.3）+ marginal 仍 = 1/2 |
| P4 | QM 比較 | `\|C\|` vs `\|cos θ\|` 之代數差（精確）；**RMS 門檻 1e−9**（無容忍擬合） | H6 | 全 3844 對報告 |
| P5 | 隨機軸 null | 無結構（分佈報告） | H9 | 10000 draws |
| P6 | ablation | `C ≡ 0` | 獨立抽樣 ⟹ 無共享 | 精確 |

⚠️ P3 之**數值**刻意留白（跑完才知）—— 但**機制歸因要求**已寫死；若跑出 > 2 而歸因唔到 ℓ≥3，判 🔴 未閉合。

---

## §7 執行順序（閘，唔可跳）

```
1. 跑 scripts/04_b2_contract.py            → 設定表 + hash + 分割 + marginal 結構驗證（P1）+ AST 掃描自測
2. 寫 scripts/05_b2_correlation.py         → 實作 §3 定義（kernel 表 → C 表 → CHSH → 比較）
3. 跑 scripts/04 ... --freeze-impl scripts/05_b2_correlation.py
   → AST 硬檢查（禁三角／禁 numpy／因子表局部性）+ 寫入 impl hash 到 freeze JSON
   ★ 此刻起 scripts/05 任何一個 byte 改動 = 整輪作廢
4. 跑 scripts/05（DEV 集出數；BLIND 集寫檔唔打印）
5. 揭示 BLIND → 全 3844 對報告 → §6 預期逐項核 → 記 register
6. 任何超參數／定義改動 → contract v2 + 新 hash + moving-goalposts 宣告，舊輪結果作廢
```

**閘之否決規則**：scripts/04 任何 `[FAIL]` ⟹ 禁止跑 scripts/05；imp hash 遺失或被改 ⟹ 禁止揭示 BLIND。

---

## §8 檔案清單

| 檔案 | 角色 |
|---|---|
| `docs/03_b2_contract.md`（本檔） | 合約正文（凍結） |
| `scripts/04_b2_contract.py` | 合約強制者（settings 凍結 + hash + AST 封鎖 + P1 結構驗證） |
| `data/04_b2_settings.json` | 62 軸 setting 表 + 3844 對之精確 cos² 表 |
| `data/04_b2_partition.json` | DEV / BLIND 分割（索引級） |
| `data/04_b2_freeze.json` | 凍結附證（各 hash + 時間戳 + 規則版本） |
| `scripts/05_b2_correlation.py`（待寫） | §3 定義之實作（**未存在前，閘顯示 WAITING**） |

---

## §9 修正記錄（amendments，全部在**任何 C(θ) 數字存在之前**）

| # | 時間 | 內容 | 是否改動 H1–H12 | 重凍 |
|---|---|---|---|---|
| A1 | 2026-09-29 | §5.1 由「平局另報」升級為 **H3 平局指派後之平衡驗證**（P1b 正式檢查）；加 edge 軸 ⊥ 4 vertex 之結構診斷；tie_audit 寫入 settings artefact | **否**（只加檢查，未改任何超參數值） | ✅ 重跑 scripts/04 並重寫 hash |

> 之後**任何** H1–H12 之改動一律 = Contract v2（新 doc + 新 hash + register 記 moving-goalposts），舊輪結果作廢。
