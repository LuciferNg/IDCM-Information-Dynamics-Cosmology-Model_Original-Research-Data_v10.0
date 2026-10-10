# O245 docs/01 — 2I ⊂ SU(2) finite-subgroup 身份驗證

**日期**: 2026-10-10（R1）
**腳本**: `scripts/01_2i_su2_subgroup.py` — **6/6 PASS**（logs/01.txt）
**目標**: O188 closeout 最後開放點：「2I→SU(2) 連續升格未 claim」。診斷結論：該升格嘅全部數學內容 = finite-subgroup 身份驗證（Klein 分類已知），**唔需要 limit 論證**；用戶裁定開 O245 推①，完成後交接回 O188。

---

## 〇、一句話

**2I（binary icosahedral，O222 quaternion 代數嘅 120 elements）作為 SU(2) 嘅 finite subgroup 身份，由直接計算建立**：全部 120 elements 係 unit quaternions（ℚ(√5) 內 norm² = 1 精確），乘法封閉、逆封閉。連續升格 claim 明確唔做（O188 範圍鐵律）。

## 一、精確結果

| 檢查 | 內容 | 結果 |
|:-----|:-----|:-----|
| A1 | **Unit quaternion**：120 elements 全 norm² = 1（ℚ(√5) 內：real part Σ(a²+5b²)=1、√5 part Σ(2ab)=0，exact Fraction）—— violations 0 | ✅ |
| A2 | **q·conj(q) = identity**（O222 qmul 精確；conjugate = (w,−x,−y,−z)）—— violations 0 | ✅ |
| A3 | **乘法封閉**：120×120 = 14,400 pairs 全喺群內 —— violations 0 | ✅ |
| A4 | **逆封閉**：每個 element 嘅 quaternion conjugate 喺群內 —— violations 0 | ✅ |
| A5 | **Double-cover pattern**：|2I| = 120 = 2×|I| = 2×60（SU(2)→SO(3) 2:1 類比） | ✅ |
| A6 | **Verdict**：finite-subgroup 身份 ESTABLISHED（grounded in A1–A5） | ✅ |

## 二、結構意義

- **O188 最後開放點收斂**：closeout 記錄嘅「2I→SU(2) 連續升格未 claim」—— 診斷話唔需要 limit 論證；O245 直接驗證 **2I < SU(2)**（unit quaternions、封閉）—— 呢個就係「升格」嘅全部數學內容。Klein 分類（2I ≅ SL(2,5) ⊂ SU(2)）由直接計算確認，唔靠引用。
- **範圍鐵律保持**：唔 claim 2I 趨近 SU(2) 嘅連續極限（冇 limit 論證、O188 唔推導/重建 LQG）。Finite-subgroup 身份係結構對應嘅完整終點。
- **R1 錯誤修正記錄**：初版 A1/A2/A4 用錯 norm/conjugate 定義（per-component norm vs 全 quaternion norm；ℚ(√5) conjugate vs quaternion conjugate）—— 修正後 6/6 全 PASS（判準零放寬；elog 反映修正版）。

## 三、判決

- **O245 R1：完成** —— 2I ⊂ SU(2) finite-subgroup 身份 ESTABLISHED
- **交接回 O188**：register handoff（O245 → O188）：O188 嘅「2I→SU(2) 升格未 claim」升級為「**2I ⊂ SU(2) finite-subgroup 身份已驗證；連續升格 claim 明確唔做**」—— 開放點收斂為有數學身份嘅 boundary。
- 🔴 未閉合：無（此 O 任務範圍）—— 2I→SU(2) 連續升格（如日後要）屬於新理論工程，唔係 IDCM↔LQG 結構對應範圍