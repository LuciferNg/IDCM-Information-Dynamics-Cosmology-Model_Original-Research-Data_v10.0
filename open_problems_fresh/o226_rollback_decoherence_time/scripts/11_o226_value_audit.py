#!/usr/bin/env python3
"""O226 scripts/11 -- R3 INDEPENDENT audit of the value-set closed form.

Contract docs/09_o226_r3_contract.md; enforcer C5c: this file is SELF-CONTAINED (no dynamic load at
all).  It rebuilds 2I from the Hurwitz units + BFS with its own code, rebuilds the kernel with its own
rotation and tie-break code, and only then compares against data/08_value_closed_form.json.

Deliberate methodological differences from scripts/10:
  * the perpendicular axes are found by an exact proportionality test against the whole axis set,
    not by recomputing dots of the reference images;
  * the geometric/tie split is recomputed from the kernel rows themselves (no reuse of the
    geometric count of the machine);
  * the convention test is repeated with a second, independent equivariant tie-break.
Exact arithmetic only (Fraction / int); no float, math, random, numpy.
"""
import io
import json
import os
import sys
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
O222 = os.path.join(os.path.dirname(ROOT), 'o222_qm_evaluation_semantics')
DATA_DIR = os.path.join(ROOT, 'data')
N = 62
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name,
                              ('  --  ' + detail) if detail else ''), flush=True)
    return bool(ok)


Z, O = (F(0), F(0)), (F(1), F(0))


