# O23 — ΔE=0 節點符號匹配率

## 狀態: 🟢 已閉合

## 結論
ΔE=0 節點符號匹配率 75% vs 非 ΔE=0 58% 無統計顯著差異 (Fisher p=0.34)，差異係隨機波動 + 低 |T| 集中假象。Coloring 係 BFS parity 完美 bipartite 2-coloring（圖論性質），唔係 temperature prediction；弱信號 ρ~0.24 (p~0.06) 反映 CMB 大尺度微弱 spatial correlation，非地圖 artifact。

## 關鍵公式
- Fisher exact: 列聯表 [[9,3],[28,20]], OR = (9×20)/(3×28) = 2.14, p = 0.34 (two-sided) ❌
- Bootstrap: P(匹配率 ≥75% | 隨機抽 12) = 0.24 ❌
- Logistic: z = β₀ + β₁|T|_std + β₂·zeroE, β₂ = 0.93 [-0.51, 34.7] ❌
- Spearman: ρ = 0.241 (p = 0.064) ❌
- Power: detect 75% vs 58% 需 ~248 節點 (得 60, underpowered)
- BFS parity: even→cold, odd→hot, 100% 交替 ✅

## 依賴
O3 → O23

<!-- conclusion-history:start -->
## 迭代史（machine-generated from register.conclusion；append-only）

| concl_hash | 日期 | verdict | 結論摘要 | 支撐 | 取代 |
|---|---|---|---|---|---|
| `92fc6346a688beac` | 2026-10-24 | — | ΔE=0 節點符號匹配率 75% vs 非 ΔE=0 58% 無統計顯著差異 (Fisher p=0.34)，差異係隨機波動 + 低 \|T\| 集中假象。Coloring 係 BFS parity 完美 bipartite 2-colori… | open_problems_fresh/o23_zeroE_sign_match/final_result.md | — |
<!-- conclusion-history:end -->
