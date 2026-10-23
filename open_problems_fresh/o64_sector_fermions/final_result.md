# O64 — 9 費米子質量階層：sector-dependent 幾何

## 狀態: 🟡 部分閉合（closeout 2026-10-11）

## 結論
結構框架成立（A₅ γ升序指派 + γ_n 譜 + 質量比恆等），但 C_f 生成器 5 線負閉合（O233）、鋸齒形證偽、斜率 5/7 盲測否證——質量生成機制交接 O209，9/9「閉合」降級為數值後驗（docs/04-09）。

## 關鍵公式
- m = M₀ · γ_n · C_f（M₀ = 27.9009 MeV, γ_n = 4sin²(nπ/88), C_f = m/(M₀γ_n) by-construction）
- A₅ γ升序指派（O137 授權）: e→1 u→2 d→3 s→4 μ→5 c→7 τ→9 b→11 t→13
- 質量比恆等: m_j/m_i ≡ (γ_j/γ_i)(C_j/C_i)（M₀ 抵消）
- c/s(混標度) = 13.597 vs O234 Nf=4 = 11.652（16.7% dev → 混標度已判死）

## 依賴
O57 → O64 → O209（質量生成機制交接）; O137（A₅ 指派）; O233（C_f 負閉合）; O234（scheme 基準）; O142（玻色子）

## 密度基準
- N_search = 不適用（closeout 係結構判決, 非數值閉合）
- 鋸齒 p: 真實質量 H0 = 0.067-0.073（證偽, docs/08）
- BIC: 單線 -4.94 最佳（證偽, docs/08）
- AUDIT: 32/32 PASS（scripts/AUDIT_independent_recheck.py, 2026-10-11）

> ⚠️ docs/03「9/9 閉合」係歷史快照, 已降級為數值後驗（docs/04）。原文保留。

<!-- conclusion-history:start -->
## 迭代史（machine-generated from register.conclusion；append-only）

| concl_hash | 日期 | verdict | 結論摘要 | 支撐 | 取代 |
|---|---|---|---|---|---|
| `0dad89d5bedcd9cf` | 2026-10-24 | partial | 結構框架成立（A₅ γ升序指派 + γn 譜 + 質量比恆等），但 Cf 生成器 5 線負閉合（O233）、鋸齒形證偽、斜率 5/7 盲測否證——質量生成機制交接 O209，9/9「閉合」降級為數值後驗（docs/04-09）。 | open_problems_fresh/o64_sector_fermions/final_result.md | — |
<!-- conclusion-history:end -->
