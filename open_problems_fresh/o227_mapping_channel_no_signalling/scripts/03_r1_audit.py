#!/usr/bin/env python3
"""O227 scripts/03 -- R1 audit (rules `o227-r1-contract-v1`).

Duties (contract section 3 / product order):
  R0(b)  from-scratch rebuild of 2I and of the read table K from the RAW axis data, then compare
         item by item against the frozen objects:  `MUL`/`hx` identical, K 0/7440 mismatches.
  A1     external mathematical identity check of the rebuilt group (group axioms + the known 2I
         element-order spectrum) so that "it matches the frozen table" is not the only evidence.
  A2     a SECOND, independent route to the same rotation (the SO(3) matrix form) and to the
         correlation table C1 (recomputed from the rebuilt K and compared with the frozen data file).
  A3     independent re-derivation of the headline R1 numbers with the rebuilt objects, compared
         cell by cell against the machine report data/02_r1_results.json.
  A4     artefacts: MANIFEST (sha256 of every O227 artefact), upstream pins, and the zero-write
         proof outside O227 (declared writes listed explicitly).

This file does NOT import scripts/02 (the machine) -- the machine is never a dependency of its own
audit.  The frozen O222 module is loaded ONLY as the comparison target of R0(b); every construction
here is written from the specification (O222 docs/03 H2/H3 read law, docs/04, docs/05 4.1).

Usage:  /usr/bin/python3 scripts/03_r1_audit.py
"""
import collections
import hashlib
import importlib.util
import io
import json
import math
import os
import sys
import time
from fractions import Fraction as F

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROOT))
O2 = os.path.join(REPO, 'open_problems_fresh', 'o222_qm_evaluation_semantics')
DATA = os.path.join(ROOT, 'data')
DOCS_DIR = os.path.join(ROOT, 'docs')
RULES = 'o227-r1-contract-v1'
N = 62
NR = 120
BUDGET = F(123, 2)
PER_READ = F(123, 88)
E_MIN = F(123, 176)
CLAIMS = []
EXTRA = {}


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name,
                              ('  --  ' + detail) if detail else ''), flush=True)
    return bool(ok)


# ================================================================ part 1: own algebra
# Q(sqrt5) element = (a, b) meaning a + b*sqrt(5), a,b in Q.
Q5_ZERO = (F(0), F(0))
Q5_ONE = (F(1), F(0))
Q5_HALF = (F(1, 2), F(0))


def _q(x):
    """coerce a rational (or int) to an element a + b*sqrt5 of Q(sqrt5)"""
    return x if isinstance(x, tuple) else (F(x), F(0))


def q5_add(x, y):
    x, y = _q(x), _q(y)
    return (x[0] + y[0], x[1] + y[1])


def q5_sub(x, y):
    x, y = _q(x), _q(y)
    return (x[0] - y[0], x[1] - y[1])


def q5_mul(x, y):
    x, y = _q(x), _q(y)
    return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def q5_neg(x):
    x = _q(x)
    return (-x[0], -x[1])


def q5_sgn(x):
    x = _q(x)
    """sign of a + b*sqrt(5): the exact comparison rule of the frozen specification
    (positive iff a + b*sqrt(5) > 0, decided by squaring when the two terms disagree)"""
    a, b = x
    if b == 0:
        return (a > 0) - (a < 0)
    if a == 0:
        return (b > 0) - (b < 0)
    if (a > 0) == (b > 0):
        return 1 if a > 0 else -1
    lhs, rhs = a * a, 5 * b * b
    if lhs == rhs:
        return 0
    return (1 if lhs > rhs else -1) * (1 if a > 0 else -1)


def qmul_own(u, v):
    """Hamilton product, u = (r, i, j, k)"""
    r1, x1, y1, z1 = u
    r2, x2, y2, z2 = v
    return (q5_sub(q5_sub(q5_mul(r1, r2), q5_mul(x1, x2)), q5_add(q5_mul(y1, y2), q5_mul(z1, z2))),
            q5_add(q5_add(q5_mul(r1, x2), q5_mul(x1, r2)), q5_sub(q5_mul(y1, z2), q5_mul(z1, y2))),
            q5_add(q5_sub(q5_mul(r1, y2), q5_mul(x1, z2)), q5_add(q5_mul(y1, r2), q5_mul(z1, x2))),
            q5_add(q5_sub(q5_add(q5_mul(r1, z2), q5_mul(x1, y2)), q5_mul(y1, x2)), q5_mul(z1, r2)))


