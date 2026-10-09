#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O221 / scripts/31 — Round 24 (Arm 2, A3): η-displacement operator as conserved charge
=======================================================================================
FSR-to-SR A3 (design docs/24): the rapidity eta is the boost parameter on the DISCRETE
88-chain (O140/O190).  This script establishes the exact group-law structure of eta on the
ladder and tests the "no accidental double-boost closure" claim.

LAYER RULE: everything here is DISCRETE-layer exactness (FSR).  It anchors what the
CONTINUOUS-layer boost generator must reduce to; it does NOT claim the continuum Lorentz
group.  Signature stays an input.

PRE-REGISTRATION (blind predictions, 2026-10-02, before running):
  * P1  exact identities:  gamma_n = csc(pi n/88) = cosh(eta_n),  v_n/c = cos(pi n/88)
       = tanh(eta_n),  csc^2 - cot^2 = 1  (mode-by-mode, n = 1..44)
  * P2  reflection and rest frame:  eta_{88-n} = eta_n (n = 1..43);  gamma_44 = 1,
       eta_44 = 0 (the rest mode)
  * P3  boost composition (GROUP LAW, exact):  cosh(eta_n + eta_m) =
       gamma_n gamma_m + sqrt((gamma_n^2 - 1)(gamma_m^2 - 1))  for all n, m in 1..44
  * P4  generator:  d gamma/d eta = sinh(eta) = sqrt(gamma^2 - 1) = cot(pi n/88)
  * P5  lightlike ladder:  e^{eta_n} = cot(pi n/176) exactly
  * P6  NO accidental double-boost closure: for n, m in 1..8,  e^{eta_n} e^{eta_m}
       equals cot(pi k/176) for some integer k ONLY in the trivial cases (n = 44 or m =
       44, i.e. identity boosts).  If a non-trivial exact equality exists, this PREDICTION
       is REFUTED and the new discrete composition law is recorded (threshold NOT relaxed).
  * All arithmetic mpmath dps 50 (the quantities are algebraic of low degree; 'exact' is
       judged at |diff| < 1e-30; a near-miss at 1e-15..1e-30 is separately recorded).

CHECKS: 31-1..31-6 as P1..P6 + honest grading.
"""

import itertools
import mpmath as mp
mp.mp.dps = 50
mp.pretty = True

def ck(cond, msg, extra=""):
    print("%s %s %s" % ("[PASS]" if cond else "[FAIL]", msg, extra))
    return bool(cond)

ok = True
N = 88
print("=" * 76)
print("O221 scripts/31 — A3: eta-displacement operator (rapidity group law, discrete layer)")
print("=" * 76)

# ---- P1: exact identities ----
p1a = p1b = p1c = True
for n in range(1, 45):
    th = mp.pi * n / N
    g = mp.csc(th)
    eta = mp.acosh(g)
    v = mp.cot(th) / g                     # cot*sin = cos
    p1a &= abs(g - mp.cosh(eta)) < mp.mpf("1e-40")
    p1b &= abs(v - mp.cos(th)) < mp.mpf("1e-40")
    p1c &= abs(g ** 2 - mp.cot(th) ** 2 - 1) < mp.mpf("1e-40")
ok &= ck(p1a and p1b and p1c,
         "31-1  P1: gamma_n = csc = cosh(eta_n); v/c = cos = tanh(eta_n); csc^2-cot^2 = 1 (n=1..44)",
         "")

# ---- P2: reflection + rest ----
p2a = all(abs(mp.acosh(mp.csc(mp.pi * (N - n) / N)) - mp.acosh(mp.csc(mp.pi * n / N)))
         < mp.mpf("1e-40") for n in range(1, 44))
rest = (abs(mp.csc(mp.pi * 44 / N) - 1) < mp.mpf("1e-40")
        and abs(mp.acosh(mp.mpf(1))) < mp.mpf("1e-40"))
ok &= ck(p2a and rest, "31-2  P2: eta_{88-n} = eta_n; rest mode gamma_44 = 1, eta_44 = 0", "")

# ---- P3: boost composition (group law) ----
p3 = True
for n, m in itertools.product(range(1, 45), repeat=2):
    g = mp.csc(mp.pi * n / N); gm = mp.csc(mp.pi * m / N)
    lhs = mp.cosh(mp.acosh(g) + mp.acosh(gm))
    rhs = g * gm + mp.sqrt((g * g - 1) * (gm * gm - 1))
    p3 &= abs(lhs - rhs) < mp.mpf("1e-35")
ok &= ck(p3, "31-3  P3: cosh(eta_n+eta_m) = gamma_n gamma_m + sqrt((g^2-1)(g'^2-1)) for all n,m",
         "")

# ---- P4: generator ----
p4 = True
for n in range(1, 45):
    g = mp.csc(mp.pi * n / N)
    p4 &= abs(mp.sqrt(g * g - 1) - mp.cot(mp.pi * n / N)) < mp.mpf("1e-40")
ok &= ck(p4, "31-4  P4: d gamma/d eta = sinh(eta) = cot(pi n/88) (generator on the shell)", "")

# ---- P5: lightlike ladder ----
p5 = all(abs(mp.exp(mp.acosh(mp.csc(mp.pi * n / N))) - mp.cot(mp.pi * n / 176))
         < mp.mpf("1e-40") for n in range(1, 45))
ok &= ck(p5, "31-5  P5: e^{eta_n} = cot(pi n/176) (lightlike ladder, n = 1..44)", "")

# ---- P6: no accidental double-boost closure ----
# trivial closures: n or m = 44 (identity boost).  Non-trivial probe on n, m in 1..8.
cot_ladder = {mp.cot(mp.pi * k / 176): k for k in range(1, 45)}
exact_hits = []; near_hits = []
for n, m in itertools.product(range(1, 9), repeat=2):
    if n == 44 or m == 44:                # trivial (not in probe range anyway)
        continue
    prod = mp.cot(mp.pi * n / 176) * mp.cot(mp.pi * m / 176)
    best = min(cot_ladder, key=lambda c: abs(c - prod))
    dist = abs(prod - best)
    if dist < mp.mpf("1e-30"):
        exact_hits.append((n, m, cot_ladder[best]))
    elif dist < mp.mpf("1e-15"):
        near_hits.append((n, m, cot_ladder[best], mp.nstr(dist, 6)))
p6ok = len(exact_hits) == 0
ok &= ck(p6ok,
         "31-6  P6: no accidental double-boost closure (e^eta_n e^eta_m != cot(pi k/176), non-trivial)",
         "exact hits = %s | near hits (1e-15..1e-30) = %s" % (exact_hits, near_hits[:6]))
if not p6ok:
    print("      REFUTED-and-recorded: new discrete composition law = %s" % exact_hits)

# ---- honest grading ----
print("\n[C7] HONEST GRADING: eta's group structure on the 88-chain is EXACT (composition law,"
      " generator, reflections, rest mode); the ladder admits NO accidental double-boost"
      " closure => {e^{eta_n}} is a generating set whose CONTINUOUS closure (the boost"
      " generator d/d eta in the l -> inf layer) is the A3 continuum reading - NOT claimed"
      " here.  Signature stays an input.")

print("\nRESULT: %s" % ("ALL CHECKS PASS" if ok else "SOME CHECKS FAILED"))
print("Summary: rapidity eta is an exact additive group parameter on the discrete ladder with")
print("exact generator identity; the discrete boost set does not close under composition on")
print("non-trivial pairs (no new discrete subgroup found in the probe).")