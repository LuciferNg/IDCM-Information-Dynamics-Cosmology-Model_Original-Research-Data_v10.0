# O130 — 小波工具箱宇宙學應用

> **Session**: 2026-08-29 (新建立，從 v9.0 遷移)
> **狀態**: 🔴 未開始 → 🟡 **遷移判決完成 (2026-09-27)**
> **來源**: v9.0 項目審計後發現不屬於 v10.0 O1-O114 任何現有系列
> **v10.0 位置**: `IDCM-v10.0--It-From-Beat/open_problems_fresh/o130_wavelet_analysis_tools/`
> **v9.0 來源**: `open_problems_fresh/wavelet_toolbox/`

## 問題

見 `docs/01_problem_record.md`

## 前置驗證：v9.0 推導先行驗證

⚠️ **必須先驗證 v9.0 推導在 v10.0 非膨脹框架中是否仍然有效，然後才能開始攻堅。**

1. 讀取 `open_problems_fresh/wavelet_toolbox/` 中的原始推導
2. 識別依賴膨脹宇宙假設的部分（v9.0 使用 v9.0 框架）
3. 在 v10.0 非膨脹框架中重新驗證每個公式
4. 如果 v9.0 推導在 v10.0 中仍然有效，則直接遷移
5. 如果 v9.0 推導在 v10.0 中失效，則需要建立新推導

## 前置

O9 (高 ℓ CMB 峰) 🟢, O42/O122 (冷斑分析) 🔴

---

## ★ 本 O 前置驗證結果 (2026-09-27) — v9.0 wavelet_toolbox → v10.0 遷移判決

> **腳本**: `scripts/01_migration_inventory.py` (**18/18**) · `scripts/02_wavelet_emd_rerun.py` (**9/9**) ·
> `scripts/03_significance_null.py` (**5/5**) = **32/32 PASS + 14 結構聲稱**
> **文檔**: `docs/02_migration_verdict.md` · **結論**: `final_result.md`

### ① P/R/A/X 判決

- **P 遷移 (5)**: `γ_n=4 sin²(πn/88)` (88 環精確 Laplacian 譜, dev<1e-12) ·
  `λ_sync=2πR_H/88≡πR_world/44` (dev=0) · `v_g=cos(πn/88)` (O99) · `B=4, z=4^ℓ−1` (O76) ·
  小波+EMD broadband 移除**方法** (框架無關)。
- **A→🔴 (1)**: 阻抗 `Z_n=γ_n/|v_g,n|`、反射 `R_n`、`s_ref=λ_sync/(2n|R_n|)` — 部件係 P 量,
  但模型**無 v10.0 對應算子**，且 **O118 已裁定「唔需要局部阻抗模型、唔需要搬遷 v9.0 SYNC 系列」**
  （與 **O131** 判決一致；兩 O 獨立重跑同得反射階梯 169–190 h⁻¹Mpc）。
- **R 🔴 (2)**: φ-ratio `A_n∝φ^n` (v9.0 自己 09_math_verify 已證偽) ·
  z=17 尖銳視界 aliasing (z=17=F_proj 存活 O138, 但 ℓ=log₄18=2.085 非 rung)。
- **X 🔴 (2)**: `H(z)=H₀(1+z)^α` with ζ(z) (05_emd_hz, ζ 已 demote; Ω_Λ=41/60 常數) ·
  sync dip `z_c=3/5` (O126 §D 已撤回)。

### ② 新發現 (本輪)

1. **「EMD 17/19 諧波」= 單調斜坡偽影 🔴** — 重跑**複現** v9.0 數字 (BOSS EMD 17/18,
   wavelet 3/18; eBOSS EMD 10/18, wavelet 0/18), 但 EMD residual 嘅 S/N 對 n **嚴格單調**
   (Spearman ρ=**0.9979**), 且只抽出 **1 個 IMF** ⟹ 所謂「17 諧波」= 一條平滑斜坡喺細 s 越 3σ。
2. **BOSS 解析度極限 n_max = 8.53 🔴** — 諧波間距 Δs_n=λ_sync/[n(n+1)], BOSS bin=5 h⁻¹Mpc
   ⟹ 只 n=3..8 (6 個) 解析得到; n=9..20 全係 **sub-bin aliasing** (v9.0 報嘅 19 諧波 12 個超限)。
3. **φ-ratio 不可辨識 🔴** — log A_n vs n 斜率 0.2937 vs log φ=0.4812 (**39%** 偏離);
   γ_n 模型 RMS 0.3115 優於 φ^n 模型 0.6064。
4. **方法敏感度 🟡** — 同一 BOSS 數據, 偵測率 4/19 (多項式) / 3/19 (小波) / 17/19 (EMD)
   ⟹ 偵測率係方法依賴量, 唔係結構預測。

### ③ 可遷移資產 (v10.0-native)

- 諧波階梯 `s_n = λ_sync/n` (同 O129 σ_sync 階梯一致)。
- k-space `k_n = n·(2π/λ_sync) = 88n/R_world` — 同 **O133** BAO wiggle 一致 (sync=88 環諧和 m=88 精確)。
- 小波/EMD broadband 移除工具 (`scripts/emd_engine.py` 原樣遷入)。
- 阻抗階梯 `Z_n`, `R_n`, `s_ref` — **排除** (部件結構，但模型無 v10 擁有者 + O118 裁定唔做)。

### ④ 開放 (移交後續)

- eBOSS 反射尺度獨立檢驗 🟡 / DESI DR2 細 bin 重跑諧波階梯 🟡 /
  aliasing 機制是否重新形式化 (或併入 O76) 🔴 / v10.0 native 阻抗算子 🟡。

### ⑤ 待裁定

O130 目錄處置 (保留 / 併入 O133) 待調律者明示; 本 session **未**作合併動作。
