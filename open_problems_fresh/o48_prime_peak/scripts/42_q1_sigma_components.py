#!/usr/bin/env python3
"""
O48 Q1.25: σ_eff 組成分解 — binning/beam/lensing 逐項估
=============================================================
Q1.24 修正: σ≈50-60 唔係 lensing width, 係「有效平滑」= binning+beam+lensing。
本 script 逐項估 σ_eff 組成:

  1. Binning width: Planck Plik bin 寬 (Δℓ≈9 低ℓ / 17 高ℓ) → 均勻矩形平均
     等效 Gauss σ ≈ Δbin/sqrt(12) (矩形→Gauss 等效)
  2. Beam width: Planck 143GHz beam FWHM≈7.3' → σ_beam(ℓ) = ℓ FWHM/sqrt(8ln2)
     喺 ℓ~1000 幾大?
  3. Lensing: σ≈10 (Q1.24)
  4. 組合: σ_eff² = σ_bin² + σ_beam² + σ_lens²(細)

目標: 睇 σ_eff 有冇可能 ≈ 50-60 (模型擬合值), 定係 beam 喺 ℓ 高先主導。
"""
import math
import numpy as np

print("="*72)
print("A. Binning 平滑 (Plik bin 寬)")
print("="*72)
# Plik: ℓ<1409 每 9 一格; ℓ>1409 每 17/33 一格 (Q1.15 己證)
# 高 ℓ bin 寬 (後期合併): Δbin ~ 17-33
# 但 binning 平滑係「bandpower 平均」——本身係低通, 對峰谷有平滑效應
# 等效 Gauss: 矩形窗寬 W 平滑 → 傳遞函數 sinc(π f W) ≈ exp(-(π f W)²/6)
# 喺 ℓ-space, 峰週期 ~297 → f = 1/297; 平滑 σ_f = W/sqrt(12) (頻率域)
for W in [9, 17, 33]:
    # 平滑喺 ℓ 域: 窗寬 W(ℓ) → 有效 σ ≈ W/sqrt(12) (ℓ 域 RMS 寬度)
    sig_b = W/math.sqrt(12)
    print(f"  bin 寬 W={W:3d}: 等效 σ_bin ≈ {sig_b:.1f}")

print("\n" + "="*72)
print("B. Beam 平滑 (Planck 143 GHz)")
print("="*72)
FWHM = 7.3/60  # 度 → deg
FWHM_rad = math.radians(FWHM)
print(f"Planck 143 GHz beam FWHM = 7.3' = {FWHM*60:.1f} arcmin")
for l in [450, 743, 1044, 1337, 2000]:
    sig = l * FWHM_rad/math.sqrt(8*math.log(2))
    print(f"  ℓ={l:5d}: σ_beam = l·FWHM/√(8ln2) = {sig:6.1f}")

print("\n" + "="*72)
print("C. 組合 σ_eff 估算")
print("="*72)
# 喺低中 ℓ (<1400): beam 效應細; binning+beam+lensing
sig_bin_lo = 9/math.sqrt(12)   # ≈2.6
sig_beam_1044 = 1044*FWHM_rad/math.sqrt(8*math.log(2))
sig_lens = 10  # Q1.24
sig_eff = math.sqrt(sig_bin_lo**2 + sig_beam_1044**2 + sig_lens**2)
print(f"  ℓ=1044: σ_bin≈{sig_bin_lo:.1f}, σ_beam={sig_beam_1044:.1f}, σ_lens={sig_lens:.0f}")
print(f"  σ_eff(ℓ=1044) ≈ {sig_eff:.1f}   ← 模型擬合 σ≈50-60?")
print()
print("  ⟹ 組合值 ~10-15 遠細過 50! 模型 σ 唔係 instrument smoothing!")
print()
print("  ∵ 峰高公式 A(p_j) 本身已包 Silk damping 包絡 exp[-(ℓ/9055)^1.5]")
print("  ∴ 峰其實好尖 (δ-like); 模型用 σ=50 加寬係為咗 cover 峰嘅")
print("    天然寬度 (聲學峰 finite width ~Δℓ≈50-100), 唔係 instrument")
print("="*72)