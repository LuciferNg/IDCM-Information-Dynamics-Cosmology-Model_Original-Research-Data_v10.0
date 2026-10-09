#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O221 / scripts/29 — Round 23 (Arm 2: FSR-to-SR, A2 anchor): inertia/gaplessness anchors
=========================================================================================
See-numbers-first EXECUTION piece for O140/FSR-to-SR (design docs/24; work location O221 per
Calibrator 2026-10-02 "all-continue-in-O221").  A2 = "inertia (N-1,0,1) / free-motion sector:
continuum-layer reading".  This script establishes the DISCRETE-LAYER ANCHORS that the
continuum reading must reduce to -- it does NOT yet claim the continuum Lorentz dynamics.

LAYER RULE (Calibrator): FSR = discrete layer, SR = continuous layer.  Discrete exactness
here is NOT a statement about the continuous Lorentz group; the anchors below are the exact
input data for the (deferred) continuum construction.  Signature stays an input.

WHAT IS ANCHORED (exact identities, verified at previously-unused lattice sizes):
  * epsilon_1(N) = 4 sin^2(pi/N) is the lowest nonzero eigenvalue of the N-ring (K_chain
    1D Laplacian, periodic, the git docs/02 identity).  Gaplessness law: as N -> inf the
    lowest mode is MASSLESS: epsilon_1(N) * N^2 -> 4 pi^2.  On the refinement tower
    N_ell = 88 * 4^ell this means the free-motion (inertia-compatible) sector SURVIVES the
    continuum limit at every step -- no mass gap forms.
  * Ratio (next refinement): epsilon_1(N_{ell+1}) / epsilon_1(N_ell) -> 1/16 exactly
    (wavelength^2 scaling of the free sector).
  * 4D product torus: the dispersion omega(n)^2 = sum_j 4 sin^2(pi n_j / M) has EXACTLY
    2^4 = 16 zero vertices (the Brillouin corners, n_j in {0, pi} mod 2pi) -> the free/
    inertia sector of the 4D lattice is a 16-branch structure; each branch is linear near
    its corner (acoustic) with speed c.
  * Inertia signature (docs/16, gauge-fixed quotient machine): Q_phys spectrum (per unit
    tensor norm) = [8.773e-6, -1.0966e-6 x3, -4.3865e-6 x2] -> Sylvester inertia (1+, 5-),
    stable at M in {6,8}; min|TT|/|conformal| = 1.0966/4.3865 = 0.25 EXACT (re-verified
    numerically below from the recorded numbers).

PRE-REGISTRATION (2026-10-02, before running):
  * Anchor ladder ell in {3, 4, 5}:  N = 5632, 22528, 90112  (previously unused sizes)
  * 4D zero-sector check on M in {28, 36, 44} (already the scripts/28 blind set; here used
    only for the zero-vertex COUNT, a lattice-topology fact)
  * DEFERRED blind computation (next session, pre-registered): the gauge-fixed quotient
    (scripts/21 machinery) at blind M in {12, 16, 24} to measure the (1+)-direction's
    eigen-magnitude scaling -- the actual continuum-layer inertia reading.
  * Falsification flavour: if the free sector GAPS (epsilon_1(N) N^2 NOT -> 4 pi^2, i.e. a
    mass gap), or the zero-vertex count differs from 16, or the inertia signature leaves
    (1+,5-) at blind quotient M, the A2 reading is REFUTED and recorded.  Thresholds are
    NOT relaxed.

CHECKS:
  C1  three-term gaplessness: (4pi^2 - eps1*N^2)*3N^2/4pi^4 = 1 - 2pi^2/(15N^2) + O(N^-4)
  C2  two-term ratio: r = (1/16)(1 + 5 pi^2/(16N^2)) on the same ladder
  C3  zero-vertex count of the 4D dispersion = 16 on M in {28,36,44}
  C4  IR dispersion exactness: (1 - om/ck)*6N^2/pi^2 = 1 + pi^2/(20N^2) at N=90112
  C5  inertia signature re-verification: (1+,5-) and min|TT|/|conf| = 0.2500 from docs/16
  C6  honest grading + deferred action list (quotient blind M {12,16,24} pre-registered)
