#!/usr/bin/env python3
"""
O215 指控判定 — IDCM h 未閉合 (O38 M₀ 標度) 完整分析
================================================================
目標: 判定 O215 指控是否成立 + 影響範圍

  [A] O73 用 Ω_b = 19/450 (O14) 鎖定 ω_ring = 72.73 (BBN 0.19%)
  [B] O215 用 Ω_b = 3/60 (O163 新) → 如果 IDCM ω_ring = 72.59:
      Ω_b·h² = 0.02635 vs Planck 0.02237 → +17.8% ❌
  [C] 反查: 如果 Ω_b = 3/60, BBN 公式應該鎖定 ω_ring = ?
      ω_ring ∝ 1/√Ω_b (ρ_c = 3ω²/8πG ∝ η_B/Ω_b)
  [D] O38 核心閉合 κ̃² = 88 是否受影響 (無量綱 vs 有量綱)?
"""

import math

print("=" * 72)
print("  O215 指控判定: IDCM h 未閉合")
print("=" * 72)

# ═══ [A] O73 鎖定 ═══
print("\n─── [A] O73 BBN 鎖定 (Ω_b = 19/450) ───")
Omega_b_O14 = 19/450
omega_ring_O73 = 72.73   # BBN 鎖定值
print(f"  Ω_b(O14) = 19/450 = {Omega_b_O14:.6f}")
print(f"  ω_ring(BBN) = {omega_ring_O73} (dev 0.19%)")
print(f"  ω_ring(IDCM) = 72.59 (src)")

# ═══ [B] O215 用新 Ω_b ═══
print("\n─── [B] O215 新 Ω_b = 3/60 ───")
Omega_b_O215 = 3/60
h_planck = 0.674
h_idcm = 72.59/100
print(f"  Ω_b(O215) = 3/60 = {Omega_b_O215:.6f}")
print(f"  用 IDCM h = {h_idcm}: Ω_b·h² = {Omega_b_O215*h_idcm**2:.5f} → dev {(Omega_b_O215*h_idcm**2-0.02237)/0.02237*100:+.2f}% ❌")
print(f"  用 Planck h = {h_planck}: Ω_b·h² = {Omega_b_O215*h_planck**2:.5f} → dev {(Omega_b_O215*h_planck**2-0.02237)/0.02237*100:+.2f}% ✅")
print(f"  ⟹ O215 被迫用 Planck h → 「IDCM h 未閉合」")

# ═══ [C] 反查: Ω_b = 3/60 應鎖定 ω_ring = ? ═══
print("\n─── [C] 反查: Ω_b = 3/60 嘅 BBN 鎖定 ═══")
# ω_ring ∝ 1/√Ω_b (ρ_c = 3ω²/8πG, η_B = n_b/n_γ 固定)
omega_ring_new = omega_ring_O73 * math.sqrt(Omega_b_O14/Omega_b_O215)
print(f"  ω_ring' = ω_ring(O73) × √(Ω_b(O14)/Ω_b(O215))")
print(f"         = {omega_ring_O73} × √({Omega_b_O14:.5f}/{Omega_b_O215:.5f})")
print(f"         = {omega_ring_new:.2f} km/s/Mpc")
print(f"  vs Planck 67.36: dev {(omega_ring_new-67.36)/67.36*100:+.2f}%")
print(f"  vs IDCM 72.59:  dev {(omega_ring_new-72.59)/72.59*100:+.2f}%")
print(f"  ⟹ 新 Ω_b 推嘅 ω_ring 接近 Planck 67.36, 唔係 72.59!")

# ═══ [D] O38 核心閉合影響 ═══
print("\n─── [D] O38 核心閉合 κ̃² = 88 是否受影響 ───")
print(f"  O38 核心閉合: κ̃² = κ²/(M₀·H₀) = ω_scale/H₀ = 88")
print(f"  κ̃² 係無量綱 (88 = 2N_d = Σγ_odd)")
print(f"  ω_scale/H₀ = 88 恆等 (H₀ 約分!) — 唔依賴 H₀ 數值!")
print(f"  ⟹ O38 核心閉合 κ̃² = 88 唔受 ω_ring 數值影響 ✅")
print(f"  O38 有量綱部分: κ² = M₀·ω_scale = 5.776e-9 eV·rad/s")
print(f"    M₀ = 27.9 MeV 依賴 ω_ring (E_kchain ∝ √ω_ring)")
print(f"    ⟹ 如果 ω_ring 改 (72.59 → 66.8), M₀ 標度都會變")

# ═══ [E] 判定 ═══
print("\n─── [E] 判定 ───")
print(f"  O215 指控「IDCM h 未閉合」: 部分成立")
print(f"  ✅ 成立部分: O73 (Ω_b=19/450) 同 O215 (Ω_b=3/60) 用唔同 Ω_b,")
print(f"     IDCM h = 0.7259 同新 Ω_b = 3/60 唔 self-consistent (+17.8%)")
print(f"  ✅ O38 核心閉合 κ̃² = 88 (無量綱) 完全不受影響")
print(f"  ✅ O38 M₀ 有量綱標度依賴 ω_ring → ω_ring 若改,M₀ 要重算")
print(f"  ❌ O215 將問題標記為「O38 M₀ 標度」— 實際上係 O73↔O215")
print(f"     嘅 Ω_b 版本衝突 (O14 19/450 vs O163/O215 3/60)")

# 用 Planck h 反推 IDCM 需要幾多 Ω_b
print(f"\n─── [F] 自洽性: IDCM h = 0.7259 需要 Ω_b = ? ───")
Omega_b_req = 0.02237/h_idcm**2
print(f"  Ω_b_req = 0.02237/{h_idcm}² = {Omega_b_req:.6f}")
print(f"  = {Omega_b_req*450:.1f}/450 vs 19/450 (O14)")
print(f"  = {Omega_b_req*60:.2f}/60  vs 3/60 (O215)")
print(f"  O14 19/450 = {19/450:.6f}: dev {(19/450-Omega_b_req)/Omega_b_req*100:+.2f}%")
print(f"  O215 3/60 = {3/60:.6f}: dev {(3/60-Omega_b_req)/Omega_b_req*100:+.2f}%")

# η_B 兩通道比較
print(f"\n─── [G] η_B 通道比較 ───")
eta_old = 2.736e-8 * (19/450) * h_idcm**2
eta_new = 2.736e-8 * (3/60) * h_planck**2
print(f"  舊: η_B = 2.736e-8×(19/450)×{h_idcm}² = {eta_old:.4e} (−0.57% 意外互補)")
print(f"  新: η_B = 2.736e-8×(3/60)×{h_planck}² = {eta_new:.4e} (+1.84%)")
print(f"  兩者都係「放棄值 × h 互補」— 冇一個係第一性原理自洽!")

print(f"\n{'='*72}")
print(f"  結論: O38 核心閉合 (κ̃²=88, 無量綱) 不受影響 ✅")
print(f"        O38 M₀ 有量綱標度依賴 ω_ring → ω_ring 由 O73 閉合 (19/450)")
print(f"        O215 用新 Ω_b=3/60 → IDCM h 需要重新審視 (O73↔O215 衝突)")
print(f"        真正開放: Ω_b 版本統一 (19/450 vs 3/60) + ω_ring 重鎖定")
print(f"{'='*72}")
