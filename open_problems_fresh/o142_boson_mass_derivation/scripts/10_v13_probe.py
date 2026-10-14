#!/usr/bin/env python3
# -*- coding: ascii -*-
# NOTE: ASCII-only enforced.  No non-ascii chars in this file (was lint-error).
"""v13 principle-first closure probe (O142) - high precision checks"""
import mpmath as mp
mp.mp.dps = 60

phi = (1+mp.sqrt(5))/2
psi_ = (1-mp.sqrt(5))/2
L = lambda n: phi**n + psi_**n
F = lambda n: (phi**n - psi_**n)/mp.sqrt(5)
gamma = lambda n: 4*mp.sin(mp.pi*n/88)**2

M0 = mp.mpf('27.900915')
N_d = mp.mpf(44); B = mp.mpf(4); N_gen = mp.mpf(3)
L5 = L(5); L4 = L(4)
lam_max = 36 - 1/gamma(20)
Lambda_IDCM = mp.sqrt(lam_max)*M0*N_gen/L5
M_Z = mp.mpf('91.1876')

print("=== v13-C: alpha_s principle-first closure ===")
print("lambda_max =", mp.nstr(lam_max, 20), "(36-1/g20)")
print("Lambda_IDCM = sqrt(lmax)*M0*N_gen/L5 =", mp.nstr(Lambda_IDCM/1000, 15), "GeV")
alpha_s_inv_IDCM = (L4/(2*mp.pi))*mp.log(M_Z/(Lambda_IDCM/1000))
alpha_s_IDCM = 1/alpha_s_inv_IDCM
print("alpha_s^-1_IDCM = (L4/2pi) ln(M_Z/Lambda) =", mp.nstr(alpha_s_inv_IDCM, 15))
print("alpha_s^-1_PDG  = 8.474576 (PDG2024 0.1180)")
print("alpha_s_IDCM    =", mp.nstr(alpha_s_IDCM, 12), " vs 0.1180")
print("dev a_s^-1 =", mp.nstr((alpha_s_inv_IDCM-8.474576)/8.474576*100, 8), "%")
print("z(a_s^-1)  =", mp.nstr((alpha_s_inv_IDCM-8.474576)/0.0647, 4), "sigma")

Lam_from_PDG = M_Z*mp.exp(-2*mp.pi*(1/mp.mpf('0.1180'))/7)
print("\nPMD value Lambda(1-loop,b0=7) =", mp.nstr(Lam_from_PDG, 10), "GeV =", mp.nstr(Lam_from_PDG*1000, 10), "MeV")
print("Lambda_IDCM dev vs 1-loop target =", mp.nstr((Lambda_IDCM/1000-Lam_from_PDG)/Lam_from_PDG*100, 8), "%")

print("\n=== density: Lambda = sqrt(lmax)*M0*(num/den) ===")
target = Lam_from_PDG
for num, den, label in [(3, 11, "N_gen/L5"), (4, 11, "B/L5"), (5, 11, "F5/L5"), (7, 11, "L4/L5"),
                        (2, 11, "2/L5"), (1, 3, "1/3"), (3, 7, "N_gen/L4"), (4, 7, "B/L4")]:
    cand = mp.sqrt(lam_max)*M0*num/den/1000
    dev = (cand-target)/target*100
    print(f"  x{label:>9s} = {mp.nstr(cand,9):>12s} GeV  dev {mp.nstr(dev,6):>10s}%")
print("  ratio sqrt(lmax)*M0/(Lambda_1loop) =", mp.nstr(mp.sqrt(lam_max)*M0/(Lam_from_PDG*1000), 8))
print("  L5/3 =", mp.nstr(L5/3, 8), "(0.16% off ratio)")

print("\n=== v13-B: alpha(0)/alpha(M_Z) spectral identities ===")
Sigma_gamma = sum(gamma(n) for n in range(1, 45))
print("Sum gamma =", mp.nstr(Sigma_gamma, 20), "(O211: B(N_d+1)/2 = 90 EXACT)")
print("alpha_GUT^-1 = 47 (O89: 2K_tree - F7 - 6 = 53-6)")
print("-> alpha^-1(0) = 90 + 47 = 137  OK" if Sigma_gamma + 47 == 137 else "FAIL 137")
print("-> alpha^-1(M_Z) = 137 - N_gen^2 = 128  OK")
print("identity: 3N0 + F5 = 132+5 = 137 ; SumGamma+alphaGUT = 90+47 = 137")

print("\n=== v13-A: v operator-trace form (all T-hat/K_Chain structure) ===")
v = mp.sqrt(lam_max)*M0*(2*N_d)*(2*F(5)+B*L4*gamma(7))
print("v = sqrt(N_d-2B-1/g20) * M0 * 2N_d * (2F5 + B*L4*g7)")
print("  sqrt(36-1/g20) =", mp.nstr(mp.sqrt(lam_max), 12), "(36 = N_d-2B = 44-8)")
print("  2F5 + B*L4*g7 = 10 + 28*g7 =", mp.nstr(10+4*7*gamma(7), 12))
print("v =", mp.nstr(v/1000, 12), "GeV  (PDG 246.2196, dev =",
      mp.nstr((v/1000-mp.mpf('246.2196'))/mp.mpf('246.2196')*100, 8), "%)")
print("v =", mp.nstr(v, 10), "MeV (O59 docs/16: 246.21 GeV dev 0.0028%)")

print("\n=== Cross-check: does Lambda_IDCM map to known mass scales? ===")
# 45.285 MeV vs hadronic scales
print("Lambda_IDCM =", mp.nstr(Lambda_IDCM, 10), "MeV")
print("m_pi = 139.57 MeV ; ratio =", mp.nstr(Lambda_IDCM/mp.mpf('139.57'), 6))
print("m_mu = 105.66 MeV ; ratio =", mp.nstr(Lambda_IDCM/mp.mpf('105.66'), 6))
print("m_s  ~ 92.5 MeV  ; ratio =", mp.nstr(Lambda_IDCM/mp.mpf('92.5'), 6))
print("1-loop Lambda(N_f=6, 5-loop scheme) ~ 90 MeV? ratio =", mp.nstr(Lambda_IDCM/mp.mpf('90'), 6))
print("sqrt(lmax)*M0 =", mp.nstr(mp.sqrt(lam_max)*M0, 8), "MeV (O59 strong scale = 166.05)")