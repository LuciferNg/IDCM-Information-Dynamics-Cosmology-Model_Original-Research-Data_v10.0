# Record 13 — 閉合延伸: E_strain 75 譜身份 + b₀ 降級 + δ→scatter (2026-09-09)

狀態: 🟢 75 = L₄L₅−μ² (E_strain 全譜量化) / ✅ b₀ 候選降級 (外推量) / 🟡 δ 解釋 53% scatter
Script: `scripts/20_closure_extensions.py` (重跑 exit 0 ✅)
Data: `data/20_closure_extensions.json`

---

## 1. E_strain 閉合形式全面譜量化 🟢

**新發現：75 = L₄L₅ − μ² = 7×11 − 2 = 77 − 2**（全部基本譜量）

E_strain 閉合形式（record 07）升級：

    E_strain = (π²/75)·M_Pl·(R_H/L_P)·44⁻⁶
             = (π²/(L₄L₅−μ²))·M_Pl·(R_H/L_P)·N_d^{−2N_gen}

| 因子 | 舊 | 新身份 |
|:-----|:--:|:-------|
| 75 | 冇身份 | **L₄L₅ − μ² = 77 − 2** |
| 44⁻⁶ | N_d | N_d^{−2N_gen}（6 = 2×3）|
| π² | 幾何常數 | 圓（世界 = 環/球）— 唔需要譜身份 |

**驗證**：E_new = 3.1135e42 kg vs E_old = 3.1121e42 → dev 0.046%（script 13 用精確常數 0.0045% — 一致）

→ 閉合形式分母同指數**全部由譜量生成**（L₄, L₅, μ², N_d, N_gen），唯一非譜量係 π（連續幾何）。

## 2. b₀ = 12/5 候選降級 ✅（誠實）

**評估**：b₀（β 跑動 intercept）係 ℓ=0 嘅外推 — 對應 z=0，LRD 唔存在 → **冇直接觀測意義**。naive intercept 2.3886（dev −0.47% vs 12/5）受 115-150 噪聲對污染（未加權 fit）。

**裁決**：b₀ = (B·N_gen)/F₅ = 12/5 候選**唔入列** — 外推量 + 受污染 + 判別力低。避免 numerology 滑梯（φ-power trap 教訓）。

**保留**：β(ℓ) = β₀ + (88/21)·ℓ 喺觀測範圍 ℓ∈[0.68, 1.70] 內嘅跑動先係物理（0.22σ 閉合不變）。

## 3. δ 分佈 → 質量 scatter 🟡

**預測**：M ∝ (1+δ)^{3/2} → log M scatter = (3/2)·σ[log₁₀(1+δ)]

- δ ∈ [0.32, 3.34]（script 14, log 均勻模擬）→ σ[log₁₀(1+δ)] = 0.151
- 預測 log M scatter = **0.226 dex**
- 觀測 logLbol scatter = **0.428 dex**（script 11）
- **δ 分佈解釋 53%** 光度 scatter；剩餘 47% → Eddington ratio scatter（record 12: LRD ≈ 10% 效率，圍繞中位數有散佈）

**意義**：環境（δ）同 Eddington（λ）雙 scatter 源 — logLbol scatter 分解 53/47，同紅化雙分量（塵埃/結構）嘅結構平行。

## 4. 開放問題更新

| # | 狀態 | 問題 |
|---|------|------|
| 23 | ✅ 降級 | b₀ = 12/5 候選 — 外推量, 判別力低, 唔入列 |
| 24 | 🆕 | E_strain 嘅 π² 來源（幾何常數 — 世界環/球結構嘅直接後果? 需要第一性原理）|
| 25 | 🆕 🟡 | logLbol scatter 53/47 分解（δ/Eddington）— 需要光譜質量驗證 λ scatter |

## 5. 驗證

- `python3 scripts/20_closure_extensions.py` → exit 0
- Part A: 75 = L₄L₅−μ² ✓; E dev 0.046%
- Part C: δ → 0.226 dex = 53% 觀測 scatter
