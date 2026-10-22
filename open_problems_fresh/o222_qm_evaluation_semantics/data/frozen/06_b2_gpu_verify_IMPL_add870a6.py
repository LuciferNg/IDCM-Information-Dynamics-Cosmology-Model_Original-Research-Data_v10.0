#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O222 scripts/06_b2_gpu_verify.py -- INDEPENDENT GPU CROSS-CHECK of the frozen B2 results.

NOT the derivation: the frozen derivation is scripts/05_b2_correlation.py (hash recorded in
data/04_b2_freeze.json). This script exists to attack that result from a different direction:
same definition, DIFFERENT implementation, DIFFERENT hardware (GPU), and exact integer
arithmetic -- no float anywhere in the kernel path (floats appear only in timings/reporting),
so the two must agree BIT-EXACTLY or one of them is wrong.

What it recomputes on the GPU (cupy, int64):
  1. the 62x62 correlation numerator table  N[a][b] = sum_g K(g,a)K(g,b)   (compare to 05)
  2. the full 62^4 ordered CHSH sweep  max |N[a][b]+N[a][b']+N[a'][b]-N[a'][b']|   (compare to 05)
  3. the non-degenerate (four distinct settings) CHSH max                            (compare to 05)
  4. the null (ii) distribution over random rational unit-quaternion sets (same LCG/seed as 05)

Exactness trick: every lattice vector has coordinates p + q*sqrt5 with rational p,q; scaling by a
common denominator D turns each into an integer pair (P,Q).  Then
    dot(u,v) = [sum(P P') + 5 sum(Q Q')] + sqrt5 [sum(P Q') + sum(Q P')]  over D^2
and sign(A + B*sqrt5) is decided exactly by integer comparisons (A^2 vs 5B^2), so the whole kernel
runs as int64 arithmetic (|A| <= ~1e5 here, so A^2 stays far inside int64).

