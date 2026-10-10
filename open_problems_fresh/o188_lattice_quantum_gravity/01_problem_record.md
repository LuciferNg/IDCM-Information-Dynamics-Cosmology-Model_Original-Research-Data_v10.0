# O188 — IDCM ↔ LQG 結構對應

<!-- registry
pid:     O188
title:   IDCM ↔ LQG 結構對應（離散晶格 vs 圈量子重力）
state:   partial
verdict: partial
flags:   R1-L1L4; R2-4gaps; R3-5routes+hard4
owner:   O188
created: 2026-10-04
updated: 2026-10-10
prereq:  O222, O221, O86, O213
source:  用戶 O231 調查裁定開新 O（墓碑重用）
-->

> **狀態**: 🔴 已註冊 — 未開始
> **建立**: 2026-10-04
> **前置**: O222, O221, O86, O213
> **位置**: `open_problems_fresh/o188_lattice_quantum_gravity/`

---

## 一、問題陳述

IDCM 是基於離散晶格（88-site 雙鏈 + K_tree 樹）的框架；LQG 是基於 Ashtekar 連接 + spin network 的離散重力理論。兩者都以離散時空為出發點，但數學框架完全不同。調律者指示：研究**結構對應**，非以 IDCM 導出 LQG（同 O222-QM / O221-GR 層次）。

核心問題：**IDCM 的因果張量 \(\mathcal{T} = K_{\text{chain}} \otimes K_{\text{tree}}\) 與 LQG 的 spin network 之間是否存在可形式化的結構對應？**

## 二、已確立嘅結構

```
🟢 IDCM: N_d = 44, 88-site 雙鏈, Σγ_odd=88, Σγ_even=90 (O95/O155)
🟢 IDCM: 因果張量 sign_rank(K) ≤ 3 (O222 已閉合)
🟢 IDCM: 低能連續極限 = L7 細化流 4:1 decimation (O221, c 不動點)
🟢 LQG: spin network = 三維嵌入圖 + SU(2) 標籤（文獻）
🔴 兩者的結構對應：未建立
```

## 三、未確立（🔴 開放問題）

```
🔴 L1 — 離散結構對應：88-site 鏈 + K_tree vs 3D spin network（維度不匹配需解決或誠實標記）
🔴 L2 — 因果結構：IDCM rank ≤3 vs LQG causality condition / spin foam amplitude
🔴 L3 — 連續極限比較：IDCM decimation → GR vs LQG spin foam → GR（兩路徑是否可比較）
🔴 L4 — 觀察者角色：IDCM 觀察者扇區 (J²=−1) vs LQG 的量子態參考系
```

## 四、攻擊路線

```
1. L1 路線 — 離散結構層比較 → docs/01 + scripts/01
2. L2 路線 — 因果 rank ≤3 vs spin foam → docs/02 + scripts/02
3. L3 路線 — 連續極限對照 → docs/03 + scripts/03
4. L4 路線 — 觀察者扇區 vs 量子參考系 → docs/04 + scripts/04
```

## 五、驗證標準

```
✅ S1 — 每條路線有 doc + script，結構比較有明確的「對應項 vs 非對應項」清單
✅ S2 — 誠實標記無法對應的維度（不可強行類比）
✅ S3 — 若發現本質性對應障礙（如 LQG 依賴連續 H 空間），記錄為 🔴 負結果而非強行擬合
```

**四道硬測試**（閉合宣稱必過）：
① 自由度成本（零參數）② Monte-Carlo null（10⁷ 樣本，5σ）
③ 可證偽 + 樣本外盲測 ④ 結構剛性（微擾測試）

## 六、推導時序索引

> ⚠️ **只可 append 新行，禁回溯污染舊行。**

