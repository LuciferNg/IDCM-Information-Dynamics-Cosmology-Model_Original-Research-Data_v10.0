# O130 — 小波工具箱宇宙學應用 (v9.0→v10.0 遷移)

## 狀態: 🟢 有用層推進完成 (2026-09-28, 62/62 PASS + 28 結構聲稱)

> 處置 (調律者 2026-09-28): **不合併**。O130 保留獨立目錄；X/R 層封存為歷史記錄
> (`docs/02_migration_verdict.md`，不改寫)；P 層 + 方法就地推到底 (`docs/03_useful_continuation.md`)。

## 結論

v9.0 `wavelet_toolbox/` 只有**方法層 + 純結構骨架**遷移 (P: γ_n=4sin²(πn/88) 88 環精確譜 /
λ_sync=2πR_H/88≡πR_world/44 / v_g=cos(πn/88) / B=4,z=4^ℓ−1 / 小波+EMD 工具)；所有**定量偵測聲稱**
失效 (R: φ-ratio 已證偽, 17/19 諧波 = 單調斜坡偽影 + sub-bin aliasing; X: H(z) ζ 模型, sync dip z_c=0.6)。
BOSS DR12 (5 h⁻¹Mpc bins) 對 K_Chain 階梯嘅解析度只到 n_max = 8.53。

## 有用層推進結論 (2026-09-28, 依調律者「不合併，只把有用的繼續在這裏推」)

用**統計上有效**嘅檢定重做同一條結構預言，得誠實答案：

- **🔴 零偵測 (script 04)**: K_Chain 階梯當**完整模板** `T(s)=Σγ_n cos(2πns/λ_sync)·exp(−½k_n²Σ²)`，
  只放振幅 A 一參數；broadband = 三次樣條；`D=max_{knots×δ}Δχ²`；null = "broadband+噪聲，無階梯"（1000 real.）。
  `D_obs=+14.57` vs null mean `+15.50` ⟹ **p = 0.500**；Δχ² 隨 broadband 自由度 **+10.7→+0.4 崩潰** ⟹ 同 broadband 退化。
  v9.0「17/19」係點態 S/N + 斜坡 + broadband 退化三重偽影。
- **可解析度定律 (script 05, zero-param)**: `n_max(Δs_bin)=(−1+√(1+4λ/Δs_bin))/2` → 5→8.53 / 4→9.59 / 2→13.76 / 0.5→28.01；
  窗口 Rayleigh `Δn_res=λ_sync/T`（BOSS 2.32>1）；leakage matrix 相鄰 max 0.18（功率 ~3%）。
  **三障礙排序**: ①bin Nyquist n_max=8.53 ②broadband 退化 ③Rayleigh 2.32。
  **門檻表**: n=N_d/2=22 → Δs≤**0.8028**；n=N_d=44 → **0.2052** h⁻¹Mpc。
- **v10.0-native aliasing (script 05 §D)**: `F_proj=17=L₆−1 ⟹ ℓ=log₄18=2.08496 非整數`，
  `n_obs=44/18=2.4444 非整數` ⟹ **中階切斷，冇整數 fold 點**；v9.0 尖銳視界 aliasing **無 v10.0 載體**，
  正確 native 描述 = 有限窗口頻譜洩漏。
- **Out-of-sample 複現 (script 06)**: eBOSS DR16 LRG 同一統計量、唔調參 ⟹ 亦零顯著 (p=0.078)；
  ★ **振幅正負號都唔一致**（BOSS +1.05e−02 vs eBOSS −1.53e−01）⟹ 噪聲。滿足 Hard Test ③。
- **★ DESI DR1 官方數據 (script 07)**: `data.desi.lbl.gov` DR1 clustering VAC — **7 tracer ξ(s) + 官方
  RascalC covariance 135×135 + window matrix**（sha256 全通過; `scripts/00_download_desi_dr1.sh`），
  4 h⁻¹Mpc binning（n_max=9.59）。**首次用相關 χ²**：全局限 p=**0.813**；**結構 δ=0 檢定 p=0.030 (≈2.2σ)**
  來自 LRG3（🟡 **未達 5σ，唔算偵測**；唯一兩個邊緣 tracer LRG3 + LRG+ELG 係同一批星系 ⟹ 非獨立）；
  結構 δ=0 max Δχ² = +3.29，振幅 **3 正 / 4 負**。
  ⚠️ **自己嘅假設被否證**：「DESI window 洗掉階梯」**錯** — W₀₀ 行和=1.000000，階梯結構振幅**保留 97.8%**
  ⟹ window 唔係障礙。**三巡天 (BOSS/eBOSS/DESI)、10 tracer 樣本：structural λ_sync 全部無偵測。**

## 關鍵公式

