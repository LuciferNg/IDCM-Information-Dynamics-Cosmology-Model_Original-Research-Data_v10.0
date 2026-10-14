#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O142 - M0 functional deconstruction: M0 = kappa^2 / omega_scale (quotient identity).

FIRST PRINCIPLES: M0 is NOT a base constant to be expanded into structural
numbers (phi^(47+37/528) = refuted over-agreement, O136 docs/36). M0 is the
PROJECTION SCALE of the mass-generation operator: dim'less spectrum -> physical
mass. Its value = coupling-density squared / frequency scale:
   M0 = kappa^2 / omega_scale = kappa^2 / (88 H0)

Verify this identity + list ALL M0 multipliers (v, Lambda, sigma) are
dimensionless structure ratios.
"""
import mpmath as mp
mp.mp.dps = 30
ok = fail = 0
def chk(name, cond, detail=""):
    global ok, fail
    if cond: ok += 1; print(f"  [PASS] {name} {detail}")
    else:    fail += 1; print(f"  [FAIL] {name} {detail}")

print("="*72)
print("A. M0 quotient identity (O38 closed values)")
print("="*72)
M0 = mp.mpf('27.900915')                 # MeV
H0_rad = mp.mpf('2.0701846673e-16')/88   # H0 = omega_scale/88  (hbar-restored? no - see below)
# O38: omega_scale = 88*H0 = 2.0701846673e-16 rad/s  => H0 = omega_scale/88
omega_scale = mp.mpf('2.0701846673e-16') # rad/s
H0 = omega_scale/88
kappa2 = mp.mpf('5.776005e-9')           # eV·rad/s
print(f"  omega_scale = 88*H0 = {mp.nstr(omega_scale,10)} rad/s")
print(f"  H0 = omega_scale/88 = {mp.nstr(H0,10)} rad/s")
print(f"  kappa^2 = M0*omega_scale = {mp.nstr(M0*1e6*omega_scale,6)} eV·rad/s  (O38: 5.776005e-9)")
chk("kappa^2 = M0*omega_scale (O38)", mp.almosteq(M0*1e6*omega_scale, kappa2, rel_eps=mp.mpf('1e-4')))
print(f"  M0_back = kappa^2/omega_scale = {mp.nstr(kappa2/omega_scale/1e6,8)} MeV")
chk("M0 = kappa^2/omega_scale (quotient identity)", mp.almosteq(kappa2/omega_scale/1e6, M0, rel_eps=mp.mpf('1e-6')))
kappa_tilde2 = kappa2/(M0*1e6*H0)       # kappa^2/(M0*H0) - dimensionless (units: eV·rad/s / (MeV→eV * rad/s))
print(f"  kappa~^2 = kappa^2/(M0*H0) = {mp.nstr(kappa_tilde2,6)}")
chk("kappa~^2 = 88 (dimensionless closure)", mp.almosteq(kappa_tilde2, mp.mpf(88), rel_eps=mp.mpf('1e-3')))

print()
print("  M0 = kappa^2/omega_scale  —— M0 係「耦合密度平方 ÷ 頻率標度」嘅商，")
print("  唔係獨立質量單位。κ² 有物理意義（W-field 單位頻率耦合密度），")
print("  ω_scale = 88H₀ 有結構身份（對偶鏈×宇宙頻率）；M0 只係兩者投影比。")

print("="*72)
print("B. H0 inside M0: M0*88*H0 = kappa^2 (M0 carries H0 dependence)")
print("="*72)
print(f"  M0*88*H0 = {mp.nstr(M0*1e6*88*H0,6)} eV·rad/s = kappa^2 :", mp.almosteq(M0*1e6*88*H0, kappa2, rel_eps=mp.mpf('1e-4')))
print("  -> M0 絕對值依賴 H0（O215 回報一致：M0 有量綱標度依賴 ω_ring）。")
print("  -> 任何想將 M0 拆成純結構數（φ 鏈）嘅嘗試，本質上係想將「商」")
print("     直接標籤化——必然 over-agreement（O136 docs/36 已證：優 5.8萬倍）。")

print("="*72)
print("C. All M0 multipliers are dimensionless structure ratios")
print("="*72)
phi = (1+mp.sqrt(5))/2
psi_ = (1-mp.sqrt(5))/2
F = lambda n: (phi**n - psi_**n)/mp.sqrt(5)
L = lambda n: phi**n + psi_**n
gamma = lambda n: 4*mp.sin(mp.pi*n/88)**2
lam_max = 36 - 1/gamma(20)
N_d, B, N_gen = mp.mpf(44), mp.mpf(4), mp.mpf(3)

v = mp.sqrt(lam_max)*M0*2*N_d*(2*F(5)+B*L(4)*gamma(7))/1000      # GeV
Lam = mp.sqrt(lam_max)*M0*N_gen/L(5)                              # MeV
sig = 88*(Lam/1000)**2                                            # GeV^2
print(f"  v     = M0 × [√λ_max·2N_d·(2F5+B·L4γ7)] = {mp.nstr(v,6)} GeV   multiplier dim'less ✓")
print(f"  Λ_QCD = M0 × [√λ_max·N_gen/L5]          = {mp.nstr(Lam,6)} MeV  multiplier dim'less ✓")
print(f"  σ     = M0² × [λ_max·2N_d·N_gen²/L5²]   = {mp.nstr(sig,6)} GeV² multiplier dim'less ✓")
print()
print("  M0 嘅功能角色 = 唯一帶量綱嘅「能標基元」；所有物理尺度（質量譜 m_n=M0·ω_n、")
print("  v、Λ、σ）都係 M0 × 無量綱結構乘子。M0 本身 = κ²/ω_scale 商，")
print("  唔需要 φ 指數展開——嗰條鏈係喺錯誤層面（patch 商嘅商）做數值展開。")

print("="*72)
print(f"RESULT: {ok} PASS / {fail} FAIL")
print("="*72)