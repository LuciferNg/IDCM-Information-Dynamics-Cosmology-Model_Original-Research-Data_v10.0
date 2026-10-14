#!/usr/bin/env python3
# -*- coding: ascii -*-
"""O142 P10 - Lambda^(3)_MSbar quick fair-comparison (3-loop by-running integral).

ALPHA/FLAG 2024 world: Lambda^(3) = 339.5(9.6) MeV  (4/5-loop matching convention).
Our alpha_s chain: IDCM boundary -> thresholds -> alpha3 at m_c (weak window).
P10 judgement premise (docs/15): direct 2-loop implicit vs ALPHA 4/5-loop is
INVALID (convention drift 2lo->3lo alone ~+74% at 5f). Fair compare = SAME loop
order as the world figure carries. We have 3-loop beta in house, so we quote the
3-loop by-running integral Lambda and the 2-loop implicit Lambda; the honest
verdict is the 3-loop one (partial 4-loop would need b3 from O124 external).
"""
import mpmath as mp
mp.mp.dps = 40
phi = (1+mp.sqrt(5))/2
psi_ = (1-mp.sqrt(5))/2
L = lambda n: phi**n + psi_**n
gamma = lambda n: 4*mp.sin(mp.pi*n/88)**2
M0 = mp.mpf('27.900915')
lam_max = 36 - 1/gamma(20)
Lambda_IDCM = mp.sqrt(lam_max)*M0*3/L(5)
M_Z = mp.mpf('91.1876')
a0 = 1/((7/(2*mp.pi))*mp.log(M_Z/(Lambda_IDCM/1000)))

def beta(Nf):
    return (11-2*mp.mpf(Nf)/3, 102-38*mp.mpf(Nf)/3,
            mp.mpf(2857)/2 - 5033*mp.mpf(Nf)/18 + 325*mp.mpf(Nf)**2/54)

# alpha3 at m_c from the v15c partial output (chain already ran; reuse the number)
a3_mc = mp.mpf('0.38258859')

def lam3_byrunning(a, Nf=3, amax=mp.mpf('1000')):
    b0,b1,b2 = beta(Nf)
    def integrand(t):
        return 1/(b0/(2*mp.pi)*t*t + b1/(8*mp.pi*mp.pi)*t**3 + b2/(32*mp.pi**3)*t**4)
    I = mp.quad(integrand, [a, amax])
    return mp.mpf('1.27')*mp.exp(-I)

def lam3_implicit2lo(a, Nf=3, mu=mp.mpf('1.27')):
    b0,b1,_ = beta(Nf)
    rhs = 2*mp.pi/(b0*a) + b1/(2*b0*b0)*mp.log(b0*a/(2*mp.pi))
    return mu*mp.exp(-rhs)

L3_run = lam3_byrunning(a3_mc)
L3_imp = lam3_implicit2lo(a3_mc)
print("IDCM chain input:  alpha3(m_c=1.27) =", mp.nstr(a3_mc, 8))
print("  Lambda^(3) 3-loop by-running integral =", mp.nstr(L3_run*1000, 7), "MeV")
print("  Lambda^(3) 2-loop implicit           =", mp.nstr(L3_imp*1000, 7), "MeV")
print("  World ALPHA/FLAG2024 (4/5-loop)      = 339.5 +/- 9.6 MeV")
z_run = (L3_run*1000 - 339.5)/9.6
z_imp = (L3_imp*1000 - 339.5)/9.6
print("  z(3-loop run) =", mp.nstr(z_run, 4), " | z(2-loop impl) =", mp.nstr(z_imp, 4))
print("  NOTE: ALPHA carries 4/5-loop matching; our 3-loop by-running is the closest")
print("  in-house order. Remaining convention gap ~ +1 loop order (expect +15-30% scale).")