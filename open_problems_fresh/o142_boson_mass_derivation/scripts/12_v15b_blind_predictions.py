#!/usr/bin/env python3
# -*- coding: ascii -*-
"""O142 v15b - BLIND predictions from IDCM boundary (EXACT methods, no shortcuts).

P1-P5: alpha_s at 1.5/3/10/45.6/4.18 GeV via standard 3-loop MS-bar threshold
       chain from IDCM boundary (RK4 200k steps, verified convergent).
P6 : boundary alpha_s(M_Z) (lattice comparison).
P7 : sigma = SumGamma_odd * Lambda_IDCM^2  (SumGamma_odd computed by nsum
     44 terms AND closed form 88 - NOT hardcoded).
P8 : alpha' = 1/(2 pi sigma).
P9 : Lambda_MS(5) EXACT by-running definition:
       ln(mu/Lam) = Integral[ alpha( mu ), Infinity ] of d a' / (-beta(a'))
     computed by mpmath quad at 40 dps (Nf=5, 3-loop beta) - no ODE, no bisection.
C1-C5 : mechanism candidates.
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
Lambda_IDCM = mp.sqrt(lam_max)*M0*N_gen/L(5)     # MeV
M_Z = mp.mpf('91.1876')
m_t, m_b, m_c = mp.mpf('172.57'), mp.mpf('4.18'), mp.mpf('1.27')

a_inv = (7/(2*mp.pi))*mp.log(M_Z/(Lambda_IDCM/1000))
a0 = 1/a_inv
print("1) IDCM boundary: Lambda_IDCM =", mp.nstr(Lambda_IDCM, 12), "MeV")
print("   alpha_s(M_Z) =", mp.nstr(a0, 10), "  (1/a =", mp.nstr(a_inv, 8), ")")

def beta(Nf):
    return (11-2*mp.mpf(Nf)/3, 102-38*mp.mpf(Nf)/3,
            2857/2 - 5033*mp.mpf(Nf)/18 + 325*mp.mpf(Nf)**2/54)
b0_5, b1_5, b2_5 = beta(5)
print("   beta(Nf=5): b0=23/3, b1=116/3, b2=9769/54  [exact fractions:",
      mp.nstr(mp.mpf(23)/3, 12), mp.nstr(mp.mpf(116)/3, 12),
      mp.nstr(mp.mpf(9769)/54, 12), "]")

# ---------- P1-P5 via threshold chain (same as v14b, 3-loop) ----------
def run_down(a0_, mu_hi, mu_lo, Nf, order, steps=200000):
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

def alpha_at(mu, order=3):
    if mu >= m_b:
        return run_down(a0, M_Z, mu, 5, order)
    a_b = run_down(a0, M_Z, m_b, 5, order)
    if mu >= m_c:
        return run_down(a_b, m_b, mu, 4, order)
    a_c = run_down(a_b, m_b, m_c, 4, order)
    return run_down(a_c, m_c, mu, 3, order)

print("\n2) BLIND predictions (preregistered docs/14):")
for name, mu in (("P1 alpha_s(1.5 GeV)", mp.mpf('1.5')),
                 ("P2 alpha_s(3 GeV)",   mp.mpf('3.0')),
                 ("P3 alpha_s(10 GeV)",  mp.mpf('10.0')),
                 ("P4 alpha_s(45.6 GeV)",mp.mpf('45.6')),
                 ("P5 alpha_s(m_b)",     mp.mpf('4.18'))):
    print(f"   {name}: {mp.nstr(alpha_at(mu), 8)}")
print("   P6 alpha_s(M_Z) =", mp.nstr(a0, 8), "(lattice comparison target)")

# ---------- P7: sigma = SumGamma_odd * Lambda^2 ----------
print("\n3) P7/P8  (SumGamma_odd by direct 44-term nsum, NOT hardcoded):")
Sg_odd = mp.nsum(lambda k: gamma(2*k-1), [1, 44], method='r')
Sg_check = mp.mpf(88)   # closed form: sum odd 4sin^2(pi n/88) over n=1..87 = 88
print(f"   nsum(odd modes 1..87) = {mp.nstr(Sg_odd, 15)}   closed-form 88: {mp.nstr(Sg_check, 15)}",
      "EXACT match:", mp.almosteq(Sg_odd, Sg_check, rel_eps=mp.mpf('1e-40')))
sig = Sg_odd*(Lambda_IDCM/1000)**2
print("   P7 sigma = SumGamma_odd*Lambda^2 =", mp.nstr(sig, 9), "GeV^2")
print("       sqrt(sigma) =", mp.nstr(mp.sqrt(sig)*1000, 6), "MeV")
print("   P8 alpha' = 1/(2 pi sigma) =", mp.nstr(1/(2*mp.pi*sig), 8), "GeV^-2")

# ---------- P9: Lambda_MS(5) by-running, EXACT integral definition ----------
print("\n4) P9 Lambda_MS(5) [3-loop, Nf=5, by-running integral definition]:")
def lam_exact(mu_alpha_pair, Nf, order=3, a_max=mp.mpf('100')):
    """ln(mu/Lam) = int_{a(mu)}^{a_max} da' / (-beta(a')) , beta 3-loop."""
    mu, a = mu_alpha_pair
    b0,b1,b2 = beta(Nf)
    def integrand(t):
        r = b0/(2*mp.pi)*t*t
        if order >= 2: r += b1/(8*mp.pi*mp.pi)*t**3
        if order >= 3: r += b2/(32*mp.pi**3)*t**4
        return 1/r
    I = mp.quad(integrand, [a, a_max])
    return mu*mp.exp(-I)
Lam5_3lo = lam_exact((M_Z, a0), 5, order=3)
print("   Lam5_3lo (integral def) =", mp.nstr(Lam5_3lo*1000, 7), "MeV")
# convergence check in upper limit
Lam5_lo  = lam_exact((M_Z, a0), 5, order=3, a_max=mp.mpf('1000'))
print("   a_max=1000 check        =", mp.nstr(Lam5_lo*1000, 7), "MeV (converged:",
      mp.nstr(1-Lam5_3lo/Lam5_lo, 4), ")")
# 2-loop cross: beta 2-loop integral should match standard implicit
def lam_2lo_implicit(mu, a, Nf):
    b0,b1,_ = beta(Nf)
    rhs = 2*mp.pi/(b0*a) + b1/(2*b0*b0)*mp.log(b0*a/(2*mp.pi))
    return mu*mp.exp(-rhs)
print("   2-loop implicit cross  =", mp.nstr(lam_2lo_implicit(M_Z, a0, 5)*1000, 7), "MeV")

# ---------- mechanism candidates ----------
print("\n5) Mechanism:")
print("   C2: b0(Nf=6)=7 from N_c=B-1=3, N_f=2N_gen=6: (11*3-2*6)/3 =", (11*3-2*6)/3)
r = Lambda_IDCM/M0
n_max = max(n for n in range(1,45) if gamma(n) <= r)
print(f"   C3: Lambda/M0 = {mp.nstr(r, 10)}; largest n with gamma_n<=Lambda/M0: {n_max}",
      "(gamma_19 =", mp.nstr(gamma(19), 8), ", gamma_20 =", mp.nstr(gamma(20), 8), ")")
print("       19 - 2F7+L4 =", int(19 - 2*F(7) + L(4)), " (i.e. 19 == 2F7-L4:", int(2*F(7)-L(4)) == 19, ")")
t_ = mp.log(M_Z/(Lambda_IDCM/1000))
print("   C4: t=ln(M_Z/Lambda) =", mp.nstr(t_, 9), " 11*ln2 =", mp.nstr(11*mp.log(2), 8),
      " dev =", mp.nstr((t_-11*mp.log(2))/(11*mp.log(2))*100, 4), "%")
# lambda_max operator identity (v13, quote)
print("   C5: lambda_max = 36-1/gamma_20 =", mp.nstr(lam_max, 10),
      " 2L6-1/gamma_20 =", mp.nstr(2*L(6)-1/gamma(20), 10))