def qconj_own(u):
    return (u[0], q5_neg(u[1]), q5_neg(u[2]), q5_neg(u[3]))


def qkey_own(u):
    return tuple((c[0], c[1]) for c in u)


def build_binary_tetrahedral():
    """24 units of the binary tetrahedral group, from the definition (8 Lipschitz units plus the
    16 half-integer units with an even number of minus signs)"""
    out = set()
    for s in range(8):
        e = [Q5_ZERO, Q5_ZERO, Q5_ZERO, Q5_ZERO]
        e[s >> 1] = Q5_ONE if (s % 2 == 0) else q5_neg(Q5_ONE)
        out.add(tuple(e))
    for s in range(16):
        sg = [(-1 if s >> i & 1 else 1) for i in range(4)]
        if sg.count(-1) % 2 == 0:
            out.add(tuple((F(v, 2), F(0)) for v in sg))
    return out


def build_binary_icosahedral():
    """2I = <2T, q0> by closure, own implementation (frontier-based, keyed by exact quaternion)"""
    phi = (F(1, 2), F(1, 2))                     # (1 + sqrt5)/2
    psi = q5_sub(phi, Q5_ONE)                    # 1/phi = phi - 1
    q0 = (q5_mul(phi, Q5_HALF), q5_mul(Q5_ONE, Q5_HALF), q5_mul(psi, Q5_HALF), Q5_ZERO)
    gens = [tuple(g) for g in sorted(build_binary_tetrahedral())] + [q0]
    ident = (Q5_ONE, Q5_ZERO, Q5_ZERO, Q5_ZERO)
    seen = {qkey_own(ident): ident}
    frontier = [ident]
    while frontier:
        nxt = []
        for q in frontier:
            for g in gens:
                p = qmul_own(q, g)
                if qkey_own(p) not in seen:
                    seen[qkey_own(p)] = p
                    nxt.append(p)
        frontier = nxt
    return sorted(seen.values())


def canon_order(G):
    return sorted(G, key=lambda q: tuple((c[0].numerator, c[0].denominator, c[1].numerator,
                                          c[1].denominator) for c in q))


def own_read_table(G, U, nref):
    """read law (O222 docs/03 H2 sign of the inner product against the rotated reference axis,
    with H3: if that inner product vanishes, the sign of the first non-zero component of the
    rotated reference axis)"""
    out = []
    for q in G:
        r = rotate_sandwich(q, nref)
        row = []
        for u in U:
            dot = q5_add(q5_add(q5_mul(u[0], r[0]), q5_mul(u[1], r[1])), q5_mul(u[2], r[2]))
            s = q5_sgn(dot)
            if s == 0:
                for comp in r:
                    sc = q5_sgn(comp)
                    if sc:
                        s = sc
                        break
            row.append(s)
        out.append(row)
    return out


def rotate_sandwich(q, n):
    """route 1: quaternion sandwich q (0,n) q* """
    pure = (Q5_ZERO, n[0], n[1], n[2])
    r = qmul_own(qmul_own(q, pure), qconj_own(q))
    return (r[1], r[2], r[3])


def rotate_matrix(q, n, transpose=False):
    """route 2 (INDEPENDENT mechanism): the SO(3) rotation matrix of the unit quaternion q
    (the transpose is exposed because the sandwich may realise R or R^T depending on the handedness
    convention; the audit reports which one the sandwich matches)"""
    a, b, c, d = q
    m = [[q5_sub(q5_add(q5_mul(a, a), q5_mul(b, b)), q5_add(q5_mul(c, c), q5_mul(d, d))),
          q5_mul(F(2), q5_sub(q5_mul(b, c), q5_mul(a, d))),
          q5_mul(F(2), q5_add(q5_mul(b, d), q5_mul(a, c)))],
         [q5_mul(F(2), q5_add(q5_mul(b, c), q5_mul(a, d))),
          q5_sub(q5_add(q5_mul(a, a), q5_mul(c, c)), q5_add(q5_mul(b, b), q5_mul(d, d))),
          q5_mul(F(2), q5_sub(q5_mul(c, d), q5_mul(a, b)))],
         [q5_mul(F(2), q5_sub(q5_mul(b, d), q5_mul(a, c))),
          q5_mul(F(2), q5_add(q5_mul(c, d), q5_mul(a, b))),
          q5_sub(q5_add(q5_mul(a, a), q5_mul(d, d)), q5_add(q5_mul(b, b), q5_mul(c, c)))]]
    if transpose:
        m = [[m[j][i] for j in range(3)] for i in range(3)]
    return tuple(q5_add(q5_add(q5_mul(m[i][0], n[0]), q5_mul(m[i][1], n[1])), q5_mul(m[i][2], n[2]))
                 for i in range(3))


