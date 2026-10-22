# O130 — 小波工具箱宇宙學應用

> **Session**: 2026-08-29 (新建立，從 v9.0 遷移)
> **狀態**: 🔴 未開始 → 🟡 遷移判決完成 (2026-09-27) → 🟢 **有用層推進完成 (2026-09-28, 62/62 PASS)**
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

---

## ★★ 有用層繼續推進 (2026-09-28) — 依調律者指示「不合併，只把有用的繼續在這裏推」

> **腳本**: `scripts/04_calibrated_detection.py` (**5/5**) · `scripts/05_resolvability_forecast.py` (**9/9**) ·
> `scripts/06_eboss_replication.py` (**5/5**) = **19/19 PASS + 10 聲稱**（O130 累計 **51/51 PASS + 24 聲稱**）
> **文檔**: `docs/03_useful_continuation.md` · **處置**: X/R 層封存為歷史記錄（`docs/02`），**不合併**入 O133

### ① 為何要推 — v9.0 點態 S/N 嘅三重結構缺陷

點態 S/N ≠ 全局檢定（①）；單調殘餘令任何正偏移「過 3σ」（②，ρ=0.9979）；broadband 一換偵測數 4→3→17（③）。

### ② 校準化檢定 (script 04) — matched filter + trial-corrected null

K_Chain 階梯當**一條完整模板** `T(s)=Σγ_n cos(2πns/λ_sync)·exp(−½k_n²Σ²)`（Σ=10 h⁻¹Mpc），
**只放振幅 A 一個參數**；broadband = 三次樣條（knots 4/5/6）；窗口 s≥40；`D = max_{knots×δ} Δχ²`；
null = "平滑 broadband + 噪聲，無階梯"（1000 realizations）。

```
knots=4: Δχ²=+10.69 | knots=5: Δχ²=+12.22 | knots=6: Δχ²=+7.23 | knots=8: Δχ²=+0.44 (broadband 食晒)
D_obs=+14.57 ; null mean +15.50 σ 7.08 max +51.75 → p = 0.500
shifted-ladder: peak 喺 δ=−5%, δ=0 唔突出
```

**🔴 零偵測**：BOSS DR12 冇偵測到階梯；Δχ² 隨 broadband 自由度**崩潰** ⟹ 同 broadband **退化**。

### ③ 可解析度定律 + 巡天預報 (script 05, zero-parameter)

- 取樣: `n_max(Δs_bin)=(−1+√(1+4λ/Δs_bin))/2` → 5→**8.53** / 4→9.59 / 2→13.76 / 1→19.66 / 0.5→28.01
- 窗口 Rayleigh: `Δn_res = λ_sync/T`；BOSS T=175 → **2.32 > 1**（相鄰模態峰位不可分）；
  leakage matrix 相鄰 **max 0.18**（功率 ~3% ⟹ 位置冇被打亂）
- **三障礙排序**: ①bin Nyquist n_max=8.53（n=9..20 全 sub-bin）②broadband 退化（p=0.50）③Rayleigh 2.32
- **門檻表**: n=F_proj/2=8.5 → Δs≤5.0306；n=N_d/2=22 → **0.8028**；n=N_d=44 → **0.2052** h⁻¹Mpc
- 🟡 **巧合記錄（非預言）**: BOSS 用 5.0，`λ/(8.5×9.5)=5.0306`（dev 0.61%）— bin 寬係儀器選擇 ⟹ post-hoc

### ④ v10.0-native aliasing (script 05 §D)

`1+z=4^ℓ` rungs {0,3,15,63,255,1023}；**F_proj=17=L₆−1 ⟹ ℓ=log₄18=2.08496 非整數**，
`n_obs=N_d/4^ℓ=44/18=2.4444 非整數` ⟹ **F_proj 切喺 K_Tree 中階，冇整數模態切斷點可 fold**。
v9.0「尖銳視界 aliasing」在 v10.0 **無精確載體**；正確 native 描述 = **有限窗口頻譜洩漏**。

### ⑤ Out-of-sample 複現 (script 06) — eBOSS DR16 LRG

同一統計量、**唔重新調參**：

| 數據集 | Δs_bin | 窗口 | n_max | Δχ²(δ=0) | A(δ=0) | p |
|:--|:--|:--|:--|:--|:--|:--|
| BOSS DR12 | 5.0 | 175.0 | 8.53 | +11.64 | **+1.05e−02** | 0.500 |
| eBOSS DR16 LRG | 5.0 | 207.5 | 8.53 | +1.35 | **−1.53e−01** | 0.078 |

**🔴 複現**：兩個獨立數據集都零顯著偵測；★ **振幅正負號都唔一致** ⟹ 噪聲特徵。
滿足 Hard Test ③（out-of-sample 盲測）。

### ⑥ 處置裁定 (2026-09-28)

- **不合併**。O130 保留獨立目錄。
- **X/R 層**（`docs/02_migration_verdict.md` 之 φ-ratio / H(z)ζ / sync dip / 阻抗模型）→ **歷史記錄，不改寫**。
- **P 層 + 方法**→ 已推到底（本節 ②–⑤）；開放項見 `docs/03_useful_continuation.md` §8。

