#!/usr/bin/env python3
"""
O12: ³He/H primordial 分辨力分析 (v2)
=====================================
IDCM 9.76e-6 (D/H × φ⁻²) vs ΛCDM ~1.04e-5 vs 觀測約束

關鍵文獻 (verified from full text):
  [1] Cooke et al. 2022 (arXiv:2203.11256, ApJ 2022)
      - Orion ³He/⁴He = (1.77±0.13)×10⁻⁴ (CRIRES 直接量度)
      - SM (³He/⁴He)_p = (1.257±0.017)×10⁻⁴
      - GCE fit (³He/⁴He)_p = (1.043±0.089)×10⁻⁴ (誤差唔包 model/yield)
      - Empirical limit (³He/H)_p ≤ (1.09±0.18)×10⁻⁵
  [2] Johnson, Weller & Cooke 2025 (arXiv:2510.08689)
      - 現有量度唔夠精確/唔夠多 → 需要 ~4 個新 ³He/⁴He 量度先達 ~30% 精度
  [3] Balser & Bania 2018 (arXiv:1810.09422) — GBT ³He+ HII regions
      - S209 (外銀河系) ³He/H = (1.10±0.28)×10⁻⁵ ← 最接近 primordial 嘅量度
  [4] Bania & Balser 2020 (arXiv:2012.11707) — GBT ³He+ PNe
"""
import math

phi = (1 + 5**0.5) / 2
phi_inv = 1 / phi

print("=" * 70)
print("O12 ³He/H primordial 分辨力分析 (v2)")
print("=" * 70)

# ── 1. 模型預測 ──
D_H = 2.555e-5          # IDCM 已閉合 (bbn 06_complete_record)
He3_H_IDCM = D_H * phi_inv**2    # 9.755e-6
He3_H_LCDM = 1.04e-5             # ΛCDM 標準預測 (Cooke 2022 引用)
print("\n[1] 模型預測")
print(f"  D/H (IDCM 閉合)        = {D_H:.4e}")
print(f"  ³He/H IDCM = D/H×φ⁻²   = {He3_H_IDCM:.4e}")
print(f"  ³He/H ΛCDM             = {He3_H_LCDM:.4e}")
diff_pct = abs(He3_H_IDCM - He3_H_LCDM) / He3_H_LCDM * 100
print(f"  兩模型差距             = {diff_pct:.2f}%")

# ── 2. 觀測約束 (2022-2025) ──
print("\n[2] 觀測約束")

# (a) Cooke 2022 empirical limit
lim = 1.09e-5
lim_err = 0.18e-5
print(f"  (a) Cooke 2022 empirical limit (³He/H)_p ≤ {lim:.2e} ± {lim_err:.2e} [1]")
print(f"      1σ range: [{lim-lim_err:.2e}, {lim+lim_err:.2e}]")
print(f"      2σ range: [{lim-2*lim_err:.2e}, {lim+2*lim_err:.2e}]")
print(f"      IDCM 9.76e-6 喺 1σ 內? {'✅' if lim-lim_err < He3_H_IDCM < lim+lim_err else '❌'}")
print(f"      ΛCDM 1.04e-5 喺 1σ 內? {'✅' if lim-lim_err < He3_H_LCDM < lim+lim_err else '❌'}")

# (b) S209 Balser & Bania 2018
s209 = 1.10e-5
s209_err = 0.28e-5
print(f"  (b) S209 外銀河系 HII 區 ³He/H = ({s209:.2e} ± {s209_err:.2e}) [3]")
print(f"      (最接近 primordial 嘅直接量度, 但 ³He 有 post-BBN production)")
z_idcm = abs(He3_H_IDCM - s209) / s209_err
z_lcdm = abs(He3_H_LCDM - s209) / s209_err
print(f"      IDCM vs S209: {abs(He3_H_IDCM-s209)/s209*100:.1f}% 偏差 = {z_idcm:.2f}σ")
print(f"      ΛCDM vs S209: {abs(He3_H_LCDM-s209)/s209*100:.1f}% 偏差 = {z_lcdm:.2f}σ")

# (c) Orion ³He/⁴He direct
print(f"\n  (c) Cooke 2022 Orion ³He/⁴He = (1.77±0.13)×10⁻⁴ (CRIRES 直接量度) [1]")
print(f"      SM primordial (³He/⁴He)_p = (1.257±0.017)×10⁻⁴ [1]")
print(f"      GCE fit (³He/⁴He)_p = (1.043±0.089)×10⁻⁴ [1]")

