# O245 — 2I ⊂ SU(2) finite-subgroup 身份驗證（IDCM↔LQG 升格收斂）

## 狀態: 🟢 已閉合（2026-10-10, verdict=closed）

## 結論
2I（binary icosahedral，O222 quaternion 代數嘅 120 elements）作為 SU(2) 嘅 finite subgroup 身份，由直接計算建立：全部 120 elements 係 unit quaternions（ℚ(√5) 精確），乘法封閉、逆封閉。連續升格 claim 明確唔做（O188 範圍鐵律）。O188 closeout 唯一開放點收斂。

## 關鍵公式
- norm²(q) = Σ_comp (a² + 5b², 2ab) = (1, 0)，a,b ∈ ℚ → 每個 element 單位范數
- |2I| = 120 = 2×|I| = 2×60（SU(2)→SO(3) double-cover 計數）
- 2I ≅ SL(2,5) ⊂ SU(2)（Klein 分類；直接計算確認，唔靠引用）

## 依賴
O188 → O222 → O245（handoff 回 O188：身份已驗證；升格唔 claim）

## 密度基準
- N_search = 1（純代數恆等式：群封閉＋norm 條件係唯一候選 → O208 規則跳過 MC）
- N_mc = 不適用（冇分位數 claim；scripts/01 6/6 PASS，判準零放寬）

> R1：scripts/01 = 6 PASS + 0 FAIL，EXIT=0（A1 unit quaternions / A2 q·conj(q)=1 / A3 乘法封閉 120×120 / A4 逆封閉 / A5 double-cover / A6 verdict）