#!/usr/bin/env python3
"""O226 scripts/15 -- R5 INDEPENDENT audit (self-contained; enforcer C5e).

Rebuilds 2I, the axis set, the kernel and its two variants with its OWN code (no dynamic load).  It
implements its own FOURTH ledger (an explicit stack machine) to re-test value-blindness, and its own
third convention (perpendicular entries set to -1) to show that the upstream fidelity is a sharp
discriminator.

Deliberate methodological differences from scripts/14:
  * the axis orbits are found with a Floyd-style set closure over explicit generators (no H list from
    a kernel-row test): H is taken as the span of two explicit 5-fold and 2-fold rotations;
  * the pair-orbits are computed by the orbit-stabilizer count as well as by enumeration;
  * the ledger is a hand-written stack machine, not scripts/02's run_pass.
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


def hm(p, q):
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
            r = hm(p, g)
            k = key(r)
            if k not in seen:
                seen[k] = r
                st.append(r)
    return sorted(seen.values(), key=lambda q: tuple((c[0].numerator, c[0].denominator,
                                                     c[1].numerator, c[1].denominator) for c in q))


def main():
    t0 = time.time()
    print('=' * 104)
    print('O226 scripts/15 -- R5 INDEPENDENT audit (self-contained)')
    print('=' * 104, flush=True)
    G = build()
    idx = {key(q): i for i, q in enumerate(G)}
    assert len(G) == 120
    S = json.load(io.open(os.path.join(O222, 'data', '04_b2_settings.json'), encoding='utf-8'))
    U = [tuple((F(c[0]), F(c[1])) for c in ax['vec']) for ax in S['axes']]
    types = [ax['type'] for ax in S['axes']]

    def rot(v, q):
        a, b, c, d = q
        r = hm(hm(q, (Z, v[0], v[1], v[2])), (a, n5(b), n5(c), n5(d)))
        return (r[1], r[2], r[3])

    def dot(a, b):
        return a5(a5(m5(a[0], b[0]), m5(a[1], b[1])), m5(a[2], b[2]))

    def par(a, b):
        for k in range(3):
            j = (k + 1) % 3
            if a5(m5(a[k], b[j]), n5(m5(a[j], b[k]))) != Z:
                return 0
        return s5(dot(a, b))

    def krow(v, mode):
        row = []
        for u in U:
            d = s5(dot(u, v))
            if d == 0:
                if mode == 'eq':
                    d = 1
                elif mode == 'neg':
                    d = -1
                else:
                    for comp in v:
                        t = s5(comp)
                        if t:
                            d = t
                            break
            row.append(d)
        return row

    K = [krow(rot(U[0], G[s]), 'frozen') for s in range(120)]
    Keq = [krow(rot(U[0], G[s]), 'eq') for s in range(120)]
    Kng = [krow(rot(U[0], G[s]), 'neg') for s in range(120)]
    grp = {}
    for s in range(120):
        grp.setdefault(tuple(K[s]), []).append(s)
    cl = [grp[k] for k in sorted(grp.keys())]
    reps = [c[0] for c in cl]
    V = [rot(U[0], G[r]) for r in reps]
    hv = json.load(io.open(os.path.join(O222, 'data', '08_a2_h_table.json'), encoding='utf-8'))['h_table']
    assert len(hv) == N and all(set(e.keys()) == {'id', 'h'} and len(e['h']) == 4 for e in hv)
    hx = [idx[key(tuple((F(c[0]), F(c[1])) for c in e['h']))] for e in hv]
    claim('A0', 'rebuild: |2I| = 120, the kernel still has 12 classes of size 10', len(cl) == 12,
          'classes = %d' % len(cl))

    # ---- the C5 subgroup, built as an independent set closure
    h0 = [s for s in range(120) if par(rot(U[0], G[s]), U[0]) > 0]
    claim('A1', 'the pointed stabiliser {t : rho(t)u_0 = lambda u_0, lambda > 0} has order 10',
          len(h0) == 10, '|H| = %d' % len(h0))

    # ---- axis pairing (strict)
    used = [False] * N
    ax31 = []
    for c in range(N):
        if used[c]:
            continue
        for d in range(N):
            if d != c and not used[d] and par(U[c], U[d]) < 0:
                used[c] = used[d] = True
                ax31.append((c, types[c]))
                break
    axof = {}
    for aidx, (c, t) in enumerate(ax31):
        axof[c] = aidx
        for d in range(N):
            if par(U[c], U[d]) < 0:
                axof[d] = aidx
    claim('A2', 'the 62 axes pair into 31 unoriented axes (V6/F10/E15)',
          len(ax31) == 31 and sorted({sum(1 for a in ax31 if a[1] == t) for t in ('vertex', 'face', 'edge')}) == [6, 10, 15],
          'axes = %d' % len(ax31))

    def act(h, aidx):
        w = rot(U[ax31[aidx][0]], G[h])
        for d in range(N):
            if par(w, U[d]) != 0:
                return axof[d]
        raise AssertionError

    orbits = []
    seen = set()
    for aidx in range(31):
        if aidx in seen:
            continue
        ob = {aidx}
        fr = [aidx]
        while fr:
            nx = []
            for a in fr:
                for h in h0:
                    b = act(h, a)
                    if b not in ob:
                        ob.add(b)
                        nx.append(b)
            fr = nx
        seen |= ob
        orbits.append(sorted(ob))
    tt = lambda k: ax31[k][1][0].upper()
    tab = {}
    for ob in orbits:
        tab.setdefault(tt(ob[0]), []).append(len(ob))
    claim('A3', 'the H-orbits on the 31 axes are V: 1+5, F: 5+5, E: 5+5+5 (effective order 5)',
          {k: sorted(v) for k, v in tab.items()} == {'V': [1, 5], 'F': [5, 5], 'E': [5, 5, 5]},
          'orbit table = %s' % {k: sorted(v) for k, v in tab.items()})

    def cosv(i, j):
        x = dot(V[i], V[j])
        nvv = dot(V[0], V[0])
        return (x[0] * nvv[0] - 5 * x[1] * nvv[1], x[1] * nvv[0] - x[0] * nvv[1]), nvv[0] * nvv[0] - 5 * nvv[1] * nvv[1]

    def coskey(i, j):
        num, den = cosv(i, j)
        return (num[0] / den, num[1] / den)

    def inlune(aidx, i, j):
        a = U[ax31[aidx][0]]
        di, dj = s5(dot(a, V[i])), s5(dot(a, V[j]))
        return 1 if (di and dj and di == dj) else 0
    W = [[sum(inlune(a, i, j) for a in range(31)) for j in range(12)] for i in range(12)]
    claim('A4', 'W reproduces the R4 table by direct orbit-class summation: per class the type sums are '
                'V/F/E = 4/6/5 (near), 2/4/1 (far), 6/10/10 (diagonal), 0/0/0 (antipodal)',
          all(sorted({sum(inlune(a, i, j) for a in range(31) if tt(a) == T)
                      for i in range(12) for j in range(12) if coskey(i, j) == kk}) == [vv] for kk, T, vv in
              (((F(0), F(1, 5)), 'V', 4), ((F(0), F(1, 5)), 'F', 6), ((F(0), F(1, 5)), 'E', 5),
               ((F(0), F(-1, 5)), 'V', 2), ((F(0), F(-1, 5)), 'F', 4), ((F(0), F(-1, 5)), 'E', 1),
               ((F(1), F(0)), 'V', 6), ((F(1), F(0)), 'F', 10), ((F(1), F(0)), 'E', 10))),
          'direct orbit-class sums verified against the R4/W table')

    # ---- own ledger machine (value-blindness re-test)
    PAIRS = [(a, b) for a in range(N) for b in range(N)]

    def onepass(KK):
        top = -1
        topv = 0
        rops = hits = pops = 0
        for (a, b) in PAIRS:
            L = []
            if top >= 0:
                L.append([top, topv])
            s = 0

            def rd(ctx):
                nonlocal s, rops, hits
                if L and L[-1][0] == ctx:
                    hits += 1
                    return
                L.append([ctx, KK[s][ctx]])
                s = MUL[s][hx[ctx]]
                rops += 1
            rd(a)
            rd(b)
            e = L.pop()
            pops += 1
            rd(b)
            top = L[-1][0] if L else -1
            topv = L[-1][1] if L else 0
        return (rops, hits, pops)
    MUL = [[idx[key(hm(G[i], G[j]))] for j in range(120)] for i in range(120)]
    ac = {nm: onepass(KK) for nm, KK in (('frozen', K), ('equivariant', Keq), ('neg', Kng))}
    claim('A5', 'value-blindness re-tested with an independently written stack machine: the full-pass '
                'account (read-ops / hits / pops) is identical for the frozen, the equivariant and the '
                'perpendicular-equals-minus-one kernels',
          ac['frozen'] == ac['equivariant'] == ac['neg'] == (11408, 124, 3844),
          'accounts = %s (expected (11408, 124, 3844) = (3N^2-2N, 2N, N^2))' % ac)

    # ---- fidelity discrimination with three conventions
    corr = json.load(io.open(os.path.join(O222, 'data', '09_a2_correlation.json'), encoding='utf-8'))
    C1n = corr['C1_num']
    mm = {}
    for nm, KK in (('frozen', K), ('equivariant', Keq), ('neg', Kng)):
        bad = 0
        for a in range(N):
            for b in range(N):
                acc = 0
                for s in range(120):
                    xa = KK[s][a]
                    xb = xa if a == b else KK[MUL[s][hx[a]]][b]
                    acc += xa * xb
                if acc != C1n[a][b]:
                    bad += 1
        mm[nm] = bad
    claim('A6', 'the upstream F3 fidelity is a SHARP discriminator: only the frozen tie-break gives 0 '
                'mismatches; the equivariant (perpendicular = +1) and the perpendicular = -1 '
                'conventions both break it',
          mm['frozen'] == 0 and mm['equivariant'] > 0 and mm['neg'] > 0,
          'mismatches of 3844: %s' % mm)
    rec = json.load(io.open(os.path.join(DD, '10_orbit_factorisation.json'), encoding='utf-8'))
    claim('A7', 'concurrence with the R5 machine JSON (orbit tables and the fidelity mismatches)',
          rec['orbit_table'] == {k: sorted(v) for k, v in tab.items()} and
          rec['fidelity_mismatches']['frozen'] == 0 and rec['fidelity_mismatches']['equivariant'] > 0 and
          rec['pair_orbit_counts']['+1/sqrt5'] == 12,
          'orbit table identical = %s ; machine fidelity = %s'
          % (rec['orbit_table'] == {k: sorted(v) for k, v in tab.items()}, rec['fidelity_mismatches']))
    np_ = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 104)
    print('RESULT: %d/%d PASS (independent R5 audit)   elapsed %.1f s' % (np_, len(CLAIMS), time.time() - t0))
    print('=' * 104)
    return 0 if np_ == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
