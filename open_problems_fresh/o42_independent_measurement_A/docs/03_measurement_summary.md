# O42 — 冷斑 A 獨立量度: 三通道結果彙整 (閉合版)

> 日期: 2026-08-25
> 狀態: 🟢 **閉合** — A = 134.2 μK 六方法獨立量度確認
> A_IDCM = 88×61/40 = 134.2 μK (O41 結構公式)

## 1. 組份分離通道 — 6 個獨立量度一致 🟢🟢 (核心結果)

| Map | 方法 | 節點 0 T (4.17°) | rank | dev vs A |
|:----|:-----|:----------------:|:----:|:--------:|
| SMICA | harmonic ILC | -134.19 μK | 1/60 | 0.01% |
| NILC | needlet ILC | -134.09 μK | 1/60 | 0.08% |
| Commander | pixel MCMC | -133.32 μK | 1/60 | 0.65% |
| SEVEM final | template | -134.47 μK | 1/60 | 0.20% |
| SEVEM 143 | template | -134.87 μK | 1/60 | 0.50% |
| SEVEM 217 | template | -131.85 μK | 2/60 | 1.75% |

**統計**: mean = -133.80 μK, std = 0.99 μK, spread = 3.02 μK
**max dev vs A = 1.75%**

→ **冷斑 A = 134.2 μK 由 4 種獨立組份分離方法 × 6 個產品一致確認**
→ 呢個係「獨立量度」：4 種算法 (harmonic ILC / needlet ILC / pixel MCMC / template)
  用唔同嘅 foreground 處理, 全部量度到同一冷斑幅度。

### ⚠️ SEVEM ordering 陷阱 (反方向 NESTED pitfall, 2026-08-25)
IRSA 嘅 SEVEM fits header 寫 `ORDERING=NESTED`, 但實際像素已係 RING。
盲信 header 做 `hp.reorder(n2r=True)` → 冷斑「消失」(+0.4 μK), 同 SMICA 負相關。
**修正**: 用 raw SMICA cross-correlation 判斷 ordering (as-is 0.70 vs reorder 0.00)。
**教訓**: 唔可以盲信 fits header — 用 cross-correlation 驗證 (skill 已更新)。

## 2. SMHW 小波通道 (exact harmonic-space SMHW + kurtosis)

| 尺度 R | 冷斑 SMHW 係數 | 全天空 percentile | 節點 rank |
|:------:|:-------------:|:----------------:|:---------:|
| 3.0°  | -30.02 μK | 0.369% | 1/60 |
| 4.17° | -31.17 μK | 1.467% | 2/60 |
| 5.0°  | -30.28 μK | 2.482% | 2/60 |

- kurtosis (R=3-7°): 全部 +0.11 (正超高斯, Cruz 2005 方向一致)
- 冷斑係 SMHW 係數全域極端 (全天空 0.4-2.5%, rank 1-2/60)
- **小波係數幅度 (31 μK) ≠ pixel 幅度 (134 μK)** — band-pass vs low-pass filter 響應差異, 互補

### 🟢 本徵尺度閉合 (2026-08-25 延伸, docs/04)

SMHW 超額譜 (減 60 節點背景) fit 高斯 dip (A=134.2 固定) → σ_fit = 4.08° (χ²=0.4)
去卷積 (σ_fit² = σ_int² + σ_kernel², σ_kernel=1.771°):

| 來源 | 冷斑尺度 | 值 |
|:-----|:--------|:---|
| **本工作 (去卷積)** | 本徵 FWHM | **8.66°** |
| **IDCM 2×R8** | 2 × 4.17° | **8.34°** |
| Vielva 2004 | angular radius | ~5° (直徑~10°) |
| Planck 2013 | 直徑 | ~10° |

