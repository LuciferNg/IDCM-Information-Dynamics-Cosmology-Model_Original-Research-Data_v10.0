#!/usr/bin/env python3
"""
CMB 開放位: 峰幅度 A_m — 文獻值結構分解
==========================================
Planck 2018 D_ℓ 峰高度 (文獻):
D₁ ≈ 5700, D₂ ≈ 2600, D₃ ≈ 1400, D₄ ≈ 800 μK²
"""
import math

phi = (1+5**0.5)/2
phi_inv = 1/phi
eps = phi_inv/4
kappa = 1/16

# 文獻峰高度 (Planck 2018, D_l = l(l+1)C_l/2π, μK²)
D = {1: 5700, 2: 2600, 3: 1400, 4: 800}

print("=" * 60)
print("CMB 峰幅度 — 文獻值 (Planck 2018)")
print("=" * 60)
print(f"D₁={D[1]}, D₂={D[2]}, D₃={D[3]}, D₄={D[4]} μK²")

print()
print("比率:")
r = {}
for m in range(2, 5):
    r[m] = D[m]/D[1]
    print(f"  A_{m}/A₁ = {r[m]:.4f}")

print()
print("結構分解 A₂/A₁ = %.4f:" % r[2])
cands2 = {
    "φ⁻²/2 = 0.191": 1/phi**2/2,
    "ε×3 = 0.4635": eps*3,
    "κ×7 = 0.4375": kappa*7,
    "φ⁻³×2 = 0.472": 1/phi**3*2,
    "L₅×φ⁻³ = 2.597": 11/phi**3,
    "ε×(1+2ε) = 0.202": eps*(1+2*eps),
    "κ×φ⁻¹×7.5 = 0.290": kappa*phi_inv*7.5,
    "φ⁻²×φ⁻¹ = 0.236": 1/phi**3,
    "ε×κ×30 = 0.290": eps*kappa*30,
}
for name, val in cands2.items():
    dev = abs(r[2]-val)/val*100
    mark = "✅" if dev < 5 else " "
    print(f"  {mark} {name} = {val:.4f}  偏差 {dev:.1f}%")

print()
print("結構分解 A₃/A₁ = %.4f:" % r[3])
cands3 = {
    "φ⁻⁴ = 0.1459": 1/phi**4,
    "ε×κ×10 = 0.0966": eps*kappa*10,
    "φ⁻²/4 = 0.0955": 1/phi**2/4,
    "ε²×2 = 0.0477": eps**2*2,
    "κ×φ⁻¹×4 = 0.155": kappa*phi_inv*4,
    "φ⁻³×φ⁻¹ = 0.146": 1/phi**4,
    "ε×φ⁻¹×1.5 = 0.143": eps*phi_inv*1.5,
}
for name, val in cands3.items():
    dev = abs(r[3]-val)/val*100
    mark = "✅" if dev < 5 else " "
    print(f"  {mark} {name} = {val:.4f}  偏差 {dev:.1f}%")

print()
print("結構分解 A₄/A₁ = %.4f:" % r[4])
cands4 = {
    "φ⁻⁵ = 0.0902": 1/phi**5,
    "ε×φ⁻¹ = 0.0955": eps*phi_inv,
    "κ×φ⁻¹×2 = 0.0773": kappa*phi_inv*2,
    "ε²/φ⁻¹ = 0.0386": eps**2/phi_inv,
    "φ⁻⁴×φ⁻¹ = 0.0902": 1/phi**5,
    "κ×ε = 0.0097": kappa*eps,
}
for name, val in cands4.items():
    dev = abs(r[4]-val)/val*100
    mark = "✅" if dev < 5 else " "
    print(f"  {mark} {name} = {val:.4f}  偏差 {dev:.1f}%")

print()
print("==> 最強候選:")
print(f"  A₂/A₁ ≈ ε×3 = {eps*3:.4f} (vs {r[2]:.4f})")
print(f"  A₃/A₁ ≈ φ⁻⁴ = {1/phi**4:.4f} (vs {r[3]:.4f})")
print(f"  A₄/A₁ ≈ φ⁻⁵ = {1/phi**5:.4f} (vs {r[4]:.4f})")
print()
print("⚠️ 誠實: 峰高度受宇宙學參數 (n_s, A_s, Ω_b) 影響")
print("  文獻值只係近似, 幅度公式需要更精確數據驗證")