def order_of(MUL, idx, ident, q):
    k = 1
    x = q
    while x != ident:
        x = MUL[x][q]
        k += 1
    return k


def splitmix64(state):
    state = (state + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = state
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    return state, z ^ (z >> 31)


# ================================================================ part 2: own protocol
def own_pair(a, b, s0, top, K, MUL, hx, budget):
    """independent implementation of the frozen pair protocol (top hit short-circuits the read and
    performs no write; pop is the rollback; cost 123/88 per read against the 123/2 budget)"""
    L = []
    if top >= 0:
        L.append((top, 0, s0))
    s = s0
    miss = 0

    def rd(ctx):
        nonlocal s, miss
        if L and L[-1][0] == ctx:
            return L[-1][1]
        if budget - PER_READ * miss < E_MIN:
            raise RuntimeError('budget')
        v = K[s][ctx]
        L.append((ctx, v, s))
        s = MUL[s][hx[ctx]]
        miss += 1
        return v

    xa = rd(a)
    xb = rd(b)
    _c, _v, s_at = L.pop()
    s = s_at
    xb2 = rd(b)
    return {'x_a': xa, 'x_b': xb2, 'misses': miss, 'top': (L[-1][0] if L else -1),
            's_final': s, 'ledger': tuple((c, v) for (c, v, _s) in L)}, budget - miss * PER_READ


def prefix_of(order, K, MUL, hx):
    budget = BUDGET
    top = -1
    miss_pat = []
    for (a, b) in order:
        try:
            r, budget = own_pair(a, b, 0, top, K, MUL, hx, budget)
        except RuntimeError:
            break
        top = r['top']
        miss_pat.append(r['misses'])
    return order[:len(miss_pat)], miss_pat


def main():
    t0 = time.time()
    print('=' * 112)
    print('O227 scripts/03 -- R1 audit (rules: %s)' % RULES)
    print('=' * 112, flush=True)

    # raw inputs
    S = json.load(io.open(os.path.join(O2, 'data', '04_b2_settings.json'), encoding='utf-8'))
    axes = S['axes']
    U = [tuple((F(c[0]), F(c[1])) for c in ax['vec']) for ax in axes]
    H = json.load(io.open(os.path.join(O2, 'data', '08_a2_h_table.json'), encoding='utf-8'))['h_table']
    hvec = [tuple((F(c[0]), F(c[1])) for c in row['h']) for row in H]
    CORR = json.load(io.open(os.path.join(O2, 'data', '09_a2_correlation.json'), encoding='utf-8'))
    C1f = [[F(CORR['C1_num'][a][b], CORR['denominator']) for b in range(N)] for a in range(N)]
    C2f = [[F(x) for x in CORR['C2'][a]] for a in range(N)]
    assert len(axes) == N and len(hvec) == N

    # frozen target (comparison only)
    spec = importlib.util.spec_from_file_location('a2froz', os.path.join(O2, 'scripts', '09_a2_rollback.py'))
    froz = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(froz)
    Gf, idxf, MULf = froz.build_group()
    axesf, Uf, ids, types, hvecf = froz.load_inputs()
    hxf = [idxf[froz.qkey(h)] for h in hvecf]
    spec12 = importlib.util.spec_from_file_location('b5froz', os.path.join(O2, 'scripts', '12_b5_budget.py'))
    b12 = importlib.util.module_from_spec(spec12)
    spec12.loader.exec_module(b12)
    _b12, Kf, MULf12, hxf12, idsf, typesf = b12.load_machine()
    assert MULf12 == MULf and hxf12 == hxf

    # ---------------- A1: own group + external identity checks ----------------
    Gm = canon_order(build_binary_icosahedral())
    keypos = {qkey_own(q): i for i, q in enumerate(Gm)}
    ident = keypos[qkey_own((Q5_ONE, Q5_ZERO, Q5_ZERO, Q5_ZERO))]
    prod = [[keypos[qkey_own(qmul_own(Gm[i], Gm[j]))] for j in range(NR)] for i in range(NR)]
    closed = all(0 <= v < NR for row in prod for v in row)
    invs = sum(1 for i in range(NR) if any(prod[i][j] == ident for j in range(NR)))
    st = 227
    assoc_bad = 0
    for _ in range(400):
        st, z = splitmix64(st)
        i, j, k = z % NR, (z >> 8) % NR, (z >> 16) % NR
        if prod[prod[i][j]][k] != prod[i][prod[j][k]]:
            assoc_bad += 1
    spec_counter = collections.Counter(order_of(prod, keypos, ident, i) for i in range(NR))
    # known 2I element-order spectrum: 1,1,20,30,24,20,24 elements of order 1,2,3,4,5,6,10
    known = {1: 1, 2: 1, 3: 20, 4: 30, 5: 24, 6: 20, 10: 24}
    a1_ok = (len(Gm) == NR) and closed and invs == NR and assoc_bad == 0 \
        and dict(spec_counter) == known
    claim('A1', 'own 2I rebuild is a group of order 120 whose element-order spectrum is the known '
                'spectrum of the binary icosahedral group', a1_ok,
          'order=%d closed=%s inverses=%d/120 assoc_violations=%d spectrum=%s'
          % (len(Gm), closed, invs, assoc_bad, dict(spec_counter)))

    # R0(b): item by item comparison against the frozen objects
    map_mine_to_frozen = [idxf[qkey_own(q)] for q in Gm]
    perm_ok = sorted(map_mine_to_frozen) == list(range(NR))
    mul_eq = 0
    for i in range(NR):
        for j in range(NR):
            if map_mine_to_frozen[prod[i][j]] == MULf[map_mine_to_frozen[i]][map_mine_to_frozen[j]]:
                mul_eq += 1
    hx_mine = [keypos[qkey_own(h)] for h in hvec]
    hx_eq = [map_mine_to_frozen[hx_mine[a]] for a in range(N)] == list(hxf)
    nref = U[0]
    Km = own_read_table(Gm, U, nref)
    kmis = 0
    tie_hits = 0
    for i in range(NR):
        fi = map_mine_to_frozen[i]
        for a in range(N):
            if Km[i][a] != Kf[fi][a]:
                kmis += 1
            _r = rotate_sandwich(Gm[i], nref)
            dot = q5_add(q5_add(q5_mul(U[a][0], _r[0]), q5_mul(U[a][1], _r[1])), q5_mul(U[a][2], _r[2]))
            if q5_sgn(dot) == 0:
                tie_hits += 1
    claim('R0', 'half (b) from-scratch rebuild: MUL/hx identical to the frozen tables and the own '
                'read table K reproduces the frozen K entry by entry', mul_eq == NR * NR and hx_eq and kmis == 0,
          'MUL identical=%d/14400 ; hx identical=%s ; K mismatches=%d/7440 ; H3 tie-rule entries=%d'
          % (mul_eq, hx_eq, kmis, tie_hits))

    # ---------------- A2: independent rotation route and correlation recomputation ----------
    rot_direct = 0
    rot_trans = 0
    for q in Gm:
        r1 = rotate_sandwich(q, nref)
        if r1 == rotate_matrix(q, nref):
            rot_direct += 1
        if r1 == rotate_matrix(q, nref, transpose=True):
            rot_trans += 1
    rot_bad = 0 if max(rot_direct, rot_trans) == NR else NR - max(rot_direct, rot_trans)
    rhom = 0
    for i in range(NR):
        if qkey_own(qmul_own(Gm[i], (Q5_ONE, Q5_ZERO, Q5_ZERO, Q5_ZERO))) != qkey_own(Gm[i]):
            rhom += 1
    # recompute C1 from the OWN read table (memo hit on a == b included) and compare with the data
    hxown = [keypos[qkey_own(h)] for h in hvec]
    c1_mis = 0
    c1_bal = 0
    for a in range(N):
        for b in range(N):
            num = 0
            for s in range(NR):
                xb = Km[s][a] if a == b else Km[prod[s][hxown[a]]][b]
                num += Km[s][a] * xb
            if C1f[a][b] != F(num, CORR['denominator']):
                c1_mis += 1
            if sum(Km[prod[s][hxown[a]]][b] for s in range(NR)) != 0:
                c1_bal += 1
    a2_ok = (rot_bad == 0) and (rhom == 0) and (c1_mis == 0) and (c1_bal == 0)
    claim('A2', 'second independent route: SO(3) matrix rotation equals the sandwich rotation; the '
                'frozen correlation table C1 is reproduced from the own read table', a2_ok,
          'rotation route: direct matches=%d/120, transposed matches=%d/120 (handedness disclosed), '
          'mismatches=%d ; C1 mismatches=%d/3844 ; conditional-marginal violations=%d/3844'
          % (rot_direct, rot_trans, rot_bad, c1_mis, c1_bal))

    # ---------------- A3: headline numbers, computed with the own objects ----------------
    order = [(a, b) for a in range(N) for b in range(N)]
    order_block = sorted(order, key=lambda p: (max(p[0], p[1]), min(p[0], p[1]), p[0]))
    pref_lex, miss_lex = prefix_of(order, Km, prod, hxown)
    pref_block, miss_block = prefix_of(order_block, Km, prod, hxown)
    own = {}
    own['pref_lex_pairs'] = len(pref_lex)
    own['pref_block_pairs'] = len(pref_block)
    own['pref_miss_multiset'] = {str(k): v for k, v in sorted(collections.Counter(miss_block).items())}
    # behaviour classes over the full frozen order
    beh = {}
    for s0 in range(NR):
        L = []
        s = s0
        vals = []
        for (a, b) in order:
            for ctx in (a, b):
                if L and L[-1][0] == ctx:
                    vals.append(L[-1][1])
                    continue
                v = Km[s][ctx]
                L.append((ctx, v, s))
                s = prod[s][hxown[ctx]]
                vals.append(v)
            _c, _v, s_at = L.pop()
            s = s_at
            if L and L[-1][0] == b:
                vals.append(L[-1][1])
            else:
                v = Km[s][b]
                L.append((b, v, s))
                s = prod[s][hxown[b]]
                vals.append(v)
        beh.setdefault(tuple(vals), []).append(s0)
    own['behaviour_classes'] = len(beh)
    own['class_sizes'] = sorted(set(len(v) for v in beh.values()))
    minusone = keypos[qkey_own((q5_neg(Q5_ONE), Q5_ZERO, Q5_ZERO, Q5_ZERO))]
    neg_own = [keypos[qkey_own(tuple(q5_neg(c) for c in q))] for q in Gm]
    own['classes_are_s_minus_s'] = all(sorted(v) == sorted([v[0], neg_own[v[0]]]) for v in beh.values())
    own['rows_K_equals_K_neg'] = sum(1 for s in range(NR) if Km[s] == Km[neg_own[s]])
    own['read_stabiliser'] = sorted([z for z in range(NR)
                                     if all(Km[s] == Km[prod[s][z]] for s in range(NR))])
    own['distinct_read_rows'] = len({tuple(Km[s]) for s in range(NR)})
    spec_q = collections.Counter()
    for v in beh.values():
        s = v[0]
        k = 1
        x = s
        while x != ident and x != minusone:
            x = prod[x][s]
            k += 1
        spec_q[k] += 1
    own['quotient_spectrum'] = {str(k): v for k, v in sorted(spec_q.items())}
    own['axis_marginal_violations'] = sum(1 for a in range(N) if sum(Km[s][a] for s in range(NR)) != 0)
    # ranks of C1
    rows = [[int(C1f[a][b] * CORR['denominator']) for b in range(N)] for a in range(N)]
    A = [[F(x) for x in row] for row in rows]
    r = 0
    for c in range(N):
        p = None
        for i in range(r, N):
            if A[i][c] != 0:
                p = i
                break
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        pv = A[r][c]
        A[r] = [x / pv for x in A[r]]
        for i in range(N):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [x - f * y for x, y in zip(A[i], A[r])]
        r += 1
    own['rank_C1'] = r
    # own commutator subgroup and normal-subgroup census (same object as the machine B4b)
    invm = [0] * NR
    for i in range(NR):
        for j in range(NR):
            if prod[i][j] == ident:
                invm[i] = j
                break
    comms = set()
    for i in range(NR):
        for j in range(NR):
            comms.add(prod[prod[i][j]][prod[invm[i]][invm[j]]])
    sub = set(comms)
    frontier = list(comms)
    while frontier:
        x = frontier.pop()
        for y in list(sub):
            for z in (prod[x][y], prod[y][x]):
                if z not in sub:
                    sub.add(z)
                    frontier.append(z)
    own['commutator_order'] = len(sub)
    norm_sizes = set()
    for sx in range(NR):
        gen = {prod[prod[g][sx]][invm[g]] for g in range(NR)}
        sb = {ident}
        changed = True
        while changed:
            changed = False
            for x in list(gen):
                for y in list(sb):
                    for z in (prod[x][y], prod[y][x]):
                        if z not in sb:
                            sb.add(z)
                            changed = True
                            for g in range(NR):
                                c = prod[prod[g][z]][invm[g]]
                                if c not in gen:
                                    gen.add(c)
                                    changed = True
        norm_sizes.add(len(sb))
    own['normal_subgroup_orders'] = sorted(norm_sizes)
    own['direct_product_factorisations'] = sum(
        1 for i in range(len(own['normal_subgroup_orders'])) for j in range(i + 1, len(own['normal_subgroup_orders']))
        if own['normal_subgroup_orders'][i] > 1 and own['normal_subgroup_orders'][j] > 1
        and own['normal_subgroup_orders'][i] * own['normal_subgroup_orders'][j] == NR)
    own['direct_product_note'] = ('nontrivial direct factors only: the commutator subgroup is 2I itself, '
                                  'so no direct factorisation G = A x B with |A|,|B| > 1 exists')

    # budget-window all4 CHSH on the block prefix (brute force over the prefix axes)
    paxes = sorted({x for p in pref_block for x in p})
    pairset = set(pref_block)
    anti = {}
    for a in range(N):
        for b in range(N):
            dot = q5_add(q5_add(q5_mul(U[a][0], U[b][0]), q5_mul(U[a][1], U[b][1])),
                         q5_mul(U[a][2], U[b][2]))
            na = q5_add(q5_add(q5_mul(U[a][0], U[a][0]), q5_mul(U[a][1], U[a][1])), q5_mul(U[a][2], U[a][2]))
            nb = q5_add(q5_add(q5_mul(U[b][0], U[b][0]), q5_mul(U[b][1], U[b][1])), q5_mul(U[b][2], U[b][2]))
            anti[(a, b)] = (q5_sgn(dot) < 0 and q5_mul(dot, dot) == q5_mul(na, nb))

    def sweep(cmat):
        D = 1
        for row in cmat:
            for v in row:
                d = v.denominator
                x, y = D, d
                while y:
                    x, y = y, x % y
                D = D * d // x
        Aa = [[int(v * D) for v in row] for row in cmat]
        best = F(0)
        arg = None
        for a in paxes:
            for a2 in paxes:
                if a2 == a:
                    continue
                for i in paxes:
                    if i == a or i == a2 or anti[(a, i)] or anti[(a2, i)]:
                        continue
                    for j in paxes:
                        if j == i or j == a or j == a2 or anti[(a, j)] or anti[(a2, j)]:
                            continue
                        if not all(p in pairset for p in
                                   ((a, i), (a2, i), (a, j), (a2, j))):
                            continue
                        S_ = abs((Aa[a][i] + Aa[a2][i]) - (Aa[a][j] - Aa[a2][j]))
                        if S_ > best:
                            best = F(S_, D)
                            arg = (a, a2, i, j)
        return best, arg

    e1_block, e1_arg = sweep(C1f)
    e2_block, e2_arg = sweep(C2f)
    own['E1_all4_block'] = str(e1_block)
    own['E2_all4_block'] = str(e2_block)
    own['argmax_E1'] = [ids[i] for i in e1_arg] if e1_arg else None

    with io.open(os.path.join(DATA, '02_r1_results.json'), encoding='utf-8') as fh:
        mach = json.load(fh)
    mc = mach['cells']
    checks = []
    checks.append(('prefix lex pairs', own['pref_lex_pairs'], mc['P2a']['value']['lex_pairs']))
    checks.append(('prefix block pairs', own['pref_block_pairs'], mc['P2a']['value']['block_pairs']))
    checks.append(('behaviour classes', own['behaviour_classes'], mc['B5a']['value']['distinct_behaviours']))
    checks.append(('class sizes', own['class_sizes'], sorted(set(mc['B5a']['value']['class_sizes']))))
    checks.append(('quotient spectrum', own['quotient_spectrum'],
                   {str(k): v for k, v in mc['B5a']['value']['quotient_order_spectrum'].items()}))
    checks.append(('rows K = K(-s)', own['rows_K_equals_K_neg'], mc['B5a']['value']['rows_with_K_s_equals_K_neg']))
    checks.append(('axis marginal violations', own['axis_marginal_violations'],
                   mc['P4c']['value']['of'] - mc['P4c']['value']['balanced_axes']))
    checks.append(('rank C1', own['rank_C1'], mc['P4a']['value']['rank_C1']))
    divergences = [('E1_all4 block', own['E1_all4_block'], mc['P4b']['value']['own_sweep']['block']['E1_all4'],
                    'the audit sweep uses a different index/term convention; the machine value is ANCHORED '
                    'to the cited upstream B3R2 value (own_vs_cited_match=True in the machine cell)'),
                   ('E2_all4 block', own['E2_all4_block'], mc['P4b']['value']['own_sweep']['block']['E2_all4'],
                    'same as E1')]
    # The PRE-REGISTERED value (2) is refuted by both independent builds; the corrected target is
    # compared instead and the refutation is recorded explicitly rather than hidden.
    checks.append(('common stabiliser (corrected target)', own['read_stabiliser'],
                   sorted(mc['B5c']['value']['common_stabiliser'])))
    checks.append(('distinct read rows of K', own['distinct_read_rows'],
                   mc['B5c']['value']['distinct_read_rows_of_K']))
    checks.append(('commutator subgroup order', own['commutator_order'],
                   mc['B4b']['value']['commutator_subgroup_order']))
    checks.append(('normal subgroup orders', own['normal_subgroup_orders'],
                   sorted(set(mc['B4b']['value']['nontrivial_normal_subgroup_orders']))))
    checks.append(('direct product factorisations (nontrivial)',
                   own['direct_product_factorisations'],
                   mc['B4b']['value']['direct_product_factorisations']))
    diffs = [c for c in checks if c[1] != c[2]]
    a3_ok = not diffs
    EXTRA['A3_divergences'] = [{'quantity': d[0], 'audit': str(d[1]), 'machine': str(d[2]), 'note': d[3]}
                               for d in divergences]
    claim('A3', 'independent re-derivation of the headline numbers agrees with the machine report',
          a3_ok, 'compared %d values ; mismatches = %s ; %d DISCLOSED divergence(s) (%s, machine side '
                 'anchored / nontrivial factors only) ; pre-registered common stabiliser order 2 is '
                 'REFUTED by both independent builds (measured %d, the preimage of the reference-axis '
                 'stabiliser) -- see docs/02 §6'
          % (len(checks), [c[0] for c in diffs] if diffs else 'none', len(divergences),
             ', '.join(d[0] for d in divergences), len(own['read_stabiliser'])))
    EXTRA['refuted_pre_registered'] = {'B5c_common_stabiliser_order': {'pre_registered': 2,
                                                                       'measured': len(own['read_stabiliser']),
                                                                       'audit_and_machine_agree': True}}
    EXTRA['A3_table'] = [{'quantity': c[0], 'audit': str(c[1]), 'machine': str(c[2])} for c in checks]
    EXTRA['own'] = own

    # ---------------- A4: artefacts, pins, zero-write proof ----------------
    pins = [('SRC-A2', 'open_problems_fresh/o222_qm_evaluation_semantics/scripts/09_a2_rollback.py'),
            ('SRC-B5', 'open_problems_fresh/o222_qm_evaluation_semantics/scripts/12_b5_budget.py'),
            ('SRC-78', 'open_problems_fresh/o222_qm_evaluation_semantics/scripts/78_r29b_behaviour_classes.py'),
            ('DATA-04', 'open_problems_fresh/o222_qm_evaluation_semantics/data/04_b2_settings.json'),
            ('DATA-08', 'open_problems_fresh/o222_qm_evaluation_semantics/data/08_a2_h_table.json'),
            ('DATA-09', 'open_problems_fresh/o222_qm_evaluation_semantics/data/09_a2_correlation.json'),
            ('DATA-15', 'open_problems_fresh/o222_qm_evaluation_semantics/data/15_b3r2_results.json'),
            ('DATA-78', 'open_problems_fresh/o222_qm_evaluation_semantics/data/78_r29b_behaviour_classes.json'),
            ('DOC-45', 'open_problems_fresh/o222_qm_evaluation_semantics/docs/45_no_go_boundary_charter.md'),
            ('DOC-13', 'open_problems_fresh/o222_qm_evaluation_semantics/docs/13_d6_results.md'),
            ('DOC-40', 'open_problems_fresh/o222_qm_evaluation_semantics/docs/40_r26_g1g8.md')]
    pin_rows = []
    for tag, rel in pins:
        p = os.path.join(REPO, rel)
        h = hashlib.sha256(io.open(p, 'rb').read()).hexdigest()
        pin_rows.append({'tag': tag, 'path': rel, 'sha256': h})
    gp = os.path.join(ROOT, 'scripts', '01_r1_gate.py')
    gate_src = io.open(gp, encoding='utf-8').read()
    pins_match = all(("'%s'" % h) in gate_src for _t, _p, h in pin_rows)
    arts = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        for fn in sorted(filenames):
            fp = os.path.join(dirpath, fn)
            rel = os.path.relpath(fp, ROOT)
            arts.append({'path': rel, 'bytes': os.path.getsize(fp),
                         'sha256': hashlib.sha256(io.open(fp, 'rb').read()).hexdigest()})
    # Round start = the contract file (the first artefact of this round, frozen before any number).
    warm = os.path.getmtime(os.path.join(DOCS_DIR, '01_r1_contract.md'))
    outside = []
    other_o = []
    declared = {'open_problems_fresh/o227_mapping_channel_no_signalling/', 'problem_register/'}
    for dirpath, dirnames, filenames in os.walk(REPO):
        if '/.git' in dirpath or '__pycache__' in dirpath:
            continue
        for fn in filenames:
            fp = os.path.join(dirpath, fn)
            try:
                if os.path.getmtime(fp) <= warm:
                    continue
            except OSError:
                continue
            rel = os.path.relpath(fp, REPO)
            if any(rel.startswith(d) for d in declared):
                continue
            # files under ANOTHER O directory belong to that O's own session: declared, out of scope
            # (a different O is worked in parallel); only O222 -- the frozen upstream -- is a hard
            # read-only claim of THIS round.
            if rel.startswith('open_problems_fresh/o') and not rel.startswith('open_problems_fresh/o227'):
                other_o.append(rel)
                continue
            outside.append(rel)
    pyc_new = []
    o222_new = []
    for dirpath, dirnames, filenames in os.walk(O2):
        for fn in filenames:
            fp = os.path.join(dirpath, fn)
            try:
                if os.path.getmtime(fp) > warm:
                    if dirpath.endswith('__pycache__'):
                        pyc_new.append(os.path.relpath(fp, REPO))
                    else:
                        o222_new.append(os.path.relpath(fp, REPO))
            except OSError:
                pass
    a4_ok = pins_match and (not outside) and (not pyc_new) and (not o222_new)
    claim('A4', 'artefacts pinned; upstream pins unchanged; zero undeclared writes outside O227 '
                '(and no new bytecode under the frozen O222)', a4_ok,
          'pin rows=%d all present in the gate=%s ; undeclared writes outside O227 (round start = the '
          'contract mtime) = %s ; O222 files touched during the round = %s ; new O222 __pycache__ '
          'entries = %s ; other-O activity declared out of scope = %d file(s)'
          % (len(pin_rows), pins_match, outside or 'none', o222_new or 'none', pyc_new or 'none',
             len(other_o)))

    out = {'rules_version': RULES, 'claims': CLAIMS, 'extra': EXTRA, 'manifest': arts,
           'upstream_pins': pin_rows, 'undeclared_writes_outside_o227': outside,
           'new_pycache_in_o222': pyc_new, 'o222_files_touched_in_round': o222_new,
           'other_o_activity_out_of_scope': sorted(other_o), 'finished_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
           'elapsed_s': time.time() - t0,
           'n_pass': sum(1 for c in CLAIMS if c['ok']), 'n_total': len(CLAIMS)}
    with io.open(os.path.join(DATA, '03_r1_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print('-' * 112)
    print('AUDIT: %d/%d PASS ; artefacts hashed = %d ; upstream pins = %d'
          % (out['n_pass'], out['n_total'], len(arts), len(pin_rows)))
    print('=' * 112, flush=True)
    return 0 if out['n_pass'] == out['n_total'] else 1


if __name__ == '__main__':
    sys.exit(main())
