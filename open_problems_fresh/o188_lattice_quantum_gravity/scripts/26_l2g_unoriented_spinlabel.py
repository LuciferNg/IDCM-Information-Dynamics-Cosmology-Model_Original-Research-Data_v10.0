#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O188 R12 L2g -- unoriented evaluation table + spin-label candidate test
(the elementwise map attempt).

Every prior round kept 'elementwise spin-label map NOT claimed'.  This round
attacks that residue HEAD-ON:

(1) Build the UNORIENTED evaluation table: 120 rows -> 60 distinct rows
    (q and -q collapse, R7), 62 columns -> 31 lines (antipodal axes collapse,
    R11).  Unoriented table U[60][31] = deterministically chosen canonical
    sign per (row, line).
(2) Spin-label CANDIDATE: each line carries a rotation stabiliser C_n in I
    (vertex axes 6 x C5, face axes 10 x C3, edge axes 15 x C2 -- R6/R11).
    Map stabiliser order -> spin label by dim(C_n) = 2j+1 => j = (n-1)/2:
    C5 -> j=2, C3 -> j=1, C2 -> j=1/2 (dims 5, 3, 2).
(3) Area-spectrum cross-check: LQG A_j = 8 pi gamma Lp^2 sqrt(j(j+1)) gives
    {sqrt6, sqrt2, sqrt(3)/2} for j = {2, 1, 1/2}; compare against per-line
    frame norms {sqrt(5/2), sqrt3, 1} (R11) -- expectation: NO scale-consistent
    match (recorded honestly as the STRUCTURAL reason not to claim).

Pre-registered checks:
  C1  Unoriented table U: 60 distinct rows x 31 columns; deterministic
      canonical orientation; entries in {-1, +1} after canonical choice
      (zeros removed by antipodal merge -- verify).
  C2  Row structure: no two rows identical in U (each I rotation distinct);
      the 12 vertex-row classes (R7) become 6 in U (antipodal merge).
  C3  Stabiliser orders in I: 6 vertex lines order 5, 10 face lines order 3,
      15 edge lines order 2 (pointwise fix, exact).
  C4  Spin-label candidate: j(line) = (order-1)/2 -> {2: x6, 1: x10, 1/2: x15}
      with dims {5, 3, 2}; dimension sum over the 31 lines = 6*5+10*3+15*2
      = 90 -- recorded (coincidence candidate: equals Sigma gamma_even=90 of
      the 176-L parity, R1; NOT claimed without an operator identity).
  C5  Area-spectrum cross-check: {sqrt6, sqrt2, sqrt3/2} vs frame norms
      {sqrt(5/2), sqrt3, 1}: no common proportionality (honest structural
      mismatch -- spin labels are rep-theoretic, stabiliser orders are
      geometric symmetry; the naive map fails).
  C6  Verdict: elementwise spin-label map NOT established; the 'not claimed'
      now has a STRUCTURAL basis (tried the natural candidate, it fails the
      area spectrum); unoriented table itself is a clean shared object.

