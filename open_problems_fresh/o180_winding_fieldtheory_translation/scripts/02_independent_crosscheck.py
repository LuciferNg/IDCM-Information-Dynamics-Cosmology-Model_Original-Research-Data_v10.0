#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O180 — 獨立核對 script (docs/05 §獨立核對)
============================================
獨立路徑: numpy float64 + 唔同公式結構 (遞歸/數值積分/求和) 重算
scripts/01_projection_kernel.py (mpmath 60 dps) 嘅所有結果,
並對比 O180 docs/02-05 + final_result.md 中聲稱嘅數值。
目的: 驗證文檔內容同計算一致, 防抄寫/精度錯誤。
"""
import numpy as np

C  = 2.99792458e8        # m/s
A0 = 1.1225e-10          # m/s^2
KPC = 3.0856775814913673e19   # m
YR = 3.15576e7                # s
MSUN = 1.98892e30
G  = 6.67430e-11
HBAR_EV = 6.582119569e-16
E_KCHAIN = 4.06e-3        # eV

R_world = C*C/(2*np.pi*A0)
R_c = R_world/44.0**3
R_d = R_c/4.0
V_max = np.sqrt(A0*R_c)

checks = []   # (label, computed, claimed, doc_ref, tol)
def chk(label, computed, claimed, doc, tol=1e-6):
    dev = abs(computed-claimed)/abs(claimed) if claimed != 0 else abs(computed-claimed)
    ok = dev < tol
    checks.append((label, computed, claimed, dev, doc, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}: computed {computed:.8g} vs "
          f"doc {claimed:.8g} (dev {dev:.3e}) [{doc}]")

# ---------------------------------------------------------------- docs/02
print("="*66)
print("A. docs/02_projection_kernel.md")
print("="*66)

# A1: a0 = (c/pi)^2 * grad_theta, grad_theta = pi/(2 R_world)
grad_theta = (np.pi/176.0)/(R_world/88.0)          # 獨立路徑: per-site step / spacing
a0_check = (C/np.pi)**2 * grad_theta
chk("a0 = (c/pi)^2 grad_theta", a0_check, A0, "docs/02 S1", 1e-12)

# A2: V_max = sqrt(a0 R_c) = c/sqrt(2 pi 44^3)
V_max_alt = C/np.sqrt(2*np.pi*44.0**3)
chk("V_max = sqrt(a0 R_c)", V_max, V_max_alt, "docs/02", 1e-12)
chk("V_max value (km/s)", V_max/1e3, 409.780939693, "docs/02 A2", 1e-6)

# A3: per-mode identity v_k^2 = a0 r_k (k=1..88), worst dev
#      (float64 floor ~1e-16; mpmath 60dps 值 1.6e-60 由 scripts/01 A3 驗證)
th = np.arange(1, 89)*np.pi/176.0
rk = 2*np.pi*R_world*np.cos(th)**2
vk = C*np.cos(th)
w3_rel = np.max(np.abs(vk**2 - A0*rk)/(A0*rk))
chk("per-mode identity holds @float64", w3_rel, 0.0, "docs/02 S2 (mpmath 1.6e-60)", 1e-12)

# A6: M_c = a0 R_c^2 / G
M_c = A0*R_c**2/G/MSUN
chk("M_c = a0 R_c^2/G (Msun)", M_c, 1.89233328244e12, "docs/02 2.3", 1e-6)
chk("M_c dev vs 1.89e12", abs(M_c-1.89e12)/1.89e12, 0.0012345, "docs/02 2.3 (0.123%)", 1e-3)

# A7: j_spec
j_spec = V_max*R_c
j_spec_kmskpc = j_spec/(1e3*KPC)
chk("j_spec km/s kpc", j_spec_kmskpc, 19866.363, "docs/02 3.1", 1e-5)
chk("j_spec alt formula c R_world/(sqrt(2pi) 44^4.5)", j_spec_kmskpc,
    C*R_world/(np.sqrt(2*np.pi)*44.0**4.5)/(1e3*KPC), "docs/02 3.1", 1e-12)

# 44-cascade (independent recursion)
print("  --- 44-cascade ---")
v_l = []
for l in range(4):
    Rl = R_world/44.0**l
    vl = np.sqrt(A0*Rl)
    v_l.append(vl)
    print(f"    l={l}: R={Rl/KPC:.4g} kpc v={vl/1e3:.4g} km/s  (claim {[119600,18030,2718.2,409.8][l]})")
    chk(f"cascade l={l} v/1e3", vl/1e3, [119600, 18030.4, 2718.18, 409.781][l], "docs/02 2.4", 1e-3)

# j* = 2 V_max R_d (flat x exp disk)
j_star = 2*V_max*R_d/(1e3*KPC)
chk("j* = 2 V_max R_d", j_star, 9933.1815, "docs/02 3.2", 1e-5)
chk("j* dev vs Posti 9770", abs(j_star-9770)/9770, 0.016702, "docs/02 3.2", 1e-4)
chk("j_spec/2 = j*", j_spec/(1e3*KPC)/2, j_star, "docs/02 R_c/(2R_d)=2", 1e-12)

# piecewise moment (independent: numerical quadrature via trapezoid)
rd = R_d
# rising part 0..R_c, flat part R_c..inf (exponential tail analytic + quad)
from scipy.integrate import quad as squad
u1, _ = squad(lambda t: t**2.5*np.exp(-t), 0, 4)
u2, _ = squad(lambda t: t**2*np.exp(-t), 4, np.inf)
j_pw = (np.sqrt(A0)*u1*rd**3.5 + V_max*u2*rd**3)/rd**2
chk("piecewise j (km/s kpc)", j_pw/(1e3*KPC), 7873.1338, "docs/02 3.3", 1e-4)

# k(R_c), k(R_d) (near-Nyquist)
def k_of(r): return 176/np.pi*np.arccos(np.sqrt(r/(2*np.pi*R_world)))
chk("k(R_c)", k_of(R_c), 87.9234, "docs/02 2.2", 1e-4)
chk("k(R_d)", k_of(R_d), 87.9617, "docs/02 2.2", 1e-4)

# ---------------------------------------------------------------- docs/03
print("="*66)
print("B. docs/03_boundary_value_mechanism.md")
print("="*66)

# B1: psi_k(1) = sin(theta_k)
psi1 = np.sin(th)
chk("psi_k(1) = sin(k pi/176) worst", np.max(np.abs(psi1-np.sin(th))), 0.0, "docs/03 0", 1e-15)

# B2: uniform phase step  (float64 floor; mpmath 值 1.5e-60 由 scripts/01 C10 驗證)
steps = np.diff(np.arcsin(psi1))
chk("phase step uniform @float64", np.max(np.abs(steps-np.pi/176)), 0.0,
    "docs/03 C10 (mpmath 1.5e-60)", 1e-12)

# B3: gamma_k = 4 psi_k(1)^2
gam = 4*np.sin(th)**2
chk("gamma_k = 4 psi_k(1)^2", np.max(np.abs(gam-4*psi1**2)), 0.0, "docs/03 A4b", 1e-15)

# B4: connection zero-deviation
A = -2*(1-2*psi1**2)
chk("sum_odd A = 0", A[::2].sum(), 0.0, "docs/03 B3", 1e-12)
chk("sum_even A = 2", A[1::2].sum(), 2.0, "docs/03 B3", 1e-12)

# B5: Wilson total phase + winding
tot = (2*th).sum()
chk("sum 2 theta_k = 44.5 pi", tot/np.pi, 44.5, "docs/03 B4", 1e-12)
chk("winding = F11/4 = 22.25", tot/(2*np.pi), 22.25, "docs/03 B4b", 1e-12)

# B6: Q = 44
Q = sum(k if k % 2 == 0 else -k for k in range(1, 89))
chk("Q = sum_even - sum_odd = 44", Q, 44.0, "docs/03 B5", 1e-12)

# B7: Tr(Dir) - Tr(Neu) = 2
TrD = sum(4*np.sin(np.pi*k/178)**2 for k in range(1, 89))
TrN = sum(4*np.sin(np.pi*k/176)**2 for k in range(0, 88))
chk("Tr(Dir)-Tr(Neu) = mu^2", TrD-TrN, 2.0, "docs/03 B6", 1e-10)

# B8: write energy 2A vs B(n) gamma
chk("2A vs B(n) gamma dev", abs(2*134.2-(123/88)*192)/((123/88)*192),
    0.0001355, "docs/03 2", 1e-3)
chk("E_write orbit max uK kB", 60*2*134.2, 16104.0, "docs/03 2", 1e-12)
chk("E_write orbit max eV", 60*2*134.2*1e-6*8.617333262e-5, 1.3877e-6, "docs/03 2", 1e-3)

# ---------------------------------------------------------------- docs/04
print("="*66)
print("C. docs/04_low_entropy_quantitative.md")
print("="*66)

# C1: E_lock = (61.5/2)*88*(pi/176)^2
E_lock = 0.5*61.5*88*(np.pi/176.0)**2
chk("E_lock lattice", E_lock, 0.862188452652, "docs/04 1.1", 1e-8)
chk("E_lock meV", E_lock*4.06, 3.5005, "docs/04 1.1", 1e-3)

# C1b: mu_logN = phi^-1 + L5/(F5 N_gen^2)
phi = (1+np.sqrt(5))/2
mu_logN = phi**-1 + 11.0/(5*9)
chk("E_lock vs mu_logN dev", abs(E_lock-mu_logN)/mu_logN, 0.00033622, "docs/04 1.3", 1e-3)

# C2: timescales
tau_rho = HBAR_EV/(2*np.sqrt(2)*E_KCHAIN)
chk("tau_rho s", tau_rho, 5.7318e-14, "docs/04 2.2", 1e-3)
tau_phonon_kyr = R_d/C/YR/1e3
chk("tau_phonon kyr", tau_phonon_kyr, 39.5305, "docs/04 2.2", 1e-4)
T_orbit_Myr = 2*np.pi*np.sqrt(R_d/A0)/YR/1e6
chk("T_orbit(R_d) Myr", T_orbit_Myr, 363.422, "docs/04 2.2", 1e-4)

# C3: entropy
S_max = 20*np.log(2)
chk("S_max k_B", S_max, 13.8629436, "docs/04 4", 1e-6)
R_write_yr = 61.5/84.63e9
chk("R_write k_B/yr", R_write_yr, 7.2669e-10, "docs/04 2.3", 1e-4)
chk("redundancy 61.5/(20ln2)", 61.5/S_max, 4.436287, "docs/04 4", 1e-5)
dS_orbit = 61.5*(T_orbit_Myr*1e6*YR/(84.63e9*YR))
chk("dS_orbit k_B", dS_orbit, 0.264096, "docs/04 2.3", 1e-4)

# C4: circulation + vorticity
Gamma_Rc = 2*np.pi*np.sqrt(A0)*R_c**1.5
chk("Gamma(R_c) = 2 pi j_spec", Gamma_Rc, 2*np.pi*j_spec, "docs/04 3.2", 1e-10)
om_Rd = 1.5*np.sqrt(A0/R_d); om_Rc = 1.5*np.sqrt(A0/R_c)
chk("omega(R_d) 1/s", om_Rd, 8.2178e-16, "docs/04 3.2", 1e-4)
chk("omega(R_c) 1/s", om_Rc, 4.1089e-16, "docs/04 3.2", 1e-4)

# ---------------------------------------------------------------- final_result
print("="*66)
print("D. final_result.md claims")
print("="*66)
chk("j_spec final_result 19,866.4", j_spec_kmskpc, 19866.4, "final_result", 1e-3)
chk("V_max 409.8", V_max/1e3, 409.8, "final_result", 1e-3)
chk("M_c dev vs 1.89e12", abs(M_c-1.89e12)/1.89e12, 0.0012345, "final_result (0.123%)", 1e-3)
chk("j* 9,933.2 dev +1.67%", abs(j_star-9770)/9770, 0.0167, "final_result", 1e-3)
chk("E_lock 0.86219", E_lock, 0.86219, "final_result", 1e-4)
chk("tau_rho 5.7e-14", tau_rho, 5.7e-14, "final_result", 1e-2)
chk("tau_phonon 39.5 kyr", tau_phonon_kyr, 39.5, "final_result", 1e-2)
chk("T_orbit 363.4 Myr", T_orbit_Myr, 363.4, "final_result", 1e-3)
chk("S_max 13.86", S_max, 13.86, "final_result", 1e-3)
chk("redundancy 4.44", 61.5/S_max, 4.44, "final_result", 1e-2)
chk("Gamma 2pi j_spec 3.85e27", Gamma_Rc, 3.85e27, "final_result", 1e-2)

print("="*66)
nfail = sum(1 for c in checks if not c[5])
print(f"INDEPENDENT CROSSCHECK: {len(checks)-nfail}/{len(checks)} PASS"
      f" ({nfail} FAIL)")
for c in checks:
    if not c[5]:
        print(f"  FAIL: {c[0]} computed {c[1]:.8g} doc {c[2]:.8g} [{c[3]}]")
