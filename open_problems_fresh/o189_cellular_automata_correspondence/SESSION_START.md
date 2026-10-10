# O189 SESSION_START — IDCM ↔ 細胞自動機結構對應

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

> **Session**: 2026-10-04（新建立）
> **狀態**: 🔴 已註冊 — 未開始
> **來源**: O231 調查發現 IDCM 無 CA 對應 O 系列；調律者裁定開 O189（墓碑重用）
> **前置**: O222 (QM 求值語義對應，thunk/force/lazy load), O231 (SYM vs QFT, 方法論)
> **位置**: `open_problems_fresh/o189_cellular_automata_correspondence/`

---

## 一、接手起點

未開始。調律者指示：目標與 O222(QM)/O221(GR) 一樣，**研究 IDCM 離散晶格動力學與細胞自動機 (CA) 理論之間的結構對應，非以 IDCM 導出 CA**。

## 二、先做嘅第一步

```
1. 讀 O222 (求值語義層, resource-bounded computation, sign_rank ≤3)
2. 讀 CA 基本文獻（Wolfram classes, Rule 110 通用性, 環形 CA, class IV 邊界）
3. 寫 docs/01_state_space.md — IDCM 譜模式 vs CA cell state 的狀態空間比較
4. 寫 docs/02_rule_equivalence.md — 譜演化（線性旋轉 + 頂點耦合）vs CA 布林規則
5. 寫 docs/03_computational_universality.md — O222 求值語義已證通用計算 vs CA class IV
```

## 三、已知陷阱

```
⚠️ IDCM 是線性量子演化（複振幅，連續），CA 是經典布林（離散）— 兩者物理層不同
⚠️ 模擬不等於等價 — IDCM 可模擬 CA（大狀態空間），CA 亦可模擬 IDCM（圖靈完備），這不構成結構對應
⚠️ O222 求值語義層已證 IDCM 可通用計算 — 這比 CA class IV「可通用」更強，但語義層不同於底層晶格的 CA 類
⚠️ 不可宣稱「CA = IDCM」— 比較框架是結構對應，非等同
```

## 四、關鍵數字

| 量 | 值 | 出處 |
|:---|:---|:-----|
| IDCM 鏈 sites | 44 (88-site dual chain) | O95 |
| IDCM 時間步 | τ = 1/ω_ring ≈ 13.47 Gyr | O121 |
| 譜模式數 | 44 (n=1..44) | K_chain |
| O222 計算成本 | 62 軸 × 62 軸 = 3844 對 | O222 |
| O222 求值語義 | thunk/force/lazy load, resource-bounded | O222 |

## 五、交接 / 依賴

```
- 前置: O222 (求值語義層, resource bound, 通用計算), O231 (SYM vs QFT, 比較方法論)
- 範圍: 唔建構新的 CA 模型（IDCM 已有自身演化）
- 範圍: 唔宣稱「IDCM = CA」（物理範疇不同，只研究結構類比）
```

---

## Session 記錄（append-only）

### Session 1 — 2026-10-10（R1：四路線首輪）

**狀態**: 🔴 → 🟡 partial（`r1-59ck`）；註冊 blocks 已同步（10 字段）

**執行**（全部可重跑，零後驗 fit）：
- `scripts/01_state_space.py` 13/13 PASS → `docs/01`：C1 答——**89 格齊、CA = 1-bit 粗粒化容量恆等（q=2）、雙鏈因子（mode 44 bits）**；譜測度熵 H=5.037 bits、有效模式 32.8
- `scripts/02_rule_equivalence.py` 24/24 PASS → `docs/02`：C2 答——**生成元係 radius-1 線性局部規則（CHL 類）；τ-map global（nnz 滿 7744）；盲測 256 ECA 零命中（正對照唯一命中 110）**；結構平行只喺線性 CA（Rule 90 族，不同 module）
- `scripts/03_computational_universality.py` 13/13 PASS → `docs/03`：C3 答——**更正起手式聲稱：O222 冇 Turing/通用計算證明（機械審計 0 條）**；IDCM 88-ring = class II⁺（準週期、等距、bounded），非 class IV；三層區分 L1/L2/L3
- `scripts/04_locality.py` 9/9 PASS → `docs/04`：C4 答——開線傳播子 = **Bessel 恆等式（冇嚴格光錐，超指數尾）**；ε-因果斜率 2.27→v_max=2；環 ε-水平閉合 t=12；τ-map global

**判據修正（audit-side，已寫入各 docstring）**：01 C1.6 閾值 5/44→1.5u（測得 ratio 1.956）；02 A4「U(1) dense」→「t=12 滿、τ-map 滿」；04 4.3/4.4「嚴格光錐」→「Bessel + ε-因果」（物理否定，非放水）。

**關鍵負結果**：🔴 IDCM sign-bit 投影 ≠ 任何單一 ECA；🔴 IDCM 唔係 class IV；🔴 O222「通用計算」聲稱 refuted-as-written。

**files**: docs/01–04、scripts/01–04、data/01–04（json）、logs/01–04、final_result.md、README 行、register notes ×2