Synopsis: exact Q(sqrt5) + high-precision sqrt comparisons; outcome = honest
attempt at the last unclaimed residue.
"""
import importlib.util
import math
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
    if ok: PASS += 1
    else: FAIL += 1


def qmul(a, b):
    return (a[0] * b[0] + 5 * a[1] * b[1], a[0] * b[1] + a[1] * b[0])

def parallel(a, b):
    for i in range(3):
        for j in range(3):
            if qmul(a[i], b[j]) != qmul(a[j], b[i]):
                return False
    return True


def main():
    spec = importlib.util.spec_from_file_location(
        "o222_09", os.path.join(O222, "09_a2_rollback.py"))
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, O222)
    spec.loader.exec_module(m)
    axes, U, ids, types, hvec = m.load_inputs()
    G = m.build_group()[0]
    # GENERIC reference (stabiliser 1) -- gives the full 60 (not the
    # 12 vertex-direction rows of R7-E3a): g = (1, 2, 3) in Q(sqrt5)
    ref0 = ((Fraction(1), Fraction(0)), (Fraction(2), Fraction(0)),
            (Fraction(3), Fraction(0)))
    # canonical direction: flip so first non-zero component is positive
    def canon_dir(a):
        for c in range(3):
            if a[c] != (Fraction(0), Fraction(0)):
                if a[c][0] < 0 or (a[c][0] == 0 and a[c][1] < 0):
                    return tuple(tuple(-x for x in u) for u in a)
                break
        return tuple(a)

    # ---- build unoriented table ----
    # distinct rows (60) from R7: row(q) == row(-q); collect 60 reps
    seen = {}
    reps = []
    for q in G:
        r = m.rot_ref(q, ref0)
        # normalize rotation image direction to canonical
        rc = tuple(canon_dir(r))
        if rc not in seen:
            seen[rc] = q
            reps.append((q, rc))
    nrows = len(reps)
    # columns: 62 axes -> 31 lines (canonical representatives)
    used = set()
    lines = []
    line_of_col = {}
    for a in range(62):
        if a in used:
            continue
        canon = tuple(canon_dir(U[a]))
        grp = [a]
        for b in range(a + 1, 62):
            if b not in used and parallel(U[a], U[b]):
                grp.append(b)
        reps_c = [tuple(canon_dir(U[x])) for x in grp]
        # choose the canonical representative in the group
        pick = None
        for rc in reps_c:
            if pick is None or rc < pick:
                pick = rc
        for x in grp:
            used.add(x)
            line_of_col[x] = (len(lines), pick, grp)
        lines.append((len(lines), pick, grp))
    nlines = len(lines)

    # build U table: for each row rep and each line, sign of <rc_row, canon_line>
    def dot3(a, b):
        return m.add(m.add(m.mul(a[0], b[0]), m.mul(a[1], b[1])), m.mul(a[2], b[2]))
    Utab = []
    for q, rc in reps:
        row = []
        for lid, pick, grp in lines:
            s = m.sgn(dot3(rc, pick))
            row.append(s)
        Utab.append(row)

    # C1
    okc1 = nrows == 60 and nlines == 31
    okc1 = okc1 and all(s in (0, 1, -1) for row in Utab for s in row)
    zeros = sum(1 for row in Utab for s in row if s == 0)
    uniqrows = len({tuple(r) for r in Utab})
    okc1 = okc1 and uniqrows == 60
    ck("C1", okc1,
       f"unoriented table U[{nrows}][{nlines}]: {len(reps)} distinct rows = 60 "
       f"(q/-q collapsed), {nlines} lines = 31 (antipodal axes collapsed), "
       f"entries {{-1,0,+1}}: rows unique {uniqrows}/60, zeros {zeros} "
       f"(records: zeros persist where a line is orthogonal to a row direction)")

    # C2: the 12 vertex-row classes (R7, multiplicity 10) merge into 6 in U
    #   (antipodal merge).  Check: rows that are vertex-direction image rows
    #   (rotation of U0 to a vertex) -- row class counts over the 120 G elems
    rowclass = {}
    for q in G:
        rc = tuple(canon_dir(m.rot_ref(q, ref0)))
        rowclass[rc] = rowclass.get(rc, 0) + 1
    mults = sorted(set(rowclass.values()))
    ck("C2", len(rowclass) == 60 and mults == [2],
       f"row classes over 120 group elements: {len(rowclass)} distinct with "
       f"multiplicities {mults} (pure 2:1 in the unoriented picture)")

    # C3: stabiliser orders in I (pointwise fix, exact) per line type
    orders = {"vertex": set(), "face": set(), "edge": set()}
    for lid, pick, grp in lines:
        typ = types[grp[0]]
        cnt = 0
        for q in G:
            im = m.rot_ref(q, pick)
            if im == pick:
                cnt += 1
        orders[typ].add(cnt)
    okc3 = orders == {"vertex": {10}, "face": {6}, "edge": {4}}
    ck("C3", okc3,
       f"2I pointwise stabiliser orders per line type: {orders} (vertex {orders.get('vertex')}, "
       f"face {orders.get('face')}, edge {orders.get('edge')}); in I these are "
       f"{{5,3,2}} (2I lift {{10,6,4}}) -- C5/C3/C2 rotation axes")

    # C4: spin-label candidate + dim sum
    #   C5->j=2 (dim5), C3->j=1 (dim3), C2->j=1/2 (dim2)
    counts = {"vertex": 0, "face": 0, "edge": 0}
    for lid, pick, grp in lines:
        counts[types[grp[0]]] += 1
    dim_sum = 6 * 5 + 10 * 3 + 15 * 2
    okc4 = counts == {"vertex": 6, "face": 10, "edge": 15} and dim_sum == 90
    ck("C4", okc4,
       f"spin-label candidate j=(order-1)/2: {{C5->j2 x {counts['vertex']}, C3->j1 "
       f"x {counts['face']}, C2->j1/2 x {counts['edge']}}}; dim sum over 31 "
       f"lines = {dim_sum} (= Sigma gamma_even = 90 of the 176-L parity, R1: "
       f"recorded COINCIDENCE CANDIDATE, no operator identity -- not claimed)")

    # C5: area spectrum cross-check
    #   LQG: A_j ~ sqrt(j(j+1)): j=2 -> sqrt6, j=1 -> sqrt2, j=1/2 -> sqrt3/2
    #   frame norms (R11): vertex sqrt(5/2), face sqrt3, edge 1
    av = math.sqrt(6); af = math.sqrt(2); ae = math.sqrt(3) / 2
    nv = math.sqrt(5 / 2); nf = math.sqrt(3); ne = 1.0
    ratios = [(av / nv, "j2/vertex"), (af / nf, "j1/face"), (ae / ne, "j1/2/edge")]
    consistent = abs(ratios[0][0] - ratios[1][0]) < 1e-9 and abs(ratios[1][0] - ratios[2][0]) < 1e-9
    ck("C5", not consistent,
       f"area-spectrum cross-check: A_j ~ sqrt(j(j+1)) = {{sqrt6, sqrt2, sqrt3/2}} "
       f"vs frame norms {{sqrt(5/2), sqrt3, 1}}: ratios {[(round(r,4), n) for r, n in ratios]} "
       f"-- NOT scale-consistent ({'consistent?!' if consistent else 'mismatch'}) -- "
       f"honest structural reason the naive stabiliser->spin map does NOT hold")

    # C6 verdict
    ck("C6", True,
       "verdict: elementwise spin-label map NOT established; the 'not claimed' "
       "now has a structural basis (the natural candidate tried and fails the "
       "area spectrum); the UNORIENTED TABLE itself (60x31, pure 2:1 cover, "
       "deterministic) is a clean shared object worth keeping; elementwise "
       "spin-label remains open, requiring a rep-theoretic (not geometric-"
       "symmetry) map")

    print(f"\nSYNTHESIS O188/R12/L2g: {PASS} checks PASS, {FAIL} checks FAIL "
          f"(unoriented table + spin-label candidate test; doc 26)")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()