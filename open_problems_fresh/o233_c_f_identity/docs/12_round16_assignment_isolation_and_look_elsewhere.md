# O233 docs/12 — 攻堅路線 R1a–R3：assignment 版本隔離、look-elsewhere 校正、鋸齒敏感度

> **日期**: 2026-10-06 · **Scripts**: `scripts/12_assignment_isolated.py`、`scripts/13_look_elsewhere.py`、`scripts/14_sawtooth_assignment_sensitivity.py`
> **承接**: 第十六輪攻堅（docs/10 剩餘方向「輕子槽成因」+ docs/06 §四 盲測設計）
> **verdict**: **R1a 確立 assignment 分歧（O209 |Δm| 排序 vs O137-R19/O233 γ 升序）；R1b 雙邊盲測**
> **輕子 ≡1 只喺 A_γ 成立（8-mode P = 1/56 = 0.0179，與 B1 一致）；R2 look-elsewhere family 校正 P = 0.1204 > 0.05 ⟹ lepton 槽降為「樣本外單目標 nominal」；R3 鋸齒 4/4 交替只喺 A_γ 成立（A_|Δm| 下 3/4 反向）。**

---

## 一、R1a：Assignment 分歧——O209 唯一分配 vs O233 γ 升序（★ 全新診斷）

### 1.1 兩套權威 assignment 對比

| 框架 | 排序依據 | assignment | 輕子 mode | 輕子 residues (mod 4) |
|:--|:--|:--|:--|:--|
| **O209**（`o209_selection_algebra/docs/03`，22/22 PASS，345/345 全鏈） | \|Δm\| 唯一最小 RMS（9! 窮舉） | 1=t, 2=b, 3=τ, 4=c, 5=μ, 7=s, 9=d, 11=u, 13=e | {3,5,13} | **{1,1,3}** ❌ |
| **O137-R19 / O120 / O233**（`o137/docs/35 §六`、`docs/36 §8.4`、`o120/docs/04 §5`） | γ_n 升序 ↔ 質量升序（C_f = m/(M₀γ_n)） | 1=e, 2=u, 3=d, 4=s, 5=μ, 7=c, 9=τ, 11=b, 13=t | {1,5,9} | **{1,1,1}** ✅ |

### 1.2 矛盾點（源文檔核實）

- **O137 docs/36 §1.3**：以 O209 輕子集 [3,5,13] 為目標，檢定 14 個候選不變量（含 n≡1 mod 4、n∈{1,5,9}）——**全部 ❌**（0/14，mod 掃描 0/3）。
- 但 O137 docs/36 §8.4 自己嘅 C_f 表用 γ 升序（e n=1 → 3.5941），即 O137 R19 **內部兩套並存**：質量表用 γ 升序、角色檢定用 O209 集。
- O209 唯一分配本身係「冪律 ansatz m = M₀|Δm|^α 下」唯一；O209 V8 已承認質量譜形狀 🔴 未閉合（RMS 0.5872）、V11 LOOCV 中位 70% 🔴、V10 α 無身份 🔴。
- O137 docs/36 §十 已裁定「三框架皆未閉合」（A/O137 Φ 目錄 4/9 被證偽、B C_f 自由 零預測力、C/O209 冪律 🟡 未達閉合）。

### 1.3 診斷結論

**lepton 槽 ≡1 mod 4（docs/10 正結果）同鋸齒（docs/05）都建基於「A₅ γ 升序 assignment」呢個框架選擇，而唔係 assignment-invariant。** O209 權威（345/345）提供相反方向嘅分配。呢個分歧**必須**喺 O233 任何升格判決前納入自由度——執行 R1b/R2/R3 如下。

---

## 二、R1b：雙邊盲測 + O210-T3 交叉（`scripts/12`，✅ 已跑）

### 2.1 輕子 ≡1 槽（A_γ 已知，對照 A_|Δm|）

| 量 | A_γ | A_\|Δm\| |
|:--|:--|:--|
| 輕子 mode | {1,5,9} | {3,5,13} |
| residues | {1,1,1} | {1,1,3} |
| 全 ≡1? | ✅ | ❌ |

