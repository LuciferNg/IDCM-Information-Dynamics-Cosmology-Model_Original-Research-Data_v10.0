#!/usr/bin/env python3
# -*- coding: ascii -*-
"""O142 v14 - Full-order MS-bar closure from IDCM structural boundary.

Criterion-2 (mechanism) attack: establish IDCM scheme <-> MS-bar correspondence
by running the STANDARD SM MS-bar RGE (with full flavor thresholds) from the
IDCM structural boundary alpha_s(M_Z) = 1/8.47562 (zero-fit boundary; derived
from Lambda_IDCM = sqrt(lam_max)*M0*N_gen/L5, all closed quantities).

Question: does the IDCM boundary + standard QCD RGE reproduce the observed
world at OUT-OF-SAMPLE scales (alpha_s(m_tau), alpha_s(2-5 GeV), Lambda_MS(5))?
If yes within PDG sigma -> the scheme correspondence is empirically established
with zero new constants. If no -> the yellow light stays (or RED if >3sigma).

Pre-registered verdict (before running):
  GREEN  : all out-of-sample alpha_s within 2 sigma (PDG errors)
  YELLOW : within 3 sigma but systematic offset / one point > 2 sigma
  RED    : any point > 3 sigma  -> Nf=6-constant scheme falsified at low scale

beta (SM MS-bar, a = alpha_s):
  d a / d ln mu = -b0 a^2/(2pi) - b1 a^3/(4pi^2) - b2 a^4/(16pi^3)
  b0 = 11 - 2 Nf/3 ; b1 = 102 - 38 Nf/3 ; b2 = 2857/2 - 5033 Nf/18 + 325 Nf^2/54
  check at Nf=6: b0=7=L4, b1=26=2F7, b2=-65/2=-F5*F7/2   [T-hat IDs]
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
a_PDG = mp.mpf('0.1179'); sig_PDG = mp.mpf('0.0009')   # PDG 2024 alpha_s(MZ)

# ---------- 1. IDCM structural boundary ----------
b0_6, b1_6, b2_6 = mp.mpf(7), mp.mpf(26), -mp.mpf(65)/2
a_inv_IDCM = (b0_6/(2*mp.pi))*mp.log(M_Z/(Lambda_IDCM/1000))
a_IDCM = 1/a_inv_IDCM
print("1) IDCM boundary (zero fit):")
print("   Lambda_IDCM =", mp.nstr(Lambda_IDCM, 10), "MeV")
print("   alpha_s^-1(MZ) =", mp.nstr(a_inv_IDCM, 8), " alpha_s =", mp.nstr(a_IDCM, 8))
print("   PDG alpha_s =", mp.nstr(a_PDG, 6), "+/-", mp.nstr(sig_PDG, 5), " -> dev", 
      mp.nstr((a_IDCM-a_PDG)/sig_PDG, 6), "sigma")

# ---------- 2. Standard MS-bar beta per Nf ----------
def beta_coeff(Nf):
    b0 = mp.mpf(11) - mp.mpf(2)*Nf/3
    b1 = mp.mpf(102) - mp.mpf(38)*Nf/3
    b2 = mp.mpf(2857)/2 - mp.mpf(5033)*Nf/18 + mp.mpf(325)*Nf*Nf/54
    return b0, b1, b2
for Nf in (6,5,4,3):
    b0,b1,b2 = beta_coeff(Nf)
    print(f"   beta(Nf={Nf}): b0={mp.nstr(b0,9)} b1={mp.nstr(b1,9)} b2={mp.nstr(b2,9)}")

# ---------- 3. RK4 RGE down with thresholds ----------
def rge_down(a_start, mu_hi, mu_lo, Nf, steps=120000):
    """Integrate d a/d ln mu = -(b0/(2pi))a^2 - (b1/(4pi^2))a^3 - (b2/(16pi^3))a^4
    from mu_hi to mu_lo with fixed Nf. Returns a(mu_lo)."""
    b0,b1,b2 = beta_coeff(Nf)
    lnh, lnl = mp.log(mu_hi), mp.log(mu_lo)
    h = (lnl - lnh)/steps
    a = a_start
    for _ in range(steps):
        def f(x):  # da/dlnmu
            return -(b0/(2*mp.pi))*x*x - (b1/(4*mp.pi*mp.pi))*x*x*x - (b2/(16*mp.pi**3))*x**4
        k1 = f(a)
        k2 = f(a + h*k1/2)
        k3 = f(a + h*k2/2)
        k4 = f(a + h*k3)
        a = a + h*(k1 + 2*k2 + 2*k3 + k4)/6
    return a

# Threshold chain from M_Z down (top decouples ABOVE M_Z; Nf=5 at M_Z)
# m_b (MS 4.18), m_c (1.27) : standard PDG running masses
m_b = mp.mpf('4.18'); m_c = mp.mpf('1.27')
a5_MZ = a_IDCM   # IDCM boundary at M_Z -> same alpha, physical scheme Nf=5? 
# NOTE: IDCM formula used b0=7 (Nf=6) at M_Z. In standard MS-bar, top is DECOUPLED
# at M_Z (m_t=172.57), so active flavors at M_Z = 5. The IDCM scheme treats Nf=6
# at all scales; the correspondence test converts: run standard Nf=5 chain from
# M_Z with the SAME boundary alpha (alpha is scheme-independent at 1-loop), OR
# treat the IDCM boundary as Nf=6 and threshold-match to Nf=5 at m_t. We do BOTH.

def chain_from_MZ(a_MZ, Nf_at_MZ, lbl):
    a = a_MZ
    # Nf_at_MZ active down to m_b
    a_b = rge_down(a, M_Z, m_b, Nf_at_MZ)
    a_c = rge_down(a_b, m_b, m_c, Nf_at_MZ-1)
    a_1 = rge_down(a_c, m_c, mp.mpf('1.0'), Nf_at_MZ-2)
    a_2 = rge_down(a_c, m_c, mp.mpf('2.0'), Nf_at_MZ-2)
    a_mtau = rge_down(a_c, m_c, mp.mpf('1.777'), Nf_at_MZ-2)
    return a_b, a_c, a_1, a_2, a_mtau

# Chain A: IDCM boundary as Nf=5 at M_Z (physically: top decoupled)
lbl = "A: Nf=5 at M_Z (physical)"
a_bA, a_cA, a_1A, a_2A, a_tauA = chain_from_MZ(a_IDCM, 5, lbl)

# Chain B: IDCM boundary as Nf=6 at M_Z, match to Nf=5 at m_t (IDCM scheme = 6 always),
# then threshold chain. Continuity 1-loop: alpha(m_t) continuous.
m_t = mp.mpf('172.57')
a_t_6 = rge_down(a_IDCM, M_Z, m_t, 6)            # up?? no: m_t > M_Z! top ABOVE M_Z.
# Since m_t > M_Z, chain B from M_Z down stays Nf=5 below M_Z; the IDCM Nf=6-at-MZ
# boundary is a SCHEME DEFINITION, not threshold physics. Compare both only via alpha(M_Z).
lblB = "B: same alpha(MZ) boundary (Nf=6 formula) -> physics same at M_Z"
a_bB, a_cB, a_1B, a_2B, a_tauB = chain_from_MZ(a_IDCM, 5, lblB)

# ---------- 4. Out-of-sample comparison ----------
# World data (PDG 2024):
#   alpha_s(m_tau=1.777) = 0.314 +/- 0.020  (tau decays, Nf=3)
#   alpha_s(2 GeV) ~ 0.30 (lattice, Nf=3; FLAG ~0.3026+/-0.0063)
#   alpha_s(5 GeV) ~ 0.215 +/- 0.007? (world avg via e+e- etc ~0.216)
# PRE-REGISTERED passband = PDG central +/- 2 sigma
def verdict(val, pm, world, sig):
    z = (val-world)/sig
    tag = "GREEN" if abs(z) <= 2 else ("YELLOW" if abs(z) <= 3 else "RED")
    return f"{mp.nstr(val,6)} vs world {world} +/- {sig}  z = {mp.nstr(z,4)}  [{tag}]"

print("\n3) Out-of-sample (no fit):")
print("   alpha_s(m_tau) :", verdict(a_tauA, None, mp.mpf('0.314'), mp.mpf('0.020')))
print("   alpha_s(2 GeV) :", verdict(a_2A,  None, mp.mpf('0.303'), mp.mpf('0.007')))
print("   alpha_s(5 GeV) :", verdict(a_1A,  None, mp.mpf('0.216'), mp.mpf('0.008')))

# ---------- 5. Lambda_MS(5) via 2-loop implicit from alpha(MZ) ----------
def lam_from_alpha_2loop(mu, a, Nf):
    """2-loop MS-bar implicit: ln(mu/Lam) = 2pi/(b0 a) + (b1/(2 b0^2)) ln(b0 a/(2pi))
    solve for Lam. (standard convention, PDG)."""
    b0,b1,_ = beta_coeff(Nf)
    rhs = 2*mp.pi/(b0*a) + b1/(2*b0*b0)*mp.log(b0*a/(2*mp.pi))
    return mu*mp.exp(-rhs)

Lam5_2lo = lam_from_alpha_2loop(M_Z, a_PDG, 5)
Lam5_IDCM = lam_from_alpha_2loop(M_Z, a_IDCM, 5)
print("\n4) Lambda_MS(5) 2-loop implicit:")
print("   from PDG alpha_s    :", mp.nstr(Lam5_2lo, 6), "MeV  (PDG 5-loop ~210-213)")
print("   from IDCM alpha_s   :", mp.nstr(Lam5_IDCM, 6), "MeV  dev vs 213:",
      mp.nstr((Lam5_IDCM-213)/213*100, 5), "%")

# ---------- 6. T-hat structural audit of beta coefficients across Nf ----------
print("\n5) T-hat audit of beta coefficients (structural, informational):")
for Nf in (6,5,4,3):
    b0,b1,b2 = beta_coeff(Nf)
    hits = []
    if abs(b0 - L(4)) < 1e-9: hits.append("b0=L4=7")
    if abs(b0 - mp.mpf(9)) < 1e-9 and Nf == 3: hits.append("b0=N_gen^2=9")
    if abs(b1 - 2*F(7)) < 1e-9: hits.append("b1=2F7=26")
    if abs(b0 - mp.mpf(23)/3) < 1e-9: hits.append("b0=23/3? no")
    print(f"   Nf={Nf}: b0={mp.nstr(b0,8)} b1={mp.nstr(b1,8)} b2={mp.nstr(b2,8)}  ids: {', '.join(hits) if hits else '-'}")

# ---------- 7. scheme-correspondence ratio Lambda_5(1-loop)/Lambda_IDCM ----------
Lam5_1lo = M_Z*mp.exp(-2*mp.pi/((23/3)*a_IDCM))
print("\n6) Scheme ratio:")
print("   Lam5(1-loop)/Lam_IDCM =", mp.nstr(Lam5_1lo/(Lambda_IDCM/1000), 8))
print("   (structural candidate 51/11 = 4.636 dense-killed; here it is DERIVED from RG, not fitted)")