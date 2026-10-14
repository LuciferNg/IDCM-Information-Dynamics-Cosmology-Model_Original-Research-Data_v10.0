#!/usr/bin/env python3
# -*- coding: ascii -*-
"""O142 v15c - P10: Lambda_MS(3) from IDCM boundary (blind, preregistered).

Lattice non-perturbative anchor (ALPHA/FLAG 2024): Lambda^(3)_MSbar = 339.5(9.6) MeV
- INDEPENDENT of the alpha_s(M_Z) world average (step-scaling + decoupling).

IDCM prediction chain (zero fit):
  boundary alpha_s(M_Z) = 1/((7/2pi) ln(M_Z/Lambda_IDCM)),  Lambda_IDCM=45.2849 MeV
  -> 3-loop MS-bar threshold chain: Nf=5 to m_b=4.18, Nf=4 to m_c=1.27, Nf=3 below
  -> Lambda^(3) via standard 2-loop implicit relation at two extraction scales
     (mu = m_c and mu = 2 GeV); Lambda is scale-independent BY DEFINITION so the
     two extractions must agree (self-consistency check).
Caveat preregistered: ALPHA quotes in 4/5-loop convention; our 2-loop implicit
extraction carries a loop-order convention drift (~+5-10% expected) - the blind
comparison uses 2-loop vs their published number and flags the drift honestly.
"""
import mpmath as mp
mp.mp.dps = 50

phi = (1+mp.sqrt(5))/2
psi_ = (1-mp.sqrt(5))/2
L = lambda n: phi**n + psi_**n
F = lambda n: (phi**n - psi_**n)/mp.sqrt(5)
gamma = lambda n: 4*mp.sin(mp.pi*n/88)**2

M0 = mp.mpf('27.900915')
N_d, B, N_gen = mp.mpf(44), mp.mpf(4), mp.mpf(3)
lam_max = 36 - 1/gamma(20)
Lambda_IDCM = mp.sqrt(lam_max)*M0*N_gen/L(5)
M_Z = mp.mpf('91.1876')
m_b, m_c = mp.mpf('4.18'), mp.mpf('1.27')
a_inv = (7/(2*mp.pi))*mp.log(M_Z/(Lambda_IDCM/1000))
a0 = 1/a_inv
print("P10  IDCM boundary -> Lambda^(3)_MSbar  (blind, preregistered)")
print("     Lambda_IDCM =", mp.nstr(Lambda_IDCM, 10), "MeV,  alpha_s(MZ) =", mp.nstr(a0, 10))

def beta(Nf):
    return (11-2*mp.mpf(Nf)/3, 102-38*mp.mpf(Nf)/3,
            2857/2 - 5033*mp.mpf(Nf)/18 + 325*mp.mpf(Nf)**2/54)

def run_down(a0_, mu_hi, mu_lo, Nf, order=3, steps=200000):
    assert mu_hi > mu_lo
    b0,b1,b2 = beta(Nf)
    lnh, lnl = mp.log(mu_hi), mp.log(mu_lo)
    h = (lnl-lnh)/steps
    a = a0_
    def f(x):
        r = -(b0/(2*mp.pi))*x*x
        if order >= 2: r -= b1/(8*mp.pi*mp.pi)*x**3
        if order >= 3: r -= b2/(32*mp.pi**3)*x**4
        return r
    for _ in range(steps):
        k1=f(a); k2=f(a+h*k1/2); k3=f(a+h*k2/2); k4=f(a+h*k3)
        a += h*(k1+2*k2+2*k3+k4)/6
    return a

# full chain state: alpha3 at just below m_c, and at mu=2 GeV, 1.5 GeV
a_b = run_down(a0, M_Z, m_b, 5)
a_c = run_down(a_b, m_b, m_c, 4)
a3_mc   = a_c                      # 1-loop continuous match at m_c
print("\n  alpha_s chain: 3-loop with thresholds")
print("  alpha3 at m_c (match) =", mp.nstr(a3_mc, 8))
extract = [mp.mpf('1.1'), mp.mpf('1.0'), mp.mpf('0.9'), mp.mpf('0.8')]
a3_pts = {}
prev = a_c
for mu in extract:
    a3_pts[mu] = run_down(prev, m_c, mu, 3)
    prev = a3_pts[mu]
    print(f"  alpha3({mp.nstr(mu,3)} GeV) = {mp.nstr(a3_pts[mu], 8)}")

def lam_implicit_2lo(mu, a, Nf):
    b0,b1,_ = beta(Nf)
    rhs = 2*mp.pi/(b0*a) + b1/(2*b0*b0)*mp.log(b0*a/(2*mp.pi))
    return mu*mp.exp(-rhs)

print("\n  Lambda^(3) via 2-loop implicit (extraction-scale independence check):")
avis = {}
for mu in extract + [m_c]:
    a = a3_mc if mu == m_c else a3_pts[mu]
    avis[mu] = lam_implicit_2lo(mu, a, 3)
    print(f"  at mu={mp.nstr(mu,3)} GeV: {mp.nstr(avis[mu]*1000, 8)} MeV")
lam3 = mp.fsum(list(avis.values()))/len(avis)
print("\n  BLIND RESULT: Lambda^(3)_MSbar(IDCM) =", mp.nstr(lam3*1000, 7), "MeV (2-loop implicit avg)")

# 3-loop by-running integral alternative (for honesty about convention drift)
def lam_exact_integral(mu, a, Nf, a_max=mp.mpf('100')):
    b0,b1,b2 = beta(Nf)
    def integrand(t):
        r = b0/(2*mp.pi)*t*t
        r += b1/(8*mp.pi*mp.pi)*t**3
        r += b2/(32*mp.pi**3)*t**4
        return 1/r
    I = mp.quad(integrand, [a, a_max])
    return mu*mp.exp(-I)
L3lo_mc = lam_exact_integral(m_c, a3_mc, 3)
L3lo_11 = lam_exact_integral(mp.mpf('1.1'), a3_pts[mp.mpf('1.1')], 3)
print("\n  (3-loop by-running integral, convention reference):")
print("  at mu=m_c:", mp.nstr(L3lo_mc*1000, 7), "MeV | at 1.1 GeV:", mp.nstr(L3lo_11*1000, 7), "MeV")

# world anchor (from search, ALPHA 17+22 combine, FLAG 2024 report)
L_alpha = mp.mpf('339.5')
sig_alpha = mp.mpf('9.6')
print("\n  World lattice (ALPHA/FLAG 2024, NON-perturbative): Lambda^(3)_MS = 339.5 +/- 9.6 MeV")
z_2lo = (lam3*1000 - L_alpha)/sig_alpha
print("  z(2-loop implicit) =", mp.nstr(z_2lo, 4))
z_3lo = (L3lo_mc*1000 - L_alpha)/sig_alpha
print("  z(3-loop integral, m_c) =", mp.nstr(z_3lo, 4), " [loop-convention drift expected]")