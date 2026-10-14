#!/usr/bin/env python3
# -*- coding: ascii -*-
"""O142 v14b - Full-order MS-bar closure from IDCM structural boundary (FIXED beta).

Convention fix (2026-10-13): beta in terms of alpha_s with group-theory
coefficients b0=11-2Nf/3, b1=102-38Nf/3, b2=2857/2-5033Nf/18+325Nf^2/54:

    d alpha_s / d ln mu = -b0 a^2/(2pi) - b1 a^3/(8pi^2) - b2 a^4/(32pi^3)

derived from dg/dlnmu = -b0 g^3/16pi^2 - b1 g^5/(16pi^2)^2 - b2 g^7/(16pi^2)^3,
g^2 = 4pi*alpha_s. (v13c2/c3/e used b1/4pi^2, b2/16pi^3 -> 2-loop and 3-loop
terms DOUBLED; corrected here. This changes the stability-test conclusions.)

Test: from IDCM structural boundary alpha_s(M_Z) = 1/8.47562 (zero fit),
run STANDARD SM MS-bar RGE with thresholds (m_b=4.18, m_c=1.27) down and
compare OUT-OF-SAMPLE alpha_s(m_tau)=0.314+/-0.020 (tau decays, PDG 2024),
alpha_s(2 GeV)~0.303+/-0.007, alpha_s(5 GeV)~0.216+/-0.008, Lambda_MS(5).

Pre-registered verdict:
  GREEN  : all out-of-sample within 2 sigma
  YELLOW : all within 3 sigma (systematic offset tolerated)
  RED    : any > 3 sigma -> Nf-constant scheme falsified at low scale

Also NOTE: at mu=M_Z the ACTIVE flavor count is 5 (top decoupled). The IDCM
value alpha_s^-1(MZ) was derived with b0=7 (Nf=6 formula) but alpha_s is
scheme- and flavor-definition-dependent at this order; we treat the IDCM
number as the boundary VALUE alpha(MZ) and run the physical 5-flavor chain.
"""
import mpmath as mp
mp.mp.dps = 30

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
a_PDG = mp.mpf('0.1179'); sig_PDG = mp.mpf('0.0009')

# ---------- 1. IDCM structural boundary ----------
b0_6 = mp.mpf(7)
a_inv_IDCM = (b0_6/(2*mp.pi))*mp.log(M_Z/(Lambda_IDCM/1000))
a_IDCM = 1/a_inv_IDCM
print("1) IDCM boundary (zero fit):")
print("   Lambda_IDCM =", mp.nstr(Lambda_IDCM, 10), "MeV")
print("   alpha_s(MZ) =", mp.nstr(a_IDCM, 9), " PDG =", mp.nstr(a_PDG, 6),
      "+/-", mp.nstr(sig_PDG, 5), " -> dev", mp.nstr((a_IDCM-a_PDG)/sig_PDG, 5), "sigma")

# ---------- 2. beta coefficients (correct convention) ----------
def beta_coeff(Nf):
    b0 = mp.mpf(11) - mp.mpf(2)*Nf/3
    b1 = mp.mpf(102) - mp.mpf(38)*Nf/3
    b2 = mp.mpf(2857)/2 - mp.mpf(5033)*Nf/18 + mp.mpf(325)*Nf*Nf/54
    return b0, b1, b2
for Nf in (6,5,4,3):
    b0,b1,b2 = beta_coeff(Nf)
    print(f"   beta(Nf={Nf}): b0={mp.nstr(b0,9)} b1={mp.nstr(b1,9)} b2={mp.nstr(b2,9)}")

# ---------- 3. RK4 RGE down (corrected denominators) ----------
def rge_down(a_start, mu_hi, mu_lo, Nf, steps=200000, order=3):
    b0,b1,b2 = beta_coeff(Nf)
    lnh, lnl = mp.log(mu_hi), mp.log(mu_lo)
    h = (lnl - lnh)/steps
    a = a_start
    def f(x, o=order):
        r = -(b0/(2*mp.pi))*x*x - (b1/(8*mp.pi*mp.pi))*x*x*x
        if o >= 3:
            r -= (b2/(32*mp.pi**3))*x**4
        return r
    for _ in range(steps):
        k1 = f(a); k2 = f(a+h*k1/2); k3 = f(a+h*k2/2); k4 = f(a+h*k3)
        a = a + h*(k1+2*k2+2*k3+k4)/6
    return a

m_b = mp.mpf('4.18'); m_c = mp.mpf('1.27')
targets = {'m_tau(1.777)': mp.mpf('1.777'), '2 GeV': mp.mpf('2.0'),
           '5 GeV': mp.mpf('5.0'), '1 GeV': mp.mpf('1.0')}

