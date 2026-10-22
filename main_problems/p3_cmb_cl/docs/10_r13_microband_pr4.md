# P3 / R13 — 1ℓ 格高分辨微帶檢驗 [1452,1476] (PR4 HiLLiPoP ℓ-by-ℓ)

> **日期**: 2026-10-22
> **狀態**: 🔴 **O256 S5 微帶預言否證（1ℓ 格強化）**；R12 判決維持；O202 R6 維持 🔴
> **承接**: O256 → P3/high-l-tail-transfer handoff (2026-10-21)
> 「殘餘 = 1ℓ 格高分辨譜檢驗 [1452,1476] 局部形態 (Planck 9ℓ/格 同 ACT/SPT 50ℓ bin 全無分辨力)」
> **Script**: `scripts/21_highl_microband_pr4.py`　**Log**: `logs/21_highl_microband_pr4.out`
> **結果**: 9 PASS / 0 FAIL

---

## 1. 被檢驗預言（O256 R1 S5, 唯一可分辨 IDCM vs lensed ΛCDM 嘅觀測簽名）

```
峰位公式 m≥8 飽和分支: ℓ_m = 1452 + ((m−1)×9 mod 25), m=8..44
⟹ 37 模態權重塌入 25ℓ 微帶 [1452,1476]
⟹ 觀測預言: 微帶內局部 bump, +5% 級 (相對平滑包絡)
```

## 2. 數據：PR4 HiLLiPoP v4.2 TT ℓ-by-ℓ（首次使用）

```
下載: https://portal.nersc.gov/cfs/cmb/planck2020/likelihoods/planck_2020_hillipop_TT_v4.2.tar.gz
      (886 MB; Tristram+ 2024, Planck PR4 NPIPE pipeline)
內容: 36 dl_PR4_v4.2_*.fits + binning_v4.2.fits
      HDU: PRIMARY / CL (D_ℓ, K²) / ERR
      ℓ 範圍 0..2800 (官方 lmax 2500)
```

### ⚠️ §2.1 致命 trap（R13 實錄，已修）

```
36 檔 = 15 cross-spectra × 對稱重複 (2) + 6 auto-spectra
auto-spectra 有 noise bias（detset 內相關未 debias）:
  100Ax100A @ ℓ=1464: D = 6471 μK²  vs 真值 ≈ 780 μK²  (8.3×)
  100Bx100B: 4265 | 143Bx143B: 1146 | 217Ax217A: 1027 | 217Bx217B: 1055
⟹ 第一次粗暴 IVW co-add 全部 36 檔 → 微帶假 bump +4.94% (z=25.9σ)「HIT」
   —— 完全係 auto-spectra 污染，唔係信號。
修正: 只取 15 個 cross-spectra（排除 XxX auto + 15 個對稱重複）
   → 同 O48 docs「15 個 dl_PR4 x fits」一致
```

**教訓（寫入禁區）**：任何 PR4 HiLLiPoP co-add 必須先過濾 auto-spectra；`glob('dl_PR4_v4.2_*x*.fits')` 直接平均 = 假結果。O48 `scripts/65_q1_pr4_coadd.py` 用同一 glob（含 auto）—— 該 script 只用峰比/FWHM，影響較輕，但需在該處標註。

## 3. 檢驗結果

### T1 — 微帶 vs 兩側同寬窗口（25ℓ 對稱）

| 數據 | 微帶 | 左 (1427-1451) | 右 (1477-1501) | 相對兩側 | z |
|:--|--:|--:|--:|--:|--:|
| co-add 15 cross | 806.97 | 841.54 | 764.74 | **+0.59% ± 0.33%** | +1.76σ |
| solo 143Ax143B ★ | 805.86 | 823.25 | 754.54 | **+2.25% ± 0.95%** | +2.34σ |

### T2 — 局部 log-線性 baseline（兩側擬合內插）

| 數據 | 微帶殘餘 (25 pt) | χ²/dof | baseline λ_local |
|:--|--:|--:|--:|
| co-add | +0.59% ± 0.28% (z=+2.15σ) | 5.81 ⚠️ | 523.7 |
| solo ★ | +2.22% ± 0.78% (z=+2.84σ) | **1.25 ✅** | 582.5 |

### T3 — 多項式包絡 residual（參考，模型不足）

```
deg=2: +3.44% (z=+12.5σ) | deg=3: +4.70% (z=+17.1σ)
⚠️ 1418-1700 段高ℓ尾非多項式形式 — 包絡模型不足，不作判決
```

### T4 — bump amplitude fit（D_obs = D_base × (1+A)）

