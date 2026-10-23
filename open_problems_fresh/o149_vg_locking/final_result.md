# O149 — 群速度鎖定（v_g Locking）

## 狀態: 🟡 部分閉合（受抑制扇區 2/2 先驗鎖定；中等/大角扇區開放）

## 結論
CKM/PMNS 混合角可以由 K_Chain 色散結構**先驗鎖定**：兩個受抑制 CKM 元素（sinθ₁₃、V_ub）由 k-ladder 規則以 **0 自由參數**鎖定（p_joint = 9.64e-10），取代 O146 §10 揭發嘅後驗搜索（831,713 候選）。中等/大角扇區 9/11 仍開放（docs 公式保持後驗標記）。

## 關鍵公式
- **定理 1**（946/946 ✅）: `beat(a,b) = 4·sin(dπ/176)·v_g((a+b)/2)`，d = b−a（O146 §10 d=1 恆等式嘅全推廣）
- **定理 2**（44/44 ✅，Z₂ 對偶字典）: `ω_n = 2·v_g(44−n)`；`γ_n = 4·v_g(44−n)²` → O65 γ-ratio 家族 = v_g²-ratio 家族
- **定理 3**（floor）: 相鄰對 ratio ≥ `sin(π/176)/cos(3π/176) = 0.017875`（tight；loose: sin(π/176) = 0.017849）→ sinθ₁₃ = 0.00351、V_ub = 0.00369 **< floor → 兩因子必然**；V_cb、PMNS 全部 > floor → 純 v_g 可達（結構預言與觀測一致）
- **定理 4**（k-ladder，先驗，0 自由參數）: `g_k = beat(44−k, 44−k+1) / beat(44−(k+1), F_{k+6})`
  - k=2 → **sinθ₁₃ = 0.00350743**（精確）
  - k=3 → **V_ub = 0.00369102**（精確）
  - k=4 → 無解（F₁₀ = 55 > 39）→ 階梯自然終止於 2 級 = CKM 兩個受抑制元素
- 盲測 **3/4 PASS**（階梯終止、PMNS 無抑制、V_td 第三機制）；🟡 V_td = beat(40,42)/beat(3,42) = 0.0085684 係搜索產物

## 獨立驗證
25/25 PASS（`scripts/99_independent_verifier.py`，mpmath 高精度、獨立 code path）；docs 11 條公式值、統計（831,713 / 23 / 29 / p=9.64e-10 / 1,806 / 8/11）、分母 mean 聚類 11/11 全部重算一致；tight floor 修正已入 docs §五/§十三。

## 開放問題
1. k-ladder 分母規則 `d = F_{k+6}`, `sum = 44−(k+1)` 嘅代數起源 🟡（O142 T̂ 轉移矩陣框架候選）
2. V_td 第三機制 🔴（新 O 建議）
3. 中等扇區 9 角先驗規則 🔴（需要 k-ladder 嘅中等類比）

## 依賴
O146 → O149（O65 交叉: γ-ratio = v_g²-ratio）

<!-- conclusion-history:start -->
## 迭代史（machine-generated from register.conclusion；append-only）

| concl_hash | 日期 | verdict | 結論摘要 | 支撐 | 取代 |
|---|---|---|---|---|---|
| `9cde85346cbae35a` | 2026-10-24 | partial | CKM/PMNS 混合角可以由 KChain 色散結構先驗鎖定：兩個受抑制 CKM 元素（sinθ₁₃、Vub）由 k-ladder 規則以 0 自由參數鎖定（pjoint = 9.64e-10），取代 O146 §10 揭發嘅後驗搜索（… | open_problems_fresh/o149_vg_locking/final_result.md | — |
<!-- conclusion-history:end -->