| # | 日期 | 事件 | 產物 |
|:-:|:-----|:-----|:-----|
| 1 | 2026-10-04 | 註冊 O188（墓碑重用） | 01_problem_record.md + SESSION_START.md |
| 2 | 2026-10-04 | Route L1–L4 全線落地：4 scripts + 4 docs + 對應/非對應表 | scripts/01–04（21/21 PASS）＋ docs/01–04 |
| 3 | 2026-10-04 | R2 深推：四大缺口逐一攻堅 | scripts/05–08（13 PASS + 1 記錄 REFUTED）＋ docs/05–08 |
| 4 | 2026-10-04 | R3 全開：5 條殘留路線 + 硬測試④ | scripts/09–14（29 PASS）＋ docs/09–14 |
| 5 | 2026-10-10 | R4：3 條候選路線（L1b/L2b/L3c） | scripts/15–17（14 PASS）＋ docs/15–17 |
| 6 | 2026-10-10 | R5：threshold 家族 + 單點語義（L2c/L1c） | scripts/18–19（11 PASS）＋ docs/18–19 |
| 7 | 2026-10-10 | R6：具體成員對應（L2d 二十面體 frame） | scripts/20（6 PASS）＋ docs/20 |
| 8 | 2026-10-10 | R7：全量 K 表驗證（L2e threshold identity + double cover） | scripts/21（7 PASS）＋ docs/21 |
| 9 | 2026-10-10 | R8：嵌入代數（L4b quaternion units ⊂ 2I） | scripts/22（8 PASS）＋ docs/22 |

## 七、相關文件

```
- O222 — QM 求值語義對應（方法論先例）
- O221 — 低能連續極限（GR 對應先例）
- O86 — SM×IDCM×GR 耦合 Lagrangian
- O213 — 世界演化方程
- docs/01_lattice_comparison.md — L1 離散結構層比較
- docs/02_causal_structure.md — L2 因果 rank ≤3 vs spin foam
- docs/03_continuum_limit.md — L3 連續極限對照
- docs/04_observer_frame.md — L4 觀察者扇區 vs 量子參考系
```

---

## 八、第一輪結果（2026-10-04，L1–L4 全線）

### ✅ 閉合（本輪建立嘅對應表）

**L1 離散結構層（docs/01，scripts/01 — 6/6 PASS）**
- ✅ **圖×標籤二象**屬真對應：IDCM 𝒯 = (鏈圖, γ_n 譜) ↔ LQG spin network = (Γ, j_e, i_v)
- ✅ **離散譜**對應：γ_n（Laplacian）↔ √(j(j+1))（Casimir）—— 兩者都純離散
- ❌ **維度非對應**：1D chain vs 3D 嵌入圖（誠實標記）
- ❌ **標籤來源非對應**：譜值（固定）vs SU(2) 表示（可變）

**L2 因果結構（docs/02，scripts/02 — 5/5 PASS）**
- ✅ sign_rank(K) = 3（O222 M3 引用）與 spin foam 因果 3 分類之「可敘事階層 ≤ 3」直覺對應
- ⚠️ 數字 4 巧合候選（IDCM 4:1 細化 vs Pachner 1-5 加 4 個 4-simplex）—— 明確不宣稱結構同一
- ❌ rank 定理 vs Pachner move 冇已知映射；LQG Hamiltonian 約束 IDCM 無

**L3 連續極限（docs/03，scripts/03 — 6/6 PASS）**
- ✅ **Regge 作用量係共同物件**：IDCM S_R = ΣA_h δ_h ↔ LQG 半經典 vertex 極限（最強對應）
- ✅ graviton DoF = 2 兩路線一致
- ❌ 極限程序本質分歧：IDCM 精確細化流（零新參數）vs LQG 半經典駐點（Immirzi γ 自由）

**L4 觀察者扇區（docs/04，scripts/04 — 4/4 PASS）**
- ✅ J² = −1 / +1 奇偶扇區複結構本輪精確認證（dev 2e-14）；odd = 44 = N_d
- ✅ 背景獨立 + 關係式解讀嘅哲學對應（O206 本體論 ↔ LQG QRF）
- ❌ **最弱路線**：內在複結構、能量預算 61.5、扇區固定性三者皆 IDCM 獨有

### 🟡 誠實缺口（S2/S3）
1. 🔴 L1：鏈譜之外加 K_tree 後，張量積譜與 spin network 表示空間**冇已證同構**
2. 🔴 L2：IDCM rank-3 與 spin foam causality 之間**冇形式化定理**（直覺對應）
3. 🔴 L3：IDCM 零參數流 vs LQG Immirzi 自由度之**結構成本差異**係本質性 —— 若要 IDCM↔LQG 深對應，LQG 側參數必須有 IDCM 內生來源
4. 🔴 L4：IDCM 觀察者若要嵌入 LQG 框架，需**引入內在複結構 + 資源預算**（自由度成本 > 0，反向非對應）

