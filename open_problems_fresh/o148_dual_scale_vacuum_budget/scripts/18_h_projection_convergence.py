#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O148 scripts/18 — h 三投影收斂深追 (S16)
==========================================
問題: h_cmb 0.67407 / h_o170 0.71157 / h_lad 0.73130 — O170 docs/12 (09-23)
      已判 h_lad stale (基於已證偽 O169 舊伸長律 4.88σ)。剩低收斂缺口:

      h_o170 有兩個候選公式:
      (A) 徑向律精確: h_o170 = ω_ring·√2·ln2/100  (M(0)=√2 = sec(πn_c/88)@n_c=22)
      (B) 代數因子:   h_o170 = h_cmb×(1+1/18)      (19/18 = (2N_gen²+1)/(2N_gen²))
      兩者差 0.007% — 係「數學恒等」定「近似閉合」?

      同埋: IDCM 冇單一 H₀ — 尺度依賴投影框架:
      h_cmb  (CMB 尺度) → Planck 67.4±0.5 ✅ (O167 0.01%)
      h_o170 (徑向尺度) → SH0ES −1.84σ (已測) / BGS −0.37σ (已測) / P1 低z BAO 71.16 (未測)

深追目標:
 1. 精確量度 (A) vs (B) 嘅偏移 — 係真恒等定 0.007% 近似?
 2. 19/18 同 √2·ln2 有冇更深層身份?
 3. 三投影「收斂意義」= IDCM 冇單一 H₀, 係尺度依賴投影 — 證據鏈?
"""
from fractions import Fraction
from decimal import Decimal, getcontext
getcontext().prec = 50

# ── 結構量 ──
omega_ring = Decimal("72.589762")    # 觀測組 72.59 (O167/O73)
pi = Decimal("3.1415926535897932384626433832795028841971693993751")
# √2, ln2 用 Decimal 精確
import math
sqrt2 = Decimal(2).sqrt()
ln2 = Decimal(math.log(2)).quantize(Decimal("1e-40"))  # 唔夠精確 — 用下面更好
# ln2 精確: 用 mpmath 或者 series
getcontext().prec = 60

# 用 Decimal ln(2) series: ln2 = 2(1/2 + 1/(3·2³) + 1/(5·2⁵) + ...) 收斂慢
# 直接用已知 60 位: ln2 = 0.6931471805599453094172321214581765680755001343602552541270
ln2 = Decimal("0.693147180559945309417232121458176568075500134360255254127")
sqrt2 = Decimal("1.414213562373095048801688724209698078569671875376948073176")

# ── h_cmb (O167 結構) ──
h_cmb = (omega_ring / 100) * (Decimal(1) - pi / 44)
print("=" * 96)
print("O148 S16 — h 三投影收斂深追 (h_lad stale 已判: O170 docs/12, 09-23)")
print("=" * 96)
print(f"\nh_cmb (CMB 尺度) = (ω_ring/100)(1−π/44) = {h_cmb:.10f} → H₀ = {h_cmb*100:.4f}")

# ── h_o170 兩候選 ──
h_o170_A = (omega_ring / 100) * sqrt2 * ln2          # 徑向律精確 (√2·ln2)
h_o170_B = h_cmb * (Decimal(1) + Decimal(1)/18)      # 代數因子 19/18
print(f"\nh_o170 (A) 徑向律: ω_ring·√2·ln2/100     = {h_o170_A:.10f} → H₀ = {h_o170_A*100:.4f}")
print(f"h_o170 (B) 代數:  h_cmb·(19/18)           = {h_o170_B:.10f} → H₀ = {h_o170_B*100:.4f}")
dev_A_B = abs(h_o170_A - h_o170_B) / h_o170_A * 100
print(f"偏移 (A) vs (B): {dev_A_B:.6f}%")
print(f"  → 係真恒等? {'🟢 係' if dev_A_B < 1e-6 else '⚠️ 唔係 — 0.007% 級近似閉合'}")

# ── h_lad (stale 參考) ──
h_lad_stale = h_cmb * (Decimal(1) + pi / 37)
print(f"\nh_lad (stale) = h_cmb·(1+π/37)          = {h_lad_stale:.10f} → H₀ = {h_lad_stale*100:.4f} (❌ 舊律, O170 已判)")

# ── 統一因子表 ──
print("\n" + "-" * 96)
print("統一結構 h(scale) = h_cmb × F(scale):")
print("-" * 96)
print(f"  F_cmb    = 1                        (scale: CMB)")
print(f"  F_o170-A = √2·ln2/(1−π/44) = {sqrt2*ln2/(Decimal(1)-pi/44):.12f}  (徑向律精確)")
print(f"  F_o170-B = 19/18            = {Decimal(19)/18:.12f}  (代數)")
print(f"  F_lad    = 1+π/37           = {Decimal(1)+pi/37:.12f}  (階梯, stale)")

# ── √2·ln2 vs 19/18 深層身份 ──
print("\n" + "-" * 96)
print("√2·ln2 vs 19/18 深層身份 (⚠️ 基準不同 — 比較要喺 F 因子層面):")
print("-" * 96)
# 正確比較: 兩者都係「相對於 h_cmb 嘅因子」
# F_o170-A = √2·ln2/(1−π/44)   (作用喺 ω_ring: h = ω_ring/100 × √2·ln2
#                                而 ω_ring/100 = h_cmb/(1−π/44) ⟹ F_A = √2·ln2/(1−π/44))
# F_o170-B = 19/18               (直接乘 h_cmb)
F_A = sqrt2 * ln2 / (Decimal(1) - pi / 44)
F_B = Decimal(19) / 18
print(f"  F_A (√2·ln2 轉 h_cmb 基準) = {F_A:.12f}")
print(f"  F_B (19/18)                = {F_B:.12f}")
print(f"  ★ 正確比較 (F 因子層): dev = {abs(F_A-F_B)/F_A*100:.6f}%  ← 0.007% 級")
print(f"  錯誤直接比較 (唔同基準): √2·ln2={sqrt2*ln2:.9f} vs 19/18={F_B:.9f} → 7.68% — 唔啱, 基準不同!")
print(f"  √2·ln2 = 0.98026 係 ω_ring 因子; 19/18 = 1.05556 係 h_cmb 因子")
print(f"  兩者經 (1−π/44) 橋接: √2·ln2/(1−π/44) = {F_A:.9f} ≈ 19/18")
print(f"")
print(f"  1−√2·ln2 = {Decimal(1)-sqrt2*ln2:.10f} (= 0.0197 = 1.97% = N2 已知投影差)")
print(f"  19/18 = (2N_gen²+1)/(2N_gen²), N_gen=3 — 純代數有理")
print(f"  √2·ln2 係超越數 (√2 代數 × ln2 超越) — 冇可能同有理數恒等!")
print(f"  ⟹ (A) vs (B) 數學上必然差 0.007% — 唔係「未收斂」, 係「超越 vs 有理 嘅必然近似」")
print(f"  ⟹ 觀測上不可分辨 (0.005 km/s/Mpc < DESI DR3 精度 σ_H ~0.5-1.0)")

# ── 觀測對照 ──
print("\n" + "-" * 96)
print("三投影 vs 觀測 (尺度依賴預言):")
print("-" * 96)
obs = [("Planck CMB", 67.4, 0.5), ("SH0ES Cepheid", 73.04, 1.04), ("DESI DR2 BAO(composite)", 68.43, 0.27)]
for name, val, err in obs:
    for label, h in [("h_cmb", h_cmb), ("h_o170A", h_o170_A), ("h_lad(stale)", h_lad_stale)]:
        s = (float(h*100) - val) / err
        if abs(s) < 8:
            print(f"  {name:<22} {val:>6.2f}±{err:<4.2f} vs {label:<12} {float(h*100):>7.3f} → {s:+5.2f}σ")

# ── 收斂判據 ──
print("\n" + "-" * 96)
print("收斂狀態判定:")
print("-" * 96)
print("""O170 docs/12 (09-23) 已判:
  h_lad = 0.73130 ❌ stale — 基於已證偽 O169 舊伸長律 (1+2φ⁻¹ℓ, 4.88σ)
  新橫向律 E(ℓ)=ℓ+1.119 下: H_eff(0.03) = 66.27 ≠ SH0ES 73.04 (−9.3%)
  → SH0ES 匹配失效, 交收 O73/h0_tension (N4)

