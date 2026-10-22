#!/usr/bin/env python3
"""O224 scripts/lib2i.py -- self-contained re-implementation of the O222 frozen machine primitives.

PROVENANCE (read-only, no writes to O222):
  * exact Q(sqrt5) arithmetic + 2I construction + readout kernel: derived from
    o222_qm_evaluation_semantics/scripts/09_a2_rollback.py (lines 45-216)
  * budget/window bookkeeping + sweep: derived from .../scripts/12_b5_budget.py
  * frozen inputs: data/frozen/04_b2_settings.json (62 axes), 08_a2_h_table.json (62 h)
    copied verbatim from o222.../data/ (sha256 recorded in data/00_contract.json)

DISCIPLINE: all judging arithmetic is exact (Fraction / Q(sqrt5) pairs of Fractions).
No float, no numpy, no math, no random in any decision path.
"""
import hashlib
import io
import json
import os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
FROZEN = os.path.join(DATA, 'frozen')

# ============================ exact Q(sqrt5) ============================


def N(a, b=0):
    return (F(a), F(b))


ZERO, ONE = N(0), N(1)


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def sub(x, y):
    return (x[0] - y[0], x[1] - y[1])


def mul(x, y):
    return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def neg(x):
    return (-x[0], -x[1])


def scale(x, k):
    return (x[0] * k, x[1] * k)


def is_zero(x):
    return x[0] == 0 and x[1] == 0


def sgn(x):
    if x[1] == 0:
        return (x[0] > 0) - (x[0] < 0)
    if x[0] == 0:
        return (x[1] > 0) - (x[1] < 0)
    if (x[0] > 0) == (x[1] > 0):
        return 1 if x[0] > 0 else -1
    lhs, rhs = x[0] * x[0], 5 * x[1] * x[1]
    if lhs == rhs:
        return 0
    return (1 if lhs > rhs else -1) * (1 if x[0] > 0 else -1)


PHI = N(F(1, 2), F(1, 2))
PSI = sub(PHI, ONE)


def qmul(a, b):
    a0, a1, a2, a3 = a
    b0, b1, b2, b3 = b
    return (sub(sub(mul(a0, b0), mul(a1, b1)), add(mul(a2, b2), mul(a3, b3))),
            add(add(mul(a0, b1), mul(a1, b0)), sub(mul(a2, b3), mul(a3, b2))),
            add(sub(mul(a0, b2), mul(a1, b3)), add(mul(a2, b0), mul(a3, b1))),
            add(sub(add(mul(a0, b3), mul(a1, b2)), mul(a2, b1)), mul(a3, b0)))


def qconj(q):
    return (q[0], neg(q[1]), neg(q[2]), neg(q[3]))


def qkey(q):
    return tuple((c[0], c[1]) for c in q)


def qinv(q):
    """inverse: conj(q)/(q conj(q)); norm^2 = a0^2+a1^2+a2^2+a3^2 (an element of Q)."""
    c = qconj(q)
    n2 = ZERO
    for x in q:
        n2 = add(n2, mul(x, x))
    assert n2[1] == 0, 'norm^2 left Q'
    inv = F(1, 1) / n2[0]
    return tuple(scale(x, inv) for x in c)


ID_ELEM = (ONE, ZERO, ZERO, ZERO)


def build_2T():
    out = set()
    for s in range(8):
        e = [ZERO, ZERO, ZERO, ZERO]
        e[s >> 1] = ONE if (s % 2 == 0) else N(-1)
        out.add(tuple(e))
    for s in range(16):
        sg = [(-1 if s >> i & 1 else 1) for i in range(4)]
        if sg.count(-1) % 2 == 0:
            out.add(tuple(scale(ONE, F(v, 2)) for v in sg))
    return out


def closure_bfs(gens, cap=20000):
    seen = {qkey(ID_ELEM): ID_ELEM}
    queue = [ID_ELEM]
    while queue:
        q = queue.pop()
        for g in gens:
            p = qmul(q, g)
            if qkey(p) not in seen:
                if len(seen) > cap:
                    return list(seen.values())
                seen[qkey(p)] = p
                queue.append(p)
    return list(seen.values())