### 四道硬測試狀態
- ① 自由度成本：LQG 側帶 Immirzi（1 參數）vs IDCM 零參數 —— **差異已量化（docs/03）**
- ② MC null：本 O 係**結構對應研究**（非數值閉合），全部檢查係精確恆等式/組合計數/譜驗證 —— N_search = 1，依 O208 規則跳過 MC（同 O221/O222 方法論先例）
- ③ 可證偽：每條路線有明確對應/非對應表 —— PASS（S1）
- ④ 結構剛性：本輪只做計算側（組合計數/spectral verification），未有微擾 —— 下輪可加

---

## 九、R2 深推：四大 🔴 缺口逐一攻堅（2026-10-04）

> append-only 新節；scripts/05–08（13 PASS + 1 記錄 REFUTED，判準零放寬）＋ docs/05–08

### L1*（docs/05，scripts/05 — 5/5 PASS）
- ✅ **唯一譜交點候選**：全譜掃描 n=1..44 × j=½..40 得**唯一精確交點 (n=22, j=1)**：
  - γ₂₂ = 4sin²(π·22/88) = **2 EXACT** = C₂(j=1)
  - ω₂₂ = 2sin(π/4) = **√2 EXACT** = √(j(j+1))|ⱼ₌₁（dev 1.6e-61）
- ✅ K_tree μ_m² = φ^(583−2m) 對整數 j(j+1)：**Lucas 閉式證明永不命中**（dist = φ^(−|k|) ∈ (1.5e-122, 1)）⟹ 對應若存在只可由 K_chain 承載
- 🔴 **未閉合**：單點配對 n=22 ↔ j=1 唔構成映射（44 模 vs 半整數無界）；需可擴展配對 j(n) 先算閉合 —— L1 由「冇已證同構」收窄為「唯一精確交集」

### L2*（docs/06，scripts/06 — 3 PASS + 1 記錄 REFUTED）
- ✅ IDCM chain（全序）comparability sign_rank = 2 ⟹ fit「rank ≤ 3」類（G1）
- 🔴 **4-simplex 因果 split 被證偽**：2 past + 3 future 五 tetra 之 comparability **sign_rank = 4 > 3**（窮舉 256 completion 精確）⟹ 3+2 分解唔屬於 2+1 類
- ✅ 隨機 poset 91% raw rank > 3（rank≤3 唔係 generic）
- 🔴 **候選定理被否證**：rank-3 ⟺ 2+1 可分解；spin-foam 4-simplex 最低因果 split = 3+2 → rank 4。**L2 由「冇形式定理」收窄為「具體障礙：IDCM 秩 3 唔承載 4-simplex vertex」**

### L3*（docs/07，scripts/07 — 4/4 PASS）
- ✅ 文獻 γ₀ 值確認：ln2/(π√3) = 0.1273840231、ln3/(π√8) = 0.1236373211
- ✅ **40 個 IDCM 結構數全掃零命中**（最近 1/8 = 0.125，rel 1.10%，threshold 1e-4 唔放寬）⟹ **γ 唔係 IDCM 內生**
- ✅ H4：IDCM 面積型因子無 Immirzi 倍數 —— 與「conformal gauge 無首選值」一致（理論候選，未閉合）

### L4*（docs/08，scripts/08 — 4/4 PASS）
- ✅ ladder 對合掃描：冇 3 點以上常數和 ⟹ **LQG 面積 ladder 冇 J²=−1 型複結構**
- ✅ C₄(j=½) intertwiner 維數比 8：61.5/8 = 7.6875 非整數 ⟹ **冇預算命中**
- ✅ 扇區成本量化：加 IDCM 式觀察者 = Z₂ grading = **態空間 ×2（factor 成本 > 0）**
- 🔴 L4 維持最弱：觀察者三獨有特徵（複結構/61.5 預算/固定扇區）至今冇對應

