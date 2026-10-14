#!/usr/bin/env python3
# -*- coding: ascii -*-
"""O142 v13c - closure robustness: 2-loop running + threshold matching.

v13 candidate: Lambda_IDCM = sqrt(lam_max)*M0*N_gen/L5 -> 1-loop alpha_s 0.016 sigma.
Mechanism completeness requires the closure survive:
  1) 2-loop RGE (b0=L4=7, b1=2F7=26) from Lambda_IDCM to M_Z
  2) Nf threshold matching (Nf=6 Lambda definition vs PDG Nf=5 value)
  3) structural identity of Lambda_IDCM/M0 (already: sqrt(lmax)*B*N_gen/N_d)
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
L4 = L(4); L5 = L(5); L6 = L(6); L7 = L(7)
F5 = F(5); F6 = F(6); F7 = F(7)
lam_max = 36 - 1/gamma(20)
strong = mp.sqrt(lam_max)*M0
Lambda_IDCM = strong*N_gen/L5   # MeV
M_Z = mp.mpf('91.1876')
alpha_s_PDG = mp.mpf('0.1180')
sig_alpha = mp.mpf('0.0009')

print("Lambda_IDCM =", mp.nstr(Lambda_IDCM, 12), "MeV =", mp.nstr(Lambda_IDCM/1000, 12), "GeV")
print("alpha_s_PDG =", mp.nstr(alpha_s_PDG, 10), "+/-", mp.nstr(sig_alpha, 8))

# ---------------- 1-loop (v13 baseline) ----------------
b0 = 7
a1_inv = (L4/(2*mp.pi))*mp.log(M_Z/(Lambda_IDCM/1000))
a1 = 1/a1_inv
print("\n=== 1-loop baseline ===")
print("alpha_s^-1 =", mp.nstr(a1_inv, 12), " alpha_s =", mp.nstr(a1, 10),
      " dev =", mp.nstr((a1-alpha_s_PDG)/alpha_s_PDG*100, 6), "%")

# ---------------- 2-loop RGE ----------------
# d(a^-1)/dt = -b0/2pi - b1/(8pi^2) * a  ... standard: with t=ln mu,
# da/dt = -b0 a^2/2pi - b1 a^3/4pi^2  ->  d(1/a)/dt = b0/2pi + b1/(4pi^2) * a
# Solve a(M_Z) by integrating from Lambda (a -> inf) analytically via
# 1/a1(mu) = (b0/2pi) ln(mu/Lambda) [1-loop]; 2-loop implicit:
# ln(mu/Lambda) = 2pi/(b0) * 1/a - (b1*2pi/(b0^2)) ln(b0*a/(2pi) + b1/(4pi^2) a/l...)
# Use standard: ln(mu/Lam) = (2pi/(b0 a)) - (b1/(4pi b0)) ln(  (2pi/b0)/a * (2pi/b0 a + b1/(4pi^2)) )... simplified integrate numerically.

def alpha_two_loop(Lam_GeV, mu_GeV, b0, b1):
    """Solve alpha at mu from 2-loop RGE with Lambda_MSbar(1-loop def) via shooting."""
    from mpmath import findroot
    # 2-loop relation (MS-bar): ln(mu/Lambda) = 2pi/(b0 a) + (b1/(4pi b0^2)) ln( (2pi/b0)/a * (2pi/b0 + b1 a/(4pi^2)) / (b1/(4pi^2)) )
    # simpler: integrate da/dlnmu = -b0 a^2/(2pi) - b1 a^3/(4 pi^2)
    # Use mpmath ODE from mu=mu0 where a given by 1-loop at some high mu, down to M_Z.
    nu0 = mp.mpf('1e7')  # GeV, high scale where 1-loop ok? Actually integrate from just above Lambda*
    # Set alpha at mu = 2*Lambda (perturbative-ish) and integrate to M_Z
    mu0 = 2*Lam_GeV
    # initial alpha0 from 1-loop: a0 = 1/((b0/2pi) ln(mu0/Lam))
    a0 = 1/((b0/(2*mp.pi))*mp.log(mu0/Lam_GeV))
    # integrate da/dlnmu = -(b0 a^2/2pi + b1 a^3/4pi^2) with dp
    steps = 20000
    ln_mu0 = mp.log(mu0); ln_mu1 = mp.log(mu_GeV)
    dln = (ln_mu1 - ln_mu0)/steps
    a = a0
    for k in range(steps):
        da = -(b0*a*a/(2*mp.pi) + b1*a*a*a/(4*mp.pi*mp.pi))
        a = a + da*dln
    return a

b1 = 26
a2 = alpha_two_loop(Lambda_IDCM/1000, M_Z, mp.mpf(b0), mp.mpf(b1))
print("\n=== 2-loop RGE (b0=7, b1=26) ===")
print("alpha_s(2-loop) =", mp.nstr(a2, 12), " dev =", mp.nstr((a2-alpha_s_PDG)/alpha_s_PDG*100, 6), "%")
print("1-loop vs 2-loop shift =", mp.nstr((a2-a1)/a1*100, 6), "%")
print("PDG sigma window =", mp.nstr(sig_alpha/alpha_s_PDG*100, 4), "%")
if abs((a2-alpha_s_PDG)/alpha_s_PDG) < 0.0076:
    print("=> closure SURVIVES 2-loop (within PDG 0.76% sigma)")
else:
    print("=> closure FAILS 2-loop")

# ---------------- Nf threshold matching ----------------
print("\n=== Nf threshold analysis ===")
# Lambda_IDCM defined in Nf=6 (b0=7). PDG Lambda_MSbar^(5) ~ 0.210 (5-loop).
# Match at top mass: alpha_6(m_t) = alpha_5(m_t) [1-loop approximation]
m_t = mp.mpf('172.57')
# 1-loop: 1/a = (b0/2pi) ln(mu/Lam)
# at m_t: alpha_6(m_t) from Lambda_IDCM(Nf=6)
a6_mt = 1/((7/(2*mp.pi))*mp.log(m_t/(Lambda_IDCM/1000)))
print("alpha_6(m_t) from Lambda_IDCM =", mp.nstr(a6_mt, 10))
# Nf=5 Lambda from matching:
b0_5 = mp.mpf(23)/3
Lam5 = m_t*mp.exp(-2*mp.pi/(b0_5*a6_mt))
print("Lambda_5(1-loop match) =", mp.nstr(Lam5*1000, 8), "MeV")
print("PDG Lambda_5 (5-loop) ~ 210 MeV ; 1-loop def gives", mp.nstr(Lam5*1000, 8), "(scheme-known difference)")
# Then alpha_5(M_Z) via 5-flavor running from m_t to M_Z:
a5_MZ = 1/((b0_5/(2*mp.pi))*mp.log(M_Z/Lam5))
print("alpha_5(M_Z) [5-flav running] =", mp.nstr(a5_MZ, 10), " dev =", mp.nstr((a5_MZ-alpha_s_PDG)/alpha_s_PDG*100, 6), "%")

# 2-loop + threshold full chain (b1_5 = 102 - 38*5/3 = 38/3):
b1_5 = 102 - mp.mpf(38)*5/3
print("b1(Nf=5) =", mp.nstr(b1_5, 8))
a5_MZ_2loop = alpha_two_loop(Lam5, M_Z, b0_5, b1_5)
print("alpha_5(M_Z) [2-loop, 5-flav] =", mp.nstr(a5_MZ_2loop, 12), " dev =", mp.nstr((a5_MZ_2loop-alpha_s_PDG)/alpha_s_PDG*100, 6), "%")

# ---------------- structural identity of Lambda/M0 ----------------
print("\n=== Structural identity: Lambda_IDCM/M0 ===")
r = Lambda_IDCM/M0
print("Lambda/M0 =", mp.nstr(r, 15))
print("sqrt(lmax)*B*N_gen/N_d =", mp.nstr(mp.sqrt(lam_max)*B*N_gen/N_d, 15))
print("dev =", mp.nstr((mp.sqrt(lam_max)*B*N_gen/N_d - r)/r*100, 8), "%")
print("N_d/B =", mp.nstr(N_d/B, 10), "= L5 =", mp.nstr(L5, 10), "-> L5 = N_d/B is EXACT identity (44/4=11)")
print("=> Lambda_IDCM = sqrt(lmax)*M0*(B*N_gen/N_d) : L5 in denominator = N_d/B (chain/branch ratio)")

# ---------------- lambda_max closed form check ----------------
print("\n=== lambda_max = 2L6 - 1/g20 ? ===")
print("2*L6 =", mp.nstr(2*L6, 12), "  lam_max+1/g20 =", mp.nstr(lam_max+1/gamma(20), 12))
print("2L6 - 1/g20 =", mp.nstr(2*L6 - 1/gamma(20), 12), " vs lam_max =", mp.nstr(lam_max, 12))
print("N_d - 2B =", N_d-2*B, " = 36 ; 2L6 =", mp.nstr(2*L6, 8), "-> 36 = 2L6 confirmed")
# sigma_phi + g1 was close but phi-power trap; check g19*(1+6g1) cold?
print("\nphi+gamma1 dev 0.0043% : phi-power trap? (memory: phi-fitting forbidden)")
print("=> REJECT phi+gamma1 as mechanism; keep sqrt(lmax)*B*N_gen/N_d")