# O258 — m_ββ Majorana 相位理論: 由 dim-5 算符推導 (α,β) 相位結構, 帶 [6.108, 22.169] meV 內預言

<!-- registry
pid:     O258
title:   m_ββ Majorana 相位理論: 由 dim-5 算符推導 (α,β) 相位結構, 帶 [6.108, 22.169] meV 內預言
state:   registered
verdict: -
flags:   -
owner:   O258
created: 2026-10-21
updated: 2026-10-21
prereq:  P6, O49, O66, O123
source:  P6 docs/10_closeout_20261020.md 剩餘項 #3
-->

> **狀態**: 📄 **已註冊 — 未開始**
> **建立**: 2026-10-21
> **前置**: P6（來源）、O49（中微子質量）、O66（M_comp）、O123（δ_CP）
> **位置**: `open_problems_fresh/o258_mbb_majorana_phase/`

---

## 一、問題陳述

m_ββ 帶 **[6.108, 22.169] meV**（P6 docs/03 重算確證；上界 = M_ee 全相長，下界 6.108 實現於 (φ₁,φ₂)≈(π,π)）。剩餘問題：IDCM 冇 dim-5 算符相位理論 —— (α,β) Majorana 相位嘅結構出處未推導；6.108 下界唔排除 CP（(π,π) 全相消亦 CP 守恆，P6 docs/06 修正）；候選 (α=π/2, β=δ/2)=6.321 meV 無結構必要性。

## 二、已確立嘅結構

```
🟢 m_ββ ∈ [6.108, 22.169] meV（P6 docs/03 重算；16 位 mpmath 驗證）
🟢 上界 = M_ee 全相長；下界 6.108 由 (φ₁,φ₂)≈(π,π) 實現
🟢 CP 守恆唔排除 6.108 —— (π,π) 全相消亦 CP 守恆（docs/06 修正，撤回舊「6.108 唔 CP」讀法）
🟢 δ_CP = 211.717474°（O123）；M₂₃ = 15.185 meV；J_CP = −0.0176（NuFIT −0.0178 ✓）
🔴 Majorana 相位 (α,β) 嘅 IDCM 結構出處 —— 未推導
🔴 dim-5 Weinberg 算符喺 IDCM 嘅對應物 —— 未建立
```

## 三、未確立（🔴 開放問題）

```
🔴 Q1: (α,β) 由 K_Chain/K_Tree/causal tensor 邊個結構決定？
🔴 Q2: dim-5 算符嘅 IDCM 對應（質量項點樣由 W-field 產生 Majorana 質量）
🔴 Q3: m_ββ 帶內預言 —— 唯一值 or 窄帶，邊個可證偽
```

## 四、攻擊路線

```
1. dim-5 Weinberg 算符 → IDCM 對應（O49/O66 質量鏈基礎）→ 高
2. δ_CP 統一式（O123: δ=arg(Z)+atan|Z|）擴展至 Majorana 相位 → 中
3. K_Chain 譜相位（π·rational 結構）→ m_ββ 預言閉合 → 中
```

> ⚠️ **只註冊禁推**（調律者 2026-10-21）：本 O 只開不推，scripts/docs/data 零建立。攻擊路線僅列參考。

## 五、驗證標準

```
✅ 由已確立結構（非反解）推出 (α,β) 或 m_ββ 唯一預言
✅ 預言喺 [6.108, 22.169] meV 帶內
✅ 樣本外可證偽（0νββ 實驗未來測量）
```

**四道硬測試**（閉合宣稱必過）：
① 自由度成本（零參數）② Monte-Carlo null（10⁷ 樣本，5σ）
③ 可證偽 + 樣本外盲測 ④ 結構剛性（微擾測試）

## 六、推導時序索引

> ⚠️ **只可 append 新行，禁回溯污染舊行。**

| # | 日期 | 事件 | 產物 |
|:-:|:-----|:-----|:-----|
| 1 | 2026-10-21 | 註冊（承接 P6 剩餘項 #3，只開不推） | P6 docs/10_closeout_20261020.md |

## 七、相關文件

```
- P6 (main_problems/p6_neutrino) — 來源；docs/03 m_ββ 重算、docs/06 CP 修正、docs/10 closeout 剩餘項 #3
- O49 (o49_neutrino_mass) — 中微子質量譜
- O66 (o66_mcomp_first_principles) — M_comp（質量公式核心）
- O123 (o123_neutrino_delta_cp) — δ_CP 閉合
- 禁區: 6.321 meV 候選（(α=π/2, β=δ/2)）已標「無結構必要性」，禁當閉合引用
```