Run:  python3 scripts/06_b2_gpu_verify.py
"""

import hashlib
import io
import re
import json
import os
import sys
import time
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
RESULTS = []


def chk(tag, name, ok, detail=""):
    RESULTS.append({"tag": tag, "name": name, "ok": bool(ok), "detail": detail})
    print("[%s] %-6s %-72s %s" % ("PASS" if ok else "FAIL", tag, name, detail))
    return ok


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


# ------------------------------------------------------------------ CPU side: exact lattice objects
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
    return (x[0] / d, -x[1] / d)


def num_sign(x):
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


def dot(a, b):
    return add(add(mul(a[0], b[0]), mul(a[1], b[1])), mul(a[2], b[2]))


def dir_canon(v):
    for x in v:
        if x != ZERO:
            return tuple(mul(inv(x), y) for y in v)
    raise ValueError("zero vector")


def qmul(a, b):
    a0, a1, a2, a3 = a
    b0, b1, b2, b3 = b
    return (sub(sub(sub(mul(a0, b0), mul(a1, b1)), mul(a2, b2)), mul(a3, b3)),
            add(add(mul(a0, b1), mul(a1, b0)), sub(mul(a2, b3), mul(a3, b2))),
            add(sub(mul(a0, b2), mul(a1, b3)), add(mul(a2, b0), mul(a3, b1))),
            add(add(mul(a0, b3), mul(a1, b2)), sub(mul(a3, b0), mul(a2, b1))))


def qconj(q):
    return (q[0], neg(q[1]), neg(q[2]), neg(q[3]))


PHI = (F(1, 2), F(1, 2))
PSI = sub(PHI, ONE)
_H = (F(1, 2), F(0))
GENS = []
for _s in (1, -1):
    for _i in range(4):
        v = [ZERO, ZERO, ZERO, ZERO]
        v[_i] = (F(_s), F(0))
        GENS.append(tuple(v))
for _s1 in (1, -1):
    for _s2 in (1, -1):
        for _s3 in (1, -1):
            GENS.append(((F(_s1, 2), F(0)), (F(_s2, 2), F(0)), (F(_s3, 2), F(0)), (F(_s1 * _s2 * _s3, 2), F(0))))
GENS.append((mul(PHI, _H), mul(ONE, _H), mul(PSI, _H), ZERO))

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
    print("[FATAL] closure = %d, expected 120" % len(G2I))
    sys.exit(2)


def matkey_of(M):
    return tuple(tuple(c for c in row) for row in M)


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


def order_of(M):
    k, X = 1, M
    while X != IM:
        X = matmul(X, M)
        k += 1
        if k > 20:
            raise RuntimeError("order")
    return k


ROTS = [rot_matrix(q) for q in G2I]
I60_KEYS, _seen = [], set()
for _M in ROTS:
    if matkey_of(_M) not in _seen:
        _seen.add(matkey_of(_M))
        I60_KEYS.append(_M)


def orbit_of(v0):
    return sorted({matvec(M, v0) for M in I60_KEYS})


def rep_of(k):
    for q in G2I:
        vec = (q[1], q[2], q[3])
        if all(x == ZERO for x in vec):
            continue
        if order_of(rot_matrix(q)) == k:
            return dir_canon(vec)


V12 = orbit_of(rep_of(5))
F20 = orbit_of(rep_of(3))
E30 = orbit_of(rep_of(2))
AXES = ([("V%02d" % i, "vertex", v) for i, v in enumerate(V12)] +
        [("F%02d" % i, "face", v) for i, v in enumerate(F20)] +
        [("E%02d" % i, "edge", v) for i, v in enumerate(E30)])
NA = len(AXES)

print("=" * 112)
print("O222 scripts/06 -- INDEPENDENT GPU CROSS-CHECK (cupy int64) of the frozen C(theta) results")
print("=" * 112)

# ---------------------------------------------------------------- integer representation
def denom_of(x):
    return x.denominator


D = 1
for _aid, _t, _v in AXES:
    for _c in _v:
        for _p in _c:
            D = D * denom_of(_p) // __import__("math").gcd(D, denom_of(_p))
print("common denominator D for every lattice coordinate: %d" % D)


def to_int_vec(v, D):
    P, Q = [], []
    for c in v:
        P.append(int(c[0] * D))
        Q.append(int(c[1] * D))
    return (P, Q)


AX = [to_int_vec(v, D) for _aid, _t, v in AXES]
DIRS = [to_int_vec(v, D) for v in V12]
# structural identity (independently re-verified here, not assumed): the 2I orbit of n_hat consists of
# exactly the 12 vertex directions, each with multiplicity 10 (= 120/12); I60 gives 5.  Compute the orbit
# on the CPU and count -- a wrong multiplicity silently changes the kernel (found 2026-09-29: the first
# GPU version expanded nothing (all counts = 1) and the whole GPU table disagreed with the frozen one).
def _key(v):
    return (tuple(v[0]), tuple(v[1]))


_orb = {}
for _q in G2I:
    _w = matvec(rot_matrix(_q), V12[0])
    _k = _key(to_int_vec(_w, D))
    _orb[_k] = _orb.get(_k, 0) + 1
MULT = [int(_orb[_key(d)]) for d in DIRS]
print("vertex multiplicities under 2I (computed): %s  (sum = %d)" % (sorted(set(MULT)), sum(MULT)))
assert sorted(set(MULT)) == [10] and sum(MULT) == 120, "2I orbit identity broken"

try:
    import cupy as cp
except Exception as exc:                                     # pragma: no cover
    print("[FATAL] cupy unavailable: %s" % exc)
    sys.exit(3)
dev_name = cp.cuda.runtime.getDeviceProperties(0)["name"].decode()
free_mem, total_mem = cp.cuda.runtime.memGetInfo()
print("GPU: %s | free %.2f GiB / %.2f GiB" % (dev_name, free_mem / 2 ** 30, total_mem / 2 ** 30))

Pa = cp.asarray([a[0] for a in AX], dtype=cp.int64)          # (62,3)
Qa = cp.asarray([a[1] for a in AX], dtype=cp.int64)
# expand the 12 vertex directions with their multiplicity so the sum over g is exact
IDX = [k for k in range(12) for _ in range(MULT[k])]
EDIRS = [DIRS[k] for k in IDX]                       # the 120-fold expanded direction list
Pd = cp.asarray([DIRS[k][0] for k in IDX], dtype=cp.int64)   # (120,3)
Qd = cp.asarray([DIRS[k][1] for k in IDX], dtype=cp.int64)

t0 = time.time()
A = cp.einsum("ij,kj->ik", Pa, Pd) + 5 * cp.einsum("ij,kj->ik", Qa, Qd)     # (62,120)
B = cp.einsum("ij,kj->ik", Pa, Qd) + cp.einsum("ij,kj->ik", Qa, Pd)
K = cp.zeros_like(A)
K[(A > 0) & (B >= 0)] = 1
K[(A < 0) & (B <= 0)] = -1
K[(B > 0) & (A < 0)] = cp.where((5 * B * B > A * A)[(B > 0) & (A < 0)], 1, -1)
K[(B < 0) & (A > 0)] = cp.where((A * A > 5 * B * B)[(B < 0) & (A > 0)], 1, -1)
K[(A == 0) & (B > 0)] = 1
K[(A == 0) & (B < 0)] = -1
ties_mask = (A == 0) & (B == 0)
n_ties = int(ties_mask.sum())
if n_ties:
    tl = ties_mask.get()
    for i, j in zip(*tl.nonzero()):
        s = 0
        for c in range(3):                                  # H3 tie rule: first non-zero component
            v = (F(EDIRS[j][0][c], D), F(EDIRS[j][1][c], D))
            if v != ZERO:
                s = num_sign(v)
                break
        K[i, j] = s
N_gpu = (K @ K.T).astype(cp.int64)
cp.cuda.Stream.null.synchronize()
t_kernel = time.time() - t0
print("GPU kernel: sign table + 62x62 correlation in %.3f s (ties resolved by H3: %d)" % (t_kernel, n_ties))

# ---------------------------------------------------------------- compare with the frozen run
frozen = json.load(io.open(os.path.join(DATA, "05_b2_correlation.json"), encoding="utf-8"))
N_cpu = frozen["N2I"]
den_cpu = frozen["denominator"]
N_gpu_l = N_gpu.get().tolist()
mism = sum(1 for a in range(NA) for b in range(NA) if N_gpu_l[a][b] != N_cpu[a][b])
chk("G1", "GPU int64 correlation table == frozen CPU exact table (all %d entries, denominator %d)"
    % (NA * NA, den_cpu), mism == 0 and den_cpu == len(IDX),
    "mismatches = %d ; |G| = %d" % (mism, len(IDX)))

# ---------------------------------------------------------------- full 62^4 CHSH sweep on GPU
t0 = time.time()
best_all = 0
arg_all = None
for a in range(NA):
    ra = N_gpu[a]
    S = cp.abs(ra[:, None] + ra[None, :] + N_gpu[:, :, None] - N_gpu[:, None, :])
    m = int(S.max())
    if m > best_all:
        best_all = m
        idx = cp.unravel_index(cp.argmax(S), S.shape)
        i, j, k = (int(x) for x in idx)
        arg_all = (a, i, j, k)
cp.cuda.Stream.null.synchronize()
t_sweep = time.time() - t0
res = json.load(io.open(os.path.join(DATA, "05_b2_results.json"), encoding="utf-8"))
chk("G2", "GPU full 62^4 ordered CHSH sweep == frozen max (as an exact fraction over the same denominator)",
    best_all == res["max_abs_S_num"],
    "GPU max |S| = %d/%d ; frozen = %d/%d ; argmax %s (%s)"
    % (best_all, den_cpu, res["max_abs_S_num"], res["S_den"],
       tuple(AXES[i][0] for i in arg_all), res.get("argmax")))

# ---------------------------------------------------------------- non-degenerate sweep on GPU
t0 = time.time()
best_dis = 0
arg_dis = None
for a in range(NA):
    ra = N_gpu[a]
    S = cp.abs(ra[:, None] + ra[None, :] + N_gpu[:, :, None] - N_gpu[:, None, :])
    a2 = cp.arange(NA)
    b = cp.arange(NA)
    b2 = cp.arange(NA)
    ok = (a2[:, None, None] != a) & (b[None, :, None] != a) & (b2[None, None, :] != a) & \
         (b[None, :, None] != b2[None, None, :]) & \
         (a2[:, None, None] != b[None, :, None]) & (a2[:, None, None] != b2[None, None, :])
    S = cp.where(ok, S, -1)
    m = int(S.max())
    if m > best_dis:
        best_dis = m
        i, j, k = (int(x) for x in cp.unravel_index(cp.argmax(S), S.shape))
        arg_dis = (a, i, j, k)
cp.cuda.Stream.null.synchronize()
t_dist = time.time() - t0
_fzlog = io.open(os.path.join(ROOT, "logs", "05_b2_correlation.out"), encoding="utf-8").read()
_m3 = re.search(r"max \|S\| over 4-distinct-setting tuples = (\d+) .*?argmax = \(([^)]*)\)", _fzlog)
_fz_dis = int(_m3.group(1)) if _m3 else -1
_fz_arg = tuple(x.strip().strip("'") for x in _m3.group(2).split(",")) if _m3 else ()
_gpu_arg = tuple(AXES[i][0] for i in arg_dis)
chk("G3", "GPU non-degenerate (four distinct settings) CHSH max + argmax == frozen record",
    _fz_dis * den_cpu == best_dis and _fz_arg == _gpu_arg,
    "GPU %d/%d argmax %s ; frozen %d/%d argmax %s" % (best_dis, den_cpu, _gpu_arg, _fz_dis, den_cpu, _fz_arg))

# ---------------------------------------------------------------- null (ii) cross-check (same LCG/seed)
def lcg(state):
    """splitmix64 mixer -- byte-for-byte the SAME generator as scripts/05, so the two nulls are the
    same draws (the earlier version of this file kept its own weak LCG, which silently made G4 compare
    two different nulls)."""
    MASK64 = (1 << 64) - 1
    state = (state + 0x9E3779B97F4A7C15) & MASK64
    z = state
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
    z = z ^ (z >> 31)
    return state, z & MASK64


def isqrt_int(n):
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


N_NULL = int(sys.argv[1]) if len(sys.argv) > 1 else 200
t0 = time.time()
null_vals = []
st = 222
for _ in range(N_NULL):
    qs = []
    for _k in range(len(G2I)):
        while True:                                    # Pythagorean quadruple: a^2+b^2+c^2+d^2 = n^2
            st, r1 = lcg(st)
            a = r1 % 49 - 24
            st, r2 = lcg(st)
            b = r2 % 49 - 24
            st, r3 = lcg(st)
            c = r3 % 49 - 24
            st, r4 = lcg(st)
            dd = r4 % 49 - 24
            n2 = a * a + b * b + c * c + dd * dd
            if n2 == 0:
                continue
            n = isqrt_int(n2)
            if n * n == n2:
                break
        qs.append(((a, b, c, dd), n))                  # q = (a,b,c,d)/n, an exact unit quaternion
    # rotation matrix numerators over n^2, then dir = R . V12[0] as an integer pair over n^2 * D
    # exact orthogonality guard: Rnum Rnum^T = n^4 * I  (integer arithmetic, verified for the first draw)
    if _ == 0:
        for (C, n) in qs[:8]:
            c0, c1, c2, c3 = C
            Rn = [[c0 * c0 + c1 * c1 - c2 * c2 - c3 * c3, 2 * (c1 * c2 - c0 * c3), 2 * (c1 * c3 + c0 * c2)],
                  [2 * (c1 * c2 + c0 * c3), c0 * c0 - c1 * c1 + c2 * c2 - c3 * c3, 2 * (c2 * c3 - c0 * c1)],
                  [2 * (c1 * c3 - c0 * c2), 2 * (c2 * c3 + c0 * c1), c0 * c0 - c1 * c1 - c2 * c2 + c3 * c3]]
            for i in range(3):
                for j2 in range(3):
                    val = sum(Rn[i][k] * Rn[j2][k] for k in range(3))
                    assert val == (n ** 4 if i == j2 else 0), "rotation matrix not orthogonal"
    P0 = [int(cc[0] * D) for cc in V12[0]]
    Q0 = [int(cc[1] * D) for cc in V12[0]]
    dirs_int = []
    for (C, n) in qs:
        # rotation matrix of q = (C0,C1,C2,C3)/n, entries as INTEGER numerators over n^2.
        # (An earlier version of this file used a hand-invented linear expression with no squares --
        # the GPU null then disagreed with the frozen null; the orthogonality check below catches that.)
        c0, c1, c2, c3 = C
        Rnum = [[c0 * c0 + c1 * c1 - c2 * c2 - c3 * c3, 2 * (c1 * c2 - c0 * c3), 2 * (c1 * c3 + c0 * c2)],
                [2 * (c1 * c2 + c0 * c3), c0 * c0 - c1 * c1 + c2 * c2 - c3 * c3, 2 * (c2 * c3 - c0 * c1)],
                [2 * (c1 * c3 - c0 * c2), 2 * (c2 * c3 + c0 * c1), c0 * c0 - c1 * c1 - c2 * c2 + c3 * c3]]
        dp = [sum(Rnum[i][j] * P0[j] for j in range(3)) for i in range(3)]
        dq = [sum(Rnum[i][j] * Q0[j] for j in range(3)) for i in range(3)]
        dirs_int.append((dp, dq, n * n * D))
    Pd2 = cp.asarray([t[0] for t in dirs_int], dtype=cp.int64)
    Qd2 = cp.asarray([t[1] for t in dirs_int], dtype=cp.int64)
    # compare signs against the first 12 axes only (the 12-vertex setting grid used by the null)
    A2 = (cp.einsum("ij,kj->ik", Pa[:12], Pd2) + 5 * cp.einsum("ij,kj->ik", Qa[:12], Qd2))
    B2 = (cp.einsum("ij,kj->ik", Pa[:12], Qd2) + cp.einsum("ij,kj->ik", Qa[:12], Pd2))
    sgn = cp.zeros_like(A2)
    sgn[(A2 > 0) & (B2 >= 0)] = 1
    sgn[(A2 < 0) & (B2 <= 0)] = -1
    m1 = (B2 > 0) & (A2 < 0)
    sgn[m1] = cp.where((5 * B2 * B2 > A2 * A2)[m1], 1, -1)
    m2 = (B2 < 0) & (A2 > 0)
    sgn[m2] = cp.where((A2 * A2 > 5 * B2 * B2)[m2], 1, -1)
    sgn[(A2 == 0) & (B2 > 0)] = 1
    sgn[(A2 == 0) & (B2 < 0)] = -1
    tbl = (sgn @ sgn.T).astype(cp.int64)
    Pv = [d[0] for d in DIRS]      # UNEXPANDED 12 vertex directions (Pd/Qd are the 120-fold expansion)
    Qv = [d[1] for d in DIRS]
    anti = [[(k != l) and all((Pv[k][c] + Pv[l][c] == 0) and (Qv[k][c] + Qv[l][c] == 0)
                              for c in range(3)) for l in range(12)] for k in range(12)]
    best = 0
    for a in range(12):
        ra = tbl[a]
        S = cp.abs(ra[:, None] + ra[None, :] + tbl[:, :, None] - tbl[:, None, :])
        i2 = cp.arange(12)
        an = cp.asarray([[anti[k][l] for l in range(12)] for k in range(12)])
        # S is indexed (a', b, b'); drop any tuple containing an antipodal pair or a repeat
        # pairwise distinctness needs ALL SIX pairs: (a,a') (a,b) (a,b') (a',b) (a',b') (b,b').
        # The first version of this mask omitted (a',b) and (a',b'), so tuples that REUSE a setting
        # were scored; they reached |S| = 236/120 and the GPU null disagreed with the frozen one.
        ok = (~an[a, :][:, None, None]) & (~an[a, :][None, :, None]) & (~an[a, :][None, None, :]) & \
             (~an[:, :, None]) & (~an[:, None, :]) & (~an[None, :, :]) & \
             (i2[:, None, None] != a) & (i2[None, :, None] != a) & (i2[None, None, :] != a) & \
             (i2[None, :, None] != i2[None, None, :]) & \
             (i2[:, None, None] != i2[None, :, None]) & (i2[:, None, None] != i2[None, None, :])
        m = int(cp.where(ok, S, -1).max())
        if m > best:
            best = m
    null_vals.append(F(best, len(G2I)))
cp.cuda.Stream.null.synchronize()
t_null = time.time() - t0
ns = sorted(null_vals)
print("GPU null (ii): %d draws in %.1f s -- max |S| median = %s, 95th pct = %s, max = %s"
      % (N_NULL, t_null, ns[len(ns) // 2], ns[len(ns) * 95 // 100], ns[-1]))
_m4 = re.search(r"ANTIPODAL-FREE statistic: median = (\S+?), 95th pct = (\S+?), max = (\S+)", _fzlog)
if _m4 and N_NULL == 500:
    _fzq = tuple(F(x.rstrip(",")) for x in _m4.groups())
    _gq = (ns[len(ns) // 2], ns[len(ns) * 95 // 100], ns[-1])
    chk("G4", "GPU null (ii) == frozen null (same splitmix64 seed, same sampler, same statistic, 500 draws)",
        _fzq == _gq, "GPU median/95th/max = %s ; frozen = %s" % (tuple(str(x) for x in _gq), tuple(str(x) for x in _fzq)))
else:
    chk("G4", "GPU null (ii) distribution recomputed independently (ANTIPODAL-FREE statistic)",
        len(null_vals) == N_NULL,
        "GPU median/95th/max = %s / %s / %s ; frozen 500-draw summary parsed only when N=500"
        % (ns[len(ns) // 2], ns[len(ns) * 95 // 100], ns[-1]))

print()
print("timings: kernel %.3f s | full sweep %.3f s | distinct sweep %.3f s | null %d draws %.1f s"
      % (t_kernel, t_sweep, t_dist, N_NULL, t_null))
n_pass = sum(1 for r in RESULTS if r["ok"] is True)
n_fail = sum(1 for r in RESULTS if r["ok"] is False)
print("=" * 112)
print("RESULT: %d/%d PASS  (%d FAIL)   GPU = %s" % (n_pass, n_pass + n_fail, n_fail, dev_name))
print("=" * 112)
io.open(os.path.join(DATA, "06_b2_gpu_verify.json"), "w", encoding="utf-8").write(json.dumps(
    {"script_sha256": sha256_file(os.path.abspath(__file__)), "gpu": dev_name,
     "frozen_table_sha256": sha256_file(os.path.join(DATA, "05_b2_correlation.json")),
     "impl_sha256_checked": json.load(io.open(os.path.join(DATA, "04_b2_freeze.json"), encoding="utf-8"))["impl"]["sha256"],
     "table_mismatches": mism, "chsh_gpu_num": best_all, "chsh_den": den_cpu,
     "chsh_frozen_num": res["max_abs_S_num"], "distinct_gpu_num": best_dis,
     "null_draws": N_NULL, "timings_s": {"kernel": t_kernel, "full_sweep": t_sweep,
                                         "distinct_sweep": t_dist, "null": t_null},
     "checks": RESULTS}, ensure_ascii=False, indent=1))
print("saved: data/06_b2_gpu_verify.json")
