#!/usr/bin/env python3
# -*- coding: ascii -*-
"""O142 v15 - BLIND predictions from IDCM boundary (no external reference values).

Inputs: Lambda_IDCM = sqrt(lam_max)*M0*N_gen/L5 (structural); M_Z; m_t/m_b/m_c
(standard PDG running masses - fixed world inputs, not refit here).
Method: boundary alpha_s(M_Z) = 1/((7/2pi) ln(M_Z/Lambda)) then standard 3-loop
MS-bar RGE with flavor thresholds (v14b construction, correct beta b1/8pi^2,
b2/32pi^3).  Prints predictions; comparison done AFTER (docs/14 prereg).

Also computes mechanism candidates C1/C3/C4.
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
Lambda_IDCM = mp.sqrt(lam_max)*M0*N_gen/L(5)     # MeV
M_Z = mp.mpf('91.1876')
m_t, m_b, m_c = mp.mpf('172.57'), mp.mpf('4.18'), mp.mpf('1.27')

a_inv = (7/(2*mp.pi))*mp.log(M_Z/(Lambda_IDCM/1000))
a0 = 1/a_inv
print("1) IDCM boundary: Lambda_IDCM =", mp.nstr(Lambda_IDCM, 10), "MeV")
print("   alpha_s(M_Z) =", mp.nstr(a0, 9), "  (1/a =", mp.nstr(a_inv, 6), ")")

def beta(Nf):
    return (11-2*mp.mpf(Nf)/3, 102-38*mp.mpf(Nf)/3,
            2857/2 - 5033*mp.mpf(Nf)/18 + 325*mp.mpf(Nf)**2/54)

def run_down(a0, mu_hi, mu_lo, Nf, order, steps=200000):
    assert mu_hi > mu_lo
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
        k1=f(a); k2=f(a+h*k1/2); k3=f(a+h*k2/2); k4=f(a+h*k3)
        a += h*(k1+2*k2+2*k3+k4)/6
    return a

def alpha_at(mu, order=3):
    """threshold chain from M_Z down: Nf=5 to m_b, Nf=4 to m_c, Nf=3 below."""
    if mu >= m_b:
        return run_down(a0, M_Z, mu, 5, order)
    a_b = run_down(a0, M_Z, m_b, 5, order)
    if mu >= m_c:
        return run_down(a_b, m_b, mu, 4, order)
    a_c = run_down(a_b, m_b, m_c, 4, order)
    return run_down(a_c, m_c, mu, 3, order)

print("\n2) BLIND predictions (preregistered, docs/14):")
for name, mu in (("P1 alpha_s(1.5 GeV)", mp.mpf('1.5')),
                 ("P2 alpha_s(3 GeV)",   mp.mpf('3.0')),
                 ("P3 alpha_s(10 GeV)",  mp.mpf('10.0')),
                 ("P4 alpha_s(M_Z/2=45.6)", mp.mpf('45.6')),
                 ("P5 alpha_s(m_b=4.18)",   mp.mpf('4.18'))):
    print(f"   {name}: {mp.nstr(alpha_at(mu), 7)}")

# P6: IDCM boundary itself (= lattice-comparison target)
print("   P6 alpha_s(M_Z) lattice target: boundary =", mp.nstr(a0, 7))

# P7: sigma = SumGamma_odd * Lambda_IDCM^2
Sg_odd = mp.mpf(88)   # EXACT closed form: sum_{odd n<=87} 4sin^2(pi n/88) = 88 (=2N_d, O144)
print("\n3) sigma / slope (C1):")
print(f"   SumGamma_odd(1,3,..,87) = {mp.nstr(Sg_odd, 12)}")
sig = Sg_odd*(Lambda_IDCM/1000)**2
print("   P7 sigma = SumGamma_odd*Lambda^2 =", mp.nstr(sig, 8), "GeV^2",
      " sqrt(sigma) =", mp.nstr(mp.sqrt(sig)*1000, 6), "MeV")
print("   P8 alpha' = 1/(2*pi*sigma) =", mp.nstr(1/(2*mp.pi*sig), 7), "GeV^-2")

# P9: Lambda_MS(5) by-running (3-loop Nf=5 ONLY, no thresholds: convention match)
# find Lam such that running from Lam to M_Z with 3-loop Nf=5 gives alpha(MZ)
def run_up_lam(Lam, mu_hi, Nf, order, steps=200000):
    """start at a(Lam)->inf approx: use implicit 1-loop at mu_hi?? No:
    instead solve: find a(mu_hi) via 1-loop, then integrate 3-loop down to M_Z
    and require result == a0. Pure by-running definition of Lambda."""
    b0,b1,b2 = beta(Nf)
    # anchor at mu_hi=1e4 with 1-loop (asymptotic agreement)
    mu_hi = mp.mpf('1e4')
    a_hi = 1/((b0/(2*mp.pi))*mp.log(mu_hi/Lam))
    return a_hi

def lam_target(Nf, order, mu_hi=mp.mpf('1e4')):
    """Lambda by-running: such that 3-loop Nf=5 running from anchor -> a0 at M_Z.
    Reuse alpha_at-style chain but keep Nf fixed (no thresholds) = the MS-bar(5)
    Lambda in that convention."""
    b0,b1,b2 = beta(Nf)
    a_hi = 1/((b0/(2*mp.pi))*mp.log(mu_hi/Lam))
    return None  # placeholder below

print("\n4) P9 Lambda_MS(5) 3-loop by-running (bisection):")
def solve_lam():
    b0,b1,_ = beta(5)
    # take candidate Lam, 1-loop anchor at 1e4, 3-loop down to M_Z, compare with a0
    def chain(Lam):
        a = 1/((b0/(2*mp.pi))*mp.log(mp.mpf('1e4')/Lam))
        return run_down(a, mp.mpf('1e4'), M_Z, 5, 3)
    lo, hi = mp.mpf('0.001'), mp.mpf('1.0')
    for _ in range(200):
        mid = (lo+hi)/2
        if chain(mid) > a0: hi = mid
        else: lo = mid
    return (lo+hi)/2, chain((lo+hi)/2)
Lam5, chk = solve_lam()
print("   Lambda_MS(5) [3-loop, by-running] =", mp.nstr(Lam5*1000, 6), "MeV",
      " (check alpha(MZ) =", mp.nstr(chk, 8), ")")

# ---------- mechanism candidates ----------
print("\n5) Mechanism candidates:")
print("   C2: b0(Nf=6)=7: (11*N_c-2*N_f)/3 with N_c=B-1=3, N_f=2*N_gen=6 ->",
      mp.nstr((11*(B-1)-2*(2*N_gen))/3, 6), "= L4")
print("   C3: active chain modes at mu=Lambda: gamma_n <= Lambda/M0")
r = Lambda_IDCM/M0
n_max = 0
for n in range(1, 45):
    if gamma(n) <= r: n_max = n
print(f"   Lambda/M0 = {mp.nstr(r, 8)}; largest n with gamma_n <= r: {n_max}",
      "(gamma_19 =", mp.nstr(gamma(19), 6), ", gamma_20 =", mp.nstr(gamma(20), 6), ")")
print("   19 = 2*F7-L4 =", 2*F(7)-L(4), "?" if int(2*F(7)-L(4))==19 else "NO")
print("   C4: t=ln(M_Z/Lambda) =", mp.nstr(mp.log(M_Z/(Lambda_IDCM/1000)), 7),
      " 11*ln2 =", mp.nstr(11*mp.log(2), 6), " dev =",
      mp.nstr((mp.log(M_Z/(Lambda_IDCM/1000))-11*mp.log(2))/(11*mp.log(2))*100, 3), "%")