- 9-mode 版本 P = C(4,3)/C(9,3) = 1/21 = 0.0476（= docs/10 B3）
- **8 有效費米子版本（t 走 VEV 剔除後）**: ≡1 槽 3 個 = 輕子專屬，P = C(3,3)/C(8,3) = **1/56 = 0.017857**（= docs/10 B1）
- 非輕子 5/5（u,d,s,c,b）residues {0,2,3,3,3} 全部避開 ≡1 —— 同事件嘅對稱面，非獨立證據。

### 2.2 ⚠️ H1b（夸克空缺）無鑑別力——已誠實標記

「6 夸克冇固定 residue」原計劃為雙邊盲測第二邊；實算發現 **max residue class size = 4 < 6**（≡1 槽 4 個、≡3 槽 3 個、≡0/≡2 各 1 個），故「6 個全同 residue」結構上概率為 0（MC 10⁶ 命中 0）——**該檢定無鑑別力，唔當正結果**。可檢定版本 = 8 費米子（H1a' 已覆蓋）。

### 2.3 O210-T3 交叉（兩讀法，`scripts/12`）

| 讀法 | 內容 | A_γ | A_\|Δm\| |
|:--|:--|:--|:--|
| 讀法 1 | Q := N_c·(B−L) ≡ \|λ\| (mod B)；輕子 N_c=3, B−L=−1 ⟹ Q = −3 ≡ 1 | ✅ 全 ≡1 | ❌ {1,1,3} |
| 讀法 2 | k ≡ ±\|B−L\| (mod B), \|B−L\|=1 ⟹ k∈{1,3} | ✅ {1}⊆{1,3} | ✅ {1,3}⊆{1,3} |

⟹ **O210-T3 讀法 1 係「輕子槽 ≡1」嘅結構候選**（N_c·(B−L) ≡ 1 mod 4），但**只喺 A_γ 下成立**；讀法 2 兩種 assignment 皆可，無鑑別力。
⚠️ 橋接前提未證：O210-T3 之 |λ| 為張量外冪度數（tensor power k），O233 之 mode n 為鏈模式——**n ≡ |λ| (mod 4) 嘅映射本身未定義**，只能當「候選銜接」，唔係已證推導。

---

## 三、R2：look-elsewhere family 校正（`scripts/13`，✅ 已跑）

**動機**：docs/10 誠實警戒「B1/B3 單一目標 nominal，未含 look-elsewhere」。同一 8-9 點 dataset 已多輪 look（鋸齒/極值/身份/槽結構）。

**方法**：family = 全部 mod-k 同餘類（k=1..44），|S(k,r) ∩ A₅| ∈ [3,4]，去重後 **5 個類**：
- mod 3 ≡1 {1,4,7,13} P=1/21；mod 3 ≡2 {2,5,11} P=1/84；**mod 4 ≡1 {1,5,9,13} P=1/21（觀測命中）**；mod 4 ≡3 {3,7,11} P=1/84；mod 6 ≡1 {1,7,13} P=1/84

**Null**（label permutation，MC 10⁶）：任意 label 置換下「∃ class: 3 個輕子全部落該 class 且 P ≤ 0.05/1/21」嘅概率：

```
P(∃ class 全落, 唔問 p)     = 0.1204
P(∃ class 全落 且 p ≤ 0.05) = 0.1204
P(∃ class 全落 且 p ≤ 1/21) = 0.1204
```

⟹ **校正後 P = 0.1204 > 0.05**：lepton 槽 B1/B3 **過唔到 family-wise look-elsewhere**。維持 docs/10 原判定——只能當「樣本外單目標盲測」，**唔可以當多重檢定後獨立證據**。

---

## 四、R3：鋸齒 assignment 敏感度（`scripts/14`，✅ 已跑）

**動機**：docs/06 主張「鋸齒真身 = Z₂ 奇偶 rank 分裂」，兩子序列各自單調增 + 相鄰 even>odd 4/4。查證此結構係唔係 assignment-invariant。