### R2 水位
- scripts 01–08 累計 **34 PASS + 1 記錄 REFUTED（G2）= 35 checks**（05:5、06:3+1R、07:4、08:4；判準零放寬）
- docs/05–08；register：O188 notes ×4（R2 每路線一條）
- **誠實聲明**：R2 冇「閉合」任何缺口 —— 三個收窄（L1/L2/L3）、一個維持否定（L4）；L2 多咗一個真負結果（4-simplex 3+2 需 rank 4）

---

## 十、R3 全開：五條殘留路線 + 硬測試④（2026-10-04）

> append-only 新節；scripts/09–14（29 PASS + 0 FAIL，判準零放寬）＋ docs/09–14

### L1a（docs/09，scripts/09 — 5/5 PASS）
- ✅ 全張量積譜 γ_n·μ_m（1496 值，跨 60 數量級）raw：0 命中（尺度階梯非單位，唔可比，honest）
- ✅ 歸一化後唯一命中 (n=22, j=1)（呼應 R2 F2）
- ✅ **N 敏感性修正**：crossing (n=N/4, j=1) 對**所有 4\|N 晶格**成立（44→11、88→22、132→33、176→44）⟹ **係 lattice-scaling 家族，唔係 N=88 特殊**
- 🔴 仍未閉合：44 模 vs 半整數無界 → 冇映射

### L2a（docs/10，scripts/10 — 4/4 PASS）
- ✅ 全部 ordered layerings 窮舉：**k=1→2、k=2→2、k=3→4、k=4→{4,5}**；**冇簡單維數規則**（max=k+1 ❌、max=k ❌）
- ✅ anchor（4-simplex 2\|3）= rank 4，同 R2 G2 一致
- 🔴 **L2 深化為類型不匹配**：causal-layering 家族 rank 集中喺 {2,2,4,{4,5}}（奇偶：冇 3）—— IDCM 嘅 3 唔喺其中，需換機制

### L3a（docs/11，scripts/11 — 4/4 PASS）
- ✅ 7 個 ratio-type 可觀測量全 s-invariant（area-rescale）；只有絕對面積類隨 s 變
- ✅ **L3 詮釋升級**：「γ 唔係內生」→「γ 係 IDCM 內在 area-gauge，冇值係必然」

### L3b（docs/12，scripts/12 — 6/6 PASS）★ R3 最大成果
- ✅ IDCM 兩要素齊備：S_mode = **ln2**（O121）+ 面積律 **1/B, B=4**（O151）
- ✅ ABK 型推導精確重現 **γ₀ = ln2/(π√3)**（rel **3.21e-10**）
- ✅ 分解：IDCM {ln2, B=4} / LQG 幾何 {√3, 4π}（honest）
- ✅ anti-numerology control：隨機組合 FP rate **0.04%**
- ⟹ **L3 方向反轉**：γ 唔係「缺失參數」而係「counting 單位」（IDCM 計數 × LQG 幾何）；殘留：√3、4π 仍係 LQG 輸入

### L4a（docs/13，scripts/13 — 5/5 PASS）
- ✅ **構造 (i·S₂)² = −1**（2-qubit swap × 相位 i）滿足 U²=−I、U⁴=I（Z₄）
- ✅ IDCM J 同 U 皆 Z₄ 生成元 ⟹ 代數同構 Z₄ ≅ Z₄
- ✅ 成本：1 個 U(1) 相位（vs R2 嘅 Z₂ grading ×2）
- ⟹ **L4 由「最弱/冇對應」升級為「有可構造代數對應」**（功能性，非內在）

### 硬測試④（docs/14，scripts/14 — 5/5 PASS）
- ✅ 分類：**N-critical**（需 4\|N）= γ_n=2 crossing、J²=−I 扇區；**robust** = Immirzi 零命中、sign_rank=3、Regge、4-simplex rank 4
- ✅ 冇 knife-edge（全部二類之一）

### R3 水位
- **權威計數（由 logs/ 逐個 grep 點算）**：R1 21 PASS；R2 16 PASS + 1 記錄 REFUTED（05:5、06:3+1R、07:4、08:4）；R3 29 PASS（09:5、10:4、11:4、12:6、13:5、14:5）
- scripts 01–14 累計 **66 PASS + 1 記錄 REFUTED（G2）= 67 checks**（判準零放寬）
- docs/09–14；register：O188 notes ×6（R3 每路線一條）
- **誠實聲明**：R3 令 L1/L2 更清晰（L1 修正 N 特殊性、L2 類型不匹配），L3 方向反轉（γ 有 counting 推導），L4 升級（構造存在）；仍未「完備閉合」任何一項