| 數據 | A | 顯著性 | |A − 5%| | 判定 |
|:--|--:|--:|--:|:--|
| co-add | +0.65% ± 0.27% | +2.37σ | 15.9σ | 拒絕 +5% |
| **solo ★** | **+2.34% ± 0.77%** | **+3.03σ** | **3.4σ** | **拒絕 +5% 預言** |

```
solo χ²(A=0) = 41.9 → χ²(fit) = 32.7 | χ²/dof = 1.36 ✅ (統計可信)
O256 S5 預言 +5% ⟹ 3.4σ 拒絕
Planck PR3 (9ℓ/格, 3 bins): 微帶內 −2.5/−3.2/−4.0%, 相對兩側 −7.8%
```

### T5 — 1ℓ 格 λ_loc(ℓ) 分段（20ℓ 滑窗）

| ℓ 段 | PR4 1ℓ λ_loc 中位 [IQR] | P3 binned λ | 一致 |
|:--|--:|--:|:--|
| 1418-1700 | **316.2** [232.5, 618.2] | 308 | ✅ |
| 1700-2000 | **413.8** [316.7, 800.1] | 410 | ✅ |
| 2000-2400 | 289.5 [141.0, 590.5] | 420 | ⚠️ 1ℓ SNR 降 |
| 2400-2800 | 138.5 [71.1, 272.5] | 646 | ⚠️ 不可靠 (lensing + SNR) |

```
★ O256 S6 結構預言 λ₁ = 半週期/lnφ = 148.5/lnφ = 308.60
  vs PR4 1ℓ 第一段 316.2 → dev +2.45%
```

### 附：PR4 vs PR3 形狀對照

```
1418..1700 段 PR4/PR3 比值: 中位 1.072 (IQR spread 0.056) ✅ 形狀一致
（PR4 整體高 7.2% = mask/beam/foreground 校準差, 正常範圍）
```

## 4. 判決

```
🔴 O256 S5 微帶預言（+5% 25ℓ bump）: 否證
   1ℓ 格 PR4 solo: A = +2.34% ± 0.77%，|A − 5%| = 3.4σ
   微帶相對兩側 +2.25%（z=2.34σ）— 遠低於 +5% 預言，且部分可歸
   143GHz 殘餘 foreground（tSZ/point source）
✅ R12 判決維持: 無 IDCM 特有微帶簽名；λ₁≈306-316 = lensed ΛCDM local band
🔴 O202 R6 缺口維持 (IDCM 無自己嘅 C_ℓ 連續形式)
✅ P3 R10 分段 λ 結構 1ℓ 格獨立確認 (316.2/413.8 vs 308/410)
   ⟹ 分段 λ 上升唔係 binning artifact — 第四數據集（PR4 ℓ-by-ℓ）確認
```

**殘餘邊緣信號誠實記錄**：solo 微帶 +2.3% (z≈3.0σ) — 未達 5σ，且與 +5% 預言差 3.4σ。可能來源：143GHz foreground residual / 局部 lensing / 統計波動。**唔作結構主張**。

## 5. 方法限制（記錄）

```
⚠️ co-add IVW 假設 15 cross 獨立 — 實際高度相關 ⟹ σ 低估 (χ²/dof 5.81)
   統計判決以 solo 143Ax143B (χ²/dof 1.25) 為準
⚠️ T3 多項式包絡喺 1418-1700 段模型不足（高ℓ尾非多項式）
⚠️ 1ℓ 格 λ_loc 喺 >2000 SNR 降 + lensing 令滑窗斜率塌陷 — 只有前兩段可信
⚠️ PR4 vs PR3 有 7.2% 整體校準差（唔影響形狀判決）
```

## 6. 結論

O256 handoff 殘餘已閉環：**1ℓ 格檢驗否定 S5 微帶預言**。IDCM 連續譜喺現有數據無可分辨觀測簽名 — R12 判決經第四數據集（PR4 ℓ-by-ℓ，25 個獨立 ℓ 點 vs 之前 3 bins）強化。O202 R6 缺口維持，方向仍為 K_Chain/K_Tree 結構重推導（O256 R3 lensing 語義路線）。

## 7. 檔案

```
- scripts/21_highl_microband_pr4.py (R13)
- logs/21_highl_microband_pr4.out
- 數據: ~/.hermes/cache/scratch/planck_2020/hillipop/planck_2020/hillipop/data/
        (dl_PR4_v4.2_*.fits 36 檔 + binning_v4.2.fits; 886MB tar 已解壓)
- 承接源: open_problems_fresh/o256_cl_continuum_envelope/docs/03_microband_verdict.md
```