| 框架 | C_f 沿質量升序 | 相鄰交替 | even-rank 單調 | odd-rank 單調 |
|:--|:--|:--|:--|:--|
| A_γ | 3.59, 3.80, 3.66, 41.3, 30.0, 186.1, 159.6, 255.8 | ✅ **4/4** | ✅ | ✅ |
| A_\|Δm\| | 0.023, 0.132, 0.420, 13.7, 30.0, 561.9, 1393, 7359 | ❌ **3/4 反向** | ✅ | ✅ |

⟹ **鋸齒 7/7 交替（docs/05, p=0.0138）只喺 A_γ 下成立**；A_|Δm| 下 C_f 接近單調增，交替消失。even/odd 兩子序列各自單調喺兩框架都成立——但「兩流各自有序」單獨無鑑別力（見 docs/06 §二 因果：完全交替 ⇔ 奇偶子序列各自有序）。

**X 算子 Z₂ 對照**（docs/06 三.2）：X 耦合 V_nm≠0 ⇔ n+m 奇；但 A_γ 鋸齒中 even-rank 粒子 mode parity = {E,E,O,O}（u2/s4/c7/b11）非純——鋸齒 rank-parity **唔直接等於** mode-parity，「同一 Z₂ 兩投影」假說需額外橋，未證。

---

## 五、戰局更新（R1a–R3 後）

| # | 結果 | 原 p | R1a–R3 後狀態 |
|:--|:--|:--|:--|
| 1 | 鋸齒 split | 0.0138 | 🟡 **assignment 敏感**（只 A_γ；A_\|Δm\| 下消失） |
| 2 | 階梯 T-rank | 0.00117 | 🟡 待 assignment 隔離重檢（同鋸齒依賴 A_γ） |
| 3 | 兩者獨立 + 升序同時極端 | 1/1055 | 🟡 同上 |
| 4 | u/d 身份層穩健 | 1.0000 | 🟢（rank 層不涉 assignment 方向；仍待重跑確認） |
| 5 | **lepton 槽 ≡1 mod 4** | 0.0476/0.0179 | 🔴 **look-elsewhere 校正後 0.1204** + assignment 敏感 |

**核心攻堅判決**：O233 五項正結果全部建基於「A₅ γ 升序 assignment」呢個框架選擇；**該選擇同 O209 唯一分配（345/345）衝突**，且無獨立結構證據裁定 γ 升序 vs |Δm| 排序邊個先係正宗質量↔模式映射。O137 R19 自己 §1.3 已以 O209 集判 lepton 槽 ❌——此分歧必須喺 O 系列層面裁決（跨 O 交接，見 §六）。

---

## 六、下一步（跨 O 交接候選）

1. 🔴 **Assignment 分歧裁決**（O209 vs O137-R19/O120/O233）：γ 升序定 |Δm| 排序？O209 V8 自認冪律形狀未閉合、O137 §十 三框架皆未閉合——兩邊都冇閉合質量譜，需要獨立判準（例如：γ_n 係鏈譜本徵值 = IDCM 主線質量骨架 vs |Δm| 係 O136 二階統計量；先前 C_f = m/(M₀γ_n) 嘅「商定義」本身已鎖定 γ 升序——見 O120 closeout §5）。→ 建議 register handoff O233 → (O209 或 O137) 統一裁定。
2. 🟡 **lepton 槽升格路徑**：若 A_γ 獲裁定，B1/B3 仍要過 family-wise null——現校正後 0.1204，需搵更強性質（唔係 mod-k 家族內）或樣本外。
3. 🟡 **O210-T3 橋**：n ≡ |λ| (mod 4) 嘅映射（鏈模式 ↔ 外冪度數）若成立，輕子槽成因有結構候選。
4. 🟢 已做：R1b 8-mode 1/56、R2 校正、R3 assignment 敏感度——全部 scripts/data 已存。

---

## 文件動作

- `scripts/12_assignment_isolated.py` + `data/12_assignment_isolated.json`（新建）
- `scripts/13_look_elsewhere.py` + `data/13_look_elsewhere.json`（新建）
- `scripts/14_sawtooth_assignment_sensitivity.py` + `data/14_sawtooth_assignment_sensitivity.json`（新建）
- `docs/12`（本文件）· SESSION_START append · register note（O233 + 跨 O handoff 候選）
- 舊檔零改動（docs/01–11、scripts/01–11 append-only）。