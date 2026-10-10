# O48 / Q1.26-28 — 攻峰形：逐峰 fit v1-v3 結果（誠實彙報）

> **日期**: 2026-10-09
> **狀態**: 🟡 峰形測量 partial — 右重確認, 但逐峰 fit 方法唔可靠
> **Script**: `43_q1_peak_shape.py` (v1), `44` (v2 SPT), `45` (v3 asym),
>            `46 q1_peak_shape_stats` (v3b 錯誤單位), `46b` (v3c μK² 修正)

## 1. 峰形 fit 三版演化

| 版本 | 方法 | 結果 | 問題 |
|:-----|:-----|:-----|:-----|
| v1 (43) | Plik, 全域 3次poly detrend, grid Gauss/Lorentz | Lorentz 全勝, σ_m {70,36,40,42,46} 遞增, γ≈38≈峰間隙/8 | 全域 detrend 污染; m=1 σ=70 異常 |
| v2 (44) | SPT-3G cross-check | 冇分辨力 (χ² 全0) | **SPT bins 疏** (每峰 2-4 點), binning 教訓重現 |
| v3 (45) | 乾淨 window + 不對稱 Lorentz | γR/γL=1.18 右重, m pattern 唔一致 | grid search 冇 error bar |
| v3b (46) | + Plik covariance | χ² 爆 2e11, fit 心漂走 | **單位 bug**: fractional residual 配 μK² covariance (scripts/36 教訓重踩) |
| v3c (46b) | μK² 全單位 + local baseline | B1 右重 PASS, C1 γ=35 帶內 PASS; fit 心仍漂 (m=1 c=96), A 爆細 | 逐峰獨立 fit 喺 Plik binning 下超參數化 |

## 2. 可靠結論 (跨版本一致)

- ✅ **峰形右重**: γR>γL 喺 v3 (γR/γL=1.18) 同 v3c (γR=41.5 vs γL=28.5,
  ratio 1.46) 兩度確認 → **峰右邊延伸, 同 Q1.16 谷偏近後峰 22% 一致**
  (峰形不對稱由兩個獨立方向支持)
- ✅ γ ≈ 35-38, 同 Q1.25 σ≈50 (Gauss σ 定義) 同階, 亦 ≈ 峰間隙/8 37.1
- 🟡 峰形 fit 心漂走 (m=1 c=96 vs 221, m=7 c=1429 vs 1409)、A 收縮到 0.00
  —— 逐峰獨立 Lorentz fit 喺 Plik bins (峰±130 內 ~30 點) 下 over-parameterized,
  峰形曲線 + baseline 唔夠分辨

## 3. 方法論教訓

1. Plik-lite 峰形測量: 峰±130 window 得 ~30 bins (每 9 一格), fit 3+ 參數
   (c, γL, γR, A) + baseline → 唔可靠; **峰形需要 joint fit 或高分辨譜**
2. SPT/ACT bins 疏 → 峰形冇分辨力 (44 已示範)
3. **covariance 檢驗必須 μK² 全單位** (scripts/36 教訓再次應驗) —
   fractional residual 配 μK² covariance 必然爆

## 4. 「攻峰形」實際成果

- 峰形**右對稱性**已由谷位 (Q1.16 27:7 分點) + 峰 fit (γR/γL=1.18-1.46) 雙重支持
- 峰寬 σ≈50 = 峰固有寬度 (Q1.25, 唔係 instrument)
- 峰形完整重建 (峰梳−谷梳干涉) 已喺 Q1.17/20 閉合 (SPT covariance Δχ²=347)
- 🟡 剩: 峰形「定量形狀」 (Lorentz/Gauss/Voigt 分類 + γL/γR 逐峰值)
  在 Plik binning 下未可測 — 需高分辨 (均勻網格) 譜或 joint acoustic fit

## 5. 建議

峰形定量測量唔應該再喺 Plik-lite 磨——本質限制 (bin 疏)。真正路徑:
- joint fit: 一次性 fit 峰位+峰高+單一峰形參數族 across 全部峰 (不逐峰獨立)
- 或揾均勻網格譜 (CAMB 級? 但有 alias 問題) / 更高ℓ 高分辨數據