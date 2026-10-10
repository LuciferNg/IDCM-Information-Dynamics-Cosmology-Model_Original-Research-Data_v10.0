# O188 — IDCM ↔ LQG 結構對應

<!-- registry
pid:     O188
title:   IDCM ↔ LQG 結構對應（離散晶格 vs 圈量子重力）
state:   partial
verdict: partial
flags:   R1-L1L4
owner:   O188
created: 2026-10-04
updated: 2026-10-04
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