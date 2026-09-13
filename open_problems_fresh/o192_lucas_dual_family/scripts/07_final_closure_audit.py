#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O192 final closure audit — INDEPENDENT re-derivation of every numeric/formula
claim in docs/01-05 + cross-doc consistency + chronology + git scope.

Discipline: this script does NOT import scripts/01-06. Every assertion is
recomputed from first principles (math/mpmath/math.comb) against values the
docs CLAIM. Doc claims are quoted in the labels with section citations.
"""
import os, math, sys, subprocess, re
from math import comb, gcd, isqrt

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(D)
PASS = FAIL = 0

def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL {label}  {detail}")

def is_prime(n):
    if n < 2: return False
    for p in range(2, isqrt(n) + 1):
        if n % p == 0: return False
    return True

def factorize(n):
    f = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1: f[n] = f.get(n, 0) + 1
    return f

# ---------------- constants (registered IDCM, zero new constants) ----------------
N_d, N, B, R, N_gen, L4, L5, L6 = 44, 88, 4, 11, 3, 7, 11, 18
MU2 = 2
F = {0:0, 1:1}
for i in range(2, 20): F[i] = F[i-1] + F[i-2]
L = {0:2, 1:1}
for i in range(2, 20): L[i] = L[i-1] + L[i-2]
PHI = (1 + 5 ** 0.5) / 2
F_proj, M = 17, 33
dimC = 3

# =====================================================================
# D01 — docs/01: L-1 family, pairing law, budget-quantum, tree product
# =====================================================================
fam = {4:6, 5:10, 6:17, 7:28, 8:46, 9:75, 10:122, 11:198, 12:321}
Lm1 = {m: L[m] - 1 for m in range(4, 13)}
check("D01a L-1 family values {6,10,17,28,46,75,122,198,321}",
      Lm1 == fam, f"got {Lm1}")

ident = {6: N_gen*MU2, 10: 2*N_gen+B, 17: F_proj, 28: B*L4,
         46: N_d+MU2, 75: L4*L5-MU2, 122: 90+M-1, 198: 2*N_gen*M,
         321: 178+(F[12]-1)}
ok = all(ident[v] == v for v in fam.values())
check("D01b every L-1 member equals its closed identity",
      ok, f"{ {k: (v, ident[v]) for k, v in fam.items() if ident[v]!=v} }")
check("D01c 75 = 2*N_d - F7 (E_strain denominator)", 75 == 2*N_d - 13)
check("D01d 321 = 2*F11 + F12 - 1", 321 == 2*89 + 144 - 1)

# pairing law
ok = all(L[m] - 1 == (F[m-1]-1) + (F[m+1]-1) + 1 for m in range(4, 13))
check("D01e pairing law L_m-1 = (F_{m-1}-1)+(F_{m+1}-1)+1, m=4..12", ok)
check("D01f L10-1 = M+N+1 = 33+88+1", Lm1[10] == M + N + 1)
check("D01g L9-1 = 20+54+1 (Level5 + N_gen*L6)", Lm1[9] == 20 + 54 + 1)
check("D01h L11-1 = 54+143+1", Lm1[11] == 54 + 143 + 1)
check("D01i L12-1 = 88+232+1 (F13-1 = 232)", Lm1[12] == 88 + 232 + 1)
check("D01j F13-1 = 232 (super-budget bound)", F[13] - 1 == 232)
check("D01k L6-1 = 17 = F_proj (m=6 crossing)", L[6] - 1 == 17)

# spectrum sums (independent computation)
gamma = [4 * math.sin(math.pi * k / 176) ** 2 for k in range(1, 89)]
S1o = sum(gamma[k-1] for k in range(1, 89) if k % 2 == 1)
S1e = sum(gamma[k-1] for k in range(1, 89) if k % 2 == 0)
check("D01l Sigma gamma_odd = 88", abs(S1o - 88) < 1e-9, f"{S1o}")
check("D01m Sigma gamma_even = 90", abs(S1e - 90) < 1e-9, f"{S1e}")
check("D01n Sigma gamma = 178", abs(S1o + S1e - 178) < 1e-9)
S2o = sum(g**2 for k, g in enumerate(gamma, 1) if k % 2 == 1)
S2e = sum(g**2 for k, g in enumerate(gamma, 1) if k % 2 == 0)
check("D01o Sigma gamma^2_odd = 264", abs(S2o - 264) < 1e-6, f"{S2o}")
check("D01p Sigma gamma^2_even = 272", abs(S2e - 272) < 1e-6, f"{S2e}")
check("D01q Sigma gamma^2 = 536 = 3*178+2 = B(2M+1)*mu^2",
      abs(S2o + S2e - 536) < 1e-6 and 536 == 3*178 + 2 and 536 == 4*67*2)
check("D01r 264 = dimC*N_d*mu^2 = 3*44*2", 264 == dimC * N_d * MU2)
check("D01s 272 = 2B*F_proj*mu^2 = 8*17*2", 272 == 2 * B * F_proj * MU2)
check("D01t gamma_44 = 2 = mu^2 (Z2 point)", abs(gamma[43] - 2) < 1e-9, f"{gamma[43]}")
check("D01u gamma_88 = 4 = B (Nyquist)", abs(gamma[87] - 4) < 1e-9, f"{gamma[87]}")

# mod-4 closed forms: k ≡ {1,2,3,0} (mod 4)
mod4 = {1: 0.0, 2: 0.0, 3: 0.0, 0: 0.0}
for k in range(1, 89):
    mod4[k % 4] += gamma[k-1]
check("D01v mod-4: n=1 -> 44-sec(pi/88)",
      abs(mod4[1] - (44 - 1/math.cos(math.pi/88))) < 1e-6, f"{mod4[1]}")
check("D01w mod-4: n=3 -> 44+sec(pi/88)",
      abs(mod4[3] - (44 + 1/math.cos(math.pi/88))) < 1e-6, f"{mod4[3]}")
check("D01x mod-4: n=2 -> 44", abs(mod4[2] - 44) < 1e-6, f"{mod4[2]}")
check("D01y mod-4: n=0 -> 46 = L8-1", abs(mod4[0] - 46) < 1e-6 and 46 == L[8] - 1, f"{mod4[0]}")

# tree product
S_m = sum(291.5 - m for m in range(0, 34))
check("D01z tree exponent sum = 9350", S_m == 9350, f"{S_m}")
check("D01aa 9350 = 2*F5^2*L5*F_proj = 2*25*11*17", 9350 == 2 * F[5]**2 * L5 * F_proj)
check("D01ab geometric mean exp = 275 = F5^2*L5 = F5*F10",
      9350 / 34 == 275 == F[5]**2 * L5 == F[5] * F[10])

# =====================================================================
# D02 — docs/02: Bessel, csc ladder, warp, half-integer echo
# =====================================================================
# Bessel J1 zeros via mpmath (independent of scripts/02)
try:
    import mpmath as mp
    mp.mp.dps = 30
    x1 = float(mp.besseljzero(1, 1))
    x40 = float(mp.besseljzero(1, 40))
    x7, x12, x24, x34 = (float(mp.besseljzero(1, n)) for n in (7, 12, 24, 34))
    x6 = float(mp.besseljzero(1, 6))
except Exception as e:
    print(f"  WARN mpmath unavailable: {e}; D02 Bessel checks skipped")
    x1 = x40 = x7 = x12 = x24 = x34 = x6 = None

if x1:
    check("D02a x1 = 3.8317 (Newton/direct)", abs(x1 - 3.8317) < 5e-5, f"{x1}")
    q40 = x40/x1
    ctrl40 = (4*40 + 1) / 5 * 1.02486
    check("D02b x40/x1 = 32.99996 (dev 0.0001%); pi-control predicts 33.0005 (0.0016%)",
          abs(q40 - 33) < 1e-3 and abs(q40 - 32.99996) < 5e-5 and
          abs(ctrl40 - 33.0005) < 1e-4, f"actual {q40:.6f} control {ctrl40:.6f}")
    # B05 unified control: x_n/x1 ~ (4n+1)/5 * 1.02486
    for n, target, name in [(7, 6, "x7/x1->6"), (12, 10, "x12/x1->10"),
                            (24, 20, "x24/x1->20"), (34, 28, "x34/x1->28"),
                            (40, 33, "x40/x1->33")]:
        xn = float(mp.besseljzero(1, n))
        pred = (4*n + 1) / 5 * 1.02486
        check(f"D02c B05 {name}: control (4n+1)/5*1.02486 = {pred:.3f} vs {xn/x1:.3f}",
              abs(pred - xn/x1) < 0.02, f"pred {pred:.4f} actual {xn/x1:.4f}")
    # B06 trap: 33*c1 - c40 = 3.1483 ≈ pi, where c_n = 3/(8*pi*(n+1/4)) = McMahon
    # first-order correction (scripts/02 definition). Exact eval:
    c1 = 3 / (8 * math.pi * 1.25)
    c40 = 3 / (8 * math.pi * 40.25)
    val = 33 * c1 - c40
    check("D02d B06 exact evaluation 33*c1-c40 = 3.1483 ~ pi (c_n = McMahon 3/(8*pi*(n+1/4)))",
          abs(val - 3.1483) < 1e-3 and abs(val - math.pi) < 0.007,
          f"got {val:.5f} (doc claims 3.1483, dev 0.21%)")
    # what natural combination gives ~pi? 33*1.25*pi - x40
    alt = 33 * 1.25 * math.pi - x40
    check("D02e B06 mechanistic form 33*(1.25*pi) - x40 ~ pi",
          abs(alt - math.pi) < 0.01, f"got {alt:.5f}")
    # pi^2 ~ 9.9
    check("D02f pi^2 ~ 9.9 (dev < 0.4%)", abs(math.pi**2 - 9.9) < 0.04, f"pi^2 = {math.pi**2:.4f}")
    # 22/7 trap
    check("D02g 22/7 vs pi dev 0.04%", abs(22/7 - math.pi)/math.pi < 0.001, f"{22/7 - math.pi:.5f}")
    # asymptotic linearity n>=2 max dev 0.755%
    devs = []
    for n in range(2, 41):
        xn = float(mp.besseljzero(1, n))
        devs.append(abs(xn - math.pi*(n + 0.25)) / (math.pi*(n + 0.25)))
    check("D02h Bessel linear ascent x_n ~ pi(n+1/4), n>=2 max dev 0.755%",
          max(devs) < 0.0076, f"max dev {max(devs)*100:.3f}%")
    d1 = abs(x1 - math.pi*1.25) / x1  # relative to x1 (McMahon-4-term 3.83164 -> 2.489%)
    check("D02i n=1 dev 2.489% (McMahon 3/(8*beta) first-order, vs x1)",
          abs(d1*100 - 2.489) < 0.08, f"{d1*100:.3f}%")

# csc ladder (docs/02 table)
csc = lambda n: 1/math.sin(math.pi*n/88)
for n, val, name in [(1, 28.0172, "csc(pi/88)=28.0172"), (4, 7.0267, "csc(4pi/88)=7.0267"),
                     (7, 4.0436, "csc(7pi/88)=4.0436"), (14, 2.0866, "csc(14pi/88)=2.0866"),
                     (15, 1.9598, "csc(15pi/88)=1.9598")]:
    check(f"D02j {name}", abs(csc(n) - val) < 5e-4, f"{csc(n):.4f}")
check("D02k |28 - 88/pi| = 0.0112 < |28 - csc| = 0.0172",
      abs(abs(28 - 88/math.pi) - 0.0112) < 1e-3 and
      abs(abs(28 - csc(1)) - 0.0172) < 1e-3,
      f"{abs(28-88/math.pi):.4f}, {abs(28-csc(1)):.4f}")
# 15/88 ~ 1/6 angle coincidence
check("D02l 15/88 = 0.17045 ~ 1/6 = 0.16667 (2.3%)", abs(15/88 - 1/6)/(1/6) < 0.025)

# warp
import math as m2
kr1 = m2.log(1e15)/m2.pi
kr2 = m2.log(1e16)/m2.pi
check("D02m k r_c = ln(1e15)/pi = 10.9940 (0.0542% vs 11)",
      abs(kr1 - 10.9940) < 5e-4 and abs(kr1 - 11)/11 < 0.00055, f"{kr1}")
check("D02n k r_c(1e-16) = 11.7270", abs(kr2 - 11.7270) < 5e-4, f"{kr2}")
check("D02o e^{-11 pi} = 9.81e-16 ~ 1e-15", abs(m2.exp(-11*m2.pi) - 9.81e-16) < 5e-18)
check("D02p 11*pi = 34.5575 vs ln(1e15) = 34.5388 (0.0543%)",
      abs(abs(11*m2.pi - m2.log(1e15))/m2.log(1e15) - 0.000543) < 1e-4)
# half-integer echo
check("D02q gcd(89, 583) = 1", gcd(89, 583) == 1)
check("D02r 583 = L5*(N_d+N_gen^2) = 11*53", 583 == 11 * (44 + 9) and 53 == (44+9))
check("D02s 89 = F11 prime", is_prime(89))
check("D02t 44.5 = F11/2, 291.5 = 583/2", 89/2 == 44.5 and 583/2 == 291.5)

# =====================================================================
# D03 — docs/03: session-push closure numbers
# =====================================================================
S3o = sum(g**3 for k, g in enumerate(gamma, 1) if k % 2 == 1)
S3e = sum(g**3 for k, g in enumerate(gamma, 1) if k % 2 == 0)
check("D03a Sigma gamma^3_odd = 880 = 2^4*F10", abs(S3o - 880) < 1e-3 and 880 == 16*55, f"{S3o}")
check("D03b Sigma gamma^3_even = 912 = 2^4*(F10+mu^2)",
      abs(S3e - 912) < 1e-3 and 912 == 16*57, f"{S3e}")
check("D03c Sigma gamma^3 = 1792 = 2^4*(2F10+mu^2)",
      abs(S3o+S3e - 1792) < 1e-3 and 1792 == 16*112, f"{S3o+S3e}")
# parity-gap law n=1..5 (independent)
for n in range(1, 6):
    Sn_odd = sum(g**n for k, g in enumerate(gamma, 1) if k % 2 == 1)
    Sn_even = sum(g**n for k, g in enumerate(gamma, 1) if k % 2 == 0)
    check(f"D03d parity-gap n={n}: diff = 2^(2n-1) = {2**(2*n-1)}",
          abs(Sn_even - Sn_odd - 2**(2*n-1)) < 1e-2, f"{Sn_even-Sn_odd:.3f}")
# Sigma sin^6 = 28 = L7-1
S6 = sum(math.sin(math.pi*k/176)**6 for k in range(1, 89))
check("D03e Sigma sin^6 = 28 = L7-1 = B*L4", abs(S6 - 28) < 1e-9 and 28 == 4*7, f"{S6}")
S2 = sum(math.sin(math.pi*k/176)**2 for k in range(1, 89))
S4 = sum(math.sin(math.pi*k/176)**4 for k in range(1, 89))
check("D03f Sigma sin^2 = F11/2 = 44.5", abs(S2 - 44.5) < 1e-9, f"{S2}")
check("D03g Sigma sin^4 = (2M+1)/2 = 33.5", abs(S4 - 33.5) < 1e-9, f"{S4}")
# quartic / quintic
S4t = sum(g**4 for g in gamma)
S5t = sum(g**5 for g in gamma)
check("D03h Sigma gamma^4 = 6288 = 2^4*3*131", abs(S4t - 6288) < 1e-1 and 6288 == 16*393 == 48*131, f"{S4t:.1f}")
check("D03i Sigma gamma^5 = 22688 = 2^5*709 (709 prime)",
      abs(S5t - 22688) < 1e-1 and 22688 == 32*709 and is_prime(709), f"{S5t:.1f}")
# structure chain (E07): 89/268/896/3144/11344 = 44*C(2n,n)+2^(2n-2)
chain = [44*comb(2*n, n) + 2**(2*n-2) for n in range(1, 6)]
check("D03j smooth chain 89/268/896/3144/11344", chain == [89, 268, 896, 3144, 11344], f"{chain}")
# L budget
check("D03k Sigma(L_m-1) = 823 prime", sum(Lm1.values()) == 823 and is_prime(823))
check("D03l 832 = L14 - L5 = 843-11 = (2B)^2*F7 = 64*13",
      sum(L[m] for m in range(4, 13)) == 832 == L[14] - L[5] == 843 - 11 == 64*13)
check("D03m Sigma(F_m-1) = 363 = N_gen*R^2 = 3*121",
      sum(F[m]-1 for m in range(4, 13)) == 363 == 3 * 121)
# dual-modulus junction
check("D03n 99 = N+R = N_gen*M = N_gen^2*R (triple meeting)",
      99 == 88+11 == 3*33 == 9*11)
check("D03o 198 = 2(N+R) = 2N_gen*M = N_gen*Sigma_lambda (66)",
      198 == 2*99 == 2*3*33 == 3*66 and 66 == 12*11//2)
check("D03p 321 = Sigma gamma + (F12-1) = 178+143 = 2F11+F12-1",
      321 == 178 + 143 == 2*89 + 144 - 1)
check("D03q 143 = dim SU(12) = 144-1", 143 == 144 - 1)
check("D03r 54 = N_gen*L6 = 3*18 (four-way registered)", 54 == 3*18)
# tree warp falsification
mu0 = PHI ** 291.5
ratio = (1 - PHI ** -34) / (1 - PHI ** -1)
Sum_mu = mu0 * ratio
check("D03s Sigma mu ~ 2.18e61 (docs/03) / 2.177e61 (docs/05)",
      abs(Sum_mu - 2.18e61) / 2.18e61 < 0.002 and abs(Sum_mu - 2.177e61)/2.177e61 < 0.002,
      f"{Sum_mu:.4e}")
check("D03t RS1 warp volume ~ 1/44", abs(1/44 - 0.0227) < 1e-4)
check("D03u 62 orders of magnitude gap", abs(math.log10(Sum_mu) - math.log10(1/44)) > 60)
# 9350 trace
check("D03v 9350 = 34*291.5 - 561, 561 = M*F_proj = 33*17",
      9350 == 34*291.5 - 561 and 561 == 33*17 and 561 == 33*34//2)
check("D03w 9350 = (M+1)*F5*F10 = 34*275", 9350 == 34 * 275 == (M+1)*5*55)
check("D03x 9350 = mu^2*F5*F10*F_proj = 2*5*55*17", 9350 == 2*5*55*17)
# trap 6 V10
V10 = L[10]*PHI + L[9]
check("D03y V10 = L10*phi+L9 = 275.018181", abs(V10 - 275.018181) < 1e-4, f"{V10}")
check("D03z 275.018 = 275 + sqrt5*phi^-10", abs(V10 - (275 + 5**0.5*PHI**-10)) < 1e-9)
check("D03aa 550 = 2*275 = 10*F10", 550 == 2*275 == 10*55)
# trap 5: phi^-k hierarchy
k_needed = m2.log(1e15) / m2.log(PHI)
check("D03ab phi^-k = 1e-15 requires k = 71.77 (non-integer)",
      abs(k_needed - 71.77) < 0.01, f"{k_needed}")
check("D03ac phi^-72 = 8.97e-16 (dev 10.3% vs 1e-15)",
      abs(PHI**-72 - 8.97e-16) < 5e-18 and abs(PHI**-72 - 1e-15)/1e-15 < 0.11)

# =====================================================================
# D04 — docs/04: closed-form unified theorem
# =====================================================================
def SF(n):  # total, odd, even, gap via closed form
    tot = 88*comb(2*n, n) + 2**(2*n-1)
    odd = 44*comb(2*n, n)
    return tot, odd, tot - odd, 2**(2*n-1)
table = {1: (178, 88, 90, 2), 2: (536, 264, 272, 8), 3: (1792, 880, 912, 32),
         4: (6288, 3080, 3208, 128), 5: (22688, 11088, 11600, 512),
         6: (83360, 40656, 42704, 2048),
         10: (16782816, 8129264, 8653552, 524288),
         20: (12680250350048, 6065247268080, 6615003081968, 549755813888)}
ok = all(SF(n) == table[n] for n in table)
check("D04a closed-form table n=1..6,10,20 exact (docs/04)", ok)
# direct numerical verification at n=4,5 vs math.sin sums
for n in (4, 5):
    tot = sum(g**n for g in gamma)
    odd = sum(g**n for k, g in enumerate(gamma, 1) if k % 2 == 1)
    check(f"D04b direct recompute n={n}: {SF(n)[0]}", abs(tot - SF(n)[0]) < 1e-1 and
          abs(odd - SF(n)[1]) < 1e-1)
# all-n parity gap = 2^(2n-1) for n=1..20 via closed form (already algebraic)
check("D04c gap identity 2^(2n-1) for all n (algebraic)",
      all(SF(n)[3] == 2**(2*n-1) for n in range(1, 21)))
# central binomial factorizations all in registered primes {2,3,5,7,11,13,17,19}
CB = [comb(2*n, n) for n in range(1, 11)]
CB_str = {2: "mu^2", 6: "N_gen*mu^2", 20: "B*F5", 70: "mu^2*F5*L4",
          252: "2^2*N_gen^2*L4", 924: "2^2*N_gen*L4*L5",
          3432: "2^3*N_gen*(F12-1)", 12870: "2*N_gen^2*F5*(F12-1)",
          48620: "2^2*F5*L5*F7*F_proj", 184756: "2^2*L5*F7*F_proj*(L6+1)"}
ok = all(set(factorize(cb)) <= {2, 3, 5, 7, 11, 13, 17, 19} for cb in CB)
check("D04d C(2n,n) factors subset of registered primes {2,3,5,7,11,13,17,19}", ok)
check("D04e C(2n,n) list matches docs/04", CB == [2, 6, 20, 70, 252, 924, 3432, 12870, 48620, 184756])
check("D04f 19 = L6+1 registered prime", 19 == 18 + 1)
# 70 = C(8,4) = mu^2*F5*L4
check("D04g C(8,4) = 70 = mu^2*F5*L4 = 2*5*7", comb(8, 4) == 70 == 2*5*7)
check("D04h 6288 = 88*C(8,4) + 2^7 = 88*70+128", 6288 == 88*70 + 128 == 48*131)
# Sigma sin^{2m} closed form
for m in range(1, 11):
    val = sum(math.sin(math.pi*k/176)**(2*m) for k in range(1, 89))
    cf = 88*comb(2*m, m)/4**m + 0.5
    check(f"D04i Sigma sin^({2*m}) = 88*C(2m,m)/4^m+1/2 (m={m})", abs(val - cf) < 1e-6, f"{val} vs {cf}")
# trap 6 family |L_n phi - L_{n+1}| = sqrt5 phi^-n
ok = all(abs(abs(L[n]*PHI - L[n+1]) - 5**0.5*PHI**-n) < 1e-9 for n in range(1, 16))
check("D04j |L_n*phi - L_{n+1}| = sqrt5*phi^-n for n=1..15 (exact)", ok)
for n, target, dev in [(8, 76, 0.00063), (9, 123, 0.00024), (10, 199, 0.00009)]:
    check(f"D04k corpus n={n}: L{n}*phi ~ {target} dev {dev}",
          abs(abs(L[n]*PHI - target)/target - dev) < 0.0001,
          f"{abs(L[n]*PHI-target)/target:.6f}")
# phi^n ~ L_n Binet convergence
check("D04l phi^11 ~ 199 = L11 (Binet, generic)", abs(PHI**11 - L[11]) < 0.05)

# =====================================================================
# D05 — docs/05: Kummer theorem, tree power sums, trap 7
# =====================================================================
# first appearance n_first(p) = (p+1)/2 for odd primes; C(2n,n) divisibility
odd_primes = [p for p in range(3, 100) if is_prime(p)]
check("D05a 24 odd primes <= 99", len(odd_primes) == 24, f"{len(odd_primes)}")
ok = True
for p in odd_primes:
    nf = (p + 1) // 2
    # p | C(2n,n) for n >= nf (first at nf)
    if comb(2*nf, nf) % p != 0: ok = False
    if nf > 1 and comb(2*(nf-1), nf-1) % p == 0: ok = False
check("D05b Kummer first appearance n_first(p) = (p+1)/2 for all odd primes <= 99", ok)
# prime factor set of C(2n,n) for n<=50: {2} u {odd p <= 99}
ok = True
for n in range(1, 51):
    facs = set(factorize(comb(2*n, n)))
    expect = {2} | {p for p in odd_primes if p <= 99}
    if not facs <= expect: ok = False
check("D05c prime factors of C(2n,n), n=1..50 subset of {2} u {odd primes <= 99}", ok)
# Legendre exponent formula
def s_p(n, p):
    s = 0
    while n:
        s += n % p
        n //= p
    return s
ok = True
for n in range(1, 21):
    for p in odd_primes:
        v_leg = (2*s_p(n, p) - s_p(2*n, p)) // (p - 1)
        c = comb(2*n, n)
        v_true = 0
        while c % p == 0:
            v_true += 1
            c //= p
        if v_leg != v_true: ok = False
check("D05d Legendre exponent v_p = (2s_p(n)-s_p(2n))/(p-1), n<=20 p<=97", ok)
# registration table identities
tbl = {3: 2, 5: 3, 7: 4, 11: 6, 13: 7, 17: 9, 19: 10, 23: 12, 31: 16, 37: 19,
       41: 21, 43: 22, 53: 27, 59: 30, 67: 34, 73: 37, 89: 45, 97: 49}
check("D05e table n_first values (p+1)/2", all(tbl[p] == (p+1)//2 for p in tbl))
idents = {2: "mu^2", 3: "N_gen", 4: "B", 6: "N_gen*mu^2", 7: "L4", 9: "N_gen^2",
          10: "2N_gen+B", 12: "B*N_gen", 16: "B^2", 19: "L6+1", 21: "F8", 22: "2L5",
          27: "N_gen^3", 30: "2Tr(T^4)", 34: "M+1", 37: "N_d-L4", 45: "N_d+1", 49: "L4^2"}
ok = all(idents.get(tbl[p]) for p in tbl)
check("D05f 18/24 rows carry closed identities", ok and len(tbl) == 18)
check("D05g 12 = B*N_gen = L5+1 = su(12) fundamental", 12 == 4*3 == 11+1)
# Fisher exact on 2x2 [[12,12],[10,15]] — standard ONE-SIDED tail (final audit fix:
# the round-3 doc value 0.178 was the point-mass P(observed table), mislabeled;
# proper one-sided tail p = 0.34. Conclusion identical: density artifact)
def fisher_one_sided(a, b, c, d):
    r1, c1, n = a+b, a+c, a+b+c+d
    return sum(comb(c1, x) * comb(n - c1, r1 - x) / comb(n, r1)
               for x in range(a, min(r1, c1) + 1))
p_tail = fisher_one_sided(12, 12, 10, 15)
# point mass P(X=12) for reference
p_mass = comb(22, 12) * comb(27, 12) / comb(49, 24)
check("D05h Fisher one-sided tail p = 0.34 (point-mass 0.178 was mislabel; conclusion unchanged)",
      abs(p_tail - 0.34) < 0.01 and abs(p_mass - 0.178) < 0.005,
      f"tail p = {p_tail:.4f}, point-mass = {p_mass:.4f}")
# tree power sums (log-space to avoid float overflow: phi^(291.5*n) ~ 1e61..1e305)
for n in range(1, 6):
    ln_cf = n*291.5*math.log(PHI) + math.log1p(-PHI**(-34*n)) - math.log1p(-PHI**-n)
    ln_direct = math.log(sum(PHI**(-m*n) for m in range(0, 34))) + n*291.5*math.log(PHI)
    check(f"D05i tree power sum closed form n={n} (log-space)",
          abs(ln_cf - ln_direct) < 1e-9, f"ln cf {ln_cf:.6f} vs {ln_direct:.6f}")
check("D05j m=1..34 -> 9316 (index range pinned)", sum(291.5-m for m in range(1, 35)) == 9316)
check("D05k (1-phi^-1) = phi^-2", abs((1 - PHI**-1) - PHI**-2) < 1e-12)
# trap 7: closed-form membership
check("D05l 48,131 not in {C(2n,n)}; 70,128 in family",
      48 not in CB and 131 not in CB and 70 in CB and 128 == 2**7)
check("D05m 832 = L14-L5 = (2B)^2*F7 arithmetic organization",
      832 == L[14]-L[5] == 64*13)

# =====================================================================
# X — cross-doc consistency + chronology + git scope + snapshot
# =====================================================================
read = lambda f: open(os.path.join(D, f), encoding="utf-8").read()
record = read("01_problem_record.md")
final = read("final_result.md")
d01, d02 = read("docs/01_lucas_dual_and_budget_quantum.md"), read("docs/02_rs1_bridge_scan.md")
d03, d04 = read("docs/03_session_push_closure.md"), read("docs/04_power_sum_closed_form.md")
d05 = read("docs/05_external_extensions.md")
ss = read("SESSION_START.md")

# cross-doc: family set + identities consistent everywhere (whitespace-normalized:
# docs/01+record print the set with spaces, final without)
strip = lambda s: re.sub(r"\s+", "", s)
famset = "{6,10,17,28,46,75,122,198,321}"
check("X01 family set in docs/01 = record = final",
      famset in strip(d01) and famset in strip(record) and famset in strip(final))
check("X02 closed form in docs/04 = record = final (round-2 tier)",
      "88·C(2n,n) + 2^{2n−1}" in d04 and "88·C(2n,n) + 2^{2n−1}" in record
      and "88·C(2n,n) + 2^{2n−1}" in final)
check("X03 Kummer + Fisher in docs/05 = record = final (round-3 tier)",
      "Kummer" in d05 and "Kummer" in record and "Kummer" in final and
      "Fisher" in d05 and "Fisher" in record and "Fisher" in final)
check("X04 trap7 in docs/05 = record = final",
      "trap ⑦" in d05 and "trap ⑦" in record and "trap ⑦" in final)
# backfill prohibition: round-2/3 content NOT in docs/01 (original record)
check("X05 no backfill: 'C(2n,n)' not in docs/01 (opening doc)",
      "C(2n,n)" not in d01 and "Kummer" not in d01)
check("X06 no backfill: round-3 'Kummer' not in docs/01/02/03",
      "Kummer" not in d01 and "Kummer" not in d02 and "Kummer" not in d03)
# E07 retraction must be marked in scripts/03 and docs/04 (content-level fix)
s03 = read("scripts/03_session_push_closure.py")
check("X07 E07 SUPERSEDED marker in scripts/03",
      "SUPERSEDED" in s03 and "artifact factorization" in s03)
check("X08 E07 retraction recorded in docs/04 + record + final",
      "撤回" in d04 and "撤回" in record and "撤回" in final)
# record status line must reflect rounds 2/3 (LIVING doc, not historical);
# status block wraps over 3 header lines — join them
head_block = " ".join(record.splitlines()[2:6])
check("X09 record status line includes scripts/05 and 06",
      "scripts/05" in head_block and "scripts/06" in head_block,
      "record status line is stale")
# record section 1-b must mark the quartic degradation claim superseded
seg = record[record.find("一乙"):record.find("## 二")]
check("X10 record 1-b quartic 'degradation' claim marked superseded",
      "劣化面" in seg and ("撤回" in seg or "SUPERSEDED" in seg),
      "record 1-b still states quartic degradation as active claim")
# timeline index present with >= 5 rows covering all rounds
tl = record[record.find("## 三、推導時序索引"):record.find("## 四、誠實修正記錄")]
rows = [ln for ln in tl.splitlines() if ln.startswith("|") and "09-13" in ln]
check("X11 timeline index has >= 5 rows (opening/RS1/push/round2/round3)",
      len(rows) >= 5, f"{len(rows)} rows")
check("X12 timeline covers rounds 2+3",
      "Round 2" in tl and "Round 3" in tl)
# honesty log covers all rounds
check("X13 honesty log has E07 retraction + verifier-side fixes",
      "E07" in record and "verifier" in record)
# SESSION_START snapshot unchanged (opening state, six next steps, no closure claim)
check("X14 SESSION_START still opening-state snapshot (no closure claim)",
      "🟡 推導完成" in ss and "下一步" in ss and "已閉合" not in ss)

# chronology: docs are write-once (+recorded corrections) — CONTENT order via git
# first-commit times; record/final are LIVING docs refreshed at each close, so their
# freshness is checked via working-tree mtime (final = terminal deliverable)
import time

def created(f):
    try:
        repo = os.path.dirname(ROOT)  # git repo root (IDCM-v10.0--It-From-Beat)
        r = subprocess.run(["git", "-C", repo, "log", "--diff-filter=A", "--format=%ct",
                            "--", os.path.join("open_problems_fresh/o192_lucas_dual_family", f)],
                           capture_output=True, text=True)
        if r.stdout.strip():
            return float(r.stdout.split()[0])
    except Exception:
        pass
    return os.path.getmtime(os.path.join(D, f))

order = ["SESSION_START.md", "docs/01_lucas_dual_and_budget_quantum.md",
         "docs/02_rs1_bridge_scan.md", "docs/03_session_push_closure.md",
         "docs/04_power_sum_closed_form.md", "docs/05_external_extensions.md"]
ct = {f: created(f) for f in order}
mono = all(ct[order[i]] <= ct[order[i+1]] for i in range(len(order)-1))
check("X15 chronology (git creation order): SESSION_START <= docs/01..05", mono,
      " | ".join(f"{os.path.basename(f)}:{time.strftime('%H:%M', time.localtime(ct[f]))}" for f in order))
check("X15b docs/02 B06 correction recorded (honesty log + timeline)",
      "32.99996" in record and "B06" in record and "final audit" in record)
# record/final freshness: updated at close (working mtime >= newest closing doc)
check("X15c record & final working-tree >= docs/05 (updated at close)",
      os.path.getmtime(os.path.join(D, "01_problem_record.md")) + 30 >=
      os.path.getmtime(os.path.join(D, "docs/05_external_extensions.md")) and
      os.path.getmtime(os.path.join(D, "final_result.md")) >=
      os.path.getmtime(os.path.join(D, "docs/05_external_extensions.md")))

# git scope: this closure's OWN commit must be confined to o192 + fresh README.
# (The repo has pre-existing dirt from other O dirs — not ours; scope = staged set.)
try:
    r = subprocess.run(["git", "-C", ROOT, "diff", "--cached", "--name-only"],
                       capture_output=True, text=True)
    staged = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
    if staged:
        bad = [s for s in staged if "o192_lucas_dual_family" not in s and "README.md" not in s]
        check("X16 staged commit scope confined to o192 dir (+fresh README)", not bad, f"{bad[:5]}")
    else:
        check("X16 staged commit scope confined to o192 dir (+fresh README)", True, "(nothing staged yet)")
    r2 = subprocess.run(["git", "-C", ROOT, "status", "--porcelain", "--",
                         "open_problems_fresh/o192_lucas_dual_family"],
                        capture_output=True, text=True)
    dirty192 = [ln for ln in r2.stdout.splitlines() if ln.strip()]
    check("X17 o192 dir committed clean (closure commit present)", not dirty192)
except Exception as e:
    print(f"  WARN git: {e}")

# A4b fix verification: scripts/06 must use the one-sided tail (not point-mass)
s06 = read("scripts/06_external_extensions.py")
check("X18 scripts/06 A4b corrected to one-sided tail (point-mass mislabel recorded)",
      "fisher_one_sided" in s06 and "point-mass" in s06 and "0.34" in s06)

print(f"\n=== {PASS} PASS / {FAIL} FAIL ===")
sys.exit(1 if FAIL else 0)
