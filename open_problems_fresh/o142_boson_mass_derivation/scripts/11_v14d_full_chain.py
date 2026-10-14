#!/usr/bin/env python3
# -*- coding: ascii -*-
"""O142 v14d - FULL self-consistent chain (fixed): Lambda_IDCM -> decoupled QCD world.

The correct construction (v13c3 [C] anchored version, with CORRECT beta
normalization b1/8pi^2, b2/32pi^3 - the v14b finding):

  Lambda_IDCM = sqrt(lam_max)*M0*N_gen/L5  [structural, zero fit]
  1) anchor at mu0 = 1e4 GeV:  alpha(mu0) = 1/((b0_6/2pi) ln(mu0/Lambda_IDCM))
     (1-loop; 2/3-loop corrections are asymptotically negligible at 1e4 GeV)
  2) Nf=6 runs DOWN to m_t (top threshold), decouple: alpha5(m_t) = alpha6(m_t)
  3) Nf=5 down to M_Z and to m_b; Nf=4 to m_c; Nf=3 to 2 GeV / m_tau / 1 GeV
  4) compare with PDG at M_Z (expect ~+0.79% per v13c3 [C] 1-loop; with
     corrected higher-loop terms we expect BETTER convergence) and out-of-sample
     alpha_s(m_tau)=0.314+/-0.020, alpha_s(2 GeV)~0.303+/-0.007, alpha_s(5 GeV)
     ~0.216+/-0.008.  Pre-registered: GREEN <2sigma / YELLOW <3 / RED >3.

Also reports the 1-loop chain for direct comparison with v13c3's +0.79%.
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
Lambda_IDCM = mp.sqrt(lam_max)*M0*N_gen/L(5)   # MeV = 45.2849
M_Z = mp.mpf('91.1876')
m_t = mp.mpf('172.57'); m_b = mp.mpf('4.18'); m_c = mp.mpf('1.27')
mu0 = mp.mpf('1e4')
a_PDG = mp.mpf('0.1180')

def beta(Nf):
    return (11-2*mp.mpf(Nf)/3, 102-38*mp.mpf(Nf)/3,
            2857/2 - 5033*mp.mpf(Nf)/18 + 325*mp.mpf(Nf)**2/54)

def rk4_step(f, a, h):
    k1 = f(a); k2 = f(a+h*k1/2); k3 = f(a+h*k2/2); k4 = f(a+h*k3)
    return a + h*(k1+2*k2+2*k3+k4)/6

def run_down(a0, mu_hi, mu_lo, Nf, order, steps=20000):
    """a0 at mu_hi, integrate da/dlnmu = -b0 a^2/2pi - b1 a^3/8pi^2 - b2 a^4/32pi^3
    to mu_lo (always DOWNWARD; asserts mu_hi > mu_lo)."""
    assert mu_hi > mu_lo, (mu_hi, mu_lo)
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

print("1) Anchor & boundary (zero fit):")
print("   Lambda_IDCM =", mp.nstr(Lambda_IDCM, 10), "MeV")
print("   alpha(mu0=1e4) 1-loop anchor =", mp.nstr(1/((7/(2*mp.pi))*mp.log(mu0/(Lambda_IDCM/1000))), 9))

def full_chain(order, verbose=True):
    """run the whole decoupled chain at given loop order; return dict of alphas."""
    a6_mu0 = 1/((7/(2*mp.pi))*mp.log(mu0/(Lambda_IDCM/1000)))   # Nf=6 anchor
    a6_mt = run_down(a6_mu0, mu0, m_t, 6, order)
    # decouple top: alpha5(m_t) = alpha6(m_t)  (1-loop continuous matching)
    a5_mt = a6_mt
    a5_MZ = run_down(a5_mt, m_t, M_Z, 5, order)
    if verbose:
        print(f"\n order {order}: alpha6(m_t)={mp.nstr(a6_mt,8)} alpha5(M_Z)={mp.nstr(a5_MZ,8)}",
              " dev vs PDG:", mp.nstr((a5_MZ-a_PDG)/a_PDG*100, 5), "%")
    # out-of-sample targets
    res = {'M_Z': a5_MZ}
    a_b = run_down(a5_mt, m_t, m_b, 5, order)
    for name, mu, w, sig in (("m_tau", mp.mpf('1.777'), mp.mpf('0.314'), mp.mpf('0.020')),
                              ("2 GeV", mp.mpf('2.0'), mp.mpf('0.303'), mp.mpf('0.007')),
                              ("5 GeV", mp.mpf('5.0'), mp.mpf('0.216'), mp.mpf('0.008'))):
        if mu >= m_b:
            a = run_down(a5_mt, m_t, mu, 5, order)
        elif mu >= m_c:
            a = run_down(a_b, m_b, mu, 4, order)
        else:
            a_c = run_down(a_b, m_b, m_c, 4, order)
            a = run_down(a_c, m_c, mu, 3, order)
        res[name] = a
        if verbose:
            z = (a-w)/sig
            tag = "GREEN" if abs(z) <= 2 else ("YELLOW" if abs(z) <= 3 else "RED")
            print(f"    alpha_s({name}) = {mp.nstr(a,7)} vs {mp.nstr(w,6)}+/-{mp.nstr(sig,4)} z={mp.nstr(z,4)} [{tag}]")
    return res

full_chain(1)
full_chain(2)
full_chain(3)

# Lambda_MS(5) 2-loop implicit from the various alpha5(M_Z) values
print("\n2) Lambda_MS(5) [2-loop implicit] at M_Z (PDG 5-loop ~210-213 MeV):")
b0,b1,_ = beta(5)
for lbl, res in (("1-loop chain", full_chain(1, verbose=False)),
                  ("3-loop chain", full_chain(3, verbose=False))):
    av = res['M_Z']
    rhs = 2*mp.pi/(b0*av) + b1/(2*b0*b0)*mp.log(b0*av/(2*mp.pi))
    print(f"   from {lbl}: {mp.nstr(M_Z*mp.exp(-rhs)*1000,6)} MeV")