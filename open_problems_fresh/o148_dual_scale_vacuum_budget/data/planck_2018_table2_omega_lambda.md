# O148 data — Planck 2018 Ω_Λ 實證錨點 (Browser 驗證)

> **日期**: 2026-09-05 | **方法**: browser CLI (HeadlessChrome 147, CDP 9222, WSL)
> **來源**:
> 1. Wikipedia "Lambda-CDM model" 參數表 (2026-09-05 快照) — https://en.wikipedia.org/wiki/Lambda-CDM_model
> 2. **主來源**: Planck 2018 results VI. Cosmological parameters, Table 2 — arXiv:1807.06209 (ar5iv HTML: https://ar5iv.labs.arxiv.org/html/1807.06209)

## 1. Planck 2018 Table 2 — Ω_Λ 全行 (直接擷取 ar5iv DOM)

| 資料組合 | Ω_Λ | Ω_m | H₀ [km/s/Mpc] |
|:---------|:-----|:-----|:---------------|
| TT+lowE | 0.679 ± 0.013 | 0.321 ± 0.013 | 66.88 ± 0.92 |
| TE+lowE | 0.699 ± 0.012 | 0.301 ± 0.012 | 68.44 ± 0.91 |
| EE+lowE | 0.711 +0.033/−0.026 | 0.289 +0.026/−0.033 | 69.9 ± 2.7 |
| **TT,TE,EE+lowE** | **0.6834 ± 0.0084** | 0.3166 ± 0.0084 | 67.27 ± 0.60 |
| **TT,TE,EE+lowE+lensing** | **0.6847 ± 0.0073** | 0.3153 ± 0.0073 | 67.36 ± 0.54 |
| TT,TE,EE+lowE+lensing+BAO | 0.6889 ± 0.0056 | 0.3111 ± 0.0056 | 67.66 ± 0.42 |

## 2. Gemini 引用審計 (docs/01 C2 實證化)

Gemini 引用 **「Planck 68.34% ± 0.56%」= 0.6834 ± 0.0056**:

- **中心 0.6834 = 真實** → Planck 2018 **TT,TE,EE+lowE** 組合嘅 Ω_Λ (68.34%)。
- **誤差 ±0.0056 = 錯位** → 0.0056 係 **TT,TE,EE+lowE+lensing+BAO** 行嘅誤差 (該行中心係 0.6889, 唔係 0.6834)。
- **組合 (0.6834, ±0.0056) 喺 Planck Table 2 唔存在** — 混行數 (中心取自第 4 行, 誤差取自第 6 行)。→ Gemini 引用係 confabulated citation, 唔可以原樣引用。

## 3. IDCM 41/60 對齊度 (scripts/01 G16 更新)

| 錨點 | 值 | |Δ| (σ) | 判決 |
|:-----|:---|:------:|:------|
| Planck 2018 TT,TE,EE+lowE | 0.6834 ± 0.0084 | **0.008σ** (6.67e-5) | 🟢 **正中紅心** (4 位有效數字全中) |
| Planck 2018 TT,TE,EE+lowE+lensing | 0.6847 ± 0.0073 | 0.19σ (1.4e-3) | 🟢 1σ 內 |
| Planck 2018 +BAO | 0.6889 ± 0.0056 | 0.99σ (5.6e-3) | 🟢 1σ 內 |

**結論**: IDCM 41/60 = 0.6833333 對 Planck 2018 **TT,TE,EE+lowE 係 0.008σ — 精確正中**。
「零殘差」嘅類別錯誤判斷 (docs/01 C2) 維持 — 但「41/60 係 TT,TE,EE+lowE 中心」係事實。

## 4. 補充觀察 (供 corpus 參考, 唔屬 O148 判決)

- Ω_m 2018 表: TT,TE,EE+lowE 0.3166 / +lensing 0.3153 / +BAO 0.3111 — o33/o39 嘅 19/41 = 0.4634 (Ω_m/Ω_Λ) 對應 TT,TE,EE+lowE: 0.3166/0.6834 = 0.46327 (δ = 1.5e-4 = 0.03%? 唔好追 — 屬陷阱窗) ⚠️
- H₀ = 67.36 ± 0.54 (+lensing) — IDCM H₀ 錨點 (o73) 可對照。

*追蹤: scripts/01 G16 (σ 計算) + docs/01 §C2 + problem_record §6 開放項 5 已更新。*