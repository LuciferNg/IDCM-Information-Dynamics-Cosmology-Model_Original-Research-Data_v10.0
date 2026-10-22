# O153 docs/00 — IDM v1.0–v4.0 降級數字考古摘錄

> **日期**: 2026-09-06
> **目的**: 原文出處索引（重新研究嘅 source material）

---

## IDM v1.0（Information Dynamics Cosmology）

| 檔案 | 內容 |
|:-----|:-----|
| `docs/IDM_paper_v1.0.md` | ε = α/√N_horizon, N_horizon ≈ 44, z_c ≈ 0.6, 零自由參數宣稱 |
| `docs/IDM_narrative_part1.md` §3.2 | N_horizon ≈ 44 直覺（視線因果域計數）; MCMC 反推 α²/ε² ≈ 42 同 44 差 4% |
| `docs/idm_final_conclusion.md` | ε = α/√N_horizon, N_horizon = 44 作為最終閉合公式 |
| `docs/IDM_paper_v4.0_zh.md` | n_horizon_first_principles.py: 幾何計數 (1D/2D/3D) vs CLT; √(N₂×N₃) = 40.2 vs CLT 41.9（4% 吻合, CLT branch 限定） |

## IDM v3.0（Domain Framework）

| 檔案 | 內容 |
|:-----|:-----|
| `01-core/domain_framework_derivation.md` | 四域 (Planck 1, Cosmic 44, Galaxy 10⁶, EW 2.5×10³³); Axiom 2 CLT Forcing ε = α/√N; Domain Independence Theorem; Phase Resolution Theorem; λ/ε≈0.84 跨域巧合判死 |
| `02-theorems-proofs/ew_domain_oas_structure.md` | N_EW = (M_Pl/v)² = 2.5×10³³; 自認 tautology; gauge = address conservation; 3 世代 origin 開放 |
| `03-extensions/d_alpha_clt_constant.md` | α = √(⟨k²⟩−⟨k⟩²); α ≈ 1 → scale-free network claim; α=1.025 exact ❌ |
| `04-predictions-verification/q7_alpha_exact.md` | α = √(π²/6−1) ≈ 1.026（**算術錯誤**, 實際 0.8031 — O153 修正） |
| `04-predictions-verification/q9_ncrit_exact.md` | N_crit = (4π/α)² ≈ 150; N_cont ≈ 1.5×10⁴; galaxy intermediate |

## IDM v4.0（Consistency Field Applied Science）

| 檔案 | 內容 |
|:-----|:-----|
| `references/parallel-researchers.md` | 四域 (44, 4, 10⁶, 3) 宣傳為「domain decomposition」 |
| `core/` | CLT/ε 繼續沿用 v3.0 框架 |

## 降級軌跡（v5+）

- IDCM v5.0–v6.0: OAS/CLT 語言逐步退場, 引入 K_Chain 譜
- IDCM v9.0–v10.0: 88-site 對偶鏈 γ_n = 4sin²(πn/88) 成為核心; ε_exact = 19/123 (O148) 取代 φ⁻¹/4; 44 由 O95 唯一性閉合
- O153（本項目）: 將 v1.0–v4.0 降級數字逐一 re-frame 到譜幾何/FSR 語言

## 關鍵教訓（由 O153 第一輪確立）

1. ε 嘅「CLT」名義係統計巧合 — 結構身份係投影比率 (f_proj/f_unproj)/N_gen = 19/123
2. MCMC 42 = 1/ε² 係 α=1 artifact — 唔係「44 嘅競爭者」
3. N_EW tautology 從 v3.0 到而家都未解決 — 誠實保持 🔴
4. 四域架構嘅 Domain Independence meta-lesson 仍然有效（大數冇算子身份, script 05 零命中）