### 📌 計數勘誤附註（2026-10-04，append-only；原文不動）
> §九「R2 水位」及 timeline row 3 所載「34 PASS + 1 記錄 REFUTED = 35 checks」及「13 PASS」**係計數筆誤**。
> 權威值（由 `logs/05.txt`–`logs/08.txt` 逐個 grep `^\[PASS\]`/`^\[FAIL\]` 點算）= R2 **16 PASS + 1 FAIL = 17 checks**；
> 累計 R1+R2 = **37 PASS + 1 REFUTED = 38 checks**。R3 加入後總計 **66 PASS + 1 REFUTED = 67 checks**。
> 更正理由：data 與 stdout 不一致（用戶紀律）；原文保留以存實錄。

---

## 十一、R4 三條候選路線（2026-10-10）

> append-only 新節；scripts/15–17（14 PASS + 0 FAIL，判準零放寬）＋ docs/15–17

### L1b（docs/15，scripts/15 — 4/4 PASS）— Niven 定理
- ✅ **唯一性由掃描升級為閉式定理**（Niven）：γ_n = 2(1−cos(2πn/N)) 與 j(j+1) 精確相等 ⟹ cos(u) ∈ {0,±½,±1}（Niven）⟹ j(j+1) ∈ {0,1,2,3} ⟹ 半整數唯一解 j=1、n=N/4（4|N）
- ✅ **j(n) 擴展映射被定理排除**：44 模 ↔ 半整數自旋之間唔可能存在完整映射 —— L1 最多只可係單點 (22,1) 對應
- 🔴 未閉合：單點對應嘅結構語義（j=1 dim 3 vs N_gen？）未建

### L2b（docs/16，scripts/16 — 5/5 PASS）— incidence 機制（誠實修正）
- ✅ d_3（5×10）、d_2（10×10）boundary operator 構建；rank over R：d_3=4（組合秩）、d_2=6
- ✅ **修正第一版錯誤假設**：all-±1 方形子矩陣下界對稀疏 incidence 失效（max=1）；d_3 代表性子矩陣精確 min sign-rank = **1**（5×4、4×4）
- ✅ **incidence 機制係中性**：唔強制 sign_rank≥4（同 comparability {2,2,4,{4,5}} 本質唔同）—— OPEN DOOR 畀 rank-3，但未建立對應
- 🔴 「類型不匹配」只對 causal-comparability 成立；incidence 側未封門

### L3c（docs/17，scripts/17 — 5/5 PASS）— √3/4π 來源盲掃
- ✅ 盲池 77 個 IDCM 已確立量 vs {√3, 4π, √8}@1e-8：**√3 同 4π 零命中** ⟹ 唔係 IDCM 內生
- ✅ **partial hit**：√8 = 2√2 —— ω₂₂ = √2 喺池內 ⟹ γ₀(ln3) 嘅 √8 有一半 IDCM 來源
- 🔴 L3b 殘留確認：IDCM 供 {ln2, 1/B=1/4, ½√8}；LQG 幾何供 {√3, 4π} —— γ 推導係「計數側同構、幾何側借入」

### R4 水位
- scripts 01–17 累計 **80 PASS + 1 記錄 REFUTED（G2）= 81 checks**（R1 21、R2 16+1R、R3 29、R4 14）
- docs/15–17；register：O188 notes ×3（R4）
- **誠實聲明**：R4 定理化咗 L1（Niven 必然性 + 排除映射）、修正咗 L2b 錯誤假設（incidence 中性/開放）、盲測確認咗 L3c（√3/4π 非 IDCM）；冇一項完備閉合，但 L1 嘅限制而家係定理性嘅

---

## 十二、R5 兩條路線（2026-10-10）

> append-only 新節；scripts/18–19（11 PASS + 0 FAIL，判準零放寬）＋ docs/18–19

