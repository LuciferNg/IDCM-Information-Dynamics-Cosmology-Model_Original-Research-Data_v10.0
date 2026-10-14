#!/usr/bin/env python3
# -*- coding: ascii -*-
"""O142 v13c3 - cross-check 2-loop alpha_s via downward ODE integration.

Run from high scale (mu0=1e4 GeV) where 1-loop and 2-loop agree, down to M_Z.
da/dlnmu = -b0/(2pi) a^2 - b1/(4pi^2) a^3
"""
import mpmath as mp
mp.mp.dps = 40

phi = (1+mp.sqrt(5))/2
psi_ = (1-mp.sqrt(5))/2
L = lambda n: phi**n + psi_**n
F = lambda n: (phi**n - psi_**n)/mp.sqrt(5)
gamma = lambda n: 4*mp.sin(mp.pi*n/88)**2

M0 = mp.mpf('27.900915')
N_d = mp.mpf(44); B = mp.mpf(4); N_gen = mp.mpf(3)
lam_max = 36 - 1/gamma(20)
Lambda_IDCM = mp.sqrt(lam_max)*M0*N_gen/L(5)   # MeV
M_Z = mp.mpf('91.1876')
a_PDG = mp.mpf('0.1180')

def integrate_alpha(Lam_GeV, mu_lo, mu_hi, b0, b1, steps=200000):
    """Integrate da/dlnmu downward from mu_hi (1-loop anchor) to mu_lo."""
    # anchor at mu_hi with 1-loop (both loops agree there for large mu)
    a = 1/((b0/(2*mp.pi))*mp.log(mu_hi/Lam_GeV))
    ln_hi = mp.log(mu_hi); ln_lo = mp.log(mu_lo)
    dln = (ln_lo - ln_hi)/steps
    for k in range(steps):
        da = -(b0*a*a/(2*mp.pi) + b1*a*a*a/(4*mp.pi*mp.pi))
        a = a + da*dln
    return a

b0_6 = mp.mpf(7); b1_6 = mp.mpf(26)

# [A] Nf=6 full 2-loop, anchored 1e4 GeV
a_2lo = integrate_alpha(Lambda_IDCM/1000, M_Z, mp.mpf('1e4'), b0_6, b1_6)
print("[A] 2-loop Nf=6 (ODE, anchor 1e4 GeV): alpha =", mp.nstr(a_2lo, 10),
      " dev =", mp.nstr((a_2lo-a_PDG)/a_PDG*100, 6), "%")
# anchor sensitivity
a_2lo_b = integrate_alpha(Lambda_IDCM/1000, M_Z, mp.mpf('1e3'), b0_6, b1_6)
print("    anchor 1e3 GeV:", mp.nstr(a_2lo_b, 10), " dev =", mp.nstr((a_2lo_b-a_PDG)/a_PDG*100, 6), "%")
a_2lo_c = integrate_alpha(Lambda_IDCM/1000, M_Z, mp.mpf('1e5'), b0_6, b1_6)
print("    anchor 1e5 GeV:", mp.nstr(a_2lo_c, 10), " dev =", mp.nstr((a_2lo_c-a_PDG)/a_PDG*100, 6), "%")

# [B] 1-loop for reference
a_1lo = 1/((b0_6/(2*mp.pi))*mp.log(M_Z/(Lambda_IDCM/1000)))
print("[B] 1-loop Nf=6:", mp.nstr(a_1lo, 10), " dev =", mp.nstr((a_1lo-a_PDG)/a_PDG*100, 6), "%")

# [C] threshold chain 2-loop: Nf=6 to m_t, Nf=5 to M_Z
m_t = mp.mpf('172.57')
b0_5 = mp.mpf(23)/3; b1_5 = 102 - mp.mpf(38)*5/3
a6_mt = integrate_alpha(Lambda_IDCM/1000, m_t, mp.mpf('1e4'), b0_6, b1_6)
# match a5(m_t)=a6(m_t): Lam5 from 2-loop implicit at m_t
def lam_for_alpha(mu, a, b0, b1):
    # 2-loop: ln(mu/Lam) = 2pi/(b0 a) + b1/(2 b0^2) ln(b0 a/2pi)
    rhs = 2*mp.pi/(b0*a) + b1/(2*b0*b0)*mp.log(b0*a/(2*mp.pi))
    return mu*mp.exp(-rhs)
Lam5 = lam_for_alpha(m_t, a6_mt, b0_5, b1_5)
print("[C] Lam5(2lo) =", mp.nstr(Lam5*1000, 8), "MeV")
# integrate Nf=5 from m_t down with anchor at m_t = a6_mt (continuous)
a5_MZ = integrate_alpha(Lam5, M_Z, m_t, b0_5, b1_5)
print("    2-loop chain alpha(MZ) =", mp.nstr(a5_MZ, 10), " dev =", mp.nstr((a5_MZ-a_PDG)/a_PDG*100, 6), "%")

# [D] what if Lambda_IDCM used as Nf=5 2-loop Lambda (mismatch check)
a_mis = integrate_alpha(Lambda_IDCM/1000, M_Z, mp.mpf('1e4'), b0_5, b1_5)
print("[D] Lambda_IDCM mis-as-Nf5 2lo:", mp.nstr(a_mis, 10), " dev =", mp.nstr((a_mis-a_PDG)/a_PDG*100, 6), "%")