#!/usr/bin/env python3
# -*- coding: ascii -*-
"""O142 v13c2 - robust 2-loop + threshold via implicit MS-bar formulas.

1-loop Lambda_IDCM -> alpha_s(M_Z): does the closure survive proper 2-loop?
Implicit 2-loop MS-bar:  ln(mu/Lam) = 2pi/(b0*a) + (b1/(2*b0*b0)) * ln(b0*a/(2pi))
Threshold at m_t: match alpha_6(m_t) = alpha_5(m_t).
"""
import mpmath as mp
mp.mp.dps = 60

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
m_t = mp.mpf('172.57')
a_PDG = mp.mpf('0.1180')

def alpha_2loop(mu, Lam, b0, b1):
    """Solve a from implicit 2-loop relation (MS-bar) by bisection (fast)."""
    lhs = mp.log(mu/Lam)
    def f(a):
        return 2*mp.pi/(b0*a) + b1/(2*b0*b0)*mp.log(b0*a/(2*mp.pi)) - lhs
    a0 = 1/((b0/(2*mp.pi))*mp.log(mu/Lam))
    lo = a0*mp.mpf('0.3'); hi = a0*mp.mpf('1.5')
    flo = f(lo)
    while f(hi)*flo > 0:
        hi *= 2
    # NOTE: lo keeps sign (f(lo)>0 for monotonically decreasing f), bracket holds.
    for _ in range(200):
        mid = (lo+hi)/2
        if f(mid)*f(lo) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo+hi)/2

print("Lambda_IDCM =", mp.nstr(Lambda_IDCM, 10), "MeV")

print("\n=== [1] Nf=6 full running (b0=7,b1=26), no thresholds ===")
a2_6 = alpha_2loop(M_Z, Lambda_IDCM/1000, mp.mpf(7), mp.mpf(26))
print("alpha_s (2-loop,Nf=6) =", mp.nstr(a2_6, 12), " dev =", mp.nstr((a2_6-a_PDG)/a_PDG*100, 6), "%")

print("\n=== [2] Threshold chain: Lambda_IDCM(Nf=6) -> m_t -> Nf=5 -> M_Z (1-loop steps) ===")
# alpha_6(m_t) from Lambda_IDCM 1-loop:
a6_mt = 1/((7/(2*mp.pi))*mp.log(m_t/(Lambda_IDCM/1000)))
# 1-loop matching a5(m_t)=a6(m_t) -> Lambda_5:
b0_5 = mp.mpf(23)/3
Lam5 = m_t*mp.exp(-2*mp.pi/(b0_5*a6_mt))
a5_MZ = 1/((b0_5/(2*mp.pi))*mp.log(M_Z/Lam5))
print("alpha_6(m_t) =", mp.nstr(a6_mt, 10))
print("Lambda_5(matched) =", mp.nstr(Lam5*1000, 8), "MeV")
print("alpha_s(1lo) =", mp.nstr(a5_MZ, 12), " dev =", mp.nstr((a5_MZ-a_PDG)/a_PDG*100, 6), "%")

print("\n=== [3] Threshold chain with 2-loop steps ===")
b1_6 = 26
b1_5 = 102 - mp.mpf(38)*5/3
# alpha_6(m_t) 2-loop from Lambda_IDCM:
a6_mt2 = alpha_2loop(m_t, Lambda_IDCM/1000, mp.mpf(7), mp.mpf(26))
# match: a5 = a6 at m_t (leading matching), Lambda_5 from 2-loop implicit with b0_5,b1_5:
def lam_from_alpha(mu, a, b0, b1):
    return mu*mp.exp(-(2*mp.pi/(b0*a) + b1/(2*b0*b0)*mp.log(b0*a/(2*mp.pi))))
Lam5_2 = lam_from_alpha(m_t, a6_mt2, b0_5, b1_5)
a5_MZ2 = alpha_2loop(M_Z, Lam5_2, b0_5, b1_5)
print("alpha_6(m_t) 2lo =", mp.nstr(a6_mt2, 10))
print("Lambda_5 2lo     =", mp.nstr(Lam5_2*1000, 8), "MeV")
print("alpha_s(2lo)     =", mp.nstr(a5_MZ2, 12), " dev =", mp.nstr((a5_MZ2-a_PDG)/a_PDG*100, 6), "%")

print("\n=== [4] What Lambda would reproduce PDG at 1-loop Nf=6? ===")
Lam_need = M_Z*mp.exp(-2*mp.pi/(7*a_PDG))
print("Required Lambda(1lo,Nf6) =", mp.nstr(Lam_need*1000, 8), "MeV")
print("Lambda_IDCM              =", mp.nstr(Lambda_IDCM, 8), "MeV")
print("ratio                    =", mp.nstr(Lam_need/Lambda_IDCM, 10))
print("sqrt(lmax)*M0 =", mp.nstr(mp.sqrt(lam_max)*M0, 8), "; Lambda_IDCM/166.04 =", mp.nstr(Lambda_IDCM/(mp.sqrt(lam_max)*M0), 10))
print("If Lambda = strong*(x): x =", mp.nstr(mp.sqrt(lam_max)*M0*mp.mpf(11)/45.2848693374, 8))
# what multiplier makes Lambda -> PDG 1-loop?  -> (L5/N_gen)*(Lam_need/Lam_IDCM)
print("mult =", mp.nstr((Lam_need/1000)/(Lambda_IDCM/1000), 8), "= ?  (N_gen/L5 = 0.2727 ; 0.45/L0)")

print("\n=== [5] Structural sanity: full v13 form in operator language ===")
# Lambda_IDCM = sqrt(2*L6 - 1/g20) * M0 * (B*N_gen/N_d)
print("2*L6 =", mp.nstr(2*L(6), 10), "(=36=N_d-2B)")
print("sqrt(2L6-1/g20)*M0*(B*N_gen/N_d) =",
      mp.nstr(mp.sqrt(2*L(6)-1/gamma(20))*M0*(B*N_gen/N_d), 15), "MeV")
print("Lambda_IDCM =", mp.nstr(Lambda_IDCM, 15), "MeV")
print("=> operator-trace identity EXACT")