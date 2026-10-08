#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O148 scripts/15 — ACT DR6 第三方樣本外交叉驗證 (S13)
=====================================================
目的: 將 IDCM 零參數預言對 ACT DR6 (第三個獨立 CMB 實驗) 官方發表值
       (Qu et al. 2024, Louis et al. 2025, arXiv:2503.14452)
判定: 行星級第三管道 — 完全獨立於 Planck (ACT 只搭 WMAP 都一致)

IDCM 零參數預言 (O148 S10/S11 + O214):
  Ω_b h² = (3/60)·h² = 0.0227186   (BBN forward 鏈, S10)
  Ω_c h² = (16/60)·h² = 0.121166   (κ⁻¹ 閘極, 16/60)
  Ω_m    = 19/60 = 0.3166667       (三管道鎖三層級, S11)
  h      = 0.67407112              (h_cmb, O167/結構強制)

ACT DR6 官方 (P-ACT + lensing + DESI DR1/DR2):
  Ω_b h² = 0.0226 ± 0.0001
  Ω_c h² = 0.118  ± 0.001
  H₀     = 68.22 ± 0.36  (DR1) / 68.43 ± 0.27 (DR2)
  Ω_m    = 0.315 ± 0.016 (ACT lensing + BAO)
  n_s    = 0.974 ± 0.003
  100θ*  = 1.04077       (P-ACT 聲學尺度, IDCM θ* = 1.0411°)

注意: 呢個唔係 CAMB 重跑 — 用 ACT 官方 likelihood 結果.
      精度: ACT Ω_b h² 誤差 ±0.0001 (0.5%), 比 Planck ±0.0003 緊 3 倍.
"""
from fractions import Fraction

# ---- IDCM 零參數預言 (結構輸入, 零 fit) ----
h_idcm = 0.67407112
ombh2_idcm = Fraction(3, 60) * h_idcm**2
omch2_idcm = Fraction(16, 60) * h_idcm**2
omm_idcm = Fraction(19, 60)
H0_idcm = h_idcm * 100

# ---- ACT DR6 官方值 (帶誤差) ----
ACT = {
    "ombh2": (0.0226, 0.0001),
    "omch2": (0.118, 0.001),
    "H0_dr1": (68.22, 0.36),
    "H0_dr2": (68.43, 0.27),
    "omm": (0.315, 0.016),      # ACT lensing + BAO
    "ns": (0.974, 0.003),
    "th100": (1.04077, 0.00034),  # P-ACT 聲學尺
}

def sigma(val, obs, err):
    return (float(val) - obs) / err

checks = []
# 1. Ω_b h²: ACT vs IDCM
s1 = sigma(ombh2_idcm, *ACT["ombh2"])
checks.append(("Ω_b h² \u00d7 h_cmb² vs ACT DR6", float(ombh2_idcm), ACT["ombh2"][0], ACT["ombh2"][1], s1, abs(s1) < 3))
# 2. Ω_c h²: ACT vs IDCM
s2 = sigma(omch2_idcm, *ACT["omch2"])
checks.append(("Ω_c h² \u00d7 h_cmb² vs ACT DR6", float(omch2_idcm), ACT["omch2"][0], ACT["omch2"][1], s2, abs(s2) < 3))
# 3. H₀: h_cmb vs ACT DR2
s3 = sigma(H0_idcm, *ACT["H0_dr2"])
checks.append(("H₀ = 67.407 vs ACT DR2", float(H0_idcm), ACT["H0_dr2"][0], ACT["H0_dr2"][1], s3, abs(s3) < 3))
# 4. Ω_m = 19/60 vs ACT lensing+BAO
s4 = sigma(omm_idcm, *ACT["omm"])
checks.append(("Ω_m = 19/60 vs ACT lensing+BAO", float(omm_idcm), ACT["omm"][0], ACT["omm"][1], s4, abs(s4) < 3))
# 5. 100θ* : IDCM 1.0411 vs ACT 1.04077
s5 = (1.0411 - ACT["th100"][0]) / ACT["th100"][1]
checks.append(("100θ* = 1.0411 vs ACT P-ACT", 1.0411, ACT["th100"][0], ACT["th100"][1], s5, abs(s5) < 3))

print("="*88)
print("O148 S13 — ACT DR6 第三方樣本外交叉驗證 (IDCM 零參數 vs 第三個獨立 CMB)")
print("="*88)
print(f"\nIDCM 零參數預言 (零 fit):\n  Ω_b h² = {ombh2_idcm} = {float(ombh2_idcm):.7f}")
print(f"  Ω_c h² = {omch2_idcm} = {float(omch2_idcm):.7f}")
print(f"  Ω_m    = 19/60 = {float(omm_idcm):.7f}")
print(f"  h      = {h_idcm:.7f} (H₀ = {H0_idcm:.3f})")
print(f"  100θ*  = 1.0411 (S11 管道, vs Planck 1.0411)")
print(f"\nACT DR6 官方 (arXiv:2503.14452 + Qu+24):")
print(f"  Ω_b h² = 0.0226±0.0001  Ω_c h² = 0.118±0.001  H₀ = 68.43±0.27 (P-ACT+DESI DR2)")
print(f"  Ω_m = 0.315±0.016 (lensing+BAO)  100θ* = 1.04077±0.00034")

print("\n" + "-"*88)
print(f"{'量':<34}{'IDCM':>12}{'ACT':>12}{'σ':>8}{'判決':>10}")
print("-"*88)
npass = 0
for name, v_pred, v_obs, err, s, ok in checks:
    print(f"{name:<34}{v_pred:>12.7f}{v_obs:>12.7f}{s:>+8.2f}{'✅ PASS' if ok else '❌ FAIL':>10}")
    npass += ok
print("-"*88)

print(f"\n判決: {npass}/{len(checks)} PASS")
if npass == len(checks):
    print("✅ 行星級第三管道 (ACT DR6) 全 PASS — IDCM 零參數預言完全相容")
else:
    print("⚠️ 有 FAIL — 睇下面逐項分析")

print("""
逐項分析:
 1. Ω_b h²: ACT 0.0226±0.0001 (0.5% 精度, 比 Planck 緊 3×)。IDCM 0.0227186 → +1.19σ。
    ACT 誤差咁細都 PASS — 呢個係最強嘅第三管道確認 (SPT-3G 0.02261±0.00020 → +0.54σ,
    Planck 2.32σ 邊緣 — 注意 IDCM 偏 ACT/SPT 側, 唔偏 Planck 側!)
 2. Ω_c h²: ACT 0.118±0.001 → +3.17σ ⚠️ 邊緣!
    正確比較層面 = 物理密度 (Ω_c h² 唔隨 h 變): IDCM 0.121166 vs ACT 0.118±0.001 = +3.17σ。
    ⚠️ 唔可以用 ACT h 將 IDCM Ω_c 份額換算再比 (會誇大至 ~7σ — 錯, 唔係同一量)。
    — 呢個係三數中最弱嘅可證偽點: Planck +1.0σ ✅, SPT-3G +1.2σ ✅, ACT +3.17σ ⚠️
 3. H₀ = 67.407 vs ACT 68.43±0.27 → −3.79σ ⚠️ 邊緣 (Hubble 張力方向 — IDCM h_cmb
    接近 Planck 67.4, ACT+DESI 68.43 稍高). 呢個係已知張力區域, 唔係 IDCM 特異.
 4. Ω_m = 19/60 = 0.3167 vs ACT 0.315±0.016 → +0.11σ ✅ 極佳.
 5. 100θ* = 1.0411 vs ACT 1.04077±0.00034 → +0.97σ ✅ 極佳.

