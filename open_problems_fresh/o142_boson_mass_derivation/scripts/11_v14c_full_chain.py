#!/usr/bin/env python3
# -*- coding: ascii -*-
"""O142 v14c - FULL self-consistent chain: IDCM 6-flavor world -> decoupled QCD world.

Answer to candidate A (scheme correspondence) in its strongest form:
  Lambda_IDCM = sqrt(lam_max)*M0*N_gen/L5  [structural, zero fit]
  1) 1-loop Nf=6 formula gives alpha6(M_Z) = 1/((7/2pi) ln(M_Z/Lambda_IDCM)).
  2) Run alpha6 UP from M_Z to m_t (Nf=6), decouple top (alpha5(m_t)=alpha6(m_t)),
     run alpha5 DOWN through m_b, m_c to 2 GeV / m_tau / 5 GeV with 3-loop MS-bar
     beta (CORRECT normalization b0/2pi, b1/8pi^2, b2/32pi^3 -- v14b finding).
  3) Compare out-of-sample alpha_s(m_tau), alpha_s(2 GeV), alpha_s(5 GeV) with PDG.
     Pre-registered: GREEN <2sigma, YELLOW <3sigma, RED >3sigma.

Includes 1-loop chain (to reproduce v13c3 [C] +0.79%) and 2-loop for sensitivity.
"""
import mpmath as mp
mp.mp.dps = 40

phi = (1+mp.sqrt(5))/2
psi_ = (1-mp.sqrt(5))/2
L = lambda n: phi**n + psi_**n
F = lambda n: (phi**n - psi_**n)/mp.sqrt(5)
gamma = lambda n: 4*mp.sin(mp.pi*n/88)**2

M0 = mp.mpf('27.900915')
N_d, B, N_gen = mp.mpf(44), mp.mpf(4), mp.mpf(3)
lam_max = 36 - 1/gamma(20)
Lambda_IDCM = mp.sqrt(lam_max)*M0*N_gen/L(5)   # MeV = 45.28487
M_Z = mp.mpf('91.1876')
m_t = mp.mpf('172.57'); m_b = mp.mpf('4.18'); m_c = mp.mpf('1.27')
a_PDG = mp.mpf('0.1180')

def beta(Nf):
    return (11-2*mp.mpf(Nf)/3, 102-38*mp.mpf(Nf)/3,
            2857/2 - 5033*mp.mpf(Nf)/18 + 325*mp.mpf(Nf)**2/54)

def rk4_step(f, a, h):
    k1 = f(a); k2 = f(a+h*k1/2); k3 = f(a+h*k2/2); k4 = f(a+h*k3)
    return a + h*(k1+2*k2+2*k3+k4)/6

def run_down(a0, mu_hi, mu_lo, Nf, order, steps=400000):
    b0,b1,b2 = beta(Nf)
    lnh, lnl = mp.log(mu_hi), mp.log(mu_lo)
    h = (lnl-lnh)/steps
    a = a0
    def f(x):
        r = -(b0/(2*mp.pi))*x*x
        if order >= 2: r -= b1/(8*mp.pi*mp.pi)*x**3
        if order >= 3: r -= b2/(32*mp.pi**3)*x**4
        return r
    for _ in range(steps):
        a = rk4_step(f, a, h)
    return a

def run_up(a0, mu_lo, mu_hi, Nf, order, steps=400000):
    """same ODE integrated upward"""
    b0,b1,b2 = beta(Nf)
    lnh, lnl = mp.log(mu_hi), mp.log(mu_lo)
    h = (lnl-lnh)/steps
    a = a0
    def f(x):
        r = -(b0/(2*mp.pi))*x*x
        if order >= 2: r -= b1/(8*mp.pi*mp.pi)*x**3
        if order >= 3: r -= b2/(32*mp.pi**3)*x**4
        return r
    for _ in range(steps):
        a = rk4_step(f, a, h)
    return a

