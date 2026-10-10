# O48 / Q1.24 — lensing 前向：σ 身份修正

> **日期**: 2026-10-09
> **狀態**: 🔴 概念修正 — σ≈50 唔係 lensing width！
> **Script**: `40_q1_lensing_forward.py`（解析）、`41_q1_lensing_fit.py`（前向 fit）

## 1. 解析公式（CAMB C_φφ）

```
σ_lens² = ½Σ (2ℓ+1)/(4π) ℓ(ℓ+1) C_ℓ^φφ = 3518.7
理論 σ_lens = 59.32  ← 候選 55 (F₁₀) 最近 (差 4.32)
```

✅ 量級正確（期望 40-60）……但係——

## 2. 直接前向 fit（無解析近似）推翻咗個結論 🔴

CAMB lensed vs unlensed TT 譜，掃有效 Gaussian 核（峰谷起伏層面）：

```
起伏 RMS: lensed 0.1320, unlensed 0.1317  ← 幾乎一樣!
最佳 σ = 10 (corr +0.993)  ← 唔係 50/55/60!
σ=40: +0.958, σ=50: +0.943, σ=60: +0.926
```

**lensing 對峰谷起伏嘅平滑好細（有效 σ≈10，近乎 no-op）**——lensing 係
remapping（非卷積），對 peak 位置/高度影響係幾%，唔會將峰抹成 σ=50 嘅高斯。

## 3. 概念修正

- 22/27/33-39 script 用嘅「σ_lens≈40-50/50-60」**唔係 lensing 寬度**——
  係「有效觀測平滑」= binning + beam + lensing 混合
- 解析公式 59.32 計嘅其實係 RMS deflection 相關量，唔係 C_ℓ 平滑核寬度
  （同直接 fit σ≈10 矛盾）——問題喺公式唔係 lensing smoothing
- IDCM 峰谷模型個 σ 係「數據有效平滑」——佢嘅結構身份唔可以靠
  lensing 前向解，要靠 binning/beam 分析

## 4. 誠實裁決

1. 🔴 **σ≈50-60 唔係 lensing width**——前向 fit 顯示 lensing 有效核 ≈10
2. 🟡 σ 身份問題改為「有效平滑參數」：仍係擬合值, 冇獨立機制
   （45/50/55/F₁₀ 平台未分辨, 但而家知道唔係 lensing）
3. ✅ 峰谷模型本身冇受影響（σ 只係形狀參數, platform 穩健）
4. ✅ F₁₀=55 仍係最近 lensing-解析候選但嗰個量無物理意義 → 撤回

## 5. 術語修正（後續文檔）

「σ_lens」→「有效平滑 σ_eff」；22 script 嘅「(σ_lens≈40)」註記更正。
唔可以再用 lensing 前向去 justify σ 值。