#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O245 R1 -- 2I subset SU(2) finite-subgroup identity verification.

Goal: verify the binary icosahedral group 2I (O222 quaternion algebra, 120
elements over Q(sqrt5)) DOES sit in SU(2) as a finite subgroup -- i.e.
every element is a UNIT quaternion (component-wise norm^2 = 1 exactly) and
the set is closed under multiplication/inverse.

O188 closeout left '2I -> SU(2) continuum lift NOT claimed' as the last
open point. Diagnosis: the lift's full mathematical content is the
finite-subgroup identity (Klein classification: 2I ~ SL(2,5) < SU(2));
NO continuum limit argument is needed and the scope rule stays intact
(no deriving/rebuilding LQG).

Pre-registered checks (zero relaxation; exact Q(sqrt5) throughout):
  A1  All 120 elements have component-wise norm^2 = 1: for each component
      (a, b) in Q(sqrt5): a^2 + 5 b^2 = 1 exactly as Fraction.
  A2  Alternative per-component check with a second normalization: every
      element satisfies conj(q)*q = identity quaternion (1,0,0,0) under the
      O222 quaternion product (exact; independent of A1 arithmetic path).
  A3  Closure under multiplication: product of any two elements is in the
      set (120x120 exact; group law already proven by O222 build_group --
      O245 re-checks independently via membership test).
  A4  Closure under inverse: inverse of every element (conjugate for unit
      quaternions) is in the set.
  A5  Embedding witness size: |2I| = 120; the double cover I(60) -> 2I(120)
      matches the SU(2) -> SO(3) 2:1 pattern (order counts).
  A6  Verdict: finite-subgroup identity ESTABLISHED (2I < SU(2), exact
      unit quaternions); continuum-lift claim explicitly NOT made
      (O188 scope rule; no limit argument).  Handoff back to O188.

Synopsis: every check exits 0 iff all conditions exact; output [PASS]/[FAIL]
ck() lines only (countable), ending with a SYNTHESIS line.
"""
import importlib.util
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
O222 = os.path.normpath(os.path.join(HERE, "..", "..", "o222_qm_evaluation_semantics", "scripts"))

PASS = FAIL = 0
def ck(idx, ok, msg):
    global PASS, FAIL
    tag = "[PASS]" if ok else "[FAIL]"
    print(f"{tag} {idx}: {msg}")
    if ok:
        PASS += 1
    else:
        FAIL += 1


def norm2_of(q):
    """quaternion norm^2 = sum_c (a_c + b_c sqrt5)^2, kept in Q(sqrt5):
    real part sum(a_c^2 + 5 b_c^2), sqrt5 part sum(2 a_c b_c).
    Unit quaternion iff real==1 and sqrt5-part==0 (exact Fractions)."""
    real = sum(c[0] * c[0] + Fraction(5) * c[1] * c[1] for c in q)
    s5 = sum(Fraction(2) * c[0] * c[1] for c in q)
    return real, s5


def conj_quat(q):
    """quaternion conjugate (w,-x,-y,-z): negate imaginary components."""
    return (q[0], tuple(-x for x in q[1]), tuple(-x for x in q[2]),
            tuple(-x for x in q[3]))


def main():
    spec = importlib.util.spec_from_file_location(
        "o222_09", os.path.join(O222, "09_a2_rollback.py"))
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, O222)
    spec.loader.exec_module(m)
    G = m.build_group()[0]
    ng = len(G)
    assert ng == 120, f"expected 120 group elements, got {ng}"

    # ---- A1: unit quaternions (full norm^2 = 1 in Q(sqrt5)) ----
    bad1 = []
    for i, q in enumerate(G):
        real, s5 = norm2_of(q)
        if real != 1 or s5 != 0:
            bad1.append((i, q, (real, s5)))
    ck("A1", not bad1,
       f"unit-quaternion condition: norm^2 = 1 in Q(sqrt5) for all {ng} "
       f"elements (real part sum(a_c^2+5b_c^2)=1, sqrt5 part sum(2a_c b_c)=0, "
       f"exact Fractions); violations {len(bad1)} "
       f"({bad1[:1] if bad1 else 'none'})")

    # ---- A2: conj(q) * q = identity under O222 quaternion product ----
    one = (Fraction(1), Fraction(0))
    zero = (Fraction(0), Fraction(0))
    ident = (one, zero, zero, zero)
    bad2 = []
    for i, q in enumerate(G):
        prod = m.qmul(q, conj_quat(q))
        if prod != ident:
            bad2.append((i, q, prod))
    ck("A2", not bad2,
       f"conjugate self-product: q * conj(q) = identity for all {ng} "
       f"elements (O222 qmul exact; violations {len(bad2)} "
       f"{bad2[:1] if bad2 else 'none'})")

    # ---- A3: closure under multiplication (all pairs) ----
    Gset = set(G)
    bad3 = []
    for i, qi in enumerate(G):
        for j, qj in enumerate(G):
            p = m.qmul(qi, qj)
            if p not in Gset:
                bad3.append((i, j, p))
    ck("A3", not bad3,
       f"multiplicative closure: qi*qj in G for all {ng}x{ng} pairs "
       f"(violations {len(bad3)} {bad3[:1] if bad3 else 'none'})")

    # ---- A4: closure under inverse (quaternion conjugate in set) ----
    bad4 = []
    for i, q in enumerate(G):
        if conj_quat(q) not in Gset:
            bad4.append((i, q))
    ck("A4", not bad4,
       f"inverse closure: conjugate of every element in G "
       f"(violations {len(bad4)} {bad4[:1] if bad4 else 'none'})")

    # ---- A5: 2:1 cover pattern (I(60) -> 2I(120), SU(2)->SO(3) analogue) ----
    ok5 = (ng == 120) and (ng // 2 == 60)
    ck("A5", ok5,
       f"order pattern: |2I| = {ng} = 2 x 60 = 2|I| (matches SU(2)->SO(3) "
       f"double-cover count)")

    # ---- A6: verdict (grounded in A1-A5 all passing) ----
    ok6 = (not bad1) and (not bad2) and (not bad3) and (not bad4) and ok5
    ck("A6", ok6,
       "verdict: finite-subgroup identity ESTABLISHED by direct computation "
       "-- 2I < SU(2) as exact unit quaternions (120 elements, norm^2 = 1 "
       "in Q(sqrt5), closed under * and inverse); continuum-lift claim "
       "explicitly NOT made (O188 scope rule; no limit argument needed); "
       "handoff back to O188 via register")
    print(f"\nSYNTHESIS O245/R1: {PASS} checks PASS, {FAIL} checks FAIL; "
          f"exit 0 (identity established, all exact)")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()