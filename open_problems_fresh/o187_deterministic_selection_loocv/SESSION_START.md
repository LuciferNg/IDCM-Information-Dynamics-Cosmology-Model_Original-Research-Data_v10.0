# O187 SESSION_START — Deterministic Selection Rule & LOOCV

<!-- registry
pid:     O187
title:   Deterministic Selection Rule & LOOCV（原 O143 duplicate 搬移）
state:   open
verdict: -
flags:   -
owner:   O187
created: 2026-10-04
updated: 2026-10-04
prereq:  O136, O65, O137
source:  O143 duplicate 搬移 (o143_deterministic_selection → O187, 2026-10-04)
-->

> **Session**: 2026-10-04（搬移建立）
> **狀態**: 🔴 開放研討（原 O143 分支）
> **來源**: 重複編號清理 — 原 `o143_deterministic_selection` 搬移至 O187
> **前置**: O136 🟡 (quark mass spectrum), O65 🟢 (CKM/PMNS), O137 🟢 (CY₃ 拓撲諧振)
> **位置**: `open_problems_fresh/o187_deterministic_selection_loocv/`

---

## 一、接手起點

**開放研討**。原 O143 分支：O136 費米子質量公式 `m = M₀ × γ_n × P_f` 中，`(n, P_f)` 配對選擇係後驗搜索（WSST 盲測發現 264 種組合搜索 8 個命中 = 數字遊戲風險）。核心問題：如何形式化 Deterministic Selection Rule + LOOCV 協議。

## 二、先做嘅第一步

```
（本 O 由原 o143_deterministic_selection 搬移 — 保持原內容原狀態）
```

## 三、已知陷阱

```
⚠️ 此係原 O143 嘅分支文檔（非主 O143）— 唔好與 o143_phase_selection_mechanism 混淆
⚠️ 後驗搜索 = 數字遊戲風險 — 唔可以閉合任何公式，除非有 deterministic selection rule
```

## 四、關鍵數字

| 量 | 值 | 出處 |
|:---|:---|:-----|
| 組合搜索 | 264 種 | WSST SM 盲測 |
| 命中數 | 8 | 同上 |
| 後驗風險 | 數字遊戲 | O136 診斷 |

## 五、交接 / 依賴

```
- 前置: O136 (quark mass spectrum, mode search) 🟡, O65 🟢, O137 🟢
- 範圍: Selection rule 形式化 + LOOCV 協議 — 唔做質量預言本身 (O136)
```

---

> ⚠️ **本檔係起手式快照，唔係狀態權威。**

---

## ✍️ 繼承鏈附註（2026-10-10 · append-only，O187 保持開放）

本題（Deterministic Selection Rule + LOOCV）自 2026-10-06 起已被後續 O 系列接管：

- **O209**（選擇律代數，識別層 🟢 已解）：Sel(𝒮)=G1∩G2={1,2,3,4,5,7,9,11,13}；閾值定理；唯一分配 t↔1..e↔13 (9! 窮舉)。詳見 `docs/02_handoff_inheritance.md`
- **O136/loocv-pointwise**（✅ closed）：冪律非逐點預言器，LOOCV 中位偏差 70.4%
- **O236**（🟡 partial）：質量譜形狀層（n槽位 × γ階梯 × C_f代際塊）
- **O144 審計線**：n_charm ∈ {25,27,33,34}，form-blind 先驗需 ~7 條約束

**O187 唔閉合**（調律者 2026-10-10 指示）：完整 deterministic selection rule + 零特例 LOOCV 仍未達成；本 O 作為母問題記錄保持 open，接收後續回流。