- **P 遷移**: `γ_n = 4 sin²(πn/88)` (88-site 環 Laplacian 精確譜, Σγ=176=4N_d, γ_n+γ_{44−n}=4)
- **P 遷移**: `λ_sync = 2πR_H/88 ≡ πR_world/44 = 294.877 Mpc` (v9≡v10, dev=0)
- **P 遷移**: `v_g = cos(πn/88)` (O99)；`B = L₃ = 4`，`z = 4^ℓ − 1` (O76)
- **A→🔴**: 阻抗 `Z_n = γ_n/|v_g,n|`，反射 `R_n = (Z_n−Z_{n−1})/(Z_n+Z_{n−1})`，`s_ref = λ_sync/(2n|R_n|)`
  — 部件結構，但模型無 v10.0 擁有者 + **O118 裁定唔做**（同 O131 一致；階梯 169–190 h⁻¹Mpc）
- **k-space**: `k_n = n·(2π/λ_sync) = 88n/R_world` (sync = 88 環諧和, m=88 精確; 44-鏈諧和 = 44/π 非整數)
- **解析度極限 (一般定律)**: `n_max(Δs_bin) = (−1+√(1+4λ_sync/Δs_bin))/2`；`Δn_res = λ_sync/T` (Rayleigh)
- **官方 window 算子**: DESI W₀₀ 行和 = 1（守恆），broadband 移除後階梯結構振幅保留 97.8% ⟹ 非障礙
- **R 🔴**: φ-ratio `A_n ∝ φ^n` 證偽 (log-slope 0.2937 vs log φ 0.4812, 39%; γ_n 模型 RMS 0.3115 < φ^n 0.6064)
- **斜坡偽影**: EMD residual S/N 對 n 單調 (Spearman ρ=0.9979, 1 IMF) ⟹ 「17/18」非 17 諧波
- **X 🔴**: `H(z)=H₀(1+z)^α` with ζ(z) (05)；sync dip `z_c = 3/5` (O126 撤回)

## 依賴

v9.0 `wavelet_toolbox/` → O130；交叉 O133 (k-space) / O129 (λ_sync) / O126 (ζ 撤回) /
O138 (z=17=F_proj) / O76 (離散 z) / O99 (色散) / O135 (P/R/A/X 分類法) / O131 (同批 stacking 遷移) /
O118 (裁定唔做阻抗模型)

## 驗證統計

| Script | PASS | 內容 |
|:-------|:----:|:-----|
| `scripts/01_migration_inventory.py` | 18/18 | λ_sync 幾何 / γ_n 精確譜 / 阻抗階梯 / H(z) ζ / z=17 / φ-ratio / P-R-A-X |
| `scripts/02_wavelet_emd_rerun.py` | 9/9 | 實數據 DWT+EMD 重跑 + 諧波掃描 + 反射階梯 + k-space 對照 |
| `scripts/03_significance_null.py` | 5/5 | φ-ratio 不可辨識 / 斜坡診斷 / BOSS 解析度極限 |
| `scripts/04_calibrated_detection.py` | 5/5 | ★ matched filter + trial-corrected null ⟹ **零偵測 (p=0.500)** |
| `scripts/05_resolvability_forecast.py` | 9/9 | ★ 可解析度定律 / Rayleigh / leakage matrix / 巡天門檻預報 / F_proj 中階切斷 |
| `scripts/06_eboss_replication.py` | 5/5 | ★ eBOSS DR16 out-of-sample 複現 (p=0.078; 振幅正負號不一致) |
| `scripts/07_desi_dr1_test.py` | 11/11 | ★ DESI DR1 官方 7 tracer + RascalC 相關 χ²；結構 δ=0 p=0.030 🟡；全局限 p=0.813；window 假設否證 |
| `scripts/00_download_desi_dr1.sh` | — | DESI DR1 clustering VAC 下載（14 檔 + sha256 驗證） |
| **合計** | **62/62** | + 28 結構聲稱 |

## 密度基準

- 本 O 係**遷移分類 + null 檢定**，非數值閉合聲稱；無結構常數匹配 → 不適用 O208 分位數門檻。
- 相關 null: φ-ratio 檢定 (斜率 39% 偏離 log φ)；斜坡診斷 (Spearman ρ=0.9979, p=1.65e-20)；
  解析度 (n_max=8.53, 客觀由 λ_sync 同 bin 間距決定)。

## 開放

- 🟡 **DESI DR2 原始 ξ(s)**: 官方未公開發佈（只有 chains）；Zenodo `16644577` 1.3 GB 補充包下載中/未完成
- 🟡 **LRG3 δ=0 p=0.030 邊緣提示**: 需獨立數據確認（DR2 / 更細 bin），未達 5σ 唔算偵測
- 🟡 v10.0 native 阻抗算子（維持 O118 裁定：唔做）
- 🔴 目錄處置：依 2026-09-28 指示**不合併**，O130 保留獨立（歷史記錄 = `docs/02`，繼續層 = `docs/03`）
