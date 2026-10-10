# O189 — IDCM ↔ 細胞自動機結構對應

<!-- registry
pid:     O189
title:   IDCM ↔ 細胞自動機結構對應（88-site 鏈作為 CA）
state:   partial
verdict: partial
flags:   r1+r2+r3+r4-107ck
owner:   O189
created: 2026-10-04
updated: 2026-10-10
prereq:  O222, O231
source:  用戶 O231 調查裁定開新 O（墓碑重用）
-->

> **狀態**: 🟡 部分閉合（R1，2026-10-10；59/59 PASS，詳見 §八）
> **建立**: 2026-10-04
> **前置**: O222, O231
> **位置**: `open_problems_fresh/o189_cellular_automata_correspondence/`

---

## 一、問題陳述

IDCM 的離散晶格（88-site 鏈 + 離散時間步 τ = 1/ω_ring）在概念上可被視為一種細胞自動機：有限狀態（譜模式）+ 局部規則（最近鄰耦合）+ 離散時間步。但此對應從未被形式化。調律者指示：研究**結構對應**，非以 IDCM 導出 CA（同 O222-QM 層次）。

核心問題：**IDCM 的 88-site 鏈演化對應哪類 CA（elementary/ring/class IV）？O222 已證的求值語義通用計算與 CA 計算能力之間是什麼關係？**

## 二、已確立嘅結構

```
🟢 IDCM: 88-site 鏈 + 離散時間步 τ (O95/O121)
🟢 IDCM: 譜演化 ω_n = 2√J |sin(πn/88)| (O221/O204)
🟢 O222: 求值語義層 (thunk/force/lazy load) 證明 IDCM 資源界限計算能力
🔴 IDCM ↔ CA 的形式化對應：未建立
```

## 三、未確立（🔴 開放問題）

```
🔴 C1 — 狀態空間：IDCM 連續複振幅 vs CA 離散狀態（如何 coarse-grain？）
🔴 C2 — 演化規則：IDCM 線性譜旋轉 vs CA 布林規則（哪個 CA 規則等價？）
🔴 C3 — 計算能力：O222 求值語義通用計算 vs Wolfram class IV 通用性
🔴 C4 — 局部性：IDCM 最近鄰耦合 vs CA 局部更新（是否相同結構？）
```

## 四、攻擊路線

```
1. C1 路線 — 狀態空間比較 → docs/01 + scripts/01
2. C2 路線 — 規則等價性 → docs/02 + scripts/02
3. C3 路線 — 計算能力比較 → docs/03 + scripts/03
4. C4 路線 — 局部性與因果性 → docs/04 + scripts/04
```

## 五、驗證標準

```
✅ S1 — 每條路線有 doc + script
✅ S2 — 誠實區分「等價」vs「模擬」vs「類比」（三層不可混）
✅ S3 — 若 IDCM 譜演化對應某具體 CA 規則（如 rule 110），證明其對應；否則標 🔴 負結果
```

**四道硬測試**（閉合宣稱必過）：
① 自由度成本（零參數）② Monte-Carlo null（10⁷ 樣本，5σ）
③ 可證偽 + 樣本外盲測 ④ 結構剛性（微擾測試）

## 六、推導時序索引

> ⚠️ **只可 append 新行，禁回溯污染舊行。**

| # | 日期 | 事件 | 產物 |
|:-:|:-----|:-----|:-----|
| 1 | 2026-10-04 | 註冊 O189（墓碑重用） | 01_problem_record.md + SESSION_START.md |
| 2 | 2026-10-10 | R1 四路線執行：狀態空間／規則等價／計算能力／局部性 | scripts/01–04（59/59 PASS）+ docs/01–04 + final_result.md |
| 3 | 2026-10-10 | R2 mod-q 商群投影（R-C 攻堅） | scripts/05（20/20 PASS）+ docs/05 —— mod-2 ⇔ Rule 90 精確 intertwinement |
| 4 | 2026-10-10 | R3 三殘餘：連續流 2-adic／period 248／ε-CHL 律 | scripts/06（8/8）+ 07（7/7）+ 08b（3/3）+ docs/06–08（08 v1 4 FAIL 記錄） |
| 5 | 2026-10-10 | R4 R-A：O222 求值語義層計算類判定 | scripts/09（10/10 PASS）+ docs/09 —— 限界=FS 非 TC；D7 遞歸 thunk 條款先升 TC；cap=TC-blocker |

