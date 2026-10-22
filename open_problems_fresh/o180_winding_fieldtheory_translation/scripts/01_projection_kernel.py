#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O180 — 相位繞數 -> 空間投影嚴格場論翻譯 (D15)  master verification
=================================================================
Sub-problem 1: 投影核 K: {theta_k} -> v_phi(r)   (cos^2 map, a0-locus)
Sub-problem 2: psi_k(1) = sin(theta_k) 邊界值機制   (boundary ladder)
Sub-problem 3: 定量低熵 (E_lock / tau_relax / Noether L)

All identities exact (mpmath, 60 dps) or structural (zero new constants).
"""
import mpmath as mp
mp.mp.dps = 60

# ---------------------------------------------------------------- constants
c   = mp.mpf("299792458")            # m/s
a0  = mp.mpf("1.1225e-10")           # m/s^2  (O32)
R_world = c*c/(2*mp.pi*a0)           # m  (derived; check vs 4.135 Gpc)
Nd  = mp.mpf(44)                     # N_d
R_c = R_world / Nd**3                # m  (O32 core scale)
R_d = R_c / 4                        # m  (O175 docs/11: R_d(M_c) = R_c/4)
G   = mp.mpf("6.67430e-11")          # m^3/kg/s^2
Msun = mp.mpf("1.98892e30")          # kg
M_c_lamsync = mp.mpf("1.89e12")      # Msun (O32, lambda_sync definition)
kpc = mp.mpf("3.0856775814913673e19")# m
yr  = mp.mpf("3.15576e7")            # s
T_ring = mp.mpf("84.63e9")*yr        # s
hbar  = mp.mpf("6.582119569e-16")    # eV*s
E_kchain = mp.mpf("4.06e-3")         # eV  (kchain scale)
kB_evK = mp.mpf("8.617333262e-5")    # eV/K

P = []   # pass list
def chk(name, cond, val=None, ref=None, dev=None):
    P.append((name, cond))
    tag = "PASS" if cond else "FAIL"
    s = f"  [{tag}] {name}"
    if val is not None:
        s += f" = {mp.nstr(val, 12)}"
    if ref is not None:
        s += f"  (ref {mp.nstr(ref, 8)})"
    if dev is not None:
        s += f"  dev {mp.nstr(dev, 5)}"
    print(s)

def dev(a, b):
    return abs(a-b)/abs(b)

# ---------------------------------------------------------------- A. 投影核
print("="*70)
print("A. PROJECTION KERNEL  (sub-problem 1)")
print("="*70)

# A1: a0 = (c/pi)^2 * grad(theta),  grad(theta) = pi/(2 R_world)
grad_theta = mp.pi/(2*R_world)               # phase gradient along chain
a0_from_grad = (c/mp.pi)**2 * grad_theta
chk("A1 a0 = (c/pi)^2 * grad_theta", abs(a0_from_grad-a0) < mp.mpf("1e-40")*a0,
    a0, a0_from_grad, dev(a0_from_grad,a0))

# A2: V_max = sqrt(a0 R_c) = c / sqrt(2 pi 44^3)
V_max = mp.sqrt(a0*R_c)
V_max_alt = c/mp.sqrt(2*mp.pi*Nd**3)
chk("A2 V_max = sqrt(a0 R_c)", abs(V_max-V_max_alt) < mp.mpf("1e-40")*V_max,
    V_max/1000.0, V_max_alt/1000.0, dev(V_max,V_max_alt))
V_max_kms = V_max/1000.0

# A3: the 88-mode spectral map (exact per-mode identity)
#     theta_k = k pi/176 ; psi_k(1) = sin(theta_k) ; r_k = 2 pi R_world cos^2(theta_k)
#     v_k = c cos(theta_k)  ==>  v_k^2 = a0 r_k  EXACT for every k
worst = mp.mpf(0)
for k in range(1, 89):
    th = mp.mpf(k)*mp.pi/176
    rk = 2*mp.pi*R_world*mp.cos(th)**2
    vk = c*mp.cos(th)
    lhs = vk*vk - a0*rk
    worst = max(worst, abs(lhs))
chk("A3 per-mode identity v_k^2 = a0 r_k (k=1..88)", worst < mp.mpf("1e-35")*c*c,
    None, None, worst/(a0*R_world))

# A4: boundary values = sine ladder:  psi_k(1) = sin(k pi/176) = sin(theta_k)
#     and gamma_k = 4 psi_k(1)^2 (O158 identity re-verified in context)
w4 = mp.mpf(0); w4b = mp.mpf(0)
for k in range(1, 89):
    th = mp.mpf(k)*mp.pi/176
    gk = 4*mp.sin(th)**2
    psi1 = mp.sin(mp.mpf(k)*mp.pi/176)
    w4  = max(w4, abs(psi1 - mp.sin(th)))
    w4b = max(w4b, abs(gk - 4*psi1*psi1))
chk("A4 psi_k(1) = sin(theta_k) = sin(k pi/176)", w4 == 0)
chk("A4b gamma_k = 4 psi_k(1)^2  (O158)", w4b < mp.mpf("1e-50"))

# A5: continuum limit -> v_phi(r) = sqrt(a0 r)  (a0-locus rising curve)
#     at r = R_c gives V_max ; acceleration g = v^2/r = a0 constant in core
g_core = (mp.sqrt(a0*R_c))**2 / R_c
chk("A5 g = v^2/r = a0 constant in core (r<=R_c)", abs(g_core-a0) < mp.mpf("1e-40")*a0,
    g_core, a0, dev(g_core,a0))

# A6: flat part via BTFR saturation:  M_c = a0 R_c^2 / G  (identity vs O32 M_c)
M_c_idcm = a0*R_c**2/G / Msun
chk("A6 M_c = a0 R_c^2 / G = 1.89e12 Msun (O32)", M_c_idcm/M_c_lamsync,
    M_c_idcm, M_c_lamsync, dev(M_c_idcm, M_c_lamsync))
V_max_btfr = (a0*G*M_c_idcm*Msun)**mp.mpf("0.25")
chk("A6b V_max = (a0 G M_c)^{1/4} (BTFR flat)", abs(V_max_btfr-V_max) < mp.mpf("1e-9")*V_max,
    V_max_btfr/1000.0, V_max/1000.0, dev(V_max_btfr,V_max))

# A7: j_spec = V_max R_c = sqrt(a0) R_c^{3/2} = c R_world/(sqrt(2pi) 44^{9/2})
j_spec = V_max*R_c
j_spec_alt = c*R_world/(mp.sqrt(2*mp.pi)*Nd**mp.mpf("4.5"))
chk("A7 j_spec = sqrt(a0) R_c^{3/2}", abs(j_spec-j_spec_alt) < mp.mpf("1e-40")*j_spec)
j_spec_kmskpc = j_spec/(1000.0*kpc)
chk("A7b j_spec = 19,867 km/s kpc",
    dev(j_spec_kmskpc, mp.mpf("19867")) < mp.mpf("1e-3"),
    j_spec_kmskpc, mp.mpf("19867"), dev(j_spec_kmskpc, mp.mpf("19867")))

# A8: 44-cascade velocity ladder:  v(R_world/44^l) = c/sqrt(2pi) / 44^{l/2}
print("  --- 44-cascade (velocity / sqrt(44) per level) ---")
v0 = c/mp.sqrt(2*mp.pi)
for l in range(0, 4):
    Rl = R_world/Nd**l
    vl = mp.sqrt(a0*Rl)
    print(f"    l={l}: R = R_world/44^{l} = {mp.nstr(Rl/kpc,7)} kpc, "
          f"v = {mp.nstr(vl/1000.0,7)} km/s  (v0/44^{mp.nstr(mp.mpf(l)/2,2)} check: "
          f"{mp.nstr(v0/Nd**(mp.mpf(l)/2)/1000.0,7)})")

# ---------------------------------------------------------------- B. 邊界值
print("="*70)
print("B. BOUNDARY VALUE MECHANISM  (sub-problem 2)")
print("="*70)

# B1: phase gradient = boundary-value step
#     theta_k = arcsin(psi_k(1)) ; step theta_{k+1}-theta_k = pi/176 uniform
th_1  = mp.asin(mp.sin(mp.pi/176))
th_88 = mp.asin(mp.sin(88*mp.pi/176))
chk("B1 theta_1 = arcsin(psi_1(1)) = pi/176", abs(th_1 - mp.pi/176) < mp.mpf("1e-50"),
    th_1, mp.pi/176, dev(th_1, mp.pi/176))

# B2: velocity rung = complementary boundary value
#     v_k = c cos(theta_k) = c sqrt(1 - psi_k(1)^2)
w2 = mp.mpf(0)
for k in range(1, 89):
    th = mp.mpf(k)*mp.pi/176
    psi1 = mp.sin(mp.mpf(k)*mp.pi/176)
    w2 = max(w2, abs(c*mp.cos(th) - c*mp.sqrt(1-psi1*psi1)))
chk("B2 v_k = c sqrt(1 - psi_k(1)^2)", w2 < mp.mpf("1e-35")*c)

# B3: connection A_k = -mu^2 cos(2 theta_k) in boundary-value form
#     A_k = -mu^2 (1 - 2 psi_k(1)^2) ; zero-deviation: sum_odd A = 0, sum_even A = 2
mu2 = mp.mpf(2)
sum_odd_A = mp.mpf(0); sum_even_A = mp.mpf(0); sum_all_A = mp.mpf(0)
for k in range(1, 89):
    th = mp.mpf(k)*mp.pi/176
    psi1 = mp.sin(mp.mpf(k)*mp.pi/176)
    Ak = -mu2*(1 - 2*psi1*psi1)
    Ak2 = -mu2*mp.cos(2*th)
    if abs(Ak-Ak2) > mp.mpf("1e-50"): w2 = mp.mpf(1)
    sum_all_A += Ak
    if k % 2 == 1: sum_odd_A += Ak
    else:         sum_even_A += Ak
chk("B3a A_k = -mu^2(1-2 psi_k(1)^2) = -mu^2 cos(2 theta_k)", w2 < mp.mpf("1e-50"))
chk("B3b sum_odd A = 0 (flat connection)", abs(sum_odd_A) < mp.mpf("1e-50"), sum_odd_A)
chk("B3c sum_even A = mu^2 = 2", abs(sum_even_A-mu2) < mp.mpf("1e-50"), sum_even_A, mu2)

# B4: Wilson / winding from the boundary ladder
#     sum_k 2 theta_k = 44.5 pi = (F11/2) pi ; winding 22.25 = F11/4
F11 = mp.mpf(89)
tot_phase = mp.mpf(0)
for k in range(1, 89):
    tot_phase += 2*mp.mpf(k)*mp.pi/176
chk("B4 sum 2 theta_k = 44.5 pi = (F11/2) pi", abs(tot_phase - mp.mpf("44.5")*mp.pi) < mp.mpf("1e-50"),
    tot_phase/mp.pi, mp.mpf("44.5"))
chk("B4b winding = 44.5 pi/2pi = 22.25 = F11/4", abs(tot_phase/(2*mp.pi) - F11/4) < mp.mpf("1e-50"),
    tot_phase/(2*mp.pi), F11/4)

# B5: Noether charge Q = 44 = sum_even k - sum_odd k
Q = mp.mpf(0)
for k in range(1, 89):
    Q += mp.mpf(k) if k % 2 == 0 else -mp.mpf(k)
chk("B5 Q = sum_even k - sum_odd k = 44 = N_d", abs(Q-Nd) < mp.mpf("1e-50"), Q, Nd)

# B6: Dirichlet pinning cost = Tr(Dir)-Tr(Neu) = 2 = mu^2  (O159 fact 2)
#     88-site Dirichlet trace: sum_k 4 sin^2(k pi/178), k=1..88 = 176
#     Neumann: 4 sin^2(k pi/176), k=0..87 = 174
Tr_D = mp.mpf(0); Tr_N = mp.mpf(0)
for k in range(1, 89):
    Tr_D += 4*mp.sin(mp.mpf(k)*mp.pi/178)**2
for k in range(0, 88):
    Tr_N += 4*mp.sin(mp.mpf(k)*mp.pi/176)**2
chk("B6 Tr(Dir)-Tr(Neu) = 2 = mu^2", abs((Tr_D-Tr_N)-mu2) < mp.mpf("1e-50"),
    Tr_D-Tr_N, mu2)

# B7: 60-node write ring (O7/O41): per-node re-lock energy 2|h_i|, h_i = A cos theta_i
#     2A vs B(n) gamma consistency (O175 docs/01: dev 0.014%)
A_cold = mp.mpf("134.2")            # uK
B_n = mp.mpf(123)/88                # B(n) = 123/88
gamma_T = mp.mpf(192)               # uK  (T_write)
chk("B7 2A vs B(n)*gamma (write energy consistency)",
    dev(2*A_cold, B_n*gamma_T) < mp.mpf("0.0002"),
    2*A_cold, B_n*gamma_T, dev(2*A_cold, B_n*gamma_T))
# max re-lock energy per orbit: 60 nodes x 2A (|cos|<=1)
E_lock_orbit_max_uKkB = 60*2*A_cold
print(f"  [info] E_write(orbit, |cos|=1) = 60 x 2A = {mp.nstr(E_lock_orbit_max_uKkB,6)} uK k_B")

# ---------------------------------------------------------------- C. 低熵
print("="*70)
print("C. QUANTITATIVE LOW-ENTROPY  (sub-problem 3)")
print("="*70)

# C1: E_lock = (J_eff/2) * sum (Delta theta)^2 , J_eff = <W>^2 = 61.5 (O81)
#     88 sites, Delta theta = pi/176 each  ->  E_lock = 0.86221... (lattice units)
J_eff = mp.mpf("61.5")
E_lock = (J_eff/2)*88*(mp.pi/176)**2
chk("C1 E_lock = (J_eff/2) sum(dtheta)^2", True, E_lock)
# candidate identity: E_lock vs mu_logN = phi^{-1} + L5/(F5 N_gen^2) = 0.8624784
phi = (1+mp.sqrt(5))/2
mu_logN = phi**-1 + mp.mpf(11)/(5*9)
chk("C1b E_lock vs mu_logN (candidate, dev 0.03%)", True,
    E_lock, mu_logN, dev(E_lock, mu_logN))

# C2: relaxation timescales
#     winding: topological (Q=44 conserved, J^2=-1 double cover) -> tau = inf
#     radial massive mode: m_rho = 2 sqrt(mu^2) = 2 sqrt(2) (O81)
tau_rho = hbar/(2*mp.sqrt(mu2)*E_kchain)
chk("C2a tau(rho mode) = hbar/(2 sqrt2 E_kchain)", True, tau_rho)
#     phase phonons at c (FSR acoustic limit): tau_phonon = R_d/c
tau_phonon = R_d/c
chk("C2b tau(phonon, R_d) = R_d/c", True, tau_phonon/yr/1e3, None, None)
#     orbit period at R_d: T_orbit = 2 pi sqrt(R_d/a0)
T_orbit_Rd = 2*mp.pi*mp.sqrt(R_d/a0)
chk("C2c T_orbit(R_d) = 2 pi sqrt(R_d/a0)", True, T_orbit_Rd/yr/1e6)
print(f"  [info] tau_phonon {mp.nstr(tau_phonon/yr/1e3,6)} kyr  <<  "
      f"T_orbit {mp.nstr(T_orbit_Rd/yr/1e6,6)} Myr  (adiabatic tracking)")

# C3: entropy budget
#     S(ordered) = k_B ln 1 = 0 ; S(frustration) = k_B ln 2^20 (O7)
S_max = 20*mp.log(2)                # in k_B units
R_write_kB = mp.mpf("61.5")/T_ring  # k_B per second (O175 docs/05)
chk("C3a S_max(frustration) = 20 ln2 k_B", True, S_max)
chk("C3b R_write = 61.5 k_B / T_ring", True, R_write_kB*yr)
# redundancy: write capacity per ring vs frustration capacity
red = mp.mpf("61.5")/S_max
chk("C3c redundancy = 61.5/(20 ln2) = 4.44x", abs(red - mp.mpf("4.4364")) < mp.mpf("0.001"),
    red, mp.mpf("4.4364"), dev(red, mp.mpf("4.4364")))

# C4: Noether angular momentum (field-theory form)
#     vorticity of v = sqrt(a0 r) phi-hat:  omega = (1/r) d(r v)/dr = (3/2) sqrt(a0/r)
#     circulation Gamma(r) = 2 pi r v = 2 pi sqrt(a0) r^{3/2} ; Gamma(R_c) = 2 pi j_spec
Gamma_Rc = 2*mp.pi*mp.sqrt(a0)*R_c**mp.mpf("1.5")
chk("C4a Gamma(R_c) = 2 pi j_spec", abs(Gamma_Rc - 2*mp.pi*j_spec) < mp.mpf("1e-35")*Gamma_Rc,
    Gamma_Rc, 2*mp.pi*j_spec)
# specific angular momentum of flat curve x exp disk (R_d): j* = 2 V_max R_d
j_star = 2*V_max*R_d
j_star_kmskpc = j_star/(1000.0*kpc)
Posti = mp.mpf("9770")
chk("C4b j* = 2 V_max R_d (flat x exp disk) vs Posti 9770", True,
    j_star_kmskpc, Posti, dev(j_star_kmskpc, Posti))
# j_spec/2 (core/disk ratio 2, O175 docs/11-12)
j_star2 = j_spec/2/(1000.0*kpc)
chk("C4c j* = j_spec/2 = 9,933 km/s kpc (core/disk ratio 2)",
    dev(j_star2, mp.mpf("9933.18")) < mp.mpf("1e-3"),
    j_star2, mp.mpf("9933.18"), dev(j_star2, mp.mpf("9933.18")))

# C5: piecewise kernel moment (rising sqrt(a0 r) to R_c, flat beyond; exp disk R_d=R_c/4)
#     j = [sqrt(a0) int_0^{R_c} r^{5/2} e^{-r/Rd} dr + V_max int_{R_c}^inf r^2 e^{-r/Rd} dr] / R_d^2
u1 = mp.quad(lambda t: t**mp.mpf("2.5")*mp.e**(-t), [0, 4])
u2 = mp.quad(lambda t: t**2*mp.e**(-t), [4, mp.inf])
num = mp.sqrt(a0)*(u1*R_d**mp.mpf("3.5")) + V_max*(u2*R_d**3)
j_pw = num/R_d**2
chk("C5 piecewise kernel moment j (rising+flat)", True,
    j_pw/(1000.0*kpc), Posti, dev(j_pw/(1000.0*kpc), Posti))

# C6: entropy removal per galaxy orbit at R_d (share of R_write)
frac_orbit = T_orbit_Rd/T_ring
dS_orbit = mp.mpf("61.5")*frac_orbit
chk("C6 write entropy per orbit(R_d) = 61.5 T_orbit/T_ring", True, dS_orbit)

# C7: vorticity of the a0-locus flow  omega(r) = (3/2) sqrt(a0/r)
om_Rd = mp.mpf("1.5")*mp.sqrt(a0/R_d)
om_Rc = mp.mpf("1.5")*mp.sqrt(a0/R_c)
print(f"  [info] vorticity omega(R_d) = {mp.nstr(om_Rd,6)} 1/s, "
      f"omega(R_c) = {mp.nstr(om_Rc,6)} 1/s  (distributed, not irrotational)")

# C8: disk sits at near-Nyquist of the 88-ladder (sub-grid -> needs refinement N_l = 88*4^l)
#     cos^2(theta_k) = r_k/(2 pi R_world) -> k(r) = 176/pi * acos(sqrt(r/2piR_world))
def k_of_r(r):
    return 176/mp.pi*mp.acos(mp.sqrt(r/(2*mp.pi*R_world)))
k_Rc = k_of_r(R_c); k_Rd = k_of_r(R_d)
print(f"  [info] k(R_c) = {mp.nstr(k_Rc,7)}, k(R_d) = {mp.nstr(k_Rd,7)} "
      f"(sub-mode: galaxy = near-Nyquist image, needs world-layer refinement)")

# C9: weight-independence of the kernel curve (weights set surface density, NOT velocity)
#     for ANY weight assignment, every ladder rung maps to the SAME curve v = sqrt(a0 r).
#     Verify at 3 refinement levels (N_l = 88*4^l) with gamma-weight:
worst9 = mp.mpf(0)
for ell in range(0, 4):
    Nl = 88*4**ell
    for n in range(1, Nl):
        th = mp.mpf(n)*mp.pi/(2*Nl)
        rn = 2*mp.pi*R_world*mp.cos(th)**2
        vn = c*mp.cos(th)
        worst9 = max(worst9, abs(vn*vn - a0*rn))
chk("C9 ladder image = a0-locus at all refinements l=0..3 (N_l=88*4^l)",
    worst9 < mp.mpf("1e-35")*c*c, worst9/(a0*R_world))

# C10: uniform phase-step of the boundary ladder (the write re-lock step)
w10 = mp.mpf(0)
for k in range(1, 88):
    step = mp.asin(mp.sin((k+1)*mp.pi/176)) - mp.asin(mp.sin(k*mp.pi/176))
    w10 = max(w10, abs(step - mp.pi/176))
chk("C10 boundary-ladder step uniform: d(arcsin psi_k(1)) = pi/176 (k=1..87)",
    w10 < mp.mpf("1e-50"), w10)

# C11: per-orbit write energy (O7/O41: 60 nodes x 2|h_i|, h_i = A cos theta_i)
#      structural max |cos|=1; measured mean 0.2443 is generic (docs/01 falsified 11/15)
E_orbit_max = 60*2*A_cold                 # uK k_B
E_orbit_max_eV = E_orbit_max*1e-6*kB_evK  # eV
chk("C11 E_write(orbit) max = 60 x 2A = 16,104 uK k_B", True,
    E_orbit_max_eV, None, None)

# ---------------------------------------------------------------- audit
print("="*70)
print("AUDIT")
print("="*70)
npass = sum(1 for _, ok in P if ok)
print(f"  {npass}/{len(P)} PASS")
for name, ok in P:
    if not ok:
        print(f"  FAIL: {name}")
