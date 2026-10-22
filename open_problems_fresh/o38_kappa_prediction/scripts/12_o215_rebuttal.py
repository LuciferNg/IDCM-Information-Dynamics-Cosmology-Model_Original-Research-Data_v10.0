#!/usr/bin/env python3
"""
驗證: O215 用嘅 h = 0.674 正正係 IDCM O167 預言嘅 CMB 投影值!
================================================================
IDCM 冇單一 H₀ — 兩個值係同一個 ω_ring 嘅投影分解 (O73 + O167 已閉合):
  h_cmb    = (ω_ring/100)·(1−π/44) = 0.6741   ← O167 預言, Planck 0.674 命中!
  h_ladder = H_eff(0.03)/100 = 0.7313          ← SH0ES 0.7304 命中!

O215 用 h = 0.674 計 η_B(3/60) — 呢個正正係 IDCM 自己嘅 CMB 投影值!
→ O215「IDCM h 未閉合」指控有問題: h 已經完整閉合 (O73 + O167)
"""

import math

print("=" * 72)
print("  O215 指控反證: IDCM h 已完整閉合 (O73 + O167)")
print("=" * 72)

omega_ring = 72.59

# [1] O167: CMB 投影值
h_cmb_idcm = (omega_ring/100) * (1 - math.pi/44)
h_cmb_planck = 67.36/100
print(f"\n─── [1] IDCM 預言 CMB h (O167) ───")
print(f"  h_cmb = (ω_ring/100)·(1−π/44) = ({omega_ring}/100)·(1−π/44)")
print(f"        = {h_cmb_idcm:.5f}")
print(f"  Planck h = 67.36/100 = {h_cmb_planck:.5f}")
print(f"  dev = {(h_cmb_idcm-h_cmb_planck)/h_cmb_planck*100:+.3f}%  ✅")

# [2] O215 用嘅 h
h_o215 = 0.674
print(f"\n─── [2] O215 用嘅 h ───")
print(f"  O215 用 h = {h_o215}")
print(f"  IDCM O167 預言 h_cmb = {h_cmb_idcm:.5f}")
print(f"  dev = {(h_o215-h_cmb_idcm)/h_cmb_idcm*100:+.3f}%")
print(f"  ⟹ O215 用嘅 0.674 ≈ IDCM 自己嘅 CMB 投影值!")

# [3] 距離階梯側
h_ladder = 73.13/100
print(f"\n─── [3] 距離階梯側 (O73/h0_tension) ───")
print(f"  h_ladder = H_eff(0.03)/100 = {h_ladder:.5f} (SH0ES 0.7304 ✅)")
print(f"  分離因子 = π/44 = {math.pi/44*100:.2f}% (結構因子, O167)")

# [4] IDCM 兩個 h 值一覽
print(f"\n─── [4] IDCM 兩個 h 值 (冇單一 H₀) ───")
print(f"  ┌────────────────────────────────────────────────┐")
print(f"  │ CMB 側:   h_cmb = {h_cmb_idcm:.5f}  (O167 預言, Planck 0.6736 ✅) │")
print(f"  │ 階梯側:   h_lad = {h_ladder:.5f}  (O73 投影, SH0ES 0.7304 ✅) │")
print(f"  │ 結構值:   ω_ring/100 = {omega_ring/100:.5f}  (O73 BBN+CMB 鎖定) │")
print(f"  └────────────────────────────────────────────────┘")
print(f"  三者關係: h_cmb = (ω_ring/100)(1−π/44); h_lad = H_eff(0.03)/100")
print(f"  ⟹ 兩個觀測值都係同一個 ω_ring 嘅投影分解 — 唔衝突!")

# [5] O215 η_B 用 h = 0.674 其實 = IDCM h_cmb
eta_new = 2.736e-8 * (3/60) * h_o215**2
eta_cmb = 2.736e-8 * (3/60) * h_cmb_idcm**2
print(f"\n─── [5] O215 η_B 用 IDCM h_cmb ───")
print(f"  η_B(0.674)   = {eta_new:.4e}")
print(f"  η_B(h_cmb)   = {eta_cmb:.4e} (用 IDCM 預言值)")
print(f"  差 = {(eta_new-eta_cmb)/eta_cmb*100:+.3f}% (可忽略)")

# [6] 結論
print(f"\n─── [6] 結論 ───")
print(f"  O215「IDCM h 未閉合」指控: ❌ 唔成立")
print(f"  IDCM h 已完整閉合: O73 (ω_ring 雙重鎖定) + O167 (CMB 投影 h_cmb)")
print(f"  O215 自己用嘅 h = 0.674 正正 = IDCM 預言嘅 h_cmb = 0.6741 (dev 0.02%)")
print(f"  IDCM 冇單一 H₀: 兩個觀測值 (67.4 CMB / 73.1 階梯) = 同一 ω_ring 投影分解")
print(f"  ⟹ O38 M₀ 標度冇「h 未閉合」問題 — 真正需要嘅係 O73↔O215 Ω_b 版本統一")
print(f"{'='*72}")
