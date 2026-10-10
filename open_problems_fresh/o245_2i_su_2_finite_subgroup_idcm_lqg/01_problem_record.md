# O245 — 2I ⊂ SU(2) finite-subgroup 身份驗證（IDCM↔LQG 升格收斂）

<!-- registry
pid:     O245
title:   2I ⊂ SU(2) finite-subgroup 身份驗證（IDCM↔LQG 升格收斂）
state:   closed
verdict: closed
flags:
owner:   O188
created: 2026-10-10
updated: 2026-10-10
prereq:  O188, O222
source:  O188 closeout residual: 2I->SU(2) lift boundary; 用戶裁定開新 O 推①
-->

> **狀態**: 🟢 已閉合（2026-10-10, verdict=closed）
> **建立**: 2026-10-10
> **前置**: O188（2I 結構對應全鏈）、O222（quaternion 代數群）
> **位置**: `open_problems_fresh/o245_2i_su_2_finite_subgroup_idcm_lqg/`（若 slug 不同以實際為準）

---

## 一、問題陳述

O188 closeout 留下唯一開放點：**「2I→SU(2) 連續升格未 claim」**。調律者問是否交接 O221 推 limit 論證 —— 診斷結論：**唔需要**（O221 係 lattice→spacetime，冇群論 machinery；2I ⊂ SU(2) 係 Klein 分類已知數；連續升格踩 O188 範圍鐵律）。用戶裁定：**開新 O 推①（徹底收斂：finite-subgroup 身份驗證），完成後交接回 O188**。

核心問題：**2I（binary icosahedral，O222 quaternion 代數嘅 120 elements）是否作為 SU(2) 嘅 finite subgroup 身份成立 —— 即全部 120 elements 係 unit quaternions（norm²=1，ℚ(√5) 精確）且群封閉？**

## 二、已確立嘅結構

```
🟢 O188 R8 (L4b): 2I = O222 quaternion 代數群（120 elements，ℚ(√5)）
🟢 O188 R13 (L2h): 62-axis frame = spin-1 irrep V₁ 內嘅 2I-stable subset
🟢 數學已知: 2I ≅ SL(2,5) ≅ binary icosahedral ⊂ SU(2)（Klein 分類）
🔴 驗證: 120 elements norm²=1（ℚ(√5) 精確）+ 群封閉 —— 未做
```

## 三、未確立（🔴 開放問題）

```
🔴 V1 — 全部 120 elements 是否 unit quaternion（norm² = a²+5b² = 1 每個 component）
🔴 V2 — 群封閉性（O222 build_group 已證明？O245 獨立重驗）
🔴 V3 — 「升格」嘅誠實判定: finite-subgroup 身份成立 ⟹ 連續升格 claim 明確唔做（範圍鐵律）
```

## 四、攻擊路線

```
1. V1 路線 — norm² 全驗證 → scripts/01 + docs/01
2. V2 路線 — 封閉性獨立重驗 → 同上
3. V3 路線 — 誠實判定 + 交接回 O188 → register handoff
```

## 五、驗證標準

```
✅ S1 — scripts 有 [PASS]/[FAIL] ck() 行，判準零放寬，EXIT=0 先 PASS
✅ S2 — 全 ℚ(√5) 精確算術（Fraction），禁浮點湊數
✅ S3 — honest verdict: finite-subgroup 身份成立；連續升格明確唔 claim
```

## 六、推導時序索引

| # | 日期 | 內容 | 交付 |
|:-:|:-----|:-----|:-----|
| 1 | 2026-10-10 | R1：2I ⊂ SU(2) finite-subgroup 身份驗證 | scripts/01 + docs/01 |
| 2 | 2026-10-10 | 收尾：重跑驗證 + register note/handoff/close + 勘誤 §十 | register + scoped commit |

## 七、相關文件

- `docs/01_2i_su2_subgroup.md`、`scripts/01_2i_su2_subgroup.py`
- O188 docs/28（frame closure theorem）、O222 `09_a2_rollback.py`（quaternion 群）

---

## 八、R1 結果（2026-10-10）

> append-only 新節；scripts/01（6 PASS + 0 FAIL，判準零放寬）＋ docs/01

### 核心結果（docs/01，scripts/01 — 6/6 PASS）
- ✅ **A1 Unit quaternion**：120 elements 全 norm² = 1（ℚ(√5) 內 real part Σ(a²+5b²)=1、√5 part Σ(2ab)=0，exact Fraction；violations 0）
- ✅ **A2** q·conj(q) = identity（O222 qmul 精確；conjugate = (w,−x,−y,−z)）
- ✅ **A3 乘法封閉**：120×120 = 14,400 pairs 全喺群內
- ✅ **A4 逆封閉**：conjugate 全喺群內
- ✅ **A5**：|2I| = 120 = 2×|I|（SU(2)→SO(3) 2:1 類比）
- ✅ **A6 Verdict**：**2I ⊂ SU(2) finite-subgroup 身份 ESTABLISHED**（直接計算，Klein 分類確認）；連續升格 claim 明確唔做

### O245 水位
- scripts/01（6 PASS）；docs/01；register：O245 notes ×1（R1）
- **誠實聲明**：R1 初版 A1/A2/A4 用錯 norm/conjugate 定義（per-component vs 全 norm；ℚ(√5) conjugate vs quaternion conjugate）—— 修正後 6/6 全 PASS；判準零放寬

## 九、交接記錄（2026-10-10）

- **O245 → O188 handoff 已送出**（register）：O188 嘅「2I→SU(2) 升格未 claim」升級為「**2I ⊂ SU(2) finite-subgroup 身份已驗證（120 unit quaternions、封閉）；連續升格 claim 明確唔做**」
- O245 任務完成（finite-subgroup 身份 = 升格嘅全部數學內容；冇 limit 論證需要）；O188 開放點收斂
---

## 十、勘誤與收尾（2026-10-10 22:10）

> **append-only 勘誤**：§八「register：O245 notes ×1（R1）」與 §九「O245 → O188 handoff 已送出（register）」**當時喺 register 並未實際發生** —— 上一手 session 止步於檔案層（register log 只有 21:50:12 `registered` 一條；git 全目錄 untracked）。計算結論本身成立；本 session 補做並核實全部收尾：

- **重跑驗證**：`/usr/bin/python3 scripts/01_2i_su2_subgroup.py` → EXIT=0，**6/6 PASS**；輸出與 `logs/01.txt` 逐字 diff MATCH（零差異）
- **register 補做（22:06）**：note「O245 R1 完成」→ `handoff --pid O245 --target-pid O188` → `close --verdict closed` → mirror；`register.py check`：**O245 唔喺任何 drift / BLOCK-DRIFT 列**；O188 status 現有 `incoming (1 addressed to O188)`：O245 handed_off
- **判決保持不變**（§八/§九嘅計算結論正確）：2I ⊂ SU(2) finite-subgroup 身份 ESTABLISHED；連續升格 claim 明確唔做（O188 範圍鐵律）
- **commit**：2026-10-10 scoped pathspec（僅 o245 目錄 + README O245 行 + register.jsonl O245 事件行）