# ³He/⁴He 模型推導
Yp_IDCM = 0.2496
Yp_obs = 0.2453
Yp_obs_err = 0.0034
He4_H_IDCM = Yp_IDCM / (4 * (1 - Yp_IDCM))
He4_H_obs = Yp_obs / (4 * (1 - Yp_obs))
He3_He4_IDCM = He3_H_IDCM / He4_H_IDCM
He3_He4_LCDM = He3_H_LCDM / He4_H_obs
print(f"\n  (d) ³He/⁴He 模型推導 (由 ³He/H + Y_p)")
print(f"      Y_p IDCM = {Yp_IDCM} → ⁴He/H = {He4_H_IDCM:.5f}")
print(f"      Y_p 觀測 = {Yp_obs} → ⁴He/H = {He4_H_obs:.5f}")
print(f"      ³He/⁴He (IDCM) = {He3_He4_IDCM:.4e}")
print(f"      ³He/⁴He (ΛCDM) = {He3_He4_LCDM:.4e}")

# 對比 3 個基準
refs = [
    ("SM (³He/⁴He)_p", 1.257e-4, 0.017e-4),
    ("GCE fit (³He/⁴He)_p", 1.043e-4, 0.089e-4),
]
for name, val, err in refs:
    for mname, mval in [("IDCM", He3_He4_IDCM), ("ΛCDM", He3_He4_LCDM)]:
        sigma = abs(mval - val) / err
        pct = abs(mval - val) / val * 100
        print(f"      {mname} vs {name} {val:.3e}: 偏差 {pct:.1f}% = {sigma:.1f}σ")

# ── 3. 分辨力分析 ──
print("\n[3] 分辨力分析")
print(f"  模型差距: {diff_pct:.2f}% (IDCM 9.76e-6 vs ΛCDM 1.04e-5)")
print(f"  觀測誤差 (Cooke limit 1σ): {lim_err/lim*100:.1f}%")
print(f"  觀測誤差 (S209 1σ): {s209_err/s209*100:.1f}%")
print(f"  → 需要 <{diff_pct/2:.1f}% 誤差先可以 2σ 分辨")
print(f"  → {'🟡 分辨唔到: 誤差大過模型差距' if lim_err/lim > diff_pct/100 else '🟢 可分辨'}")

# Johnson 2025
print(f"\n  Johnson 2025: 需要 ~4 個新 ³He/⁴He 量度 (太陽 3kpc 內) 先達 ~30% 精度 [2]")
print(f"  → 30% >> 6.2% 模型差距 → 2026 年止根本分辨唔到")

# 加權平均 (S209 + empirical limit 都指向 ~1.0-1.1e-5)
print(f"\n  觀測加權平均傾向: S209 1.10e-5, empirical limit 1.09e-5")
print(f"  → 兩者都喺 IDCM 9.76e-6 同 ΛCDM 1.04e-5 之間, 偏向 ΛCDM 側但誤差大")

# ── 4. 結論 ──
print("\n[4] 結論")
print(f"  (1) IDCM 9.76e-6 完全 consistent with Cooke 2022 empirical limit (1.09±0.18)e-5 ✅")
print(f"  (2) ΛCDM 1.04e-5 都 consistent ✅")
print(f"  (3) S209 量度 1.10e-5: IDCM 0.50σ, ΛCDM 0.21σ — 兩者都兼容 🟡")
print(f"  (4) ³He/⁴He 角度 (SM 1.257e-4): IDCM 有 ~4.9σ 名義張力 (未計系統誤差)")
print(f"      vs GCE fit 1.043e-4: IDCM 1.5σ, ΛCDM 2.7σ — 反轉!")
print(f"  (5) 誠實結論: ³He 係 IDCM 最弱嘅 BBN 測試 — 觀測極難, 誤差太大")
print(f"      2026 年止觀測分辨唔到 IDCM vs ΛCDM")
print()
print("  分辨所需: ³He/H 直接量度 (DLA/HII) 誤差 <3% 先可以分辨 6% 差距")
print("  未來: ngVLA (2030s) ³He+ 觀測 / JWST HII 區高分辨光譜 / 更多 DLA ³He 嘗試")
