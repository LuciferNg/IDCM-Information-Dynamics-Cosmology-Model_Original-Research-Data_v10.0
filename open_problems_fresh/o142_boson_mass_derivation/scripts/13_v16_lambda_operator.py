#!/usr/bin/env python3
# -*- coding: ascii -*-
"""O142 v16a - Lambda operator identity test:
   Lambda_MS(5) NLO (166.006 MeV from P9) == sqrt(lambda_max)*M0 ?
   If EXACT -> operator derivation: Lambda_MS5 = sqrt(2L6 - 1/gamma_20) * M0
   and Lambda_IDCM (1-loop Nf=6) = Lambda_MS5 * N_gen/L5  (single structural ratio).
"""
import mpmath as mp
mp.mp.dps = 50
phi = (1+mp.sqrt(5))/2
psi_ = (1-mp.sqrt(5))/2
L = lambda n: phi**n + psi_**n
F = lambda n: (phi**n - psi_**n)/mp.sqrt(5)
gamma = lambda n: 4*mp.sin(mp.pi*n/88)**2

M0 = mp.mpf('27.900915')
lam_max = 36 - 1/gamma(20)
core = mp.sqrt(lam_max)*M0
print("lambda_max =", mp.nstr(lam_max, 15))
print("sqrt(lambda_max) =", mp.nstr(mp.sqrt(lam_max), 12))
print("sqrt(lambda_max)*M0 =", mp.nstr(core, 12), "MeV   <-- candidate Lambda_MS(5)")
print("  vs P9 Lambda_MS(5) NLO implicit = 166.0064 MeV")
dev = (core-166.0064)/166.0064*100
print("  dev =", mp.nstr(dev, 6), "%")

# Lambda_IDCM itself
Lam_IDCM = core*3/11
print("\nLambda_IDCM = sqrt(lam_max)*M0*N_gen/L5 =", mp.nstr(Lam_IDCM, 12), "MeV")

# Structural components with T-hat IDs
print("\ncomponents:")
print("  2*L6 =", mp.nstr(2*L(6), 12), " (=36)")
print("  gamma_20 =", mp.nstr(gamma(20), 12), " 1/gamma_20 =", mp.nstr(1/gamma(20), 12))
print("  lambda_max = 2L6 - 1/gamma_20 =", mp.nstr(2*L(6) - 1/gamma(20), 12))

# gamma_20 : 4 sin^2(20 pi/88) = 4 sin^2(5 pi/22). sin(5pi/22) = cos(3pi/11)!
sin5p22 = mp.sin(5*mp.pi/22)
cos3p11 = mp.cos(3*mp.pi/11)
print("\ncheck: sin(5pi/22) =", mp.nstr(sin5p22, 12), " cos(3pi/11) =", mp.nstr(cos3p11, 12),
      " equal:", mp.almosteq(sin5p22, cos3p11, rel_eps=mp.mpf('1e-40')))
# 20 mode <-> 3pi/11: 3 = N_gen, 11 = L5. So gamma_20 = 4 cos^2(N_gen*pi/L5)
print("gamma_20 = 4 cos^2(3 pi/11) =", mp.nstr(4*cos3p11**2, 12))
print("  -> index 20 anchored to N_gen*pi/L5 (3 pi/11). mode n=20 of 88:",
      5*mp.pi/22, "= 3pi/11 + pi/2 - pi/2... exact: pi/2 - 3pi/11 =", mp.nstr(mp.pi/2-3*mp.pi/11,6))

# Lambda ratio table: Lambda_MS5 / Lambda_IDCM
print("\nLambda_MS5/Lambda_IDCM = 11/3 =", mp.nstr(Lam_IDCM*11/3, 12))

# ------------------------------------------------------------------
# Density test: is sqrt(lambda_max)*M0 unique in V_core window around 166.0064?
# vocabulary: L_n, F_n, gamma_n, N_d, B, N_gen products/ratios
V_core = [2,3,4,5,7,8,11,13,17,18,21,29,33,34,35,36,44,47,55,71,88,89,90,123,176,178,528]
print("\nDensity: candidate = sqrt(lambda_max)*M0 / M0 = sqrt(lambda_max) =", mp.nstr(mp.sqrt(lam_max), 10))
target = mp.sqrt(lam_max)
hits = []
for a in V_core:
    for b in V_core:
        for s in (1,-1):
            v = mp.mpf(a)/b
            d = abs(v-target)/target
            if d < 0.002:  # 0.2% window
                hits.append((mp.nstr(v,10), mp.nstr(d,4), f"{a}/{b}"))
print(f"V_core ratio hits within 0.2% of sqrt(lambda_max): {len(hits)}")
for h in hits[:10]: print("  ", h)

# irrational-algebraic candidate? sqrt of lambda_max itself is the 'operator' answer.
print("\nConclusion candidates:")
print("  (a) Lambda_MS5 = sqrt(2L6 - 1/(4cos^2(3pi/11))) * M0  [all IDCM closed qty]")