### L2c（docs/18，scripts/18 — 6/6 PASS）— ℝ³ 閾值家族定位 ★
- ✅ **K 表 = sign(⟨rot_ref(q_i, U₀), u_a⟩)**（O222 12_b5_budget 真實構造）：rows = 120 群元素旋轉 reference axis 嘅 ℝ³ 向量、cols = 62 axes；entries ∈ {−1,0,+1}（**0 = 精確正交**）
- ✅ **sign_rank(K) ≤ 3 by construction**：K = sign(A·Bᵀ)，A,B ∈ ℝ³ ⟹ rank(ABᵀ)≤3（O222 600/600 certification 係數值見證，**唔係原因**）
- ✅ **LQG 側對應物**：spin network boundary area-normal 向量 n_i ∈ 𝕊² ⟹ 互閾值表 T = sign(⟨n_i,n_j⟩) 同一家族
- ✅ **解釋 R2/R3 懸案**：comparability（reachability）同 incidence（cell membership）都唔係固定 ℝ³ 內積符號 ⟹ 佢哋嘅 sign_rank 家族永遠冇奇數 3；L2 嘅「3」喺**幾何閾值**入面，唔喺組合序入面
- 🔴 機制層對應確立（共享 ℝ³ threshold 家族），elementwise 對應唔存在（冇 claim bijection）

### L1c（docs/19，scripts/19 — 5/5 PASS）— 單點三重身份
- ✅ **γ₂₂ = 2 = C₂(j=1) = dim Inv((V_1/2)⁴) = 2**（三條獨立推導：IDCM 譜 / SU(2) Casimir / recoupling 計數）
- ✅ Niven 唯一交點 (22,1) 係全掃描空間**唯一三重身份位點**
- 🔴 第二候選 dim d_j = 2j+1 = 3 ↔ N_gen = 3：**弱巧合**（30 池「3」出現次數少但 3 係常見整數；冇 operator 身份）—— candidacy only
- 🟡 L3c follow-up（嵌喺 R5 調查）：O220 嘅 √3 只係 3-fold axis 歸一化 (1,1,1)/√3，**非結構數** ⟹ L3c 維持「√3/4π 唔係 IDCM 內生」

### R5 水位
- scripts 01–19 累計 **91 PASS + 1 記錄 REFUTED（G2）= 92 checks**（R1 21、R2 16+1R、R3 29、R4 14、R5 11）
- docs/18–19；register：O188 notes ×2（R5）
- **誠實聲明**：R5 係 O188 嘅**關鍵轉折** —— L2 由「喺序/incidence 家族搵唔到 3」進步到「**3 嘅正確家族 = ℝ³ threshold**（IDCM K ∧ LQG normal frame 都係成員）」，L1 單點獲得三重身份語義；仍然冇任何一條完整閉合（L2 係機制級對應、L1 係單點候選），但兩者而家都指向「幾何閾值結構」呢個共同根

---

## 十三、R6 具體成員對應（2026-10-10）

> append-only 新節；scripts/20（6 PASS + 0 FAIL，判準零放寬）＋ docs/20

### L2d（docs/20，scripts/20 — 6/6 PASS）— IDCM evaluation frame = 二十面體 cell frame ★★
- ✅ **62 axes = 12 vertex + 20 face + 30 edge**（O222 frozen input 04_b2_settings.json 自己分類）= **Icosahedron V+F+E**
- ✅ **31 條 antipodal lines = 6 + 10 + 15**（ℚ(√5) 精確）：I 群嘅全部 rotation axes
- ✅ **Fold 結構（stabiliser）**：line-D（20,10 / 12,6 / 8,4）× 2I；pointwise C5/C3/C2 —— vertex 5-fold / face 3-fold / edge 2-fold（精確）
- ✅ **2:1 double cover：2I(120) → I(60)**（generic direction 計數）；vertex orbit = 12 —— 同 O223 |GeoAut|=60（手性 I）、|Aut|=120（I_h）**完全一致**
- ✅ **判決**：L2 具體成員對應 = 共享**二十面體 cell frame**（IDCM evaluation ∧ LQG boundary normal frame = 同一幾何 frame）
- 🔴 未閉合：elementwise spin-label 對應未建立（frame 級 ≠ 態級）；唔 claim