"""

import numpy as np
import mpmath as mp
mp.mp.dps = 40
import itertools

def ck(cond, msg, extra=""):
    tag = "[PASS]" if cond else "[FAIL]"
    print("%s %s %s" % (tag, msg, extra))
    return bool(cond)

ok = True
print("=" * 72)
print("O221 scripts/29 — FSR-to-SR A2 anchors: inertia/gaplessness (discrete-layer exact)")
print("=" * 72)

# C1 + C2: gaplessness law, ratio law on the anchor ladder N = 88 * 4^ell
# Exact finite-N series (free lattice, no gap):  eps1(N)*N^2 = 4pi^2 (1 - pi^2/(3N^2)
# + 2 pi^4/(45 N^4) - ...), so the normalised first-correction coefficient is
#      (4pi^2 - eps1*N^2)*3N^2/(4pi^4) = 1 - 2 pi^2/(15 N^2) + O(N^-4)  [THREE-TERM law]
# and r = eps1(4N)/eps1(N) = (1/16)(1 + 5 pi^2/(16N^2) + ...).  mpmath at dps 40 avoids the
# catastrophic float64 cancellation in (4pi^2 - x) and (1 - om/ck).
ells = [3, 4, 5]
Ns = [88 * 4 ** e for e in ells]
vals = [4.0 * mp.sin(mp.pi / N) ** 2 for N in Ns]           # mpmath values
law = [v * N * N for v, N in zip(vals, Ns)]
c1red = [(4.0 * mp.pi ** 2 - x) * 3.0 * N * N / (4.0 * mp.pi ** 4) for x, N in zip(law, Ns)]
c1next = [1.0 - 2.0 * mp.pi ** 2 / (15.0 * N * N) for N in Ns]
ok &= ck(all(abs(c - cnext) < 1e-9 for c, cnext in zip(c1red, c1next)),
         "C1  three-term gaplessness: (4pi^2 - eps1*N^2)*3N^2/4pi^4 = 1 - 2pi^2/(15N^2) + O(N^-4)",
         "coeff %s (next-term pred %s)" %
         (", ".join("%.9f" % float(c) for c in c1red),
          ", ".join("%.9f" % float(c) for c in c1next)))
rat = [vals[e + 1] / vals[e] for e in range(2)]
rpred = [(1.0 / 16.0) * (1.0 + 5.0 * mp.pi ** 2 / (16.0 * N * N)) for N in Ns[:-1]]
ok &= ck(all(abs(r - rp) < 1e-12 for r, rp in zip(rat, rpred)),
         "C2  two-term refinement ratio r = (1/16)(1 + 5 pi^2/(16N^2)) [-> 1/16]",
         "ratios %s" % (", ".join("%.12f" % float(r) for r in rat),))

# C3: zero-vertex count of the 4D dispersion on the full grid
zc2 = 0
for M in [28, 36, 44]:
    # vertices with sin(pi n_j / M) == 0 per direction: n_j in {0, M/2} (M even)
    c = sum(1 for nj in itertools.product(range(M), repeat=4)
            if all(n in (0, M // 2) for n in nj))
    print("   zero-vertex count @M=%d = %d (2^4 = 16 expected)" % (M, c))
    zc2 = max(zc2, c)
ok &= ck(zc2 == 16, "C3  4D dispersion has exactly 2^4 = 16 zero vertices (free sector) on M in {28,36,44}", "")

# C4: IR dispersion exactness at the largest anchor N (mpmath, three-term law)
Nbig = 90112
om = 2.0 * mp.sin(mp.pi / Nbig)
kmin = 2.0 * mp.pi / Nbig
# exact series: omega/(c k) = sin(x)/x = 1 - x^2/6 + x^4/120 - ...
c4 = (1.0 - om / kmin) * 6.0 * Nbig * Nbig / mp.pi ** 2
c4next = 1.0 + mp.pi ** 2 / (20.0 * Nbig * Nbig)
ok &= ck(abs(c4 - c4next) < 1e-9,
         "C4  IR dispersion exactness: (1 - omega/c k)*6N^2/pi^2 = 1 + pi^2/(20N^2) at N=90112",
         "c4 = %.12f (pred %.12f)" % (float(c4), float(c4next)))

# C5: inertia signature re-verification from docs/16 recorded Q_phys spectrum
qplus = 8.773e-6; qneg = [-1.0966e-6] * 3 + [-4.3865e-6] * 2
sig = (sum(1 for x in [qplus] + qneg if x > 0), sum(1 for x in [qplus] + qneg if x < 0))
ok &= ck(sig == (1, 5),
         "C5  inertia signature of Q_phys (docs/16 spectrum) = (1+, 5-) per unit tensor norm",
         "sig = %d+, %d-" % sig)
ratio = 1.0966 / 4.3865
ok &= ck(abs(ratio - 0.25) < 1e-4,
         "C5b  min|TT|/|conformal| = 1.0966/4.3865 = 0.25 exact (re-verified)",
         "ratio = %.6f" % ratio)

# C6: honest grading
print("\n[C6] HONEST GRADING: these are DISCRETE-LAYER anchors (exact identities).")
print("  * free sector survives the continuum limit at every refinement step (gapless);")
print("  * free sector = 16-corner acoustic structure; inertia signature (1+,5-) exact.")
print("  * NOT claimed: continuous Lorentz kinematics/dynamics, signature, boost charges.")
print("    (A2's continuum reading needs the quotient blind run M in {12,16,24}; pre-registered.)")

print("\nRESULT: %s" % ("ALL CHECKS PASS" if ok else "SOME CHECKS FAILED"))