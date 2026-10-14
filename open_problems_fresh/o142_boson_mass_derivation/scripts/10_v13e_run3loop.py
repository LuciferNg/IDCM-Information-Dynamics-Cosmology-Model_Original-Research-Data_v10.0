#!/usr/bin/env python3
# -*- coding: ascii -*-
"""O142 v13e - 3-loop running with T-hat beta coefficients.

Now that b0=L4=7, b1=2F7=26, b2=-F5*F7/2=-65/2 are ALL T-hat invariants at
Nf=6, test whether 3-loop running from Lambda_IDCM converges toward PDG
alpha_s(M_Z)=0.1180.

Beta (MS-bar, a=alpha_s/pi normalization):
  da/dt = -b0 a^2 / (2pi) - b1 a^3 / (4 pi^2) - b2 a^4 / (16 pi^3)  [a=alpha_s]
Rederive with a = alpha_s:
  1/a: standard:  d(1/a)/dt = b0/(2pi) + b1/(4 pi^2) a + b2/(16 pi^3) a^2
Where t = ln mu.

Implicit 3-loop solution (MS-bar, matching 1-loop Lambda):
  ln(mu/Lam) = 2pi/(b0 a) + (b1/(2 b0^2)) ln(b0 a/2pi)
               + [ (b2/(4 b0^3)) ln(b0 a/2pi) - (b1^2/(4 b0^4)) ln(...) ] ... 
We instead integrate the ODE directly from a high anchor (mu0=1e4 GeV)
using 3-loop beta, with anchor alpha(1e4) from the *2-loop* implicit to
remove scheme ambiguity, then compare with 1-loop and 2-loop runs.
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

# beta coefficients (T-hat identities at Nf=6)
b0 = mp.mpf(7)          # L4
b1 = mp.mpf(26)         # 2*F7
b2 = -mp.mpf(65)/2      # -F5*F7/2
b3 = mp.mpf('-850.77831251111')  # 4-loop MS-bar

def beta_da(a, order=3):
    # da/dlnmu = -b0 a^2/(2pi) - b1 a^3/(4 pi^2) - b2 a^4/(16 pi^3) [- b3 a^5/(64 pi^4) ...]
    r = -(b0*a*a/(2*mp.pi)) - (b1*a**3/(4*mp.pi**2))
    if order >= 3:
        r -= b2*a**4/(16*mp.pi**3)
    if order >= 4:
        r -= b3*a**5/(64*mp.pi**4)
    return r

def alpha_1loop(mu, Lam):
    return 1/((b0/(2*mp.pi))*mp.log(mu/Lam))

def alpha_2loop_implicit(mu, Lam):
    lhs = mp.log(mu/Lam)
    def f(a):
        return 2*mp.pi/(b0*a) + b1/(2*b0*b0)*mp.log(b0*a/(2*mp.pi)) - lhs
    a0 = alpha_1loop(mu, Lam)
    lo = a0*mp.mpf('0.3'); hi = a0*mp.mpf('1.5')
    flo = f(lo)
    while f(hi)*flo > 0:
        hi *= 2
    for _ in range(300):
        mid = (lo+hi)/2
        if f(mid)*f(lo) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo+hi)/2

def alpha_3loop_implicit(mu, Lam):
    """Standard 3-loop MS-bar implicit relation (Vladimirov / Chetyrkin):
    ln(mu/Lam) = 2pi/(b0 a) + (b1/(2 b0^2)) ln(b0 a/2pi)
                 + b2/(4 b0^2) [ln(b0 a/2pi)] - (b1^2 b2)/(2 b0^5) ... 
    approximate: use ln(mu/Lam) = L0 + (b1/b0^2) ln L0 + ...  iterate:
    L0 = 2pi/(b0 a) + (b1/(2b0^2)) ln( 2pi/(b0 a) * something )
    """
    lhs = mp.log(mu/Lam)
    def f(a):
        x = b0*a/(2*mp.pi)
        # a = alpha_s; MS-bar 3-loop: L = 2pi/(b0 a) + (b1/(2 b0^2)) ln x
        #        + (b2/(4 b0^3)) x^0 * (ln^2 x ... )  -- use standard formula:
        # L = 2pi/(b0 a) + (b1/(2 b0^2)) ln x + (b2/(16 b0^3)) x^2*... 
        # We use the exact ODE integral instead below; this implicit is for anchor.
        return 2*mp.pi/(b0*a) + b1/(2*b0*b0)*mp.log(x) \
               + (b2/(4*b0**3))*(mp.log(x))**2 / 1
    try:
        a0 = alpha_2loop_implicit(mu, Lam)
        lo = a0*mp.mpf('0.5'); hi = a0*mp.mpf('1.5')
        fl = f(lo)
        if f(hi)*fl > 0:
            hi *= 2
        for _ in range(300):
            mid = (lo+hi)/2
            if f(mid)*f(lo) <= 0:
                hi = mid
            else:
                lo = mid
        return (lo+hi)/2
    except Exception as e:
        return None

def integrate_alpha(Lam_GeV, mu_lo, mu_hi, order, steps=400000):
    a = alpha_2loop_implicit(mu_hi, Lam_GeV)  # anchor 2-loop implicit at high mu
    ln_hi = mp.log(mu_hi); ln_lo = mp.log(mu_lo)
    dln = (ln_lo - ln_hi)/steps
    for k in range(steps):
        a = a + beta_da(a, order)*dln
    return a

Lam_G = Lambda_IDCM/1000

print("Lambda_IDCM =", mp.nstr(Lambda_IDCM, 10), "MeV")
print("PDG alpha_s =", mp.nstr(a_PDG, 8), "+/-0.0009")

# 1-loop
a1 = alpha_1loop(M_Z, Lam_G)
print("\n1-loop  :", mp.nstr(a1, 10), " dev =", mp.nstr((a1-a_PDG)/a_PDG*100, 6), "%")
# 2-loop implicit at M_Z
a2 = alpha_2loop_implicit(M_Z, Lam_G)
print("2-loop  :", mp.nstr(a2, 10), " dev =", mp.nstr((a2-a_PDG)/a_PDG*100, 6), "%")
# 3-loop via ODE (order=3)
a3 = integrate_alpha(Lam_G, M_Z, mp.mpf('1e4'), 3)
print("3-loop  :", mp.nstr(a3, 10), " dev =", mp.nstr((a3-a_PDG)/a_PDG*100, 6), "%")
# 4-loop via ODE (order=4)
a4 = integrate_alpha(Lam_G, M_Z, mp.mpf('1e4'), 4)
print("4-loop  :", mp.nstr(a4, 10), " dev =", mp.nstr((a4-a_PDG)/a_PDG*100, 6), "%")

# anchor sensitivity for 3-loop
for mu_hi in [mp.mpf('1e3'), mp.mpf('1e4'), mp.mpf('1e5')]:
    av = integrate_alpha(Lam_G, M_Z, mu_hi, 3)
    print(f"3-loop anchor {mp.nstr(mu_hi,4)}:", mp.nstr(av, 10),
          " dev =", mp.nstr((av-a_PDG)/a_PDG*100, 6), "%")