## 七、相關文件

```
- O222 — 求值語義層（適用於計算能力比較）
- O231 — SYM vs QFT 比較方法論
- O121 — 離散時間步 τ = 1/ω_ring

---

## 八、R1 執行結果（2026-10-10，append-only）

> 推導詳見 `docs/01–04`；`scripts/01–04` 可重跑（59/59 PASS）。

| 路線 | 狀態 | 一句結論 |
|:---|:--:|:---|
| C1 狀態空間（docs/01） | 🟢 | 88 格同位；CA = 1-bit 粗粒化容量恆等（q=2）；雙鏈因子（mode 44 bits）；譜熵 H=5.037、有效模式 32.8 |
| C2 規則等價（docs/02） | 🟢 | 生成元 = radius-1 線性局部規則（CHL 類）；τ-map global；**盲測 256 ECA 零命中**（正對照唯一命中 110） |
| C3 計算能力（docs/03） | 🟢 | **起手式「O222 通用計算」聲稱 REFUTED-as-written**（審計 0 條）；IDCM 88-ring = class II⁺（準週期、等距、bounded），非 class IV |
| C4 局部性（docs/04） | 🟢 | 開線傳播子 = Bessel 恆等式（**冇嚴格光錐**）；ε-因果斜率 2.27→v_max=2；環 ε-水平閉合 t=12；τ-map global |

**驗證標準 S1–S3**：
- S1 每路線有 doc + script ✅（docs/01–04 + scripts/01–04）
- S2 等價/模擬/類比三層分離 ✅（每篇 §「等價／模擬／類比」）
- S3 對應之證明或負結果 ✅（C2：🔴 負結果，窮舉 256 + 正對照；C3：🔴 class IV 否證）

**殘餘（未閉合，同 O 續推，唔開新 O）**：
1. IDCM 理論整體（O222 語義層 + 無界 chain refinement）之計算類——本輪只答固定 88-ring；
2. sign_rank ≤ 3 對計算類嘅約束力（→ O224/O228）；
3. coarse-grain 嘅動力學兼容性（quantize 後演化身份）——本輪只有容量對齊；
4. ℤ 線上 Bessel 尾嘅可模擬性（IDCM 無限格版本嘅 CHL 局部規則 radius 與 t 關係之一般律）。

---

## 九、治管裁決（2026-10-10，append-only）

調律者裁定：**唔開新 O**。R-B 非歸屬 O189，經 register `handoff` O189→O228（ref: docs/03 §六②）；R-A／R-C／R-D 留 O189 續推（直接寫入 SESSION_START＋docs 新檔）。register 對應事件：handoff（2026-10-10）＋ note（治管裁決）＋ mirror（REGISTER.md 475 rows）。

## 十、R2 執行結果（2026-10-10，append-only）

> 推導詳見 `docs/05_mod2_quotient.md`；`scripts/05_mod2_quotient.py` **20/20 PASS**（可重跑）。

- 🟢 **R-C 已回答**：mod-q 商群投影 = 動力學兼容嘅精確粗粒化。`π_q∘F = F_q∘π_q`（q ∈ {2,3,5,7,13}，驗證零例外）；q=2 由 2I≡0 (mod 2) 推導出 **F mod 2 = Rule 90**（零擬合）。負對照（隨機實矩陣 50/50 不匹配）證明「整數生成元」係必要條件。
- 🟢 **2-adic 合併結構**：γ₀=0 ↔ γ₄₄=4 都 ≡0 (mod 2) ⟹ kernel(F mod 2) = span{1, (−1)^j}（nullity 2）；奇 p（p∤88）nullity 1。R1 嘅 Rule-90 nullity 2 / period 248 由此獲得結構解釋。
- 🔴 **新殘餘**（R2 後）：① unitary 連續流嘅 2-adic 行為（e^{−iFt} 非整數）未答；② Rule-90 period 248 閉式（ord(2 mod 88) 系）未閉。
- **R-C 狀態**：已回答（商群意義）；R-A、R-D 照舊留 O189。

## 十一、R3 執行結果（2026-10-10，append-only）

> 推導詳見 docs/06–08；scripts/06（8/8）＋ scripts/07（7/7）＋ scripts/08+08b（v1 0/4 FAIL 記錄 ＋ v2 3/3 PASS）。

- 🟢 **殘餘①閉合**（docs/06）：連續流 2-adic no-go 定理——U(t) ∈ M₈₈(ℤ) ⟹ 特徵值 e^{−iγ_n t} 係代數整數 ⟹ Kronecker 單位根 ⟹ t 超越；π 超越（Lindemann）＋ γ_n 代數 ⟹ γ_n/π ∉ ℚ。**連續時間對任何非零代數 t 冇模 q 商群**；唯一商群 = 生成元映射（R2）。
- 🟢 **殘餘②閉合**（docs/07）：**period 248 = 8×31 = 2³(2⁵−1)**——8 = Frobenius 重數（(x^11−1)^8 = x^88−1 over F₂），31 = max ord(λ^j+λ^{−j})（GF(2¹⁰) 內 λ 本原 11 次根；31 = 2⁵−1 唔除 3·11）；300 seeds lcm = 248、max preperiod ≤ 4。
- 🟢 **R-D 閉合**（docs/08）：**ε-CHL 律** r_ε(t) = 2t + C_eff(ln 1/ε)^{2/3} t^{1/3}，C_eff = 1.3106[1−(ln t)/(2 ln 1/ε)]^{2/3}（Debye 尾）；v1 預註冊 C=1.432 **0/4 FAIL（原樣保留，唔拆）**，v2 修正律 3/3（WA 9 格 0.91–0.97、WB 0.972、WC 0.653）；coarse-ε（1e-2）係 peaks-limited regime，不屬本律。
- **R-A（理論整體計算類）為 O189 唯一剩低殘餘**。

## 十二、R4 執行結果（2026-10-10，append-only）

> 推導詳見 docs/09；scripts/09（10/10 PASS）。

- 🟢 **R-A 閉合**：O222 求值語義層計算類判定——
  ① **限界版（as stated：force 單值 ＋ 200 步上限（A6）＋ memo≤3844（B5 預算）＋ 有限晶格 gen 集）＝ 有限態機，唔係 Turing-complete**（E1：可達配置有限｜測 1；E4：基數上界 (|U|+1)^8·CAP，有界＋全總 ⟹ 對角線論證非萬能）；
  ② **TC 門檻 = O222 冇寫嘅 D7 條款**（遞歸 thunk 圖／自引用生成器）——加咗即 μ-遞歸 ⟹ TC；E3 盲測：fac(10)=3628800、fib(20)=6765、gcd(21,14)=7、**ack(3,3)=61** 全由 memoized thunk 強制引擎計出（引擎自引用 rec，非外部遞歸）；
  ③ **stated cap = TC-blocker**（E2：countdown 1000→0 喺 200 步禁／1000 步過）⟹ 「O222 已證通用計算」喺條款下係錯（唔止冇證明）；真正身份 = 資源界限確定性語義（對接 O228 k_min ≥ ⌈log₂m⌉）。
- **O189 所有歸屬殘餘已答完**（R-A/B/C/D ＋ R2 殘餘①②）；狀態保持 `partial`（三層分離 L1/L2/L3，唔聲稱「IDCM 世界 = 通用電腦」）。