真正收斂缺口 = h_o170 兩候選 0.007% 偏移:
  (A) √2·ln2 (徑向律精確 — 由 M(0)=√2=sec(π·22/88) 生成)
  (B) 19/18 (代數 — (2N_gen²+1)/(2N_gen²))
  數學必然差: √2·ln2 超越 vs 19/18 有理 ⟹ 永遠差 0.007% — 唔係「未收斂」, 係「兩個近似描述」

判定選項:
  ✓ 如果 19/18 係結構真值 → h_o170 可證偽預言 P1 = 71.152 (低z BAO D_H)
  ✓ 如果 √2·ln2 係徑向律真值 → P1 = 71.157
  ⟹ P1 嘅 0.005 km/s/Mpc 差 (<0.01%) 細過 DESI DR3 精度 (σ_H ~0.5-1.0)
  ⟹ 實際可觀測不可分辨 — 兩候選對觀測都係「71.16」
  ⟹ ★收斂意義: 三投影 → 兩投影 (h_lad stale 排除), 兩投影差 = 尺度依賴 (5.5%)
     h_cmb 67.41 (CMB) vs h_o170 71.16 (徑向) — 由 F = 19/18 ≈ √2·ln2/(1−π/44) 連結
""")

# ── 剩餘開放 (P1 判決點) ──
print("-" * 96)
print("P1 判決時機: DESI DR3 / BGS 完整 D_H (O170 N1) — 屆時 arch M(0.19)≈1.54 直接判生死")
print(f"  h_o170 預言 H₀(徑向) → 0 = {h_o170_A*100:.3f} (√2·ln2) / {h_o170_B*100:.3f} (19/18)")
print("  CMB-S4 σ_H₀ → ±0.1: 可以分辨 67.41 vs 71.16 (框架級) 但唔可以分辨 A/B (0.005)")
print("=" * 96)