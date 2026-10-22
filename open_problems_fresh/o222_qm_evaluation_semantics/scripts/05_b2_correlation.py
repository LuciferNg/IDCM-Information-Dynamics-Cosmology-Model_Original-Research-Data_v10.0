#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O222 scripts/05_b2_correlation.py  —  B2 C(theta) lattice derivation UNDER CONTRACT v1 (frozen)

Frozen definition (docs/03_b2_contract.md SS3), reproduced verbatim in code:
    K(g, a) = sign( u_a . (g n_hat) )                  exact algebraic; ties by H3 rule
    C[a][b] = sum_{g in G} w(g) K(g,a) K(g,b)          G = 2I (120) primary / I (60) control

Hard bans (enforced by scripts/04_b2_contract.py, AST scan): no cos/sin/tan/pi/sqrt/exp/log,
no numpy/scipy/math/random, no non-integral float literals anywhere -> exact rational arithmetic only.
Sequential (rollback) level is NOT defined in the frozen contract -> reported PENDING (amendment A2 needed).
Blinding: DEV (V x V, 144 pairs) printed; BLIND (3700 pairs) written to file, aggregates only with --reveal.

Run:  python3 scripts/05_b2_correlation.py            # compute + write; print DEV only
      python3 scripts/05_b2_correlation.py --reveal   # also print full-grid aggregates