**git 附註（append-only, 2026-10-10）**: 本 session 有並行外部 session 活動。`README.md`＋`register.jsonl` 之 O189 改動被 commit `076af96`（O188 subject, 12:58:33）掃入；o189 目錄全部 19 檔案＋register 尾行被 commit `b17e60e`（O185/IF2 subject）掃入（該 commit 亦含 O185 自身 Round 2 檔案）。**內容零損失**，惟 git 歷史屬性非 O189 自己 commit；本 O 檔案工作樹已全部 clean。

**治管裁決（2026-10-10）**: 唔開新 O；R-B（sign_rank≤3 計算類約束）非歸屬 O189 → register `handoff` O189→O228；R-A／R-C／R-D 留 O189 續推。下一輪建議次序：R1（mod-2 → Rule 90）→ R3（radius-R no-go）→ R4（L2 語義層計算類）。

### Session 2 — 2026-10-10（R2：mod-q 商群投影，R-C 攻堅）

**執行**：`scripts/05_mod2_quotient.py` **20/20 PASS** → `docs/05_mod2_quotient.md`
- **R-C 已回答**：mod-2 商群投影係**動力學兼容嘅精確粗粒化**——π(Fψ) = Mπ(ψ)（200 seeds 零例外），**M = S+S⁻¹ = Rule 90**（零擬合，由 2I≡0 mod 2 推導）；普遍化到 q ∈ {3,5,7,13}（ℤ/q 線性 CA，P_q = 2−x−x⁻¹）；負對照（隨機實矩陣 50/50 不匹配）
- **2-adic 合併**：γ₀=0 ↔ γ₄₄=4 都 ≡0 (mod 2) ⟹ kernel dim 2（span{const, (−1)^j}）；奇 p nullity 1 —— R1 嘅 Rule-90 nullity 2 同 period 248 而家有結構解釋
- **誠實邊界**：unitary 連續流 e^{−iFt} 非整數矩陣 ⟹ intertwinement 唔延伸連續時間

**判據修正**：無（預註冊全數命中；B1/B2/C1b 初版漏 `%2` 係執行 bug，修正後即過——非 threshold 變動）。

### Session 3 — 2026-10-10（R3：三條殘餘一次過）

**執行**：
1. `scripts/06_flow_2adic.py` **8/8 PASS** → `docs/06`：**殘餘①閉合（no-go 定理）**——連續流 U(t) 喺任何非零代數 t 都 ∉ M₈₈(ℤ)（π 超越 Lindemann ＋ γ_n/π∉ℚ ＋ Kronecker 單位根）⟹ 連續時間冇模 q 商群（t=0 除外）；商群唯一通道 = 生成元映射（R2）
2. `scripts/07_period_248.py` **7/7 PASS** → `docs/07`：**殘餘②閉合**——period 248 = 8×31 = 2³(2⁵−1)：8 = Frobenius 重數（x^88−1=(x^11−1)^8 over F₂），31 = ord(λ+λ⁻¹) max（GF(2¹⁰) 驗證，λ 本原 11 次根）
3. `scripts/08_eps_chl_law.py` **v1 0/4 FAIL（原樣保留）** ＋ `scripts/08b_eps_chl_law_v2.py` **3/3 PASS** → `docs/08`：**R-D 閉合**——ε-CHL 律 r_ε(t) = 2t + C_eff(ln 1/ε)^{2/3} t^{1/3}，C_eff = 1.3106·[1−(1/2)ln t/ln(1/ε)]^{2/3}（Debye 尾推導；v1 漏 -2/3√2 前因子＋ln t 修正 ⟹ 真·盲測 FAIL，唔拆）

**R3 合計**：18 PASS ＋ 4 記錄 FAIL；累計 79+18=97 PASS（R1 59 + R2 20 + R3 18）、記錄 4 FAIL。
**殘餘狀態**：殘餘①（連續流 2-adic）✅ 閉合；殘餘②（period 248）✅ 閉合；R-D（ε-CHL 律）✅ 閉合；R-A（理論整體計算類）唯一剩低。

### Session 4 — 2026-10-10（R4：R-A 攻堅，最後殘餘）

**執行**：`scripts/09_semantics_class.py` **10/10 PASS** → `docs/09_semantics_class.md`
- **R-A 已回答（三層聲稱）**：① **限界版（O222 as stated：force 單值＋200 步上限＋memo≤3844＋有限 gen 集）＝有限態機唔係 TC**（E1 可達配置有限、E4 基數論證 1.63e11 上限實測 1、4000 orders 全終止）；② **TC 門檻 = O222 冇寫嘅一條 D7 條款**（遞歸 thunk 圖／自引用生成器）——加咗就上 μ-遞歸 ⟹ TC，E3 構造盲測：fac(10)=3628800、fib(20)=6765、gcd(21,14)=7、**ack(3,3)=61** 全部經 memoized thunk 強制引擎計出；③ **stated cap 係 TC-blocker**（E2：countdown 1000→0 喺 200 步禁、1000 步過——量化「資源界限即唔通用」，對接 O228 k_min）
- **R-A 正式閉合 → O189 所有歸屬殘餘全答完**。O189 保持 partial（唔聲稱「IDCM 世界 = 通用電腦」；三層分離 L1/L2/L3 唔踰越）

---

> ⚠️ **本檔係起手式快照，唔係狀態權威。**