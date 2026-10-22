#!/usr/bin/env python3
"""
O215 指控影響量化: ω_ring 若由 72.59 → 66.83, M₀ 標度變化
================================================================
O215 新 Ω_b = 3/60 暗示 ω_ring' = 66.83 (接近 Planck 67.36)
→ O38 M₀ 有量綱標度依賴 ω_ring (E_kchain ∝ √ω_ring)
→ 量化 M₀ 變化
"""

import math
from decimal import Decimal, getcontext
getcontext().prec = 50

phi = (Decimal(1) + Decimal(5).sqrt())/Decimal(2)

print("=" * 70)
print("  O215 指控影響量化: M₀ 標度 vs ω_ring")
print("=" * 70)

# 現行 O38/O73: ω_ring = 72.59
omega_ring_old = 72.59
omega_ring_new = 66.83   # O215 Ω_b = 3/60 暗示

# M₀ = E_kchain·φ^(47+37/528), E_kchain = √(M_P·ħ·ω_ring)·(1891/2025)
# E_kchain ∝ √ω_ring
E_kchain_old = Decimal('4.060265e-3')   # eV (O34, ω_ring = 72.59)
ratio = Decimal(math.sqrt(omega_ring_new/omega_ring_old))
E_kchain_new = E_kchain_old * ratio
M0_old = E_kchain_old * phi**(Decimal(47) + Decimal(37)/Decimal(528))
M0_new = E_kchain_new * phi**(Decimal(47) + Decimal(37)/Decimal(528))

print(f"\n─── M₀ 標度變化 ───")
print(f"  ω_ring: {omega_ring_old} → {omega_ring_new} (×{omega_ring_new/omega_ring_old:.4f})")
print(f"  E_kchain: {float(E_kchain_old)*1e3:.6f} → {float(E_kchain_new)*1e3:.6f} meV (∝√ω_ring)")
print(f"  M₀: {float(M0_old)*1e-3:.4f} → {float(M0_new)*1e-3:.4f} MeV")
dev_m0 = abs(float(M0_new)-float(M0_old))/float(M0_old)*100
print(f"  M₀ 變化: {dev_m0:.2f}%")

# κ 變化
print(f"\n─── κ 變化 ───")
kappa_old_keV = 9.4186
kappa_new_keV = kappa_old_keV * math.sqrt(omega_ring_new/omega_ring_old)
print(f"  κ: {kappa_old_keV} → {kappa_new_keV:.4f} keV")

# 質量譜變化
print(f"\n─── 質量譜變化 (m_n = M₀·ω_n) ───")
m7_old = 13.8002
m7_new = m7_old * float(ratio)
print(f"  m_7: {m7_old} → {m7_new:.4f} MeV")
print(f"  m_7 目標 (DM) = 13.8 MeV: dev {(m7_new-13.8)/13.8*100:+.2f}%")

# ω_scale 變化
print(f"\n─── ω_scale 變化 ───")
# ω_scale = 88·ω_ring (s⁻¹ 標度)
print(f"  ω_scale ∝ ω_ring: ×{omega_ring_new/omega_ring_old:.4f}")
print(f"  (ω_scale 同 M₀ 同方向變化)")

# κ̃² 不受影響
print(f"\n─── κ̃² = 88 不受影響 ───")
print(f"  κ̃² = ω_scale/H₀ = 88 恆等 (H₀ 約分!)")
print(f"  無量綱, 同 ω_ring 數值無關 ✅")

# 關鍵: m_7 目標
print(f"\n─── 關鍵判定 ───")
print(f"  m_7 = M₀·√γ_7 目標 13.8 MeV (DM)")
print(f"  若 ω_ring = 66.83: m_7 = {m7_new:.3f} MeV (dev {(m7_new-13.8)/13.8*100:+.2f}%)")
print(f"  ⟹ ω_ring 更改會破壞 m_7 = 13.8 MeV 閉合!")
print(f"  ⟹ O38/O34 標度鏈同 O215 新 Ω_b 有真實張力")

# 反查: 要同時滿足 m_7 = 13.8 同 Ω_b·h² = 0.02237?
print(f"\n─── 雙重約束 ───")
print(f"  約束 1: m_7 = 13.8 MeV → ω_ring = 72.59 (O34/O38 鏈)")
print(f"  約束 2: Ω_b·h² = 0.02237 → 若 Ω_b = 3/60, h = 0.674 → ω_ring = 67.4")
print(f"  兩約束衝突: 72.59 vs 67.4 → dev {(72.59-67.4)/67.4*100:.1f}%")
print(f"  ⟹ 真開放問題: Ω_b 版本 (19/450 vs 3/60) 決定 ω_ring, 決定 M₀")
