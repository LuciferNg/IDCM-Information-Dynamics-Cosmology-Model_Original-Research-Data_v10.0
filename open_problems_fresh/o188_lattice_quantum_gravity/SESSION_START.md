# O188 SESSION_START — IDCM ↔ LQG 結構對應

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

> **Session**: 2026-10-04（新建立）
> **狀態**: 🔴 已註冊 — 未開始
> **來源**: O231 調查發現 IDCM 無 LQG 對應 O 系列；調律者裁定開 O188（墓碑重用）
> **前置**: O222 (QM 求值語義對應), O221 (低能連續極限), O86 (SM×GR), O213 (世界演化方程)
> **位置**: `open_problems_fresh/o188_lattice_quantum_gravity/`

---

## 一、接手起點

未開始。調律者指示：目標與 O222(QM)/O221(GR) 一樣，**研究 IDCM 離散晶格與 LQG 概念之間的結構對應，非以 IDCM 導出 LQG**。

## 二、先做嘅第一步

```
1. 讀 O221 (低能連續極限, GR correspondence)、O222 (QM 求值語義, 方法論 precedent)
2. 讀 LQG 基本文獻（spin network 定義、Ashtekar 變數、Hamiltonian 約束、spin foam）
3. 寫 docs/01_lattice_comparison.md — 離散結構層 (88-site chain vs 3D spin network)
4. 寫 docs/02_causal_structure.md — IDCM 因果 rank ≤3 vs LQG spin foam causality
5. 寫 docs/03_continuum_limit.md — IDCM→GR vs LQG→GR 連續極限比較
```

## 三、已知陷阱

```
⚠️ LQG 用 3D spin network，IDCM 用 1D chain + tree — 維度不對應要誠實標記，不可強行對應
⚠️ LQG 有 Hamiltonian 約束（微分同胚不變性），IDCM 無此概念
⚠️ O222 方法論：thunk/force 語義與 QM 自然對譯；LQG 的 spin 代數與 IDCM 譜代數能否對語不保證
⚠️ 不可宣稱「IDCM 是 LQG 的一種實現」— 目標係結構對應，非同一理論
```

## 四、關鍵數字

| 量 | 值 | 出處 |
|:---|:---|:-----|
| IDCM 鏈 site 數 | N_d = 44 (88-site dual) | O95 |
| IDCM 因果張量 rank | sign_rank(K) ≤ 3 | O222 |
| O221 連續極限 | L7 細化流 4:1 decimation | O221 |
| O213 世界演化 | 細化流 ℓ 為演化參數 | O213 |

## 五、交接 / 依賴

```
- 前置: O222 (因果張量秩≤3, QM 對應方法論), O221 (低能連續極限 L7 decimation→GR)
- 前置: O86 (SM×IDCM×GR 耦合 Lagrangian), O213 (細化流演化方程)
- 範圍: 唔推導 LQG（不涉 Ashtekar 變數的物理實現）
- 範圍: 唔以 IDCM 重建 LQG（目標為結構對應）
```

---

## Session 2026-10-04（第一輪，L1–L4）

- **交付**：scripts/01–04（21/21 PASS，logs/01–04.txt）＋ docs/01–04（對應項/非對應項表）
- **結論摘要**：
  - L1（docs/01）圖×標籤二象 + 離散譜 = 真對應；維度（1D vs 3D）與標籤來源（譜 vs 表示）非對應
  - L2（docs/02）sign_rank(K)=3（O222 引用）vs spin foam causality = 直覺對應，冇形式化定理；數字 4 巧合候選明確不宣稱
  - L3（docs/03）**Regge 作用量係共同物件**（最強對應）；graviton dof=2 一致；極限程序本質分歧（IDCM 零參數 vs LQG Immirzi）
  - L4（docs/04）**最弱路線**：J²=−1 複結構/能量預算/扇區固定性皆 IDCM 獨有，LQG QRF 冇
- **引用確認**：O222 sign_rank(K)=3（R20 M3，非早期 [5,6]）；O159 J²=−1 odd sector 本輪精確認證（dev 2e-14）
- **記錄**：01_problem_record §八（append-only）＋ register 兩條 note
- **狀態**：🟡 partial（對應表建立；形式化定理缺口 4 項列於 §八）

---

> ⚠️ **本檔係起手式快照，唔係狀態權威。**