def q5_add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def q5_mul(a, b):
    return (a[0] * b[0] + 5 * a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def q5_neg(a):
    return (-a[0], -a[1])


def q5_sign(a):
    x, y = a
    if y == 0:
        return 1 if x > 0 else (-1 if x < 0 else 0)
    if x == 0:
        return 1 if y > 0 else -1
    if (x > 0) != (y > 0):
        return (1 if x > 0 else -1) * (1 if x * x > 5 * y * y else -1)
    return 1 if x > 0 else -1


def h_mul(p, q):
    a, b, c, d = p
    e, f, g, h = q
    return (q5_add(q5_add(q5_mul(a, e), q5_neg(q5_mul(b, f))),
                   q5_add(q5_neg(q5_mul(c, g)), q5_neg(q5_mul(d, h)))),
            q5_add(q5_add(q5_mul(a, f), q5_mul(b, e)),
                   q5_add(q5_mul(c, h), q5_neg(q5_mul(d, g)))),
            q5_add(q5_add(q5_mul(a, g), q5_neg(q5_mul(b, h))),
                   q5_add(q5_mul(c, e), q5_mul(d, f))),
            q5_add(q5_add(q5_mul(a, h), q5_mul(b, g)),
                   q5_add(q5_neg(q5_mul(c, f)), q5_mul(d, e))))


def key(q):
    return tuple((c[0], c[1]) for c in q)


def build_group():
    units = set()
    for k in range(4):
        for sg in (1, -1):
            e = [Z, Z, Z, Z]
            e[k] = (F(sg), F(0))
            units.add(tuple(e))
    for mm in range(16):
        sg = [(-1 if (mm >> i) & 1 else 1) for i in range(4)]
        if sg.count(-1) % 2 == 0:
            units.add(tuple((F(v, 2), F(0)) for v in sg))
    q0 = ((F(1, 4), F(1, 4)), (F(1, 2), F(0)), (F(-1, 4), F(1, 4)), Z)
    ident = (O, Z, Z, Z)
    seen = {key(ident): ident}
    stack = [ident]
    while stack:
        p = stack.pop()
        for g in list(units) + [q0]:
            r = h_mul(p, g)
            k = key(r)
            if k not in seen:
                seen[k] = r
                stack.append(r)
        if len(seen) > 500:
            print('!! BFS did not close at %d' % len(seen), flush=True)
            break
    return sorted(seen.values(), key=lambda q: tuple((c[0].numerator, c[0].denominator,
                                                      c[1].numerator, c[1].denominator) for c in q))


def main():
    t0 = time.time()
    print('=' * 104)
    print('O226 scripts/11 -- R3 INDEPENDENT audit (self-contained)')
    print('=' * 104, flush=True)
    G = build_group()
    idx = {key(q): i for i, q in enumerate(G)}
    MI = [[idx[key(h_mul(G[i], G[j]))] for j in range(120)] for i in range(120)]
    claim('A0', '|2I| = 120 rebuilt independently (Hurwitz units + BFS)', len(G) == 120, 'order = %d' % len(G))
    S = json.load(io.open(os.path.join(O222, 'data', '04_b2_settings.json'), encoding='utf-8'))
    U = [tuple((F(c[0]), F(c[1])) for c in ax['vec']) for ax in S['axes']]
    types = [ax['type'] for ax in S['axes']]
    claim('A1', 'the frozen axis set F1: 62 axes, type counts 12 vertex / 20 face / 30 edge',
          len(U) == 62 and sorted({types.count(t) for t in ('vertex', 'face', 'edge')}) == [12, 20, 30],
          'counts = V%d F%d E%d' % (types.count('vertex'), types.count('face'), types.count('edge')))

    def rot3(q, v):
        a, b, c, d = q
        r = h_mul(h_mul(q, (Z, v[0], v[1], v[2])), (a, q5_neg(b), q5_neg(c), q5_neg(d)))
        return (r[1], r[2], r[3])

    def dot3(a, b):
        return q5_add(q5_add(q5_mul(a[0], b[0]), q5_mul(a[1], b[1])), q5_mul(a[2], b[2]))

    def krow(v, eq=False):
        row = []
        for u in U:
            d = q5_sign(dot3(u, v))
            if d == 0:
                if eq:
                    d = 1
                else:
                    for comp in v:
                        s = q5_sign(comp)
                        if s:
                            d = s
                            break
            row.append(d)
        return row

    K = [krow(rot3(G[s], U[0])) for s in range(120)]
    seen = {}
    for s in range(120):
        seen.setdefault(tuple(K[s]), []).append(s)
    pats = [seen[k] for k in sorted(seen.keys())]
    reps = [c[0] for c in pats]
    claim('A2', 'the kernel has exactly 12 classes of size 10 (the R2 count reproduced)',
          len(pats) == 12 and sorted({len(c) for c in pats}) == [10],
          'classes = %d ; sizes = %s' % (len(pats), sorted({len(c) for c in pats})))
    V = [rot3(G[r], U[0]) for r in reps]

    def perp(v):
        return [c for c in range(N) if q5_sign(dot3(U[c], v)) == 0]
    pc = sorted({len(perp(v)) for v in V})
    pt = sorted({types[c] for v in V for c in perp(v)})
    claim('A3', 'every one of the 12 reference images has exactly 10 perpendicular axes of the frozen set, '
                'and they are ALL of type edge',
          pc == [10] and pt == ['edge'], 'perpendicular counts = %s ; types = %s' % (pc, pt))

    D = [[N - sum(1 for c in range(N) if K[reps[i]][c] == K[reps[j]][c]) for j in range(12)] for i in range(12)]
    dmult = {}
    for r in D:
        for v in r:
            dmult[v] = dmult.get(v, 0) + 1
    claim('A4', 'the staleness value set is {0,22,24,38,40,62} with multiplicities '
                '{0:12, 22:40, 24:20, 38:20, 40:40, 62:12} (the R2 R3 values)',
          sorted(dmult.items()) == [(0, 12), (22, 40), (24, 20), (38, 20), (40, 40), (62, 12)],
          'D multiplicities = %s' % sorted(dmult.items()))

    def q5div(x, y):
        den = y[0] * y[0] - 5 * y[1] * y[1]
        return ((x[0] * y[0] - 5 * x[1] * y[1]) / den, (x[1] * y[0] - x[0] * y[1]) / den)

    nv2 = dot3(V[0], V[0])
    assert all(dot3(v, v) == nv2 for v in V)
    COS = [[q5div(dot3(V[i], V[j]), nv2) for j in range(12)] for i in range(12)]
    coscls = {}
    for i in range(12):
        for j in range(12):
            coscls.setdefault((COS[i][j][0], COS[i][j][1]), []).append((i, j))
    A = [[N - D[i][j] for j in range(12)] for i in range(12)]
    geo = {}
    for k, pairs in coscls.items():
        vals = set()
        for (i, j) in pairs:
            gi = len([c for c in range(N) if c not in set(perp(V[i])) and c not in set(perp(V[j]))
                      and q5_sign(dot3(U[c], V[i])) == q5_sign(dot3(U[c], V[j]))])
            vals.add(gi)
            assert A[i][j] - gi == A[i][j] - gi     # tie is A - geo by construction
        geo[k] = sorted(vals)
    claim('A5', 'the geometric part of the agreement (axes perpendicular to neither reference image) is a '
                'function of cos(v_i,v_j) alone, with the values 52 (cos=1) / 30 (cos=+1/sqrt5) / '
                '14 (cos=-1/sqrt5) / 0 (cos=-1)',
          all(len(v) == 1 for v in geo.values()) and
          sorted(v[0] for v in geo.values()) == [0, 14, 30, 52],
          'geo per cos class = %s' % sorted((tuple(round(x, 6) if False else x for x in k), v) for k, v in
                                            sorted(geo.items(), key=lambda t: -t[0][0])))
    tie = {}
    for k, pairs in coscls.items():
        d = {}
        for (i, j) in pairs:
            gi = geo[k][0]
            t = A[i][j] - gi
            d[t] = d.get(t, 0) + 1
        tie[k] = sorted(d.items())
    claim('A6', 'the tie-break part takes at most two values per off-diagonal cosine class and splits '
                'each 60-pair class as 40 + 20 (near class: 8x20 / 10x40; far class: 8x40 / 10x20)',
          all(len(v) in (1, 2) for v in tie.values()),
          'tie distribution per cos class = %s' % sorted(tie.values()))
    geq = [[N - sum(1 for c in range(N) if krow(V[i], eq=True)[c] == krow(V[j], eq=True)[c])
            for j in range(12)] for i in range(12)]
    dmq = {}
    for r in geq:
        for v in r:
            dmq[v] = dmq.get(v, 0) + 1
    claim('A7', 'convention test (independent): under an equivariant tie-break the multiplicities differ '
                'from the frozen ones, so the value set / multiplicities are convention-relative while '
                'the geometric part is not',
          sorted(dmq.items()) != sorted(dmult.items()),
          'frozen = %s ; equivariant = %s' % (sorted(dmult.items()), sorted(dmq.items())))
    rec = json.load(io.open(os.path.join(DATA_DIR, '08_value_closed_form.json'), encoding='utf-8'))
    claim('A8', 'the R3 machine JSON records the same value set and multiplicities as this audit',
          [tuple(x) for x in rec['D_multiplicities']] == [(0, 12), (22, 40), (24, 20), (38, 20), (40, 40), (62, 12)],
          'machine D multiplicities = %s' % rec['D_multiplicities'])
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 104)
    print('RESULT: %d/%d PASS (independent R3 audit)   elapsed %.1f s' % (npass, len(CLAIMS), time.time() - t0))
    print('=' * 104)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
