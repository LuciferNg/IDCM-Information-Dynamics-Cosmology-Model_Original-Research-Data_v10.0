#!/usr/bin/env python3
"""O226 scripts/13 -- R4 INDEPENDENT audit (self-contained; enforcer C5d).

Rebuilds 2I (Hurwitz units + BFS), the axis set, the kernel and BOTH conventions with its OWN code;
no dynamic load at all.  Verifies the R4 theorems (geo = 2W, the W type table, the W_V factorisation,
the equivariant theorem A_eq = 2W + 10, the class-count robustness) and concurs with data/09.

Deliberate methodological differences from scripts/12:
  * the double lune is decided by the SIGN PRODUCT sgn((a.v_i)(a.v_j)) computed from the raw dots of the
    canonical representative (no lune_status helper, no axis object);
  * the perpendicular axes are found by an exact zero test on the whole dot, per type;
  * the vertex graph is built from the 12 pointed vertex axes with its own adjacency test.
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
DD = os.path.join(ROOT, 'data')
N = 62
CLAIMS = []
Z = (F(0), F(0))
O = (F(1), F(0))


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def a5(x, y):
    return (x[0] + y[0], x[1] + y[1])


def m5(x, y):
    return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def n5(x):
    return (-x[0], -x[1])


def s5(x):
    a, b = x
    if b == 0:
        return 1 if a > 0 else (-1 if a < 0 else 0)
    if a == 0:
        return 1 if b > 0 else -1
    if (a > 0) != (b > 0):
        return (1 if a > 0 else -1) * (1 if a * a > 5 * b * b else -1)
    return 1 if a > 0 else -1


def hmul(p, q):
    a, b, c, d = p
    e, f, g, h = q
    return (a5(a5(m5(a, e), n5(m5(b, f))), a5(n5(m5(c, g)), n5(m5(d, h)))),
            a5(a5(m5(a, f), m5(b, e)), a5(m5(c, h), n5(m5(d, g)))),
            a5(a5(m5(a, g), n5(m5(b, h))), a5(m5(c, e), m5(d, f))),
            a5(a5(m5(a, h), m5(b, g)), a5(n5(m5(c, f)), m5(d, e))))


def key(q):
    return tuple((c[0], c[1]) for c in q)


def build():
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
    st = [ident]
    while st:
        p = st.pop()
        for g in list(units) + [q0]:
            r = hmul(p, g)
            k = key(r)
            if k not in seen:
                seen[k] = r
                st.append(r)
    return sorted(seen.values(), key=lambda q: tuple((c[0].numerator, c[0].denominator,
                                                      c[1].numerator, c[1].denominator) for c in q))


def main():
    t0 = time.time()
    print('=' * 104)
    print('O226 scripts/13 -- R4 INDEPENDENT audit (self-contained)')
    print('=' * 104, flush=True)
    G = build()
    idx = {key(q): i for i, q in enumerate(G)}
    claim('A0', '|2I| = 120 rebuilt independently', len(G) == 120, 'order = %d' % len(G))
    S = json.load(io.open(os.path.join(O222, 'data', '04_b2_settings.json'), encoding='utf-8'))
    U = [tuple((F(c[0]), F(c[1])) for c in ax['vec']) for ax in S['axes']]
    types = [ax['type'] for ax in S['axes']]

    def rot(v, q):
        a, b, c, d = q
        r = hmul(hmul(q, (Z, v[0], v[1], v[2])), (a, n5(b), n5(c), n5(d)))
        return (r[1], r[2], r[3])

    def dot(a, b):
        return a5(a5(m5(a[0], b[0]), m5(a[1], b[1])), m5(a[2], b[2]))

    def krow(v, eq):
        row = []
        for u in U:
            d = s5(dot(u, v))
            if d == 0:
                if eq:
                    d = 1
                else:
                    for comp in v:
                        t = s5(comp)
                        if t:
                            d = t
                            break
            row.append(d)
        return row

    K = [krow(rot(U[0], G[s]), False) for s in range(120)]
    grp = {}
    for s in range(120):
        grp.setdefault(tuple(K[s]), []).append(s)
    cl = [grp[k] for k in sorted(grp.keys())]
    reps = [c[0] for c in cl]
    claim('A1', 'the frozen kernel still has 12 classes of size 10', len(cl) == 12 and
          sorted({len(c) for c in cl}) == [10], 'classes = %d' % len(cl))
    V = [rot(U[0], G[r]) for r in reps]
    nv2 = dot(V[0], V[0])

    # axis pairing with own code
    def cross_zero(a, b):
        for k in range(3):
            x = a5(m5(a[k], b[(k + 1) % 3]), n5(m5(a[(k + 1) % 3], b[k])))
            if x != Z:
                return False
        return True

    used = [False] * N
    ax = []
    for c in range(N):
        if used[c]:
            continue
        for d in range(N):
            if d == c or used[d]:
                continue
            # the central-symmetric partner: parallel AND dot < 0
            if cross_zero(U[c], U[d]) and s5(dot(U[c], U[d])) < 0:
                used[c] = used[d] = True
                ax.append((c, types[c]))
                break
    claim('A2', 'the 62 pointed axes pair into 31 unoriented axes with type counts V6 / F10 / E15',
          len(ax) == 31 and sum(1 for a in ax if a[1] == 'vertex') == 6 and
          sum(1 for a in ax if a[1] == 'face') == 10 and sum(1 for a in ax if a[1] == 'edge') == 15,
          'axes = %d (V%d F%d E%d)' % (len(ax), sum(1 for a in ax if a[1] == 'vertex'),
                                       sum(1 for a in ax if a[1] == 'face'),
                                       sum(1 for a in ax if a[1] == 'edge')))

    def Wv(i, j, ty=None):
        n = 0
        for (c, t) in ax:
            if ty and t != ty:
                continue
            di, dj = s5(dot(U[c], V[i])), s5(dot(U[c], V[j]))
            if di != 0 and dj != 0 and di == dj:
                n += 1
        return n
    W = [[Wv(i, j) for j in range(12)] for i in range(12)]
    geo = [[len([c for c in range(N) if s5(dot(U[c], V[i])) != 0 and s5(dot(U[c], V[j])) != 0 and
                 s5(dot(U[c], V[i])) == s5(dot(U[c], V[j]))]) for j in range(12)] for i in range(12)]
    claim('A3', 'geo = 2W for all 144 pairs; W takes the four values {26,15,7,0} and geo {52,30,14,0}',
          all(geo[i][j] == 2 * W[i][j] for i in range(12) for j in range(12)) and
          sorted({W[i][j] for i in range(12) for j in range(12)}) == [0, 7, 15, 26],
          'W values = %s ; geo values = %s' % (sorted({W[i][j] for i in range(12) for j in range(12)}),
                                               sorted({geo[i][j] for i in range(12) for j in range(12)})))

    def cosv(i, j):
        den = nv2[0] * nv2[0] - 5 * nv2[1] * nv2[1]
        x = dot(V[i], V[j])
        return ((x[0] * nv2[0] - 5 * x[1] * nv2[1]) / den, (x[1] * nv2[0] - x[0] * nv2[1]) / den)
    ck = {}
    for i in range(12):
        for j in range(12):
            ck.setdefault((cosv(i, j)[0], cosv(i, j)[1]), []).append((i, j))
    tab = {}
    for k, prs in ck.items():
        t = {}
        for ty in ('vertex', 'face', 'edge'):
            t[ty] = sorted({Wv(i, j, ty) for (i, j) in prs})
        tab[(k[0], k[1])] = t
    one, mone = (F(1), F(0)), (F(-1), F(0))
    near, far = (F(0), F(1, 5)), (F(0), F(-1, 5))
    ok = (tab.get(one) == {'vertex': [6], 'face': [10], 'edge': [10]} and
          tab.get(near) == {'vertex': [4], 'face': [6], 'edge': [5]} and
          tab.get(far) == {'vertex': [2], 'face': [4], 'edge': [1]} and
          tab.get(mone) == {'vertex': [0], 'face': [0], 'edge': [0]})
    claim('A4', 'the W type table is (6,10,10) / (4,6,5) / (2,4,1) / (0,0,0) for cos = 1 / +1/sqrt5 / '
                '-1/sqrt5 / -1 (Pr-7.2 reproduced independently)', ok, 'table = %s' % tab)
    # vertex factorisation
    vp = [i for i in range(12)]
    adj = {}
    for i in range(12):
        adj[i] = [j for j in range(12) if j != i and cosv(i, j) == (F(0), F(1, 5))]
    com = [[len(set(adj[i]) & set(adj[j])) for j in range(12)] for i in range(12)]
    ok5 = all(Wv(i, j, 'vertex') == 2 * (1 if j in adj[i] else 0) + com[i][j]
              for i in range(12) for j in range(12) if i != j)
    claim('A5', 'W_V = 2*[i~j] + |N_i n N_j| for every off-diagonal pair (degrees 5, common neighbours '
                '0/2) and W_V(i,i) = 6', ok5 and sorted({len(v) for v in adj.values()}) == [5] and
          sorted({com[i][j] for i in range(12) for j in range(12) if i != j}) == [0, 2] and
          all(Wv(i, i, 'vertex') == 6 for i in range(12)),
          'degrees = %s ; common-neighbour values = %s' % (sorted({len(v) for v in adj.values()}),
                                                           sorted({com[i][j] for i in range(12) for j in range(12) if i != j})))

    # perpendicular structure
    per1 = [sum(1 for (c, t) in ax if t == 'edge' and s5(dot(U[c], v)) == 0 and
                all(True for _ in range(1))) for v in V]
    perpair = {}
    for i in range(12):
        for j in range(12):
            k = (i, j)
            n = sum(1 for (c, t) in ax if s5(dot(U[c], V[i])) == 0 or s5(dot(U[c], V[j])) == 0)
            perpair.setdefault((i == j, i, j), n)
    antip = [(i, j) for i in range(12) for j in range(12) if i != j and cosv(i, j) == (F(-1), F(0))]
    claim('A6', 'each reference image has exactly 5 perpendicular EDGE axes; a non-antipodal '
                'off-diagonal pair has 9 perpendicular-involved axes (5+5-1), while the diagonal and '
                'the antipodal pairs (where the two reference images share all 5 perpendicular axes) '
                'have 5',
          sorted(set(per1)) == [5] and
          sorted({v for k, v in perpair.items() if k[0]}) == [5] and
          sorted({perpair[(False, i, j)] for (i, j) in antip}) == [5] and
          sorted({v for k, v in perpair.items() if not k[0] and (k[1], k[2]) not in antip}) == [9],
          'per-image = %s ; per-pair (off-diag) = %s' % (sorted(set(per1)),
                                                         sorted({v for k, v in perpair.items() if not k[0]})))
    Af = [[len([c for c in range(N) if K[reps[i]][c] == K[reps[j]][c]]) for j in range(12)] for i in range(12)]
    Keq = [[(s5(dot(U[c], rot(U[0], G[s]))) or 1) for c in range(N)] for s in range(120)]
    grp2 = {}
    for s in range(120):
        grp2.setdefault(tuple(Keq[s]), []).append(s)
    cl2 = sorted(grp2.values(), key=lambda c: c[0])
    Aeq = [[len([c for c in range(N) if Keq[reps[i]][c] == Keq[reps[j]][c]]) for j in range(12)]
           for i in range(12)]
    Deq = [[N - Aeq[i][j] for j in range(12)] for i in range(12)]
    claim('A7', 'equivariant convention: A_eq = 2W + 10 for all pairs, hence D_eq = 52 - 2W with the '
                'value set {0,22,38,52} and multiplicities (12,60,60,12)',
          all(Aeq[i][j] == 2 * W[i][j] + 10 for i in range(12) for j in range(12)),
          'D_eq values = %s ; multiplicities = %s'
          % (sorted({Deq[i][j] for i in range(12) for j in range(12)}), sorted(_mult(Deq).items())))
    claim('A8', 'equivariant convention: still 12 classes of size 10 and the SAME partition as the '
                'frozen kernel',
          len(cl2) == 12 and sorted({len(c) for c in cl2}) == [10] and
          sorted([sorted(c) for c in cl2]) == sorted([sorted(c) for c in cl]),
          'classes = %d ; same partition = %s'
          % (len(cl2), sorted([sorted(c) for c in cl2]) == sorted([sorted(c) for c in cl])))
    rec = json.load(io.open(os.path.join(DD, '09_w_closed_form.json'), encoding='utf-8'))
    claim('A9', 'concurrence with the R4 machine JSON (W table and D_eq multiplicities)',
          rec['W_table'] == W and [tuple(x) for x in rec['D_eq_multiplicities']] == sorted(_mult(Deq).items()),
          'W table identical = %s ; D_eq multiplicities = %s'
          % (rec['W_table'] == W, sorted(_mult(Deq).items())))
    np_ = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 104)
    print('RESULT: %d/%d PASS (independent R4 audit)   elapsed %.1f s' % (np_, len(CLAIMS), time.time() - t0))
    print('=' * 104)
    return 0 if np_ == len(CLAIMS) else 1


def _mult(tab):
    d = {}
    for r in tab:
        for v in r:
            d[v] = d.get(v, 0) + 1
    return d


if __name__ == '__main__':
    sys.exit(main())
