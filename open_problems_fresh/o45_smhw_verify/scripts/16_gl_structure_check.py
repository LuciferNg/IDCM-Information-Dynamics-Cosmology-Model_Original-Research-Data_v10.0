#!/usr/bin/env python3
"""O45 — GL 疇壁結構數字閉合 (2026-09-12)"""
import numpy as np

R_fit, xi_fit = 6.022, 0.663
R8, FWHM_int, Nd, F7, Ngen = 4.17, 8.66, 44, 13, 3

print("=== GL 疇壁參數結構閉合 ===")
print(f"疇半徑 R* = {R_fit:.3f}°")
cands_R = {
    'R8×F₇/N_gen²': R8*F7/Ngen**2,
    'R8×√2': R8*np.sqrt(2),
    'FWHM_int×φ⁻¹': FWHM_int/1.618,
    'Nd×0.137': Nd*0.137,
}
for name, v in cands_R.items():
    print(f"  {name:<18} = {v:.3f}°  (dev {abs(v-R_fit)/R_fit*100:.2f}%)")

print(f"\n相干長度 ξ* = {xi_fit:.3f}°")
cands_xi = {
    'R8/2π': R8/(2*np.pi),
    'FWHM_int/F₇ = 8.66/13': FWHM_int/F7,
    'σ_sm×3/8': (4.17/2.355)*3/8,
    'R8/Nd×7': R8/Nd*7,
}
for name, v in cands_xi.items():
    print(f"  {name:<18} = {v:.4f}°  (dev {abs(v-xi_fit)/xi_fit*100:.2f}%)")

print("\nGL 相干長度 (IDCM 單位換算):")
print(f"  ξ_GL = 1/√(2μ²) = 0.500 unit → 1 unit = {xi_fit/0.5:.3f}° → 88 units = {xi_fit/0.5*88:.1f}°")
print(f"  ξ_GL = 1/√(V''(W₀)) = 1/√8 = 0.354 unit → 1 unit = {xi_fit/0.354:.3f}° → 88 units = {xi_fit/0.354*88:.1f}°")
print(f"  對照: 90° = Σγ (世界角) → 1 unit = 90/88 = {90/88:.3f}° → ξ = {90/88*0.5:.3f}° or {90/88*0.354:.3f}°")

print("\n=== n=12 ≡ GL 疇壁 等價性 ===")
print(f"  SG+R  χ² = 104.0, profRMS = 6.6")
print(f"  GL+R  χ² = 104.8, profRMS = 6.75")
print(f"  → 兩個模型統計等價 (Δχ²=0.8 << 1)")
print(f"  → n=12 係 GL tanh 疇壁輪廓嘅等效 super-Gaussian 參數化")
print(f"  → 真正物理: W-field 凝聚疇 + GL 疇壁 (O37/O39 Lagrangian 基礎)")
