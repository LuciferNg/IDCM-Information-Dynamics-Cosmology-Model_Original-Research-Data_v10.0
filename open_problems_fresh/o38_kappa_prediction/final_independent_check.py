#!/usr/bin/env python3
"""
O38 獨立文檔核對 (Zero-dependency re-verification)
=============================================================
獨立重算 O38 所有核心公式/數值, 再對照文檔聲稱值。
唔 import 任何 O38 script — 由第一原理重算 (防幻覺)。
"""
from mpmath import mp, mpf, sqrt, sin, pi, ln
mp.dps = 50

print("=" * 72)
print("  O38 獨立文檔核對 (零依賴重算, mpmath 50 位)")
print("=" * 72)

checks = []

# ═══ 核心常數 ═══
c_km = mpf("299792.458")
R_world = mpf("4129.94")
omega_ring = mpf("72.59")
Mpc_km = mpf("3.085677581e19")
hbar = mpf("6.582119569e-16")
M_P = mpf("1.220890e28")
E_kchain = mpf("4.060265e-3")
phi = (1 + sqrt(5))/2

# ω_scale (rad/s)
omega_scale = 88 * (c_km*1000) / (R_world * Mpc_km * 1000)
H0_s = omega_ring * 1000 / (Mpc_km * 1000)
ratio = omega_scale / H0_s
print(f"\n─── 核心數值 ───")
print(f"  ω_scale/ω_ring = {float(ratio):.6f}  (期望 88; src R_world 捨入 → dev 3.3e-5)")
checks.append(abs(ratio - 88) < 1e-3)

# M₀
M0_eV = E_kchain * phi**(47 + 37/528)
M0_MeV = M0_eV * 1e-6
print(f"  M₀ = E_kchain·φ^(47+37/528) = {float(M0_MeV):.6f} MeV (docs: 27.9009)")
checks.append(abs(M0_MeV - mpf("27.900915")) < 1e-3)

# κ² = M₀·ω_scale (eV·rad/s)
kappa2 = M0_eV * omega_scale
print(f"  κ² = M₀·ω_scale = {float(kappa2):.6e} eV·rad/s (docs: 5.776e-9)")
checks.append(abs(kappa2 - mpf("5.776e-9")) < mpf("0.05e-9"))

# κ (MeV^½)
kappa_nat = sqrt(M0_MeV)
print(f"  κ (natural) = √M₀ = {float(kappa_nat):.4f} MeV^½ (docs: 5.282)")
checks.append(abs(kappa_nat - mpf("5.2821")) < 1e-3)

# m_7 = M₀·√γ_7
g7 = 4 * sin(pi*7/88)**2
m7 = M0_MeV * sqrt(g7)
print(f"  m_7 = M₀·√γ_7 = {float(m7):.4f} MeV (docs: 13.8002)")
checks.append(abs(m7 - mpf("13.8002")) < mpf("0.01"))

# Σγ_odd / Σγ_even (O34 定義: 88-site 對偶鏈, 分母 176!)
# Σγ_odd  = Σ_{n=1..44} 4sin²(π(2n−1)/176)  (奇數半整數子空間)
# Σγ_even = Σ_{n=1..44} 4sin²(π(2n)/176)    (偶數)
sum_odd = mpf(0); sum_even = mpf(0)
for n in range(1, 45):
    g_odd = 4 * sin(pi*(2*n-1)/176)**2
    g_even = 4 * sin(pi*(2*n)/176)**2
    sum_odd += g_odd
    sum_even += g_even
print(f"  Σγ_odd (176 分母, n=1..44 奇數) = {float(sum_odd):.6f} (期望 88)")
print(f"  Σγ_even (176 分母, n=1..44 偶數) = {float(sum_even):.6f} (期望 90)")
checks.append(abs(sum_odd - 88) < 1e-4)
checks.append(abs(sum_even - 90) < 1e-4)

# R_H = c/ω_ring
R_H = c_km / (omega_ring * 1000 / (Mpc_km * 1000)) / Mpc_km
print(f"  R_H = c/ω_ring = {float(R_H):.4f} Mpc (docs: 4129.94)")
checks.append(abs(R_H - mpf("4129.94")) < mpf("0.01"))

# T_sync = 2π/ω_ring (Gyr)
T_sync = 2*pi/H0_s / mpf("3.15576e16")
print(f"  T_sync = 2π/ω_ring = {float(T_sync):.4f} Gyr (docs: 84.64)")
checks.append(abs(T_sync - mpf("84.64")) < mpf("0.05"))

# O81 裁決: κ_lat²·E_scale² = M₀
B = 4
kappa_lat2 = mpf(1)/(B**4)
E_scale = sqrt(M0_MeV) * B**2
check_scale = kappa_lat2 * E_scale**2
print(f"  O81: κ_lat²·E_scale² = {float(check_scale):.6f} MeV vs M₀ = {float(M0_MeV):.6f} (dev=0)")
checks.append(abs(check_scale - M0_MeV) < 1e-6)

# κ_crit = sin(π/88)/⟨W⟩, ⟨W⟩² = 61.5
W0 = sqrt(mpf("61.5"))
kappa_crit = sin(pi/88) / W0
print(f"  O81: κ_crit = sin(π/88)/⟨W⟩ = {float(kappa_crit):.8f} (docs: 0.00455132)")
checks.append(abs(kappa_crit - mpf("0.00455132")) < 1e-7)

# B⁻⁴ vs κ_crit
print(f"  B⁻⁴ = 1/256 = {float(mpf(1)/256):.8f} /κ_crit = {float(mpf(1)/256/kappa_crit):.4f} (亞臨界 ✅)")

# O167: h_cmb
h_cmb = (omega_ring/100) * (1 - pi/44)
print(f"  O167: h_cmb = (ω_ring/100)(1−π/44) = {float(h_cmb):.5f} (docs: 0.67407)")
checks.append(abs(h_cmb - mpf("0.67407")) < 1e-4)

# O170: H₀ = c·ln4/(R_world·√2)
H0_o170 = c_km * ln(4) / (R_world * sqrt(2))
print(f"  O170: H₀ = c·ln4/(R_world·√2) = {float(H0_o170):.3f} (O170 聲稱 71.157)")
checks.append(abs(H0_o170 - mpf("71.157")) < mpf("0.01"))

# O170 vs O73 張力
print(f"  O170 vs O73: dev = {float(abs(H0_o170-omega_ring)/omega_ring*100):.2f}% (docs: 1.97%)")

print(f"\n{'='*72}")
n_ok = sum(1 for c in checks if c)
print(f"  獨立核對: {n_ok}/{len(checks)} PASS")
print("=" * 72)
import sys
sys.exit(0 if all(checks) else 1)
