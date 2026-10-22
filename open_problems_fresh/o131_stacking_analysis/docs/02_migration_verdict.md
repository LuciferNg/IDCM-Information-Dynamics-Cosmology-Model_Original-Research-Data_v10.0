# O131 — 前置驗證: v9.0 stacking_toolbox → v10.0 遷移判決

> **日期**: 2026-09-27
> **範圍**: `open_problems_fresh/o131_stacking_analysis/`（本目錄內；未改動任何其他 O / v9.0 檔案）
> **判決依據**: `scripts/01_v9_rerun_inventory.py` (9/9) + `scripts/02_crosscheck_v9_v10.py` (13/13 + 3 CLAIM)
> **方法**: 依 `o-series-research-workflow` → `references/version-migration-verdict.md` 三分類
> （✅ 遷移 / 🟡 φ 近似 / 🔴 失效）+ 框架依賴掃描。

---

## 一、v9.0 來源檔案盤點

| 檔案 | 內容 | 狀態 |
|:-----|:-----|:-----|
| `IDCM-v9.0--W-Field-Lattice/open_problems_fresh/stacking_toolbox/01_stacked_waveform.py` | **唯一**檔案 (239 行)：相位對齊疊加 + 阻抗反射偵測 | 已複製為 `data/v9_01_stacked_waveform.py.orig` |
| `.../kchain_cosmic_web/_core.py` | 常數來源 (H0_IDCM=72.59, R_H, λ_sync, Ω_Λ φ-form, ζ(z)) | 唯讀引用 |
| `.../sync_bump_analysis/ross_dr12_corrfunc.zip` | BOSS DR12 Ross 2016 ξ(s) 單極子 post-recon | 已複製入 `data/` |
| `.../sync_bump_analysis/eboss_dr16_lrg_xi.txt` | eBOSS DR16 LRG ξ(s) | 已複製入 `data/` |

⚠️ v9.0 檔案硬編碼 `/home/wsl/IDCM/...`（**該目錄已不存在**）⟹ v9.0 script 目前**無法原樣重跑**。
本 O 以 `data/` 相對路徑忠實複現（唯一改動 = 路徑）。

## 二、忠實重跑（scripts/01，9/9 PASS）

| 量 | 值 |
|:---|:---|
| BOSS DR12 | 36 點, s ∈ [2.5, 177.5] h⁻¹Mpc |
| eBOSS DR16 | 49 點, s ∈ [7.5, 247.5] h⁻¹Mpc |
| λ_sync | 294.8771 Mpc = **406.2228 h⁻¹Mpc** |
| 疊加諧波 (n=4..20 落 BOSS 範圍) | 17 個 |
| mean stacked ξ (諧波) | −0.308835 |
| "Stacked S/N" (v9 定義 = mean(ξ/err)) | −119.89 |
| 反射疊加 | 10 個, mean ξ = +0.022169, "S/N" = +0.47 |
| 反射改善倍率 (v9 表) | **max 1.02, 大部分 < 1** |

**★ 重跑揭示嘅 v9.0 內部負結果**（非本 O 新增，係 v9.0 自己嘅輸出）：
1. **反射位置退化**：全部 10 個 `s_ref = λ_sync/(2n|R|)` 擠喺 **169.2–189.5 h⁻¹Mpc**（唔散開）⟹ 唔係「44 模式各產生一個反射」嘅預期圖像。
2. **無 S/N 增益**：v9 自己嘅 "Improvement" 欄 ≤ 1.02（大部分 < 1）⟹ 疊加**冇**達到設計目的（Boost S/N）。
3. **小波去 broadband 失效**：`pywt` 警告 `Level value of 3 is too high: all coefficients will experience boundary effects`；BOSS 殘餘 std = 0.596（同 ξ 本身同量級）⟹ 去 broadband 冇分離出 wiggle。
4. "S/N" 定義 = `mean(ξ/err)` 唔係信噪比（會隨 err 分佈爆大）⟹ 該欄本身唔可解讀。

## 三、v9.0 物件 vs v10.0 權威值（scripts/02，13/13 PASS + 3 CLAIM）