# ---------------- chain 1-loop (reproduce v13c3 [C]) ----------------
a6_MZ_1 = 1/((7/(2*mp.pi))*mp.log(M_Z/(Lambda_IDCM/1000)))
a6_mt_1 = run_up(a6_MZ_1, M_Z, m_t, 6, order=1)
a5_mt_1 = a6_mt_1   # 1-loop matching: continuous
a5_MZ_1 = run_down(a5_mt_1, m_t, M_Z, 5, order=1)
a5_2_1  = run_down(a5_MZ_1, M_Z, 2.0, 5, order=1) if False else None
# full downward from m_t to 2 GeV / m_tau / 5 GeV through b,c
def chain_down(a5_at_mt, target, order):
    if target >= m_b:
        return run_down(a5_at_mt, m_t, target, 5, order)
    a_b = run_down(a5_at_mt, m_t, m_b, 5, order)
    if target >= m_c:
        return run_down(a_b, m_b, target, 4, order)
    a_c = run_down(a_b, m_b, m_c, 4, order)
    return run_down(a_c, m_c, target, 3, order)

print("1) IDCM structural boundary:")
print("   Lambda_IDCM =", mp.nstr(Lambda_IDCM, 10), "MeV")
print("   alpha6(M_Z) 1-loop =", mp.nstr(a6_MZ_1, 9), " (PDG alpha_s(MZ)=0.1180, dev",
      mp.nstr((a6_MZ_1-a_PDG)/a_PDG*100, 5), "%)")
print("   alpha6(m_t) 1-loop =", mp.nstr(a6_mt_1, 9))

# ---------------- chain 1-loop down to world scales ----------------
print("\n2) 1-loop chain (Nf5 from m_t down; reproduce v13c3 +0.79% at MZ):")
a5_MZ_1 = run_down(a5_mt_1, m_t, M_Z, 5, 1)
print("   alpha5(M_Z) =", mp.nstr(a5_MZ_1, 8), " dev vs PDG:",
      mp.nstr((a5_MZ_1-a_PDG)/a_PDG*100, 5), "% (v13c3 [C] reported +0.79%)")
for name, mu in (("m_tau", mp.mpf('1.777')), ("2 GeV", mp.mpf('2.0')), ("5 GeV", mp.mpf('5.0'))):
    a = chain_down(a5_mt_1, mu, 1)
    print(f"   alpha_s({name}) 1-loop = {mp.nstr(a,7)}")

# ---------------- chain 2-loop & 3-loop ----------------
print("\n3) 2-loop and 3-loop chains (correct beta normalization, v14b):")
for order in (2, 3):
    a6_MZ = a6_MZ_1  # boundary from 1-loop formula (IDCM scheme statement)
    # up to m_t in Nf=6 at that order
    a6_mt = run_up(a6_MZ, M_Z, m_t, 6, order)
    a5_mt = a6_mt
    a5_MZ = run_down(a5_mt, m_t, M_Z, 5, order)
    print(f"  order {order}: alpha5(M_Z) = {mp.nstr(a5_MZ,8)} dev =",
          mp.nstr((a5_MZ-a_PDG)/a_PDG*100,5), "%")
    for name, mu, w, sig in (("m_tau", mp.mpf('1.777'), mp.mpf('0.314'), mp.mpf('0.020')),
                              ("2 GeV", mp.mpf('2.0'), mp.mpf('0.303'), mp.mpf('0.007')),
                              ("5 GeV", mp.mpf('5.0'), mp.mpf('0.216'), mp.mpf('0.008'))):
        a = chain_down(a5_mt, mu, order)
        z = (a-w)/sig
        tag = "GREEN" if abs(z) <= 2 else ("YELLOW" if abs(z) <= 3 else "RED")
        print(f"     alpha_s({name}) = {mp.nstr(a,7)} vs {mp.nstr(w,6)}+/-{mp.nstr(sig,4)} z={mp.nstr(z,4)} [{tag}]")

# ---------------- 4. Lambda_MS(5) 2-loop implicit via standard lib ----------------
# from alpha5(MZ) 3-loop chain, compute the 2-loop implicit Lambda (Nf=5)
b0,b1,_ = beta(5)
for lbl, av in (("PDG 0.1180", a_PDG), ("IDCM 3lo chain", None)):
    if av is None:
        a6_mt = run_up(a6_MZ_1, M_Z, m_t, 6, 3)
        av = run_down(a6_mt, m_t, M_Z, 5, 3)
    rhs = 2*mp.pi/(b0*av) + b1/(2*b0*b0)*mp.log(b0*av/(2*mp.pi))
    Lam = M_Z*mp.exp(-rhs)
    print(f"   Lambda_MS(5) [2-loop implicit] from {lbl}: {mp.nstr(Lam*1000,6)} MeV",
          "(PDG 5-loop ~210-213 MeV; 2-loop Landau-consistent ~166)")