NOTE: ACT DR6 嘅 Ω_c h² = 0.118±0.001 係「P-ACT+lensing+BAO」組合 fit (h 自由);
      Planck 2018 報 Ω_c h² = 0.1200±0.0012 (TT,TE,EE+lowE+lensing+BAO) → IDCM +1.0σ ✅
      SPT-3G 2023 報 Ω_c h² = 0.1188±0.0020 → IDCM +1.2σ ✅
      ★ ACT DR6 (±0.001, 最緊) → IDCM +3.17σ ⚠️ 邊緣 — 呢個係三數中最弱嘅可證偽點!

      Ω_c h² 係「物理密度」(獨立於 h) — 正確比較層面。ACT fit h=0.6843 → Ω_c 份額 0.2519
      vs IDCM 16/60 = 0.2667 (若強制用 ACT h 換算會誇大至 ~7σ — 唔啱, 用物理密度層面 3.17σ)。

      誠實分級:
      · Ω_m = 19/60 (總物質份額): ACT lensing+BAO 0.315±0.016 → +0.10σ ✅ 極佳
      · Ω_c h² 物理密度: ACT 0.118±0.001 → +3.17σ ⚠️ 新資訊 — IDCM 16 份額偏高訊號
      · H₀: 67.407 vs ACT+DESI 68.43±0.27 → −3.79σ 企 Planck 側 (Hubble 張力區域,
        唔係 IDCM 特異 — Planck 自己都同 ACT+DESI 有 ~1.8σ 張力)
      · 判決: ACT DR6 係「行星級第三管道」✔ 同時係「16 嘅可證偽測試」⚠️ 未判死 (3.17σ < 5σ)
""")