| 物件 | v9.0 | v10.0 權威 | dev | 分類 |
|:-----|:-----|:-----------|:----|:----:|
| λ_sync = 2πR/88 | 294.877138 Mpc | πR_world/44（同一 R，公式恆等） | **0 EXACT** | ✅ 遷移 |
| λ_sync 註冊值捨入 | 294.877138 | 294.877026（R_world=4129.94, 4 s.f.） | 3.783e-07 | （純捨入） |
| R (c/ω_ring) | 4129.941562 Mpc | R_world（公式恆等） | **0 EXACT** | ✅ 遷移 (標籤 🔴) |
| γ_n = 4sin²(πn/88) | 同式 | 同式 | **0 EXACT** | ✅ 遷移 |
| v_g(n) = cos(πn/88) | 同式 | 同式 | **0 EXACT** | ✅ 遷移 |
| Ω_Λ = 4/(φ⁴−1) | 0.683281573 | **41/60 = 0.683333333** | 7.575e-05 | 🟡 φ 近似 |
| ε = φ⁻¹/4 | 0.1545084972 | **19/123 = 0.154471545** | 2.392e-04 | 🟡 φ 近似 |
| H₀ = 72.59 | 標「哈伯常數」 | **ω_ring = 72.59（角頻率）** | 0（數值同） | 🔴 標籤失效 |
| h = 0.7259 | 用 ω_ring 做 h | 三個 h 投影 (0.674071 / 0.73130 / 0.71157) | — | 🔴 慣例非預言 |
| z_c = 0.6 (sync dip) | F₄/F₅ = 3/5 | 1+z = 4^ℓ，ℓ(0.6) = **0.339036** 非整數 | — | 🔴 撤回 |
| ζ(z) 阻抗修正 | ZETA_A/B/z1/z2 | v9 demote 參數 | — | 🔴 失效 |

**尾截斷恆等式（EXACT，dps=50）** — 令 🟡 判定有結構依據（非「巧合近似」）：
- `41/60 − 4/(φ⁴−1) = 5.1760334e-5 = √5·φ⁻¹⁰/[60(3φ+1)]` ⟹ Ω_Λ 舊 φ 形 = v10 精確式之 **Lucas 尾截斷**。
- `19/123 − φ⁻¹/4 = −3.6952472e-5 = −√5·φ⁻¹⁰/492` ⟹ ε 舊 φ 形 = 同上。

## 四、框架依賴掃描（scripts/02 §B，48 個 v9.0 檔案）

| 標記 | 命中 | 分佈 |
|:-----|:----:|:-----|
| `inflation` / `e-fold` | **0 / 0** | — |
| `(1+z)` 膨脹律 | 120 | 集中於 `03_verify_hz.py` / `04_derive_hz.py` / `40_hz_derivation*.py` |
| `z_c` (sync dip) | 45 | `04_derive_hz.py`×37 / `05_impedance_reflection.py`×6 |
| `zeta` / `ZETA_` | 2 / 8 | **全喺 `_core.py`** |
| `Omega_L` (φ-form) | 32 | `03_verify_hz.py`×10 等 |
| `H0_IDCM` | 20 | — |
| `R_H` (Hubble radius 標籤) | 270 | — |

**★ 關鍵發現**：`stacking_toolbox/01_stacked_waveform.py` **本身**冇任何顯式膨脹假設
（`inflation` / `(1+z)` / `ζ(z)` / `Ω_Λ` / `z_c` 全部 = 0）；框架包袱**只經 `import _core` 間接繼承**。

## 五、判決（三分類）

| 層 | 內容 | 判決 |
|:---|:-----|:----:|
| **骨架層** | λ_sync 幾何、γ_n、v_g、諧波位置 λ_sync/n | ✅ **遷移**（公式恆等，dev = 0） |
| **φ 近似層** | Ω_Λ φ-form、ε φ-form | 🟡 **近似**（= v10 精確式之 Lucas 尾截斷） |
| **物理層** | H₀ 標籤、h 慣例、ζ(z)、z_c=0.6、H(z)=(1+z)^α | 🔴 **失效**（已 demote / 已撤回 / 標籤錯） |
| **獨有內容** | 阻抗反射模型 (Z=γ/\|v_g\| → R → s_ref) | 🔴 **無 v10 對應 + 已由 O118 裁定唔做** |
| **技術層** | 小波去 broadband + 逆變異數加權堆疊 | ✅ 框架無關數據分析（**唔含結構推導**） |

**一句話判決**：O131 原命題「K_Chain 模式疊加波形分析在 v10.0 中的驗證」**未實現** ——
其**結構內容**（λ_sync 諧波階梯）已由 **O31**（🟢 已閉合）完成；其**獨有內容**（阻抗反射）
無 v10 結構基礎且已被 **O118** 排除；重跑顯示 v9.0 自身輸出**無 S/N 增益**（負結果）。

## 六、依賴 / 引用

- 方法: `o-series-research-workflow` → `references/version-migration-verdict.md`
- v10.0 權威: O73 (ω_ring/R_world) · O171 (R_world 精確式) · O127 (r_d) · O148/O215 (Ω_Λ=41/60) ·
  O135 (ε=19/123, φ-ladder 降級) · O34/O124 (γ_n, v_g) · O126 §D / O129 (z_c 撤回) ·
  O31 (λ_sync 諧波階梯, 🟢) · O100/O133 (P(k)/σ8) · O118 (唔搬遷 SYNC 系列)
