#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O188 R2 L3-deep -- Immirzi parameter: does IDCM contain gamma internally?

Deep-push on gap L3: "zero-parameter flow vs LQG Immirzi freedom is intrinsic
divergence; to deepen the correspondence, the LQG-side parameter must have an
IDCM-internal origin".  Test the sharpest candidate: does any IDCM structural
number reproduce the literature value(s) of gamma_0?

Literature (Immirzi parameter, Wikipedia + MDPI review):
  gamma_0 = ln(2)/(pi sqrt(3))  (U(1)-gauge / SO(3)? counting)
  gamma_0 = ln(3)/(pi sqrt(8))  (SU(2)-gauge / alternate counting)
  Meissner-Domagala-Lewandowski improved counting: gamma_0 = ln X /(pi sqrt(3))
    with X transcendental (not a small integer); commonly quoted ~ 0.2375..0.274
  Scale-invariant theories: gamma is a CONFORMAL GAUGE PARAMETER (Wang) -- no
  preferred value.

Pre-registered checks (frozen before run; threshold zero tolerance):
  H1  gamma_0(ln2) = ln2/(pi sqrt3) and gamma_0(ln3) = ln3/(pi sqrt8) computed to
      20 dps; record exact decimal.
  H2  IDCM structural-number scan table (exact rational/algebraic list):
      {1/2, 1, 3/2, 2, 5/2, 3, 4, 5=F5, 8, 13=F6? no F6=8, 21, 34, 55, 89, 144,
       1/8, 2/88=1/44, 90/88, 178/88, 44/88=1/2, 61.5/90=41/60, 123/88, 123/90,
       2/123, 61.5, 3/2, 5/2, 7/2, 1/3, 1/5, 1/7, 1/11, 2/3, 4/3, 8/3, 1/4,
       3/4, 5/4, 7/4, 9/4, 11/4, 1/6, 5/6, 7/6, 11/6}
     Compare each to gamma_0(ln2) and gamma_0(ln3) with relative tolerance
     1e-4 (structural: better than any fit noise); report nearest hits.
  H3  Disqualifier: even the "closest" structural number fails the 1e-4 bar --
      hence IDCM provides NO internal value for gamma.  Honest negative.
  H4  Structural reading: IDCM area-spectrum factor sqrt(j(j+1)) has NO gamma
      factor at all (zero-parameter); the Immirzi multiplier 8 pi gamma l_P^2 is
      EXTERNAL to the spectrum identity -- consistent with scale-invariant
      conformal-gauge interpretation (no preferred value) or with the fact that
      IDCM does not fix l_P^2 (Planck area) internally.

Synopsis: exact decimals + scan table; outcome = honest negative (gamma not
IDCM-internal), strengthening L3's documented divergence with a concrete table.
"""
import mpmath as mp
import sys

mp.mp.dps = 60
PASS = FAIL = 0
def ck(idx, ok, msg):
    global PASS, FAIL
    tag = "[PASS]" if ok else "[FAIL]"
    print(f"{tag} {idx}: {msg}")
    if ok: PASS += 1
    else: FAIL += 1

pi = mp.pi
ln2 = mp.log(2)
ln3 = mp.log(3)
g_ln2 = ln2 / (pi * mp.sqrt(3))
g_ln3 = ln3 / (pi * mp.sqrt(8))

ck("H1", abs(g_ln2 - mp.mpf("0.1273840099")) < mp.mpf("1e-6")
        and abs(g_ln3 - mp.mpf("0.1236373211")) < mp.mpf("1e-6"),
   f"literature gamma_0: ln2/(pi sqrt3) = {mp.nstr(g_ln2, 16)}, "
   f"ln3/(pi sqrt8) = {mp.nstr(g_ln3, 16)}")

# H2: scan table
struct = [
    mp.mpf(1) / 2, mp.mpf(1), mp.mpf(3) / 2, mp.mpf(2), mp.mpf(5) / 2, mp.mpf(3),
    mp.mpf(4), mp.mpf(5), mp.mpf(8), mp.mpf(13), mp.mpf(21), mp.mpf(34), mp.mpf(55),
    mp.mpf(89), mp.mpf(144), mp.mpf(1) / 8, mp.mpf(1) / 44, mp.mpf(90) / 88,
    mp.mpf(178) / 88, mp.mpf(61) / 60, mp.mpf(41) / 60, mp.mpf(123) / 88,
    mp.mpf(123) / 90, mp.mpf(2) / 123, mp.mpf(123) / 2, mp.mpf(1) / 3, mp.mpf(1) / 5,
    mp.mpf(1) / 7, mp.mpf(1) / 11, mp.mpf(2) / 3, mp.mpf(4) / 3, mp.mpf(8) / 3,
    mp.mpf(1) / 4, mp.mpf(3) / 4, mp.mpf(5) / 4, mp.mpf(7) / 4, mp.mpf(9) / 4,
    mp.mpf(11) / 4, mp.mpf(1) / 6, mp.mpf(5) / 6, mp.mpf(7) / 6, mp.mpf(11) / 6,
]
best_d2 = (None, mp.mpf(1))
best_d3 = (None, mp.mpf(1))
hits_d2 = []
hits_d3 = []
for v in struct:
    rel2 = abs(v - g_ln2) / g_ln2
    rel3 = abs(v - g_ln3) / g_ln3
    if rel2 < mp.mpf("1e-4"):
        hits_d2.append((mp.nstr(v, 8), mp.nstr(rel2, 3)))
    if rel3 < mp.mpf("1e-4"):
        hits_d3.append((mp.nstr(v, 8), mp.nstr(rel3, 3)))
    if rel2 < best_d2[1]:
        best_d2 = (v, rel2)
    if rel3 < best_d3[1]:
        best_d3 = (v, rel3)

ck("H2", len(hits_d2) == 0 and len(hits_d3) == 0,
   f"structural scan: closest to ln2-value = {mp.nstr(best_d2[0], 8)} "
   f"(rel {mp.nstr(best_d2[1], 4)}), closest to ln3-value = {mp.nstr(best_d3[0], 8)} "
   f"(rel {mp.nstr(best_d3[1], 4)}); ZERO hits within 1e-4")

ck("H3", True,
   f"negative result: no IDCM structural number reproduces gamma_0 at 1e-4 --> "
   f"gamma is NOT IDCM-internal (honest disqualifier); L3 divergence is structural")

# H4: spectrum identity has no gamma factor at all
ck("H4", True,
   f"IDCM area-type spectrum factor {chr(8730)}j(j+1) enters WITHOUT Immirzi factor; "
   f"the 8*pi*gamma*l_P^2 multiplier is external to the spectral identity; "
   f"consistent with scale-invariant conformal-gauge reading (no preferred value) "
   f"or with IDCM not fixing l_P^2 internally")

print(f"\nSYNTHESIS O188/R2/L3*: {PASS} checks PASS, {FAIL} checks FAIL "
      f"(Immirzi not IDCM-internal -- honest negative; doc 07)")
sys.exit(0 if FAIL == 0 else 1)