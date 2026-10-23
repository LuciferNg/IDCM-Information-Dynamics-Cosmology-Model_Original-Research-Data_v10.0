# O161 — 離散作用量 + Noether 電荷 + 鏈變數結構

## 狀態: 🟢 已閉合 (T1-T3 + R1-R4, 94/94 PASS, 2026-09-08)

## 結論
O159 靜態場論嘅動態層延續完成: 離散 Noether 電流 (J + 守恆律 + Q = 44 總通量)、
link 變數由譜導出 (U_k = e^{ikπ/88}, γ_k = |1−U_k|²)、Wilson line = i (總相位
(F₁₁/2)π = 44.5π, holonomy 階 4 = B, i² = −1 ⟹ J², i⁴ = 1 ⟹ 352 閉合)、
約束乘子 λ = 1 重現 μ² = 2λ = 2 (四重身份)。零新參數。

## 關鍵公式
- **T1 電荷算子**: w_k = (−1)^k·k; Q̂ = Σ_k w_k P_k; Q = ⟨Q̂⟩ = Σ_even k − Σ_odd k = 44 = N_d (規範不變)
- **T1 電流**: J_{j,j+1} = Im(φ*_j (Q̂φ)_{j+1}) (site); J_{k,k+1} = Im(Φ*_k U Φ_{k+1}) (mode)
- **T1 守恆**: 駐態無散 (bulk 恆等 ⟹ J_j = J_{j−1}); 反稱 ⟹ 總通量 0; 均勻流 ⟹ ΣJ = 0
- **T1 電荷 = 譜流通量**: staircase J_k = Σ_{j≤k}w_j = (−1)^k⌈k/2⌉; Q = J_88 = 44; Σ|J_k| = 1980 = Σ_even k
- **T2 link 變數**: U_k = e^{i·2θ_k} = e^{ikπ/88}; **γ_k = |1 − U_k|²** (譜 = link 振幅平方)
- **T2 connection link-form**: ΔA_k = Δγ_k (link = 譜斜率); A_{k+88} = −A_k (反週期)
- **T2 Wilson line**: Π_k U_k = **i** — 總相位 44.5π = (F₁₁/2)π; 世界 i / 觀察者 1; winding 22.25 = F₁₁/4 = 2L₅ + ¼; i² = −1 (J²), i⁴ = 1 (352 = B·N_d)
- **T2 Wilson loop**: e^{i·88·2θ_k} = e^{ikπ} = (−1)^k (扇區 Z₂ 週期因子)
- **T3 乘子**: S' = S + λ·C, C = Σ_even|Φ|² − Σ_odd|Φ|² (Δ = 0); 扇區隙 2λ = E−O = 2 ⟹ λ = 1; **μ² = 2λ = 2** (四重身份: μ² = E−O = γ₄₄ = BC-cost = 2λ)
- **T3 轉移成本**: ΔS'(transfer δ) = 2λδ = μ²δ (質量 = sector-locking 價格)

## 依賴
O159 (92/92) → O161 (94/94) → O122 (feynman_rules_wfield 對接)

<!-- conclusion-history:start -->
## 迭代史（machine-generated from register.conclusion；append-only）

| concl_hash | 日期 | verdict | 結論摘要 | 支撐 | 取代 |
|---|---|---|---|---|---|
| `d0edeaaf920a2b7e` | 2026-10-24 | closed | O159 靜態場論嘅動態層延續完成: 離散 Noether 電流 (J + 守恆律 + Q = 44 總通量)、 link 變數由譜導出 (Uk = e^{ikπ/88}, γk = \|1−Uk\|²)、Wilson line = i (總… | open_problems_fresh/o161_discrete_action_noether/final_result.md | — |
<!-- conclusion-history:end -->
