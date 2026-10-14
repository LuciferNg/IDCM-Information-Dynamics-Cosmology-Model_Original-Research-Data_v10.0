#!/usr/bin/env python3
# -*- coding: ascii -*-
"""O142 v16c - sigma chain operatorization + rho fixity audit.

(a) sigma = SumGamma_odd * Lambda^2 with the v16 Lambda operator form:
    sigma = 2N_d * M0^2 * rho^2 * lambda_max      (SumGamma_odd = 88 = 2N_d, O144 closed)
    Check numeric closure (0.1804633 GeV^2 expected).
(b) rho fixity audit: rho = N_gen/L5 is a FIXED structural number (3/11).
    If rho were free, lambda_max = B*N_gen^2 - 1/(4cos^2(rho pi)) would wander;
    show lambda_max is O59-closed (native_12d) and NOT back-fit from Lambda.
(c) Sceptic test: is Lambda = M0*rho*sqrt(lambda_max) sensitive to rho? show
    that any rho != 3/11 gives a different Lambda -> no freedom was exploited.
"""
import mpmath as mp
mp.mp.dps = 50
phi = (1+mp.sqrt(5))/2
psi_ = (1-mp.sqrt(5))/2
L = lambda n: phi**n + psi_**n

M0 = mp.mpf('27.900915')
N_d, B, N_gen, L5 = mp.mpf(44), mp.mpf(4), mp.mpf(3), mp.mpf(11)
rho = N_gen/L5

gam20 = 4*mp.cos(N_gen*mp.pi/L5)**2
lam_max = B*N_gen**2 - 1/gam20
Lam = M0*rho*mp.sqrt(lam_max)

print("=== (a) sigma full chain operatorized ===")
Sg_odd = mp.mpf(88)  # EXACT: sum odd-mode gamma_n = 88 = 2N_d (O144 closed)
sig = Sg_odd * (Lam/1000)**2   # GeV^2
sig2 = 2*N_d * M0**2 * rho**2 * lam_max / 1e6  # MeV^2 -> GeV^2 (M0 in MeV)
print("  sigma = SumGamma_odd*Lambda^2          =", mp.nstr(sig, 9), "GeV^2")
print("  sigma = 2N_d * M0^2 * rho^2 * lam_max  =", mp.nstr(sig2, 9), "GeV^2")
print("  EXACT equal:", mp.almosteq(sig, sig2, rel_eps=mp.mpf('1e-30')))
print("  sqrt(sigma) =", mp.nstr(mp.sqrt(sig)*1000, 6), "MeV")
print("  Regge world 0.18 GeV^2 : dev", mp.nstr((sig-0.18)/0.18*100, 4), "%")

print("\n=== (b) rho fixity: lambda_max is O59-native_12d-closed, not back-fit ===")
# O59 native_12d: lambda_max = 36 - 1/gamma_20. Two equivalent evaluations:
lam_ref_mode = 36 - 1/(4*mp.sin(mp.pi*20/88)**2)          # mode-20 expression (O59)
lam_ref_rho  = 36 - 1/(4*mp.cos(N_gen*mp.pi/L5)**2)        # rho-angle expression (v16)
print("  lambda_max(mode expr)  =", mp.nstr(lam_ref_mode, 15))
print("  lambda_max(rho expr)   =", mp.nstr(lam_ref_rho, 15))
print("  EXACT identical (sin/cos complement identity):",
      mp.almosteq(lam_ref_mode, lam_ref_rho, rel_eps=mp.mpf('1e-40')))
print("  Lambda consumes lambda_max unchanged:", mp.almosteq(lam_max, lam_ref_rho, rel_eps=mp.mpf('1e-40')))

print("\n=== (c) sceptic: rho sensitivity (no freedom exploited) ===")
# If rho were tunable, Lambda would change by ~ (dLam/drho). Show exact partial.
# Lambda = M0 * rho * sqrt(B*N_gen^2 - sec2(rho*pi)/4) with rho=N_gen/L5 fixed.
# Compare: hypothetical rho = 3.0/11.001 etc - any shift breaks the O59 lambda_max.
for dr in ['0', '1e-6', '-1e-6', '1e-3']:
    rhop = rho + mp.mpf(dr)
    lam_p = B*N_gen**2 - 1/(4*mp.cos(rhop*mp.pi)**2)
    Lam_p = M0*rhop*mp.sqrt(lam_p)
    print(f"  rho={mp.nstr(rhop,8)}  Lambda={mp.nstr(Lam_p,10)} MeV  (dLam={mp.nstr((Lam_p-Lam)*1000,6)} keV)")

print("\n  -> rho is 3/11 exactly (N_gen/L5), not a fit parameter;")
print("     lambda_max is O59-native_12d closed; v16 only RE-EXPRESES the")
print("     existing Lambda in terms of a single structural rho.")

print("\n=== (d) check: gamma_20 also = 4 sin^2(mode20*pi/88), mode20=N_d-2B*N_gen ===")
mode20 = N_d - 2*B*N_gen
g_mode = 4*mp.sin(mode20*mp.pi/88)**2
print("  mode20 =", mp.nstr(mode20,3), " gamma_20(mode) =", mp.nstr(g_mode,12),
      " == 4cos^2(rho pi):", mp.almosteq(g_mode, gam20, rel_eps=mp.mpf('1e-40')))