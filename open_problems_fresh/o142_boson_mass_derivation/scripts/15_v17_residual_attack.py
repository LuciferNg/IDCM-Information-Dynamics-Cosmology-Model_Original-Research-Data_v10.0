#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O142 v17 - residual attack: (1) v/Lambda common-core ratio structure
(2) rho*pi = 3pi/11 algebraic identity (cos(3pi/11), degree-5).

residuals from docs/16 §6:
  R4: v and Lambda share core sqrt(lambda_max)*M0 - EW<->QCD scale common origin
  R2: cos(3pi/11) degree-5 algebraic number - structure not closed
Also re-state R1 (+0.023%) and R3 (lattice sigma tension) status.
"""
import mpmath as mp
mp.mp.dps = 60
phi = (1+mp.sqrt(5))/2
psi_ = (1-mp.sqrt(5))/2
L = lambda n: phi**n + psi_**n
F = lambda n: (phi**n - psi_**n)/mp.sqrt(5)
gamma = lambda n: 4*mp.sin(mp.pi*n/88)**2
M0 = mp.mpf('27.900915')
lam_max = 36 - 1/gamma(20)
core = mp.sqrt(lam_max)*M0          # MeV
Lam = core*3/11                     # MeV
v13 = core*88*(2*F(5)+4*L(4)*gamma(7))/1000   # GeV  (v formula, docs/11 §2.1)
g7 = gamma(7)

print("="*72)
print("R4. v / Lambda common-core analysis")
print("="*72)
print(f"  core = sqrt(lam_max)*M0 = {mp.nstr(core,12)} MeV = {mp.nstr(core/1000,10)} GeV")
print(f"  Lambda_IDCM = core*N_gen/L5 = {mp.nstr(Lam,10)} MeV")
print(f"  v = core*2N_d*(2F5+B*L4*gamma7)/1000 = {mp.nstr(v13,8)} GeV (dev vs PDG 246.2196: {mp.nstr((v13-246.2196)/246.2196*100,5)}%)")
print(f"  v/Lambda ratio = {mp.nstr(v13/(Lam/1000), 8)}")
r = v13/(Lam/1000)
print(f"    = (core*88*(10+28g7)/1000) / (core*3/11/1000) = 88*(10+28g7)*11/3")
r2 = 88*(10+28*g7)*11/3
print(f"    recompute: {mp.nstr(r2,8)}  match:", mp.almosteq(r,r2,rel_eps=mp.mpf('1e-40')))
print(f"    factor: 88*(10+28g7) = {mp.nstr(88*(10+28*g7),8)}")
inner = 10+28*g7
print(f"    inner = 10+28*gamma7 = {mp.nstr(inner,8)} ; gamma7 = {mp.nstr(g7,10)}")
# structure of inner: 10 = 2F5; 28 = B*L4; gamma7
# v/Lam = 88*(11/3)*(2F5 + B*L4*gamma7) = (2N_d * L5/N_gen) * (2F5 + B*L4*gamma7)
print(f"    -> v/Lam = (2N_d * L5/N_gen) * (2F5 + B*L4*gamma7)")
print(f"            = (88 * 11/3) * (10 + 28*gamma7)")
print(f"NOTE: 88*11/3 = {mp.nstr(88*11/3,8)} = 2N_d*L5/N_gen (N_gen and L5 swapped vs Lambda!)")
print(f"     v uses *N_d*N_d-ish, Lambda uses /L5: v scales UP by sites, Lambda by ratio - check docs/11")

# check: is inner (10+28g7) expressible in pure beats? g7 = 4sin^2(7pi/88)
print(f"\n  inner = 2F5 + B*L4*gamma7 = 10 + 112*sin^2(7pi/88)).")
# degree: gamma7 = 4sin^2(7pi/88): 7pi/88 = 7*pi/(8*11). sin(7pi/88) algebraic degree = ? 
# 88 = 8*11. 7pi/88 = (7/8)(pi/11). Not cyclotomic-of-88? e^{i 7pi/88} = 176th root? -> deg phi(176)/2?
# relevance: gamma7 known from mu-lepton mode (v6 framework) - closed already.
print("  (harmonic relation: gamma7 = mu-lepton mode, closed in v6 framework; inner is"
      "\n   composition of closed quantities -> NOT a new residual)")

print("="*72)
print("R2. rho*pi = 3pi/11 algebraic identity")
print("="*72)
c3 = mp.cos(3*mp.pi/11)
print(f"  cos(3pi/11) = {mp.nstr(c3,15)}")
print(f"  gamma20 = 4cos^2(3pi/11) = {mp.nstr(4*c3**2,12)} = {mp.nstr(gamma(20),12)} (match: {mp.almosteq(4*c3**2,gamma(20),rel_eps=mp.mpf('1e-50'))})")
# minimal polynomial of 2cos(3pi/11) via 22nd cyclotomic: 2cos(3pi/11) = zeta22^3 + zeta22^-3
# Phi_22(x) = x^10 - x^9 + x^8 - x^7 + x^6 - x^5 + x^4 - x^3 + x^2 - x + 1
# y = z + z^-1 = 2cos(3pi/11): reduce Phi_22 with x^2 - yx + 1 = 0
# do it symbolically with fractions
import fractions
def reduce_cyclo(N, k):
    """minimal polynomial of zeta_N^k + zeta_N^{-k} = 2cos(2pi k/N) via resultant-free
    manual reduction of Phi_N on x^2 - y x + 1."""
    Phi = [fractions.Fraction(1) for _ in range(N)]  # coeffs ascending
    # Phi_N for N=22: sum_{j=0}^{10} x^j - sum ... actually build via mobius
    import sympy as sp  # will try
    return None
try:
    import sympy as sp
    x = sp.symbols('x')
    z11 = sp.exp(2*sp.pi*sp.I/22)
    # 2cos(3pi/11) = z11^3 + z11^-3 ; minimal poly over Q
    a = sp.exp(3*sp.pi*sp.I/11)
    mpoly = sp.minimal_polynomial(sp.exp(3*sp.pi*sp.I/11)+sp.exp(-3*sp.pi*sp.I/11), x)
    print(f"  minimal polynomial of 2cos(3pi/11): {sp.factor(mpoly)}")
    print(f"  degree: {sp.degree(mpoly)}")
    # factor over rationals
    print(f"  factor over Q: {sp.factor(mpoly)}")
except Exception as e:
    print(f"  sympy minimal poly failed: {e}")
print()
print("  structural probe: 3pi/11 vs golden angle?")
twopi_over_11 = 2*mp.pi/11
print(f"    2pi/11 = {mp.nstr(twopi_over_11,8)}")
print(f"    3pi/11 = {mp.nstr(3*mp.pi/11,8)}")
print(f"    pi/2 - 3pi/11 = {mp.nstr(mp.pi/2-3*mp.pi/11,8)} = 5pi/22")
print(f"    3pi/11 + pi/2 = {mp.nstr(3*mp.pi/11+mp.pi/2,8)}")
print(f"    N_gen*pi/L5: 3*pi/11 = {mp.nstr(3*mp.pi/11,8)} (def)")
print(f"    B*N_gen*pi/N_d? 4*3*pi/44 = {mp.nstr(12*mp.pi/44,8)} = 3pi/11 (EXACT: 12/44=3/11)")
print(f"  -> 3pi/11 = B*N_gen*pi/N_d : rho = B*N_gen/N_d = 12/44 = 3/11 (v13b identity, EXACT)")

print("="*72)
print("R1/R3 status (no new computation, restated)")
print("="*72)
print("  R1: Lambda_MS5 NLO 166.0064 vs core 166.0445: +0.023%, not exact -> NOT upgraded")
print("      (both closed qty; 0.023% = 0.0380 MeV; no simple ratio; docs/16 §6.1 note)")
print("  R3: sigma lattice tension: lattice sqrt(sigma)=445(6) vs 424.8 MeV (-3.0 sigma)")
print("      world self-discrepancy Regge 0.18 vs lattice 0.198 (~7%); kept open")

print("\nDONE")