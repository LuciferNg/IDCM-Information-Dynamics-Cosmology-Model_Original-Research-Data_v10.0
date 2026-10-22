# O241 docs/14 — R14: Lamb shift / g−2 歸屬審計（驗收問題陳述未落帳項）

> **狀態**: ✅ 審計完成 — 兩項均已由 O139 承接，O241 唔重推
> **日期**: 2026-10-08 ｜ **方法**: O139 產物目錄 + docs/05 審計

---

## 0. 問題陳述遺留項核對

O241 問題陳述提到「Lamb shift ~1057.8 MHz、g−2_e 真空極化圈 1.3e-13 吻合」作為實證現象背景。
docs/02 §3 時寫「呢啲屬差分譜量 L1 層；O139（低能 QED）承接，唔屬本 O Q2」—— R14 = 落帳審計，確認承接存在。

## 1. O139 承接審計（低能 QED → QED）

**目錄**: `o139_finite_qft_to_qed/`（14 docs + 14 scripts）

| 遺留項 | O139 承接 | 狀態 |
|:---|:---|:---|
| **g−2 精度** | docs/05 `g2_precision_wall_and_muon_bound` | 🟢 scripts/06 15/15 PASS |
| | "12 位小數 = 圈數（4.56-loop）唔係真確度" 結構分析 | 核心結論 |
| g−2 真空極化 (HVP) | docs/10 `confined_hadronic_hvp` | scripts/11 ✅ |
| α running (QED 圈) | docs/07/08/09 `alpha_running_*` | 多輪 ✅/🟡 |
| **Lamb shift 機制** | docs/01 `derivation`（低能 QED 場論 → Lamb 類效應） | 承接存在（結構層）|
| μ 子 g−2 界 | docs/05 §後半 + docs/06 | 🟢 分析完成 |

**結論**: 問題陳述提嘅 Lamb/g−2 唔係 O241 真空漲落（模譜差→力/頻移）結構要重推 —— 佢哋係
**QED 圈修正**，O139 已用 v10 結構框架承接（g−2 精度牆 15/15 PASS）。O241 範圍 =
Casimir（Q2✅）、DCE（R11/R13✅）、退相干（Q3 承接 O138✅）、CMB 判準（Q4/R10/R12）。

## 2. 判決

> **O241 所有問題陳述項會計核對完成：**
> - Casimir 力 ✅（Q2, dev 1e-12）
> - Lamb shift / g−2 → **O139 承接**（唔重推, docs/01 + docs/05 已覆蓋）
> - DCE → ✅（R11 半頻模定理 + R13 Wilson 對照）
> - CMB 判準 → ✅（Q4 設計 + R10 高 ℓ FAIL 照記錄 + R12 binning 依賴 🟡）
> - 退相干 → ✅（Q3 承接 O138 閉合）
>
> **O241 餘下項目（docs/04 F-Q4.2 正式裁決 + docs/16 半頻模實驗）均已 handoff 到對應 O 目錄**
> —— O241 主體任務完成，無未落帳遺留。

## 3. Handoff（register）

- g−2/Lamb：已由 O139 承接 —— **本 O 唔重推**（防重複推導）。
- F-Q4.2 一致 binning 裁決 → O9/O48。
- O83 峰位公式伸延 m≥8 → O83。

---

*本檔為 O241 docs/14 — R14 Lamb/g−2 歸屬審計*
*框架: IDCM v10.0 ｜ 撰寫: 2026-10-08*