def build_group():
    """2I with the canonical order used by O222 (sorted by the (num,den) key)."""
    gens = list(build_2T())
    q0 = (scale(PHI, F(1, 2)), scale(ONE, F(1, 2)), scale(PSI, F(1, 2)), ZERO)
    G = closure_bfs(gens + [q0])
    assert len(G) == 120, '|2I| = %d (expected 120)' % len(G)
    G = sorted(G, key=lambda q: tuple((c[0].numerator, c[0].denominator, c[1].numerator,
                                       c[1].denominator) for c in q))
    idx = {qkey(q): i for i, q in enumerate(G)}
    MUL = [[idx[qkey(qmul(a, b))] for b in G] for a in G]
    return G, idx, MUL


def rot_ref(q, n):
    """rotate the 3-vector n by the quaternion q (conjugation) -- R_{-q} = R_q."""
    pure = (ZERO, n[0], n[1], n[2])
    r = qmul(qmul(q, pure), qconj(q))
    return (r[1], r[2], r[3])


def sgn_vec(v):
    """frozen tie rule: sign of the inner product; on a tie, the first nonzero component."""
    s = sgn(v)
    return s


# ============================ frozen inputs ============================
def load_inputs():
    S = json.load(io.open(os.path.join(FROZEN, '04_b2_settings.json'), encoding='utf-8'))
    axes = S['axes']
    U = [tuple((F(c[0]), F(c[1])) for c in ax['vec']) for ax in axes]
    ids = [ax['id'] for ax in axes]
    types = [ax['type'] for ax in axes]
    H = json.load(io.open(os.path.join(FROZEN, '08_a2_h_table.json'),
                          encoding='utf-8'))['h_table']
    hvec = [tuple((F(c[0]), F(c[1])) for c in row['h']) for row in H]
    return axes, U, ids, types, hvec


def build_K(G, U, nref):
    """K[i][a] = sgn(u_a . R_{g_i} nref) with the frozen tie rule (O222 09 lines 203-217)."""
    K = []
    for q in G:
        r = rot_ref(q, nref)
        row = []
        for u in U:
            dot = add(add(mul(u[0], r[0]), mul(u[1], r[1])), mul(u[2], r[2]))
            s = sgn(dot)
            if s == 0:
                for comp in r:
                    sc = sgn(comp)
                    if sc != 0:
                        s = sc
                        break
            row.append(s)
        K.append(row)
    return K


def load_machine():
    """returns (G, idx, MUL, U, ids, types, hx, K) -- the frozen machine."""
    axes, U, ids, types, hvec = load_inputs()
    G, idx, MUL = build_group()
    hx = [idx[qkey(h)] for h in hvec]
    K = build_K(G, U, U[0])
    return G, idx, MUL, U, ids, types, hx, K


# ============================ frozen correlators ============================
def e1_table(K, MUL, hx, n=120, nax=62):
    """common-lambda control (fresh state + empty ledger per pair); integers / 120."""
    C = [[0] * nax for _ in range(nax)]
    for a in range(nax):
        ha = hx[a]
        for b in range(nax):
            if a == b:
                C[a][b] = n
                continue
            acc = 0
            for s in range(n):
                acc += K[s][a] * K[MUL[s][ha]][b]
            C[a][b] = acc
    return C


def e2_table(K, MUL, hx, n=120, nax=62):
    """persistent-ledger world-line; exact DP over the 120 states; returns Fraction table.

    Faithful port of O222 scripts/09 run_pair: `rd` ADVANCES the world state
    s <- MUL[s][hx[ctx]] on a miss, the second read of the pair is preceded by a rollback
    to the state recorded at the popped ledger entry.
    """
    p = [F(1, n)] * n
    C = [[None] * nax for _ in range(nax)]

    def run_pair(a, b, s0, top):
        L = []
        if top >= 0:
            L.append((top, 0, s0))
        st = [s0]

        def rd(ctx):
            if L and L[-1][0] == ctx:
                return L[-1][1]
            v = K[st[0]][ctx]
            L.append((ctx, v, st[0]))
            st[0] = MUL[st[0]][hx[ctx]]
            return v
        xa = rd(a)
        xb = rd(b)
        _c, _v, s_at = L.pop()
        st[0] = s_at
        xb2 = rd(b)
        return {'s_final': st[0], 'x_a': xa, 'x_b': xb2,
                'top_final': (L[-1][0] if L else -1)}
    top = -1
    for a in range(nax):
        for b in range(nax):
            newp = [F(0)] * n
            acc = F(0)
            for s0 in range(n):
                if p[s0] == 0:
                    continue
                r = run_pair(a, b, s0, top)
                newp[r['s_final']] += p[s0]
                acc += p[s0] * (r['x_a'] * r['x_b'])
            C[a][b] = acc
            top = run_pair(a, b, 0, top)['top_final']
            p = newp
    return C


