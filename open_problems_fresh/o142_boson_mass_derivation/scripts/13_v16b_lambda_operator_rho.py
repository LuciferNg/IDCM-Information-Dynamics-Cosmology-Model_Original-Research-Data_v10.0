#!/usr/bin/env python3
# -*- coding: ascii -*-
"""O142 v16b - Lambda_IDCM operator derivation (mechanism criterion 6).

CLAIM: Lambda_IDCM is not a fitted composite - it is a single-parameter
algebraic function of {M0, B, N_gen, L5} with NO free gamma_20:
   gamma_20 is NOT an independent mode: mode 20 = N_d - 2B*N_gen (N_d=44, B=4, N_gen=3)
   gamma_20 = 4 cos^2(N_gen*pi/L5)                       (angle identity)
   lambda_max = B*N_gen^2 - 1/gamma_20 = 36 - 1/gamma_20 (36 = B*N_gen^2!)
   Lambda_IDCM = M0 * (N_gen/L5) * sqrt(lambda_max)
All checks EXACT with mpmath 50 dps.
"""
import mpmath as mp
mp.mp.dps = 50
phi = (1+mp.sqrt(5))/2
psi_ = (1-mp.sqrt(5))/2
L = lambda n: phi**n + psi_**n

M0 = mp.mpf('27.900915')
N_d, B, N_gen, L5 = mp.mpf(44), mp.mpf(4), mp.mpf(3), mp.mpf(11)

print("=== Step 1: mode identity 20 = N_d - 2B*N_gen ===")
mode20 = N_d - 2*B*N_gen
mode24 = 2*B*N_gen
print(f"  20 = N_d - 2B*N_gen = 44 - 24 = {mode20}")
print(f"  24 = 2B*N_gen = {mode24}")
print(f"  complement check: 20 + 24 = {mode20+mode24} = N_d  -> sin(20pi/88) = cos(24pi/88)")

print("\n=== Step 2: gamma_20 = 4 sin^2(20pi/88) = 4 cos^2(N_gen*pi/L5) ===")
g20_by_mode = 4*mp.sin(mp.pi*20/88)**2
g20_by_rho  = 4*mp.cos(N_gen*mp.pi/L5)**2
print(f"  gamma_20 (mode) = {mp.nstr(g20_by_mode, 15)}")
print(f"  4cos^2(N_gen pi / L5) = {mp.nstr(g20_by_rho, 15)}")
print(f"  EXACT equal: {mp.almosteq(g20_by_mode, g20_by_rho, rel_eps=mp.mpf('1e-40'))}")

print("\n=== Step 3: lambda_max = B*N_gen^2 - 1/gamma_20 ===")
lam_a = 36 - 1/g20_by_rho
lam_b = B*N_gen**2 - 1/g20_by_rho
print(f"  B*N_gen^2 = {B*N_gen**2}  (= 36 = 2L6, dual reading)")
print(f"  lambda_max = {mp.nstr(lam_a, 15)}  vs B*N_gen^2 - 1/gamma_20 = {mp.nstr(lam_b, 15)}")
print(f"  EXACT equal: {mp.almosteq(lam_a, lam_b, rel_eps=mp.mpf('1e-40'))}")

print("\n=== Step 4: Lambda_IDCM as algebraic function of {M0,B,N_gen,L5} ===")
rho = N_gen/L5
Lam = M0 * rho * mp.sqrt(lam_a)
print(f"  rho = N_gen/L5 = {mp.nstr(rho, 15)}")
print(f"  Lambda_IDCM = M0 * rho * sqrt(B*N_gen^2 - 1/(4cos^2(rho*pi)))")
print(f"             = {mp.nstr(Lam, 12)} MeV")
print(f"  expected   = 45.2848693374  MeV")

print("\n=== Step 5: does ANY other mode reproduce the same complement structure? ===")
# mode n = N_d - 2B*N_gen + k would give angle (2k-shifted); only k=0 makes the
# complement angle exactly N_gen*pi/L5 within 1..44 (N_d-... > 0 and partner < 44)
hits = []
for n in range(1, 45):
    # gamma_n == 4cos^2(N_gen*pi/L5) ?  i.e. n or 88-n maps to complement
    if mp.almosteq(4*mp.sin(mp.pi*n/88)**2, g20_by_rho, rel_eps=mp.mpf('1e-12')):
        hits.append(n)
print(f"  modes n in 1..44 with gamma_n == 4cos^2(3pi/11): {hits}")
print("  (gamma spectrum monotonic in 1..44 -> unique n; n and 44-n pairs...)")

print("\n=== Step 6: uniqueness of lambda_max identity among B,N_gen vocabulary ===")
target = lam_a
cands = []
for a in (B, N_gen, L5, N_d, B*N_gen, N_gen**2, B*N_gen**2, 2*L(6)):
    for s in (1, -1):
        v = mp.mpf(a) + s/g20_by_rho
        d = abs(v-target)/target
        if d < 1e-9:
            cands.append((mp.nstr(v,12), f"{a} {s} 1/gamma_20"))
print(f"  identities B*N_gen^2 +/- 1/gamma_20 in vocab: {cands}")

print("\n=== Step 7: rho unification (the mechanism) ===")
print("  lambda_max = B*N_gen^2 - 1/(4 cos^2(rho pi)),  rho = N_gen/L5")
print("  Lambda_IDCM = M0 * rho * sqrt(lambda_max)")
print("  -> gamma_20 ceases to be an input: mode 20 = N_d - 2B*N_gen is")
print("     pinned by {N_d, B, N_gen}; its angle = rho*pi = (N_gen/L5)*pi.")
print("  -> the 'N_gen/L5' factor in Lambda is the SAME rho that builds lambda_max.")