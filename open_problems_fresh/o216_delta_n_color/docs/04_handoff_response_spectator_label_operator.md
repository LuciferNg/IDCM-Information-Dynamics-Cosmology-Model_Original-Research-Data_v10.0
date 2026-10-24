# O216 docs/04 — 對 M4 入站 handoff 之答覆：標籤層 spectator 依賴算子

> 日期：2026-10-24｜性質：**入站 handoff 答覆**（非新推導、非 reopen）
> 來源：`v11.0/M4` — `main_problems/m4_mass_spectral_readout/docs/20_identifiability.md` §六
> register 事件：`2026-10-24T13:50:13+08:00 handed_off M4 → O216`（非轉交產權）
> 本 O 狀態：🟢 closed（不變）

## 一、接收列舉（三條命令，2026-10-24）

| 檢查 | 結果 |
|:--|:--|
| `register.py status --pid O216` | `incoming (1 addressed to O216)` ← 本條 |
| `register.jsonl` 全事件掃描 | 6 條：registered×2、closed×2、conclusion×1、handed_off×1（本條） |
| 跨 O 目錄 grep `O216`（排除自身） | **0 命中** — 無其他 O 以檔案形式提及 |

分流：本條 = **請求輸入**（問標籤層有冇 spectator 依賴算子），唔係新開放問題、唔係更正要求 ⟹ 以 note 答覆，唔開新 pid、唔改 M4 任何檔案。

## 二、來源 claim 核實（先核數，後判）

M4 引述之 8 通道 em 讀數，用其定義 `Δm = Σ(m_final − m_initial)·coeff + E`、外部固定 `X = m_d − m_u = 2.56 MeV`（FLAG24）逐條重算（零 import M4 script，`Fraction` 精確）：

| 通道 | Δm (MeV) | coeff | E 重算 | M4 claim | 判 |
|:--|--:|--:|--:|--:|:--|
| n−p | +1.2933 | +1 | −1.2667 | −1.2667 | ✅ |
| K⁺−K⁰ | −3.9340 | −1 | −1.3740 | −1.3740 | ✅ |
| π⁺−π⁰ | +4.5936 | +1 | +2.0336 | +2.0336 | ✅ |
| Σ⁻−Σ⁰ | +4.8070 | +1 | +2.2470 | +2.2470 | ✅ |
| Σ⁰−Σ⁺ | +3.2720 | +1 | +0.7120 | +0.7120 | ✅ |
| Σ⁻−Σ⁺ | +8.0790 | +2 | +2.9590 | +2.9590 | ✅ |
| Ξ⁻−Ξ⁰ | +6.8500 | +1 | +4.2900 | +4.2900 | ✅ |
| D⁺−D⁰ | +4.8200 | +1 | +2.2600 | +2.2600 | ✅ |

**8/8 PASS（dev = 0，4dp）**。A 組 spread = 0.1073（claim 0.107 ✅）；B 組 spread = 3.578（claim 3.578 ✅）；E 全域跨度 = 5.664 MeV（claim 5.66 ✅）。

⟹ M4 觀測硬事實成立：同一 u→d 取代，spectator 由 {u,d}/s̄ 換到 {d,s}/{u,s}/{s,s}/c，E 由 −1.32 變到 +0.71…+4.29。**加性預言（每 flavour 一權重相加 ⟹ 同取代 E 全等）被數據否證。**

## 三、判定：🔴 標籤層冇 spectator 依賴算子（範疇性）

**答案：冇，而且唔可能有。** 三條結構理由：

### R1 — 標籤 ≠ operator（O216 no-go 之直接推論）
本 O 已證（docs/03）：鏈長族 ℳ = 2^a·11^b，**3 ∤ 88/44/176 ⟹ 無 Z₃ 扇區**；色荷冇鏈層 eigenvalue 可言，只能作規範嵌入層**標籤**（SU(3)_c 表示論 label，同角色 σ_g 一層，O209 docs/10、O67）。
標籤層嘅內容 = 表示 label 嘅**多重集**——冇 Hamiltonian、冇譜、冇 operator algebra。要求「標籤層嘅 operator」= 範疇錯誤（operator 須有作用空間；label 只係 index）。

### R2 — 標籤層任何良定義量恆等可加
標籤層最一般嘅量 = 多重集函數；對 label 求和／對稱化後，任何**單標籤可測**泛函都化為 `Σ_i w(label_i)`（逐 label 權重和）。即標籤層算子（如有）恆等**加性**。
M4 C2c 已用數據否證加性類（B 組 spread 3.578 MeV ≫ σ_E ~0.1–0.23）⟹ **spectator 依賴唔可能來自標籤層**。

### R3 — 色數 3 = B−1 亦係加性標籤，解釋唔到 spread
本 O 交付嘅 `3 = B−1 = N_gen`（O68/O88 嵌入層閉合引用）中，B（baryon number）係**加性**量子數。若讀數只依賴 B（或任何 U(1) 加性荷），同取代通道必然同 E ⟹ 與 8 通道譜矛盾。
⟹ spectator 依賴必須**超越所有加性標籤**（B、Q、色數、substitution count——M4 四類已排除）。

**結論**：spectator 依賴算子**唔在 O216 管轄層**。它屬 channel-level 群論算子（「通道內佔用集 → em 讀數」嘅非加性映射），M4 已 handoff `O124`（Y = T₃^R + (B−L)/2）與 `O85`（adjoint 分解）。按 10-16 裁決，屬他 O 之剩餘項本 O 內禁推、只 register 發還——本答覆**唔代 O124/O85 推導**。

## 四、可操作定位（非 O216 導出，只列結構必要條件）

供 M4 建候選式時 self-check，唔係預言：

1. **最少 2-body**：非加性 ⟹ 候選式必含 pairwise（或更高階）項；純 1-body 項已被 C2c 殺。
2. **唔可以用色標籤做 pairwise 核**：SU(3)_c 標籤層唯一自然 pairwise 不變量 = 二次 Casimir C₂(R)（∝ T^aT^a 收縮）；同一 R 下多重集改變 C₂ 不變 ⟹ 單靠 C₂ 產生唔到 B 組 spread。算子必須用 **flavour 標籤**（屬 O124 電荷結構），唔係色標籤。
3. **檢定形式**：對稱核 `E = Σ_i w_i + Σ_{i<j} K_{ij}` 可直接用 M4 8 通道約束集檢定；報自由度成本（參數數 vs 8 通道）＋ 樣本外通道（M4 尚未用嘅通道）作盲測。
4. **本 O 不再供給**：色荷標籤身份已交付完畢（色數 3、Δn_color no-go）；再上一層算子屬 O124/O85 管轄。

## 五、狀態與核實

- O216 保持 🟢 closed（**唔 reopen**）；本 doc = 對外答覆記錄，append-only。
- M4 目錄**零寫入**（只讀 docs/18、docs/20）；答覆經 register note 落 `M4`。
- 本 doc 數字全部由 `Fraction` 精確重算（8/8 PASS），零 import 來源 script。