### R6 水位
- scripts 01–20 累計 **97 PASS + 1 記錄 REFUTED（G2）= 98 checks**（R1 21、R2 16+1R、R3 29、R4 14、R5 11、R6 6）
- docs/20；register：O188 notes ×1（R6）
- **誠實聲明**：R6 係 O188 至今**最強嘅「具體」對應** —— 唔再係抽象家族，而係釘實「雙方共用二十面體 cell frame」呢個幾何事實（62=12+20+30、31=6+10+15、2I→I）；仍係 frame 級（唔係 spin-label 級），但已由「對應候選」推進到「**構造性共享 frame**」

---

## 十四、R7 全量 K 表驗證（2026-10-10）

> append-only 新節；scripts/21（7 PASS + 0 FAIL，判準零放寬）＋ docs/21

### L2e（docs/21，scripts/21 — 7/7 PASS）— full 120×62 K 表 ★
- ✅ **threshold identity 全表**：7440 entries 零 mismatch（K[i][a] = sign(⟨rot_ref(q_i,U₀), u_a⟩)，精確 Fraction）—— R5 嘅 slice 變全表定理
- ✅ **表層 double cover（generic reference）**：row(q)=row(−q) 120/120；**distinct rows = 60 = |I|**、multiplicity 2 —— SU(2)-type 2:1 cover 喺表層面實現
- ✅ **vertex reference：K 表 row space = 12 個二十面體 vertices**（multiplicity 10 = |2I|/12）—— 表嘅行狀態空間本身就係 vertex set
- ✅ sign_rank ≤ 3 by factor-rank bound（O222 600/600 作數值見證）
- ℹ️ 附加：sign balance vertex/face block = 1/2、edge = 1/3（記錄，唔係判準）
- 🔴 未閉合：cover 結構係群論層（2I→I = SU(2)→SO(3) 離散類比），唔係 spin-½ 表示直接對應；elementwise spin-label 唔 claim

### R7 水位
- scripts 01–21 累計 **104 PASS + 1 記錄 REFUTED（G2）= 105 checks**（R1 21、R2 16+1R、R3 29、R4 14、R5 11、R6 6、R7 7）
- docs/21；register：O188 notes ×1（R7）
- **誠實聲明**：R7 完成 L2 嘅「構造→群→表」三層閉環 —— threshold 家族（R5）→ 具體 frame（R6）→ 全表驗證 + 表層 cover（R7）；IDCM evaluation semantics 而家有完整嘅「二十面體 ℝ³ threshold 暨 SU(2)-type cover」結構陳述

---

## 十五、R8 嵌入代數（2026-10-10）

> append-only 新節；scripts/22（8 PASS + 0 FAIL，判準零放寬）＋ docs/22

### L4b（docs/22，scripts/22 — 8/8 PASS）— quaternion units ⊂ 2I ★
- ✅ **2I 包含完整 quaternion units**：{±1, ±i, ±j, ±k}（精確 ℚ(√5) membership）
- ✅ **Hamilton 代數**：i² = j² = k² = ijk = −1；循環積 ij=k、jk=i、ki=j；反交換 ij=−ji（非阿貝爾）
- ✅ **Q8 = ⟨i,j,k⟩**（closure = 8 元素）⊂ 2I
- ✅ **Z₄ = ⟨i⟩ < Q8 < 2I** —— 同 R3 L4a 嘅 (iS₂)²=−I 相位構造、IDCM odd sector 嘅 J²=−I（N_d=44）係**同一個 Z₄**（「一個代數物件，三種出現」）
- ✅ 判決：L4 由「構造存在」→「**嵌入代數**」（SU(2)-type skeleton：quaternion units + Hamilton relations）
- 🔴 未閉合：離散 2I skeleton ↔ 連續 SU(2) 嘅升格需要 limit 論證（未做）；elementwise spin-label 唔 claim

### R8 水位
- scripts 01–22 累計 **112 PASS + 1 記錄 REFUTED（G2）= 113 checks**（R1 21、R2 16+1R、R3 29、R4 14、R5 11、R6 6、R7 7、R8 8）
- docs/22；register：O188 notes ×1（R8）
- **誠實聲明**：R8 令 L4 由「最弱缺口」升為「有多重群論支撐」—— 同一 Z₄ 喺 L4a 構造、IDCM odd sector、2I cover 內部三處出現；L2 同 L4 而家由同一個群物件（2I）匯流