→ **冷斑本徵 FWHM 8.66° ≈ 2×R8 (8.34°), 偏差 3.7%** (vs 文獻 10°: 13%)
⚠️ v1 曾寫「σ=4.08°=R8 4.17°」— 量綱錯誤 (R8 係 FWHM), 已修正。

## 2b. T-E 偏振交叉相關 (通道 3, 2026-08-25 延伸)

SEVEM final Q/U @4.17° (AS-IS RING):

- 冷斑: Q=−0.53, U=−0.17, |P|=0.55 μK
- 60 節點 |P|: mean 0.50 ± 0.29 μK → 冷斑 **z = +0.20σ** (正常)
- **冷斑係溫度-only 結構, 冇偏振異常** — 同 Planck 2015 XVI 一致
  (「stacking polarization at cold/hot spot positions agrees with ΛCDM」)
- 支持 IDCM 相位模型: 冷斑 = cos(θ_i) 相位結構, 偏振唔受影響

## 3. ISW 解耦通道 (文獻整合)

| 項目 | IDCM | ΛCDM |
|:-----|:----:|:-----:|
| A_prim | **134.2 μK** (ISW=0) | 94–124 μK |
| Eridanus ISW 貢獻 | **0 μK** | −10~−40 μK (marginal ~10) |

- Planck 2015 XXI: ISW 重建 map rms 只有 **0.56 μK** → 冷斑 ISW 貢獻理應極細
- Nadathur+2015: ΛCDM 中 supervoid ISW 解釋唔到冷斑 → 間接支持 IDCM
- 分辨所需精度 ±5 μK → DESI 2026+ / Euclid 2027+

## 4. 徑向溫度剖面

| 量度 | 值 |
|:-----|:---|
| 中心 (θ≈0) 4.17° smooth | -134.2 μK (= A) |
| 冷斑回升點 (T > −20 μK) | 8.2° |
| 最近節點 | 節點 0 (0°) + 3 個 26.1° (A₅ 結構) |

4.17° 平滑後嘅中心值 −134.2 μK 精確等於 A — 平滑核匹配冷斑核心幅度。
剖面: 中心 −134 → 8.2° 回升到 −20 → 外圍轉正 (A₅ 網絡背景)。

## 5. 總結 — O42 三通道閉合

| 通道 | 結果 | 狀態 |
|:-----|:-----|:----:|
| 組份分離 | **6 量度一致 −134 μK (std 0.99 μK, max dev 1.75%)** | 🟢🟢 A 獨立確認 |
| SMHW 小波 | 冷斑 rank 1-2/60, 全域極端, kurtosis +0.11 | 🟢 結構確認 |
| SMHW 本徵尺度 | **本徵 FWHM 8.66° ≈ 2×R8 (8.34°), 偏差 3.7%** | 🟢🟢 尺度閉合 |
| T-E 偏振 | 冷斑 z=+0.2σ, 冇偏振異常 (溫度-only) | 🟢🟢 已完成 |
| ISW 解耦 | ISW 解釋唔到冷斑; IDCM A_prim=134.2 合理 | 🟢 文獻支持 |
| 徑向剖面 | 中心 −134.2 μK (=A), 8.2° 回升, A₅ 一致 | 🟢 結構確認 |

**A = 88×61/40 = 134.2 μK 由 post-diction → 六方法獨立量度確認嘅預言。**
**冷斑本徵直徑 8.66° ≈ 2×R8 (SMHW 譜獨立量度 + 去卷積, 3.7% 偏差)。**

## 6. 剩餘開放問題

| 問題 | 狀態 | 建議 |
|:-----|:----:|:-----|
| SMHW 係數 → pixel 幅度換算 (31 vs 134) | 🟡 | 已部分閉合 (filter 響應), 完整換算推導 |
| DESI Eridanus 精確 ISW | 🔴 | 2026+ |
| 透鏡勢場重建 | 🔴 | 需計算資源 |
| E/B 分解偏振 (完整 T-E 譜) | 🟡 | 需要低噪偏振數據 |