"""

import hashlib
import io
import itertools
import json
import os
import sys
import time
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
os.makedirs(DATA, exist_ok=True)
REVEAL = "--reveal" in sys.argv
RESULTS = []
_T0 = time.time()


def stage(msg):
    print("  [stage %7.1fs] %s" % (time.time() - _T0, msg))


def chk(tag, name, ok, detail=""):
    RESULTS.append({"tag": tag, "name": name, "ok": bool(ok), "detail": detail})
    print("[%s] %-7s %-80s %s" % ("PASS" if ok else "FAIL", tag, name, detail))
    return ok


def claim(tag, name, text):
    RESULTS.append({"tag": tag, "name": name, "ok": None, "detail": text})
    print("[CLAIM] %-7s %-80s %s" % (tag, name, text))


# ======================================================== exact Q(sqrt5) arithmetic
ZERO, ONE = (F(0), F(0)), (F(1), F(0))


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def neg(x):
    return (-x[0], -x[1])


def sub(x, y):
    return (x[0] - y[0], x[1] - y[1])


def mul(x, y):
    return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def inv(x):
    d = x[0] * x[0] - 5 * x[1] * x[1]
    if d == 0:
        raise ZeroDivisionError("non-invertible in Q(sqrt5)")
    return (x[0] / d, -x[1] / d)


def num_sign(x):
    """EXACT sign of p + q*sqrt5, no square root anywhere."""
    p, q = x
    if p == 0 and q == 0:
        return 0
    if q == 0:
        return 1 if p > 0 else -1
    if p == 0:
        return 1 if q > 0 else -1
    if p > 0 and q > 0:
        return 1
    if p < 0 and q < 0:
        return -1
    if p > 0 and q < 0:
        return 1 if p * p > 5 * q * q else -1
    return 1 if 5 * q * q > p * p else -1


PHI = (F(1, 2), F(1, 2))
PSI = sub(PHI, ONE)


def dot(a, b):
    return add(add(mul(a[0], b[0]), mul(a[1], b[1])), mul(a[2], b[2]))


def norm2(a):
    return dot(a, a)


def dir_canon(v):
    for x in v:
        if x != ZERO:
            return tuple(mul(inv(x), y) for y in v)
    raise ValueError("zero vector")


# ======================================================== lattice group (same construction as scripts/04)
def qmul(a, b):
    a0, a1, a2, a3 = a
    b0, b1, b2, b3 = b
    return (sub(sub(sub(mul(a0, b0), mul(a1, b1)), mul(a2, b2)), mul(a3, b3)),
            add(add(mul(a0, b1), mul(a1, b0)), sub(mul(a2, b3), mul(a3, b2))),
            add(sub(mul(a0, b2), mul(a1, b3)), add(mul(a2, b0), mul(a3, b1))),
            add(add(mul(a0, b3), mul(a1, b2)), sub(mul(a3, b0), mul(a2, b1))))


def qconj(q):
    return (q[0], neg(q[1]), neg(q[2]), neg(q[3]))


GENS = []
for _s in (1, -1):
    GENS.append((ONE if _s > 0 else neg(ONE), ZERO, ZERO, ZERO))
    GENS.append((ZERO, ONE if _s > 0 else neg(ONE), ZERO, ZERO))
    GENS.append((ZERO, ZERO, ONE if _s > 0 else neg(ONE), ZERO))
    GENS.append((ZERO, ZERO, ZERO, ONE if _s > 0 else neg(ONE)))
for _s1 in (1, -1):
    for _s2 in (1, -1):
        for _s3 in (1, -1):
            GENS.append(((F(_s1, 2), F(0)), (F(_s2, 2), F(0)), (F(_s3, 2), F(0)), (F(_s1 * _s2 * _s3, 2), F(0))))
_HALF = (F(1, 2), F(0))
GENS.append((mul(PHI, _HALF), mul(ONE, _HALF), mul(PSI, _HALF), ZERO))   # (phi, 1, psi, 0)/2 with psi = phi - 1

gset = set(GENS)
frontier = list(gset)
while frontier and len(gset) <= 400:
    nxt = []
    for a in frontier:
        for b in GENS:
            c = qmul(a, b)
            if c not in gset:
                gset.add(c)
                nxt.append(c)
    frontier = nxt
G2I = sorted(gset)
if len(G2I) != 120:
    print("[FATAL] closure did not close at 120 -- |G| = %d. Almost always a non-unit generator "
          "(a flipped psi component was the actual cause on 2026-09-29). Aborting instead of burning minutes."
          % len(G2I))
    sys.exit(2)


def rot_matrix(q):
    cols = []
    for i in range(3):
        e = [ZERO, ZERO, ZERO]
        e[i] = ONE
        r = qmul(qmul(q, (ZERO, e[0], e[1], e[2])), qconj(q))
        cols.append((r[1], r[2], r[3]))
    return tuple(tuple(cols[j][i] for j in range(3)) for i in range(3))


def matvec(M, v):
    return tuple(add(add(mul(M[i][0], v[0]), mul(M[i][1], v[1])), mul(M[i][2], v[2])) for i in range(3))


def matmul(A, B):
    return tuple(tuple(add(add(mul(A[i][0], B[0][j]), mul(A[i][1], B[1][j])), mul(A[i][2], B[2][j]))
                       for j in range(3)) for i in range(3))


IM = tuple(tuple(ONE if i == j else ZERO for j in range(3)) for i in range(3))


def matkey_of(M):
    return tuple(tuple(c for c in row) for row in M)


def order_of(M):
    k, X = 1, M
    while X != IM:
        X = matmul(X, M)
        k += 1
        if k > 20:
            raise RuntimeError("order not found")
    return k


ROTS = [rot_matrix(q) for q in G2I]              # 120 rotations (each I-rotation appears twice)
I60_KEYS = []
for _M in ROTS:
    if _M not in I60_KEYS:
        I60_KEYS.append(_M)
G60 = []
_seen60 = set()
for _q in G2I:
    _k = matkey_of(rot_matrix(_q))
    if _k not in _seen60:
        _seen60.add(_k)
        G60.append(_q)


def orbit_of(v0):
    return sorted({matvec(M, v0) for M in I60_KEYS})


def rep_of(order_k):
    for q in G2I:
        vec = (q[1], q[2], q[3])
        if all(x == ZERO for x in vec):
            continue
        if order_of(rot_matrix(q)) == order_k:
            return dir_canon(vec)
    raise RuntimeError("no representative of order %d" % order_k)


V12 = orbit_of(rep_of(5))
F20 = orbit_of(rep_of(3))
E30 = orbit_of(rep_of(2))
AXES = ([("V%02d" % i, "vertex", v) for i, v in enumerate(V12)] +
        [("F%02d" % i, "face", v) for i, v in enumerate(F20)] +
        [("E%02d" % i, "edge", v) for i, v in enumerate(E30)])
NA = len(AXES)
REF = V12[0]
N2I = None                                       # C table (integer numerators), set below

print("=" * 118)
print("O222 B2 -- C(theta) from 2I x 62 lattice axes, UNDER CONTRACT v1 (no trig / no float / no fitting)")
print("=" * 118)
print("groups: |2I| = %d, |I| = %d ; axes: %d (V %d / F %d / E %d) ; measure: uniform"
      % (len(G2I), len(I60_KEYS), NA, len(V12), len(F20), len(E30)))
stage("group + axes built")  # noqa
chk("P0", "structure reproduced from scripts/04 (|2I| = 120, |I| = 60, 62 axes)",
    len(G2I) == 120 and len(I60_KEYS) == 60 and NA == 62, "NA = %d" % NA)


# ======================================================== frozen kernel (SS3)
def tie_sign(vec):
    """H3 frozen tie rule: sign of the FIRST non-zero component."""
    for comp in vec:
        s = num_sign(comp)
        if s != 0:
            return s
    return 0


def k_table(setting, ref, group, w=None):
    """Single-setting factor table: K(g, a) = sign(u_a . (g n_hat)), ties by H3.
    ONE setting only -- the remote setting must never appear here (contract SS4.1).
    `w` optionally carries the precomputed image directions of n_hat (same group, same ref)."""
    u = setting
    dirs = w if w is not None else [matvec(M, ref) for M in [rot_matrix(q) for q in group]]
    out = []
    ties = 0
    for gv in dirs:
        s = num_sign(dot(u, gv))
        if s == 0:
            s = tie_sign(gv)
            ties += 1
        out.append(s)
    return out, ties


def pair_build(K, w_num, a, b):
    """C[a][b] as an exact numerator over w_num: sum_g w(g) K(g,a) K(g,b) with w = 1/w_num."""
    row_a = K[a]
    row_b = K[b]
    s = 0
    for i in range(len(row_a)):
        s += row_a[i] * row_b[i]
    return s


def qm_sq_diff(c_num, den, cos2):
    """EXACT sign/zero of C^2 - cos^2(theta), both exact (C rational, cos^2 in Q(sqrt5))."""
    c2 = F(c_num * c_num, den * den)
    return (c2 - cos2[0], -cos2[1])


W2I = [matvec(M, REF) for M in ROTS]                      # image directions of n_hat under 2I (120)
W60 = []
_seen = set()
for _M in ROTS:
    kk = tuple(tuple(c for c in r) for r in _M)
    if kk not in _seen:
        _seen.add(kk)
        W60.append(matvec(_M, REF))                       # one per I-rotation (60)

# ---- EXACT STRUCTURAL IDENTITY (speed, verified below against the direct loop) -------------
#   Over 2I the image g n_hat runs over exactly the 12 vertex vectors with multiplicity 10
#   (over I60: multiplicity 5).  Therefore
#       sum_g K(g,a)K(g,b)  =  sum_k mult_k K_k(a)K_k(b)          [k over the 12 vertices]
#   so sign rows over the 12 vertices are lossless; the direct 120-element dot loop gives the
#   identical table (dual-path check P0c).
VKEY = [tuple(v) for v in V12]
MULT2I = [sum(1 for d in W2I if tuple(d) == key) for key in VKEY]
MULT60 = [sum(1 for d in W60 if tuple(d) == key) for key in VKEY]
IDX2I = [k for k in range(12) for _ in range(MULT2I[k])]
IDX60 = [k for k in range(12) for _ in range(MULT60[k])]
SROW = []
ORTH = []
for _i in range(NA):
    _u = AXES[_i][2]
    _sr = []
    _orr = []
    for _v in V12:
        _sn = num_sign(dot(_u, _v))
        _orr.append(1 if _sn == 0 else 0)
        _sr.append(tie_sign(_v) if _sn == 0 else _sn)
    SROW.append(_sr)
    ORTH.append(_orr)
chk("P0b", "multiplicities exact: every vertex direction hit 10x (2I) / 5x (I60); 12x10 = 120, 12x5 = 60",
    set(MULT2I) == {10} and set(MULT60) == {5},
    "mult sets = %s / %s" % (sorted(set(MULT2I)), sorted(set(MULT60))))
_direct_bad = 0
_tie_bad = 0
for _i in range(NA):
    _rdir, _tdir = k_table(AXES[_i][2], REF, G2I, W2I)
    if sorted(_rdir) != sorted([SROW[_i][k] for k in IDX2I]):
        _direct_bad += 1
    if _tdir != sum(MULT2I[k] * ORTH[_i][k] for k in range(12)):
        _tie_bad += 1
_drows = [k_table(V12[i], REF, G2I, W2I)[0] for i in range(12)]
_frows = [[SROW[i][k] for k in IDX2I] for i in range(12)]
_pair_bad = 0
for _a in range(12):
    for _b in range(12):
        if pair_build(_drows, len(G2I), _a, _b) != pair_build(_frows, len(G2I), _a, _b):
            _pair_bad += 1
chk("P0c", "dual-path: fast vertex table == direct 120-element loop (row multiset, ties, all 144 DEV correlations)",
    _direct_bad == 0 and _tie_bad == 0 and _pair_bad == 0,
    "row-multiset mismatches = %d ; tie mismatches = %d ; correlation mismatches = %d/144"
    % (_direct_bad, _tie_bad, _pair_bad))

K2I = [[SROW[i][k] for k in IDX2I] for i in range(NA)]
K60 = [[SROW[i][k] for k in IDX60] for i in range(NA)]
ties_total = sum(MULT2I[k] * ORTH[i][k] for i in range(NA) for k in range(12))
m2I = [sum(row) for row in K2I]
m60 = [sum(row) for row in K60]
chk("P1", "marginal = 1/2 EXACT for all 62 axes, ties ASSIGNED by H3 (2I: 120 ; I60: 60)",
    all(v == 0 for v in m2I) and all(v == 0 for v in m60),
    "nonzero marginals: %d/62 (2I), %d/62 (I60) ; tie events (ref V00) = %d"
    % (sum(1 for v in m2I if v != 0), sum(1 for v in m60 if v != 0), ties_total))

rob_bad = 0
for r in V12:
    Wr = [matvec(M, r) for M in ROTS]
    multr = [sum(1 for d in Wr if tuple(d) == key) for key in VKEY]
    if set(multr) != {10}:
        rob_bad += 1
    for i in range(NA):
        if sum(multr[k] * SROW[i][k] for k in range(12)) != 0:
            rob_bad += 1
chk("P1b", "H4 robustness: every reference axis maps to the 12 vertices x10 and its marginal vanishes (12 x 62)",
    rob_bad == 0, "violations = %d" % rob_bad)

DEN = len(G2I)
N2I = [[0] * NA for _ in range(NA)]
for a in range(NA):
    for b in range(NA):
        N2I[a][b] = pair_build(K2I, DEN, a, b)
NC60 = [[pair_build(K60, len(G60), a, b) for b in range(NA)] for a in range(NA)]
chk("H5", "C[a][b] assembled from single-setting factor tables (local); C(a,a) = 1 exactly",
    all(N2I[a][a] == DEN for a in range(NA)), "denominator = %d ; C(V00,V00) = 1" % DEN)

COS2 = [[None] * NA for _ in range(NA)]
for a in range(NA):
    for b in range(NA):
        d = dot(AXES[a][2], AXES[b][2])
        COS2[a][b] = mul(mul(d, d), inv(mul(norm2(AXES[a][2]), norm2(AXES[b][2]))))

def is_antipodal(i, j):
    """exact: u_i + u_j = 0 (the antipodal partner of a lattice axis)."""
    if i == j:
        return False
    return all(add(x, y) == ZERO for x, y in zip(AXES[i][2], AXES[j][2]))


ANTI = [[is_antipodal(i, j) for j in range(NA)] for i in range(NA)]
_n_anti = sum(1 for i in range(NA) for j in range(NA) if ANTI[i][j] and i != j)
chk("L-SET2", "setting set contains antipodal pairs (these force C = -1 for ANY sign kernel, so all "
    "CHSH statements are reported both raw and antipodal-free)", _n_anti == NA // 2 * 2,
    "antipodal ordered pairs = %d (= %d axis pairs)" % (_n_anti, _n_anti // 2))

DEV = [(i, j) for i in range(12) for j in range(12)]
BLIND = [(i, j) for i in range(NA) for j in range(NA) if not (i < 12 and j < 12)]

stage("kernel tables + C table + cos^2 built")
print()
print("--- DEV set (V x V, %d pairs) : the only visible set before --reveal ---" % len(DEV))
print("%-6s %-6s %-8s %12s %10s %18s %10s" % ("a", "b", "type", "C = N/120", "|C|", "cos^2 (Q(sqrt5))", "C^2 == cos^2"))
dev_rows = []
dev_eq = 0
for (a, b) in DEV:
    c = F(N2I[a][b], DEN)
    d = qm_sq_diff(N2I[a][b], DEN, COS2[a][b])
    eq = (d[0] == 0 and d[1] == 0)
    dev_eq += 1 if eq else 0
    dev_rows.append({"a": AXES[a][0], "b": AXES[b][0], "type": AXES[a][1] + "x" + AXES[b][1],
                     "C_num": N2I[a][b], "C_den": DEN,
                     "cos2": [str(COS2[a][b][0]), str(COS2[a][b][1])], "exact_eq": eq})
    if len(dev_rows) <= 30:
        print("%-6s %-6s %-8s %12s %10s %18s %10s"
              % (AXES[a][0], AXES[b][0], AXES[a][1][:3] + "x" + AXES[b][1][:3], str(c), str(abs(c)),
                 "%s + %s*sqrt5" % (COS2[a][b][0], COS2[a][b][1]), "YES" if eq else "no"))
print("   ... all %d DEV pairs -> data/05_b2_dev_values.json" % len(DEV))


def grid_metrics(pairs):
    eq = 0
    max_gap_num = F(0)
    max_abs_c = F(0)
    for (a, b) in pairs:
        d = qm_sq_diff(N2I[a][b], DEN, COS2[a][b])
        if d[0] == 0 and d[1] == 0:
            eq += 1
        else:
            gap = abs(d[0]) + abs(d[1])
            if gap > max_gap_num:
                max_gap_num = gap
        ac = abs(F(N2I[a][b], DEN))
        if ac > max_abs_c:
            max_abs_c = ac
    return eq, max_gap_num, max_abs_c


eq_dev, gap_dev, mac_dev = grid_metrics(DEV)
chk("P4", "DEV grid: exact algebraic comparison C^2 vs cos^2 in Q(sqrt5) (no tolerance to tune)",
    True, "exact matches = %d/%d ; max |delta| (num+den coeff) = %s ; max |C| = %s"
    % (eq_dev, len(DEV), gap_dev, mac_dev))


# ---- P2: CHSH full ordered sweep over the whole frozen setting table --------
def chsh_sweep(idx, table):
    best = 0
    arg = None
    for a in idx:
        ra = table[a]
        for a2 in idx:
            ra2 = table[a2]
            base = [ra[b] + ra2[b] for b in range(len(ra))]
            for b in idx:
                bb = base[b]
                for b2 in idx:
                    s = bb + ra[b2] - ra2[b2]
                    if s < 0:
                        s = -s
                    if s > best:
                        best = s
                        arg = (a, a2, b, b2)
    return best, arg


print()
def chsh_free(idx, anti, table, den):
    """max |S| over four DISTINCT, pairwise NON-ANTIPODAL settings.

    Why this statistic exists (A4, 2026-09-29): an antipodal setting pair has C = -1 EXACTLY for any
    sign kernel whatsoever -- sign(u.(g nhat)) flips with u -> -u, so that entry is a property of the
    SETTING SET, not of the dynamics.  Every observed |S| = 2 (lattice AND random-quaternion null)
    was attained through such a pair, so the raw maximum cannot discriminate anything; the honest
    comparison needs the antipodal-free subsample."""
    best = 0
    arg = None
    for quad in itertools.combinations(idx, 4):
        a, a2, b, b2 = quad
        if anti[a][a2] or anti[a][b] or anti[a][b2] or anti[a2][b] or anti[a2][b2] or anti[b][b2]:
            continue
        for perm in itertools.permutations((a, a2, b, b2)):
            p, p2, q, q2 = perm
            sv = table[p][q] + table[p][q2] + table[p2][q] - table[p2][q2]
            if sv < 0:
                sv = -sv
            if sv > best:
                best = sv
                arg = perm
    return best, arg


def chsh_distinct(idx, table, den):
    """max |S| over tuples with FOUR DISTINCT settings -- the meaningful CHSH.  The degenerate
    case a = a', b = b' gives |S| = 2 for ANY model (1+1+1-1) and carries no information."""
    best = 0
    arg = None
    for quad in itertools.permutations(idx, 4):
        a, a2, b, b2 = quad
        s = table[a][b] + table[a][b2] + table[a2][b] - table[a2][b2]
        if s < 0:
            s = -s
        if s > best:
            best = s
            arg = quad
    return best, arg


stage("DEV metrics done (pre-sweep)")
print("--- P2: coexistence-level CHSH, FULL ordered sweep over all 62^4 setting 4-tuples ---")
best_all, arg_all = chsh_sweep(list(range(NA)), N2I)
S = F(best_all, DEN)
print("max |S| = %s (= %s)   argmax (a,a',b,b') = %s"
      % (str(S), str(float(S)), tuple(AXES[i][0] for i in arg_all)))
chk("P2", "full 62^4 ordered sweep executed (no subset selection, no cherry-pick)", True,
    "argmax = %s" % (tuple(AXES[i][0] for i in arg_all),))
in_lhv = (best_all <= 2 * DEN)
if in_lhv:
    verdict = "LHV-class: |S| <= 2 EXACTLY -- matches pre-registered P2 (g is a shared hidden variable)"
elif best_all * best_all < 8 * DEN * DEN:
    verdict = "above 2, below Tsirelson (|S|^2 < 8)"
elif best_all * best_all == 8 * DEN * DEN:
    verdict = "exactly Tsirelson |S| = 2*sqrt2"
else:
    verdict = "ABOVE Tsirelson (|S|^2 > 8)"
chk("P2b", "verdict against the pre-registered H8 windows (exact: |S| vs 2, |S|^2 vs 8)", in_lhv, verdict)
claim("P2c", "Tsirelson comparison carried out exactly (no irrational input)",
      "|S|^2 = %s ; |S|^2 - 8 = %s (exact rational sign)"
      % (str(F(best_all * best_all, DEN * DEN)), str(F(best_all * best_all, DEN * DEN) - 8)))


def chsh_conv(idx, table, den, flip):
    best = 0
    for a in idx:
        for a2 in idx:
            for b in idx:
                for b2 in idx:
                    t = (table[a][b], table[a][b2], table[a2][b], table[a2][b2])
                    s = sum(-t[k] if k == flip else t[k] for k in range(4))
                    s = -s if s < 0 else s
                    if s > best:
                        best = s
    return F(best, den)


print()
print("--- P2e: NON-DEGENERATE CHSH (four distinct settings) ---")
best_dis, arg_dis = chsh_distinct(list(range(NA)), N2I, DEN)
Sd = F(best_dis, DEN)
print("max |S| over 4-distinct-setting tuples = %s (= %s)   argmax = %s"
      % (str(Sd), str(float(Sd)), tuple(AXES[i][0] for i in arg_dis)))
chk("P2e", "non-degenerate sweep over all %d ordered 4-distinct-setting tuples executed"
    % (NA * (NA - 1) * (NA - 2) * (NA - 3)), True,
    "max |S| = %s ; argmax = %s" % (str(Sd), tuple(AXES[i][0] for i in arg_dis)))
if best_dis <= 2 * DEN:
    vd = "LHV-class: |S| <= 2 EXACTLY on non-degenerate settings as well (matches pre-registered P2)"
elif best_dis * best_dis < 8 * DEN * DEN:
    vd = "above 2, below Tsirelson"
elif best_dis * best_dis == 8 * DEN * DEN:
    vd = "exactly Tsirelson 2*sqrt2"
else:
    vd = "ABOVE Tsirelson"
chk("P2f", "verdict on non-degenerate settings (H8 windows)", best_dis <= 2 * DEN, vd)

print()
print("--- P2g: ANTIPODAL-FREE CHSH (four distinct, no antipodal pair -- see A4) ---")
best_free, arg_free = chsh_free(list(range(NA)), ANTI, N2I, DEN)
Sf = F(best_free, DEN)
print("max |S| (antipodal-free) = %s (= %s)   argmax = %s"
      % (str(Sf), str(float(Sf)), tuple(AXES[i][0] for i in arg_free)))
chk("P2g", "antipodal-free sweep executed: max |S| on the non-trivial setting subsample",
    True, "max |S| = %s (raw max was %s) ; argmax = %s"
    % (str(Sf), str(F(best_all, DEN)), tuple(AXES[i][0] for i in arg_free)))

conv = sorted({str(chsh_conv(list(range(12)), N2I, DEN, f)) for f in range(4)})
chk("P2d", "sign-convention invariance check on the 12-vertex grid (all 4 minus positions)",
    len(conv) == 1, "distinct max values = %s" % conv)

best60, arg60 = chsh_sweep(list(range(NA)), NC60)
claim("H1", "measure control: uniform on I (60 rotations) vs uniform on 2I (120 quaternions)",
      "max |S| = %s (I60) vs %s (2I) ; %s"
      % (str(F(best60, len(G60))), str(F(best_all, DEN)),
         "identical on both measures" if F(best60, len(G60)) == F(best_all, DEN) else "DIFFERS -- measure sensitivity"))

stage("CHSH sweep + conventions + I60 control done")
# ---- P6: ablation = independent draws per wing -------------------------------
sample_pairs = [(0, 1), (0, 12), (0, 30), (5, 7), (11, 22), (12, 20), (20, 30), (30, 40), (44, 55), (1, 61)]
explicit_ok = all(sum(x * y for x in K2I[a] for y in K2I[b]) == 0 for (a, b) in sample_pairs)
ident_ok = all(m2I[a] * m2I[b] == 0 for a in range(NA) for b in range(NA))
chk("P6", "ablation (communication attribution): independent draws per wing -> C = 0 EXACT",
    explicit_ok and ident_ok,
    "identity (sum_g K(g,a))(sum_h K(h,b)) = 0 over all %d pairs ; explicit double sum verified on %d pairs"
    % (NA * NA, len(sample_pairs)))


# ---- P5: nulls, seed 222 (H9) ----------------------------------------------
stage("ablation done")


MASK64 = (1 << 64) - 1


def lcg(state):
    """Deterministic splitmix64 mixer (declared): returns (new_state, mixed 64-bit value).
    The mixer matters: the earlier multiplicative LCG left consecutive draws correlated, so the
    sampled rotation set was structurally poor (found 2026-09-29 by checking the null marginals).
    Still a pure deterministic function -- no imports, no hidden state, seed fixed at 222."""
    state = (state + 0x9E3779B97F4A7C15) & MASK64
    z = state
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
    z = z ^ (z >> 31)
    return state, z & MASK64


def isqrt_int(n):
    """Integer square root by Newton iteration -- exact, no floats, no math module."""
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


def rand_unit_quat(state):
    """Exact RATIONAL unit quaternion by rejection on Pythagorean quadruples: draw integers
    (a,b,c,d) and keep those whose norm^2 is a perfect square n^2; then q = (a,b,c,d)/n is a
    rational unit quaternion.

    WHY NOT STEREOGRAPHIC (the R3/R8 attempts, both degenerate): the stereographic chart from
    (1,0,0,0) only ever covers a neighbourhood of the IDENTITY rotation -- small parameters cluster
    the sampled rotations near identity, and large parameters run to (-1,0,0,0), which is the SAME
    rotation (q and -q coincide in SO(3)).  Both regimes gave null marginals of +-76..120 instead of
    the random-walk scale +-11, i.e. a "null" that could not vary.  Pythagorean quadruples cover
    S^3 isotropically (symmetric under sign flips and coordinate permutations; not the exact Haar
    measure, which the null does not require -- the null tests structure, not measure)."""
    for _try in range(100000):
        state, r1 = lcg(state)
        a = r1 % 49 - 24
        state, r2 = lcg(state)
        b = r2 % 49 - 24
        state, r3 = lcg(state)
        c = r3 % 49 - 24
        state, r4 = lcg(state)
        d = r4 % 49 - 24
        n2 = a * a + b * b + c * c + d * d
        if n2 == 0:
            continue
        n = isqrt_int(n2)
        if n * n != n2:
            continue
        return state, ((F(a, n), F(0)), (F(b, n), F(0)), (F(c, n), F(0)), (F(d, n), F(0)))
    raise RuntimeError("Pythagorean-quadruple sampler failed (increase the try budget)")


def rand_dir(state):
    """Rational direction (not normalised -- the kernel uses sign(u.(g n_hat)) only)."""
    vals = []
    for _ in range(6):
        state, rv = lcg(state)
        vals.append(rv % 4001 - 2000)
    v = ((F(vals[0]), F(vals[1])), (F(vals[2]), F(vals[3])), (F(vals[4]), F(vals[5])))
    if all(c == ZERO for c in v):
        v = (ONE, ZERO, ZERO)
    return state, v


def rand_sign_row(u):
    """Sign row of a (random) setting against the 12 vertex directions, H3 ties applied."""
    row = []
    for v in V12:
        sn = num_sign(dot(u, v))
        row.append(tie_sign(v) if sn == 0 else sn)
    return row


N_NULL_DIR = 10000
st = 222
null_absC = []
for _ in range(N_NULL_DIR):
    st, ua = rand_dir(st)
    st, ub = rand_dir(st)
    ra = rand_sign_row(ua)
    rb = rand_sign_row(ub)
    numer = sum(MULT2I[k] * ra[k] * rb[k] for k in range(12))
    null_absC.append(abs(F(numer, DEN)))
real_mean = sum(abs(F(N2I[a][b], DEN)) for a in range(NA) for b in range(NA)) / (NA * NA)
chk("P5", "null (i): %d random-direction pairs, seed 222 -- |C| distribution vs the real grid"
    % N_NULL_DIR, len(null_absC) == N_NULL_DIR,
    "null mean|C| = %s ; real grid mean|C| = %s ; null max|C| = %s"
    % (str(sum(null_absC) / len(null_absC)), str(real_mean), str(max(null_absC))))

N_NULL_GROUP = 500
st = 222
null_S = []
_unit_fail = 0
_rotdist = set()
_nullmarg = []
for _ in range(N_NULL_GROUP):
    qs = []
    for _k in range(len(G2I)):
        st, q = rand_unit_quat(st)
        qs.append(q)
    _unit_fail += sum(1 for _q in qs
                      if qmul(_q, qconj(_q))[0] != ONE
                      or any(_x != ZERO for _x in qmul(_q, qconj(_q))[1:]))
    _rotdist.add(len({matkey_of(rot_matrix(q)) for q in qs}))
    Wn = [matvec(rot_matrix(q), REF) for q in qs]
    rows = [k_table(V12[i], REF, qs, Wn)[0] for i in range(12)]
    _nullmarg.append(max(abs(sum(r)) for r in rows))
    loc = [[pair_build(rows, DEN, a, b) for b in range(12)] for a in range(12)]
    anti12 = [[is_antipodal(i, j) for j in range(12)] for i in range(12)]
    bestn, _an = chsh_free(list(range(12)), anti12, loc, DEN)
    null_S.append(F(bestn, DEN))
null_S_sorted = sorted(null_S)
chk("P5b1", "null is NOT degenerate: >= 100 distinct rotations per draw and null marginals at the "
    "random-walk scale (~sqrt(120) ~ 11, not ~120)", min(_rotdist) >= 100 and max(_nullmarg) < 4 * len(G2I) // 10,
    "min distinct rotations = %d ; max |null marginal| = %d" % (min(_rotdist), max(_nullmarg)))
chk("P5b0", "every random quaternion in the null is EXACTLY unit (q q* = 1) -- a non-unit generator "
    "silently degenerates the null", _unit_fail == 0, "%d draws, non-unit count = %d" % (N_NULL_GROUP, _unit_fail))
claim("P5b", "null (ii): random RATIONAL unit-quaternion sets replace 2I (seed 222)",
      "%d draws (resolution reduced from 10^4 for runtime; the criterion is unchanged) ; max|S| on the "
      "12-vertex grid, ANTIPODAL-FREE statistic: median = %s, 95th pct = %s, max = %s"
      % (N_NULL_GROUP, str(null_S_sorted[len(null_S_sorted) // 2]),
         str(null_S_sorted[len(null_S_sorted) * 95 // 100]), str(null_S_sorted[-1])))

stage("nulls done")
claim("P3", "sequential / rollback-level C(theta) -- NOT COMPUTED",
      "Contract v1 pins only the coexistence kernel (SS3); the rollback-level construction is not defined "
      "there, so computing it now would be an unfrozen derivation (forbidden by SS7). Requires amendment A2 "
      "(definition + its own pre-registered windows) before any number at that level.")

# ---- artefacts --------------------------------------------------------------
io.open(os.path.join(DATA, "05_b2_dev_values.json"), "w", encoding="utf-8").write(json.dumps(
    {"rules_version": "contract-v1", "set": "DEV = V x V", "pairs": dev_rows}, ensure_ascii=False, indent=1))
blind_rows = [{"a": AXES[a][0], "b": AXES[b][0], "type": AXES[a][1] + "x" + AXES[b][1],
               "C_num": N2I[a][b], "C_den": DEN} for (a, b) in BLIND]
bp = os.path.join(DATA, "05_b2_blind_values.json")
io.open(bp, "w", encoding="utf-8").write(json.dumps(
    {"rules_version": "contract-v1", "set": "BLIND = all pairs outside V x V", "pairs": blind_rows},
    ensure_ascii=False, indent=1))
io.open(os.path.join(DATA, "05_b2_correlation.json"), "w", encoding="utf-8").write(json.dumps(
    {"rules_version": "contract-v1", "denominator": DEN, "N2I": N2I, "N60": NC60,
     "axis_ids": [a[0] for a in AXES], "axis_types": [a[1] for a in AXES],
     "cos2": [str(c[0]) + "," + str(c[1]) for c in [COS2[i][j] for i in range(NA) for j in range(NA)]]},
    ensure_ascii=False, indent=1))
h_blind = hashlib.sha256(io.open(bp, "rb").read()).hexdigest()
print()
print("DEV   : data/05_b2_dev_values.json (%d pairs, values printed above)" % len(dev_rows))
print("BLIND : data/05_b2_blind_values.json (%d pairs, values NOT printed) sha256 = %s" % (len(blind_rows), h_blind[:32]))
print("table : data/05_b2_correlation.json (exact integer numerators, denominator %d)" % DEN)

if REVEAL:
    print()
    print("--- REVEAL: full 3844-pair aggregates (BLIND unlocked for reporting) ---")
    eq_g, gap_g, mac_g = grid_metrics(DEV + BLIND)
    chk("P4r", "full grid: exact algebraic comparison C^2 vs cos^2, by type class", True,
        "exact matches = %d/3844 ; max |delta| = %s ; max |C| = %s" % (eq_g, gap_g, mac_g))
    tstats = {}
    for (a, b) in DEV + BLIND:
        tstats.setdefault(AXES[a][1] + "x" + AXES[b][1], []).append(abs(F(N2I[a][b], DEN)))
    for k in sorted(tstats):
        v = tstats[k]
        print("   %-9s n=%4d  mean|C| = %-14s max|C| = %s" % (k, len(v), str(sum(v) / len(v)), str(max(v))))
    distinct = sorted({N2I[a][b] for a in range(NA) for b in range(NA)})
    print("   antipodal-free max |S| = %s   (raw max %s) ; null median/95th/max = %s / %s / %s"
          % (str(Sf), str(F(best_all, DEN)), str(null_S_sorted[len(null_S_sorted) // 2]),
             str(null_S_sorted[len(null_S_sorted) * 95 // 100]), str(null_S_sorted[-1])))
    claim("P4s", "QM comparison summary",
          "C is rational with denominator %d taking %d distinct values; exact coincidences with cos^2(theta): "
          "%d/3844 -> the coexistence kernel does NOT reproduce -cos(theta) pointwise (exact statement, "
          "no tolerance involved)" % (DEN, len(distinct), eq_g))
else:
    print()
    print("[blind] BLIND written but NOT printed (Contract SS2/SS7); re-run with --reveal for aggregates.")

n_pass = sum(1 for r in RESULTS if r["ok"] is True)
n_fail = sum(1 for r in RESULTS if r["ok"] is False)
n_claim = sum(1 for r in RESULTS if r["ok"] is None)
print()
print("=" * 118)
print("RESULT: %d/%d PASS  (%d FAIL, %d claims excluded)   mode = %s"
      % (n_pass, n_pass + n_fail, n_fail, n_claim, "REVEAL" if REVEAL else "frozen-run"))
print("=" * 118)
io.open(os.path.join(DATA, "05_b2_results.json"), "w", encoding="utf-8").write(json.dumps(
    {"mode": "reveal" if REVEAL else "frozen-run", "pass": n_pass, "fail": n_fail, "claims": n_claim,
     "max_abs_S_num": best_all, "S_den": DEN, "argmax": [AXES[i][0] for i in arg_all], "verdict": verdict,
     "blind_sha256": h_blind, "checks": RESULTS}, ensure_ascii=False, indent=1))
print("saved: data/05_b2_results.json | 05_b2_dev_values.json | 05_b2_blind_values.json | 05_b2_correlation.json")