def chain_alpha(mu_target, order=3):
    """alpha(mu) via standard threshold chain from M_Z: Nf=5 to m_b, Nf=4 to m_c,
    Nf=3 below; if mu >= m_b -> Nf=5 direct; m_c <= mu < m_b -> Nf=4."""
    a = a_IDCM
    if mu_target >= m_b:
        return rge_down(a, M_Z, mu_target, 5, order=order)
    a_b = rge_down(a, M_Z, m_b, 5, order=order)
    if mu_target >= m_c:
        return rge_down(a_b, m_b, mu_target, 4, order=order)
    a_c = rge_down(a_b, m_b, m_c, 4, order=order)
    return rge_down(a_c, m_c, mu_target, 3, order=order)

print("\n2) Out-of-sample alpha_s (IDCM boundary + standard MS-bar RGE, 3-loop):")
world = {'m_tau(1.777)': (mp.mpf('0.314'), mp.mpf('0.020')),
         '2 GeV': (mp.mpf('0.303'), mp.mpf('0.007')),
         '5 GeV': (mp.mpf('0.216'), mp.mpf('0.008')),   # world avg ~0.215-0.219
         '1 GeV': (mp.mpf('0.43'),  mp.mpf('0.05'))}    # rough; report only
for name, mu in targets.items():
    a = chain_alpha(mu)
    if name in world:
        w, s = world[name]
        z = (a-w)/s
        tag = "GREEN" if abs(z) <= 2 else ("YELLOW" if abs(z) <= 3 else "RED")
        print(f"   alpha_s({name}) = {mp.nstr(a,6)}  vs world {mp.nstr(w,5)}+/-{mp.nstr(s,5)}  z={mp.nstr(z,4)}  [{tag}]")
    else:
        print(f"   alpha_s({name}) = {mp.nstr(a,6)}")

# sensitivity to loop order at 2-loop vs 3-loop
print("\n3) Loop-order sensitivity (same boundary):")
for name, mu in [('m_tau','1.777'), ('2 GeV','2.0')]:
    a2 = chain_alpha(mp.mpf(mu), order=2)
    a3 = chain_alpha(mp.mpf(mu), order=3)
    print(f"   alpha_s({name}): 2-loop {mp.nstr(a2,6)} | 3-loop {mp.nstr(a3,6)}")

# ---------- 4. Lambda_MS(5) from implicit formulas (PDG convention) ----------
# NOTE 2026-10-13: order=3 term below is NOT the standard 3-loop implicit
# (standard formula differs; the b2*ln^2 term here is a probe only).
# Values printed in MeV (was mislabeled GeV -> *1000 fixed). Use 2-loop value;
# 3-loop value should NOT be used as evidence.
def lam_from_alpha(mu, a, Nf, order):
    b0,b1,b2 = beta_coeff(Nf)
    x = b0*a/(2*mp.pi)
    L1 = 2*mp.pi/(b0*a)
    L2 = L1 + b1/(2*b0*b0)*mp.log(x) if order >= 2 else L1
    L3 = L2 + b2/(4*b0**3)*mp.log(x)**2 if order >= 3 else L2
    return mu*mp.exp(-L3)

print("\n4) Lambda_MS(5) implicit (from alpha(MZ) boundary; values in MeV):")
print("   PDG alpha_s,  2-loop:", mp.nstr(lam_from_alpha(M_Z, a_PDG, 5, 2)*1000, 5), "MeV",
      " 3-loop(probe):", mp.nstr(lam_from_alpha(M_Z, a_PDG, 5, 3)*1000, 5), "MeV  (PDG 5-loop ~213 MeV)")
print("   IDCM alpha_s, 2-loop:", mp.nstr(lam_from_alpha(M_Z, a_IDCM, 5, 2)*1000, 5), "MeV",
      " 3-loop(probe):", mp.nstr(lam_from_alpha(M_Z, a_IDCM, 5, 3)*1000, 5), "MeV")

# ---------- 5. Structural audit: T-hat ids of beta across Nf ----------
print("\n5) T-hat / structural audit of beta coefficients:")
for Nf in (6,5,4,3):
    b0,b1,b2 = beta_coeff(Nf)
    ids = []
    for n in range(1,15):
        if abs(b0 - L(n)) < 1e-9: ids.append(f"b0=L{n}")
        if abs(b1 - 2*F(n)) < 1e-9: ids.append(f"b1=2F{n}")
    if abs(b0 - mp.mpf(9)) < 1e-9: ids.append("b0=9=N_gen^2")
    if abs(b0 - mp.mpf(23)/3) < 1e-9: ids.append("b0=23/3")
    if abs(b1 - mp.mpf(154)/3) < 1e-9: ids.append("b1=154/3")
    print(f"   Nf={Nf}: b0={mp.nstr(b0,8)} b1={mp.nstr(b1,8)} b2={mp.nstr(b2,8)}  ids={', '.join(ids) if ids else '-'}")

# ---------- 6. scheme ratio (derived, not fitted) ----------
Lam5_1lo = M_Z*mp.exp(-2*mp.pi/((23/3)*a_IDCM))
print("\n6) Scheme ratio (derived from RG):")
print("   Lam5(1-loop)/Lam_IDCM =", mp.nstr(Lam5_1lo/(Lambda_IDCM/1000), 7))