def antipodal(U, nax=62):
    """exact algebraic antipodal test (O222 09 lines 397-407)."""
    anti = bytearray(nax * nax)
    for a in range(nax):
        ua = U[a]
        na = add(add(mul(ua[0], ua[0]), mul(ua[1], ua[1])), mul(ua[2], ua[2]))
        for b in range(nax):
            ub = U[b]
            dot = add(add(mul(ua[0], ub[0]), mul(ua[1], ub[1])), mul(ua[2], ub[2]))
            nb = add(add(mul(ub[0], ub[0]), mul(ub[1], ub[1])), mul(ub[2], ub[2]))
            if sgn(dot) < 0 and mul(dot, dot) == mul(na, nb):
                anti[a * nax + b] = 1
    return anti


def _gcd(x, y):
    while y:
        x, y = y, x % y
    return x


def to_ints(Cmat, nax=62):
    D = 1
    for r in Cmat:
        for v in r:
            f = F(v)
            D = D * f.denominator // _gcd(D, f.denominator)
    return [[int(F(v) * D) for v in r] for r in Cmat], D


def chsh_max(Cmat, anti, mode='all4', nax=62):
    """exact max |S| = |C(a,i) - C(a,j) + C(a2,i) + C(a2,j)| over tuples, efficient P/Q form."""
    N, D = to_ints(Cmat, nax)
    best = (0, None)
    rng = range(nax)
    for a in rng:
        Na = N[a]
        for a2 in rng:
            if mode in ('distinct', 'distinct_anti', 'all4') and a2 == a:
                continue
            Na2 = N[a2]
            P = [Na[i] + Na2[i] for i in rng]
            Q = [Na[j] - Na2[j] for j in rng]
            jok = [True] * nax
            if mode in ('distinct_anti', 'all4'):
                for j in rng:
                    if anti[a * nax + j] or anti[a2 * nax + j]:
                        jok[j] = False
            if mode == 'all4':
                for j in rng:
                    if j == a or j == a2:
                        jok[j] = False
            cand = sorted([(Q[j], j) for j in rng if jok[j]])
            if not cand:
                continue
            sel = cand[:3] + cand[-3:]
            for i in rng:
                if mode == 'all4' and (i == a or i == a2):
                    continue
                if mode in ('distinct_anti', 'all4') and (anti[a * nax + i] or anti[a2 * nax + i]):
                    continue
                for qv, j in sel:
                    if mode in ('distinct', 'distinct_anti', 'all4') and j == i:
                        continue
                    t = P[i] - qv
                    if t < 0:
                        t = -t
                    if t > best[0]:
                        best = (t, (a, a2, i, j))
    return (F(best[0], D), best[1])


# ============================ report helpers ============================
class Report(object):
    def __init__(self, tag):
        self.tag = tag
        self.claims = []

    def claim(self, tag, name, ok, detail=''):
        self.claims.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
        print('[%s] %-7s %s%s' % ('PASS' if ok else 'FAIL', tag, name,
                                  ('  --  ' + detail) if detail else ''), flush=True)
        return bool(ok)

    def finish(self, outpath, extra=None):
        d = dict(extra or {})
        d['script'] = self.tag
        d['claims'] = self.claims
        npass = sum(1 for c in self.claims if c['ok'])
        d['n_pass'] = npass
        d['n_claims'] = len(self.claims)
        with io.open(outpath, 'w', encoding='utf-8') as fh:
            json.dump(d, fh, indent=1, ensure_ascii=False)
        print('RESULT: %d/%d PASS  (%d FAIL)' % (npass, len(self.claims),
                                                 len(self.claims) - npass))
        return npass == len(self.claims)


def sha256(path):
    h = hashlib.sha256()
    with io.open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()
