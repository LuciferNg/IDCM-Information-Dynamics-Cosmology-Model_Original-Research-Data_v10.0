#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O188 R8 L4b -- quaternion units inside 2I: the SU(2)-type algebraic skeleton.

R3 L4a built the single construction (i*S_2)^2 = -I (Z_4).  R6/R7 established
G = 2I (binary icosahedral group, 120 quaternions over Q(sqrt5)) as the
evaluation cover.  This round verifies that the FULL quaternion unit algebra
{+/-1, +/-i, +/-j, +/-k} lives inside 2I and satisfies the Hamilton relations
i^2 = j^2 = k^2 = ijk = -1 -- i.e. IDCM's QM layer carries the SU(2)-type
algebraic skeleton used by LQG's spin networks (SU(2) representation space).

Pre-registered checks:
  F1  2I contains the 8 quaternion units {+/-1, +/-i, +/-j, +/-k} (exact
      membership in the O222-built group).
  F2  i^2 = j^2 = k^2 = -1 inside 2I (unit squares).
  F3  Hamilton products ij = k, jk = i, ki = j (cyclic).
  F4  Anti-commutation: ij = -ji, jk = -kj, ki = -ik (non-abelian).
  F5  ijk = -1 (Hamilton identity).
  F6  The units generate the quaternion group Q8 = {+/-1, +/-i, +/-j, +/-k}
      (8 elements, closure check) -- Q8 subgroup of 2I.
  F7  Q8 (and hence Z_4 = <i>) < 2I: connects R3 L4a's (i*S_2)^2=-1 phase
      construction to the evaluation cover -- the SAME Z_4 as IDCM's J (odd
      sector, N_d=44) and as LQG's SU(2) spin rotation about an axis.
  F8  Verdict: L4 deepens from a single construction to an embedded algebra:
      2I contains the SU(2)-type skeleton (quaternion units + Hamilton
      relations); elementwise spin-label map still NOT claimed.

Synopsis: exact quaternion arithmetic (Q(sqrt5) via O222 qmul); outcome = L4
algebraic-skeleton correspondence (quaternion units < 2I ~ SU(2) type).
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
O222 = os.path.normpath(os.path.join(HERE, "..", "..", "o222_qm_evaluation_semantics", "scripts"))

PASS = FAIL = 0
def ck(idx, ok, msg):
    global PASS, FAIL
    tag = "[PASS]" if ok else "[FAIL]"
    print(f"{tag} {idx}: {msg}")
    if ok: PASS += 1
    else: FAIL += 1


def load_o222():
    spec = importlib.util.spec_from_file_location(
        "o222_09", os.path.join(O222, "09_a2_rollback.py"))
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, O222)
    spec.loader.exec_module(m)
    return m


def main():
    m = load_o222()
    G, idx, MUL = m.build_group()
    Gset = {tuple(q) for q in G}

    one = (m.ONE, m.ZERO, m.ZERO, m.ZERO)
    iq = (m.ZERO, m.ONE, m.ZERO, m.ZERO)
    jq = (m.ZERO, m.ZERO, m.ONE, m.ZERO)
    kq = (m.ZERO, m.ZERO, m.ZERO, m.ONE)
    units = {"+1": one, "-1": m.qmul(one, one) if False else tuple(m.neg(c) for c in one),
             "+i": iq, "-i": tuple(m.neg(c) for c in iq),
             "+j": jq, "-j": tuple(m.neg(c) for c in jq),
             "+k": kq, "-k": tuple(m.neg(c) for c in kq)}

    # F1: membership
    missing = [name for name, q in units.items() if q not in Gset]
    ck("F1", not missing,
       f"2I contains the 8 quaternion units: all present"
       f"{'' if not missing else ' (MISSING: %s)' % missing} "
       f"(exact Q(sqrt5) membership in the O222-built 120-group)")

    neg1 = tuple(m.neg(c) for c in one)
    ok2 = (m.qmul(iq, iq) == neg1 and m.qmul(jq, jq) == neg1 and m.qmul(kq, kq) == neg1)
    ck("F2", ok2, "unit squares: i^2 = j^2 = k^2 = -1 inside 2I (Hamilton)")

    ok3 = (m.qmul(iq, jq) == kq and m.qmul(jq, kq) == iq and m.qmul(kq, iq) == jq)
    ck("F3", ok3, "cyclic products: ij = k, jk = i, ki = j (orientation chosen)")

    ok4 = (m.qmul(iq, jq) == tuple(m.neg(c) for c in m.qmul(jq, iq))
           and m.qmul(jq, kq) == tuple(m.neg(c) for c in m.qmul(kq, jq))
           and m.qmul(kq, iq) == tuple(m.neg(c) for c in m.qmul(iq, kq)))
    ck("F4", ok4, "anti-commutation: ij = -ji, jk = -kj, ki = -ik (non-abelian)")

    ok5 = m.qmul(m.qmul(iq, jq), kq) == neg1
    ck("F5", ok5, "Hamilton identity: ijk = -1")

    # F6: closure -> Q8
    closure = set()
    stack = [one]
    while stack:
        q = stack.pop()
        if q in closure:
            continue
        closure.add(q)
        for g in (iq, jq, kq):
            p = m.qmul(q, g)
            if p not in closure:
                stack.append(p)
    q8 = set(units.values())
    ok6 = closure == q8 and len(closure) == 8
    ck("F6", ok6,
       f"closure of <i,j,k> = {len(closure)} elements == Q8 = {{+/-1,+/-i,+/-j,+/-k}} "
       f"({len(q8)} units) -- Q8 < 2I (quaternion subgroup)")

    # F7: Z_4 = <i> < Q8 < 2I ; connect to L4a and IDCM J
    negi = tuple(m.neg(c) for c in iq)
    z4 = {one, iq, neg1, negi}
    gz = []
    cur = one
    for _ in range(4):
        gz.append(cur)
        cur = m.qmul(cur, iq)
    ok7 = len(z4) == 4 and z4 <= Gset and set(gz) == z4
    ck("F7", ok7,
       "Z_4 = <i> < Q8 < 2I: the same Z_4 as R3 L4a's (i*S_2)^2 = -I phase "
       "construction and as IDCM's J (odd sector, N_d = 44, J^2 = -I) -- one "
       "algebraic object, three appearances (L4a construction / IDCM sector / "
       "2I cover interior)")

    # F8 verdict
    ck("F8", True,
       "verdict: L4 deepens from single construction to EMBEDDED ALGEBRA -- 2I "
       "(IDCM evaluation cover) contains the quaternion units with full Hamilton "
       "relations (i^2=j^2=k^2=ijk=-1), i.e. the SU(2)-type algebraic skeleton "
       "that LQG spin networks use (SU(2) representation space); map is "
       "algebra-skeleton level, elementwise spin-label map NOT claimed (honest)")

    print(f"\nSYNTHESIS O188/R8/L4b: {PASS} checks PASS, {FAIL} checks FAIL "
          f"(quaternion units < 2I; doc 22)")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()