### ⑦ DESI DR1 官方數據 — 第三個獨立巡天 (script 07, 11/11)

> **下載**: `data.desi.lbl.gov/public/dr1/vac/dr1/full-shape-bao-clustering/v1.0/data/recsym/`
> （腳本 `scripts/00_download_desi_dr1.sh`）— **7 tracer ξ(s) + RascalC covariance 135×135 + window matrix**,
> 全部 sha256 驗證通過; 輸出 `data/desi/07_desi_dr1_test.json`

- **★ 首次用相關 χ² + 官方 covariance**：窗口 s∈[42,198] (40 bins), 官方 4 h⁻¹Mpc binning (n_max=9.59)。
- **🔴 無顯著偵測**：全局 trial-corrected (7 tracer × 3 knots × 9 shifts, joint null) **p = 0.813**；
  λ 允許浮動就完全無信號 (ELG 嘅 p=0.000 喺 **δ=+0.10 非結構 λ**)。
- **🟡 邊緣提示**：δ=0 **結構檢定** p = **0.030 (≈2.2σ)**，來自 LRG3；唯一兩個 p_delta0 ≤ 0.02
  嘅 tracer (LRG3 + LRG+ELG) 係**同一批星系** ⟹ 非獨立；**未達 5σ 唔算偵測**。
- 結構 δ=0：max Δχ² = +3.29 (LRG2, 1 dof)；振幅 **3 正 / 4 負** ⟹ 冇一致符號。
- **⚠️ 自己嘅假設被否證**：「DESI window 洗掉階梯」**錯** — W₀₀ 行和 = 1.000000，
  階梯**結構振幅保留 97.8%** ⟹ window **唔係**障礙；障礙仍係 ①bin Nyquist ②broadband 退化。
- **三巡天交叉 (BOSS / eBOSS / DESI, 10 tracer 樣本)**：structural λ_sync **全部無偵測**。
- 🟡 DESI **DR2** 原始 ξ(s) 官方未公開發佈（只有 chains）；Zenodo `16644577` 1.3 GB 補充包
  已開始下載但速率 ~0.2 MB/s（預估 ~1.8 h）**未完成**。

---

## ⚠️ 2026-09-28 收尾：DESI DR2 完成 + 全線單位修正（最終狀態）

1. **DESI DR2 官方補充數據已到手並驗證**：Zenodo `16644577` `dr2-bao-zenodo.zip`
   size 1,306,284,840 B、md5 `425623648b4b12515fa1943a5857fd46` **完全一致**（8 路並行 range 下載 +
   續傳 + 拼接；下載器曾把 early-EOF 當完成 → 已修，見 `data/desi/dr2/PROVENANCE.md`）。
   `figure5/multipoles_<tracer>_{data,theory}.txt`：**8 tracer × 23 pt，s = 62.04..150.02，Δs ≈ 3.998**。
2. **⚠️ 單位修正（根因）**：`λ_sync` 由 **406.2227 → 198.63 h⁻¹Mpc**。v9.0 `_core.py`
   `LAMBDA_SYNC / H` 方向錯（Mpc→h⁻¹Mpc 應 **×h**），錯 1/h² = 1.897×；O130 scripts 03–08 原封繼承。
   **三條獨立證據**：v9 源碼、Planck r_d 147.09 Mpc×h = 99.1（BAO 峰公認 ~100）、
   DESI DR2 官方 best-fit 曲線實測 bump = **102.0 h⁻¹Mpc**。獨立佐證：**O132 / O31 舊記錄已記同一 bug**。
3. **修正後最終結果（全線重跑 83/83 PASS）**：
   - 節點 s_n = λ/n（n=3..9）= **66.2, 49.7, 39.7, 33.1, 28.4, 24.8, 22.1 h⁻¹Mpc**；
     n_max(Δs=5) = **5.823**、n_max(4) = **6.565**；門檻 n=22 → 0.3925、n=44 → 0.1003 h⁻¹Mpc。
   - **BOSS p = 0.935**、**eBOSS p = 0.432**、**DESI DR1 p_global = 0.640 / δ=0 p = 1.000**、
     **DESI DR2 p_global = 1.000、p_delta0_global = 1.000（adq 0.987）**。
   - 原「邊緣訊號」（eBOSS 0.078、DR1 LRG3 0.030、DR2 raw Δχ² 12.83）**全部消失**；
     原「BOSS bin 落在 F_proj/2 門檻（dev 0.61%）」的 🟡 巧合 **撤回**（真 dev 50.8%）。
   - **四巡天（BOSS / eBOSS / DESI DR1 / DESI DR2）、17 tracer、全部窗口：structural λ_sync 皆無偵測。**
4. **新增結構事實**：λ_sync/2 = 99.3 h⁻¹Mpc ≡ r_d（BAO 尺度 = 階梯 n=2 節點）⟹ 用「ΛCDM+BAO 模型」
   做對照對 IDCM **保守**（會移除階梯自己預測的結構）；DESI DR2 的 BAO-fit 窗只含 1 個 j=1 節點。
5. 記錄：`docs/04_unit_correction.md`（完整對照）、`data/0*_stdout.txt`、`data/desi/dr2/PROVENANCE.md`。
